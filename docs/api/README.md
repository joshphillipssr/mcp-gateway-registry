# MCP Gateway Registry - OpenAPI Specifications

This directory contains comprehensive OpenAPI (Swagger) specification files for all API categories in the MCP Gateway Registry. Each file is organized by functional area and includes complete endpoint definitions, request/response schemas, and authentication requirements.

## Quick Navigation

### API Categories

| File | Category | Endpoints | Auth Method |
|------|----------|-----------|-------------|
| [a2a-agent-management.yaml](a2a-agent-management.yaml) | A2A Agent Management | 8 | JWT Bearer Token |
| [anthropic-registry-api.yaml](anthropic-registry-api.yaml) | Anthropic MCP Registry API v0 | 6 | JWT Bearer Token |
| [authentication-login.yaml](authentication-login.yaml) | Authentication & Login | 7 | OAuth2 + Session Cookie |
| [server-management.yaml](server-management.yaml) | Server Management (UI + Admin) | 22 | Session Cookie + HTTP Basic Auth |
| [health-discovery.yaml](health-discovery.yaml) | Health Monitoring & Discovery | 4 | Session Cookie / None |

**Total Endpoints:** 49 API endpoints across all categories

---

## API Specifications Overview

### 1. A2A Agent Management API

**File:** `a2a-agent-management.yaml`

**Purpose:** Register, update, delete, and discover A2A (Agent-to-Agent) agents

**Key Endpoints:**
- `POST /api/agents/register` - Register a new agent
- `GET /api/agents` - List all agents with filtering
- `GET /api/agents/{path}` - Get single agent details
- `PUT /api/agents/{path}` - Update agent
- `DELETE /api/agents/{path}` - Delete agent
- `POST /api/agents/{path}/toggle` - Enable/disable agent
- `POST /api/agents/discover` - Discover agents by skills
- `POST /api/agents/discover/semantic` - Semantic agent discovery (NLP)

**Authentication:** JWT Bearer Token with `publish_agent` scope for write operations

**Use Cases:**
- Agent developers registering new agents
- Clients discovering agents by capability
- Semantic search for agent discovery

---

### 2. Anthropic MCP Registry API v0

**File:** `anthropic-registry-api.yaml`

**Purpose:** Standard Anthropic MCP Registry API for discovering MCP servers and A2A agents

**Key Endpoints (MCP Servers):**
- `GET /v0/servers` - List MCP servers with pagination
- `GET /v0/servers/{serverName}/versions` - List server versions
- `GET /v0/servers/{serverName}/versions/{version}` - Get server version details

**Key Endpoints (A2A Agents):**
- `GET /v0/agents` - List A2A agents in Anthropic format
- `GET /v0/agents/{agentName}/versions` - List agent versions
- `GET /v0/agents/{agentName}/versions/{version}` - Get agent version details

**Authentication:** JWT Bearer Token

**Use Cases:**
- Client tools listing available servers/agents
- Integration with Anthropic ecosystem
- Standard API compliance

---

### 3. Authentication & Login API

**File:** `authentication-login.yaml`

**Purpose:** OAuth2-based user authentication, login, logout, and provider management

**Key Endpoints:**
- `GET/POST /api/auth/login` - Display/submit login form
- `GET /api/auth/auth/{provider}` - OAuth2 redirect
- `GET /api/auth/auth/callback` - OAuth2 callback handler
- `GET/POST /api/auth/logout` - User logout
- `GET /api/auth/providers` - List available OAuth2 providers
- `GET /api/auth/me` - Get current user information

**Authentication:** Session Cookie + OAuth2

**Supported Providers:**
- Keycloak
- Cognito
- Generic OAuth2

**Use Cases:**
- User login/logout
- Session management
- User information retrieval
- Provider configuration

---

### 4. Server Management API

**File:** `server-management.yaml`

**Purpose:** Internal MCP server management, registration, administration, and JWT token generation

**UI Management Endpoints (Session Cookie):**
- `GET /api/` - Dashboard home
- `GET /api/servers` - Get servers as JSON
- `GET /api/server_details/{service_path}` - Get server details
- `GET /api/tools/{service_path}` - Get service tools
- `POST /api/register` - Register new service
- `GET/POST /api/edit/{service_path}` - Edit service
- `POST /api/toggle/{service_path}` - Toggle service status
- `POST /api/refresh/{service_path}` - Refresh service health

