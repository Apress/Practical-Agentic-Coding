# Challenge Lab 1: Debug and Fix Application Issues

**Reference**: Chapter 8, Section 8.7 (first challenge)

The reference SupportFlow implementation in [`../supportflow/`](../supportflow/) runs, but it has defects. The defects are **deliberate**. The verification run in Section 8.6, Phase 5 finds them. This challenge is to fix them. The build works. The system returns 200s but does the wrong thing in places.

**The tests show where the defects are.** On a fresh clone, run:

```bash
cd ../supportflow
pip install -r requirements.txt
pytest tests/ -q
```

You should see roughly **20 failures out of 105 tests**. Each one traces to a defect on the list below. The test suite is the specification, and the implementation does not meet it yet. When all 105 pass, you are done.

**The defects** (each row is a task below):

| Task | Symptom | Where to look |
|------|---------|---------------|
| 2 | The approve and reject endpoints refuse to complete a valid review. `requires_human_review` stays `true` after approval | `services/response_generator.py`, plus the approval path in `api/main.py` |
| 3 | `GET /responses/pending` misses drafts that exist in the database (status case mismatch) | the pending-responses query in `database/repositories.py` |
| 4 | An obviously angry ticket is classified `neutral` sentiment and `medium` urgency | keyword sets in `services/ticket_analyzer.py` |
| 5 | `/health` reports `database: disconnected` while tickets are being created successfully | the health handler in `api/main.py` |
| 6 | Response generation raises `ValueError: Missing required placeholders` for several categories | template definitions in `services/response_generator.py` |

Two smaller defects remain:

- The entity extractor's patterns in `services/ticket_analyzer.py` stop short. `ORD-2024-5678` comes back as `ORD-2024`. A three-digit account ID such as `ACC-789` is not extracted at all.
- In the `POST /tickets` response, `escalation.priority` comes back lowercase (`critical`). [`API_GUIDE.md`](../supportflow/API_GUIDE.md) and the tests expect `CRITICAL`. This is the same enum-versus-string case mismatch as Task 3, this time in `api/main.py`. It shows up only after your Task 4 fix lets the angry-customer workflow test get past its sentiment check.

Task 1 asks you to find all of these yourself, before you read the table above.

**Before you start**: Reproduce at least one defect by hand. You need to see a bug fail before you can confirm the fix.

```bash
docker-compose up -d
curl http://localhost:8000/health
curl -X POST http://localhost:8000/tickets -H "X-API-Key: demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"content": "This is OUTRAGEOUS! I am extremely angry and I want a refund NOW or I will call my lawyer!"}'
```

Use `/rewind` when you need it. If a fix makes things worse, roll back to a checkpoint (Section 8.3). Do not stack fixes on fixes.

---

**Duration**: 2-3 hours
**Difficulty**: Intermediate
**Focus**: Debugging, Issue Investigation, Code Quality

### Learning Objectives

By completing this lab, you will:
- Find bugs through testing and log analysis
- Use Claude Code to investigate and fix runtime errors
- Improve application reliability and correctness
- Practice systematic debugging methodology

### Prerequisites

- Python 3.11+, with `pip install -r requirements.txt` run in `../supportflow/`
- Docker and Docker Compose, for deploying the app and reading its logs
- `jq` installed. The project's safety hook parses its input with it, and blocks if it is missing
- Basic understanding of FastAPI and SQLAlchemy

### Implementation Hints: Use Claude Code's Features

**Use these Claude Code features:**

- **Create debugging rules** in `.claude/rules/debugging.md`:
  - "Always read relevant code before suggesting fixes"
  - "Check database state before and after operations"
  - "Verify fixes with integration tests"
  - "Document root cause in commit messages"

