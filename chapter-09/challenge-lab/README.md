# Challenge Lab: TeamMemory with Graph Relationships

Chapter 9, Section 9.7.

Add DevMemory's third scope (Section 9.5): organizational memory, backed by
Neo4j. You build:

- a pipeline that promotes patterns upward
- graph queries that traverse decisions

This challenge lab ships scaffolds with TODOs and no reference solution. The
Cypher you need is in the docstring hints. The verification queries below tell
you whether your code works. Plan a few hours for a first pass through the four
implementation steps. The stretch goals are open-ended.

## The problem

Five teams run their own DevMemory instances (agent scope plus shared project
scope). Nothing crosses team boundaries. The payments team learns that retry
logic needs idempotency keys. The orders team then has to learn the same thing.

Build TeamMemory, a third, organization-wide layer:

- High-confidence patterns get promoted into it from individual projects.
- A graph ties decisions, components, and teams together. Cross-team questions
  become graph traversals.

## Prerequisites

- The hands-on lab (Section 9.6) finished, with all five exercises passing.
  This lab imports `ScopedMemory` and `PatternMiner` from it.
- Docker Desktop, for the Neo4j and ChromaDB containers.
- The same OpenAI API key the hands-on lab needed (Mem0 still handles the vector
  side), or the Ollama config from that lab's README. Export the key here too:
  `export OPENAI_API_KEY=sk-your-real-key` (on Windows PowerShell,
  `$env:OPENAI_API_KEY = "sk-your-real-key"`).

## Setup

Run these from `chapter-09/challenge-lab/`.

### 1. Start the services

ChromaDB here binds the same host port (8000) as the hands-on lab's container.
If that container is still up, stop it first:

```bash
cd ../hands-on-lab && docker compose down && cd ../challenge-lab
```

Then start this lab's containers:

```bash
docker compose up -d
```

This starts ChromaDB (port 8000) and Neo4j (7474 for the browser, 7687 for
Bolt).

If you already started Neo4j with the book's
`docker run -d --name neo4j ... neo4j:5-community` command, stop it first with
`docker stop neo4j`. The compose file runs the same image with the same
`neo4j` / `devmemory` login on the same ports. The two cannot run at once.

### 2. Install dependencies

Activate the hands-on lab's virtualenv first. The neo4j driver then installs
next to the Mem0 and ChromaDB packages you already have, not in the global
interpreter:

```bash
source ../hands-on-lab/venv/bin/activate   # Windows: ..\hands-on-lab\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Put the hands-on lab on the import path

This lab reuses your finished `ScopedMemory` and `PatternMiner` from the other
lab's `starter/`. Point Python at them:

```bash
export PYTHONPATH=../hands-on-lab/starter
```

On Windows PowerShell, use `$env:PYTHONPATH = "..\hands-on-lab\starter"`.

After this, `from scopes import ScopedMemory` and `from memory_core import PatternMiner`
resolve. Set this in every shell you run this lab from.

Put the code you write for this lab in a script in `challenge-lab/`. Import the
scaffolds like this:

- `from starter.graph_store import GraphMemoryStore`
- `from starter.promotion import MemoryPromotion`

### 4. Verify Neo4j

Open http://localhost:7474 and log in with username `neo4j`, password
`devmemory`. Run:

```cypher
RETURN 'Neo4j is ready' AS status
```

Neo4j takes 20 to 30 seconds to accept connections on a cold start. If the
browser cannot connect, wait and retry.

`docker-compose.yml` publishes ChromaDB and Neo4j on `127.0.0.1` only. This
keeps them off your network. This setup can fail when you run Docker Desktop on
Windows and the lab inside a WSL distro. If `http://localhost:7474` (or
ChromaDB on port 8000) answers in Windows but not in WSL:

1. Remove the `127.0.0.1:` prefix from the `ports` entries in
   `docker-compose.yml` (for example `"7474:7474"`).
2. Run `docker compose up -d` again.

This publishes the ports on every interface. Do it only on a network you trust.

## Graph schema

The graph uses four node labels and four relationship types:

```cypher
(:Decision {title, rationale, date, confidence})
   -[:AFFECTS]-> (:Component {name, team})

(:Pattern {knowledge, confidence, episode_count})
   -[:APPLIES_TO]-> (:Service {name})

(:Team {name})
   -[:OWNS]-> (:Service {name})

(:Memory {id, content, scope})
   -[:DERIVED_FROM]-> (:Episode {session_type, outcome, timestamp})
```

The lab's queries walk these relationships:

- "Which decisions touch the payment service?" walks
  `Decision -[:AFFECTS]-> Component`.
- "Which teams have hit this error pattern?" walks
  `Pattern -[:APPLIES_TO]-> Service <-[:OWNS]- Team`.

Why these need a graph and not vector search: Chapter 9, Section 9.5.

## Starter files

| File | What to implement | Where the hints are |
|------|-------------------|---------------------|
| `starter/graph_store.py` | `GraphMemoryStore`: five Neo4j methods | Cypher templates in each docstring |
| `starter/promotion.py` | `MemoryPromotion`: three pipeline methods | Steps in each docstring |