**Admin Operations (HTTP Basic Auth):**
- `POST /api/internal/register` - Internal service registration
- `POST /api/internal/remove` - Remove service
- `POST /api/internal/toggle` - Toggle service
- `POST /api/internal/healthcheck` - Health check all services
- `GET /api/internal/list` - List all services
- `POST /api/internal/add-to-groups` - Add server to groups
- `POST /api/internal/remove-from-groups` - Remove from groups
- `POST /api/internal/create-group` - Create user group
- `POST /api/internal/delete-group` - Delete user group
- `GET /api/internal/list-groups` - List all groups

**Token Management:**
- `GET /api/tokens` - Token generation page
- `POST /api/tokens/generate` - Generate JWT token
- `GET /api/admin/tokens` - Admin get Keycloak token

**Authentication:** Session Cookie (UI) + HTTP Basic Auth (Admin)

**Use Cases:**
- Dashboard service management
- Service registration and configuration
- Administrative operations
- JWT token generation for API access
- User group and permission management

---

### 5. Health Monitoring & Discovery API

**File:** `health-discovery.yaml`

**Purpose:** Real-time service health monitoring, statistics, and public MCP server discovery

**Health Monitoring:**
- `GET /api/health/ws/health_status` - HTTP health status
- `GET /api/health/ws/stats` - WebSocket statistics

**Public Discovery:**
- `GET /.well-known/mcp-servers` - Public server discovery (no auth required)

**Utility:**
- `GET /health` - Simple health check

**Authentication:** Session Cookie / None (public)

**Use Cases:**
- Real-time health monitoring in dashboards
- Load balancer health checks
- Public server discovery for external tools
- Performance statistics and monitoring

---

## Using These Specifications

### View in Swagger UI

Import any of these YAML files into Swagger UI:

```bash
# Option 1: Upload file
1. Go to https://editor.swagger.io
2. Click "File" > "Import File"
3. Select one of the YAML files

# Option 2: Provide URL (if hosted)
https://your-registry.example.com/docs
```

### Generate Client Libraries

Generate client code from these specifications:

```bash
# Generate Python client
openapi-generator-cli generate \
  -i docs/api/a2a-agent-management.yaml \
  -g python-client \
  -o ./python-client

# Generate JavaScript client
openapi-generator-cli generate \
  -i docs/api/server-management.yaml \
  -g javascript \
  -o ./js-client

# Generate Go client
openapi-generator-cli generate \
  -i docs/api/anthropic-registry-api.yaml \
  -g go-client \
  -o ./go-client
```

### Validate Specifications

```bash
# Validate individual spec
openapi-spec-validator docs/api/a2a-agent-management.yaml

# Validate all specs
for file in docs/api/*.yaml; do
  echo "Validating $file..."
  openapi-spec-validator "$file"
done
```

### Convert Formats

```bash
# Convert YAML to JSON
yq eval -o=json docs/api/a2a-agent-management.yaml > docs/api/a2a-agent-management.json

# Convert JSON to YAML (if needed)
yq eval docs/api/a2a-agent-management.json > docs/api/a2a-agent-management.yaml
```

---

## Authentication Methods

### 1. JWT Bearer Token

Used by: A2A Agent APIs, Anthropic Registry API v0

```bash
curl -H "Authorization: Bearer <jwt_token>" \
  http://localhost:7860/api/agents
```

**Token Sources:**
- Keycloak M2M service account (`mcp-gateway-m2m`)
- Generated via `/api/tokens/generate` endpoint
- Valid scopes: `publish_agent`, `modify_service`, `toggle_service`, etc.

### 2. Session Cookie

Used by: UI Server Management, Health Monitoring

```bash
curl -b "mcp_gateway_session=<session_value>" \
  http://localhost:7860/api/servers
```

**How to Obtain:**
1. Login via `/api/auth/login` (form submission)
2. Or OAuth2 via `/api/auth/auth/{provider}`
3. Browser automatically includes cookie in requests

### 3. HTTP Basic Auth

Used by: Internal Admin Endpoints

