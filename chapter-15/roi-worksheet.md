# ROI Worksheet: The Honest Calculation

Use this sheet to record your own numbers. Definitions and reasoning: Chapter 15, Section 15.7.

Complete it BEFORE the pilot. Budget the J-curve valley up front.

The book's quarterly pattern is illustrative. It is not a benchmark. What sets the depth and duration of the valley for your team: Chapter 15, Section 15.7. Readiness scores and migration-phase sequencing: Chapters 13-14.

## Step 1: Total cost, per quarter

Include every category. Definitions and the rows budgets most often miss: Table 15.10 in the book.

| Cost category | Hint | Often missed? | Q1 | Q2 | Q3 | Q4 |
|---------------|------|---------------|----|----|----|----|
| Tool licenses | Seats plus metered usage | Yes | | | | |
| API tokens | Inference spend, all agents | Sometimes | | | | |
| Infrastructure | Memory and coordination stores | Sometimes | | | | |
| Training time | Multi-quarter ramp, both tracks | Yes | | | | |
| Productivity dip | J-curve valley (Chapter 13) | Yes | | | | |
| Maintenance | Rules, agents, governance tests | Yes | | | | |
| Review overhead | Human review of agent output | Yes | | | | |
| **Total investment** | | | | | | |

Interactive and unattended agent usage are often metered as separate billing streams. If your vendor splits them, give each its own row.

## Step 2: Total value, per quarter

Expected timeline for each row: Table 15.11 in the book. Check it before you call a value missing.

| Value category | Hint | Q1 | Q2 | Q3 | Q4 |
|----------------|------|----|----|----|----|
| Velocity improvement | DORA lead time, deploy frequency | | | | |
| Quality improvement | Failure and defect rates | | | | |
| MTTR reduction | Fix and resolution times | | | | |
| Developer satisfaction | Survey scores, flow time | | | | |
| Innovation capacity | Hours moved to design work | | | | |
| **Total return** | | | | | |

## Step 3: The quarterly J-curve view

Expected shape: Table 15.12 and Figure 15.5 in the book.

1. Log your actuals here as each quarter closes.
2. Compare them with the book's shape.

| Quarter | Your investment | Your return | Your cumulative ROI |
|---------|----------------|-------------|---------------------|
| Q1 | | | |
| Q2 | | | |
| Q3 | | | |
| Q4+ | | | |

## Step 4: What the CFO will ask

Answer these six questions before the meeting. Write the answers here. What engineering should bring for each: Table 15.14 in the book.

| CFO question | Hint | Your answer |
|--------------|------|-------------|
| What problem does this solve? | Name the workflows and owners | |
| How will we measure gains? | Baselines, targets, dollar value | |
| How much will we spend? | One budget line, all costs | |
| When does this pay back? | Stage gates on the J-curve | |
| What are the new risks? | Chapter 12 governance summary | |
| When do we scale or shut down? | Exit criteria for the pilot | |

## Step 5: The effective gain check

**Effective gain per feature** = (human hours saved x blended hourly cost) minus (AI token cost + tool amortization + infrastructure allocation + governance overhead)

Apply the three adjustments from Section 15.7 before you present the number.

| Adjustment | Hint | Your value |
|------------|------|------------|
| Raw effective gain per feature | From the formula above | |
| Quality adjustment | Subtract rework from new defects | |
| Learning curve adjustment | Months 1-6 run negative | |
| Capacity reallocation note | Throughput gain or cost saving? | |
| **Adjusted gain** | | |