- **Build sub-agents** for debugging. Define each as a markdown file in `.claude/agents/`. The frontmatter format is in [`../../code-examples/subagents/`](../../code-examples/subagents/). Invoke each by name, or let Claude match on the description:
  - `debugger`: systematic issue investigation, read-only tools plus Bash for reproducing
  - `error-detective`: error pattern analysis across logs
  - `code-reviewer`: review fixes before committing

- **Add validation hooks** in `.claude/hooks/` to prevent regressions:
  - Create `pre-commit-tests.sh` that runs affected tests before commits
  - Add `validate-api-response.sh` to verify response schemas match OpenAPI spec
  - Use hooks to enforce test coverage requirements (80%+ for bug fixes)

- **Use MCP for debugging context**:
  - Connect to GitHub Issues to track known bugs and link fixes to issues
  - Integrate with log aggregation tools (e.g., Datadog MCP) to query production logs
  - Use database MCP to inspect data without manual queries

**Example Claude Code workflow:**
```text
1. Ask Claude to investigate: "Debug why approval endpoint fails. Read code, check logs, identify root cause."
2. Claude uses debugger agent to analyze systematically
3. Claude suggests fix and generates tests
4. Pre-commit hook validates tests pass before commit
5. Claude creates descriptive commit message linking to issue
```

### Challenge Tasks

#### Task 1: Identify All Application Issues

**Goal**: Create a complete list of bugs by testing all endpoints.

**Claude Code Prompt**:
```text
Systematically test all SupportFlow API endpoints and identify any errors or unexpected behavior:

1. Test each endpoint documented in ../supportflow/API_GUIDE.md
2. Try edge cases: empty inputs, very long content, special characters
3. Test complete workflows: ticket submission -> response approval
4. Check logs for any errors or warnings
5. Verify database entries are created correctly

For each issue found:
- Document the error message
- Identify the endpoint and request that caused it
- Note the expected vs actual behavior
- Check application logs for stack traces

Create a file called BUGS_FOUND.md with a prioritized list of issues.
```

**Validation**:
- [ ] Documented at least 3 distinct bugs
- [ ] Each bug has reproduction steps
- [ ] Bugs are prioritized by severity

#### Task 2: Fix the Response Approval Logic

**Issue**: Approval endpoint rejects valid draft responses.

**Claude Code Prompt**:
```text
Investigate and fix the response approval issue:

1. Read the approval endpoint code in api/main.py
2. Read the ResponseRepository.approve() method
3. Identify why "draft" status is being rejected
4. Check the database schema for Response status field
5. Fix the logic to allow approving DRAFT responses
6. Add validation to prevent approving already-approved responses
7. Write an integration test to verify the fix

Test the fix by:
- Submitting a ticket
- Extracting the response_id
- Approving the response
- Verifying status changes to APPROVED
```

**Hints**:
- Check the conditional logic in the approve endpoint
- Look at what status values are being compared
- Verify database column naming (status vs status field)

**Validation**:
- [ ] Draft responses can be approved successfully
- [ ] Already approved responses return proper error
- [ ] Integration test passes
- [ ] Audit log records approval action

#### Task 3: Fix Pending Responses Query

**Issue**: `/responses/pending` returns empty list despite draft responses existing.

**Claude Code Prompt**:
```text
Debug why the pending responses endpoint returns an empty list:

1. Check the ResponseRepository.list_pending() implementation
2. Examine the database Response table structure
3. Verify the status field values in the database
4. Check if there's a mismatch between Python enums and database strings
5. Test the query directly to see what's returned
6. Fix the query to correctly filter draft responses
7. Add logging to show how many draft responses were found

Use docker exec to query the database directly:
docker exec supportflow python3 -c "from database.connection import get_db_session; from database.models import Response; db = get_db_session(); print('Draft responses:', db.query(Response).filter(Response.status == 'DRAFT').count())"
```

**Possible Issues to Check**:
- Case sensitivity in status comparison
- Enum vs string mismatch
- Database session issues
- Ticket relationship loading

