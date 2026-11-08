# Challenge Lab: Debugging with Competing Hypotheses

Reference: Chapter 10, Section 10.8

> **Agent teams switch (as of November 7, 2026).** Agent teams are experimental
> in Claude Code and disabled unless you opt in. To switch them on:
>
> 1. Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in your shell, or under
>    `"env"` in `.claude/settings.json`.
> 2. Start a new interactive session.
>
> Check the agent teams page at code.claude.com/docs for the current switch.
> Expect the interface details to shift.

**Time**: 45-60 minutes. This is the second half of the chapter's 90-120
minute lab budget (Sections 10.7 and 10.8).

**Prerequisites**:

- Claude Code CLI, signed in
- The experimental agent teams feature, switched on (see the note above)
- Python 3.11+

The starter services use the standard library only. There is nothing to install.

**Done when**: Your team's conclusion in `starter/findings.md` meets the
verification criteria below. Grade it against the rubric in
`solution/ROOT-CAUSE.md`.

## The scenario

A simulated e-commerce app fails intermittently at checkout with 500 errors. The failing service changes from request to request: payment, then inventory, then the API gateway. One investigator working alone tends to lock onto the first plausible theory. Your job is to run three investigators who argue it out.

## Requirements

Run an agent team of three teammates, one per hypothesis. Each teammate tries to break the others' theories:

```text
Create an agent team to investigate checkout failures.
Spawn 3 teammates:
- Payment investigator (hypothesis: payment gateway timeout under load)
- Inventory investigator (hypothesis: race condition on stock check)
- Gateway investigator (hypothesis: request header corruption on retry)
Have them share findings and try to disprove each other's theories.
Update a shared findings.md with the consensus.
```

## Verification criteria

- Teammates message each other directly. They do not only go through the lead.
- Teammates answer evidence that contradicts their own theory. They do not ignore it.
- Every investigator records its evidence in `findings.md`.
- The final report shows the chain from starting hypotheses through evidence to verdict.
- The team finds the true root cause, a race condition in inventory reservation.

## Bonus challenge

Add a fourth teammate whose only job is skepticism. It reads each hypothesis and looks for evidence against it. The other three must then defend their claims.

## Hints

- Switch on agent teams first. See the agent teams note at the top of this file.
- In each teammate's spawn prompt, tell it to read only its own service directory plus `logs/`. Then no investigator can quietly read another's evidence.
- This boundary is only an instruction. Claude Code does not enforce it. A subagent definition can limit which tools a teammate has. Nothing in Claude Code scopes those tools to one directory per teammate.
- The shared `findings.md` is the blackboard pattern from Section 10.6, as a plain file.
- Start with `starter/logs/`. Correlate the three log files on `request_id`. The sequence across files tells you more than any single line.
- All three hypotheses have real supporting evidence in the code and the logs. This is why a single agent stops early. Two of the three are still wrong.
- Do not open `solution/ROOT-CAUSE.md` until your team has written its conclusion. It is the answer key.

## Starter scaffolds

`starter/` holds a small simulated e-commerce application. It has three
services (payment, inventory, gateway) and a seeded concurrency bug. Each
service is a plain standard-library HTTP handler, so there is nothing to install.

```text
starter/
├── README.md              # scenario, how to run it, what your team must produce
├── findings.md            # shared investigation board, a template to fill in
├── run_services.py        # starts all three services
├── reproduce_failure.py   # concurrency harness plus a reconciliation report
├── logs/                  # production traces from the incident
└── services/              # payment, inventory, gateway
```

```bash
cd starter
python run_services.py --check   # verify all three answer /health, then exit
python run_services.py           # run all three (Ctrl+C to stop)
```

Reproduce the failure. It does not appear one request at a time:

```bash
python reproduce_failure.py --embedded --concurrency 8
```

Point your agent team at the `starter/` directory. Let it drive traffic and
read the code. Start with `starter/README.md`.

`solution/ROOT-CAUSE.md` is the answer key. It has a rubric for grading the
conclusion and the quality of the coordination. Read it only after your team
reaches a conclusion.
