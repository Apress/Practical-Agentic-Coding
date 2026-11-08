# Maintaining this repository

Notes for the authors and for anyone contributing a correction or an update. Readers looking for the labs should start at [README.md](README.md).

**The published book is the source of truth.** A reader arrives here with the printed book open. Names, section numbers, and file paths in this repo must match the book.

## Layout and naming

Use one directory per chapter, zero-padded: `chapter-01` through `chapter-16`.

- Chapters 1 and 2 hold a `README.md` only.
- Chapter 3 adds four copy-ready team-process templates.

These are conceptual chapters with no code. Each README explains why there is nothing to run. It maps each book section to the later chapter that implements it.

Do not commit an empty directory. Git does not track empty directories, so a reader's clone would not match the README.

- If a directory must exist before it has content, put a `.gitkeep` in it. Say in the owning README what is coming.
- Otherwise, leave the directory out until it has a file.

Inside a chapter:

| Directory | Holds |
|-----------|-------|
| `code-examples/` | Standalone snippets and reference implementations tied to numbered book sections. Readers study them. They may not run end to end. |
| `tutorials/` | Tool setup walkthroughs (Chapters 4 to 8). In Chapter 8 this sits inside `hands-on-lab/`, because the book's Section 8.6 pointer says the lab directory contains the tutorials. |
| `hands-on-lab/` | The main guided lab. `starter/` holds scaffolded code with TODOs, `complete/` holds the reference solution, `exercises/` holds the step-by-step guides, `tests/` validates the reader's work. |
| `challenge-lab/` | The open-ended extension. Problem statement, hints, success criteria. No answer key where the output is not reproducible. |

Chapter 4 is the exception on exercises. It has a top-level `exercises/` directory instead of one nested under a lab. It ships configuration exercises and no guided lab.

Some chapters use a different layout:

- Chapters 11 and 12 nest `challenge-lab/` inside `hands-on-lab/`.
- Chapter 8 nests `tutorials/` inside `hands-on-lab/`. Its Section 8.6 pointer promises the lab directory holds the SupportFlow solution, exercise guides, and tutorials.
- Chapters 5 through 8 keep the lab application itself (`daily-briefing-agent/`, `moneymind/`, `linkforge/`, `supportflow/`) instead of a `starter/` and `complete/` pair. The reader builds it with the tool and does not fill in stubs.

Leave these as they are. The book and the chapter READMEs point at the existing paths. Moving directories breaks links in print.

File naming:

- Python and Markdown: lowercase with hyphens for documents (`exercise-1-memory-core.md`), lowercase with underscores for Python modules (`memory_core.py`). Follow whatever the sibling files already do.
- Exercise guides: `exercise-N-topic.md`, numbered in the order the lab expects.
- Per-chapter update logs: `UPDATES.md`, or `UPDATES-<TOPIC>.md` when it is scoped to one framework (see `chapter-14/hands-on-lab/UPDATES-AIDLC-2.0.md`).
- Environment templates: `.env.example`, always tracked, never a real `.env`.

## Adding a chapter artifact

1. **Find the promise in the book.** Every artifact here should match something the book asks the reader to do or points them to. Note the exact section number and the exact path the book prints.
2. **Put it where the book says.** If the book prints `companion-repo/chapter-11/code-examples/cost-guardrails.py`, the file goes at `chapter-11/code-examples/cost-guardrails.py`. The `companion-repo/` prefix in the book is this repository's root.
3. **Match the book's identifiers.** Class names, function names, and behavior should match the printed listing.
4. **Update the chapter README.** Add the new file to its directory tree, its asset list, and its section-mapping table.
5. **Give it a way to run.** Add a `requirements.txt` (or `package.json`), a setup step, and a way to verify the result. Where a lab has a `verify_setup.py`, extend it. Do not add a second checker.
6. **Add a changelog entry** in [CHANGELOG.md](CHANGELOG.md), naming the chapter (see "Changelog and dating rules" below).

