# Cookie Security Design

## Overview

This document explains the design decisions behind the session cookie security implementation in the MCP Gateway Registry, particularly regarding the use of domain cookies for cross-subdomain authentication.

## Background

The MCP Gateway Registry supports authentication through both traditional username/password and OAuth2 providers. In deployments where the auth server and registry are on different subdomains (e.g., `auth.example.com` and `registry.example.com`), session cookies must be shared across these subdomains for seamless authentication.

## Design Decision: Single-Tenant Architecture

This implementation is designed for **single-tenant deployments** where:
- All subdomains are owned and controlled by a single organization
- Cross-subdomain cookie sharing is a desired feature, not a security risk
- Users authenticate once and access multiple services on different subdomains

## Cookie Security Configuration

### Environment Variables

Two key environment variables control cookie security behavior:

1. **`SESSION_COOKIE_SECURE`** (default: `false`)
   - Set to `true` in production deployments with HTTPS
   - When `true`, cookies are only transmitted over HTTPS connections
   - Prevents man-in-the-middle (MITM) attacks and session hijacking
   - **Production Requirement:** MUST be set to `true` when deployed with HTTPS

2. **`SESSION_COOKIE_DOMAIN`** (default: `None`)
   - When set (e.g., `.example.com`), enables cross-subdomain cookie sharing
   - Must start with a dot (`.`) to match all subdomains
   - When `None`, cookies are scoped to the exact host that sets them
   - **Format:** `.example.com` (note the leading dot)

### Cookie Security Flags

The implementation sets the following security flags on all session cookies:

| Flag | Value | Purpose |
|------|-------|---------|
| `httponly` | `True` | Prevents JavaScript access, mitigating XSS attacks |
| `samesite` | `"lax"` | Provides CSRF protection while allowing cross-site navigation |
| `secure` | Configurable | Ensures HTTPS-only transmission in production |
| `path` | `"/"` | Explicitly scopes cookie to entire domain |
| `domain` | Configurable | Enables cross-subdomain sharing when needed |

## Security Considerations

### ✅ Safe Deployment Scenarios

This design is **SAFE** for:

1. **Single-Tenant Production Deployments**
   - Example: `auth.company.com` and `registry.company.com`
   - All subdomains owned by the same organization
   - Configuration:
     ```bash
     SESSION_COOKIE_SECURE=true
     SESSION_COOKIE_DOMAIN=.company.com
     ```

2. **Development and Testing**
   - Local development on `localhost`
   - Configuration:
     ```bash
     SESSION_COOKIE_SECURE=false
     SESSION_COOKIE_DOMAIN=  # Leave unset
     ```

### ⚠️ Unsafe Deployment Scenarios

This design is **NOT SAFE** for:

1. **Multi-Tenant SaaS Deployments**
   - Example: `customer1.saas-platform.com` and `customer2.saas-platform.com`
   - **Risk:** Setting `SESSION_COOKIE_DOMAIN=.saas-platform.com` would allow:
     - Customer A to access Customer B's sessions
     - Cross-tenant authentication bypass
     - Serious data breach potential

2. **Shared Hosting Environments**
   - Multiple organizations sharing the same root domain
   - **Risk:** Similar to multi-tenant scenario

### Alternative Solutions for Multi-Tenant

If you need multi-tenant deployment, consider these alternatives:

1. **Token-Based Authentication**
   - Use JWT tokens passed via headers instead of cookies
   - Tokens explicitly scoped to each tenant
   - No domain-sharing concerns

2. **Separate Auth Domains per Tenant**
   - `customer1-auth.platform.com` and `customer1-app.platform.com`
   - Different root domains prevent cookie sharing between tenants

3. **Reverse Proxy with Path-Based Routing**
   - Single domain with path-based service routing
   - Example: `platform.com/auth` and `platform.com/registry`
   - No cross-subdomain cookie requirements

4. **Centralized OAuth Flow**
   - OAuth server on separate domain
   - Token exchange instead of session cookies
   - Better tenant isolation

## Attack Scenarios Mitigated

