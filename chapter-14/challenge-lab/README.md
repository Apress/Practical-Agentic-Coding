# Challenge Lab: Wiring AI-DLC into CI/CD (Section 14.10)

Extend the hands-on lab into the Operations phase. This README is the build
guide. For the background: Chapter 14, Section 14.10.

Pick one of two routes:

- **Route 1**: build the phase yourself in a GitHub Actions pipeline, on top of
  the 1.x lab setup.
- **Route 2**: run the phase natively on a harness that 2.0 supports.

[../hands-on-lab/UPDATES-AIDLC-2.0.md](../hands-on-lab/UPDATES-AIDLC-2.0.md)
covers both routes. The challenge is open-ended. The starter scaffold gives
you the shape. You write the logic.

**Time**: open-ended. Plan on a half day to build the pipeline on the 1.x
setup. Running Workflows 2.0 natively adds its own install and setup time.

## What ships here

```text
challenge-lab/
├── README.md                                    # This file
└── starter/
    └── .github/workflows/aidlc-operations.yml   # Scaffold with numbered TODOs
```

## Prerequisites

- The finished hands-on lab ([../hands-on-lab/README.md](../hands-on-lab/README.md)).
  The AI-DLC 1.x rules are installed, and you have run a bolt.
- Chapter 11's Zero-Downtime Deployer, ready to call
  ([../../chapter-11/hands-on-lab/](../../chapter-11/hands-on-lab/)).
- The Chapter 11 gate patterns ([../../chapter-11/code-examples/](../../chapter-11/code-examples/)).
- Chapter 12's governance test suite. It runs the checks on the audit
  artifacts ([../../chapter-12/code-examples/governance_tests.py](../../chapter-12/code-examples/governance_tests.py)).
- A repository secret that holds an API key or workload-identity credential for
  the headless agent. Do not log the CI runner into anyone's personal
  subscription. The policy and billing reasons are in Section 14.10.

## The challenge

- Add the Chapter 11, Section 11.5 security and cost gates as pipeline jobs
- Make governance-test failures block merges (AI-DLC checkpoint verification
  as a quality gate)
- Reuse the canary deployment agent built in the Chapter 11 hands-on lab
- End state: the pipeline deploys a canary, checks its health, then shifts
  traffic or rolls back on its own

## Success criteria

- [ ] CI/CD carries the whole Operations flow (1.x lab setup extended, or
      native on Workflows 2.0)
- [ ] Every pull request gets a headless-agent security scan
- [ ] The cost gate stops any deploy that would blow the budget
- [ ] A failing health check triggers automatic canary rollback
- [ ] Each agent decision in the pipeline lands in an audit trail

## Starter scaffold

[`starter/.github/workflows/aidlc-operations.yml`](./starter/.github/workflows/aidlc-operations.yml)
holds three jobs:

- security gate
- cost gate
- canary deploy

It has seven numbered TODOs. You write the code at each one. These parts are
already in place:

- the job graph
- triggers
- least-privilege permissions
- artifact upload

The gate logic is yours.

Copy the file into your own repository's root. GitHub Actions only reads
workflows from the repository root:

```bash
mkdir -p /path/to/my-project/.github/workflows
cp starter/.github/workflows/aidlc-operations.yml \
   /path/to/my-project/.github/workflows/
```

On Windows, from this directory in PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path C:\path\to\my-project\.github\workflows
Copy-Item starter\.github\workflows\aidlc-operations.yml C:\path\to\my-project\.github\workflows\
```

Then:

1. Commit the file on a branch.
2. Open a pull request. The two gate jobs run on every pull request.
   `deploy-canary` runs only on pushes to `main`, so it does not run while you
   work on the branch.
3. Check the Actions tab after each push. A job with an unfinished TODO passes
   without doing anything. Finish the TODO to make the job do real work.

## Hints

- Install the AI-DLC rules in CI the same way as locally. Use the hands-on
  lab's pinned `curl` + `cp` steps as a workflow setup step. The headless
  agent session then runs under the same rules as your interactive sessions.
- For the audit trail, make every agent step write its decision + reasoning
  to a job artifact. The Chapter 12 governance test suite can then check
  those artifacts.
- On AI-DLC Workflows 2.0, the engine's built-in audit log and verification
  stages cover several criteria natively. See
  [../hands-on-lab/UPDATES-AIDLC-2.0.md](../hands-on-lab/UPDATES-AIDLC-2.0.md).
  Check the harness support matrix before you build your pipeline on it.
