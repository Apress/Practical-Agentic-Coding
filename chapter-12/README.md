# Chapter 12: Security, Privacy, and Ethical Considerations in AI Development

Runnable code for Chapter 12.

> **Where the repo differs from the printed book.** `PathRestrictionValidator`
> in `code-examples/composable_validators.py` is stricter than the book's
> listing. It normalizes each path and matches whole path components. So
> `/src/../etc/passwd` and `/srcevil/` do not pass as `/src`. The lab's
> version keeps the book's Section 12.8 `startswith()` form. Both of those
> inputs get past it.

**What's here**

- `code-examples/`: standalone examples. Each file runs on its own and
  prints a walkthrough of one pattern. For example, you can watch a
  validator block a call or a drift monitor fire an alert.
- `hands-on-lab/`: the lab where you write code.
  - `starter/` has 42 TODOs across five modules.
  - `tests/` checks each one.
  - `complete/` is the answer key.
- `hands-on-lab/challenge-lab/`: the open-ended extension. You test a
  multi-agent system as a composed whole.

**What you need**: Python 3.11+. No Docker, no API keys, no cloud account.
Nothing in this chapter calls a model.

## Directory Structure

```text
chapter-12/
├── README.md                    # This file
├── code-examples/               # Standalone examples from chapter sections
│   ├── composable_validators.py # Section 12.3: Composable validator pattern
│   ├── execution_rails.py       # Section 12.3: Four-step execution rail
│   ├── safety_contracts.py      # Section 12.4: Compositional safety verification
│   ├── goal_drift_monitor.py    # Section 12.5: Goal drift detection
│   ├── governance_tests.py      # Section 12.6: AGILITY governance test suite
│   ├── incident_response.py     # Section 12.7: Detection and containment
│   ├── model-access-policies/   # Section 12.2: model-allowlist policy templates (AWS, Azure, GCP)
│   └── requirements.txt         # numpy, scikit-learn, sqlparse (optional)
└── hands-on-lab/                # Main lab (Section 12.8)
    ├── README.md                # Lab setup and exercise order
    ├── verify_setup.py          # Environment check
    ├── conftest.py              # Anchors pytest import path here
    ├── requirements.txt         # Lab dependencies
    ├── starter/governance/      # Five modules, 42 TODOs for you
    ├── complete/                # Reference solution (mirrors starter/)
    │   ├── governance/          # Completed modules
    │   └── tests/               # Same 24 tests, run against complete/
    ├── tests/                   # Tests that validate your implementation
    └── challenge-lab/           # Multi-agent safety testing (Section 12.9)
```

## Quick Start

### Code Examples

Each file runs standalone and prints a narrated walkthrough:

```bash
cd code-examples
python3 -m venv .venv && source .venv/bin/activate   # Windows: py -m venv .venv, then .venv\Scripts\activate
pip install -r requirements.txt
python composable_validators.py
python execution_rails.py
python safety_contracts.py
python goal_drift_monitor.py
python governance_tests.py
python incident_response.py
```

`sqlparse` in `requirements.txt` is optional. `AbsoluteBoundary` in
`composable_validators.py` uses it to split SQL statements when it is
installed. Without it, a built-in splitter runs instead. Every check runs
either way.

Two examples trade fidelity for runnability. Each file documents its
choice.

- `goal_drift_monitor.py` scores alignment with TF-IDF cosine similarity
  instead of embeddings from a real embedding model. This keeps the demo
  offline and its printed numbers stable. TF-IDF measures vocabulary
  overlap only. An on-task paraphrase can score low. The file ships an
  `embedding_similarity` function for the production swap.
  `GoalDriftMonitor` takes a `score_fn`, so nothing else changes.
- `composable_validators.py` detects PII with regex instead of Presidio,
  which the chapter names. The regex covers emails, phone numbers, SSNs,
  and card numbers. It needs no install.

One subdirectory does not run. `model-access-policies/` holds
cloud-policy templates (AWS SCP, Azure Policy, GCP org policy) for the
model-allowlist control in Section 12.2. Its README lists what to
replace before you use them.

### Hands-On Lab: Building a Governance Pipeline

You build five things:

- composable validators
- a resource budget that halts an agent at its limit
- a hash-chained audit trail
- a goal drift monitor
- the execution rail that composes them

**Time**: 60-90 minutes. **Prerequisites**: Python 3.11+.

```bash
cd hands-on-lab
python3 -m venv venv && source venv/bin/activate   # Windows: py -m venv venv, then venv\Scripts\activate
pip install -r requirements.txt
python verify_setup.py
```

Then open `starter/governance/` and implement the TODOs. Run the tests
from the `hands-on-lab` directory:

```bash
pytest tests/test_governance.py -v
```

There are 24 tests. All of them fail with `NotImplementedError` before
you start. This is expected. If you get stuck, `complete/` has a working
version of every module. Run
`pytest complete/tests/test_governance.py -v` to confirm all 24 pass
against it.

Full instructions: [hands-on-lab/README.md](./hands-on-lab/README.md)

### Challenge Lab: Multi-Agent Safety Testing

Test a multi-agent system for safety as a composed whole. The lab gives
you six scaffolded tests. You write the test bodies.

**Time**: 90-120 minutes, after the hands-on lab.

**Start here**: [hands-on-lab/challenge-lab/README.md](./hands-on-lab/challenge-lab/README.md)

## Chapter Sections Mapped to Code

Each section maps to the file that implements it.

| Section | Topic | Code |
|---------|-------|------|
| 12.1 | Why agent governance is engineering | Conceptual (no code) |
| 12.2 | The threat landscape | `code-examples/model-access-policies/` (allowlist policy templates) |
| 12.3 | Guardrails-as-code | `code-examples/composable_validators.py`, `code-examples/execution_rails.py` |
| 12.4 | Multi-agent safety | `code-examples/safety_contracts.py` |
| 12.5 | Privacy, ethics, and alignment | `code-examples/goal_drift_monitor.py`, `AbsoluteBoundary` and `PIIValidator` in `code-examples/composable_validators.py` |
| 12.6 | Governance as executable tests | `code-examples/governance_tests.py` |
| 12.7 | When prevention fails: incident response | `code-examples/incident_response.py` |
| 12.8 | Hands-on lab | `hands-on-lab/starter/`, solution in `hands-on-lab/complete/` |
| 12.9 | Challenge lab | `hands-on-lab/challenge-lab/` |

## Go further with security standards

This reference builds on Chapter 12. Plans, pricing, and availability change. Each item links to the vendor page with current details.

- **OWASP Top 10 for LLM Applications 2026.** The 2026 edition reorders the list. Excessive Agency is number three. When you compare editions, match entries by name instead of number. The OWASP GenAI Security Project also accepted the Agent Control Standard (September 2026). It defines runtime controls applied at the same intercept point as the `ExecutionRail` pattern in this chapter's code. Introduced in August 2026. [LLM Top 10 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/), [Agent Control Standard](https://genai.owasp.org/resource/agent-control-standard-acs/)
