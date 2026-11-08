# Challenge Lab 2: Security Hardening and Production Configuration

**Reference**: Chapter 8, Section 8.7 (second challenge)

SupportFlow ships with:

- A single hardcoded demo API key
- No rate limiting
- No role separation
- Plain HTTP

That is fine for a lab but not for production. In this challenge you fix each of these.

**Prerequisite**: Finish [Challenge Lab 1](challenge-1-debug-and-fix.md) first. If the approval logic is still broken, an auth layer only hides the bug.

**Claude Code features to use here**:

- A `.claude/rules/security.md` rule file. Claude checks every generated change against the OWASP Top 10.
- A PreToolUse secret-scanning hook. It stops a key from reaching a commit.
- `/sandbox` (Section 8.3). It keeps hardening experiments inside the project.

---

**Duration**: 3-4 hours
**Difficulty**: Advanced
**Focus**: Security, Production Readiness, Best Practices

### Learning Objectives

By completing this lab, you will:
- Implement security best practices for API applications
- Configure production-grade environment management
- Add authentication and authorization improvements
- Understand common web application vulnerabilities
- Use Claude Code for security code reviews

### Prerequisites

- Completed Challenge Lab 1 (bugs fixed)
- Understanding of web security concepts
- Familiarity with environment variables and secrets management

### Implementation Hints: Use Claude Code's Security Features

**Use these Claude Code features:**

- **Create security rules** in `.claude/rules/security.md`:
  - "Never commit secrets or API keys to git"
  - "Always use parameterized queries to prevent SQL injection"
  - "Validate all inputs with Pydantic before processing"
  - "Hash passwords with bcrypt, never store plaintext"
  - "Use timing-safe comparison for authentication checks"

- **Build security sub-agents** for code review. Define each in `.claude/agents/`. Copy [`../../code-examples/subagents/security-reviewer.md`](../../code-examples/subagents/security-reviewer.md) as a starting point and adapt it:
  - `security-auditor`: full OWASP Top 10 audit pass
  - `penetration-tester`: adversarial probing of the running API
  - `compliance-auditor`: regulatory requirements (GDPR, SOC 2)

- **Implement security validation hooks** in `.claude/hooks/`:
  - Create `check-secrets.sh` to scan commits for leaked credentials using `git-secrets` or `trufflehog`
  - Add `validate-dependencies.sh` to run `pip-audit -r requirements.txt` on Python packages. (`safety check` is deprecated. Its replacement, `safety scan`, needs an account.)
  - Use `security-scan.sh` to run Bandit static analysis before merges
  - Add `audit-log-validator.sh` to check that all sensitive operations are logged

- **Use MCP for security integrations**:
  - Connect to HashiCorp Vault MCP for secrets retrieval (never hardcode)
  - Integrate with Snyk or GitHub Security Advisories for vulnerability scanning
  - Use SIEM MCP to send audit logs to Splunk/ELK for monitoring
  - Connect to OWASP Dependency-Check for continuous security assessment

**Example Claude Code security workflow:**
```text
1. Ask Claude: "Review API authentication for security vulnerabilities"
2. Security-auditor agent scans code for OWASP Top 10 issues
3. Claude suggests: bcrypt hashing, timing-safe comparison, rate limiting
4. Implement fixes with Claude's guidance
5. Pre-commit hook runs Bandit scan, blocks commit if high-severity issues found
6. Claude updates security documentation automatically
```

**Security-specific prompts to use:**
- "Perform security audit on authentication code looking for timing attacks, injection vulnerabilities, and weak cryptography"
- "Review all database queries for SQL injection risks and suggest parameterization improvements"
- "Scan codebase for hardcoded secrets and suggest environment variable replacements"
- "Generate security test cases for input validation covering XSS, CSRF, and injection attacks"

### Challenge Tasks

#### Task 1: Implement Secure API Key Management

**Goal**: Replace hardcoded API key with secure secret management.

**Claude Code Prompt**:
```text
Implement secure API key management for production:

1. Remove hardcoded "demo-key-12345" from code
2. Create an API key generation system:
   - Generate cryptographically secure random API keys
   - Store hashed API keys in database (not plaintext)
   - Implement key creation endpoint for admins only
   - Add key revocation capability

3. Update authentication to:
   - Hash incoming API keys before comparison
   - Use timing-safe comparison to prevent timing attacks
   - Log authentication attempts (success and failure)
   - Implement rate limiting on failed attempts

4. Create key management CLI scripts under scripts/:
   - scripts/generate_api_key.py: generate new API keys
   - scripts/revoke_api_key.py: revoke a key by ID
   - List active keys
   - Rotate keys

5. Update documentation with key management instructions

Use bcrypt or argon2 for key hashing, not plain comparison.
```

