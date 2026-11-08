# Challenge Lab: Extending the Daily Briefing Agent

**Reference**: Chapter 5, Section 5.7 (the hands-on lab) and the Chapter Exercises at the end of Chapter 5

**Time**: Budget 45 to 90 minutes per challenge. The challenges are independent. Do them in any order. Challenge 1 is closest to the lab you just finished. Each one ends with success criteria you can check yourself.

> **Current tool behavior (as of November 7, 2026).**
>
> - Kiro's file hooks do not fire on saves you make yourself in the editor. They fire when Kiro's agent saves a file. This affects Challenge 3.
> - Kiro's Create powers page and its Power Builder use only three parts: `plugin.json`, `mcp.json`, and `skills/`. The Power Builder turns steering files into skills instead of the `dev.kiro/` directory Section 5.5 describes. This affects "Build a Power" under Going Further.

## Overview

The hands-on lab took the Daily Briefing agent from a vibe prompt to a deployed application. These four challenges are the exercises printed at the end of Chapter 5. Each one changes something the specs already decided. You drive each change through the specification. Do not edit generated code.

There are no answer keys. Agentic output is not reproducible line for line. Each challenge gives you:

- A starting prompt
- A list of artifacts that must change
- Success criteria you can check yourself

The three practice exercises in [`../hands-on-lab/exercises/`](../hands-on-lab/exercises/) do have fixed answers. Each ends with an answer key or sample solutions.

## Prerequisites

- The hands-on lab (Section 5.7) completed at least through Phase 7, with the application running locally
- Kiro authenticated
- The AWS Infrastructure Power installed (Phase 5)
- The AWS MCP servers connected (Phase 6)
- An AWS account you can deploy to, if you want to take Challenge 1 past template validation
- Your `.kiro/` directory committed to Git. You can then diff what each challenge changes and roll back cleanly

## Before You Start

Commit your work and create a branch. Every challenge rewrites spec files. Use `git diff` on the requirements to see what changed.

```bash
git add .kiro/ && git commit -m "chore: checkpoint before challenge lab"
git checkout -b challenge-1-ecs-migration
```

---

## Challenge 1: Modify the Briefing Agent (Deployment Model)

**From the book**: "Update the requirements to change the deployment model to ECS, ALB, and CloudFront instead of AppRunner."

### The Problem

The lab used App Runner, the shortest path to a running container. Real projects can need something else. For example:

- Your platform team standardizes on ECS.
- Security requires a WAF in front of the load balancer.
- You need path-based routing that App Runner cannot express.

This change is like the Lightsail to App Runner switch in Phase 8, one layer deeper.

### What to Do

Start in the chat. Do not start in the CloudFormation templates:

```text
The deployment target is changing. Replace AWS App Runner with ECS Fargate behind
an Application Load Balancer, with CloudFront in front of the ALB. Update the
requirements, the design document, the AWS architecture diagram, and the
implementation tasks to reflect this. Call out every IAM policy, security group,
and networking change the switch requires, and tell me which existing tasks
become obsolete.
```

If you deployed with Amazon ECS Express Mode (see the App Runner note at the top of the lab README), the ECS service and load balancer already exist. In that case, the challenge is to put CloudFront in front of the ALB and restrict the ALB to CloudFront.

Review what Kiro proposes before you let it change a template.

### Artifacts That Must Change

- `.kiro/specs/tech-news-aggregator/requirements.md`: the deployment requirement and its acceptance criteria
- `.kiro/specs/tech-news-aggregator/design.md`: architecture section, diagram, IAM and networking detail
- `.kiro/specs/tech-news-aggregator/tasks.md`: App Runner tasks removed or replaced, ECS and ALB tasks added in dependency order
- `.kiro/steering/tech.md`: the AWS services table
- The application stack CloudFormation template. The base stack with VPC, database, and S3 should barely change, because the lab split the infrastructure into two stacks

### Success Criteria

- No reference to App Runner survives anywhere in `.kiro/` or in the templates
- Task ordering still respects dependencies: cluster and task definition before service, target group before listener, ALB before CloudFront origin
- The templates pass `cfn-lint`, and `cfn-guard` reports no new security findings
- The ECS task role grants exactly the Bedrock, S3, and Secrets Manager access the App Runner role had, and nothing more
- CloudFront is the only public entry point. The ALB is internal or restricted to CloudFront's prefix list

### Reflection

Note which changes were mechanical and which needed a judgment call. Note where Kiro made an infrastructure decision you would have made differently. Note whether a steering rule would have prevented it.

