# GitHub Copilot Cloud Agent: Issue Templates

Copy-ready issue templates for the Copilot cloud agent. To dispatch the agent, add Copilot as the assignee on a GitHub Issue. It picks up the work in the background.

When to hand work to the cloud agent and why: Chapter 7, Section 7.5. The Section 7.6 lab (Phase 4) runs it on LinkForge.

> **Name change.** GitHub calls the book's "Copilot Async Agent" the **Copilot cloud agent**. The book's mission control is the agents page at github.com/copilot/agents.

## Issue-Driven Development

### Feature Implementation Issue
```markdown
Title: Add user profile picture upload

Description:
Add the ability for users to upload profile pictures.

Requirements:
- [ ] POST /api/users/:id/avatar endpoint
- [ ] Accept JPEG, PNG, WebP (max 5MB)
- [ ] Resize images to 200x200 and 50x50
- [ ] Store in S3 with CloudFront CDN
- [ ] Update user model with avatar_url
- [ ] Add unit and integration tests

Technical Constraints:
- Use Sharp for image processing
- Use multer for file uploads
- Follow existing error handling patterns

Acceptance Criteria:
- [ ] All tests passing
- [ ] Documentation updated
- [ ] No breaking changes to existing API

Assignee: Copilot (select from the assignees list)
```

### Bug Fix Issue
```markdown
Title: Fix race condition in order processing

Description:
Users report occasional duplicate orders when clicking submit rapidly.

Reproduction:
1. Add items to cart
2. Click "Place Order" rapidly 3-4 times
3. Multiple orders are sometimes created

Root Cause Analysis Needed:
- Check for missing transaction boundaries
- Verify idempotency key implementation
- Review optimistic locking setup

Expected Fix:
- Implement proper idempotency
- Add request deduplication
- Add integration test for race condition

Logs:
[Attach relevant logs or error messages]

Assignee: Copilot (select from the assignees list)
```

### Refactoring Issue
```markdown
Title: Refactor authentication to use refresh tokens

Description:
Current JWT implementation has no refresh mechanism, forcing users to re-login frequently.

Current State:
- Access tokens expire in 1 hour
- No refresh token mechanism
- Users must re-authenticate after expiry

Desired State:
- Access tokens: 15 minute expiry
- Refresh tokens: 7 day expiry (stored in HTTP-only cookie)
- Automatic token refresh on 401
- Token revocation on logout

Files to Modify:
- src/middleware/auth.ts
- src/services/authService.ts
- src/routes/auth.ts
- frontend/src/services/api.ts

Testing Requirements:
- Unit tests for token refresh logic
- Integration tests for full auth flow
- E2E test for automatic refresh

Assignee: Copilot (select from the assignees list)
```

## CI/CD Automation Issues

### Pipeline Setup Issue
```markdown
Title: Set up GitHub Actions CI/CD pipeline

Description:
Create a complete CI/CD pipeline for this project.

Pipeline Stages:

1. **On Pull Request:**
   - Run linting (ESLint/Prettier)
   - Run type checking (TypeScript)
   - Run unit tests
   - Run integration tests
   - Generate coverage report
   - Security scan with Snyk

2. **On Merge to Main:**
   - All PR checks
   - Build Docker image
   - Push to container registry
   - Deploy to staging
   - Run smoke tests
   - Notify Slack

3. **On Release Tag:**
   - Deploy to production
   - Create GitHub release
   - Update changelog

Requirements:
- Use GitHub Secrets for credentials
- Cache dependencies between runs
- Parallel test execution
- Fail fast on first error
- Artifacts for test reports

Assignee: Copilot (select from the assignees list)
```

### Infrastructure Issue
```markdown
Title: Create Kubernetes deployment manifests

Description:
Generate Kubernetes manifests for deploying this service.

Components Needed:
1. Deployment with:
   - 3 replicas
   - Resource limits (CPU: 500m, Memory: 512Mi)
   - Liveness and readiness probes
   - Rolling update strategy

2. Service:
   - ClusterIP type
   - Port 80 -> 8080

3. Ingress:
   - TLS termination
   - Path-based routing

4. ConfigMap:
   - Non-sensitive configuration

5. Secret:
   - Database credentials
   - API keys

6. HPA:
   - Scale 3-10 replicas
   - Target 70% CPU

7. NetworkPolicy:
   - Only allow traffic from ingress

Namespace: production

Assignee: Copilot (select from the assignees list)
```

## Documentation Issues

### API Documentation Issue
```markdown
Title: Generate OpenAPI specification

Description:
Create complete API documentation.

Requirements:
- OpenAPI 3.0 specification
- All endpoints documented
- Request/response schemas
- Authentication requirements
- Example requests and responses
- Error responses documented

Output:
- openapi.yaml in docs/
- Generate HTML docs with Redoc
- Add to GitHub Pages

Endpoints to Document:
- All routes in src/routes/

Style Guide:
- Use snake_case for field names
- Include deprecation notices
- Version information in title

Assignee: Copilot (select from the assignees list)
```

## Monitoring Agent Progress

1. **Agents page**: follow every session from github.com/copilot/agents, or from the repository's Agents tab.
2. **Review the pull request**: assigning an issue always creates one. Give feedback in pull request comments. Merge when you are satisfied.
3. **GitHub Actions**: workflows do not run automatically on the agent's pushes. Approve them with **Approve and run workflows**, then watch the runs.
4. **Plan check**: the cloud agent is not part of Copilot Free. On Business and Enterprise it follows the organization's Copilot in the cloud policy. As of November 7, 2026, that policy is on by default.
