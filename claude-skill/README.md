# Terragrunt Forge — Claude Skill Setup Guide

This directory contains a Claude skill for generating production-ready Terragrunt stacks for AWS, built from patterns in the [stack-forge](https://github.com/pt1691/stack-forge) project.

## What's Included

| File | Purpose |
|------|---------|
| `TERRAGRUNT_SKILL.md` | Claude Project knowledge file — attach this to a Claude project to give it deep Terragrunt/AWS expertise |
| `mcp_server.py` | MCP (Model Context Protocol) server — gives Claude tools to programmatically generate Terragrunt configs |

---

## Option 1: Claude Project Knowledge File

Upload `TERRAGRUNT_SKILL.md` as a knowledge file in your Claude project:

1. Go to [claude.ai](https://claude.ai) → **Projects**
2. Create a new project (e.g. "Terragrunt Infrastructure")
3. Click **Add content** → Upload `TERRAGRUNT_SKILL.md`
4. Optionally set custom instructions to reference it

Claude will now use the patterns from stack-forge whenever you ask it to create Terragrunt configs.

---

## Option 2: MCP Server (Tool-Based)

The MCP server exposes these tools to Claude:

| Tool | Description |
|------|-------------|
| `list_resource_types` | Show all supported AWS resource types |
| `generate_terragrunt_project` | Generate a complete multi-stack project |
| `generate_terraform_module` | Generate a single Terraform module |
| `generate_child_terragrunt_hcl` | Generate one terragrunt.hcl file |
| `get_environment_defaults` | Get recommended defaults per environment |

### Prerequisites

```bash
# From the stack-forge root
pip install -e ".[claude-skill]"
# or manually:
pip install "mcp[cli]" pydantic
```

> **Note:** Use the full path to the Python executable that has `mcp` installed.
> Using a bare `python` command will fail if VS Code or Claude Desktop can't resolve it from PATH.

### Configure for Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "terragrunt-forge": {
      "command": "/absolute/path/to/stack-forge/.venv/bin/python",
      "args": ["/absolute/path/to/stack-forge/claude-skill/mcp_server.py"],
      "env": {}
    }
  }
}
```

### Configure for VS Code (Claude in Copilot)

Open (or create) `.vscode/mcp.json` at your workspace root.

If your workspace root **is** the `stack-forge` folder:

```json
{
  "servers": {
    "terragrunt-forge": {
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["${workspaceFolder}/claude-skill/mcp_server.py"],
      "env": {}
    }
  }
}
```

If `stack-forge` is a **subfolder** of your workspace (e.g. `~/Documents/github/`):

```json
{
  "servers": {
    "terragrunt-forge": {
      "command": "${workspaceFolder}/stack-forge/.venv/bin/python",
      "args": ["${workspaceFolder}/stack-forge/claude-skill/mcp_server.py"],
      "env": {}
    }
  }
}
```

### Test Locally

```bash
cd stack-forge
.venv/bin/python claude-skill/mcp_server.py
```

---

## Usage Examples

### In Claude Chat (with knowledge file):

> "Create a Terragrunt stack with VPC, EKS, and RDS for my project 'analytics-platform' at org 'datateam', for dev and prod environments in us-east-1"

### With MCP tools:

Claude will call `generate_terragrunt_project` with:
```json
{
  "name": "analytics-platform",
  "organization": "datateam",
  "default_region": "us-east-1",
  "stacks_json": "[{\"name\": \"network\", \"environment\": \"dev\", \"resources\": [{\"name\": \"main-vpc\", \"type\": \"vpc\", \"variables\": {\"vpc_cidr\": \"10.0.0.0/16\"}}]}, ...]"
}
```

---

## Option 3: Both (Recommended)

Use **both** together for the best experience:
- The knowledge file gives Claude **deep context** about Terragrunt patterns, security practices, and conventions
- The MCP server gives Claude **tools to generate files** programmatically with consistent output

---

## Supported Resources

| Resource | Security Features |
|----------|------------------|
| VPC | Flow logs, private subnets, NAT gateways |
| EKS | KMS encryption, IRSA/OIDC, managed node groups |
| RDS | KMS encryption, multi-AZ, managed passwords, enhanced monitoring |
| S3 | Versioning, SSE encryption, public access blocked |
| DynamoDB | SSE encryption, PITR, auto-scaling |
| Lambda | Basic execution role, CloudWatch logs, VPC support |
| IAM Role | Permissions boundary, least-privilege |
| Security Group | Explicit ingress/egress rules |
| Secrets Manager | KMS encryption, rotation support |
| ECR | Image scanning, lifecycle policies, immutable tags |
