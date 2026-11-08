# Hands-on Lab: Building DevMemory

Chapter 9, Section 9.6.

> **Why the version pin?** The chapter's install command and this repo's
> `requirements.txt` both pin `mem0ai>=1.0.6,<2`. Mem0 2.0 (April 2026) moved
> the user ID on `search()` and `get_all()` into a `filters` dict. On 2.x, the
> book's `search(query, user_id=...)` calls raise `ValueError: Top-level entity
> parameters ... are not supported`. The chapter's listings and this starter
> target the 1.x API. Install with Setup step 2 below and the pin is handled
> for you. It resolves to 1.0.11, the last 1.x release.

> **Updates to the printed book (as of November 7, 2026)**
>
> - **Python 3.15 is not supported.** ChromaDB's onnxruntime dependency
>   publishes no wheels for Python 3.15 (or for 3.14 on Intel Macs).
>   `pip install -r requirements.txt` cannot install it there.
> - **Add an `llm` block if you type the Phase 1 listing.** OpenAI does not
>   serve `gpt-4.1-nano-2025-04-14`, the fact-extraction model Mem0 1.x uses
>   when the config names none. `starter/memory_core.py` names OpenAI's listed
>   substitute, `gpt-5.6-luna`, in an `llm` block. If you type the Phase 1
>   listing from the book, add the same `llm` line to `mem0_config`. Without
>   it, the first `remember()` call that extracts facts fails with an error
>   from OpenAI.

You build DevMemory, a memory layer for any agentic tool. Mem0 handles the
memory lifecycle. ChromaDB stores the vectors. You write five pieces on top:

1. the memory core
2. session capture
3. memory scopes
4. pattern mining
5. trust scoring

Fill in the TODOs in `starter/`. The tests tell you when each piece works.
Plan about 90 minutes end to end.

## What you build

| Component | Book section | What it does |
|-----------|--------------|--------------|
| `DevMemory` | 9.6, Phase 1 | Three methods over Mem0: `remember`, `recall`, `recall_all` |
| `ApprenticeCapture` | 9.6, Phase 2 | Records a debugging session, derives the heuristic behind it |
| `ScopedMemory` | 9.6, Phase 3 | Private agent-level memory and shared project memory, with read-through recall |
| `PatternMiner` | 9.6, Phase 4 | Consolidates repeated episodes into one semantic fact |
| Trust scoring | 9.6, Phase 5 | Filters shared memories on provenance before they reach agent context |

The patterns behind these: Chapter 9, Section 9.4 (Apprentice Pattern,
Pattern Mining) and Section 9.5 (memory scopes, provenance and trust).

## Prerequisites

| What | Version | Why |
|------|---------|-----|
| Python | 3.11 to 3.14 (3.11 and 3.12 tested; 3.11 to 3.13 on an Intel Mac) | The book's listings and this starter target Python 3.11+. For 3.15, see the update note at the top of this file |
| Docker Desktop | any current release | Runs the ChromaDB container through `docker compose` |
| An OpenAI API key | any current key | Mem0's default LLM and embedder are OpenAI, so `remember()` and `recall()` make API calls |

Do not skip the API key. Mem0 uses one model to extract facts from what you
store and another to embed them. Out of the box, both are OpenAI. Without a
key, `DevMemory(config)` fails at construction with
`openai.OpenAIError: Missing credentials`.

The cost stays small. Fact extraction uses `gpt-5.6-luna` (see the update note
at the top of this file). Embeddings use Mem0's default,
`text-embedding-3-small`. A full pass through the tests, the exercise snippets,
and the demo makes a few dozen short calls. Expect the total to be cents.

To run fully local, point Mem0 at [Ollama](https://ollama.com). In the config
dict in `starter/memory_core.py`, replace the `llm` block and add an `embedder`
block:

```python
mem0_config = {
    "vector_store": {...},                        # leave as is
    "llm": {"provider": "ollama", "config": {"model": "llama3.1:8b"}},
    "embedder": {"provider": "ollama", "config": {"model": "mxbai-embed-large"}},
}
```

Then:

1. Pull both models: `ollama pull llama3.1:8b` and `ollama pull
   mxbai-embed-large`.
2. Install the client: `pip install ollama`.

Fact extraction needs a model that follows JSON instructions well. A very small
model produces worse memories than the OpenAI default.

Switch before you store anything, or start from an empty store. The OpenAI
embedder writes 1536-dimension vectors. `mxbai-embed-large` writes 1024.
ChromaDB rejects the mix with `InvalidArgumentError: Collection
expecting embedding with dimension of 1536, got 1024`. To reset, run
`docker compose down -v` (see Cleaning up), then run `docker compose up -d`
again. `verify_setup.py` detects the Ollama blocks. It then checks for a
running Ollama server instead of an OpenAI key.

## Setup

Run these from `chapter-09/hands-on-lab/`. Every later command in this file
assumes that directory. `pytest.ini` sets the import path from there.

### 1. Get the code

```bash
git clone https://github.com/Apress/Practical-Agentic-Coding.git
cd Practical-Agentic-Coding/chapter-09/hands-on-lab
```

### 2. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start ChromaDB

```bash
docker compose up -d
```

The container is named `devmemory-chromadb` and listens on port 8000. Wait a
few seconds. Then check that `docker compose ps` shows it healthy.

The heartbeat path changes between ChromaDB releases. The book's Section 9.6
sends you here for the current check. For the pinned 1.5.9 image, run:

```bash
curl http://localhost:8000/api/v2/heartbeat
```

A reply like `{"nanosecond heartbeat":1792345761484377849}` means the server is
up. Chroma 1.x answers the old `/api/v1/...` paths with HTTP 410 Gone. On Windows
PowerShell, type `curl.exe`. Plain `curl` there is an alias for
`Invoke-WebRequest`.

If you already started ChromaDB with the book's `docker run -d --name chromadb
... chromadb/chroma:latest` command, skip `docker compose up -d`. That container
serves the lab the same way on port 8000. Do not run both. They bind the same
port.

The compose file also:

- adds a healthcheck
- pins the image version
- publishes the port on 127.0.0.1 only
- keeps the vectors in a named Docker volume, `chroma-data`

ChromaDB 1.x has no login. If you use the book's command, write
`-p 127.0.0.1:8000:8000` to keep the server off your network.

### 4. Configure

```bash
cp .env.example .env
```

`.env.example` carries an `OPENAI_API_KEY=your_openai_api_key_here` placeholder.
Replace it with your real key in `.env`. Then export the same value in the shell
you run the lab from:

```bash
export OPENAI_API_KEY=sk-your-real-key
```

On Windows, use `$env:OPENAI_API_KEY = "sk-your-real-key"` in PowerShell or
`set OPENAI_API_KEY=sk-your-real-key` in Command Prompt.

`.env` is gitignored, so the key never gets committed. You must both export
the key and write it to `.env`. Mem0 reads the key from the environment, not
from this lab's `.env` file. Only `load_config()` in `starter/config.py` reads
the other values in `.env`. The tests and `demo.py` use the `DevMemoryConfig`
defaults, as the book's listings do.

### 5. Verify

```bash
python verify_setup.py
```

The script runs seven checks:

1. Python version
2. Docker
3. starter files
4. packages
5. `.env`
6. model access
7. the ChromaDB heartbeat

Model access means an exported `OPENAI_API_KEY`. If you made the Ollama change
in Prerequisites, it means a running Ollama server. The script exits with
status 1 until all seven pass. Fix anything that fails before you start
exercise 1. No check makes a model call, so running it costs nothing.

## Exercises

Do them in order. Each builds on the last.

| Exercise | File to edit | Topic | How you verify |
|----------|--------------|-------|----------------|
| 1 | `starter/memory_core.py` | Mem0-backed memory core | `pytest starter/tests/test_memory.py -v` |
| 2 | `starter/capture.py` | Apprentice Pattern capture | `pytest starter/tests/test_capture.py -v` |
| 3 | `starter/scopes.py` | Memory scopes | `pytest starter/tests/test_scopes.py -v` |
| 4 | `starter/memory_core.py` (`PatternMiner`) | Pattern Mining | Snippet in `exercises/exercise-4-mining.md` |
| 5 | `starter/trust.py` | Trust scoring | Snippet in `exercises/exercise-5-trust.md`, then `python starter/demo.py` |

Exercises 4 and 5 have no test file. Each guide has an inline verification
snippet instead:

- Pattern Mining needs three or more captured sessions before it produces a
  pattern.
- Trust scoring needs stored memories to filter.

`demo.py` is the end-to-end check. It only runs clean after exercise 5. It
calls `filter_by_trust()` from `trust.py`, which raises `NotImplementedError`
until then.

Strategic forgetting (Section 9.2) is not on the default path:

- Decay enters as the Exercise 5 extension (the age-decay factor in the trust
  score).
- The full decay-retention lifecycle runs in the standalone
  [`../code-examples/confidence_decay.py`](../code-examples/confidence_decay.py)
  demo.
- The `CONFIDENCE_THRESHOLD` and `RETENTION_DAYS` values in `.env` are for
  wiring that behavior in yourself. `load_config()` reads them. Nothing on the
  default exercise path uses them.

Step-by-step guides are in [`exercises/`](./exercises/), one file per exercise.

## Running the tests

```bash
pytest starter/tests/ -v
```

These are integration tests. They talk to the running ChromaDB container and
make model calls through Mem0. Expect a few seconds per test. All nine error at
setup in these cases:

- The API key is not exported: `openai.OpenAIError: Missing credentials`.
- The container is down: `ValueError: Could not connect to a Chroma server`.

Before you implement anything, with the key exported and ChromaDB up, eight of
the nine fail with `NotImplementedError`. The ninth,
`test_record_action_without_session_is_safe`, already passes, because
`record_action()` comes implemented. Each exercise turns its own tests green.

The book's expected-output block prints four tests. This suite has nine, with
more granular names:

- The book's `test_remember_and_recall` is split into three finer checks.
- Capture gains two edge-case tests.
- Scopes gains a read-through recall check.

All nine passing means the same thing as the book's four. The `recall_all()`
test stores its two memories with `infer=False`. Mem0's fact extraction may
drop content-free text like "Memory one", and the count would then depend on
the model.

On Python 3.12, pytest also reports `DeprecationWarning:
datetime.datetime.utcnow() is deprecated` from the `Action` and `Session`
dataclasses in `capture.py`. That line comes from the book's listing and is
harmless. Python 3.11 does not warn.

## End-to-end demo

After all five exercises:

```bash
python starter/demo.py
```

The demo:

1. captures three identical debugging sessions
2. mines them into one pattern
3. writes a team decision to the shared scope
4. recalls it as a different agent
5. prints the result with a trust score

Output like this means all five pieces work together:

```text
Discovered 1 patterns:
  For debugging sessions, checking 'docker logs api-service' first leads to success (3 of 3 times) (confidence: 1.0)
  [0.50] Team decision: use retry with exponential backoff for all external service calls. Max 3 retries, base delay 100ms.
