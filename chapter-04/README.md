# Chapter 4: Recent Advances in AI and Autonomous Agents

This directory holds the configuration files for Chapter 4:

- MCP and A2A protocol configurations
- AGENTS.md templates
- a rules file
- invocation patterns
- the governance configuration for the AGILITY framework

## What's here and what you do

- **`code-examples/`** holds the chapter's listings as working files. Most also have a longer extended version, where the book trimmed for space. Copy them into your own project and edit them.
- **`tutorials/`** has one quick-reference setup guide per protocol or standard.
- **`exercises/`** gives you a scenario to build the artifact yourself. Each one has hints and a solution.

Most of this directory is configuration. You do not need to install or run anything. Four Python files run standalone. They demonstrate patterns and are not SDK integrations (see [Running the Python examples](#running-the-python-examples)).

## What you will be able to do

After the chapter and these exercises, you can:

- Recognize the shift from AI-assisted coding ("vibe coding") to autonomous agent systems.
- Describe what the 2025 announcements from AWS, Google, and OpenAI changed.
- Explain the goals of the main standardization efforts (AAIF, MCP, A2A).
- Compare agentic IDE designs, including Amazon Kiro, Google Antigravity, and Cursor.
- Configure agent behavior with an AGENTS.md file and an Agent Card (agent-card.json).
- Apply the AGILITY framework to an agent design.

## Directory structure

```text
chapter-04/
├── README.md                          # This file
├── code-examples/
│   ├── mcp-config/                    # Model Context Protocol configuration
│   │   ├── basic_config.json          # Listing 4-1
│   │   ├── enterprise_config.json     # Extended: adds permissions, rate limits, monitoring
│   │   └── README.md
│   ├── a2a-protocol/                  # Agent-to-Agent protocol
│   │   ├── agent-card.json            # Listing 4-2 (spec-conformant Agent Card)
│   │   ├── agent_manifest_governance.json  # Extended: governance ideas beyond the spec
│   │   ├── discovery.json             # Extended: registry and direct discovery config
│   │   └── README.md
│   ├── agents-md/                     # AGENTS.md templates
│   │   ├── AGENTS.md                  # Listing 4-6 (backend service)
│   │   ├── AGENTS_enterprise.md       # Listing 4-3 (Nexus Inventory System)
│   │   └── README.md
│   ├── rules-files/                   # Rules and steering mechanisms
│   │   ├── steering-code-quality.md   # Listing 4-4 (Kiro steering file, full version)
│   │   └── README.md
│   ├── invocation-patterns/           # How the runtime calls an agent
│   │   ├── sync_invocation.py         # Listing 4-7
│   │   ├── model_router.py            # Listing 4-5, extended with a policy-driven router
│   │   ├── handoff_pattern.py         # Extended: agent-to-agent delegation
│   │   ├── tool_using_invocation.py   # Worked solution to Exercise 4.2
│   │   └── README.md
│   └── governance/                    # AGILITY framework
│       ├── agility_config.json        # Governance configuration, one block per pillar
│       ├── ai_robots.txt              # Agent access control (the Limitations pillar)
│       ├── decision_log_schema.json   # Schema for the decision log (the Governance pillar)
│       └── README.md
├── tutorials/
│   ├── mcp-setup.md
│   ├── a2a-integration.md
│   ├── agents-md-guide.md
│   └── governance-guide.md
└── exercises/
    ├── README.md
    ├── exercise-1-mcp-config.md
    ├── exercise-2-agent-card.md
    └── exercise-3-agents-md.md
```

## Prerequisites

- Comfort reading JSON, YAML, and Markdown. That covers most of this directory.
- Git.
- Python 3.11 or later, only if you want to run the four Python examples.
- An agentic tool to try the configurations against. Any of the Part II tools works; you do not need one to complete the exercises.

## Which book section maps to which files

| Section | Topic | Files |
|---|---|---|
| 4.1 | The agentic turn: market evolution (2023-2025) | Conceptual |
| 4.2 | Standardization: AAIF, MCP, A2A, AGENTS.md, rules files, the agentic IDE landscape | `code-examples/mcp-config/`, `code-examples/a2a-protocol/`, `code-examples/agents-md/`, `code-examples/rules-files/` |
| 4.3 | Foundation models powering agentic systems | `code-examples/invocation-patterns/model_router.py` |
| 4.4 | Governance and responsible AI frameworks (AGILITY) | `code-examples/governance/`, `tutorials/governance-guide.md` |
| 4.5 | Key concepts in practice (AGENTS.md, invocation patterns) | `code-examples/agents-md/`, `code-examples/invocation-patterns/` |
| 4.6 | Looking ahead: marketplaces, swarms, role shifts | Conceptual; the swarm work is in [chapter-10](../chapter-10/) |

## Listings in this directory

| Listing | Book title | File |
|---|---|---|
| 4-1 | mcp_basic_config.json | [`code-examples/mcp-config/basic_config.json`](./code-examples/mcp-config/basic_config.json) |
| 4-2 | agent-card.json | [`code-examples/a2a-protocol/agent-card.json`](./code-examples/a2a-protocol/agent-card.json) |
| 4-3 | sample_AGENTS.md | [`code-examples/agents-md/AGENTS_enterprise.md`](./code-examples/agents-md/AGENTS_enterprise.md) |
| 4-4 | .kiro/steering/code-quality.md | [`code-examples/rules-files/steering-code-quality.md`](./code-examples/rules-files/steering-code-quality.md) |
| 4-5 | simple_model_router.py | [`code-examples/invocation-patterns/model_router.py`](./code-examples/invocation-patterns/model_router.py) |
| 4-6 | AGENTS.md for a backend service | [`code-examples/agents-md/AGENTS.md`](./code-examples/agents-md/AGENTS.md) |
| 4-7 | Synchronous agent invocation with a coding persona | [`code-examples/invocation-patterns/sync_invocation.py`](./code-examples/invocation-patterns/sync_invocation.py) |

These files are extended examples written for this repo:

- `enterprise_config.json`
- `agent_manifest_governance.json`
- `discovery.json`
- `handoff_pattern.py`
- everything under `governance/`

The book shows the minimum version. These files show the same patterns at production scale. `tool_using_invocation.py` is a worked solution to the book's Exercise 4.2.

### Where the files differ from the printed listings

The listing files match the book. Note these differences:

- **Listing 4-3 (`AGENTS_enterprise.md`)**: the book's sections in the same order, extended with an architecture diagram, a type-safety example, commands, environment variables, and a review checklist.
- **Listing 4-5 (`model_router.py`)**: `route_task` is the listing unchanged. Its keyword match is case-sensitive. The demo lowercases each task description before it calls `route_task`. In your own router, normalize case inside the function.
- **Cursor rules format (Section 4.2)**: current Cursor documentation uses project rules in `.cursor/rules/` (`.mdc` files with YAML front matter) plus `AGENTS.md`. The older single-file `.cursorrules` is legacy. [`code-examples/rules-files/`](./code-examples/rules-files/) follows the current format.

## Go further with MCP and A2A

These capabilities build on the Chapter 4 protocols. Plans, pricing, and availability change. Each item links to the vendor page with current details.

- **Skills over MCP.** An MCP server can publish Agent Skills (the same `SKILL.md` skill folders). A client lists, reads, and verifies them over MCP. One set of skills then serves many repositories, with no copy in each. It is an opt-in extension. It stays off until both client and server enable it. Client support varies, so check the extension page before you depend on it. Introduced in MCP TypeScript SDK 2.4.0 (October 2026). [Skills over MCP](https://modelcontextprotocol.io/extensions/skills/overview)
- **A2A CLI.** The A2A project's official `a2a` command fetches an Agent Card (`a2a card get <url>`). It also sends a message to an agent (`a2a send -a <url> "..."`, with `--stream` for live updates). Use it to test the Agent Card from Exercise 2 against a real A2A server, or to call an agent from a CI job. It speaks A2A Protocol v1.0. Install it with Homebrew, WinGet, or Go. Introduced in October 2026. [Introducing the A2A CLI](https://github.com/a2aproject/A2A/blob/main/docs/blog/posts/introducing-a2a-cli.md)

## Running the Python examples

All four run with no dependencies beyond the standard library:

```bash
cd code-examples/invocation-patterns
python3 sync_invocation.py
python3 model_router.py
python3 handoff_pattern.py
python3 tool_using_invocation.py
```

Each prints a walkthrough of its pattern and exits with status 0. [`code-examples/invocation-patterns/README.md`](./code-examples/invocation-patterns/README.md) lists what each one prints. That includes the expected `AGENTS.md not found` warning from `sync_invocation.py`. On Windows, use `py` in place of `python` if `python` is not on your PATH.

What each file does:

- `sync_invocation.py` defines its own `Agent` class. It does not import a vendor SDK.
- `model_router.py` routes by capability tier (reasoning, balanced, fast), not by pinned model name. Section 4.3 explains why. The cost and latency figures in its catalog are placeholders. Replace them with published numbers for the models you bind each tier to.
- `handoff_pattern.py` simulates the model's transfer decision with keyword matching. In a real system, the model makes that call. Chapter 10 builds a coordinated agent team.
- `tool_using_invocation.py` is a worked solution to the book's Exercise 4.2. It parses the Commands section of AGENTS.md and generates tests. Then it calls a simulated `run_tests()` tool. It returns one result object with both the tests and the test output.

## Tutorials

| Tutorial | What you build | Time |
|---|---|---|
| [MCP Setup](./tutorials/mcp-setup.md) | An MCP configuration with filesystem, GitHub, database, and Slack servers | 20-30 min |
| [A2A Integration](./tutorials/a2a-integration.md) | A spec Agent Card, then an extended manifest | 25-35 min |
| [AGENTS.md Guide](./tutorials/agents-md-guide.md) | An AGENTS.md for your own project | 20-30 min |
| [Governance Guide](./tutorials/governance-guide.md) | AGILITY controls, from accountability through the update pipeline | 25-35 min |

## Exercises

| Exercise | Scenario | Time |
|---|---|---|
| [Exercise 1](./exercises/exercise-1-mcp-config.md) | Configure MCP for a team needing GitHub, PostgreSQL, Slack, and file access | 30-45 min |
| [Exercise 2](./exercises/exercise-2-agent-card.md) | Write the Agent Card for a security review agent | 35-45 min |
| [Exercise 3](./exercises/exercise-3-agents-md.md) | Write AGENTS.md for an order management system (this is Exercise 4.1 in the book) | 30-40 min |

The repo numbers its exercises on its own. [exercises/README.md](./exercises/README.md) maps them to the book's exercises (Exercise 4.1, Exercise 4.2, and the end-of-chapter Chapter Exercises).

## Key terms

| Term | Meaning |
|------|---------|
| MCP (Model Context Protocol) | The standard for connecting an agent to a tool or data source |
| A2A (Agent-to-Agent) | The protocol for discovery, handshake, and task delegation between agents |
| AGENTS.md | The file that tells any coding agent how to work in your repository |
| Rules files | Narrower, tool-specific rules. A Markdown rule only guides the model. Blocking takes a hook or a CI check (see `code-examples/rules-files/`). |
| AGILITY | Accountability, Governance, Integrity, Limitations, Intervention, Transparency, Youth (continuous learning and update) |

The concepts behind each term: Chapter 4, Section 4.2 and Section 4.4.

## Related chapters

- **[Chapter 2](../chapter-02/)**: the zoned governance model that AGILITY builds on.
- **[Chapter 5](../chapter-05/)**: Amazon Kiro, spec-driven development, and steering files.
- **[Chapter 6](../chapter-06/)**: Google Antigravity and the Antigravity CLI.
- **[Chapter 7](../chapter-07/)**: Cursor and GitHub Copilot in agent mode, including `.cursor/rules`.
- **[Chapter 8](../chapter-08/)**: Claude Code, CLAUDE.md, and MCP in depth.
- **[Chapter 10](../chapter-10/)**: multi-agent coordination with a running agent team.
- **[Chapter 12](../chapter-12/)**: AGILITY as executable tests and guardrails, plus no-go zones.

---

Start with the [MCP Setup Tutorial](./tutorials/mcp-setup.md). Or open the [code examples](./code-examples/) directly.
