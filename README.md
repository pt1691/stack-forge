# 🔨 Stack Forge

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **Self-Service Infrastructure Templating Engine for Terraform & Terragrunt**

A CLI tool that generates production-ready Terraform and Terragrunt configurations from reusable templates. Stop writing boilerplate infrastructure code and start deploying in minutes.

## ✨ Features

- 🚀 **Quick Setup** - Generate complete infrastructure stacks with a few commands
- 📦 **Pre-built Templates** - VPC, EKS, S3, RDS, Lambda, and more
- 🔧 **Terragrunt Support** - DRY configurations with Terragrunt integration
- 🏷️ **Consistent Tagging** - Automatic resource tagging across all resources
- 🔒 **Security Best Practices** - Templates follow AWS security guidelines
- 📝 **Customizable** - Extend with your own templates

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/praneethturlapati/stack-forge.git
cd stack-forge

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install -e .
```

### Create Your First Infrastructure

```bash
# Initialize a new project
forge init --name my-platform --org mycompany

# Add a network stack
forge add-stack --name network --env dev

# Add resources to the stack
forge add-resource --stack network --name main-vpc --type vpc
forge add-resource --stack network --name logs --type s3_bucket

# Generate Terraform files
forge generate

# Review generated files
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
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .
```

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙋‍♂️ Author

**Praneeth Turlapati**
- LinkedIn: [linkedin.com/in/praneeth-turlapati](https://linkedin.com/in/praneeth-turlapati)
- GitHub: [github.com/pt1691](https://github.com/pt1691)

---

⭐ **If you find this useful, please star the repository!**
