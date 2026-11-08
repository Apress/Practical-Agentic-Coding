# Chapter 15: Measuring Success: KPIs and ROI for AI-Augmented Teams

Chapter 15 covers how to measure AI-augmented teams and calculate ROI. This folder has the fill-in sheets for that work.

## What this chapter ships

Chapter 15 has no code lab. You build a metrics dashboard for your own team (Section 15.9). This directory has:

- the fill-in dashboard template for that build
- the reference sheets to keep open while you do it

```text
chapter-15/
├── README.md                # This file
├── kpi-quick-reference.md   # Part III system KPIs, leading/lagging split, what not
│                            #   to measure, minimum viable set (Sections 15.5-15.8)
├── roi-worksheet.md         # Quarterly investment/return worksheet with the J-curve
│                            #   framing (Section 15.7)
└── dashboard-template.md    # The Section 15.9 dashboard: seven starter KPI rows
                             #   plus a blank fill-in copy for your team
```

## Assets

- **[kpi-quick-reference.md](./kpi-quick-reference.md)**: a fill-in sheet for the agentic-specific KPIs from Section 15.5. It covers memory system, multi-agent coordination, DevOps pipeline, and governance KPIs. Each row has a data source and baseline/target columns for your own numbers. Definitions and target ranges are in the chapter.
- **[roi-worksheet.md](./roi-worksheet.md)**: a fill-in worksheet for the quarterly investment, return, and cumulative ROI from Section 15.7. It lists the cost categories to budget. The book's timeline is illustrative. It is not a guarantee.
- **[dashboard-template.md](./dashboard-template.md)**: the Section 15.9 measurement dashboard (Table 15.18) as a fill-in sheet. It has two tables:
  - The book's seven KPIs as starter rows. The KPI and data source are pre-filled. You set the other four columns.
  - A blank six-column copy for your own team. The columns are KPI, data source, cadence, your target range, action trigger, and owner.

The Part II tools have enterprise cost and usage features that feed the cost and adoption rows. Examples are Kiro credit pooling and usage export, Copilot usage metrics, and Claude Code spend controls. See the "Go further" lists for [Kiro](../chapter-05/README.md#go-further-with-kiro), [Cursor and GitHub Copilot](../chapter-07/README.md#go-further-with-cursor-and-github-copilot), and [Claude Code](../chapter-08/README.md#go-further-with-claude-code).

## How to use this chapter's assets

1. Read Sections 15.1-15.4 first.
2. Set up the six minimum-viable metrics (Section 15.8) before anything else. They come from Git, CI, and your tool admin console. The setup is a PR-template checkbox and a weekly CI export.
3. Wire the KPIs from [kpi-quick-reference.md](./kpi-quick-reference.md) into the systems you built in chapters 9-12. Each KPI's data source column names the log or system that already emits the data. The systems are:
   - the [Chapter 9](../chapter-09/) memory system
   - the [Chapter 10](../chapter-10/) multi-agent coordination lab
   - the [Chapter 11](../chapter-11/) DevOps pipeline
   - the [Chapter 12](../chapter-12/) governance suite
4. Fill in [roi-worksheet.md](./roi-worksheet.md) before the first Finance conversation.
5. Fill in every column of the dashboard table in [dashboard-template.md](./dashboard-template.md) for your own team. Include the action trigger and a named owner on every row.

Budget one to two hours for the fill-in work (steps 2-5). The reading in step 1 is separate.

You are done when:

- the six minimum-viable metrics are flowing
- every dashboard row has all six columns filled, including an action trigger and a named owner

## Prerequisites

All three documents are plain markdown tables. Copy them into your own notes, spreadsheet, or wiki. Then fill them in.

The Part III KPIs need the chapters 9-12 systems running, because those systems emit the data. See [../chapter-09/](../chapter-09/), [../chapter-10/](../chapter-10/), [../chapter-11/](../chapter-11/), and [../chapter-12/](../chapter-12/) (each README covers setup for its hands-on lab).