---

## Challenge 2: Vibe Check (Persona Swap)

**From the book**: "Change the functional requirement from 'witty journalist' to 'academic researcher' and document how the code structure and output change."

### The Problem

The "Witty Tech Journalist" persona is a vibe requirement. In this challenge you swap the persona and measure how far the change spreads. The background is in Chapter 5, Section 5.2.

### What to Do

Capture a baseline first. Run the app and save the generated briefing:

```bash
cp briefing_$(date +%Y-%m-%d).md baseline-witty.md
```

On Windows (PowerShell):

```powershell
Copy-Item "briefing_$(Get-Date -Format yyyy-MM-dd).md" baseline-witty.md
```

Then change the persona through the spec:

```text
The persona is changing from "Witty Tech Journalist" to "Academic Researcher."
The tone is measured, precise, and cites sources; it avoids sarcasm and prefers
qualification over confidence. Update product.md, the requirements, and the
summarization prompt. Tell me which parts of the codebase this touches and which
parts are persona-independent.
```

Regenerate a briefing on the same stories. Diff the two briefings.

### Artifacts That Must Change

- `.kiro/steering/product.md`: the persona and voice section
- `.kiro/specs/tech-news-aggregator/requirements.md`: the summary tone acceptance criteria
- The summarization service prompt (wherever Kiro put it during the lab)
- Any UI copy, headers, or empty-state text that carried the witty voice
- Tests that assert on tone or on specific phrasing

### Success Criteria

- You can name every file the persona change touched, and every file it did not
- The summarization service interface is unchanged. The persona is data, not structure. If Kiro changed the interface, ask it why and decide whether that was necessary
- Both briefings summarize the same source stories, so the diff shows only the change in voice
- You have written a short note (three or four sentences is enough) on what the diff shows about how far a vibe requirement reaches

### Reflection

Check whether the persona swap stayed in the prompt layer or leaked into ranking, filtering, or data models. If it leaked, find out why. Write down the specification that would have prevented it.

---

## Challenge 3: Security Hook (Pre-Commit Scanner)

**From the book**: "Implement a pre-commit security scanner for codebase data security."

### The Problem

The final prompt in the lab asked Kiro to sweep the repository for credentials, AWS account names, and PII before the first commit. That was a one-time cleanup. This challenge makes the check continuous.

Kiro hooks fire on Kiro's own lifecycle events (`PostFileSave`, `Stop`, `PreToolUse`, and so on), not on Git's.

- A hook can review a file the moment Kiro's agent saves it.
- A hook can run a scanner from the terminal.
- As of November 7, 2026, Kiro's file hooks do not fire on saves you make yourself in the editor.
- A hook cannot by itself block a `git commit` you run outside Kiro.

So a complete answer has two halves.

### What to Do

**Half one: the Kiro hook.** Create a hook on `PostFileSave`, scoped to source files. It reviews the saved file for:

- Hardcoded credentials
- AWS account numbers
- Real email addresses and personal names
- Connection strings
- Private keys

Start from the prompt in [`../code-examples/hooks/security-audit.kiro.hook`](../code-examples/hooks/security-audit.kiro.hook). Tighten it:

1. Narrow the file pattern.
2. Make the prompt report a severity and a remediation for each finding.

In Kiro IDE 1.0 and later, create the hook through the AGENT HOOKS (+) chat flow. Do not copy the file. That example uses the pre-1.0 format.

**Half two: the Git gate.** Ask Kiro to add a real pre-commit hook. The check then holds when you commit from a plain terminal:

```text
Add a pre-commit security gate to this project. Use a config-driven scanner
(detect-secrets or gitleaks) wired through the pre-commit framework, with the
configuration committed to the repository. Add a Make target so contributors can
run the same scan on demand, and add a task to tasks.md covering the setup.
Update .gitignore for anything the scan flags as generated.
```

### Artifacts That Must Change

- Your new hook in `.kiro/hooks/` (Kiro 1.0 and later saves it as `<name>.json`), enabled, with a narrow file pattern
- `.pre-commit-config.yaml`: the Git-level gate
- The scanner's own config (`.secrets.baseline` or `.gitleaks.toml`)
- `Makefile`: a `security-scan` target
- `.kiro/steering/tech.md` or a new `security-policies.md`: the rule the hook enforces, written down
- `.gitignore`: anything the scan flags that should never have been tracked

### Success Criteria

