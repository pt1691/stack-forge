"""Configuration models for Stack Forge."""

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class CloudProvider(str, Enum):
    """Supported cloud providers."""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class Environment(str, Enum):
    """Standard deployment environments."""

    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class ResourceType(str, Enum):
    """Supported AWS resource types."""

    VPC = "vpc"
    SUBNET = "subnet"
    SECURITY_GROUP = "security_group"
    S3_BUCKET = "s3_bucket"
    RDS = "rds"
    EKS = "eks"
    LAMBDA = "lambda"
    IAM_ROLE = "iam_role"
    DYNAMODB = "dynamodb"
    SECRETS_MANAGER = "secrets_manager"
    ECR = "ecr"
    CLOUDWATCH = "cloudwatch"


class VariableType(str, Enum):
    """Terraform variable types."""

    STRING = "string"
    NUMBER = "number"
    BOOL = "bool"
    LIST = "list(string)"
    MAP = "map(string)"
    OBJECT = "object"


class Variable(BaseModel):
    """Terraform variable definition."""

    name: str
    type: VariableType = VariableType.STRING
    description: str = ""
    default: Any | None = None
    required: bool = True
    sensitive: bool = False
    validation_regex: str | None = None


class Output(BaseModel):
    """Terraform output definition."""

    name: str
    description: str = ""
    value: str
    sensitive: bool = False


class ResourceConfig(BaseModel):
    """Configuration for a single resource."""

    name: str
    type: ResourceType
    enabled: bool = True
    variables: dict[str, Any] = Field(default_factory=dict)
    tags: dict[str, str] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)


class StackConfig(BaseModel):
    """Configuration for an infrastructure stack."""

    name: str = Field(..., description="Unique stack name")
    description: str = ""
    provider: CloudProvider = CloudProvider.AWS
    region: str = Field(default="us-west-2")
    environment: Environment = Environment.DEV

    # Organization/Project settings
    organization: str = Field(default="myorg")
    project: str = Field(default="myproject")

    # Resources to include
    resources: list[ResourceConfig] = Field(default_factory=list)

    # Global tags applied to all resources
    global_tags: dict[str, str] = Field(default_factory=dict)

    # Backend configuration
    backend_type: str = "s3"
    backend_config: dict[str, str] = Field(default_factory=dict)

    # Terragrunt settings
    use_terragrunt: bool = True
    terragrunt_source: str | None = None

    def get_default_tags(self) -> dict[str, str]:
        """Get default tags with stack metadata."""
        return {
            "Environment": self.environment.value,
            "Project": self.project,
            "Organization": self.organization,
            "ManagedBy": "stack-forge",
            **self.global_tags,
        }


class TemplateMetadata(BaseModel):
    """Metadata for an infrastructure template."""

    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    provider: CloudProvider = CloudProvider.AWS
    resource_type: ResourceType

    # Template requirements
    required_variables: list[Variable] = Field(default_factory=list)
    optional_variables: list[Variable] = Field(default_factory=list)
    outputs: list[Output] = Field(default_factory=list)

    # Dependencies
    dependencies: list[str] = Field(default_factory=list)

    # Tags
    tags: list[str] = Field(default_factory=list)


class ProjectConfig(BaseModel):
    """Stack Forge project configuration (forge.yaml)."""

    version: str = "1.0"
    name: str
    organization: str

    # Default settings
    default_provider: CloudProvider = CloudProvider.AWS
    default_region: str = "us-west-2"

    # Environments
    environments: list[Environment] = Field(
        default_factory=lambda: [Environment.DEV, Environment.STAGING, Environment.PROD]
    )

    # Stacks
    stacks: list[StackConfig] = Field(default_factory=list)

    # Output directory
    output_dir: Path = Field(default=Path("infrastructure"))

    # Terragrunt settings
    terragrunt_root: Path = Field(default=Path("terragrunt"))
