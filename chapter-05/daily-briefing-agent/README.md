# Reference Artifacts: Tech News Aggregator

**This is not the lab starter.** The starter you build in is [`../hands-on-lab/daily-briefing-agent/`](../hands-on-lab/daily-briefing-agent/). This directory is a read-only reference: the `.kiro/` artifacts that the author's Kiro session actually produced while writing Chapter 5, kept so you can compare your own specs against a finished set.

## Why It Exists

Section 5.7 walks through eight phases of conversation with Kiro. Because agentic output is not reproducible line for line, your `requirements.md` will not match the author's word for word, and it should not. What is useful is the *shape*: how many requirements the flow produced, how acceptance criteria were phrased in EARS notation, how much detail landed in the design document, and how tasks were grouped into MVPs.

Read these files after you finish a phase, not before. Reading the finished specs first turns the lab into transcription.

## What Is Here

```text
daily-briefing-agent/
├── README.md                   # This file
├── .gitignore                  # Produced by the final cleanup prompt in Phase 8
└── .kiro/
    ├── steering/
    │   ├── product.md          # Persona, features, target users
    │   ├── tech.md             # Stack, conventions, AWS services (inclusion: always)
    │   └── structure.md        # Directory layout, import order, anti-patterns
    ├── specs/tech-news-aggregator/
    │   ├── requirements.md     # ~14 KB of EARS-notation acceptance criteria
    │   ├── design.md           # ~50 KB: architecture, components, IAM, data models
    │   └── tasks.md            # ~30 KB: MVP-grouped implementation plan
    ├── hooks/
    │   ├── test-coverage-hook.kiro.hook
    │   └── docs-sync-hook.kiro.hook
    └── settings/
        └── mcp.json            # Empty: this snapshot predates Phase 6
```

Compare the sizes against the starter's specs. The starter's `design.md` is roughly 10 KB; this one is roughly 50 KB. That gap is what Phases 2 and 3 produce.

There is no `src/`, `tests/`, or `infrastructure/` directory here on purpose. This snapshot is the specification, not the generated application. The code is what you and Kiro write during the lab.

## The Project These Specs Describe

A tech news aggregator with a "Witty Tech Journalist" persona. It collects technology stories from Hacker News, generates sharp and slightly cynical summaries with Amazon Bedrock, and writes a daily briefing to markdown. The target architecture is a containerized Flask application on AWS App Runner, with Aurora PostgreSQL for persistence, S3 for briefing files, VPC endpoints for private service access, and Secrets Manager for credentials.

## How to Use It

**After Phase 2 (spec definition)**, diff your requirements against the reference:

```bash
diff ../hands-on-lab/daily-briefing-agent/.kiro/specs/tech-news-aggregator/requirements.md \
     .kiro/specs/tech-news-aggregator/requirements.md
```

Then ask yourself which requirements the author's run captured that yours missed, and whether they were missed because of a constraint you never stated.

**After Phase 3 (iterative refinement)**, read the reference `tasks.md` and check task ordering. Infrastructure deployment has to happen in dependency order, and it is easy to end up with a plan that deploys the application stack before the base stack.

**After Phase 5 (Powers)**, look at how the reference `design.md` handles IAM. The Bedrock statement scopes to specific foundation-model ARNs rather than a wildcard, which is a detail worth carrying into your own version.

**When something in your specs looks wrong**, search this directory for the same section before you ask Kiro to fix it. Sometimes the reference shows a shape you did not know to ask for.

## Three Caveats

**The model IDs are frozen.** The reference `design.md` pins specific Bedrock model IDs and inference-profile ARNs that were current when the chapter was written, and its editorial notes point to the Bedrock console's Model access page, which no longer takes access requests in commercial Regions (Bedrock now enables models on first use). For current IDs and access steps, see the lab starter's [`.env.example`](../hands-on-lab/daily-briefing-agent/.env.example); each model's card under [Models at a glance](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html) lists the valid IDs. The account ID in the example inference-profile ARN (`123456789012`) is the AWS documentation placeholder, not a real account.

**The hooks are a record, not files to copy.** The two `.kiro.hook` files use the layout from before Kiro IDE 1.0, and their `when.type` values carry the book's trigger names (`PostFileSave`, `Manual Trigger`) instead of the `fileEdited` and `userTriggered` values that layout expects. The lab starter and [`../code-examples/hooks/`](../code-examples/hooks/) carry loadable versions.

**`mcp.json` is empty here.** This snapshot was taken before the MCP servers were added in Phase 6. The lab starter ships with a populated `mcp.json` you can use as-is.

## Related

- Lab starter: [`../hands-on-lab/daily-briefing-agent/`](../hands-on-lab/daily-briefing-agent/)
- Lab walkthrough: [`../hands-on-lab/README.md`](../hands-on-lab/README.md)
- Phase 1 vibe output from the same session: [`../daily-briefing-agent-notes/`](../daily-briefing-agent-notes/)
- Chapter overview: [`../README.md`](../README.md)
