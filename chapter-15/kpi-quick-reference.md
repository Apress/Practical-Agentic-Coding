# KPI Quick Reference: Part III System KPIs

Use this sheet to record your own numbers. Definitions and reasoning: Chapter 15, Sections 15.5 to 15.8.

The sheet covers:

- the agentic-system KPIs
- the leading/lagging split
- the do-not-measure list
- the minimum viable set

In the four KPI tables, every data source names a system you built in Part III. That system already emits the data.

1. For each KPI, record where you stand today.
2. Set a target for the next quarter.

## Memory system KPIs (Chapter 9 systems)

Book reference: Table 15.5.

| KPI | Data source | Hint | Your baseline | Your target |
|-----|-------------|------|---------------|-------------|
| Retrieval hit rate | Memory search logs | Should trend upward | | |
| Confidence decay curve | Trust scoring system | Reinforce winners, decay noise | | |
| Knowledge capture rate | Memory store growth | Steady weekly capture | | |
| Consolidation frequency | Pattern mining logs | Episodic converts to semantic | | |

## Multi-agent coordination KPIs (Chapter 10 systems)

Book reference: Table 15.6. The last row pairs speed with spend. Why: Section 15.5.

| KPI | Data source | Hint | Your baseline | Your target |
|-----|-------------|------|---------------|-------------|
| Task decomposition accuracy | Manager agent logs | Subtasks rebuild the task | | |
| Handoff quality | Agent communication logs | Few human corrections | | |
| Feedback loop convergence | Agent interaction logs | Finding-to-fix in few cycles | | |
| Parallel efficiency | Execution time comparison | Faster than one agent | | |
| Cost-adjusted parallelism | Execution time + token billing | Speedup worth its cost | | |

## DevOps pipeline KPIs (Chapter 11 systems)

Book reference: Table 15.7.

| KPI | Data source | Hint | Your baseline | Your target |
|-----|-------------|------|---------------|-------------|
| MTTR improvement | Incident logs | Should trend downward | | |
| Security gate false positive rate | Gate decision logs | Low noise, real blocks | | |
| Cost gate savings | Cost estimation logs | Overruns caught before deploy | | |
| Self-healing resolution rate | Pipeline logs | Fixed without human help | | |

## Governance KPIs (Chapter 12 systems)

Book reference: Table 15.8.

| KPI | Data source | Hint | Your baseline | Your target |
|-----|-------------|------|---------------|-------------|
| AGILITY test suite coverage | CI/CD test results | No pillar left untested | | |
| Incident response time | Incident logs | Detection to containment, fast | | |
| Audit trail completeness | Audit log verification | Every action logged | | |
| Emergency stop activations | Emergency stop logs | Should approach zero | | |

## Leading vs lagging indicators (Section 15.6)

1. Check the leading rows weekly and act on them.
2. Report the lagging rows quarterly.

Warning signs and timing for each row: Table 15.9 in the book.

| Type | Metric | Current reading | Action needed? |
|------|--------|-----------------|----------------|
| Leading | Memory hit rate trend | | |
| Leading | Agent acceptance rate stability | | |
| Leading | Governance test count | | |
| Leading | Review queue depth | | |
| Lagging | Quarterly defect rate | | |
| Lagging | MTTR trend | | |
| Lagging | Deployment frequency | | |
| Lagging | Developer satisfaction | | |

## What NOT to measure (Section 15.7)

Keep these off your dashboard:

- lines of code
- individual contribution scores
- acceptance rate as a performance measure
- self-reported time saved
- commit count
- story points
- vendor benchmark scores in procurement decisions

The reason for each and its replacement metric: Table 15.15 in the book.

## Minimum viable measurement (Section 15.8)

Get these six running before you wire any of the KPIs above. They need only Git, CI, and your tool admin console. Details: Table 15.17 in the book.

- [ ] Time-to-PR
- [ ] Time-to-merge
- [ ] AI-assisted flag on the PR template
- [ ] Test coverage trend
- [ ] Build failure rate
- [ ] Seats vs active users