## Implementation order

1. **`graph_store.py`**: `store_decision()` and `query_by_component()`. Insert a
   decision and query it back. Watch the graph form in the Neo4j browser. Use
   parameterized Cypher (`$title`), not string interpolation.

2. **`graph_store.py`**: `store_pattern()` and `get_provenance_chain()`. The
   first connects patterns to services. The second traces a memory back to its
   source episodes.

3. **`promotion.py`**: `evaluate_promotion()`. Check confidence against the
   threshold and cross-project count against Neo4j. Then write `promote()`. It
   writes to both stores: Mem0 for the vector side, Neo4j for the graph side.

4. **`promotion.py`**: `run_batch()`. Scan project patterns and promote the ones
   that qualify.

The promotion rule comes from Section 9.5. A pattern qualifies when both are
true:

- confidence is 0.9 or higher
- the pattern holds in two or more projects

`promotion.py`'s `MemoryPromotion` is the challenge version of the Section 9.5
class of the same name. It differs from the book's class:

- It takes your graph store and `ScopedMemory`, not a thresholds dict and a
  scope string.
- `evaluate_promotion()` answers yes or no for one pattern.

The 9.5 listing itself runs in `../code-examples/memory_promotion.py`.

The scaffolds leave three things to you:

- **The `UNWIND` templates return one row per related node.** We ran the
  `store_decision()` and `store_pattern()` hints against Neo4j 5.26 with the 6.x
  Python driver.
  - With two or more components, `result.single()` warns
    `Expected a result with a single record, but found multiple`. The id it
    returns is still right.
  - With an empty or missing list, the query returns no rows, so
    `result.single()["id"]` raises `TypeError`. That happens if `run_batch()`
    calls `promote(pattern)` without services, as its docstring sketches.

  Use a `FOREACH` to return exactly one row in every case:

  ```cypher
  CREATE (d:Decision {title: $title, rationale: $rationale, confidence: $confidence})
  FOREACH (comp_name IN $components |
      MERGE (c:Component {name: comp_name})
      CREATE (d)-[:AFFECTS]->(c))
  RETURN elementId(d) AS id
  ```

- **Nothing writes provenance yet.** `get_provenance_chain()` reads
  `(:Memory)-[:DERIVED_FROM]->(:Episode)` paths. No scaffold method creates
  `Memory` or `Episode` nodes. Add one, for example a method that takes the
  promoted memory's id and the source episodes. Call it from `promote()`.
- **Read-through stops at the project scope.** The hands-on lab's
  `recall_for_agent()` reads the agent and shared scopes only. To meet "every
  agent sees organizational memories", also recall from
  `MemoryPromotion.ORG_SCOPE`. Return those results under their own key.

## Requirements

**Organizational memory scope**
- Memory accessible across all projects, not just one
- Promotion from project scope when confidence is at least 0.9 and cross-project
  count is at least 2
- Demotion: when multiple projects contradict an organizational memory, its
  confidence decays until it archives

**Queries to support**
- "Which decisions touch the payment service?"
- "Which teams have hit this error pattern before?"
- "Where did this organizational policy come from?" (the provenance chain)

## Verification

### The graph store writes relationships

After `store_decision()`, in the Neo4j browser:

```cypher
MATCH (d:Decision)-[:AFFECTS]->(c:Component)
RETURN d.title, collect(c.name) AS affected_components
```

If each row pairs a decision title with a list of component names, the store
works.

### The provenance chain resolves

After provenance tracking:

```cypher
MATCH path = (m:Memory)-[:DERIVED_FROM*]->(e:Episode)
RETURN [node IN nodes(path) | properties(node)] AS chain
LIMIT 5
```

### Full success criteria

Section 9.7 lists these; verify each in the Neo4j browser:

- [ ] Decision records land in Neo4j together with their `AFFECTS` relationships
- [ ] `query_by_component("payment-service")` returns every decision that touches that component
- [ ] The promotion pipeline lifts qualifying patterns into the organizational scope
- [ ] Every agent sees organizational memories in its read-through results
- [ ] A memory can be traced back through `DERIVED_FROM` to its source episodes
- [ ] `calculate_trust()` uses graph connectivity as a signal

For the last one, extend `calculate_trust()` from the hands-on lab with the
`graph_trust_boost()` signal. A memory linked to more validated decisions gets
a higher score than an isolated one.

## Stretch goals

- Wrap TeamMemory in an MCP server so the Part II tools can query organizational
  knowledge directly
- Describe TeamMemory's capabilities in an Agent Card, per the A2A specification
  from Chapter 4
- Store the Decision Journal pattern (Section 9.4) fully in the graph.
  `../code-examples/decision_journal.py` has the record structure. Model its
  `affects` list as a relationship.
- Visualize the knowledge graph across teams

## Cleaning up

```bash
docker compose down     # stop and remove both containers; keeps the data
docker compose down -v  # same, and also discard the graph and vector data
```

Container data lives in two Docker volumes, `chroma-data` and `neo4j-data`. It
survives a plain `docker compose down`. Add `-v` to reset Neo4j and ChromaDB to
empty.
