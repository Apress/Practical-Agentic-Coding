# Case Study: ZenithStays Revenue Management System

A worked example application, built with the agentic workflows this book teaches.

- It is not a lab. There are no TODOs to fill in and no tests to make pass.
- No chapter walks through it or prints its code.
- Read it alongside Chapter 13. It is a real agent-produced codebase, stopped partway through its build. Its design trail sits next to the code.

**What the system is.** ZenithStays is a hotel revenue management system. As designed, it has:

- a dashboard for occupancy and revenue analytics
- an interactive rate calendar
- integrations with property management systems and online travel agents
- an AI assistant that proposes pricing actions for a human to approve

This repository publishes three parts:

- the design trail
- a backend API that runs on mock data
- two agent action-group handlers

Look at the structure more than the domain. The design is specification-first. It maps one architecture onto two cloud providers, with a multi-agent backend.

## How it maps to Chapter 13

Chapter 13 does not mention ZenithStays. The mapping below is ours. Use it to find each Chapter 13 idea in this code. The ideas themselves are explained in the book.

| Chapter 13 section | Where to look here | What you find |
|--------------------|--------------------|---------------|
| Section 13.3, Case Study 1 (institutional memory) | `design/` | The specs, architecture documents, and style guide the agents worked from. They are in the same repository as the code, and they were written before the implementation. |
| Section 13.4, Case Study 2 (single agent to coordinated fleet) | `design/aws/agentic_architecture.md` | A Supervisor agent that triages requests and three specialists it delegates to: Strategy, Market Intelligence, and Execution (Chapter 10 patterns). These are agents inside the product. They are not coding agents. The code implements only part of this design (see `backend/` below). |
| Section 13.6, Case Study 4 (governance) | `design/frontend_agent_ux.md` and `design/mocks/agent_ux_mocks.html` | Agent recommendations shown as proposals with explicit approve or dismiss actions. The agent recommends, and the human decides. In the published backend, the approval endpoint is still a stub. It returns success without calling the Execution agent. |
| Section 13.8 (traceability) | `backend/server.js` and `backend/src/schemas/` | Every request is logged with its trace ID. Each agent action group has an OpenAPI contract. The specification is further along than the code. |

Read the chapter first. This directory illustrates it. It does not replace it.

## What is in here

Everything sits under `code/`:

```text
casestudy/revenuemgmtsystem/code/
├── design/       # Specifications, architecture, UX, and style guide
└── backend/      # Node.js/Express API on mock data and agent handlers
```

### `design/`

The specification and architecture trail that the implementation was generated from. Read these in order:

1. `backend_spec_v2.md`: data model, API surface, compute strategy.
2. `cloud_comparison_strategy.md`: the same logical architecture mapped onto AWS and GCP services.
3. `aws/agentic_architecture.md`: the multi-agent design. It shows which agent owns which decision and which tools each one can reach.

The other files:

- `aws/implementation_guide.md` and `gcp/implementation_guide.md` are the deployment plans. They describe infrastructure code and files that this repository does not include (the CDK and Terraform projects, a backend Dockerfile). Read them as plans. They are not runbooks.
- `frontend_agent_ux.md` and `phase_2_ui_implementation.md` cover how agent output reaches the interface.
- `mocks/agent_ux_mocks.html` is a static mock of that interface. Open it in a browser. It loads Tailwind, the Inter font, and Lucide icons from public CDNs.
- `style_guide.md` and `theme.js` are the design system.

The documents date from December 2025 and are not kept current. Some model IDs, prices, and service details differ from what the providers offer today. Each affected document says so in a note at the top.

### `backend/`

A Node.js and Express API. It has:

- controllers and routes per domain: properties, dashboard, settings, chat, integrations, users
- a mock data service
- a Bedrock agent service

Two files to read:

- `src/services/cloud/` sketches the adapter pattern. A `StorageInterface` has AWS and GCP providers behind a `CloudFactory`. This is how the same codebase would target either provider. The providers are stubs that log the call and return a URL. Nothing in the server calls the factory yet.
- `src/controllers/dashboardController.js` asks the Strategy agent for the dashboard insight. If no agent is configured or the call fails, it falls back to mock data. The API runs without cloud credentials. Every other endpoint serves mock data.

`src/lambdas/agents/` holds the Bedrock action-group handlers. `src/schemas/*_agent.json` holds their OpenAPI contracts. Only two of the four designed agents are built:

- `strategy/index.py` with `strategy_agent.json`. It records pricing insights to DynamoDB.
- `execution/index.py` with `execution_agent.json`. It accepts rate and promotion changes. Its PMS or database write is still commented out, so it logs the request and returns a transaction ID.

The Supervisor and Market Intelligence agents exist in the design document only.

**A bug fixed after generation.** As generated, both handlers read the request body as a map keyed by property name. Bedrock sends `properties` as a list of name, type, and value objects. The handlers answered a real agent with HTTP 500. A check against the event shape in the Amazon Bedrock documentation caught the bug. The published handlers build the map from the list. For what this example shows about verification: Chapter 13, Section 13.2.

## Running it

The backend runs standalone on mock data, with no cloud account. It needs Node.js 22.12 or later:

```bash
cd code/backend
npm ci
node server.js
```

It listens on port 3001.

1. Open `http://localhost:3001/health`.
2. Open `http://localhost:3001/api/dashboard/stats`.
3. Without `STRATEGY_AGENT_ID`, the insight endpoint (`/api/dashboard/insight`) logs that it is falling back to mock data.

[`code/backend/README.md`](code/backend/README.md) covers:

- configuration (`.env.example`)
- verification requests
- Windows variants
- common failures

To wire a real agent, set `STRATEGY_AGENT_ID`, `AWS_REGION`, and AWS credentials.

> **Service change (as of November 7, 2026).** Since July 30, 2026, Amazon Bedrock Agents (now Bedrock Agents Classic) has been closed to new customers. The real-agent path only works in an AWS account that used Bedrock Agents in the previous 12 months. AWS directs new agent work to Amazon Bedrock AgentCore.

## A note on scope

This is a snapshot of one build. It is not a maintained product. Dependency versions, cloud service names, and tool details go out of date. Read it as you would a colleague's project. Study the decisions and the structure. Do not deploy it as a template.
