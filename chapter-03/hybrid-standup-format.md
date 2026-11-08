# Hybrid Standup Format

A short standup template for teams running AI agents alongside human developers.

1. Copy the agenda into your team's meeting notes template.
2. Copy the status-report format into the automation that produces your agents' progress summaries.

Why this format: Chapter 3, Section 3.3 (Daily Standups for Coordination).

## Agenda (13 minutes plus 2 per human, so under 20 minutes for a Foundation Team)

| Segment | Time | Content |
|---------|------|---------|
| Human updates | 2 minutes each | Yesterday, today, blockers, same as any standup |
| AI agent summary | 3 minutes total | Read the generated per-agent reports; pull out anything marked needs-review or blocked |
| Coordination planning | 5 minutes | Pair the day's human work with agent tasks; surface resource conflicts |
| Obstacle resolution | 5 minutes | Assign an owner to each blocker that needs human judgment or another team |

## AI agent status report template

Write one short block per agent. Generate it from the agent's task log. Do not write it by hand. The book's example uses these markers:

- completed
- in progress
- next
- needs review
- blocked
- human input needed

```text
Code generation agent status:
  Completed:    User profile API integration (3 endpoints)
  In progress:  Shopping cart state management (75% complete)
  Needs review: Payment processing security implementation
  Blocked:      Waiting for third-party API documentation for shipping calculator

Quality assurance agent status:
  Completed:    Generated 47 unit tests (94% coverage achieved)
  In progress:  Performance testing for checkout flow
  Next:         Integration testing for user management system
  Human input:  User acceptance criteria for payment error handling
```

## Notes

- Agents do not attend the meeting. Read their reports instead.
- Keep the total agent segment to 3 minutes, however many agents you run. Move anything that needs discussion to coordination planning or obstacle resolution.
- Assign an owner to each "needs review" and "human input needed" item before the standup ends.
