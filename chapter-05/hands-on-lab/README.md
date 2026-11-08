# Hands-On Lab: Build the "Daily Briefing" Agent

**Reference**: Chapter 5, Section 5.7

**Time**: about 2.5 to 3 hours across eight phases. The per-phase breakdown is at the end.

**Done when**: everything under "Expected Outputs" checks out.

> **Current tool behavior (as of November 7, 2026).** The steps below follow Kiro, the AWS MCP servers, Amazon Bedrock, AWS App Runner, and LocalStack as they work today. Where they differ from the book, follow these steps:
>
> - **Workspace trust (Before You Start).** Kiro opens a folder you have not trusted in Restricted Mode. In Restricted Mode it ignores the folder's steering files and `.kiro/settings/mcp.json`. It does not run the folder's hooks. It asks before every command. Trust the starter folder before Phase 1, as "Before You Start" shows.
> - **Hooks (Phase 4).** Kiro IDE 1.0 and later create hooks through a chat flow. They save hooks as `.kiro/hooks/<name>.json`. They do not create Manual Trigger hooks. The starter's two hooks use the `.kiro.hook` format, which Kiro lists as legacy hooks.
> - **MCP servers (Phase 6).** AWS has retired the AWS Diagram MCP Server. Phase 2, Step 3 uses Mermaid diagrams instead. The AWS Knowledge MCP Server is a remote server you reach by URL.
> - **AWS API MCP Server (Phase 6).** AWS lists the AWS API MCP Server as superseded by its managed AWS MCP Server. The AWS API MCP Server still installs and runs, but it prints a deprecation notice. To follow AWS's recommended setup, add the AWS MCP Server instead. AWS's [setup guide](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/getting-started-aws-mcp-server.html) has the Kiro entry. If you use it, the guide says to remove the AWS API and AWS Knowledge entries. This keeps the agent from seeing duplicate tools.
> - **Bedrock (Phase 7).** Bedrock has no per-model access requests. Anthropic models need a one-time use-case form. Call current Claude models through an inference profile ID such as `global.anthropic.claude-haiku-5-5`. They accept only the default sampling settings, so leave `temperature`, `top_p`, and `top_k` out of requests. They also think by default. Read the text block by its type, and keep `max_tokens` well above the summary length.
> - **App Runner (Phases 7 and 8).** AWS App Runner does not accept new customers. The cutoff was April 30, 2026. Accounts that already use it can still create services. If your account is new to App Runner, use Amazon ECS Express Mode, which AWS recommends instead:
>   1. Name it in place of AppRunner in the Phase 8 prompt.
>   2. Ask Kiro to change the steering files (`tech.md` and `structure.md`) and `AGENTS.md` to match.
>
>   Express Mode runs the container on Fargate behind an Application Load Balancer (CloudFormation type `AWS::ECS::ExpressGatewayService`). Those resources bill while they exist, so the teardown steps still apply.
> - **LocalStack (Phase 7).** The `localstack/localstack` image starts only with a LocalStack auth token. See the Docker Desktop prerequisite.
> - **Spec modes (Phase 2).** Kiro calls the spec mode without approval gates Quick Spec. The book's term is Quick Plan.

## Overview

In this lab you build a working web application with Kiro's Spec-Driven Development (SDD) methodology. The application is a tech news aggregator. It:

- Collects technology news
- Summarizes it with a foundation model, using a "Witty Tech Journalist" persona
- Saves the result as a daily briefing markdown file

In each phase you work the same loop:

1. State your intent.
2. Review what the agent proposes.
3. Correct the specification, not the code.
4. Regenerate.

**On reproducibility**: Agentic coding is not deterministic. Your requirements, design, and tasks will differ from the author's and from other readers'. The model, its version, and your exact phrasing all change the result. This is expected. Experiment with the prompts. For example, to build the frontend in Vue instead of Flask templates, or to summarize with a non-Bedrock model, change the constraints and compare the result.

## Learning Outcomes

By completing this lab, you will:

- Create and configure Kiro steering files
- Write specs using the SDD flow, with EARS-notation acceptance criteria
- Configure hooks for automated testing and documentation
- Install and use a Kiro Power for AWS infrastructure
- Configure MCP servers for external tool access
- Execute tasks iteratively to build a complete application
- Change an architectural decision after implementation has started, through the spec