**Security Requirements**:
- [ ] No hardcoded API keys in code
- [ ] Keys stored as hashes in database
- [ ] Keys generated with 32+ bytes of entropy
- [ ] Timing-safe comparison prevents timing attacks
- [ ] Failed auth attempts logged

**Validation**:
```bash
# Test key generation
docker exec supportflow python3 scripts/generate_api_key.py

# Test with new key
curl -H "X-API-Key: <new-key>" http://localhost:8000/responses/pending

# Test revoked key fails
docker exec supportflow python3 scripts/revoke_api_key.py <key-id>
curl -H "X-API-Key: <revoked-key>" http://localhost:8000/responses/pending
# Should return 401 Unauthorized
```

#### Task 2: Implement Role-Based Access Control (RBAC)

**Goal**: Add different permission levels for API users.

**Claude Code Prompt**:
```text
Implement role-based access control:

1. Define user roles:
   - VIEWER: Can only read tickets and responses
   - AGENT: Can create tickets and approve responses
   - ADMIN: Full access including user management

2. Create User and Role models in database:
   - User: id, email, role, api_key_hash, created_at
   - Link API keys to users

3. Add role-based decorators for endpoints:
   - @require_role("agent") for ticket submission
   - @require_role("agent") for response approval
   - @require_role("admin") for key management

4. Update authentication to check permissions:
   - Verify user has required role for endpoint
   - Return 403 Forbidden for insufficient permissions
   - Log permission denied attempts

5. Create admin endpoints:
   - POST /admin/users - Create users
   - GET /admin/users - List users
   - PUT /admin/users/{id}/role - Change user role
   - DELETE /admin/users/{id} - Deactivate user

Test RBAC with different role users.
```

**Validation**:
- [ ] Three distinct roles implemented
- [ ] VIEWER cannot approve responses
- [ ] AGENT cannot access admin endpoints
- [ ] Permission checks on all endpoints
- [ ] Audit logs record permission denials

#### Task 3: Add Rate Limiting and Request Throttling

**Goal**: Prevent API abuse and DoS attacks.

**Claude Code Prompt**:
```text
Implement rate limiting to protect the API:

1. Add rate limiting middleware using slowapi or similar:
   - 100 requests per minute per API key
   - 10 ticket submissions per minute per API key
   - 5 login attempts per minute per IP

2. Implement different limits for different roles:
   - VIEWER: 50 requests/minute
   - AGENT: 200 requests/minute
   - ADMIN: 1000 requests/minute

3. Add rate limit headers to responses:
   - X-RateLimit-Limit: Maximum requests
   - X-RateLimit-Remaining: Requests left
   - X-RateLimit-Reset: When limit resets

4. Store rate limit state in Redis (or in-memory for now)

5. Return 429 Too Many Requests when limit exceeded

6. Add rate limit bypass for health checks

Test rate limiting by submitting many rapid requests.
```

**Implementation Tip**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/tickets")
@limiter.limit("10/minute")
def submit_ticket(...):
    ...
```

**Validation**:
- [ ] Rate limits enforced per API key
- [ ] 429 status returned when exceeded
- [ ] Rate limit headers in responses
- [ ] Different limits for different roles
- [ ] Health check endpoint not rate limited

#### Task 4: Input Validation and Sanitization

**Goal**: Prevent injection attacks and validate all inputs.

**Claude Code Prompt**:
```text
Enhance input validation and sanitization:

1. Review all API endpoints for input validation gaps
2. Add thorough Pydantic validators for:
   - Ticket content: Max length, forbidden characters, HTML escaping
   - Reviewer names: Email format validation, length limits
   - Rejection reasons: Required length, profanity filter

3. Prevent SQL injection:
   - Verify all database queries use parameterized statements
   - Review raw SQL usage (should be none)
   - Add SQLAlchemy query logging in debug mode

4. Prevent XSS attacks:
   - HTML escape all user input before storage
   - Sanitize output before sending to clients
   - Add Content-Security-Policy headers