If the book promises something that cannot be built faithfully, do not improvise a substitute. Record it as an erratum.

## Language and numbering rules

These come from the book's style conventions. They apply to every reader-facing file here, including READMEs, lab instructions, and worksheets.

- **Section numbers are top-level only.** Chapters number sections as `11.4`. Subsections are unnumbered. Never write "Section 11.4.2" in a reader-facing document. Use the top-level section that contains the material, checked against the book's headings. `grep -rnE 'Section [0-9]+\.[0-9]+\.[0-9]+' --include='*.md' .` should find nothing apart from this line.
- **Chapter titles are quoted verbatim** from the book when used in navigation links.
- **Tool names**:
  - Amazon Kiro (not "AWS Kiro")
  - Antigravity (one word, never "AntiGravity")
  - the Antigravity CLI and its `agy` command (it succeeded the Gemini CLI for consumer use)
  - Copilot cloud agent
  - Claude Code, documented at code.claude.com/docs
  - Cursor rules live in `.cursor/rules` (`.mdc` files with YAML frontmatter) plus `AGENTS.md`. The old single-file `.cursorrules` is legacy (Cursor's help center says it "is legacy and will be deprecated"). No lab or example here should use it.
  - ASH is the Automated Security Helper.
- **Plain practitioner English.** No em dashes. Use commas, colons, periods, or parentheses. Avoid: comprehensive, leverage, utilize, facilitate, robust, cutting-edge, game-changing, revolutionary, seamless, paradigm shift. This rule applies to prose only. It does not apply to code identifiers, JSON enum values, or quoted third-party text.
- **Shell blocks are copy-pasteable.** Write the bare command with no `$` prefix. Every fenced block gets a language tag.
- **Never invent tool facts.** No made-up flags, doc URLs, API paths, or model IDs. If you cannot verify a claim, soften it to what you can support, or drop it. Where a model choice matters, describe the tier ("a fast model for summarization"). Do not pin an alias that will age out.

## Recording tool drift

Tools in this space change faster than the book can. Pick the pattern that matches the size of the change.

**A lab-local change** (an install path moves, a command renames, a version pins differently):

1. Edit the lab in place so it still works.
2. Add a short dated note at the top of the lab README. Say that the instructions here are the tested version and win over the book text where they differ.

Chapter 14's lab README is the model for this.

**A change big enough to affect how a reader applies a chapter** (a tool succession, a framework major release, a protocol shift, a billing change): write an entry in [chapter-16/UPDATES.md](chapter-16/UPDATES.md). Use the template at the top of that file (area, what changed, chapters affected). Keep routine version bumps out of it. Vendor documentation is the authority for feature-level detail.

**A framework that forks into two live versions** gets its own scoped file next to the lab it affects. `chapter-14/hands-on-lab/UPDATES-AIDLC-2.0.md` is the example. The file covers:

- the date of the check, at the top, in the form the dating rule below sets
- what carried over
- what is genuinely new
- how to run the existing lab on the new version

Keep the lab itself pinned to the version the book teaches. Put the migration path in the update file.

Each of these also gets a [CHANGELOG.md](CHANGELOG.md) entry in the next release. A returning reader checks the changelog for what changed.

## Changelog and dating rules

- **Changelog.** [CHANGELOG.md](CHANGELOG.md) is the release history. v1.0 is the first release. It has no change list, because it is the repository as it accompanies the book. There is no Unreleased stub. A later change gets a new version heading, such as `## v1.1`. Under it, summarize what the change does and which chapters it touches.
- **Dating tool notes.** A note about a tool's current behavior carries the date it was checked. This release dates its tool notes "As of November 7, 2026" (headings use "(as of November 7, 2026)"). A later check uses its own date, in the same form, for the notes it touches. Leave the other notes alone. Do not add a date where nothing time-sensitive is stated.
- **Present tense.** State what a tool does today and what the reader should do. Where the tool differs from the printed book, name the book's term. The reader can then match the two.

## TODO: continuous verification in CI

A technical reviewer recommended this, and we have adopted it. It is not built yet. Two CI jobs would catch the drift we now find by hand:

- **Schema-lint the listings.** Validate the configuration artifacts in each chapter's `code-examples/` (agent cards, MCP configs, IaC snippets, rules files) against the published specs they claim to follow. A spec change or a hand-edit that breaks the format then fails a build before it reaches a reader.
- **Smoke-test each lab against pinned dependency versions.** For every chapter with a `requirements.txt` or `package.json`, install the pinned versions into a clean environment. Run the lab's test suite (or its `verify_setup.py`). A stale pin or an upstream API change then shows up here before a reader hits it.

## Pre-push checklist

Run through this before pushing to the public repository.

- [ ] **No secrets.** No real `.env` files, no API keys, tokens, connection strings, or certificates. Search the diff for `sk-`, `AKIA`, `password`, and `Bearer `. Every credential appears only as a placeholder in a `.env.example`.
- [ ] **No build or cache junk.** `.gitignore` covers `__pycache__/`, `*.py[cod]`, and `.pytest_cache/`, so running the labs locally does not add them to a commit. Confirm that nothing slipped in before the ignore rules existed:

  ```bash
  git ls-files | grep -E '__pycache__|\.pyc$|\.pytest_cache|node_modules|/venv/'
  ```

  That must print nothing. To also clear the untracked copies out of your working tree, run the command below. The copies come back each time you run a lab's tests. That is fine.

  ```bash
  find . -path ./.git -prune -o -type d \( -name __pycache__ -o -name .pytest_cache \) -prune -exec rm -rf {} +
  ```

  Also check for test output dumps (`test_output.txt`, `playwright_output.txt`, `test_run_log.txt`). They are ignored too.
- [ ] **No empty directories.** `find . -path ./.git -prune -o -type d -empty -print` returns nothing, except directories that hold a `.gitkeep` for a documented reason. Git does not track empty directories, so a clone would not match a README that lists one. Two known exceptions sit under `casestudy/` (`code/design/mocks/iterations/` and `code/backend/src/lambdas/agents/analyst/`). They are author-owned snapshot content. Git will not carry them anyway, so a reader's clone is already correct.
- [ ] **Banned words.** Prose is clean apart from three documented exemptions:
  - the rule list in this file
  - the Kiro-session artifacts under `chapter-05/daily-briefing-agent/`. This is a read-only snapshot the chapter tells the reader not to edit. Its README lists the editorial notes it carries.
  - the satirical persona examples in `chapter-05/daily-briefing-agent-notes/` and `chapter-05/hands-on-lab/daily-briefing-agent/.kiro/steering/product.md`. There, "revolutionary" is a joke about tech press releases.
- [ ] **`package-lock.json` files are committed** for the Node applications. They are deliberately not ignored. Reproducible installs depend on them.
- [ ] **Links resolve.** Every relative Markdown link points at a file that exists. Every external link is one you have opened.
- [ ] **Paths match reality.** Directory trees in READMEs list the files that are actually there, and no files that are not.
- [ ] **Commands are copy-pasteable.** No `$` sigils. No placeholder paths a reader cannot resolve. A correct language tag on every fenced block. Windows alternatives where activation or path syntax differs.
- [ ] **Section numbers are top-level** and match the book's headings.
- [ ] **Terminology matches** the list above.
- [ ] **Exercise TODOs survive.** `starter/` scaffolds are supposed to have TODO comments. They are the exercise. Do not "fix" them.
- [ ] **CHANGELOG.md carries the change** under a new version heading (for example `## v1.1`), for any change after v1.0.

## Contributions from readers

[Contributing.md](Contributing.md) covers the fork-branch-pull-request flow. When you review an incoming pull request, check it against the book first. A change can make the code better but diverge from the printed listing. That confuses the reader who is following along. In that case, take the fix and note the divergence in the chapter README.
