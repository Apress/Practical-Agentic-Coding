---
name: add-endpoint
description: Add a new API endpoint to a FastAPI service following the project's layering, naming, and testing standards. Use when asked to add a route, endpoint, or resource to the API.
---

# Add an API Endpoint

Follow this procedure whenever you add an endpoint. The project rules define the standards. This skill gives the order of operations.

## Steps

1. **Schema first.** Add the request and response models to `schemas.py` (Pydantic v2). Name them `{Resource}Create` and `{Resource}Response`.
2. **Service layer.** Put the business logic in a `*Service` class, not in the route function. Inject dependencies through the constructor.
3. **Route last.** Add the route under `/api/v1/{resource}`. The function body should only validate input, call the service, and shape the response. Raise `HTTPException` for error cases.
4. **Tests.** Add tests for the happy path and each error status code. Mock external dependencies (database, Redis). Use no live connections in tests.
5. **Verify.** Run `pytest --cov=src` and confirm coverage has not dropped below 80%.

## Do not

- Put queries or business logic in the route function.
- Return ORM models directly; always return the Pydantic response schema.
- Skip the failure-path tests.
