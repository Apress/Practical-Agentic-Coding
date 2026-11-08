---
name: review-drafts
description: Review SupportFlow's pending draft responses against the customer-response rules in CLAUDE.md, then summarize which to approve, which to reject, and why. Use when asked to review drafts, clear the review queue, or check pending responses.
---

# Review Pending Draft Responses

SupportFlow's constitution requires that a human approve every customer-facing response before it is sent. That rule creates a recurring procedure: pull the queue, check each draft against the standards, and recommend a decision. This skill runs that procedure the same way every time.

You do not approve or reject on your own. You produce a recommendation the human reviewer acts on.

## Step 1: Pull the queue

Fetch every draft awaiting review:

```bash
curl -s -X GET http://localhost:8000/responses/pending \
  -H "X-API-Key: ${API_KEY:-demo-key-12345}"
```

If the API is not running, start it (`docker-compose up -d`) and retry. If the queue is empty, say so and stop; do not invent drafts to review.

## Step 2: Check each draft

For each response in the queue, check all six rules. Cite the specific text that triggers any failure.

| # | Rule | What a failure looks like |
|---|------|---------------------------|
| 1 | **No internal details.** No stack traces, exception names, error codes, database or SQL references, internal IDs, or service names. | "Our database returned error code 500" |
| 2 | **Status is DRAFT.** `status` must be `DRAFT` and `requires_human_review` must be `true`. Anything else is a constitutional breach, not a style problem. (Until Challenge Lab 1 fixes the case mismatch, the reference build stores `draft` in lowercase; treat the two as the same.) | `status: "APPROVED"` on an unreviewed response |
| 3 | **Placeholders are resolved.** No unsubstituted `{placeholder}` text left in the subject or body. | "Hello {customer_name}," |
| 4 | **Tone matches sentiment.** A ticket analyzed as `angry` or `negative` needs acknowledgment of the frustration before the resolution, not a cheerful template opener. | Angry refund complaint answered with "Thanks for reaching out!" and nothing else |
| 5 | **Commitments are real.** No promised timeline, refund amount, or policy exception the ticket data does not support. | "Your refund will arrive within 2 hours" when no refund was authorized |
| 6 | **Escalated tickets are not closed out.** If the ticket's escalation result requires human handling, the draft must hand off rather than resolve. | A draft that answers a legal-threat ticket as routine |

Rules 1 and 2 are enforced in code as well (validators in `models/response.py` and `GeneratedResponse.model_post_init`). If you find a draft that violates either one, that is a bug in the enforcement path, not just a bad draft. Say so explicitly.

## Step 3: Summarize

Report in this shape, nothing more:

```text
Reviewed N pending drafts.

APPROVE (n)
  RESP-...  ticket TKT-...  billing  all six checks pass

REJECT (n)
  RESP-...  ticket TKT-...  technical
      Rule 1 (internal details): body contains "SQL timeout on the tickets table"
      Rule 3 (placeholders): subject still reads "Re: {issue_summary}"

NEEDS HUMAN JUDGMENT (n)
  RESP-...  ticket TKT-...  escalated CRITICAL (legal threat)
      Tone is fine, but this ticket should not be answered from a template.
```

Put anything you are unsure about in the third bucket. A draft parked for a human is cheap; a wrong customer email is not.

## Step 4: Act only when told

Wait for the reviewer to name the decisions. Then apply them:

```bash
# Approve
curl -s -X POST http://localhost:8000/responses/RESP-XXXX/approve \
  -H "X-API-Key: ${API_KEY:-demo-key-12345}" \
  -H "Content-Type: application/json" \
  -d '{"reviewed_by": "reviewer@example.com"}'

# Reject, with the reason from your findings
curl -s -X POST http://localhost:8000/responses/RESP-XXXX/reject \
  -H "X-API-Key: ${API_KEY:-demo-key-12345}" \
  -H "Content-Type: application/json" \
  -d '{"reviewed_by": "reviewer@example.com", "reason": "Rule 1: internal details in body"}'
```

Confirm each call returned the expected status change, and note that both actions write an audit log entry, which is the other half of the constitutional requirement.