```bash
curl -u admin:password \
  http://localhost:7860/api/internal/list
```

**Credentials:**
- Username: `ADMIN_USER` environment variable
- Password: `ADMIN_PASSWORD` environment variable

### 4. Public (No Authentication)

Used by: Discovery endpoints, login form, health check

```bash
curl http://localhost:7860/.well-known/mcp-servers
curl http://localhost:7860/health
```

---

## Common Use Cases

### Register a New Agent

```bash
curl -X POST http://localhost:7860/api/agents/register \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d @agent-config.json
```

See: [a2a-agent-management.yaml](a2a-agent-management.yaml#/paths/~1api~1agents~1register)

### List All MCP Servers (Anthropic Format)

```bash
curl -X GET http://localhost:7860/v0/servers \
  -H "Authorization: Bearer <token>"
```

See: [anthropic-registry-api.yaml](anthropic-registry-api.yaml#/paths/~1v0~1servers)

### Generate JWT Token

```bash
curl -X POST http://localhost:7860/api/tokens/generate \
  -H "Cookie: mcp_gateway_session=<session>" \
  -H "Content-Type: application/json" \
  -d '{
    "requested_scopes": ["publish_agent"],
    "expires_in_hours": 8
  }'
```

See: [server-management.yaml](server-management.yaml#/paths/~1api~1tokens~1generate)

### Discover Servers (Public)

```bash
curl http://localhost:7860/.well-known/mcp-servers
```

See: [health-discovery.yaml](health-discovery.yaml#/paths/~1.well-known~1mcp-servers)

---

## Response Status Codes

### Success

- **200 OK** - Successful GET/POST operation
- **201 Created** - Resource successfully created
- **204 No Content** - Successful DELETE operation
- **303 See Other** - Form submission redirect

### Client Errors

- **400 Bad Request** - Invalid input or missing fields
- **401 Unauthorized** - Missing or invalid authentication
- **403 Forbidden** - User lacks required permissions
- **404 Not Found** - Resource doesn't exist
- **409 Conflict** - Resource conflict (e.g., duplicate path)
- **422 Unprocessable Entity** - Validation error

### Server Errors

- **500 Internal Server Error** - Unexpected server error
- **502 Bad Gateway** - Upstream service unreachable
- **503 Service Unavailable** - Service temporarily unavailable

---

## Error Response Format

All APIs return consistent error responses:

```json
{
  "detail": "Human-readable error message",
  "error_code": "optional_error_code",
  "request_id": "unique_request_identifier"
}
```

---

## Development Endpoints

When running locally, FastAPI automatically provides:

- **Swagger UI:** http://localhost:7860/docs
- **ReDoc:** http://localhost:7860/redoc
- **OpenAPI JSON:** http://localhost:7860/openapi.json

---

## File Structure

```
docs/api/
├── README.md                          # This file
├── a2a-agent-management.yaml          # Agent lifecycle management
├── anthropic-registry-api.yaml        # Anthropic API v0 compliance
├── authentication-login.yaml          # OAuth2 & session auth
├── server-management.yaml             # UI & admin operations
└── health-discovery.yaml              # Health & public discovery
```

---

## Integration Examples

### Python

```python
from openapi_client import ApiClient, Configuration
from openapi_client.apis import AgentAPI

config = Configuration(
    host="http://localhost:7860",
    api_key="<jwt_token>"
)
client = ApiClient(config)
agent_api = AgentAPI(client)

# List agents
agents = agent_api.list_agents()
```

### JavaScript/Node.js

```javascript
const OpenAPIClient = require('openapi-client');

const client = new OpenAPIClient({
  BASE: 'http://localhost:7860',
  TOKEN: '<jwt_token>'
});

// List agents
const agents = await client.agents.listAgents();
```

### cURL

See "Common Use Cases" section above for cURL examples.

---

## Support & Documentation

For more information:
- See [api-reference.md](../api-reference.md) for detailed endpoint documentation
- See [auth.md](../auth.md) for authentication details
- See [complete-setup-guide.md](../complete-setup-guide.md) for setup instructions

---

## Version

- **API Version:** v0.1.0 (Anthropic v0 spec) + custom extensions
- **Last Updated:** 2025-11-03
- **Status:** Production Ready

---
