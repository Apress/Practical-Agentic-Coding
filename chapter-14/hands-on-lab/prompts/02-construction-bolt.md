# Prompt: Construction Bolt, Test-First (Step 3)

After approving the Inception artifacts:

```text
Proceed to Construction. Work test-first: write pytest tests for the
three endpoints (GET, PUT, DELETE /users/{id}/notification-preferences)
against the approved requirements, show me the tests for review, and
only after I approve them, implement the FastAPI endpoints and the
schema migration to make them pass.
```

Review the tests before you approve them. They are your executable
requirements. If a test encodes a behavior you did not agree to in Inception,
fix it now. Do not wait until after implementation.
