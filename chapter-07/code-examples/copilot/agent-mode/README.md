# GitHub Copilot Agent Mode Examples

Prompts for Copilot Agent Mode, with what the agent does for each. Agent Mode can use tools, correct itself, and work with your environment.

## When to Use Agent Mode

- Complex, multi-step tasks
- Tasks requiring terminal commands
- Bug fixes needing test verification
- Features spanning multiple files
- Tasks where the solution path isn't clear

## Agent Mode Prompts

### Bug Fixing with Self-Healing

```text
The tests are failing. Run the test suite, identify the failures,
fix them, and verify the fixes by re-running the tests.
```

**What Agent Does:**
1. Runs `npm test` or `pytest`
2. Reads error output
3. Identifies failing tests
4. Locates source of bug
5. Applies fix
6. Re-runs tests to verify
7. Iterates until passing

### Feature Discovery and Implementation

```text
Add a search feature for the user list. Figure out where the
user list is implemented and add search functionality with:
- Backend: Full-text search endpoint
- Frontend: Search input with debounce
- Tests: Unit and integration tests
```

**What Agent Does:**
1. Explores file system to find user list
2. Identifies backend API structure
3. Creates search endpoint
4. Finds frontend component
5. Adds search UI
6. Writes tests
7. Verifies everything works

### Dependency Updates

```text
Update all npm dependencies to their latest compatible versions.
Run tests after each major update to catch breaking changes.
Fix any issues that arise.
```

**What Agent Does:**
1. Runs `npm outdated`
2. Updates packages one by one
3. Runs tests after each update
4. Identifies breaking changes
5. Applies fixes
6. Commits working state

### Database Migration

```text
Add a "tags" feature to blog posts:
- Create migration to add tags table
- Add many-to-many relationship
- Update API endpoints
- Add tests
- Run migration in dev environment
```

**What Agent Does:**
1. Creates migration file
2. Updates models
3. Modifies API endpoints
4. Generates tests
5. Runs migration command
6. Verifies with database query

### Code Quality Improvement

```text
Run the linter, fix all fixable errors automatically, and for
issues that can't be auto-fixed, make the necessary code changes.
Then run tests to ensure nothing broke.
```

**What Agent Does:**
1. Runs `eslint --fix`
2. Reviews remaining errors
3. Manually fixes complex issues
4. Runs test suite
5. Iterates until clean

## Agent Mode Capabilities

### Tool Use
- **Terminal**: Run commands, view output
- **File System**: Read, write, create files
- **Browser**: Navigate, fill forms (in supported environments)
- **Git**: Commit, push, create branches

### Self-Correction Loop
```text
Generate Code → Run Tests → Analyze Errors → Fix → Repeat
```

### Discovery Mode
- Crawls file system for relevant files
- Reads existing patterns
- Identifies integration points
- Maps dependencies

## Agent Mode vs Edit Mode

> **Tool note (as of November 7, 2026).** VS Code deprecated Edit mode in version 1.110. VS Code 1.126 and later offer it only when Agent mode is disabled by policy. To get Edit mode's precision in Agent mode, attach only the files to change. Review each edit before you keep it.

Section 7.3 compares the two modes. The table is kept to match that comparison.

| Aspect | Edit Mode (retired) | Agent Mode |
|--------|-----------|------------|
| File Selection | Manual (pin files) | Automatic discovery |
| Terminal Access | No | Yes |
| Self-Correction | Limited | Full loop |
| Autonomy | Human reviews each change | Autonomous with verification |
| Best For | Precision edits | Complex tasks |

## Best Practices

### 1. Clear Objectives
```text
Good: "Add pagination to the users endpoint with limit/offset parameters"
Bad: "Make the API better"
```

### 2. Include Constraints
```text
Good: "Add search using PostgreSQL full-text search, not a separate service"
Bad: "Add search"
```

### 3. Verification Steps
```text
Good: "Add the feature and verify by running the test suite"
Bad: "Add the feature"
```

### 4. Error Boundaries
```text
Good: "If you encounter authentication issues, skip that and move on"
Bad: "Fix everything"
```

## Example Session

### User Prompt:
```text
The /api/orders endpoint is slow. Profile it, identify the bottleneck,
and optimize it. Target: response time under 100ms.
```

### Agent Actions:
1. **Profile**: Runs endpoint with timing
2. **Analyze**: Identifies N+1 query issue
3. **Research**: Checks existing query patterns
4. **Fix**: Adds eager loading
5. **Verify**: Re-runs with timing
6. **Iterate**: If still slow, adds caching
7. **Document**: Adds comment explaining optimization

### Agent Output (illustrative; your numbers will differ):
```text
I identified the bottleneck:
- The /api/orders endpoint was making N+1 queries for order items
- Each order triggered a separate query for its items

Fix applied:
- Added eager loading with `include: { orderItems: true }`
- Added index on order_items.order_id

Before: 450ms
After: 45ms

Test results: All passing
```

## Safety Considerations

1. **Review Changes**: Always review Agent's changes before merging
2. **Test Environment**: Run Agent tasks in dev/staging first
3. **Rollback Plan**: Ensure you can revert if needed
4. **Sensitive Data**: Don't expose production credentials
5. **Rate Limits**: Be aware of API limits for external services
