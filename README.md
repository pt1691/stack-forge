# 🔨 Stack Forge

[![CI](https://github.com/pt1691/stack-forge/actions/workflows/ci.yml/badge.svg)](https://github.com/pt1691/stack-forge/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/stack-forge-infra.svg)](https://pypi.org/project/stack-forge-infra/)
[![PyPI downloads](https://img.shields.io/pypi/dm/stack-forge-infra.svg)](https://pypi.org/project/stack-forge-infra/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **Self-Service Infrastructure Templating Engine for Terraform & Terragrunt**

A CLI tool that generates production-ready Terraform and Terragrunt configurations from reusable templates. Stop writing boilerplate infrastructure code and start deploying in minutes.

## ⚡ 30-Second Quick Start

```bash
pip install stack-forge-infra
forge list-templates  # See available templates!
```

**That's it!** Now create your first infrastructure:

```bash
mkdir my-infra && cd my-infra
forge init --name my-app --org mycompany
forge add-stack --name network --env dev
forge add-resource --stack network --name main-vpc --type vpc
forge generate  # Creates Terraform files!
```

---

## ✨ Features

- 🚀 **Quick Setup** - Generate complete infrastructure stacks with a few commands
- 📦 **Pre-built Templates** - VPC, EKS, S3, RDS, Lambda, and more
- 🔧 **Terragrunt Support** - DRY configurations with Terragrunt integration
- 🏷️ **Consistent Tagging** - Automatic resource tagging across all resources
- 🔒 **Security Best Practices** - Templates follow AWS security guidelines
- 📝 **Customizable** - Extend with your own templates

## 🚀 Installation

```bash
pip install stack-forge-infra
```

Or with [pipx](https://pipx.pypa.io/) for an isolated global install:

```bash
pipx install stack-forge-infra
```

## 📖 Workflow Example

```bash
# 1. Create a new project
mkdir my-platform && cd my-platform
forge init --name my-platform --org acmecorp

# 2. Add a stack (environment + resource group)
forge add-stack --name network --env dev

# 3. Add resources to the stack
forge add-resource --stack network --name main-vpc --type vpc
forge add-resource --stack network --name logs --type s3_bucket

# 4. Generate Terraform files
forge generate

# 5. Review what was created
tree infrastructure/
```

## 📋 Commands

| Command | Description |
|---------|-------------|
| `forge init` | Initialize a new Stack Forge project |
| `forge add-stack` | Add a new infrastructure stack |
| `forge add-resource` | Add a resource to a stack |
| `forge generate` | Generate Terraform/Terragrunt files |
| `forge show` | Show project configuration |
| `forge validate` | Validate configuration |
| `forge list-templates` | List available templates |

## 📦 Available Templates

| Template | Description |
|----------|-------------|
| `vpc` | VPC with public/private subnets, NAT gateways, flow logs |
| `s3_bucket` | S3 bucket with versioning, encryption, lifecycle rules |
| `eks` | EKS cluster with managed node groups, IRSA, encryption |
| `rds` | RDS instance with Multi-AZ, automated backups |
| `dynamodb` | DynamoDB table with auto-scaling |
| `lambda` | Lambda function with IAM role, CloudWatch logs |
| `iam_role` | IAM role with customizable policies |
| `security_group` | Security group with configurable rules |
| `secrets_manager` | Secrets Manager with rotation |
| `ecr` | ECR repository with lifecycle policies |

## 📁 Generated Structure

```
infrastructure/
├── network/
│   ├── providers.tf          # AWS provider configuration
│   ├── backend.tf            # S3 backend for state
│   ├── main.tf               # Module calls
│   ├── terragrunt.hcl        # Terragrunt configuration
│   └── modules/
│       ├── main-vpc/
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       └── logs/
│           ├── main.tf
│           ├── variables.tf
│           └── outputs.tf
```

## ⚙️ Configuration (forge.yaml)

```yaml
version: "1.0"
name: my-platform
organization: mycompany
default_provider: aws
default_region: us-west-2
environments:
  - dev
  - staging
  - prod

stacks:
  - name: network
    environment: dev
    region: us-west-2
    use_terragrunt: true
    resources:
      - name: main-vpc
        type: vpc
        variables:
          vpc_cidr: "10.0.0.0/16"
          az_count: 3
          enable_nat_gateway: true
          
      - name: logs
        type: s3_bucket
        variables:
          versioning_enabled: true
```

## 🤖 Claude AI Integration

Stack Forge ships with a `claude-skill/` directory that supercharges your Terragrunt workflow with Claude AI in two ways:

### 1. Claude Project Knowledge File
Upload `claude-skill/TERRAGRUNT_SKILL.md` to a [Claude Project](https://claude.ai) to give Claude deep, project-specific knowledge about:
- All 10 resource types and their variables/outputs
- Terragrunt directory structure conventions
- Environment-specific defaults (dev / staging / prod)
- Security best practices and tagging conventions
- Dependency chains between resources

### 2. MCP Server (Tool Use)
The `claude-skill/mcp_server.py` is a [Model Context Protocol](https://modelcontextprotocol.io/) server that exposes 5 tools Claude can call to **generate Terragrunt configs programmatically**:

| Tool | Description |
|------|-------------|
| `list_resource_types` | List all supported resource types with descriptions |
| `generate_terragrunt_project` | Generate a complete multi-environment Terragrunt project |
| `generate_terraform_module` | Generate a standalone Terraform module for a resource |
| `generate_child_terragrunt_hcl` | Generate a single child `terragrunt.hcl` |
| `get_environment_defaults` | Get recommended variable defaults per environment |

**Quick setup (Claude Desktop):**

```bash
pip install "mcp[cli]" pydantic
```

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "terragrunt-forge": {
      "command": "python",
      "args": ["/path/to/stack-forge/claude-skill/mcp_server.py"]
    }
  }
}
```

See [claude-skill/README.md](claude-skill/README.md) for full setup instructions including VS Code configuration.

## 🔧 Custom Templates

Add your own templates in `~/.stack-forge/templates/`:

```
~/.stack-forge/templates/
└── my_custom_resource/
    ├── main.tf.j2
    ├── variables.tf.j2
    └── outputs.tf.j2
```

Templates use Jinja2 with these available variables:
- `{{ name }}` - Resource name
- `{{ environment }}` - Environment (dev/staging/prod)
- `{{ region }}` - AWS region
- `{{ variables }}` - Resource-specific variables
- `{{ tags }}` - Merged tags

## 📝 Best Practices

1. **Use environments** - Create separate stacks for dev/staging/prod
2. **DRY with Terragrunt** - Enable `use_terragrunt: true` for DRY configs
3. **Consistent naming** - Use descriptive stack and resource names
4. **Tag everything** - Define `global_tags` in your project config

## 🧪 Development

```bash
# Clone and install in editable mode
git clone https://github.com/pt1691/stack-forge.git
cd stack-forge
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .
```

See [RELEASING.md](RELEASING.md) for the release process.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙋‍♂️ Author

**Praneeth Turlapati**
- LinkedIn: [linkedin.com/in/praneeth-turlapati](https://linkedin.com/in/praneeth-turlapati)
- GitHub: [github.com/pt1691](https://github.com/pt1691)

---

⭐ **If you find this useful, please star the repository!**