## Prerequisites

### Software

- [Kiro](https://kiro.dev/docs/getting-started/installation/), installed and authenticated. If you have not done this yet, follow [`../tutorials/kiro-setup.md`](../tutorials/kiro-setup.md) first.
- Node.js and npm. The local PostgreSQL MCP server (MCP Toolbox for Databases) and several other MCP servers launch through `npx`.
- [uv](https://docs.astral.sh/uv/). The AWS MCP servers launch through `uvx`.
- [Docker Desktop](https://www.docker.com/products/docker-desktop/), running. LocalStack needs it. So does a local Postgres container, if you run one for the MCP server to talk to.
- A LocalStack auth token. As of November 7, 2026, the `localstack/localstack` image starts only with one:
  1. Create a LocalStack account. The free Hobby plan covers non-commercial use.
  2. Set `LOCALSTACK_AUTH_TOKEN` in the shell you start LocalStack from. Export it on macOS and Linux, or set `$env:LOCALSTACK_AUTH_TOKEN` in PowerShell.

  Docker Compose reads the token from your shell, not from `.env.local`.
- Python 3.11 or newer. The spec constraint in Phase 2 pins Python 3.13. The starter scaffold runs on 3.11 and up.
- AWS CLI configured with credentials Kiro can use. Check with `aws sts get-caller-identity`.
- Git. Commit before each phase so you can diff what the agent changed.

### AWS Access

You need an account with access to:

- Amazon Bedrock. In commercial Regions, Bedrock enables a model the first time you call it. Your IAM identity needs these AWS Marketplace permissions: `aws-marketplace:Subscribe`, `aws-marketplace:Unsubscribe`, and `aws-marketplace:ViewSubscriptions`. Anthropic models also need a one-time use-case form per account. Before Phase 7, open a Claude model from **Model catalog** in the Bedrock console and submit the form. Otherwise the summarization tasks fail with `AccessDeniedException`.
- Aurora PostgreSQL
- AWS App Runner, if your account already uses it. Otherwise use Amazon ECS Express Mode (see the note at the top)
- Amazon S3
- AWS Secrets Manager

Phases 1 through 6 cost only Kiro credits. Phase 7 onward provisions real AWS resources. Aurora and App Runner bill while they exist, even when idle. Tear them down when you finish (see "Tear Down the AWS Resources" after Phase 8).

### Knowledge

- Basic Python and Flask
- Familiarity with AWS services
- A rough idea of how web scraping works

### Before You Start

Copy the starter out of the repository. This keeps your work separate from the checked-in version:

```bash
# run from chapter-05/ in your clone
cp -r hands-on-lab/daily-briefing-agent ~/daily-briefing-agent
cd ~/daily-briefing-agent
git init && git add . && git commit -m "chore: lab starter"
```

On Windows (PowerShell):

```powershell
# run from chapter-05\ in your clone
Copy-Item -Recurse hands-on-lab\daily-briefing-agent $HOME\daily-briefing-agent
Set-Location $HOME\daily-briefing-agent
git init; git add .; git commit -m "chore: lab starter"
```

Then open the folder in Kiro and trust it:

1. Select File > Open Folder and open the folder.
2. Run **Workspaces: Manage Workspace Trust** from the command palette.
3. Choose **Trust Folder**.
4. Run **Developer: Reload Window**.
5. Check that the Kiro (ghost) icon in the left rail shows SPECS and AGENT HOOKS. Powers have their own panel, the ghost icon with a lightning bolt.

Kiro opens a folder you have not trusted in Restricted Mode, without asking. In Restricted Mode it ignores the starter's steering files and `.kiro/settings/mcp.json`. It does not run hooks. It asks before every command.

If the panels do not show, Kiro has not recognized the folder as a project. Check that `.kiro/` came across with the copy.

## Lab Structure

```text
hands-on-lab/
├── README.md                          # This file
├── daily-briefing-agent/              # Starter project
│   ├── .kiro/
│   │   ├── steering/
│   │   │   ├── product.md             # Product overview and persona
│   │   │   ├── tech.md                # Technology stack and conventions
│   │   │   └── structure.md           # Project structure
│   │   ├── specs/
│   │   │   └── tech-news-aggregator/
│   │   │       ├── requirements.md    # Requirements spec (short: you extend it)
│   │   │       ├── design.md          # Design spec (short: you extend it)
│   │   │       └── tasks.md           # Implementation tasks
│   │   ├── hooks/                     # Pre-1.0 hook format (see Phase 4)
│   │   │   ├── test-coverage.kiro.hook
│   │   │   └── docs-sync.kiro.hook
│   │   └── settings/
│   │       └── mcp.json               # MCP servers, pre-populated
│   ├── src/
│   │   ├── __init__.py
│   │   └── config.py                  # Configuration module (given, not a TODO)
│   ├── tests/
│   │   ├── __init__.py
│   │   └── conftest.py                # Shared pytest fixtures (given)
│   ├── AGENTS.md                      # Agent directives, always included
│   ├── Makefile                       # Development shortcuts
│   ├── pytest.ini                     # Test markers and default options
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Environment template
│   ├── .gitignore
│   └── README.md                      # Project README
├── prompts/                           # The book's lab prompts as paste-ready files
│   ├── vibe_prompt.txt                # Listing 5-2 (Phase 1)
│   ├── design_spec_review.txt         # Listing 5-3 (Phase 2, Step 1)
│   └── Spec_definition.txt            # Listing 5-4 (Phase 2, Step 2)
└── exercises/                         # Practice exercises, with answer keys
    ├── exercise-1-sdd-basics.md
    ├── exercise-2-steering-files.md
    └── exercise-3-hooks-powers.md
```

The three files in `prompts/` match the book's Listings 5-2, 5-3, and 5-4 word for word. The same text appears inline in the phases below. Where a tool change affects a prompt, the note next to it says so.

You and Kiro write everything not listed above during the lab. This includes models, services, repositories, scrapers, the Flask app, and CloudFormation templates.

The starter's specs are short on purpose. After each phase, compare them with [`../daily-briefing-agent/`](../daily-briefing-agent/). It holds the full specs the author's session produced.

## Lab Phases

### Phase 1: Setup and Vibe Exploration (15 minutes)

**Objective**: Set up the project. See what vibe mode does with an underspecified prompt.

#### Step 1: Confirm the project opens

The folder you copied should already register as a Kiro project. To start from an empty folder instead, create one and let Kiro initialize it. The [first-project guide](https://kiro.dev/docs/getting-started/first-project/) covers this.

#### Step 2: Enter the vibe prompt

1. Leave model selection on "Auto". Kiro picks a model based on the prompt.
2. Switch the Autopilot toggle in chat to Supervised. Kiro starts in Autopilot, which applies changes without stopping for per-change review.

Autopilot is separate from tool approval. Kiro still asks before it runs most terminal commands. As of November 7, 2026, the approval prompt offers these choices:

- **Allow**: this run only.
- **Always allow**: saves a rule. To keep the rule for this session only, choose This session under Apply to.
- **Deny**
- **Always deny**

In Kiro Chat, enter this prompt. It is Listing 5-2 in the book, shipped here as [`prompts/vibe_prompt.txt`](prompts/vibe_prompt.txt):

```text
I am planning to develop a web application and need guidance on the initial
steps. My preference is to begin by exploring concepts within this current
working folder, though I intend to transition to a spec-driven development
approach later. The goal is to first establish the web app based on a specific
persona and intent. Once I solidify the core idea, I will transition to a formal
specification mode. This statement represents my overarching goal for the
application. It gives a persona and purpose to my web application: you are a
"Witty Tech Journalist." Your tone is sharp, concise, and slightly cynical. You
prioritize substance over hype. The purpose of this project is to create a news
aggregator that curates and presents tech stories along with witty summaries.
```

**What to watch for**: Vibe mode often creates artifacts on its own, usually draft markdown files. This is expected. Save whatever it produces into a scratch directory. You compare it with your Phase 2 constraints later. [`../daily-briefing-agent-notes/`](../daily-briefing-agent-notes/) shows what the author's session produced.

---

### Phase 2: Spec Definition (30 minutes)

**Objective**: Replace creative exploration with concrete constraints.

#### Create a spec

1. Select the Kiro (ghost) icon in the left rail.
2. In the SPECS section, click **(+)** to create a new spec. When Kiro asks, choose **Feature**, then the **Requirements-First** workflow. This is the gated flow this lab uses.
3. Review the requirements Kiro generates.

Kiro writes `requirements.md` as user stories. The acceptance criteria use EARS (Easy Approach to Requirements Syntax) notation: "WHEN [condition] THE SYSTEM SHALL [behavior]." Check that each criterion has a concrete trigger and an observable result. In Phase 7, the WHEN/SHALL statements drive property-based tests.

In the gated flow, you approve requirements, then design, then tasks. Use the gated flow in this lab. Kiro has other spec modes:

- **Quick Spec** (the book calls it Quick Plan) skips the approval gates.
- **Bugfix Specs** target a reported defect.

**Your job**: Review the requirements and refine them with Kiro. You own the deliverables, not the agent.

#### Step 1: Review initial design specs

Select "Move to Design Phase" in chat. Then ask clarifying questions. This is Listing 5-3 in the book, shipped here as [`prompts/design_spec_review.txt`](prompts/design_spec_review.txt):

```text
Create the architectural diagram using Mermaid in the design document.
Explain how the user and data security are handled. For performance, do we need
to add the cache? Are you using a key-value or JSON-based database? What unit
testing framework and functional testing framework are used?
```

Review the components Kiro proposes, such as ranking engines, story repositories, and web controllers. Check that each one has:

- A clear purpose
- Defined interfaces
- Named methods

#### Step 2: Iterative refinement via conversation

This block is Listing 5-4 in the book, shipped here as [`prompts/Spec_definition.txt`](prompts/Spec_definition.txt):

```text
Constraint: The application must be written in Python 3.13 and use Python libraries like Flask for UI.
Constraint: Use 'requests' and 'beautifulsoup4' for scraping.
Constraint: Scrape headlines from 'news.ycombinator.com.'
Constraint: Output must be saved to a file named 'briefing_YYYY-MM-DD.md'.
Constraint: Use Amazon Bedrock APIs and Claude Sonnet and Haiku's latest models for summarization.
Constraint: Always use CloudFormation for infrastructure as code to deploy on AWS and ensure the templates are valid using Kiro Powers.
Constraint: Deployment of AWS Infra must be in sequence. Write separate tasks for generating testing data if needed. The base template should contain infrastructure components like VPC and networking, DB servers, ECR repositories, and S3 buckets and secrets. The app stack should contain app-related resources that are frequently updated.
Constraint: The application should be able to deploy on serverless cloud services. Use Amazon Lightsail for deploying Flask apps and Aurora Postgres for the database (if needed) and expose UI applications only through CloudFront.
Constraint: Unit Test coverage should be 70%
Constraint: Use Hypothesis library for property-based testing
Instruction: Group tasks in logical groupings; start with MVP, local deployment, and testing. Once local testing is completed, build CloudFormation templates, validate, and deploy to AWS in dependency order. Test infrastructure on AWS at every stage from database to UI.
Requirement: As a functional tester, I want to use the Playwright Test Automation framework to test UI functionality end-to-end using the best testing framework to test the web app in the Chrome browser.
Requirement: Build MVP for story summarization with basic functionality to test end-to-end. In the second phase, we will focus on improving the summarization and adding enhanced features.
Design: For local development, always use a virtual Python environment for isolated dependency management. Docker for deployment.
Design: Create AWS Deployment Architecture. You can use AWS tools to generate diagrams.
```

Notes on this block:

- The Lightsail constraint is the wrong choice on purpose. Phase 8 changes it.
- The Lightsail constraint also disagrees with the starter's shipped `design.md` and `tech.md`. Those files show the App Runner outcome from after Phase 8. This mismatch is intended. Your spec wins until Phase 8 resolves it.
- With the Hypothesis constraint, expect Kiro to generate property-based tests from your EARS acceptance criteria. In Phase 7, check that the WHEN/SHALL wording shows up as test properties.

While you refine:

- **Catch errors early**: If the agent proposes a React frontend when you asked for Python, say so in chat.
- **Let the agent course-correct**: Give feedback in chat. The agent refactors the design document and the planned tasks. Do not edit them by hand.
- **Check components**: purpose, interfaces, key methods.

#### Step 3: Visualize the architecture

Ask Kiro for Mermaid diagrams in `design.md`. They should map the data layer, the external services, and how the components connect.

The book also points to the AWS Diagram MCP Server for image diagrams with AWS icons. AWS has retired that server. Its PyPI releases are yanked and its documentation page is gone. Use Mermaid here, including for the diagram Listing 5-3 asks for.

#### Step 4: Final validation and handoff

Read Kiro's summary of the validated stack: web framework, data storage, and infrastructure. When you agree with the specs, select **Move to implementation plan** to generate the tasks.

---

### Phase 3: Iterative Refinement (20 minutes)

**Objective**: Shape the implementation plan through conversation, before any code exists.

#### Confirm the architecture

Before you move to implementation, check:

- **Web framework**: Flask
- **Data storage**: Aurora PostgreSQL and S3
- **Infrastructure**: whatever the agent settled on. The author's run moved from Lightsail to App Runner at this point.
- **Artifacts**: documentation and UX artifacts such as wireframes and style-guide requirements

#### Ask about gaps

```text
In the implementation plan, do you have the task to design the web interface?
```

#### Add tasks the plan is missing

```text
Write tasks for creating proper documentation in a markdown file using best
practices after each MVP.
```

#### Ask how local development will work

```text
How are you planning to use the PostgreSQL database and other dependencies
in local testing?
```

#### Clean up the plan

```text
Review end-to-end tasks and ensure no duplication.
```

Each prompt changes the plan, not the output. Read the diff in `tasks.md` after each one.

---

### Phase 4: Configure Hooks (15 minutes)

**Objective**: Automate test coverage and documentation.

In Kiro IDE 1.0 and later, the **(+)** opens a chat flow instead of the "Create an agent hook" form the book shows.

1. Click **(+)** in the **AGENT HOOKS** section.
2. Describe the hook in plain English.
3. Answer Kiro's questions about the event and the files it should watch. Kiro saves the result as `.kiro/hooks/<name>.json`.
4. Check that the new hook shows as enabled in the panel.

#### Hook 1: test coverage

| Element | Configuration |
|---------|---------------|
| Hook name | `Auto Test Coverage` |
| Trigger type | `PostFileSave` |
| File patterns | `src/**/*.py` |
| Agent prompt | Analyze the modified file, identify new or changed functions, check test coverage, generate tests for the gaps, run them, update coverage reports |

Use the pattern `src/**/*.py`, not `*.py`. A hook that fires on every Python file in the tree, including tests and scripts, slows the session and wastes credits.

#### Hook 2: documentation sync

The book makes this a Manual Trigger hook. Kiro IDE 1.0 cannot create new manual hooks. For an on-demand workflow, use a steering file with `inclusion: manual` instead. You run it as a slash command:

1. In the Steering section of the Kiro panel, click **(+)** and create a workspace steering file named `docs-sync.md`.
2. Give it this content:

   ```markdown
   ---
   inclusion: manual
   ---

   Review recent source changes and update README.md and the /docs folder to reflect new features, API changes, or usage instructions.
   ```

3. Type `/docs-sync` in chat whenever you want the documentation refreshed.

The starter ships both hooks in `.kiro/hooks/` in the pre-1.0 `.kiro.hook` format. Kiro lists them as legacy hooks.

- The test-coverage hook has an upgrade badge that converts it to the current format.
- The manual docs-sync hook has no 1.0 equivalent. It still runs from the panel's play button.

Build your own versions anyway, for the practice. Then disable or delete the shipped copies in your working copy, so the same hook does not run twice. See [`../code-examples/hooks/`](../code-examples/hooks/) for four more.

---

### Phase 5: Install a Kiro Power (10 minutes)

**Objective**: Add AWS infrastructure capability. The agent can then build and validate CloudFormation and CDK.

1. Open the **POWERS** sidebar in the left rail.
2. Browse to the AWS infrastructure Power.
3. Click **Install**.

Kiro handles the configuration. It loads an installed Power only when the conversation matches the Power's keywords. Section 5.5 covers what a Power bundles.

**Troubleshooting**: If a Power or MCP server fails, paste the terminal error into Kiro Chat and ask Kiro to diagnose it. Kiro can read its own error messages, find a missing dependency, and walk you through the fix. Review what it proposes. Do not hand-edit code or configuration unless it is yours to change, such as an AWS profile setting.

---

### Phase 6: Configure MCP Servers (15 minutes)

**Objective**: Connect the AWS MCP servers.

The chapter's server list is:

1. [AWS API MCP Server](https://awslabs.github.io/mcp/servers/aws-api-mcp-server) (superseded; see the note at the top)
2. [AWS Knowledge MCP Server](https://awslabs.github.io/mcp/servers/aws-knowledge-mcp-server): a remote server at `https://knowledge-mcp.global.api.aws`, with nothing to install
3. [AWS Documentation MCP Server](https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server)
4. [Amazon Aurora Postgres MCP Server](https://awslabs.github.io/mcp/servers/postgres-mcp-server)
5. AWS Diagram MCP Server: retired by AWS. Its PyPI releases are yanked and it has no documentation page. Skip it. Phase 2, Step 3 covers diagrams with Mermaid.

The starter's `.kiro/settings/mcp.json` already declares three servers: AWS Documentation, AWS Knowledge, and a local PostgreSQL server.

1. Install uv. The AWS servers that run locally launch through `uvx`.
2. Add the **AWS API** and **Aurora Postgres** servers through the Kiro MCP menu.

The full catalog is at [awslabs.github.io/mcp](https://awslabs.github.io/mcp).

**Hint**: Ask Kiro to do it. From the MCP menu, use "Ask Kiro": `Add AWS API MCP Server. Use the us-east-1 region.`

**Notes**:

- Most AWS MCP servers need an AWS profile configured in your environment. Check each server's documentation.
- The local PostgreSQL server runs MCP Toolbox for Databases through `npx`. Install Node.js and set the `POSTGRES_*` environment variables. This matches the chapter's Listing 5-1. The reference `mcp/postgres` Docker image is archived.
- Kiro only expands environment variables you have approved. When it warns about `${POSTGRES_PASSWORD}`, add the variable under **Mcp Approved Env Vars** in Kiro settings.

Once the servers are configured, do not paste schemas into chat. Say "query the local database to find the story table structure". Kiro fetches it over MCP.

More configuration examples, including the credentials-free variants: [`../code-examples/mcp-configs/`](../code-examples/mcp-configs/).

---

### Phase 7: Execute Tasks (45+ minutes)

**Objective**: Build the application.

#### Pre-flight checklist

1. **Specs ready**: `tech-news-aggregator` is complete in the SPECS sidebar.
2. **Hooks configured**: Auto Test Coverage and Documentation Sync are enabled in AGENT HOOKS.
3. **Power installed**: the AWS infrastructure Power appears in POWERS.
4. **MCP servers connected**: each server shows a green check in the MCP panel.
5. **Tasks synced**: In `tasks.md`, click **Sync Files** (the book calls this button Update tasks). The task list then matches your latest requirements. Read the "Key Updates Made" summary Kiro posts in chat, including its requirements traceability.

#### Execute

1. Open `tasks.md` in the center pane.
2. Click **Start task** (the power icon) next to a task. Or use **Run all Tasks**. It runs independent tasks in parallel waves, ordered by their dependencies.
3. Review every change before accepting it.

**Group into MVPs.**

- **MVP 1**: Build and test on your local machine.
- **MVP 2**: Build, validate, and deploy the CloudFormation templates to AWS. Use your default profile and name the region explicitly.

You get a working, testable application before any AWS spend.

#### Verify MVP 1 locally

When the local tasks finish, run the app and its tests:

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env.local                        # then edit: region, bucket, model IDs
make test-unit                                    # or: pytest -m unit -v
make run                                          # or: python run_dev_server.py
```

On Windows (PowerShell), `make` is usually not installed. Run the commands the targets wrap:

```powershell
python3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env.local                 # then edit: region, bucket, model IDs
pytest -m unit -v
python run_dev_server.py
```

Open `http://localhost:5000`. Check that you see:

- The Witty Tech Journalist masthead
- A list of story cards, each with a generated summary

Check that a `briefing_YYYY-MM-DD.md` file appears.

About the `Makefile` targets:

- `run`, `localstack`, and `docker-build` call files the lab has not created yet, such as `run_dev_server.py`, `docker-compose.localstack.yml`, and `Dockerfile`. They work once the matching tasks complete.
- `make lint` and `make format` work as soon as dependencies are installed.
- `make test` and `make test-unit` report `no tests ran` and exit with an error (pytest exit code 5) until Kiro writes the first test file. This is expected on the bare starter.

#### Iterate on what you get

If stories come back without summaries, or the UI is wrong, fix the spec, not the code:

```text
Some of the stories did not generate summaries. Can we fix the design or
tasks to address this?
```

Expect the agent to add retry logic and verify again. If the outcome is still wrong, create substories or new user stories. Do not widen the scope of an existing story.

For non-functional gaps, run validation explicitly. Before deployment, ask Kiro to:

1. Validate the CloudFormation templates with `cfn-lint` and `cfn-guard`.
2. Fix any security compliance findings in both the base and app stacks.

---

### Phase 8: Iterative Improvements (20 minutes)

**Objective**: Change an architectural decision after implementation has started. Update the specs, not the templates.

Phase 2 pinned Lightsail. Suppose that turns out to be wrong. Do not edit the templates. Enter this prompt:

```text
Lightsail service won't work for this use case due to multiple constraints. We
also don't need Cloudfront now. I want you to change the requirements, design,
and tasks to deploy the Flask app to AppRunner with the proper IAM policy setup
for service-to-service access. I also want you to update the design document
along with the AWS diagram to reflect the change.
```

If your account is new to App Runner, name Amazon ECS Express Mode instead of AppRunner (see the App Runner note at the top).

Read the diff on all three spec artifacts. You can make this kind of update at the start of a phase or mid-implementation. Describe the change clearly.

#### Prepare the repository

Before committing, ask Kiro to clean up after itself:

```text
The following tasks are necessary for code repository maintenance and
preparation:

1. Code repository cleanup: Address the redundancy and presence of temporary py
   and sh files by reviewing and cleaning up the code repository. This task may
   require a large context model for thoroughness and to ensure system
   functionality is preserved.
2. Documentation update: Following the code cleanup, the documentation must be
   updated and thoroughly maintained to ensure it is current. This task also
   necessitates a foundation model with a large context window.
3. Code base review and pre-commit preparation: The final step involves a
   complete review of the code base to prepare it for Git commit. During this
   review, it is critical to ensure that sensitive data, including environment
   properties, AWS account names, credentials, personal names, email addresses,
   and any other PII, is either obscured or added to the .gitignore file.
```

Then commit `.kiro/` with the code. A fresh clone then carries the same specs, steering, hooks, and MCP config. Review future changes under `.kiro/` in pull requests like any other code.

---

## Tear Down the AWS Resources

Everything Phase 7+ provisioned keeps billing while it exists. Aurora Serverless and App Runner cost money even when idle. Expect tens of dollars a month between them, more if you sized up. Tear down as soon as you finish.

Kiro wrote the templates, so ask Kiro to run the teardown:

```text
Generate and run the teardown for everything this project deployed. Delete the
app stack before the base stack, and tell me about anything CloudFormation
cannot delete on its own.
```

Whether Kiro runs it or you do, follow this checklist:

1. **Delete the app stack first, then the base stack.** The app stack (App Runner service, app-level IAM roles) depends on the base stack (VPC, Aurora, ECR, S3, secrets). Deleting in the wrong order fails on dependencies.
2. **Empty the S3 briefings bucket before its stack deletes.** CloudFormation does not delete a non-empty bucket. The stack delete fails and rolls back.
3. **Check that the Aurora cluster is gone.** It is the biggest line item. If deletion protection was enabled, disable it first.
4. **Expect Secrets Manager secrets to remain for a while.** Deletion is scheduled (7 to 30 days), not immediate. This is normal. They cost almost nothing in that window.
5. **Delete any images pushed to ECR** if the repository was retained.

Check that nothing is left:

```bash
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE DELETE_FAILED
```

An empty result for this project's stacks means you are done. A `DELETE_FAILED` stack almost always means a non-empty bucket or a dependency order problem. Fix the cause and retry the delete. As a final check, look at the Billing console a day later.

---

## Expected Outputs

On completion you should have:

1. **A working Flask application**, running locally on port 5000
2. **Steering files**: `product.md`, `tech.md`, `structure.md`, extended from the starter versions
3. **Spec documents**: requirements, design, and tasks in `.kiro/specs/tech-news-aggregator/`
4. **Configured hooks**: auto test coverage and documentation sync, both enabled
5. **CloudFormation templates**: a base stack and an app stack, both passing `cfn-lint`
6. **Daily briefings**: markdown files named `briefing_YYYY-MM-DD.md`
7. **Tests passing** at 70% coverage or better, including property-based tests derived from your EARS criteria

## Troubleshooting

| Issue | What to check |
|-------|---------------|
| MCP server will not connect | The folder is trusted (in Restricted Mode Kiro does not read `.kiro/settings/mcp.json`). AWS credentials and region are set. For the PostgreSQL server, Node.js is installed and the `POSTGRES_*` environment variables are set |
| An AWS MCP server fails with `uvx: command not found` | Install uv, then restart Kiro so it picks up the new PATH |
| Kiro warns about an environment variable in `mcp.json` | Approve it under **Mcp Approved Env Vars** in Kiro settings |
| Bedrock returns AccessDenied | The one-time Anthropic use-case form was submitted for this account. Your IAM identity had the `aws-marketplace` permissions on the first call. The model is offered in your Region |
| Bedrock returns ValidationException on the model ID | The ID is a bare or retired model ID. InvokeModel and Converse need an inference profile ID such as `global.anthropic.claude-haiku-5-5`. Each model's card under "Models at a glance" in the Bedrock docs lists the valid IDs |
| Bedrock returns ValidationException with a valid inference profile ID | The request sets `temperature`, `top_p`, or `top_k`. Current Claude models accept only the default sampling settings. Remove those parameters from the request and from the steering |
| LocalStack exits at startup, or Compose reports LOCALSTACK_AUTH_TOKEN missing | `LOCALSTACK_AUTH_TOKEN` is set in your shell. Docker Desktop is running. Port 4566 is free |
| Tests fail on import | You installed into the virtual environment. You are running from the project root |
| `make run` fails with a missing file | The task that creates `run_dev_server.py` has not completed yet |
| A hook fires constantly | The file filter is too broad. In a `.kiro/hooks/<name>.json` hook, narrow `matcher`, a regular expression on the file path, such as `src/.*\.py$` (in the JSON file: `"src/.*\\.py$"`). In a legacy `.kiro.hook` file, narrow the glob in `patterns` to `src/**/*.py` |

### Getting Help

- Paste the error into Kiro Chat and ask Kiro to diagnose it. This is usually the fastest route.
- Kiro documentation: [kiro.dev/docs](https://kiro.dev/docs/)
- AWS MCP server documentation: [awslabs.github.io/mcp](https://awslabs.github.io/mcp)

## Next Steps

1. Do the four end-of-chapter exercises in [`../challenge-lab/`](../challenge-lab/):
   - Swap App Runner for ECS through the requirements.
   - Change the persona and measure the blast radius.
   - Build a pre-commit security scanner.
   - Generate domain steering.
2. Diff your specs against the author's reference set in [`../daily-briefing-agent/`](../daily-briefing-agent/).
3. Tear down the AWS resources you provisioned, following "Tear Down the AWS Resources" above.

## Time Estimate

| Phase | Duration |
|-------|----------|
| 1. Setup and vibe exploration | 15 minutes |
| 2. Spec definition | 30 minutes |
| 3. Iterative refinement | 20 minutes |
| 4. Configure hooks | 15 minutes |
| 5. Install a Power | 10 minutes |
| 6. Configure MCP servers | 15 minutes |
| 7. Execute tasks | 45+ minutes |
| 8. Iterative improvements | 20 minutes |
| **Total** | **~2.5 to 3 hours** |

Phase 7 takes the longest. Its time depends on the model, your AWS setup, and how many times you iterate.