```

The exact wording of the recalled memory varies. Mem0 rewrites what you store
into extracted facts. The second line may be a paraphrase of what `demo.py`
wrote. It may also be split into several shorter facts, one line each. Mem0's
extraction prompt's own examples split a sentence into separate facts.

The episodes persist in ChromaDB. A second run reports `(6 of 6 times)`, a
third `(9 of 9 times)`, and so on. To start the demo from an empty memory
again, run `docker compose down -v` (see Cleaning up).

## Troubleshooting

**`openai.OpenAIError: Missing credentials`**
Mem0 needs an API key. Export `OPENAI_API_KEY` in the shell you run tests from,
or switch to Ollama (see Prerequisites).

**ChromaDB not reachable**
```bash
docker compose ps
docker compose down && docker compose up -d
```

**ChromaDB not reachable from WSL**
`docker-compose.yml` publishes ChromaDB on `127.0.0.1` only. This keeps the
unauthenticated server off your network. This setup can fail when you run
Docker Desktop on Windows and the lab inside a WSL distro. If
`curl http://localhost:8000/api/v2/heartbeat` fails in WSL but works in
Windows:

1. Change `"127.0.0.1:8000:8000"` to `"8000:8000"` in `docker-compose.yml`.
2. Run `docker compose up -d` again.

