# Register Demo Servers Script

Automatically register demo MCP servers (AI Registry Tools, Current Time API) to the MCP Gateway Registry after deployment.

## Overview

The `register-demo-servers.sh` script provides automated registration of demo servers across different deployment environments:

- **Local Docker Compose**: Manual invocation after `docker compose up`
- **AWS ECS**: Integrated into `post-deployment-setup.sh`
- **AWS EKS (Helm)**: Can be run as a Kubernetes Job post-install hook

## Quick Start

### Local Docker Compose

After starting your local registry with `docker compose up`:

```bash
# Generate admin M2M token first
cd /home/ubuntu/repos/mcp-gateway-registry
bash cli/generate_ingress_token.sh

# Register demo servers
./scripts/register-demo-servers.sh \
  --registry-url http://localhost \
  --token-file .oauth-tokens/registry-admin-m2m-bot.json
```

### AWS ECS Deployment

The script is **automatically called** during post-deployment setup:

```bash
cd terraform/aws-ecs
terraform apply

# Post-deployment (includes server registration at step 8)
./scripts/post-deployment-setup.sh
```

To register servers manually after deployment:

```bash
# Get the registry URL from terraform outputs
REGISTRY_URL=$(cd terraform/aws-ecs && terraform output -raw registry_url)

# Register servers
./scripts/register-demo-servers.sh \
  --registry-url "$REGISTRY_URL" \
  --token-file .oauth-tokens/registry-admin-m2m-bot.json
```

### AWS EKS (Helm) Deployment

#### Option 1: Kubernetes Job (Recommended)

Create a post-install Helm hook job:

```yaml
# charts/mcp-gateway-registry-stack/templates/post-install-register-servers-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "mcp-gateway-registry-stack.fullname" . }}-register-servers
  labels:
    {{- include "mcp-gateway-registry-stack.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": post-install,post-upgrade
    "helm.sh/hook-weight": "10"
    "helm.sh/hook-delete-policy": before-hook-creation
spec:
  template:
    metadata:
      name: {{ include "mcp-gateway-registry-stack.fullname" . }}-register-servers
    spec:
      restartPolicy: Never
      containers:
      - name: register-servers
        image: "{{ .Values.registry.image.repository }}:{{ .Values.registry.image.tag }}"
        command:
          - /bin/bash
          - /scripts/register-demo-servers.sh
        args:
          - --registry-url
          - "http://{{ include "mcp-gateway-registry-stack.fullname" . }}-registry:{{ .Values.registry.service.port }}"
          - --token
          - "$(ADMIN_TOKEN)"
        env:
          - name: ADMIN_TOKEN
            valueFrom:
              secretKeyRef:
                name: {{ include "mcp-gateway-registry-stack.fullname" . }}-admin-token
                key: token
        volumeMounts:
          - name: scripts
            mountPath: /scripts
          - name: examples
            mountPath: /examples
      volumes:
        - name: scripts
          configMap:
            name: {{ include "mcp-gateway-registry-stack.fullname" . }}-scripts
            defaultMode: 0755
        - name: examples
          configMap:
            name: {{ include "mcp-gateway-registry-stack.fullname" . }}-server-examples
```

#### Option 2: Manual Registration

After Helm deployment:

```bash
# Port-forward to registry service
kubectl port-forward svc/mcp-gateway-registry-stack-registry 7860:7860

# In another terminal, register servers
./scripts/register-demo-servers.sh \
  --registry-url http://localhost:7860 \
  --token-file .oauth-tokens/registry-admin-m2m-bot.json
```

## Usage

```bash
./scripts/register-demo-servers.sh [OPTIONS]
```

### Options

| Option | Description | Example |
|--------|-------------|---------|
| `--registry-url URL` | Registry base URL | `--registry-url https://registry.example.com` |
| `--token-file PATH` | Path to admin M2M token JSON file | `--token-file .oauth-tokens/admin.json` |
| `--token TOKEN` | Admin M2M bearer token (alternative to --token-file) | `--token eyJ0eXAi...` |
| `--skip-airegistry` | Skip registering AI Registry Tools server | `--skip-airegistry` |
| `--skip-currenttime` | Skip registering Current Time API server | `--skip-currenttime` |
| `--dry-run` | Show what would be done without executing | `--dry-run` |
| `--help` | Show help message | `--help` |

### Environment Variables

Instead of command-line flags, you can use environment variables:

```bash
export REGISTRY_URL="https://registry.example.com"
export ADMIN_TOKEN="eyJ0eXAi..."

./scripts/register-demo-servers.sh
```

