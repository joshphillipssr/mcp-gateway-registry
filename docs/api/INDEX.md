# MCP Gateway Registry - API Specifications Index

Complete OpenAPI/Swagger specifications for all 49 API endpoints organized by category.

## Overview

| File | Category | Endpoints | Auth | Status |
|------|----------|-----------|------|--------|
| [README.md](README.md) | Documentation Hub | — | — | Complete |
| [a2a-agent-management.yaml](a2a-agent-management.yaml) | A2A Agent Management | 8 | JWT Bearer | ✅ |
| [anthropic-registry-api.yaml](anthropic-registry-api.yaml) | Anthropic Registry v0 | 6 | JWT Bearer | ✅ |
| [authentication-login.yaml](authentication-login.yaml) | Authentication & Login | 7 | OAuth2/Session | ✅ |
| [server-management.yaml](server-management.yaml) | Server Management | 22 | Session/Basic | ✅ |
| [health-discovery.yaml](health-discovery.yaml) | Health & Discovery | 4 | Session/None | ✅ |

**Total:** 49 endpoints across 5 categories

---

## Quick Start

1. **View in Swagger UI:**
   - Upload any `.yaml` file to https://editor.swagger.io
   - Or access locally: http://localhost:7860/docs

2. **Generate Clients:**
   ```bash
   openapi-generator-cli generate -i docs/api/a2a-agent-management.yaml -g python-client -o ./client
   ```

3. **Validate Specs:**
   ```bash
   openapi-spec-validator docs/api/*.yaml
   ```

---

## File Descriptions

### README.md
- Comprehensive guide to all API specifications
- Authentication method details
- Common use cases and examples
- Client generation instructions
- Integration examples

### a2a-agent-management.yaml
**8 Endpoints for Agent Lifecycle Management**
- Agent registration and updates
- Agent listing and discovery
- Skill-based discovery
- Semantic (NLP) discovery

### anthropic-registry-api.yaml
**6 Endpoints for Anthropic-compliant API**
- MCP server listing and discovery
- A2A agent discovery in Anthropic format
- Version management
- Cursor-based pagination

### authentication-login.yaml
**7 Endpoints for User Authentication**
- OAuth2 integration (Keycloak, Cognito)
- Form-based login
- Session management
- User information retrieval
- Provider configuration

### server-management.yaml
**22 Endpoints for MCP Server Administration**
- Dashboard and UI operations (10 endpoints)
- Admin operations (12 endpoints)
- Service registration and configuration
- Group and permission management
- JWT token generation

### health-discovery.yaml
**4 Endpoints for Monitoring and Discovery**
- Real-time health status
- WebSocket statistics
- Public server discovery
- Health check endpoint

---

## Authentication Summary

| Auth Type | Used By | Header/Cookie | Endpoints |
|-----------|---------|---------------|-----------|
| JWT Bearer | A2A Agents, Anthropic API | `Authorization: Bearer <token>` | 14 |
| Session Cookie | UI, Health Monitoring | `mcp_gateway_session=<value>` | 20 |
| HTTP Basic | Admin Operations | `Authorization: Basic <base64>` | 12 |
| Public/None | Discovery, Health | None | 3 |

---

## Total Endpoint Count

```
A2A Agent Management:        8 endpoints
Anthropic Registry API v0:   6 endpoints
Authentication & Login:      7 endpoints
Server Management:          22 endpoints
Health & Discovery:          4 endpoints
─────────────────────────────────────────
TOTAL:                      49 endpoints
```

---

## Related Documentation

- [Complete API Reference](../api-reference.md) - Detailed endpoint documentation
- [Authentication Guide](../auth.md) - Authentication details and flows
- [Setup Guide](../complete-setup-guide.md) - Installation and configuration

---

## Tools & Resources

- **Editor:** https://editor.swagger.io
- **Validator:** `openapi-spec-validator`
- **Generator:** `openapi-generator-cli`
- **Local Docs:** http://localhost:7860/docs
- **ReDoc:** http://localhost:7860/redoc

---

## Support

For questions or issues with these specifications, refer to:
- Main API documentation in `docs/api-reference.md`
- Architecture documentation in `docs/`
- GitHub issues in the repository

---

*Last updated: 2025-11-03*
