# Case Study Worksheet

Use this template to document your own agentic transformation. It follows the structure of the Chapter 13 case studies.

Start filling it in on day one of a pilot. You cannot reconstruct baselines later. Baselines also back the leadership conversation in Chapter 15.

---

## 1. Goal

Write the outcome this transformation should produce. State it as a business or engineering outcome. A tool deployment is not a goal. ("Reduce time from PR open to merge" is a goal. "Roll out Claude Code" is not.)

- Primary goal:
- Success criteria (how you will know it worked):
- Timebox:

## 2. Baseline

Record the before-state with numbers. The table is a suggested minimum. For the full measurement setup, see Chapter 15.

| Metric | Baseline value | Date captured | Source |
|--------|---------------|---------------|--------|
| Lead time for changes | | | |
| Deployment frequency | | | |
| Change failure rate | | | |
| Review queue age (PR open to merge) | | | |
| Relevant cost line (licenses, tokens) | | | |

Also record the qualitative baseline:

- Readiness scores (from [readiness-rubric.md](./readiness-rubric.md)):
- Where the team sits on the Bias Spectrum (Chapter 14):
- Current tool stack and who uses what:

## 3. Intervention

What you actually changed, in order.

- Tools and configuration introduced (memory files, agents, hooks, gates):
- Governance deployed alongside (not after) the tools:
- Training provided (technology track AND cultural track, per Section 13.8):
- What you deliberately did NOT change:

## 4. Metrics during and after

Track the same metrics as the baseline. Set the measurement dates to match the J-curve in Section 13.7. Expect the valley in weeks 5-12. Do not read the valley as failure.

| Metric | Week 4 | Week 12 | Week 26 | Notes |
|--------|--------|---------|---------|-------|
| | | | | |

## 5. Lessons

- What worked, and which chapter pattern it maps to:
- What failed, and which named failure pattern it was (velocity-quality trap, tool sprawl, review bottleneck, agent loops, governance gap, emotional friction):
- What you would sequence differently:
- What goes into institutional memory (rules, skills, context libraries) so the next team does not relearn it:
