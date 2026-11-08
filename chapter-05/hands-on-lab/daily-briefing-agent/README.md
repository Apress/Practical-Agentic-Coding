# Daily Briefing Agent (Lab Starter)

**Reference**: Chapter 5, Section 5.7

This is the starter project for the Chapter 5 hands-on lab. It is a scaffold. You and Kiro write the application during the lab. This folder ships:

- The `.kiro/` configuration Kiro reads
- A few files that are tedious to generate and easy to get wrong

The target is a tech news aggregator with a "Witty Tech Journalist" persona. It collects stories from Hacker News. It presents them with sharp, concise, slightly cynical summaries that prioritize substance over hype.

**Start with the lab walkthrough**: [`../README.md`](../README.md).

## What Ships Here

| Path | What it is |
|------|-----------|
| `.kiro/steering/product.md` | Product vision, persona, target users. `inclusion: always` |
| `.kiro/steering/tech.md` | Stack, conventions, AWS services, coverage rules. `inclusion: always` |
| `.kiro/steering/structure.md` | Directory layout, import order, anti-patterns |
| `.kiro/specs/tech-news-aggregator/requirements.md` | Starter requirements. Short on purpose. You extend them in Phase 2 |
| `.kiro/specs/tech-news-aggregator/design.md` | Starter design. Short on purpose. You extend it in Phase 2 |
| `.kiro/specs/tech-news-aggregator/tasks.md` | Starter task list |
| `.kiro/hooks/test-coverage.kiro.hook` | File-save hook (`PostFileSave` in the book) that keeps tests in step with source. Pre-1.0 hook format. Kiro 1.0 and later lists it as a legacy hook with an upgrade badge |
| `.kiro/hooks/docs-sync.kiro.hook` | Manual-trigger hook that refreshes documentation. Pre-1.0 format. Kiro 1.0 and later still runs it as a legacy hook, but cannot create new manual hooks. The lab's Phase 4 shows the replacement |
| `.kiro/settings/mcp.json` | MCP servers: AWS Documentation (runs through `uvx`), AWS Knowledge (remote, by URL), local PostgreSQL (runs through `npx`) |
| `AGENTS.md` | Agent directives. Always included, regardless of inclusion mode |
| `src/config.py` | Configuration module. Given, not a TODO. It is the single source of truth for settings |
| `tests/conftest.py` | Shared pytest fixtures |
| `pytest.ini` | Test markers (`unit`, `integration`, `property`, `browser`, `slow`) and default options |
| `requirements.txt` | Python dependencies for the finished application |
| `Makefile` | Development shortcuts |
| `.env.example` | Environment template. Copy to `.env.local` and edit |

## What You Build

You build everything else during the lab:

- `src/models/`, `src/services/`, `src/repositories/`, `src/scrapers/`, `src/web/`
- The tests that go with them
- The CloudFormation templates
- The Dockerfile
- The LocalStack compose file

If a `Makefile` target fails on a missing file, the task that creates the file has not run yet.

## Getting Started

### Prerequisites

- [Kiro](https://kiro.dev/docs/getting-started/installation/), installed and authenticated
- Python 3.11 or newer. The spec constraint in Phase 2 pins Python 3.13. The scaffold runs on 3.11 and up
- Node.js and npm. The local PostgreSQL MCP server in `.kiro/settings/mcp.json` runs through `npx`
- [uv](https://docs.astral.sh/uv/). The AWS Documentation MCP server runs through `uvx`
- Docker Desktop, running. LocalStack needs it. So does a local Postgres container, if you run one for the MCP server to talk to
- AWS CLI configured, for the deployment phases. Check with `aws sts get-caller-identity`

### Copy this out of the repository first

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

Work in the copy. Your generated code stays out of the book's repository, and you can diff each phase against a clean baseline.

### Open in Kiro

1. Select File > Open Folder, then select your copy.
2. Run **Workspaces: Manage Workspace Trust**.
3. Choose **Trust Folder**.
4. Run **Developer: Reload Window**.
5. Check that the Kiro (ghost) icon in the left rail shows SPECS and AGENT HOOKS. Powers have their own panel, the ghost icon with a lightning bolt.

Kiro opens a folder you have not trusted in Restricted Mode. In Restricted Mode it skips `.kiro/steering/`, `.kiro/settings/mcp.json`, and the hooks.

If the panels do not show, `.kiro/` did not come across with the copy.

### Then follow the lab

1. **Read the steering files.** Kiro reads `product.md`, `tech.md`, and `structure.md` before every response.
2. **Work the specs.** Open the SPECS panel. Review `tech-news-aggregator`. Extend it with the constraints from Phase 2 of the lab.
3. **Enable the hooks.** Both shipped hooks are in `.kiro/hooks/`, in the pre-1.0 format. In Phase 4 you build them yourself. Kiro 1.0 writes yours as `.kiro/hooks/<name>.json`. Afterwards, compare the trigger, file pattern, and prompt with these. Then disable the shipped copies, so a hook does not run twice.
4. **Execute tasks.** Open `tasks.md` and use "Start task" or "Run all Tasks".

The full eight-phase walkthrough is in [`../README.md`](../README.md).

## Local Development

Once the MVP 1 tasks complete:

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env.local                        # then edit region, bucket, model IDs
make test-unit                                    # or: pytest -m unit -v
make run                                          # once run_dev_server.py exists
```

On Windows (PowerShell), where `make` is usually not installed:

```powershell
python3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env.local                 # then edit region, bucket, model IDs
pytest -m unit -v
python run_dev_server.py                          # once it exists
```

To check the scaffold before any lab code exists, check that the configuration module loads your `.env.local`:

```bash
python -c "from src.config import get_config; c = get_config(); print(c.ENV, c.AWS_REGION, c.BEDROCK_MODEL_ID)"
```

With the shipped `.env.example` copied unchanged, that prints `development us-east-1 global.anthropic.claude-haiku-5-5`.

The app serves on `http://localhost:5000` and writes briefings as `briefing_YYYY-MM-DD.md`.

### Make Targets

| Target | What it does | Available |
|--------|--------------|-----------|
| `make install` | Install dependencies | Immediately |
| `make dev` | Install dev tooling and the Playwright Chromium build | Immediately |
| `make test` | Run the whole suite | Once tests exist (until then pytest reports `no tests ran` and exits with code 5) |
| `make test-unit` | Fast tests with mocked AWS | Once tests exist |
| `make test-integration` | LocalStack-backed tests | Once the LocalStack compose file exists |
| `make test-coverage` | Coverage report into `htmlcov/` | Once tests exist |
| `make lint` / `make format` | flake8 and mypy / black and isort | Immediately |
| `make run` | Development server | Once `run_dev_server.py` exists |
| `make localstack` | Start LocalStack | Once `docker-compose.localstack.yml` exists |
| `make clean` | Remove caches, coverage, local DBs, generated briefings | Immediately |

## Configuration

`src/config.py` is the single source of truth. Precedence, highest first:

1. System environment
2. `.env` files
3. The defaults in the `Config` class

Read settings through `get_config()`. Do not call `os.getenv` from application code.

### Bedrock model IDs

`BEDROCK_MODEL_ID` and `BEDROCK_FALLBACK_MODEL_ID` are environment variables on purpose. Bedrock's Claude lineup changes. The identifier also depends on which Bedrock API you invoke.

- The shipped defaults are global inference profile IDs for the current Haiku and Sonnet tiers: `global.anthropic.claude-haiku-5-5`, with `global.anthropic.claude-sonnet-5-5` as the fallback. The bedrock-runtime InvokeModel and Converse APIs expect this form for current Claude models.
- A global profile may route a request to any Region. To keep requests in one geography, use a geo profile such as `us.anthropic.claude-haiku-5-5`.
- Each model's card under [Models at a glance](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html) in the Bedrock User Guide lists the valid IDs.

Bedrock enables a model the first time you call it. Anthropic models first need a one-time use-case form for your AWS account. Open a Claude model from **Model catalog** in the Bedrock console and submit the form. Until then, calls return `AccessDeniedException`.

When you deploy, the App Runner role needs `bedrock:InvokeModel` on the inference profile and on the foundation models. The starter's `design.md` IAM policy shows both resources.

## Target Architecture

- **Backend**: Python with Flask
- **Database**: Aurora PostgreSQL, with SQLite for local development and LocalStack for integration tests
- **AI**: Amazon Bedrock with a Claude model for summaries
- **Storage**: Amazon S3 for briefing files
- **Deployment**: AWS App Runner with a VPC connector
- **Testing**: pytest, Hypothesis for property-based tests, Playwright for browser tests

This list shows where the lab ends up. The book's Phase 2 constraint pins Amazon Lightsail + CloudFront on purpose. Phase 8 then switches to App Runner through the specs. Until Phase 8, the shipped spec files disagree with your in-progress spec. This mismatch is intended.

### AWS Services

| Service | Purpose |
|---------|---------|
| App Runner | Container deployment |
| Aurora PostgreSQL | Data storage |
| Amazon Bedrock | Summary generation |
| S3 | Briefing storage |
| Secrets Manager | Database credentials |
| CloudWatch | Monitoring |

Phases 1 through 6 cost only Kiro credits. From Phase 7 onward you provision real resources. Tear them down when you finish.

## Related

- Lab walkthrough: [`../README.md`](../README.md)
- Practice exercises: [`../exercises/`](../exercises/)
- End-of-chapter challenges: [`../../challenge-lab/`](../../challenge-lab/)
- The author's reference specs, for comparison: [`../../daily-briefing-agent/`](../../daily-briefing-agent/)
- Chapter overview: [`../../README.md`](../../README.md)
- Kiro documentation: [kiro.dev/docs](https://kiro.dev/docs/)
- AWS MCP servers: [awslabs.github.io/mcp](https://awslabs.github.io/mcp)

## License

Part of the companion materials for *Practical Agentic Coding* (Apress). See `LICENSE.txt` at the repository root.
