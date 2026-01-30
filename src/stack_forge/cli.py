"""Command-line interface for Stack Forge."""

import logging
from pathlib import Path

import typer
import yaml
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from . import __version__
from .engine import get_template_engine
from .models import (
    CloudProvider,
    Environment,
    ProjectConfig,
    ResourceConfig,
    ResourceType,
    StackConfig,
)

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

console = Console()

app = typer.Typer(
    name="forge",
    help="🔨 Stack Forge - Self-Service Infrastructure Templating Engine",
    add_completion=False,
    rich_markup_mode="rich",
)


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        console.print(f"Stack Forge v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool | None = typer.Option(
        None, "--version", "-v", help="Show version and exit.", callback=version_callback, is_eager=True
    ),
    verbose: bool = typer.Option(False, "--verbose", "-V", help="Enable verbose logging."),
):
    """Stack Forge - Generate Terraform & Terragrunt configurations."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@app.command()
def init(
    name: str = typer.Option(..., "--name", "-n", help="Project name"),
    organization: str = typer.Option(..., "--org", "-o", help="Organization name"),
    provider: CloudProvider = typer.Option(CloudProvider.AWS, "--provider", "-p", help="Cloud provider"),
    region: str = typer.Option("us-west-2", "--region", "-r", help="Default region"),
    output_dir: Path = typer.Option(Path("."), "--output", help="Output directory for project files"),
):
    """
    🚀 Initialize a new Stack Forge project.

    Creates a forge.yaml configuration file.

    Example:

        forge init --name my-infra --org mycompany
    """
    config = ProjectConfig(
        name=name,
        organization=organization,
        default_provider=provider,
        default_region=region,
    )

    config_path = output_dir / "forge.yaml"

    if config_path.exists() and not typer.confirm(f"⚠️ {config_path} already exists. Overwrite?"):
        raise typer.Exit(0)

    # Create directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write configuration
    with open(config_path, "w") as f:
        yaml.dump(config.model_dump(mode="json"), f, default_flow_style=False, sort_keys=False)

    console.print(
        Panel(
            Text.from_markup(
                f"✅ Project initialized!\n\n"
                f"[cyan]Project:[/cyan] {name}\n"
                f"[cyan]Organization:[/cyan] {organization}\n"
                f"[cyan]Provider:[/cyan] {provider.value}\n"
                f"[cyan]Region:[/cyan] {region}\n\n"
                f"[dim]Configuration saved to:[/dim] {config_path}\n\n"
                f"Next steps:\n"
                f"  1. Edit [cyan]forge.yaml[/cyan] to add stacks\n"
                f"  2. Run [cyan]forge add-stack[/cyan] to add infrastructure\n"
                f"  3. Run [cyan]forge generate[/cyan] to create Terraform files"
            ),
            title="🔨 Stack Forge",
            border_style="green",
        )
    )


@app.command("add-stack")
def add_stack(
    name: str = typer.Option(..., "--name", "-n", help="Stack name"),
    environment: Environment = typer.Option(Environment.DEV, "--env", "-e", help="Environment"),
    config_file: Path = typer.Option(Path("forge.yaml"), "--config", "-c", help="Path to forge.yaml"),
):
    """
    ➕ Add a new stack to your project.

    Example:

        forge add-stack --name network --env dev
    """
    if not config_file.exists():
        console.print("[red]Error:[/red] forge.yaml not found. Run 'forge init' first.")
        raise typer.Exit(1)

    # Load existing config
    with open(config_file) as f:
        config_data = yaml.safe_load(f)

    config = ProjectConfig(**config_data)

    # Check if stack exists
    for stack in config.stacks:
        if stack.name == name and stack.environment == environment:
            console.print(f"[yellow]Warning:[/yellow] Stack '{name}' already exists for {environment.value}")
            raise typer.Exit(1)

    # Create new stack
    new_stack = StackConfig(
        name=name,
        environment=environment,
        provider=config.default_provider,
        region=config.default_region,
        organization=config.organization,
        project=config.name,
    )

    config.stacks.append(new_stack)

    # Save updated config
    with open(config_file, "w") as f:
        yaml.dump(config.model_dump(mode="json"), f, default_flow_style=False, sort_keys=False)

    console.print(f"✅ Stack [cyan]{name}[/cyan] added for [green]{environment.value}[/green] environment")
    console.print(f"\n[dim]Next: Add resources with[/dim] forge add-resource --stack {name}")


@app.command("add-resource")
def add_resource(
    stack_name: str = typer.Option(..., "--stack", "-s", help="Stack name"),
    resource_name: str = typer.Option(..., "--name", "-n", help="Resource name"),
    resource_type: ResourceType = typer.Option(..., "--type", "-t", help="Resource type"),
    environment: Environment = typer.Option(Environment.DEV, "--env", "-e", help="Environment"),
    config_file: Path = typer.Option(Path("forge.yaml"), "--config", "-c", help="Path to forge.yaml"),
):
    """
    🧱 Add a resource to a stack.

    Example:

        forge add-resource --stack network --name main-vpc --type vpc

        forge add-resource --stack data --name logs --type s3_bucket
    """
    if not config_file.exists():
        console.print("[red]Error:[/red] forge.yaml not found.")
        raise typer.Exit(1)

    # Load config
    with open(config_file) as f:
        config_data = yaml.safe_load(f)

    config = ProjectConfig(**config_data)

    # Find stack
    target_stack = None
    for stack in config.stacks:
        if stack.name == stack_name and stack.environment == environment:
            target_stack = stack
            break

    if not target_stack:
        console.print(f"[red]Error:[/red] Stack '{stack_name}' not found for {environment.value}")
        raise typer.Exit(1)

    # Add resource
    new_resource = ResourceConfig(
        name=resource_name,
        type=resource_type,
    )

    target_stack.resources.append(new_resource)

    # Save config
    with open(config_file, "w") as f:
        yaml.dump(config.model_dump(mode="json"), f, default_flow_style=False, sort_keys=False)

    console.print(
        f"✅ Resource [cyan]{resource_name}[/cyan] ({resource_type.value}) added to stack [green]{stack_name}[/green]"
    )


@app.command()
def generate(
    config_file: Path = typer.Option(Path("forge.yaml"), "--config", "-c", help="Path to forge.yaml"),
    output_dir: Path | None = typer.Option(None, "--output", "-o", help="Output directory (default: from config)"),
    stack_name: str | None = typer.Option(None, "--stack", "-s", help="Generate only this stack"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be generated without creating files"),
):
    """
    ⚡ Generate Terraform/Terragrunt configurations.

    Example:

        forge generate

        forge generate --stack network --output ./infrastructure
    """
    if not config_file.exists():
        console.print("[red]Error:[/red] forge.yaml not found.")
        raise typer.Exit(1)

    # Load config
    with open(config_file) as f:
        config_data = yaml.safe_load(f)

    config = ProjectConfig(**config_data)
    output_path = output_dir or config.output_dir

    # Filter stacks if specified
    stacks_to_generate = config.stacks
    if stack_name:
        stacks_to_generate = [s for s in config.stacks if s.name == stack_name]
        if not stacks_to_generate:
            console.print(f"[red]Error:[/red] Stack '{stack_name}' not found")
            raise typer.Exit(1)

    if not stacks_to_generate:
        console.print("[yellow]Warning:[/yellow] No stacks defined. Add stacks with 'forge add-stack'")
        raise typer.Exit(0)

    if dry_run:
        console.print("[cyan]Dry run mode - no files will be created[/cyan]\n")

    engine = get_template_engine()
    all_generated = []

    for stack in stacks_to_generate:
        console.print(f"\n🔨 Generating stack: [cyan]{stack.name}[/cyan] ({stack.environment.value})")

        if dry_run:
            # Show what would be generated
            tree = Tree(f"📁 {output_path}/{stack.name}/")
            tree.add("📄 providers.tf")
            tree.add("📄 backend.tf")
            tree.add("📄 main.tf")
            if stack.use_terragrunt:
                tree.add("📄 terragrunt.hcl")

            modules_branch = tree.add("📁 modules/")
            for resource in stack.resources:
                if resource.enabled:
                    resource_branch = modules_branch.add(f"📁 {resource.name}/")
                    resource_branch.add("📄 main.tf")
                    resource_branch.add("📄 variables.tf")
                    resource_branch.add("📄 outputs.tf")

            console.print(tree)
        else:
            generated = engine.render_stack(stack, output_path)
            all_generated.extend(generated)
            console.print(f"  ✅ Generated {len(generated)} files")

    if not dry_run:
        console.print(
            Panel(
                Text.from_markup(
                    f"✅ Generation complete!\n\n"
                    f"[cyan]Files generated:[/cyan] {len(all_generated)}\n"
                    f"[cyan]Output directory:[/cyan] {output_path}\n\n"
                    f"Next steps:\n"
                    f"  1. Review generated files in [cyan]{output_path}[/cyan]\n"
                    f"  2. Run [cyan]terraform init[/cyan] to initialize\n"
                    f"  3. Run [cyan]terraform plan[/cyan] to preview changes"
                ),
                title="🔨 Stack Forge",
                border_style="green",
            )
        )


@app.command("list-templates")
def list_templates():
    """
    📋 List available infrastructure templates.
    """
    table = Table(title="📋 Available Templates", box=box.ROUNDED, header_style="bold cyan")

    table.add_column("Type", style="bold")
    table.add_column("Description")
    table.add_column("Provider")

    templates = [
        (ResourceType.VPC, "Virtual Private Cloud with subnets, NAT gateways, and flow logs", "AWS"),
        (ResourceType.S3_BUCKET, "S3 bucket with versioning, encryption, and lifecycle rules", "AWS"),
        (ResourceType.EKS, "Managed Kubernetes cluster with node groups and IRSA", "AWS"),
        (ResourceType.RDS, "Relational database with Multi-AZ and automated backups", "AWS"),
        (ResourceType.DYNAMODB, "NoSQL database with auto-scaling", "AWS"),
        (ResourceType.LAMBDA, "Serverless function with IAM role and CloudWatch logs", "AWS"),
        (ResourceType.IAM_ROLE, "IAM role with customizable policies", "AWS"),
        (ResourceType.SECURITY_GROUP, "Security group with configurable rules", "AWS"),
        (ResourceType.SECRETS_MANAGER, "Secrets Manager secret with rotation", "AWS"),
        (ResourceType.ECR, "Elastic Container Registry repository", "AWS"),
    ]

    for resource_type, description, provider in templates:
        table.add_row(resource_type.value, description, provider)

    console.print(table)
    console.print("\n[dim]Use with: forge add-resource --type <type>[/dim]")


@app.command()
def show(config_file: Path = typer.Option(Path("forge.yaml"), "--config", "-c", help="Path to forge.yaml")):
    """
    👁️ Show project configuration.
    """
    if not config_file.exists():
        console.print("[red]Error:[/red] forge.yaml not found.")
        raise typer.Exit(1)

    with open(config_file) as f:
        config_data = yaml.safe_load(f)

    config = ProjectConfig(**config_data)

    # Project info
    console.print(
        Panel(
            Text.from_markup(
                f"[bold]Project:[/bold] {config.name}\n"
                f"[bold]Organization:[/bold] {config.organization}\n"
                f"[bold]Provider:[/bold] {config.default_provider.value}\n"
                f"[bold]Region:[/bold] {config.default_region}\n"
                f"[bold]Environments:[/bold] {', '.join(e.value for e in config.environments)}"
            ),
            title="📊 Project Configuration",
            border_style="cyan",
        )
    )

    if not config.stacks:
        console.print("\n[yellow]No stacks defined yet.[/yellow]")
        console.print("[dim]Add stacks with: forge add-stack --name <name>[/dim]")
        return

    # Stacks table
    table = Table(title="\n📚 Stacks", box=box.ROUNDED, header_style="bold cyan")

    table.add_column("Stack", style="bold")
    table.add_column("Environment")
    table.add_column("Region")
    table.add_column("Resources")
    table.add_column("Terragrunt")

    for stack in config.stacks:
        resource_count = len([r for r in stack.resources if r.enabled])
        table.add_row(
            stack.name,
            stack.environment.value,
            stack.region,
            str(resource_count),
            "✅" if stack.use_terragrunt else "❌",
        )

    console.print(table)


@app.command()
def validate(config_file: Path = typer.Option(Path("forge.yaml"), "--config", "-c", help="Path to forge.yaml")):
    """
    ✅ Validate project configuration.
    """
    if not config_file.exists():
        console.print("[red]Error:[/red] forge.yaml not found.")
        raise typer.Exit(1)

    errors = []
    warnings = []

    try:
        with open(config_file) as f:
            config_data = yaml.safe_load(f)

        config = ProjectConfig(**config_data)

        # Check for empty stacks
        for stack in config.stacks:
            if not stack.resources:
                warnings.append(f"Stack '{stack.name}' ({stack.environment.value}) has no resources")

            # Check for duplicate resource names
            names = [r.name for r in stack.resources]
            duplicates = {n for n in names if names.count(n) > 1}
            if duplicates:
                errors.append(f"Duplicate resource names in '{stack.name}': {duplicates}")

        # Check for duplicate stacks
        stack_keys = [(s.name, s.environment) for s in config.stacks]
        duplicate_stacks = {k for k in stack_keys if stack_keys.count(k) > 1}
        if duplicate_stacks:
            errors.append(f"Duplicate stacks: {duplicate_stacks}")

    except Exception as e:
        errors.append(f"Invalid configuration: {e}")

    # Display results
    if errors:
        console.print(Panel("\n".join(f"❌ {e}" for e in errors), title="Validation Errors", border_style="red"))
        raise typer.Exit(1)

    if warnings:
        console.print(Panel("\n".join(f"⚠️ {w}" for w in warnings), title="Validation Warnings", border_style="yellow"))

    console.print("✅ Configuration is valid!")


def cli_entrypoint():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    cli_entrypoint()
