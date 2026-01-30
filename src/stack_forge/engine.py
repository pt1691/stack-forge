"""Template engine for generating Terraform/Terragrunt configurations."""

import logging
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .models import (
    ResourceConfig,
    ResourceType,
    StackConfig,
)

logger = logging.getLogger(__name__)


# Built-in templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates"


class TemplateEngine:
    """Jinja2-based template engine for infrastructure generation."""

    def __init__(self, templates_dir: Path | None = None):
        self.templates_dir = templates_dir or TEMPLATES_DIR
        self.env = Environment(
            loader=FileSystemLoader([str(self.templates_dir)]),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        # Register custom filters
        self.env.filters["terraform_string"] = self._terraform_string
        self.env.filters["terraform_list"] = self._terraform_list
        self.env.filters["terraform_map"] = self._terraform_map
        self.env.filters["snake_case"] = self._snake_case
        self.env.filters["kebab_case"] = self._kebab_case

    @staticmethod
    def _terraform_string(value: str) -> str:
        """Format value as Terraform string."""
        return f'"{value}"'

    @staticmethod
    def _terraform_list(values: list[str]) -> str:
        """Format list as Terraform list."""
        items = ", ".join(f'"{v}"' for v in values)
        return f"[{items}]"

    @staticmethod
    def _terraform_map(d: dict[str, str]) -> str:
        """Format dict as Terraform map."""
        items = ", ".join(f'{k} = "{v}"' for k, v in d.items())
        return f"{{{items}}}"

    @staticmethod
    def _snake_case(s: str) -> str:
        """Convert string to snake_case."""
        return s.lower().replace("-", "_").replace(" ", "_")

    @staticmethod
    def _kebab_case(s: str) -> str:
        """Convert string to kebab-case."""
        return s.lower().replace("_", "-").replace(" ", "-")

    def get_template(self, resource_type: ResourceType, template_name: str = "main.tf.j2") -> str:
        """Get a template for a resource type."""
        template_path = f"{resource_type.value}/{template_name}"
        try:
            return self.env.get_template(template_path)
        except Exception:
            # Fall back to generic template
            return self.env.get_template(f"generic/{template_name}")

    def render_resource(
        self,
        resource: ResourceConfig,
        stack: StackConfig,
    ) -> dict[str, str]:
        """Render templates for a single resource."""
        context = self._build_context(resource, stack)

        result = {}

        # Render main.tf
        try:
            main_template = self.get_template(resource.type, "main.tf.j2")
            result["main.tf"] = main_template.render(**context)
        except Exception as e:
            logger.warning(f"Could not render main.tf for {resource.type}: {e}")

        # Render variables.tf
        try:
            vars_template = self.get_template(resource.type, "variables.tf.j2")
            result["variables.tf"] = vars_template.render(**context)
        except Exception:
            logger.debug(f"No variables.tf template for {resource.type}")

        # Render outputs.tf
        try:
            outputs_template = self.get_template(resource.type, "outputs.tf.j2")
            result["outputs.tf"] = outputs_template.render(**context)
        except Exception:
            logger.debug(f"No outputs.tf template for {resource.type}")

        return result

    def render_stack(self, stack: StackConfig, output_dir: Path) -> list[Path]:
        """Render all templates for a stack."""
        generated_files = []
        stack_dir = output_dir / stack.name

        # Generate provider configuration
        provider_content = self._render_provider(stack)
        provider_file = stack_dir / "providers.tf"
        self._write_file(provider_file, provider_content)
        generated_files.append(provider_file)

        # Generate backend configuration
        backend_content = self._render_backend(stack)
        backend_file = stack_dir / "backend.tf"
        self._write_file(backend_file, backend_content)
        generated_files.append(backend_file)

        # Generate each resource as a module
        for resource in stack.resources:
            if not resource.enabled:
                continue

            resource_dir = stack_dir / "modules" / resource.name
            rendered = self.render_resource(resource, stack)

            for filename, content in rendered.items():
                file_path = resource_dir / filename
                self._write_file(file_path, content)
                generated_files.append(file_path)

        # Generate root main.tf that calls modules
        root_main = self._render_root_main(stack)
        root_main_file = stack_dir / "main.tf"
        self._write_file(root_main_file, root_main)
        generated_files.append(root_main_file)

        # Generate terragrunt.hcl if enabled
        if stack.use_terragrunt:
            terragrunt_content = self._render_terragrunt(stack)
            terragrunt_file = stack_dir / "terragrunt.hcl"
            self._write_file(terragrunt_file, terragrunt_content)
            generated_files.append(terragrunt_file)

        return generated_files

    def _build_context(self, resource: ResourceConfig, stack: StackConfig) -> dict[str, Any]:
        """Build template context with all variables."""
        return {
            "resource": resource,
            "stack": stack,
            "name": resource.name,
            "type": resource.type.value,
            "variables": resource.variables,
            "tags": {**stack.get_default_tags(), **resource.tags},
            "environment": stack.environment.value,
            "region": stack.region,
            "organization": stack.organization,
            "project": stack.project,
        }

    def _render_provider(self, stack: StackConfig) -> str:
        """Render provider configuration."""
        if stack.provider.value == "aws":
            return f'''# AWS Provider Configuration
# Generated by Stack Forge

terraform {{
  required_version = ">= 1.0"

  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "{stack.region}"

  default_tags {{
    tags = {{
      Environment  = "{stack.environment.value}"
      Project      = "{stack.project}"
      Organization = "{stack.organization}"
      ManagedBy    = "terraform"
      GeneratedBy  = "stack-forge"
    }}
  }}
}}
'''
        return "# Provider configuration not available"

    def _render_backend(self, stack: StackConfig) -> str:
        """Render backend configuration."""
        bucket = stack.backend_config.get("bucket", f"{stack.organization}-terraform-state")
        key = stack.backend_config.get(
            "key", f"{stack.project}/{stack.environment.value}/{stack.name}/terraform.tfstate"
        )
        region = stack.backend_config.get("region", stack.region)
        dynamodb_table = stack.backend_config.get("dynamodb_table", f"{stack.organization}-terraform-locks")

        return f'''# Backend Configuration
# Generated by Stack Forge

terraform {{
  backend "s3" {{
    bucket         = "{bucket}"
    key            = "{key}"
    region         = "{region}"
    encrypt        = true
    dynamodb_table = "{dynamodb_table}"
  }}
}}
'''

    def _render_root_main(self, stack: StackConfig) -> str:
        """Render root main.tf that calls all modules."""
        modules = []
        for resource in stack.resources:
            if not resource.enabled:
                continue

            module_block = f'''
module "{resource.name}" {{
  source = "./modules/{resource.name}"

  # Variables passed to the module
  environment = var.environment
  project     = var.project

  # Resource-specific variables
'''
            for key, value in resource.variables.items():
                if isinstance(value, str):
                    module_block += f'  {key} = "{value}"\n'
                elif isinstance(value, bool):
                    module_block += f"  {key} = {str(value).lower()}\n"
                elif isinstance(value, (int, float)):
                    module_block += f"  {key} = {value}\n"
                else:
                    module_block += f"  {key} = {value}\n"

            if resource.depends_on:
                deps = ", ".join(f"module.{d}" for d in resource.depends_on)
                module_block += f"\n  depends_on = [{deps}]\n"

            module_block += "}\n"
            modules.append(module_block)

        header = f'''# Main Terraform Configuration
# Stack: {stack.name}
# Generated by Stack Forge

variable "environment" {{
  description = "Deployment environment"
  type        = string
  default     = "{stack.environment.value}"
}}

variable "project" {{
  description = "Project name"
  type        = string
  default     = "{stack.project}"
}}
'''
        return header + "\n".join(modules)

    def _render_terragrunt(self, stack: StackConfig) -> str:
        """Render terragrunt.hcl configuration."""
        bucket = stack.backend_config.get("bucket", f"{stack.organization}-terraform-state")
        key = f"{stack.project}/{stack.environment.value}/{stack.name}/terraform.tfstate"
        region = stack.backend_config.get("region", stack.region)
        dynamodb_table = stack.backend_config.get("dynamodb_table", f"{stack.organization}-terraform-locks")

        return f'''# Terragrunt Configuration
# Stack: {stack.name}
# Generated by Stack Forge

# Include root terragrunt.hcl
include "root" {{
  path = find_in_parent_folders()
}}

# Local variables
locals {{
  environment = "{stack.environment.value}"
  project     = "{stack.project}"
  region      = "{stack.region}"
}}

# Remote state configuration
remote_state {{
  backend = "s3"

  config = {{
    bucket         = "{bucket}"
    key            = "{key}"
    region         = "{region}"
    encrypt        = true
    dynamodb_table = "{dynamodb_table}"
  }}

  generate = {{
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }}
}}

# Generate provider configuration
generate "provider" {{
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {{
  region = "{region}"

  default_tags {{
    tags = {{
      Environment  = "{stack.environment.value}"
      Project      = "{stack.project}"
      Organization = "{stack.organization}"
      ManagedBy    = "terragrunt"
      GeneratedBy  = "stack-forge"
    }}
  }}
}}
EOF
}}

# Inputs
inputs = {{
  environment = local.environment
  project     = local.project
  region      = local.region
}}
'''

    def _write_file(self, path: Path, content: str) -> None:
        """Write content to file, creating directories as needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        logger.info(f"Generated: {path}")


# Singleton instance
_engine: TemplateEngine | None = None


def get_template_engine() -> TemplateEngine:
    """Get singleton template engine instance."""
    global _engine
    if _engine is None:
        _engine = TemplateEngine()
    return _engine