This publishes the port on every interface. Do it only on a network you trust.

**`ModuleNotFoundError: No module named 'memory_core'`**
Run from `hands-on-lab/`, not from inside `starter/`. `pytest.ini` sets
`pythonpath = starter` relative to this directory.

**Import errors after installing**
```bash
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

**Port 8000 already in use**
The challenge lab's ChromaDB binds the same port. So does a container you
started with the book's `docker run` command. Stop whichever is up first:
`cd ../challenge-lab && docker compose down`, or `docker stop chromadb`.

If something else holds the port:

1. Change `"127.0.0.1:8000:8000"` to `"127.0.0.1:8001:8000"` in
   `docker-compose.yml`.
2. Change the `chromadb_port` default in `starter/config.py` to `8001`.

The tests and `demo.py` build `DevMemoryConfig` with its defaults, so
`CHROMADB_PORT` in `.env` does not reach them. `verify_setup.py` reads the same
default.

**`InvalidArgumentError: Collection expecting embedding with dimension of 1536, got 1024`**
You switched embedders (OpenAI to Ollama, or back) on a store that already holds
vectors from the other one. Reset the store as described under Prerequisites,
or use a new `project_name`.

**Tests pass but recall returns nothing**
Mem0 decides what is worth remembering. Very short or contentless strings can be
extracted into nothing at all. Store something a person would recognize as a
fact.

## Cleaning up

```bash
docker compose down     # stop and remove the ChromaDB container; keeps the vectors
docker compose down -v  # same, and also discard the stored vectors
```

Everything runs locally, so there is no cloud spend to stop. The vectors live in
the `chroma-data` Docker volume. The volume survives a plain
`docker compose down`. Add `-v` when you want the next run to start from an
empty memory.

## Next steps

- **Challenge lab** (Section 9.7): add Neo4j, organizational scope, and a
  cross-project promotion pipeline. See [../challenge-lab/README.md](../challenge-lab/README.md).
- **Chapter 10**: the shared project scope becomes the blackboard that
  coordinating agents read from and write to.
- **Chapter 11**: trust scoring gates deployment decisions.
