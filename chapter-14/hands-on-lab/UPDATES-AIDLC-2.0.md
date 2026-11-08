# AI-DLC Workflows 2.x: How It Differs and How to Run This Lab on It

> **Update to the book (as of November 7, 2026).** AI-DLC 2.11.3 is the
> stable release on the repository's default `main` branch. These notes were
> checked against 2.11.0. The 2.11.3 changes are noted where they apply. The
> 2.x line ships a release every week or two. Treat the details below as a
> snapshot.

For the latest, use the vendor's own guides:

- the [repository README](https://github.com/awslabs/aidlc-workflows) and its
  Getting Started guide
- the documentation site at
  [awslabs.github.io/aidlc-workflows](https://awslabs.github.io/aidlc-workflows/)
  (User Guide, Harness Engineer Guide, Developer Reference)

## Where the two versions live

As of November 7, 2026, the two versions live here:

- **2.x is the default.** The `main` branch carries Workflows 2.x (2.7.0,
  the first 2.x release from `main`, shipped on 2026-09-01). Links to a `v2`
  branch redirect to `main`.
- **1.x lives on a `v1` branch.** The repository keeps it "for existing v1
  installations and maintenance." New installations are pointed at `main`.
- The 1.x rules zips (v1.0.0 and v1.0.1) are still on the Releases page. The
  Section 14.9 lab is pinned to v1.0.1 and works unchanged.
- **An Operations phase for 1.x** is in development on a separate
  `v1-operations` branch. It has three parts: Rules Validation, Deployment,
  and Post-Deployment Testing. It is not part of any 1.x release yet.

## What carries over and what differs

These Chapter 14 terms carry over to 2.x:

- **Phases**: Inception and Construction are unchanged. 2.x has five phases
  instead of three, numbered 0 to 4:
  - Initialization and Ideation come before Inception.
  - Construction follows Inception.
  - A full Operation phase comes last. Operations was the least mature part of 1.x.
  - There are 33 stages in all, with a verification gate between phases.
- **Bolts**: still the unit of Construction work.
  - Construction can start with a walking skeleton. The first Unit goes
    through every stage before the others start.
  - You choose whether ordinary checkpoints stop for you or pass
    automatically under an explicit grant.
  - A failure stops Construction either way.
- **Units of Work**: kept (Units Generation and Delivery Planning stages).
- **Human-in-the-loop gates**: kept. From Ideation on, you approve each stage
  before the workflow moves on.
- **Mob elaboration**: kept, as a mob of agents. User Stories is the stage
  that runs this way.

These parts differ in 2.x:

- **Executable engine.** The workflow is an engine. In 1.x it was rules text. A
  deterministic engine makes the routing and stage decisions. The `/aidlc`
  session is the "conductor." It carries out each decision and then asks the
  engine for the next move.
- **Verification.** Stages carry machine-checkable verification.
- **Learning loop.** When you confirm a correction at a stage's approval
  gate, it is saved as a persistent rule. You do not need to make the same
  correction twice.
- **Record directory.** Each piece of work gets its own directory,
  `aidlc/spaces/<space>/intents/<YYMMDD>-<label>/`, with an audit trail. 1.x
  used a loose `aidlc-docs/` folder.
- **Workflow profiles.** The engine calls a profile a scope. Eleven ship:
  `classic`, `express`, `feature`, `enterprise`, `mvp`, `poc`, `bugfix`,
  `refactor`, `infra`, `security-patch`, `workshop`. Each has its own stage
  route and a depth: `minimal`, `standard`, or `comprehensive`.
- **Agents.** Fourteen agents cover the lifecycle:
  - eleven domain agents: Product, Design, Delivery, Architect, AWS Platform,
    Compliance, DevSecOps, Developer, Quality, Pipeline & Deploy, Operations
  - two reviewers
  - a composer that builds a plan when no profile fits
- **Plugins.** A plugin mechanism supports team extensions. The repository
  ships `test-pro`.

**Team Units.** As of November 7, 2026, teammates can each take a Unit of
Construction. Team Units need a single-repository workspace.

1. In your own clone, claim a Unit with `/aidlc --claim <unit>`.
2. Work it through its stages.
3. Publish it from that clone with `/aidlc unit publish <unit>`.
4. From a checkout that holds no Unit claim, run `/aidlc unit pin <unit>`. It
   asks one merge question. Choose Approve to land the Unit.
5. In the claiming clone, run a plain `git pull` to take main back.

`/aidlc team-board` shows claims and merge readiness. 2.11.3 is the first
release where the flow runs end to end with an agent. It was tried on Claude
Code and GitHub Copilot CLI. Its release notes list gaps that are still open
([CLI commands](https://github.com/awslabs/aidlc-workflows/blob/v2.11.3/docs/guide/12-cli-commands.md),
[2.11.3 release notes](https://github.com/awslabs/aidlc-workflows/releases/tag/v2.11.3)).

## Running the Section 14.9 lab on 2.x

Prerequisites:

- Claude Code (or another supported harness), installed and signed in
- Git

The native installer brings everything else. You do not install bun yourself.
Only the manual-copy install path needs it.

Use a fresh folder. Do not reuse your 1.x lab folder. The two versions write different
files into a project. As the book says, do not mix them.

1. Install AI-DLC once per machine.

   macOS, Linux, or WSL:

   ```bash
   curl -fsSL https://github.com/awslabs/aidlc-workflows/releases/latest/download/install.sh | sh
   ```

   Windows PowerShell:

   ```powershell
   irm https://github.com/awslabs/aidlc-workflows/releases/latest/download/install.ps1 | iex
   ```

   If the installer prints a PATH instruction, apply it. On Windows, open a
   new terminal. Then check the install with `aidlc version`.

2. Set up the project for Claude Code and check it. These commands are the
   same in bash and PowerShell:

   ```bash
   mkdir aidlc2-lab
   cd aidlc2-lab
   git init
   aidlc config --harness claude
   aidlc doctor
   ```

   If `aidlc config` asks, accept the recommended defaults. It writes:

   - `.claude/`
   - `aidlc/`
   - `aidlc.settings.json`
   - a `.mcp.json`, when MCP servers are on
   - its own block in `.gitignore`

   On a new project, `aidlc doctor` usually reports a few advisory warnings.
   For example, it may say the hooks have not run yet. Fix any `fail` row.

   To hold the project on one release, also run `aidlc config --pin <version>`
   with the version that `aidlc version` prints. The pin is written to
   `.aidlc-version`. It applies to everyone who clones the project.

   > **Security update (as of November 7, 2026).** Pin 2.11.3 or later.
   > Through 2.11.0, the installed engine read a cloned project's `.env` and
   > ran its `bunfig.toml` preload. The native `aidlc` through 2.11.2 carries
   > a Bun decoder with a known exploited flaw
   > ([2.11.3 release notes](https://github.com/awslabs/aidlc-workflows/releases/tag/v2.11.3)).
   > Upgrading Bun on its own does not fix it. Run `aidlc update`. Then run
   > `aidlc config --pin 2.11.3` in any project pinned to an older release.

   The setup keeps the model provider and login that Claude Code already
   uses. It writes provider settings only if you choose Amazon Bedrock
   (`aidlc config providers`). In that case, set up Bedrock model access and
   AWS credentials before the first run.

3. Start Claude Code in the folder (`claude`). Trust the folder when it asks.
   Then start the workflow with the lab scenario. The colon tells the engine
   that `feature` is the profile. The rest is your request. `feature` runs the
   full lifecycle, including the Operation phase the challenge lab needs:

   ```text
   /aidlc feature: I need to add notification preferences to our user
   service. We need endpoints for getting, updating, and deleting
   notification preferences. Supported channels: email, SMS, push.
   ```

   A plain `/aidlc <description>` also works. The agent proposes a profile
   and asks you to confirm it before anything starts. Inside the session:

   - `/aidlc --status` shows progress.
   - `/aidlc --doctor` reruns the health check.

Compared with the 1.x lab, expect these differences:

1. The engine takes you through explicit, numbered stages. 1.x used
   free-form directed questions. Approval gates are fixed stages in the
   workflow.
2. Construction checks each Unit against machine-checkable verification
   before your checkpoint. Once you grant it, ordinary checkpoints can pass
   automatically. A failure still stops the run.
3. Artifacts land under `aidlc/spaces/.../intents/...` with an audit trail.
   1.x wrote loose markdown files.
4. Corrections you confirm at gates become persistent rules (the learning
   loop). The workflow adapts to your team over time.

The lab goal is the same on both versions. Inception finds the requirements
you missed. Construction ships a tested increment.

## The Section 14.10 challenge lab: two routes to Operations

The challenge lab wires AI-DLC into CI/CD. That is where the two versions
differ most. On the v1.0.1 rules this lab installs, Operations is a
placeholder. The v1 README marks it as future work. There is no Operations
phase to trigger. Section 14.10 offers two routes. This file documents both.

**Route 1: build the phase on the 1.x lab setup (any harness).**

1. Keep the 1.x rules from the Section 14.9 lab.
2. Build the Operations phase yourself in your pipeline. Give it the shape
   Workflows 2.x ships:
   - deployment, health validation, and verification stages
   - escalation to a human when a stage cannot verify
3. Start from the scaffold at
   [../challenge-lab/starter/.github/workflows/aidlc-operations.yml](../challenge-lab/starter/.github/workflows/aidlc-operations.yml).
   It already has that shape:
   - security and cost gates that block merges
   - a canary deploy job with health-based rollback
   - an audit artifact trail
4. Write the code at each numbered TODO.

This route works with every tool from Part II. The phase logic lives in your
workflow file. To see how AWS is building the same stages
for 1.x, read the unreleased `v1-operations` branch. The challenge does not
depend on it.

**Route 2: run the phase natively on 2.x (supported harnesses only).** The
2.x engine ships a full Operation phase. It has Pipeline & Deploy and
Operations domain agents, machine-checkable verification at each stage, and
an audit trail.

1. Install 2.x as described above.
2. Pick a profile that runs the Operation phase. `feature` and `enterprise`
   run all 33 stages. `mvp` and `classic` do not run Operation.
   `/aidlc --status` shows what your run selected.
3. The engine covers these challenge success criteria natively:
   - verification gates
   - the audit trail
   - human escalation
4. Wire the engine's run into CI.
5. Add the Chapter 11 security and cost gates around it.

> **CI update (as of November 7, 2026).** Set `AIDLC_UNATTENDED=1` in the CI
> job. Gates keep waiting for a person. A pipeline can run stages but cannot
> approve them. From 2.11.3, if the agent asks on its own for a system
> package install, the install is held. It does not run. Install the job's tools in a
> step before AI-DLC starts
> ([interaction modes](https://github.com/awslabs/aidlc-workflows/blob/v2.11.3/docs/guide/07-interaction-modes.md),
> [2.11.3 release notes](https://github.com/awslabs/aidlc-workflows/releases/tag/v2.11.3)).

Check the harness table in the repository README first. As of November 7,
2026, it lists Claude Code, Kiro IDE and Kiro CLI, Codex CLI, Cursor,
opencode, and GitHub Copilot. If your pipeline's harness is not on it, take
Route 1.

**On Kiro, check the harness name against your release.** As of November 7,
2026:

- On 2.11.3, `aidlc config --harness kiro-ide` sets up Kiro IDE and Kiro
  CLI's v3 engine. `--harness kiro` sets up Kiro CLI (V2).
- In 2.11.4-preview.20261106.1 and on `main`, the names swap. `kiro` means
  Kiro IDE and the v3 engine. Kiro CLI (V2) becomes `kiro-v2`.
- `kiro-ide` works on both. Use it for Kiro IDE and the v3 engine.
- Start Kiro CLI with the engine named: `kiro-cli --v3` or `kiro-cli --v2`.
  AI-DLC's own startup lines say the same
  ([repository README](https://github.com/awslabs/aidlc-workflows/blob/main/README.md),
  [2.11.3 release notes](https://github.com/awslabs/aidlc-workflows/releases/tag/v2.11.3),
  [2.11.4-preview.20261106.1 release notes](https://github.com/awslabs/aidlc-workflows/releases/tag/v2.11.4-preview.20261106.1)).

Both routes share the success criteria in the
[challenge lab README](../challenge-lab/README.md). Both follow the same
authentication rule. Headless CI agents run on an API key or workload
identity. They never use a personal subscription login.

## Version guidance

- Pin versions for anything you depend on.
  - `aidlc config --pin <version>` holds a project on one 2.x release.
  - The Section 14.9 lab pins the 1.x rules zip by its release URL.
- 1.x is not deprecated. It is not the default either. The repository keeps
  the `v1` branch for existing installations and maintenance. It points new
  installations at 2.x.
- To see which harnesses each version supports, check the repository. Do not
  rely on any printed list.
