# SupportFlow Phase 4 Build Prompt

**Reference**: Chapter 8, Section 8.6, Phase 4 (Unit Testing the Complete System)

This is the complete build prompt the chapter points to. The condensed version printed in the book is enough for Claude to build a working system. This expanded version adds request/response examples and endpoint documentation requirements. The reference solution in this directory was built against it. Use it when you want your build to track the reference implementation closely.

Before you paste it:

- **Run it from Phase 3's end state.** The prompt assumes these already exist in your project:
  - `CLAUDE.md`
  - The three services (`TicketAnalyzer`, `ResponseGenerator`, `EscalationEngine`)
  - The PreToolUse safety hook
  - The `review-drafts` skill
- **Expect your build to differ.** File names and internals vary from session to session. Match the behavior, which is the endpoint contract below and in [`API_GUIDE.md`](API_GUIDE.md). Do not try to match lines of code.

## The prompt

```text
Create a deployable FastAPI application for SupportFlow with Swagger UI.

1. REST API (api/main.py) using the existing TicketAnalyzer,
   ResponseGenerator, and EscalationEngine services:

   - POST /tickets: submit a support ticket.
     Request: {"content": "I'm very frustrated! I was charged twice
     for order #12345."} (content required, 10-5000 characters).
     Response 201: the stored ticket with its analysis (category,
     urgency, sentiment, confidence scores, extracted entities,
     requires_priority_review), the escalation evaluation
     (should_escalate, priority, reasons), and the auto-generated
     draft response with status "DRAFT" and
     requires_human_review=true.

   - GET /tickets/{ticket_id}: complete ticket details including the
     analysis, escalation result, and every response. 404 if the
     ticket does not exist.

   - GET /responses/pending: all responses with status DRAFT awaiting
     human review, plus a total count.

   - POST /responses/{response_id}/approve:
     Request: {"reviewed_by": "reviewer@example.com"}.
     Only DRAFT responses may be approved; return 400 if the response
     was already reviewed. Record the reviewer and an ISO 8601
     reviewed_at timestamp.

   - POST /responses/{response_id}/reject:
     Request: {"reviewed_by": "reviewer@example.com",
               "reason": "Tone does not match the customer's
                sentiment"} (reason required, 10-1000 characters).
     Same DRAFT-only rule; store the rejection reason.

   - GET /health: no authentication. Report overall status, a
     timestamp, and real database connectivity (run an actual query;
     do not assume the database is up).

2. SQLite database with SQLAlchemy models (Ticket, TicketAnalysis,
   Response, AuditLog) behind a repository pattern. Read DATABASE_URL
   from the environment, defaulting to sqlite:///./supportflow.db.

3. API key authentication via the X-API-Key header on every endpoint
   except /health. Read the key from the API_KEY environment variable,
   default demo-key-12345. Return 401 for a missing or wrong key.

4. Audit logging of every operation (ticket.created, ticket.analyzed,
   response.generated, response.approved, response.rejected) to the
   audit_logs table with ISO 8601 timestamps and the acting user.

5. Docker deployment: a multi-stage Dockerfile plus docker-compose.yml
   publishing port 8000, persisting the SQLite file in a ./data bind
   mount, with a container healthcheck against /health.

6. Integration tests covering the full workflow: submit an angry
   billing ticket -> analysis flags it for priority review ->
   escalation fires -> a draft response is generated -> approve it.
   Also cover authentication rejections (missing and wrong key) and
   assert that audit log entries are written for each operation.

7. Documentation: update README.md with deployment and testing
   instructions, and write an API_GUIDE.md documenting every endpoint
   with an example request, an example response, validation rules, and
   error codes (400, 401, 404, 422). Swagger UI at /docs and
   ReDoc at /redoc must work out of the box.

Constitutional requirements (from CLAUDE.md, non-negotiable): every
generated response is created as DRAFT and requires human approval
before it can be sent; every operation is audit-logged; no internal
system details (stack traces, internal IDs, database or service names)
may appear in customer-facing response text.
```

## Checking the result

The endpoint contract, with example payloads for every endpoint, is in [`API_GUIDE.md`](API_GUIDE.md). Spot-check your build against it:

1. Submit the angry billing ticket from the prompt.
2. Check that the analysis flags it.
3. Check that the draft appears in `GET /responses/pending`.
4. Approve it.
5. Check that the audit trail recorded each step.

Then move on to Phase 5 (Section 8.6). There, Claude verifies the deployed container end to end.
