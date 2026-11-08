# Chapter 3: The Human + AI Developer Model: Orchestration Principles

Chapter 3 covers how people lead teams that work with AI agents. This folder has copy-ready templates for that work.

## Why there is no code here (and what ships instead)

Chapter 3 is an organizational chapter. Its artifacts are team templates, context documents, and dashboards. None of them are programs.

The chapter prints two YAML examples:

- the Foundation Team template (Section 3.2)
- the project context framework (Section 3.3)

Copy them from the chapter into your own repository and edit them. You do not run them. This folder does not ship them as files, so you have no second copy to keep in sync.

The other templates from the chapter are shipped here as editable files:

- **[decision-authority-matrix.md](decision-authority-matrix.md)**: the Table 3.1 decision-authority framework, with room for your own decision types (Section 3.3).
- **[hybrid-standup-format.md](hybrid-standup-format.md)**: the hybrid standup agenda and the AI agent status-report format (Section 3.3).
- **[hybrid-team-dashboard-template.md](hybrid-team-dashboard-template.md)**: the sprint dashboard as a fill-in template, with the book's Sprint 23 worked example (Section 3.4).
- **[hybrid-retrospective-format.md](hybrid-retrospective-format.md)**: the 60-minute hybrid retrospective structure (Section 3.4).

| Book section | Topic | Where the practical material lives |
|---|---|---|
| 3.1 | Introduction (the economic and investment reality) | Conceptual; the ROI models are in [chapter-15](../chapter-15/) |
| 3.2 | Team composition and structure | Copy the Foundation Team template from the chapter into your own repo |
| 3.3 | Communication and coordination strategies | Copy the project context framework from the chapter; templates here: [standup format](hybrid-standup-format.md), [authority matrix](decision-authority-matrix.md); the machine-readable equivalent for agents is AGENTS.md, see [chapter-04](../chapter-04/code-examples/agents-md/) |
| 3.4 | Performance management and measurement | Templates here: [dashboard](hybrid-team-dashboard-template.md), [retrospective](hybrid-retrospective-format.md); [chapter-15](../chapter-15/) ships the KPI reference and worksheets |
| 3.5 | Real-world orchestration architectures | Conceptual; the A2A protocol the Gemini example relies on is configured in [chapter-04](../chapter-04/code-examples/a2a-protocol/), and Kiro gets a full lab in [chapter-05](../chapter-05/) |
| 3.6 | Measuring orchestration effectiveness | [chapter-15](../chapter-15/) |
| 3.7 | Challenges and mitigation strategies | Context overflow is addressed by the memory system in [chapter-09](../chapter-09/) |
| 3.8 | Future directions and emerging patterns | [chapter-10](../chapter-10/) builds a coordinated agent team you can run |

## Where to go next in this repo

- **[chapter-10](../chapter-10/)**: builds the orchestration patterns from Section 3.8 as a working multi-agent team, with handoff protocols and shared state.
- **[chapter-14](../chapter-14/)**: has the migration and skill-development plans. They turn the target structure from Section 3.2 into steps.
- **[chapter-15](../chapter-15/)**: has the metrics for the review process in Section 3.4.