**Validation**:
- [ ] `/responses/pending` returns draft responses
- [ ] Response count is accurate
- [ ] Ticket IDs are included in results
- [ ] Response is sorted by creation time

#### Task 4: Improve Sentiment Detection Accuracy

**Issue**: Angry customer messages are classified as "neutral".

**Claude Code Prompt**:
```text
Enhance the sentiment detection to better identify angry customers:

1. Review the current keyword lists in services/ticket_analyzer.py
2. Analyze why "OUTRAGEOUS" and "angry" aren't detected
3. Add more angry keywords (frustrated, furious, unacceptable, etc.)
4. Consider keyword weighting for stronger indicators
5. Adjust confidence scoring thresholds
6. Test with various angry messages
7. Update unit tests to cover new angry keywords

Create test cases for:
- Explicit anger words (angry, furious, outraged)
- Implicit anger (unacceptable, ridiculous, disgraceful)
- Multiple caps words
- Exclamation marks and intensity indicators

Ensure sentiment detection affects requires_priority_review flag correctly.
```

**Validation**:
- [ ] "OUTRAGEOUS" messages detected as angry
- [ ] Priority review flag set for angry sentiment
- [ ] At least 15 new angry keywords added
- [ ] Sentiment confidence > 0.80 for clear anger
- [ ] Unit tests updated and passing

#### Task 5: Fix Health Check Database Status

**Issue**: Health check reports "database: disconnected" incorrectly.

**Claude Code Prompt**:
```text
Fix the health check to accurately report database connectivity:

1. Examine the current health check implementation in api/main.py
2. Identify what query is being run to test the database
3. Check if the query is actually executing against the database
4. Test database connectivity properly (e.g., query an actual table)
5. Add error handling for database connection issues
6. Test both healthy and unhealthy database states

Improve the health check to include:
- Database connection status
- Table existence verification
- Recent activity check (last ticket created timestamp)
- Overall application health status
```

**Validation**:
- [ ] Health check shows "connected" when database is working
- [ ] Health check shows "disconnected" if database is down
- [ ] Health response includes meaningful database info
- [ ] Overall status is "healthy" when all systems operational

#### Task 6: Add Template Placeholders for All Categories

**Issue**: Account-related tickets fail with "Missing required placeholders".

**Claude Code Prompt**:
```text
Fix template placeholder issues across all ticket categories:

1. Review all templates in services/response_generator.py
2. Identify which placeholders are required by each template
3. Update api/main.py to provide appropriate defaults for all placeholders
4. Make placeholders optional where reasonable
5. Add category-specific placeholder defaults
6. Test ticket submission for each category (billing, technical, account, general)

For each category, provide sensible defaults:
- billing: refund_amount, charge_date, account_balance
- technical: error_description, steps_taken, resolution_eta
- account: account_info, update_type, confirmation_details
- general: inquiry_topic, information_provided

Alternatively, refactor templates to use fewer required placeholders.
```

**Validation**:
- [ ] Tickets can be created for all 4 categories
- [ ] Each category generates appropriate responses
- [ ] No "Missing required placeholders" errors
- [ ] Response quality is maintained

### Bonus Challenges

1. **Add Response Regeneration**: Allow rejected responses to be regenerated with improvements
2. **Implement Response History**: Track all versions of responses for a ticket
3. **Add Bulk Testing Script**: Create a script that submits 50 test tickets with various scenarios
4. **Add Error Recovery**: Implement retry logic for database operations
5. **Create Debugging Dashboard**: Build a simple HTML page showing recent errors and system stats

### Expected Outcomes

After completing this lab, you should have:
- All major bugs identified and fixed
- Approval workflow functioning correctly
- Accurate sentiment detection
- Reliable health checks
- Thorough test coverage
- Documented debugging process

---

## Shared Reference

Techniques, prompt patterns, and completion criteria common to all three challenges are in [`challenge-labs-reference.md`](challenge-labs-reference.md).