## Registered Servers

The script registers these demo servers by default:

### 1. AI Registry Tools
- **Path**: `/airegistry-tools/`
- **Config**: `cli/examples/airegistry.json`
- **Description**: Provides tools to discover and search servers, agents, and skills
- **Tags**: registry, discovery, search, semantic-search, tool-finder

### 2. Current Time API
- **Path**: `/currenttime/`
- **Config**: `cli/examples/currenttime.json`
- **Description**: Returns current server time in various formats and timezones
- **Tags**: time, timezone, datetime, api, utility

## Token Generation

### Local/Development

```bash
# Generate Entra ID M2M token
bash cli/generate_ingress_token.sh

# Token saved to: .oauth-tokens/registry-admin-m2m-bot.json
```

### AWS ECS

Tokens are automatically generated during `post-deployment-setup.sh` via Keycloak M2M service accounts.

### AWS EKS

Create a Kubernetes Secret with the admin M2M token:

```bash
# Generate token locally
bash cli/generate_ingress_token.sh

# Extract access token
ADMIN_TOKEN=$(jq -r '.access_token' .oauth-tokens/registry-admin-m2m-bot.json)

# Create Kubernetes secret
kubectl create secret generic mcp-gateway-registry-stack-admin-token \
  --from-literal=token="$ADMIN_TOKEN"
```

## Verification

After registration, verify servers are available:

```bash
# List all servers
curl -s "${REGISTRY_URL}/api/servers/list" | jq '.servers[] | {path, name}'

# Test AI Registry Tools
curl -X POST "${REGISTRY_URL}/airegistry-tools/mcp" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'

# Test Current Time API
curl -X POST "${REGISTRY_URL}/currenttime/mcp" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'
```

## Troubleshooting

### Token Issues

**Problem**: `No admin token provided`

**Solution**:
```bash
# Check token file exists and is valid
ls -la .oauth-tokens/registry-admin-m2m-bot.json
jq . .oauth-tokens/registry-admin-m2m-bot.json

# Regenerate if needed
bash cli/generate_ingress_token.sh
```

### Registry Not Ready

**Problem**: `Registry did not become ready in time`

**Solution**:
- Wait longer for services to start
- Check registry health: `curl ${REGISTRY_URL}/health`
- Review logs: `docker logs mcp-gateway-registry-registry-1`

### Registration Failed

**Problem**: `Failed to register: <server-name>`

**Solution**:
```bash
# Check registry API is accessible
curl -v "${REGISTRY_URL}/api/servers/list"

# Try manual registration
uv run python api/registry_management.py \
  --registry-url "${REGISTRY_URL}" \
  register --config cli/examples/airegistry.json
```

### Permission Denied

**Problem**: `bash: ./scripts/register-demo-servers.sh: Permission denied`

**Solution**:
```bash
chmod +x scripts/register-demo-servers.sh
```

## Adding Custom Servers

To register additional servers, create a JSON config file and update the script:

1. Create server config:
```json
{
  "server_name": "My Custom Server",
  "description": "Description of the server",
  "path": "/my-server/",
  "proxy_pass_url": "http://my-server:8000/",
  "auth_scheme": "none",
  "tags": ["custom", "demo"],
  "num_tools": 5,
  "license": "MIT"
}
```

2. Add to script:
```bash
_register_myserver() {
    log_step "Registering My Custom Server"
    local config_file="$EXAMPLES_DIR/my-server.json"
    _register_server "$config_file" "My Custom Server"
}

# Call in main()
_register_myserver || true
```

## Integration with CI/CD

### GitHub Actions

```yaml
- name: Register Demo Servers
  env:
    REGISTRY_URL: ${{ secrets.REGISTRY_URL }}
    ADMIN_TOKEN: ${{ secrets.ADMIN_M2M_TOKEN }}
  run: |
    ./scripts/register-demo-servers.sh
```

### AWS CodePipeline

Add to buildspec.yml:

```yaml
post_build:
  commands:
    - export REGISTRY_URL=$(aws ssm get-parameter --name /mcp-gateway/registry-url --query Parameter.Value --output text)
    - export ADMIN_TOKEN=$(aws secretsmanager get-secret-value --secret-id mcp-gateway-admin-token --query SecretString --output text)
    - ./scripts/register-demo-servers.sh
```

## See Also

- [ECS Deployment Guide](../terraform/aws-ecs/README.md)
- [Helm Chart Documentation](../charts/mcp-gateway-registry-stack/README.md)
- [Server Registration API](../api/README.md)
- [Service Management](../cli/README.md)
