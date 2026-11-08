# Artifact Examples

An artifact is a document in which the agent shows its reasoning and proof of work. You read it and comment on it. What artifacts are for: Chapter 6, Section 6.3.

These two files are real examples of the two most common artifact types. Both describe the same feature (a Spending Summary card). Read them back to back to see the plan and the result of one task.

## Files

| File | Artifact type | When the agent produces it |
|------|---------------|----------------------------|
| `implementation-plan-example.md` | Implementation Plan | Before writing any code, in Plan mode |
| `walkthrough-example.md` | Walkthrough | After finishing a multi-file change |

The lab also shows artifact types that are not markdown files:

- Screenshots and browser recordings from the browser subagent
- Test reports

Exercise 3 in `../../hands-on-lab/exercises/` shows how to request each of them.

## How to Use These

1. Read the implementation plan first. Review it as you would a colleague's design doc.
2. Read the walkthrough next. It records what happened, including the file-by-file change list at the end.

## Review Checklist

When an agent hands you an Implementation Plan:

- [ ] Does the approach fit the architecture you already have?
- [ ] Are the files it plans to touch the files you would have touched?
- [ ] Does it respect the rules in `.agents/rules/`?
- [ ] Are new dependencies justified, or could existing code do the job?
- [ ] Is the scope what you asked for, without extra features?
- [ ] Are the risks and open questions named?

Comment directly on the artifact. The agent adds your feedback to the revised plan.
