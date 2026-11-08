# Cursor Agent Chat Prompt Examples

Prompts for Cursor's Agents Window (the agent chat, powered by the Composer model).

> Naming note: "Composer" names Cursor's in-house model. The multi-agent surface itself is the Agents Window.

## Scaffolding Prompts

### New Feature Scaffold
```text
Create a complete feature for [feature name]:
1. API endpoint in main.py
2. Service class with business logic
3. Database model and migration
4. Pydantic schemas for request/response
5. Unit tests with 80% coverage

Follow the existing patterns in this codebase.
```

### Microservice Bootstrap
```text
Create a FastAPI microservice structure for [service name]:
- main.py with health check and CORS
- models.py with SQLAlchemy async models
- schemas.py with Pydantic v2 validation
- database.py with connection pooling
- config.py with pydantic-settings
- Dockerfile with multi-stage build
- docker-compose.yml for local development
- requirements.txt with pinned versions
```

### React Component Structure
```text
Create a React component structure for [component name]:
- Component file with TypeScript
- Styles using Tailwind CSS
- Custom hooks for logic separation
- Unit tests with React Testing Library
- Storybook stories for documentation
```

## Refactoring Prompts

### Extract Service Pattern
```text
Refactor [file/function] to use the service pattern:
1. Extract business logic from route handler
2. Create a new service class
3. Implement dependency injection
4. Update the route to use the service
5. Keep all existing tests passing
```

### Add Caching Layer
```text
Add Redis caching to [function/service]:
1. Cache read operations with configurable TTL
2. Invalidate cache on write operations
3. Use cache-aside pattern
4. Handle cache failures gracefully (fallback to DB)
5. Add cache hit/miss metrics
```

### Implement Repository Pattern
```text
Refactor database access in [service] to use repository pattern:
1. Create a repository interface
2. Implement concrete repository class
3. Update service to use repository
4. Add transaction support
5. Update tests to mock repository
```

## Integration Prompts

### Add Authentication
```text
Add JWT authentication to this FastAPI application:
1. Create auth service with login/register
2. JWT token generation and validation
3. Protected route decorator
4. Password hashing with bcrypt
5. Refresh token mechanism
6. Integration with existing user model
```

### Add API Versioning
```text
Implement API versioning for this service:
1. Version prefix in URL (/api/v1/, /api/v2/)
2. Router organization by version
3. Deprecation headers for old versions
4. Version negotiation support
5. Documentation for each version
```

### Add WebSocket Support
```text
Add WebSocket support for real-time [feature]:
1. WebSocket endpoint with authentication
2. Connection manager for multiple clients
3. Message broadcasting
4. Heartbeat/ping-pong for connection health
5. Graceful disconnection handling
```

## Testing Prompts

### Generate Test Suite
```text
Generate thorough tests for [module]:
1. Unit tests for all public methods
2. Edge cases and error paths
3. Mock external dependencies
4. Parameterized tests for variations
5. Integration tests for API endpoints
6. Target 85% code coverage
```

### Add Load Testing
```text
Create load tests for this API:
1. Locust or k6 test scripts
2. Test scenarios for normal and peak load
3. Endpoint-specific test cases
4. Performance assertions
5. Report generation
```

## DevOps Prompts

### CI/CD Pipeline
```text
Create a GitHub Actions workflow:
1. Run tests on PR
2. Type checking and linting
3. Build Docker image
4. Push to container registry
5. Deploy to staging on merge to main
6. Deploy to production with approval
```

### Kubernetes Deployment
```text
Create Kubernetes manifests for this service:
1. Deployment with resource limits
2. Service and Ingress
3. ConfigMap and Secrets
4. HPA for auto-scaling
5. NetworkPolicy for security
6. PodDisruptionBudget
```

## Best Practices for Prompts

1. **Be Specific**: Include exact file names and patterns
2. **Reference Context**: Mention existing patterns to follow
3. **Define Acceptance Criteria**: List what "done" looks like
4. **Include Constraints**: Mention technologies and versions
5. **Iterate**: Use follow-up prompts to refine

## Prompt Template
```text
[Action] [Target] for [Purpose]:

Requirements:
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]

Constraints:
- Follow patterns in [existing file]
- Use [specific technology/version]
- Maintain [existing behavior]

Acceptance Criteria:
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] All tests passing
```
