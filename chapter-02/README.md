# Chapter 2: Key Concepts: Agent Memory, Rules, and Governance Frameworks

Chapter 2 introduces agent memory, rule frameworks, and governance models. Later chapters build each one.

## Why there is no code here

Chapter 2 is the concepts chapter for Part III. It has one short illustrative snippet and no lab. Each pattern it introduces gets a full runnable implementation later in the book. The table below shows which chapter directory implements each concept.

| Book section | Topic | Where the code lives |
|---|---|---|
| 2.1 | Introduction | Conceptual; frames the three subsystems the chapter covers |
| 2.2 | Agent memory systems (types, context management, memory performance) | [chapter-09](../chapter-09/) builds DevMemory: episodic, semantic, and procedural stores on a vector backend (ChromaDB); its open-ended challenge lab adds a Neo4j graph backend |
| 2.3 | Rule-based frameworks in agentic systems (rule engines, rule validation) | [chapter-04](../chapter-04/code-examples/rules-files/) for rule-file formats; [chapter-05](../chapter-05/) for Kiro steering files; [chapter-07](../chapter-07/) for Cursor rules and Copilot instructions; [chapter-08](../chapter-08/) for CLAUDE.md and hooks |
| 2.4 | Governance frameworks for autonomous development (policy management, risk management) | [chapter-04](../chapter-04/code-examples/governance/) for AGILITY configuration (Chapter 4's seven-pillar governance framework); [chapter-12](../chapter-12/) builds the validator pipeline, audit log, and drift monitor |
| 2.5 | Integration patterns and best practices (memory-rule-governance) | [chapter-09](../chapter-09/) and [chapter-12](../chapter-12/) together |
| 2.6 | Emerging architectural patterns (observability, human-in-the-loop) | [chapter-10](../chapter-10/) for role-based agent teams and shared state |
| 2.7 | Challenges and limitations | Conceptual |

## Reading order that works

1. Read Chapter 2.
2. Do [chapter-04](../chapter-04/) to see rules and governance as concrete files.
3. Do [chapter-09](../chapter-09/) to build the memory system.
4. Do [chapter-12](../chapter-12/) to build the governance pipeline.