5. Add request size limits:
   - Max request body size: 1MB
   - Max ticket content: 5000 characters
   - Max header size limits

6. Validate data types strictly:
   - Use Pydantic discriminated unions where applicable
   - Reject requests with extra unexpected fields
   - Validate UUID formats for IDs

Create test cases for injection attempts.
```

**Security Tests**:
```python
# Test SQL injection attempts
content = "'; DROP TABLE tickets; --"
content = "1' OR '1'='1"

# Test XSS attempts
content = "<script>alert('XSS')</script>"
content = "<img src=x onerror=alert('XSS')>"

# Test oversized inputs
content = "A" * 10000  # Exceeds 5000 limit
```

**Validation**:
- [ ] All inputs validated with Pydantic
- [ ] No raw SQL queries in codebase
- [ ] HTML/script tags escaped or rejected
- [ ] Request size limits enforced
- [ ] Security tests pass

#### Task 5: Implement HTTPS and TLS Configuration

**Goal**: Secure API communications with TLS.

**Claude Code Prompt**:
```text
Configure HTTPS/TLS for production deployment:

1. Generate self-signed certificates for testing:
   - Create SSL certificate and private key
   - Store in secure location (not in git)

2. Update docker-compose.yml to support HTTPS:
   - Add nginx reverse proxy service
   - Configure TLS termination at nginx
   - Forward requests to uvicorn backend
   - Redirect HTTP to HTTPS

3. Create nginx.conf with security headers:
   - Strict-Transport-Security (HSTS)
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - X-XSS-Protection: 1; mode=block
   - Content-Security-Policy

4. Update uvicorn to run behind nginx:
   - Bind to 127.0.0.1 instead of 0.0.0.0
   - Trust X-Forwarded-For headers
   - Use ProxyHeaders middleware

5. Document HTTPS setup for production with Let's Encrypt

Test HTTPS access: https://localhost:443
```

**Nginx Configuration Example**:
```nginx
server {
    listen 443 ssl http2;
    server_name localhost;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://supportflow:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Validation**:
- [ ] HTTPS endpoint accessible
- [ ] HTTP redirects to HTTPS
- [ ] Security headers present
- [ ] TLS 1.2+ only
- [ ] Certificate validation works

#### Task 6: Secrets Management and Environment Configuration

**Goal**: Externalize all configuration and secrets.

**Claude Code Prompt**:
```text
Implement proper secrets management:

1. Audit code for all hardcoded secrets/config:
   - Database URLs
   - API keys
   - Encryption keys
   - Third-party API credentials

2. Create environment-based configuration:
   - config/development.env
   - config/staging.env
   - config/production.env (template only, actual file in secrets manager)

3. Use Pydantic Settings for config management:
   - Create settings.py with BaseSettings
   - Load from environment variables
   - Validate all config at startup
   - Fail fast if required config missing

4. Implement secrets rotation strategy:
   - Document how to rotate API keys
   - Document how to rotate database passwords
   - Create rotation scripts

5. Add .env.example with all required variables

6. For production, document integration with:
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault
   - Or Google Secret Manager

Never commit secrets to git. Use .gitignore properly.
```

**Settings.py Example**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_secret_key: str
    environment: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

**Validation**:
- [ ] No secrets in code
- [ ] All config from environment
- [ ] Startup fails if config missing
- [ ] .env.example documented
- [ ] Production secrets strategy documented

### Bonus Challenges

1. **Add OAuth2 Authentication**: Implement OAuth2/OpenID Connect for user login
2. **Implement API Key Scopes**: Fine-grained permissions (read:tickets, write:tickets)
3. **Add Audit Log Encryption**: Encrypt sensitive data in audit logs at rest
4. **Implement mTLS**: Mutual TLS for service-to-service authentication
5. **Add Security Scanning**: Integrate Bandit/Safety for automated security checks
6. **Create Security Tests**: Automated OWASP top 10 security test suite

### Expected Outcomes

After completing this lab, you should have:
- Production-grade security implemented
- No hardcoded secrets or keys
- Rate limiting preventing abuse
- HTTPS/TLS configured
- Role-based access control
- Thorough input validation
- Security documentation

---

## Shared Reference

Techniques, prompt patterns, and completion criteria common to all three challenges are in [`challenge-labs-reference.md`](challenge-labs-reference.md).