### 1. Session Hijacking (MITM)
- **Threat:** Attacker intercepts session cookies over unencrypted HTTP
- **Mitigation:** `secure=True` flag in production
- **Status:** ✅ Mitigated when `SESSION_COOKIE_SECURE=true`

### 2. Cross-Site Scripting (XSS)
- **Threat:** Malicious JavaScript reads session cookies
- **Mitigation:** `httponly=True` flag
- **Status:** ✅ Always mitigated

### 3. Cross-Site Request Forgery (CSRF)
- **Threat:** Malicious site triggers authenticated requests
- **Mitigation:** `samesite="lax"` flag
- **Status:** ✅ Always mitigated

### 4. Subdomain Cookie Theft (Single-Tenant)
- **Threat:** Attacker controls a subdomain and steals cookies
- **Mitigation:** Only valid in trusted single-tenant environments
- **Status:** ⚠️ Acceptable risk for single-tenant deployments

## Production Deployment Checklist

Before deploying to production:

- [ ] Set `SESSION_COOKIE_SECURE=true` in environment
- [ ] Verify HTTPS is properly configured and enforced
- [ ] Set `SESSION_COOKIE_DOMAIN` to your root domain (e.g., `.example.com`)
- [ ] Confirm you are deploying in a single-tenant architecture
- [ ] Test cross-subdomain authentication between auth and registry services
- [ ] Verify cookies are NOT transmitted over HTTP
- [ ] Review logs for any cookie-related warnings

### Example Production Configuration

```bash
# .env for production
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_DOMAIN=.example.com
SESSION_COOKIE_NAME=mcp_gateway_session
SESSION_MAX_AGE_SECONDS=28800  # 8 hours
AUTH_SERVER_URL=http://auth-server:8888  # Internal URL
AUTH_SERVER_EXTERNAL_URL=https://auth.example.com  # External URL
```

## Code Implementation

The cookie security implementation is found in:

- **Configuration:** [`registry/core/config.py`](../registry/core/config.py) (lines 25-26)
  - `session_cookie_secure`: Controls HTTPS-only flag
  - `session_cookie_domain`: Controls cross-subdomain sharing

- **Cookie Setting:** [`registry/auth/routes.py`](../registry/auth/routes.py) (lines 139-158)
  - Comprehensive security comments explaining single-tenant model
  - Conditional domain attribute application
  - All security flags properly set

## Monitoring and Validation

### Runtime Validation

The application logs cookie configuration for debugging:

```python
logger.info(f"User '{username}' logged in successfully.")
```

### Security Auditing

Periodically review:
1. Cookie flags are properly set in browser developer tools
2. Cookies are NOT transmitted over HTTP in production
3. `secure` flag is enabled in production environments
4. Domain scope matches your deployment architecture

### Browser Developer Tools Verification

In your browser's developer tools (Application/Storage → Cookies), verify:

| Property | Expected Value | Notes |
|----------|---------------|-------|
| `Secure` | ✓ (checked) | Production only |
| `HttpOnly` | ✓ (checked) | Always |
| `SameSite` | `Lax` | Always |
| `Domain` | `.example.com` | If configured |
| `Path` | `/` | Always |

## Version History

- **2025-12-10:** Initial design document created
  - Added `session_cookie_secure` configuration
  - Added `session_cookie_domain` configuration
  - Implemented comprehensive cookie security in `registry/auth/routes.py`
  - Documented single-tenant security model and multi-tenant warnings

## References

- [OWASP Session Management Cheat Sheet](https://cheatsheetsecurity.org/cheatsheets/session-management-cheat-sheet)
- [MDN: Set-Cookie HTTP Header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie)
- [RFC 6265: HTTP State Management Mechanism](https://datatracker.ietf.org/doc/html/rfc6265)
- Security Analysis: [`.scratchpad/pr-258-security-analysis.md`](../.scratchpad/pr-258-security-analysis.md)

## Contact

For questions or security concerns regarding this implementation, please:
- Open an issue in the GitHub repository
- Tag the issue with `security` label
- Provide details about your deployment scenario