- Asking Kiro to write a file that contains a fake AWS key triggers the hook. The hook produces a finding with a severity and a fix. Saving that file yourself does not fire Kiro's file hooks
- The pre-commit gate blocks a commit containing that same fake key, run from a terminal outside Kiro
- The scan is clean on your existing repository, or every remaining finding is a deliberate, documented allowlist entry
- The hook does not fire on documentation, test fixtures, or lockfiles. It stays fast enough to leave on
- No real secret is committed as part of building this, including in your test fixtures. Use obviously fake values

### Reflection

Compare the two halves. The Kiro hook can read intent. The pre-commit gate cannot, but it also cannot be talked out of blocking. Decide which one you would trust as the last line of defense. Write down why you might keep both.

---

## Challenge 4: Agent Steering (Generate and Tune)

**From the book**: "Generate an agent steering document for the project and experiment with adding steering rules."

### The Problem

The lab gave you `product.md`, `tech.md`, and `structure.md`. In this challenge you add domain steering on top. Then you measure whether a steering rule changes agent behavior. Section 5.4 lists five common domain documents:

- API standards
- Testing approach
- Code style
- Security guidelines
- Deployment process

### What to Do

Ask Kiro to read the codebase it just built and write the steering that matches it:

```text
Read the source, tests, and infrastructure in this project and generate a
testing-standards.md steering file that documents the conventions actually in
use: test layout, markers, fixture patterns, mocking approach, and coverage
expectations. Use inclusion: fileMatch scoped to test files. Where the codebase
is inconsistent, flag the inconsistency instead of picking a winner.
```

Then run the experiment:

1. Pick one rule in that file.
2. Ask Kiro to add a new test.
3. Check whether Kiro followed the rule.
4. Invert the rule.
5. Ask for a comparable test.
6. Check again.

### Artifacts That Must Change

- `.kiro/steering/testing-standards.md`: new, with `inclusion: fileMatch` and a `fileMatchPattern` that matches your test files
- At least one more domain file of your choosing (`api-standards.md`, `code-conventions.md`, `security-policies.md`, or `deployment-workflow.md`)
- `AGENTS.md`: updated if the new steering supersedes something already stated there
- A short `steering-experiment.md` of your own recording the before-and-after of the rule you inverted

### Success Criteria

- Every new steering file has valid YAML front matter and an inclusion mode chosen deliberately, not by default
- The `fileMatch` pattern fires. The rule affects generated test files and does not affect generated source files
- At least one file uses a live-file link (`#[[file:...]]`) so the steering cannot drift from the artifact it describes
- No credentials, account identifiers, or personal data appear in any steering file
- Your experiment note names the rule, the two prompts, and what changed in the output. "No observable change" is a legitimate finding if you can show it

### Reflection

List which rules changed behavior and which Kiro ignored. An ignored rule is usually one of these:

- Too vague to act on
- Phrased as a preference, not a constraint
- Contradicted by something in `AGENTS.md`

Rewrite one ignored rule until Kiro follows it.

---

## Going Further

Ideas that go past the printed exercises:

- **Add a second source.** Hacker News is one scraper. Add a second one. An RSS feed is easiest. This exercises the deduplication requirement.
- **Deliver the briefing.** Add email or Slack delivery on a schedule.
- **Ship a bugfix spec.** Break something on purpose. Then use a Bugfix Spec instead of the full gated flow. Compare the two workflows. Section 5.7, Phase 2 names the spec modes.
- **Build a Power.** Bundle the steering files and MCP configuration from this project into a Kiro Power. Install it into a fresh project (Section 5.5). Use the Agent Plugins layout:
  - A `plugin.json` manifest with activation keywords
  - `mcp.json` for the servers
  - A `skills/` directory of SKILL.md packages that carries the steering guidance

  As of November 7, 2026, Kiro's Create powers page and its Power Builder use only those three parts. The Power Builder turns steering files into skills instead of the `dev.kiro/` directory Section 5.5 describes. Write the Power by hand or use the Power Builder. Then test it locally: in the Powers panel, use Add Custom Power and import from a folder.

## Where to Look When You Get Stuck

- Hook configuration reference and examples: `../code-examples/hooks/`
- MCP server examples and troubleshooting: `../code-examples/mcp-configs/`
- Steering file locations and inclusion modes: `../tutorials/steering-files-guide.md`
- The author's reference specs, to compare against your own: `../daily-briefing-agent/.kiro/specs/tech-news-aggregator/`
- Kiro's own documentation: [kiro.dev/docs](https://kiro.dev/docs/)

When something in Kiro fails, paste the terminal output into Kiro Chat and ask Kiro to diagnose it. See Section 5.7 (Phase 5).
