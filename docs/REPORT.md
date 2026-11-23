---
title: "Software Engineering — Assignment #05"
subtitle: "AI-assisted repository customization, agent readiness and software risk governance"
---

**Student:** _Surname Name_ · **Date:** 23 November 2026 · **AI assistant:** Claude Opus 5.5 (Anthropic), Claude app

**Repository:** `expense-tracker` (source code included in Appendix C: AGENTS.md, README and the full baseline → final diff; commit references below).
A small, non-sensitive Python CLI that records personal expenses in a local JSON file.
All data used is synthetic; the repository contains no credentials or personal data.

| Reference | Commit | Content |
|---|---|---|
| Baseline (tag `baseline`) | `5f85206` | original v0.1.0, untouched |
| Task 2 | `02d05a8` | AGENTS.md, acceptance criteria, `__main__.py`, tool config, README fix |
| Task 3 | `fba7d24` | Strategy refactoring of export formats |
| Mitigation M1 | `6b3a2ef` | input validation (R-01) |
| Mitigation M2 | `03e5dba` | CSV formula-injection neutralisation (R-02) + regression tests |
| Docs / evidence | `7771bcd`, `3a7a43d` | evidence logs, README "Known limitations" |
| Final (tag `final`) | `babc7cc` | final check log re-run on `3a7a43d` — reviewed version |
| Report | next commit | this report only (no code changes) |

All command outputs quoted below are copied from the log files in `evidence/` (exact commands, exit codes, timestamps). Environment: Python 3.13.18, pytest 9.1.1, ruff 0.16.9, mypy 2.3.1, Linux.

# Acceptance criteria

| ID | Criterion | Verification | Final status |
|---|---|---|---|
| AC1 | `add` → `list` preserves amount, category, description, date of a valid expense | round-trip test + golden `list.txt` | **Pass** |
| AC2 | `summary` (with/without `--month`) prints correct category totals and grand total | 3 report tests + golden `summary_*.txt` | **Pass** |
| AC3 | `export csv/json/md` output for valid data is byte-identical to baseline | `diff -r golden_baseline golden_final` → exit 0 | **Pass** |
| AC4 | Whole suite passes from a clean checkout with the documented command `python3 -m pytest -q` | `evidence/06_final_checks.txt` | **Pass** (failed at baseline) |
| AC5 | A data file written by v0.1.0 loads unchanged in the final version | `evidence/05_ac5_backward_compat.txt` | **Pass** |

# Task 1 — Baseline and context

**Repository map (baseline `5f85206`)**

| Element | Location |
|---|---|
| Entry point | `expense_tracker.cli:main` (console script `expense-tracker` in `pyproject.toml`) |
| Modules | `cli.py` (argparse + all command logic + export formatting), `models.py` (`Expense` dataclass), `storage.py` (JSON load/save), `report.py` (month filter, totals) |
| Runtime dependencies | none (standard library only) |
| Dev dependencies | `pytest`, `ruff`, `mypy` — declared **without versions** |
| Tests | `tests/test_basic.py` — 4 tests (totals, month filter, grand total, save/load round-trip) |
| Build | setuptools via `pyproject.toml`; no CI, no Makefile, no lint/type config |

**Baseline commands and actual results** (`evidence/01_baseline_checks.txt`)

| Command | Result |
|---|---|
| `python3 -m pytest -q` (as documented) | **exit 2** — `ModuleNotFoundError: No module named 'expense_tracker'`, collection error |
| `PYTHONPATH=src python3 -m pytest -q` | exit 0 — **4 passed** |
| `ruff check .` | **exit 1** — 2 errors (I001 unsorted imports in `models.py`, DTZ007 naive datetime in `report.py`) |
| `mypy src` | exit 0 — no issues in 5 files (non-strict; functions are untyped, so little is checked) |
| `python3 -m expense_tracker --help` (README command) | **fails** — `No module named expense_tracker.__main__` |
| `pip wheel . --no-deps --no-build-isolation` | exit 0 — `expense_tracker-0.1.0-py3-none-any.whl` built |

**Concrete weaknesses with evidence**

| # | Weakness | Evidence |
|---|---|---|
| W1 | Documented test command does not work from a clean checkout (src layout, no `pythonpath`) | `pytest` exit 2 above |
| W2 | README usage command `python -m expense_tracker` is wrong — no `__main__.py` | command output above |
| W3 | No input validation: `-50`, `nan`, `inf`, date `2026-13-45` are all stored; one bad date then crashes `summary --month` | `evidence/02_baseline_probes.txt` P1–P3 |
| W4 | User text is exported to CSV verbatim, including spreadsheet formulas | probe P4: `"=HYPERLINK(""http://evil.example"",""click"")"` |
| W5 | Corrupt data file → raw `JSONDecodeError` traceback, no recovery path; `save()` writes in place | probe P5; `storage.py` |
| W6 | Lint results depend on the installed ruff version: no `[tool.ruff]` config and unpinned dev deps | ruff reported DTZ007 with no repo config |
| W7 | No AGENTS.md / agent instructions, no CI | file listing |

**Facts vs. assumptions.** *Observed facts:* everything in the two tables above (commands were executed, outputs saved). *Assumptions:* that users open CSV exports in Excel/LibreOffice (makes W4 exploitable); that a crash during `save()` can truncate the file (not reproduced). *Unverified AI suggestions* are kept separate and classified in Task 4.

# Task 2 — Agent instructions (AGENTS.md)

A root-level `AGENTS.md` was created (see file). It contains: purpose; architecture table per module; the data-file compatibility contract; setup; **safe commands** (pytest, `ruff check`, `mypy src`, manual runs only against `/tmp` scratch files, wheel build, read-only git); coding conventions (thin CLI, new export format = new Strategy class, validation at the boundary with `ValueError` → exit 2, type hints); test expectations (a failing-then-passing test for every fix, paste real outputs, never claim un-run results, AC1–AC5 must hold); **forbidden actions** (no secrets/real personal data, no deploy/publish/push to `main`/tags, no destructive commands such as `rm -rf` outside `/tmp`, `git push --force`, `git reset --hard`, deleting a user's `expenses.json`, **no dependency changes without human approval**, no weakening of tests/lint, no network); **review gates** (agent delivers summary, diff, logs, risk notes → human approves; `storage.py`, data format and dependencies always need explicit sign-off).

In the same commit, the reproducibility gaps W1/W2 were fixed so that the safe commands in AGENTS.md actually work: `[tool.pytest.ini_options] pythonpath = ["src"]`, `src/expense_tracker/__main__.py`, explicit `[tool.ruff]` (rules E, F, W, I, B; line length 100) and `[tool.mypy]` sections, README rewritten with correct commands. `docs/ACCEPTANCE_CRITERIA.md` records AC1–AC5.

**Disclosure.** The assistant used (Claude in the Claude app's agent workspace) does not automatically load `AGENTS.md` (Claude Code auto-loads `CLAUDE.md`). The relevant AGENTS.md rules (safe commands, forbidden actions, test expectations) were therefore given to the assistant explicitly in the working context, and all later steps were run under them (scratch data only in `/tmp`, no dependency changes, no network, real outputs pasted).

# Task 3 — Focused pattern decision

**Problem.** `cmd_export` in `cli.py` (27 non-blank lines) mixed three concerns: choosing a format through an `if/elif/elif/else` chain on strings, formatting rows for each format, and opening/writing the output file. Adding a format meant editing the CLI, and the formatting could not be unit-tested without touching the filesystem.

**Options evaluated.**

| Option | Verdict |
|---|---|
| Leave as is | Works, but the chain grows with each format and is untestable without files — real maintainability cost. |
| **Strategy** (one exporter object per format, selected from a registry) | Removes the conditional, separates pure formatting from I/O, makes each format testable — **chosen**. |
| Adapter | Not applicable: there is no incompatible external interface to wrap. |
| Plugin system / entry points | Over-engineering for 3 formats in a single-user tool. |

**Refactoring (`fba7d24`).** New `exporters.py`: an `Exporter` `Protocol` with `render(expenses) -> str`, three classes `CsvExporter`, `JsonExporter`, `MarkdownExporter`, and the registry `EXPORTERS = {"csv": ..., "json": ..., "md": ...}`. `cmd_export` now looks up the strategy, exits 1 on an unknown format, and writes the rendered text.

| Metric | Before | After |
|---|---|---|
| `cmd_export` non-blank lines | 27 | 11 |
| Format conditionals in CLI | 3 branches + else | 1 dictionary lookup |
| Imports in `cli.py` | 7 (incl. `csv`, `json`) | 6 |
| Export formats unit-testable without files | no | yes (5 new tests) |

**Proof that acceptance criteria still hold.** The same valid dataset was run through baseline and refactored code; `diff -r golden_baseline golden_refactor` produced no differences for `data.json`, `list.txt`, both summaries and all three exports (`cmp` also confirmed byte-identical CSV, including `\r\n` row endings because the file is opened with `newline=""`). Tests: 9 passed, ruff and mypy clean. *Trade-off noted:* JSON/Markdown files are now also written with `newline=""`; on Linux this is identical, on Windows they now get `\n` instead of `\r\n` (not tested on Windows).

# Task 4 — Read-only risk review

The assistant was asked, in read-only mode (no file edits), to list candidate risks for the baseline across correctness, maintainability, security, dependency and agent operations. Every candidate was then investigated with code reading and the probes in `evidence/02_baseline_probes.txt`.

| ID | Candidate finding (AI-proposed) | Category | Classification | Evidence / reasoning |
|---|---|---|---|---|
| R-01 | No validation of amount/date; invalid data corrupts totals or breaks summaries | Correctness | **Confirmed** | P1: `add -50` and `--date 2026-13-45` → "Added."; P2: `summary --month` → `ValueError: time data '2026-13-45'…`; P3: `nan` → `TOTAL nan` |
| R-02 | CSV formula injection in exports | Security | **Confirmed** (behaviour); spreadsheet execution plausible | P4: description exported as `=HYPERLINK(...)` unescaped; `cli.py` `writer.writerow([... e.description])` |
| R-03 | Corrupt JSON crashes the tool; non-atomic `save()` can lose data | Correctness / reliability | **Confirmed** (crash); data loss on interrupted write **plausible/unverified** | P5: `JSONDecodeError` traceback, exit 1; `storage.save` opens target with `"w"` (truncates first) |
| R-04 | Money stored as `float` → rounding errors | Correctness | **Confirmed**, low impact | P6: JSON export `"total": 0.30000000000000004`; screen output rounded to 2 dp |
| R-05 | Unpinned dev dependencies / tool behaviour drifts | Dependency | **Confirmed** | `pyproject.toml`: `dev = ["pytest", "ruff", "mypy"]`; ruff applied version-default rules (DTZ007) with no repo config |
| R-06 | Export logic duplicated in an if/elif chain mixed with I/O | Maintainability | **Confirmed** | `cli.py` `cmd_export` (baseline) |
| R-07 | Agent can't run the project correctly: wrong README command, tests fail from clean checkout, no AGENTS.md | Agent operations | **Confirmed** | Task 1 table: pytest exit 2, `__main__` missing |
| R-08 | Two concurrent runs can lose an update (read-modify-write) | Correctness | **Plausible / unverified** | Code pattern load→append→save without locking; not reproduced (single-user CLI, race window small) |
| R-09 | "`json.load` of the data file allows code execution (insecure deserialisation)" | Security | **Unsupported** | `json.load` only builds dicts/lists/str/numbers; no `pickle`, `eval` or object hooks in the code |
| R-10 | "Tests write to the real `expenses.json`" | Agent operations | **Unsupported** | `tests/test_basic.py` uses `tmp_path`; no test calls `storage.load()` with the default path |
| R-11 | "Path traversal through `--file` / export output path" | Security | **Unsupported** (as a vulnerability) | Local single-user CLI: the user can only write where their own OS permissions allow; no privilege boundary is crossed |

11 findings across 5 categories; 7 confirmed, 1 plausible, 3 unsupported.

# Task 5 — Risk register

Score = Likelihood (1–3) × Impact (1–3). "Before" = baseline, "After" = final.

| ID | Category | Cause → Event → Consequence | Component | L | I | Score | Mitigation | Owner | Verification plan | After (L×I) / residual risk |
|---|---|---|---|---|---|---|---|---|---|---|
| R-01 | Correctness | No input checks → typo such as `-50` or `2026-13-45` is saved → wrong totals; `summary --month` crashes until the JSON is fixed by hand | `cli.cmd_add`, `models` | 3 | 3 | **9** | M1: `Expense.create()` validates; CLI prints `error:` and exits 2 | Maintainer (student) | 9 parametrised tests + probes P1–P3 re-run | 1×3 = **3**. Legacy files with bad dates still crash summary (`evidence/08`) |
| R-02 | Security | User text starting with `=`,`+`,`-`,`@` → exported to CSV verbatim → executed as a formula when opened in a spreadsheet (data exfiltration via links) | `exporters.CsvExporter` | 2 | 3 | **6** | M2: prefix such cells with `'` | Maintainer | 7 tests + probe P4 re-run | 1×2 = **2**. Other consumers (JSON/MD) not escaped; quote prefix visible in cell |
| R-03 | Correctness | Hand edit or crash mid-write → invalid/truncated JSON → traceback, possible loss of all records | `storage` | 2 | 3 | **6** | Planned: catch `JSONDecodeError` with clear message; atomic write (temp file + `os.replace`). Interim control: README backup warning | Maintainer | test with corrupt file; kill-during-save test | **6 (open)** |
| R-07 | Agent ops | Wrong docs/commands → agent/user runs failing commands or "fixes" the wrong thing | README, pyproject | 3 | 2 | **6** | Task 2: AGENTS.md, `__main__`, pytest config, README fixed | Maintainer | AC4 check log | 1×2 = **2** |
| R-05 | Dependency | Dev tools unpinned → different versions → lint/type/test results change between machines | `pyproject.toml` | 2 | 2 | **4** | Planned: pin dev tools (e.g. `requirements-dev.txt` with `==`), needs approval per AGENTS.md. Partial: explicit ruff/mypy config added | Maintainer | fresh venv install reproduces identical results | 2×1 = **2** (config added; pins open) |
| R-04 | Correctness | Floats for money → binary rounding → JSON export shows `0.30000000000000004` | `models`, `report` | 3 | 1 | **3** | Accepted for v0.1.x; planned: integer cents/`Decimal` with migration | Maintainer | sum test 0.1+0.2 == 0.30 | **3 (accepted)**, documented in README |
| R-06 | Maintainability | Format if/elif mixed with I/O → each new format edits CLI → regressions | `cli.cmd_export` | 3 | 1 | **3** | Task 3 Strategy refactor | Maintainer | golden diff + 5 exporter tests | 1×1 = **1** |
| R-08 | Correctness | Two processes save at once → last write wins → lost record | `storage` | 1 | 2 | **2** | Not mitigated (plausible only) | Maintainer | would need a concurrency test | 2 (unverified) |

**Top two confirmed risks for corrective action:** **R-01 (9)** and **R-02 (6)**. R-02, R-03 and R-07 tie at 6; R-07 was already resolved by the Task 2 documentation work, and R-02 was chosen over R-03 because it can harm third parties who open a shared export, while its fix is minimal and fully testable. R-03 is next in the queue and is a release condition (Task 9). No execution evidence was invented: every "confirmed" item links to a saved command output.

# Task 6 — Agent-readiness audit

| Criterion | Baseline (`5f85206`) | Final (`babc7cc`) |
|---|---|---|
| Readable structure | OK — small src layout, but CLI mixed with formatting | OK — clear module responsibilities (documented in AGENTS.md) |
| README accuracy | **Fail** — run command and test command wrong | Pass — commands verified; known limitations listed |
| Reproducible setup | Partial — install works; tests need undocumented `PYTHONPATH` | Pass — `pip install -e ".[dev]"`, `python3 -m pytest -q` works from clean checkout |
| Pinned dependencies | **Fail** — dev deps unpinned, no lock file | **Fail** — still unpinned (R-05 open) |
| Tests | 4 tests, documented command fails | 27 tests, pass; regression tests for M1/M2 |
| Lint / type checks | ruff 2 errors, no config; mypy no config | ruff clean with repo config; mypy clean (non-strict; `--strict` still reports 29 issues) |
| Build | wheel builds | wheel builds |
| CI | none | none |
| Logging / error reporting | tracebacks for user errors | validation errors are clear (`error:` + exit 2); corrupt file still traceback |
| Security safeguards | none | input validation, CSV neutralisation; no secrets in repo |
| AGENTS.md: permissions, safe commands, prohibited actions, review gates | **missing** | present and specific |

**Readiness level: baseline = 1 (Baseline); final = 2 (Documented).** Level 2 is justified because instructions, safe/forbidden actions, review gates and acceptance criteria are written down and the documented commands were executed successfully. **Not level 3** — missing evidence: (1) no CI that runs tests/lint/types on every change; (2) dev dependencies not pinned/locked; (3) no coverage measurement (coverage tool not available in this environment); (4) open data-integrity risk R-03; (5) mypy only non-strict; (6) no branch protection / pre-commit or secret scanning configured.

# Task 7 — Mitigation and verification

**Mitigation record M1 — R-01 input validation (`6b3a2ef`)**

* *Change:* new `Expense.create(amount, category, description, date)` — amount must parse as a finite number > 0; category stripped and non-empty; date must match `YYYY-MM-DD` and be a real calendar date (`date.fromisoformat`). `cmd_add` catches `ValueError`, prints `error: <message>` to stderr, exits 2, and **writes nothing**.
* *Diff review:* the first proposal only used `float()` + `> 0`; review found it would still accept `nan` (comparisons with NaN are False, so `nan <= 0` is False) and `inf` → `math.isfinite` added. `date.fromisoformat` alone accepts other ISO forms on Python 3.11+ (e.g. `20261101`), so the explicit regex was added. Storage format unchanged (AC5).
* *Tests:* 8 parametrised bad inputs (negative, zero, nan, inf, text, 2026-13-45, 2026-2-30, 05.11.2026), empty category, "bad add does not break later summary", normalisation test.

**Mitigation record M2 — R-02 CSV formula injection (`03e5dba`)**

* *Change:* `_safe_cell()` in `exporters.py` prefixes text cells (category, description) that start with `=`, `+`, `-`, `@`, TAB or CR with a single quote, following OWASP CSV-injection guidance. Numeric/date columns untouched. Implemented in the CSV strategy only — the Task 3 refactor made this a one-place change.
* *Diff review:* checked that normal text (including commas and quotes) is unchanged (test + golden diff), and that the prefix is applied after the `csv` module's own quoting, not instead of it.
* *Tests:* 6 parametrised payloads + "normal text untouched".

**Test evidence**

| Run | Command | Result |
|---|---|---|
| Baseline, documented command | `python3 -m pytest -q` | exit 2, collection error |
| Baseline, with path | `PYTHONPATH=src python3 -m pytest -q` | 4 passed |
| New tests before mitigations (`fba7d24`) | `python3 -m pytest -q tests/test_mitigations.py` | **17 failed, 1 passed** (`evidence/03`) |
| Final (`3a7a43d`) | `python3 -m pytest -q` | **27 passed, 0 failed** |
| Final | `ruff check .` / `mypy src` | all checks passed / no issues in 7 files |
| Final | wheel build | `expense_tracker-0.1.0-py3-none-any.whl` |
| Final probes (`evidence/07`) | same probes as baseline | P1/P3 → `error:` exit 2; P2 summary works; P4 cell exported as `'=HYPERLINK(...)`; P5, P6 unchanged (open risks) |
| AC3 / AC5 | golden diff; baseline data file | identical / loads unchanged |

*Not executed:* tests on Windows/macOS; Python 3.10–3.12 (only 3.13.18 available); opening the CSV in a real spreadsheet application; coverage measurement; concurrency test for R-08. *Screenshots:* the work was done in a terminal-only environment, so verbatim terminal logs in `evidence/` are provided instead of screenshots.

**Updated scores:** R-01 9 → 3, R-02 6 → 2 (plus R-07 6 → 2 and R-06 3 → 1 from Tasks 2–3). **Limitations / trade-offs:** validation applies to new input only, so old bad records still break `summary --month` (`evidence/08`); the `'` prefix appears in the spreadsheet cell and changes the text for any program that reads the CSV literally; legitimate descriptions starting with `-` (e.g. "-20% discount") are also prefixed.

# Task 8 — Background agent safeguards (hypothetical)

**Task:** "Mitigate R-03: make `storage.save()` atomic and turn a corrupt data file into a clear error message, with tests."

| Safeguard | Definition |
|---|---|
| Isolation | New branch `agent/r03-atomic-save` from tag `final`, in a separate worktree: `git worktree add ../et-r03 -b agent/r03-atomic-save final`. Container with **no network** and no access to the user's home directory or real `expenses.json`. |
| Allowed files | `src/expense_tracker/storage.py`, `src/expense_tracker/cli.py` (error handling only), `tests/test_storage.py` (new), `README.md` "Known limitations" section. Everything else read-only. |
| Allowed commands | `python3 -m pytest -q`, `ruff check .`, `mypy src`, `pip wheel . --no-deps --no-build-isolation -w /tmp/dist`, `git status/diff/add/commit` on the agent branch, file operations only inside the worktree and `/tmp`. |
| Prohibited | edits to `pyproject.toml` dependencies or any dependency install; `git push` to `main`, force-push, tags, rebase of shared history; `rm -rf` outside `/tmp`; changing the JSON data format; skipping/deleting tests or lint rules; network access; reading secrets/env files. |
| Limits | 30 min wall-clock, max 40 tool calls, max diff 200 changed lines; exceeding any limit → stop and report. |
| Required artifacts | (1) change summary with rationale; (2) full `git diff final...agent/r03-atomic-save`; (3) pytest / ruff / mypy logs with pass/fail totals; (4) wheel build result; (5) risk notes: what is still unverified (e.g. power loss on Windows), updated R-03 score; (6) AC1–AC5 check (golden diff). Delivered as a **draft** pull request. |
| Human review gate | A human reviews the diff line by line, re-runs the checks locally, and approves. Because `storage.py` is touched, AGENTS.md requires explicit sign-off. No merge or release without approval; the agent cannot merge. |
| Failure handling | If any check fails or a limit is hit, the agent stops, commits nothing to shared branches, and opens the draft PR labelled `needs-human` with logs. A human either gives a corrected task or abandons it. |
| Rollback | Before merge: `git worktree remove ../et-r03` and `git branch -D agent/r03-atomic-save` — main is untouched. After merge: `git revert <merge-commit>` and re-run checks; because the data format is unchanged, users' files stay valid; users are told to keep the backup recommended in the README. |

# Task 9 — Release decision

**Decision: CONDITIONAL** for tag `final` (`babc7cc`, v0.1.x).

* *Why not NO-GO:* all critical checks pass — 27/27 tests, ruff and mypy clean, wheel builds, AC1–AC5 verified (golden outputs byte-identical to baseline, baseline data loads). The highest risk (R-01, score 9) and the security risk R-02 are mitigated and covered by regression tests.
* *Why not GO:* a confirmed data-integrity risk remains open (R-03, score 6: corrupt file → traceback; non-atomic save), dev dependencies are unpinned (R-05) and readiness is level 2, not 3.
* *Conditions, controls and owners:*

| Condition | Control | Owner | Deadline |
|---|---|---|---|
| R-03 open | README tells users to back up `expenses.json`; fix via the Task 8 agent task + human review | Maintainer (student) | before v0.2 |
| Legacy bad dates (R-01 residual) | documented in README; add tolerant parsing/report in v0.2 | Maintainer | v0.2 |
| R-05 unpinned tools | pin dev tools after approval; until then record tool versions in every check log (done in `evidence/`) | Maintainer | v0.2 |
| R-04 float noise | accepted, documented; screen output rounded | Maintainer | review at v0.2 |

# Task 10 — AI reflection

I used Claude Opus 5.5 (Anthropic) in the Claude app's agent workspace, which can run shell commands. The context it received was the assignment PDF, the repository files, the outputs of every command it ran, and the AGENTS.md rules, which I supplied explicitly because this tool does not load AGENTS.md automatically.

A useful suggestion was to write the regression tests before the mitigations and run them against the unmodified code first. The result, 17 failed and 1 passed, proved that the tests really detect R-01 and R-02. The golden-output comparison likewise turned "behaviour is unchanged" into a byte-level `diff`.

Several suggestions were weak or wrong. The read-only review claimed that `json.load` allows code execution, that the tests overwrite the real `expenses.json`, and that `--file` is a path-traversal vulnerability. Reading the code disproved all three, so they are classified as unsupported. The first validation draft also used only `float(x) > 0`, which still accepts `nan` and `inf`. The probe script exposed this and `math.isfinite` was added.

I personally checked each finding against the files and the saved command output, compared the diffs before accepting them, and reran the full test, lint, type and build checks at the end. The tests also changed my decisions. The probes showed that one bad date breaks every later monthly summary, which raised R-01 from a cosmetic problem to the top risk. The final probes showed that old bad records still fail, so the release is CONDITIONAL rather than GO.

The repository instructions helped. With safe commands and forbidden actions written down, the assistant used only /tmp scratch files and left dependencies untouched. Next time I would add CI and pinned tool versions first, so that agent results can be reproduced on any machine.

# Appendix A — AI-use record

| Date | Tool / model | Prompt summary | Output used | Problems found | Changes made | Verification source |
|---|---|---|---|---|---|---|
| 2026-11-23 | Claude Opus 5.5, Claude app | Read the assignment PDF and plan the tasks | task breakdown, choice of a small CLI project | — | — | assignment PDF |
| 2026-11-23 | same | Create a small expense-tracker baseline, commit and tag it; run tests, lint, types, build | baseline code, check script | documented `pytest` command fails; README run command fails | recorded as W1/W2 | `evidence/01` |
| 2026-11-23 | same | Probe the baseline for risky behaviour | probe script and output | — | — | `evidence/02` |
| 2026-11-23 | same | Draft AGENTS.md and acceptance criteria | AGENTS.md, AC1–AC5 | first draft referenced files that did not exist yet | marked `exporters.py` as introduced in Task 3 | file review |
| 2026-11-23 | same | Propose one pattern for the export code and implement it | Strategy registry | possible line-ending change | kept `newline=""`; Windows trade-off documented | golden `diff -r`, 9 tests |
| 2026-11-23 | same | Read-only risk review: list candidate risks, do not edit files | 11 candidates | 3 unsupported claims (R-09, R-10, R-11) | classified as unsupported with reasons | code reading, probes |
| 2026-11-23 | same | Write failing regression tests, then minimal fixes for R-01 and R-02 | `test_mitigations.py`, M1, M2 | first validation accepted nan/inf; ISO date too permissive | `isfinite` and regex added | `evidence/03`, `06`, `07` |
| 2026-11-23 | same | Readiness audit, background-agent design, release decision, report | this report | — | wording reviewed | evidence logs, git log |

# Appendix B — Evidence files (key logs reproduced in Appendix D)

`evidence/01_baseline_checks.txt` · `02_baseline_probes.txt` · `03_mitigation_tests_before.txt` · `04_golden_comparison.txt` · `05_ac5_backward_compat.txt` · `06_final_checks.txt` · `07_final_probes.txt` · `08_residual_legacy_bad_date.txt`. Reproduce: `git checkout baseline` / `git checkout final` and run the commands shown in each file.

# Appendix C — Source code

## C.1 AGENTS.md (final)

```text
# AGENTS.md — instructions for AI coding agents

This file is the operating contract for any AI coding agent (Claude Code, Codex,
Copilot agent, etc.) working in this repository. Humans should read it too.

## 1. Purpose
`expense-tracker` is a small offline command-line tool that records personal
expenses in a local JSON file and prints listings, monthly summaries and exports
(CSV / JSON / Markdown). It has no network access, no server and no database.

## 2. Architecture (src layout)
| Path | Responsibility |
|---|---|
| `src/expense_tracker/cli.py` | argparse entry point (`main`), one `cmd_*` function per sub-command. Only I/O and wiring — no business rules. |
| `src/expense_tracker/__main__.py` | enables `python -m expense_tracker` |
| `src/expense_tracker/models.py` | `Expense` dataclass, (de)serialisation, input validation |
| `src/expense_tracker/storage.py` | load/save the JSON data file |
| `src/expense_tracker/report.py` | pure functions: month filter, totals |
| `src/expense_tracker/exporters.py` | export formats (Strategy registry `EXPORTERS`) — introduced in the Task 3 refactor |
| `tests/` | pytest suite; every test must use `tmp_path`, never the real data file |

Data file format (must stay backward compatible): a JSON list of
`{"amount": number, "category": str, "description": str, "date": "YYYY-MM-DD"}`.

## 3. Setup
```
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
```
Python >= 3.10. Do not change the supported Python range without approval.

## 4. Safe commands (allowed without asking)
```
python3 -m pytest -q            # tests (pythonpath is configured in pyproject)
ruff check .                    # lint (read-only; do NOT run with --fix on files you were not asked to touch)
mypy src                        # type check
python3 -m expense_tracker --file /tmp/<scratch>.json <command>   # manual check with a scratch file
pip wheel . --no-deps --no-build-isolation -w /tmp/dist           # build check
git status / git diff / git log # inspection
```

## 5. Coding conventions
- Keep `cli.py` thin: parsing, printing, exit codes. Business rules live in `models.py` / `report.py`.
- New export format = new class in `exporters.py` + one entry in `EXPORTERS`; never add `if/elif` chains on format names.
- Validate user input at the boundary (`Expense.create`) and raise `ValueError` with a clear message; the CLI turns it into `error: ...` and exit code 2.
- Type hints on all new functions; keep `mypy src` clean.
- Standard library only at runtime. Small, focused commits with a message that says *why*.

## 6. Test expectations
- Every behaviour change or bug fix comes with a test that fails before and passes after.
- Run `python3 -m pytest -q`, `ruff check .` and `mypy src` before declaring work done, and paste the actual output (pass/fail counts). Never claim a result you did not run.
- Acceptance criteria AC1–AC5 (see `docs/ACCEPTANCE_CRITERIA.md`) must stay true.

## 7. Forbidden actions (never do these)
- Never read, create or commit secrets, tokens, `.env` files or real personal/financial data. Use only synthetic sample data.
- Never deploy, publish to PyPI, push tags or push to `main`; work on a feature branch.
- No destructive commands: `rm -rf` outside `/tmp`, `git push --force`, `git reset --hard`, history rewrites, deleting or overwriting a user's `expenses.json`.
- No dependency changes (adding, removing, upgrading packages, editing `[project.dependencies]` or dev extras) without explicit human approval in the task.
- Do not disable, skip or weaken tests, lint rules or type checks to make a check pass.
- Do not access the network from code or tests.

## 8. Review gates
1. Agent produces: change summary, diff, test/lint/type/build output, and a note of risks or unverified assumptions.
2. A human reviews the diff and the evidence and approves before merge.
3. Changes to `storage.py` (data-loss risk), the data file format, or dependencies always need explicit human sign-off.

## 9. When unsure
Stop and ask instead of guessing. Prefer the smallest change that satisfies the task.
```

## C.2 README.md (final)

```text
# Expense Tracker

A tiny offline command-line tool to record personal expenses and print summaries.
Standard library only at runtime; data lives in a local JSON file.

## Install

```
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```
python3 -m expense_tracker add 12.50 food "Lunch" --date 2026-11-01
python3 -m expense_tracker list
python3 -m expense_tracker summary --month 2026-11
python3 -m expense_tracker export csv out.csv      # formats: csv, json, md
python3 -m expense_tracker --file other.json list  # use another data file
```

After `pip install -e .` the same commands are available as `expense-tracker ...`.
Data is saved to `expenses.json` in the current folder unless `--file` is given.

## Checks

```
python3 -m pytest -q
ruff check .
mypy src
pip wheel . --no-deps --no-build-isolation -w /tmp/dist
```

## Known limitations (v0.1.x)
- **Back up `expenses.json` before upgrading or editing it by hand.** A corrupted or
  hand-edited file stops the tool with a traceback, and saving is not atomic (risk R-03).
- Records with invalid dates written by v0.1.0 can still break `summary --month`;
  fix them by hand (new input is validated since M1).
- Amounts are floats; totals are rounded to 2 decimals on screen, the JSON export may
  show binary rounding noise such as `0.30000000000000004` (risk R-04).

## For AI agents
Read [AGENTS.md](AGENTS.md) before changing anything. Acceptance criteria:
[docs/ACCEPTANCE_CRITERIA.md](docs/ACCEPTANCE_CRITERIA.md).
```

## C.3 Acceptance criteria file

```text
# Acceptance criteria (must remain true after every change)

| ID | Criterion | How it is verified |
|---|---|---|
| AC1 | `add` then `list` preserves every field (amount, category, description, date) of a valid expense. | `tests/test_basic.py::test_save_and_load_roundtrip`, golden `list.txt` comparison |
| AC2 | `summary` (with and without `--month`) prints correct per-category totals and grand total for valid data. | `test_totals_by_category`, `test_filter_month`, `test_grand_total`, golden `summary_*.txt` |
| AC3 | `export csv|json|md` output for valid data is byte-identical to the baseline version. | golden comparison of `out.csv`, `out.json`, `out.md` (`diff -r`) + `tests/test_exporters.py` |
| AC4 | The full suite passes from a clean checkout with the documented command `python3 -m pytest -q`. | check log in `evidence/` |
| AC5 | A data file written by the baseline version (v0.1.0) loads unchanged in the new version. | golden `data.json` from baseline is reused by the final run |
```

## C.4 Baseline source (tag `baseline`, 5f85206)

**pyproject.toml**

```python
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "expense-tracker"
version = "0.1.0"
description = "Small command-line expense tracker that stores data in a local JSON file"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]

[project.scripts]
expense-tracker = "expense_tracker.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
```

**src/expense_tracker/models.py**

```python
from dataclasses import dataclass, asdict


@dataclass
class Expense:
    amount: float
    category: str
    description: str
    date: str  # YYYY-MM-DD

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Expense(
            amount=float(data["amount"]),
            category=data["category"],
            description=data.get("description", ""),
            date=data["date"],
        )
```

**src/expense_tracker/storage.py**

```python
import json
import os

from .models import Expense

DEFAULT_FILE = "expenses.json"


def load(path=DEFAULT_FILE):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Expense.from_dict(item) for item in data]


def save(expenses, path=DEFAULT_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump([e.to_dict() for e in expenses], f, indent=2)
```

**src/expense_tracker/report.py**

```python
from datetime import datetime


def filter_month(expenses, month):
    """Return expenses whose date falls in month (YYYY-MM)."""
    result = []
    for e in expenses:
        d = datetime.strptime(e.date, "%Y-%m-%d")
        if d.strftime("%Y-%m") == month:
            result.append(e)
    return result


def totals_by_category(expenses):
    totals = {}
    for e in expenses:
        totals[e.category] = totals.get(e.category, 0) + e.amount
    return totals


def grand_total(expenses):
    total = 0
    for e in expenses:
        total += e.amount
    return total
```

**src/expense_tracker/cli.py**

```python
import argparse
import csv
import json
import sys

from . import storage
from .models import Expense
from .report import filter_month, grand_total, totals_by_category


def cmd_add(args):
    expenses = storage.load(args.file)
    expenses.append(Expense(float(args.amount), args.category, args.description, args.date))
    storage.save(expenses, args.file)
    print("Added.")


def cmd_list(args):
    expenses = storage.load(args.file)
    for i, e in enumerate(expenses, 1):
        print(f"{i}. {e.date} {e.category:<12} {e.amount:>10.2f}  {e.description}")


def cmd_summary(args):
    expenses = storage.load(args.file)
    if args.month:
        expenses = filter_month(expenses, args.month)
    for cat, total in sorted(totals_by_category(expenses).items()):
        print(f"{cat:<12} {total:>10.2f}")
    print(f"{'TOTAL':<12} {grand_total(expenses):>10.2f}")


def cmd_export(args):
    expenses = storage.load(args.file)
    if args.format == "csv":
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "category", "amount", "description"])
            for e in expenses:
                writer.writerow([e.date, e.category, e.amount, e.description])
    elif args.format == "json":
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(
                {"expenses": [e.to_dict() for e in expenses], "total": grand_total(expenses)},
                f,
                indent=2,
            )
    elif args.format == "md":
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("| date | category | amount | description |\n")
            f.write("|---|---|---|---|\n")
            for e in expenses:
                f.write(f"| {e.date} | {e.category} | {e.amount:.2f} | {e.description} |\n")
            f.write(f"\n**Total:** {grand_total(expenses):.2f}\n")
    else:
        print("Unknown format: " + args.format)
        sys.exit(1)
    print(f"Exported {len(expenses)} expenses to {args.output}")


def build_parser():
    p = argparse.ArgumentParser(prog="expense-tracker")
    p.add_argument("--file", default=storage.DEFAULT_FILE)
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("add")
    a.add_argument("amount")
    a.add_argument("category")
    a.add_argument("description", nargs="?", default="")
    a.add_argument("--date", required=True)
    a.set_defaults(func=cmd_add)

    sub.add_parser("list").set_defaults(func=cmd_list)

    s = sub.add_parser("summary")
    s.add_argument("--month")
    s.set_defaults(func=cmd_summary)

    x = sub.add_parser("export")
    x.add_argument("format")
    x.add_argument("output")
    x.set_defaults(func=cmd_export)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
```

**tests/test_basic.py**

```python
from expense_tracker import storage
from expense_tracker.models import Expense
from expense_tracker.report import filter_month, grand_total, totals_by_category


def sample():
    return [
        Expense(10.0, "food", "lunch", "2026-11-01"),
        Expense(5.5, "transport", "bus", "2026-11-02"),
        Expense(20.0, "food", "dinner", "2026-10-30"),
    ]


def test_totals_by_category():
    assert totals_by_category(sample()) == {"food": 30.0, "transport": 5.5}


def test_filter_month():
    assert len(filter_month(sample(), "2026-11")) == 2


def test_grand_total():
    assert grand_total(sample()) == 35.5


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "data.json"
    storage.save(sample(), path)
    assert storage.load(path) == sample()
```

## C.5 Changes baseline → final (`git diff baseline final -- pyproject.toml src tests`)

```diff
diff --git a/pyproject.toml b/pyproject.toml
index 3ca39cf..d97474c 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -17,3 +17,17 @@ expense-tracker = "expense_tracker.cli:main"
 
 [tool.setuptools.packages.find]
 where = ["src"]
+
+[tool.pytest.ini_options]
+pythonpath = ["src"]
+testpaths = ["tests"]
+
+[tool.ruff]
+target-version = "py310"
+line-length = 100
+
+[tool.ruff.lint]
+select = ["E", "F", "W", "I", "B"]
+
+[tool.mypy]
+python_version = "3.10"
diff --git a/src/expense_tracker/__main__.py b/src/expense_tracker/__main__.py
new file mode 100644
index 0000000..4e28416
--- /dev/null
+++ b/src/expense_tracker/__main__.py
@@ -0,0 +1,3 @@
+from .cli import main
+
+main()
diff --git a/src/expense_tracker/cli.py b/src/expense_tracker/cli.py
index e4e1b10..5e06b52 100644
--- a/src/expense_tracker/cli.py
+++ b/src/expense_tracker/cli.py
@@ -1,16 +1,20 @@
 import argparse
-import csv
-import json
 import sys
 
 from . import storage
+from .exporters import EXPORTERS
 from .models import Expense
 from .report import filter_month, grand_total, totals_by_category
 
 
 def cmd_add(args):
+    try:
+        expense = Expense.create(args.amount, args.category, args.description, args.date)
+    except ValueError as exc:
+        print(f"error: {exc}", file=sys.stderr)
+        sys.exit(2)
     expenses = storage.load(args.file)
-    expenses.append(Expense(float(args.amount), args.category, args.description, args.date))
+    expenses.append(expense)
     storage.save(expenses, args.file)
     print("Added.")
 
@@ -31,30 +35,14 @@ def cmd_summary(args):
 
 
 def cmd_export(args):
-    expenses = storage.load(args.file)
-    if args.format == "csv":
-        with open(args.output, "w", newline="", encoding="utf-8") as f:
-            writer = csv.writer(f)
-            writer.writerow(["date", "category", "amount", "description"])
-            for e in expenses:
-                writer.writerow([e.date, e.category, e.amount, e.description])
-    elif args.format == "json":
-        with open(args.output, "w", encoding="utf-8") as f:
-            json.dump(
-                {"expenses": [e.to_dict() for e in expenses], "total": grand_total(expenses)},
-                f,
-                indent=2,
-            )
-    elif args.format == "md":
-        with open(args.output, "w", encoding="utf-8") as f:
-            f.write("| date | category | amount | description |\n")
-            f.write("|---|---|---|---|\n")
-            for e in expenses:
-                f.write(f"| {e.date} | {e.category} | {e.amount:.2f} | {e.description} |\n")
-            f.write(f"\n**Total:** {grand_total(expenses):.2f}\n")
-    else:
+    exporter = EXPORTERS.get(args.format)
+    if exporter is None:
         print("Unknown format: " + args.format)
         sys.exit(1)
+    expenses = storage.load(args.file)
+    # newline="" keeps the csv module's \r\n row endings byte-identical to the baseline
+    with open(args.output, "w", newline="", encoding="utf-8") as f:
+        f.write(exporter.render(expenses))
     print(f"Exported {len(expenses)} expenses to {args.output}")
 
 
diff --git a/src/expense_tracker/exporters.py b/src/expense_tracker/exporters.py
new file mode 100644
index 0000000..125c271
--- /dev/null
+++ b/src/expense_tracker/exporters.py
@@ -0,0 +1,61 @@
+"""Export formats (Strategy pattern).
+
+Each exporter turns a list of expenses into the text of one output file.
+Exporters are pure (no file I/O), so they can be unit-tested directly;
+the CLI only picks a strategy from ``EXPORTERS`` and writes the result.
+"""
+
+from __future__ import annotations
+
+import csv
+import io
+import json
+from typing import Protocol
+
+from .models import Expense
+from .report import grand_total
+
+
+class Exporter(Protocol):
+    def render(self, expenses: list[Expense]) -> str: ...
+
+
+# Cells starting with these characters are interpreted as formulas by
+# Excel / LibreOffice / Google Sheets (OWASP "CSV Injection").
+_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")
+
+
+def _safe_cell(text: str) -> str:
+    """Neutralise spreadsheet formulas in user-controlled text (risk R-02)."""
+    return "'" + text if text.startswith(_FORMULA_PREFIXES) else text
+
+
+class CsvExporter:
+    def render(self, expenses: list[Expense]) -> str:
+        buf = io.StringIO()
+        writer = csv.writer(buf)
+        writer.writerow(["date", "category", "amount", "description"])
+        for e in expenses:
+            writer.writerow([e.date, _safe_cell(e.category), e.amount, _safe_cell(e.description)])
+        return buf.getvalue()
+
+
+class JsonExporter:
+    def render(self, expenses: list[Expense]) -> str:
+        payload = {"expenses": [e.to_dict() for e in expenses], "total": grand_total(expenses)}
+        return json.dumps(payload, indent=2)
+
+
+class MarkdownExporter:
+    def render(self, expenses: list[Expense]) -> str:
+        lines = ["| date | category | amount | description |", "|---|---|---|---|"]
+        for e in expenses:
+            lines.append(f"| {e.date} | {e.category} | {e.amount:.2f} | {e.description} |")
+        return "\n".join(lines) + f"\n\n**Total:** {grand_total(expenses):.2f}\n"
+
+
+EXPORTERS: dict[str, Exporter] = {
+    "csv": CsvExporter(),
+    "json": JsonExporter(),
+    "md": MarkdownExporter(),
+}
diff --git a/src/expense_tracker/models.py b/src/expense_tracker/models.py
index beff372..b6c0b95 100644
--- a/src/expense_tracker/models.py
+++ b/src/expense_tracker/models.py
@@ -1,4 +1,9 @@
-from dataclasses import dataclass, asdict
+import math
+import re
+from dataclasses import asdict, dataclass
+from datetime import date as _date
+
+_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
 
 
 @dataclass
@@ -19,3 +24,23 @@ class Expense:
             description=data.get("description", ""),
             date=data["date"],
         )
+
+    @staticmethod
+    def create(amount: str, category: str, description: str, date: str) -> "Expense":
+        """Build an Expense from raw user input, rejecting invalid values (risk R-01)."""
+        try:
+            value = float(amount)
+        except ValueError:
+            raise ValueError(f"amount must be a number, got {amount!r}") from None
+        if not math.isfinite(value) or value <= 0:
+            raise ValueError(f"amount must be a positive finite number, got {amount!r}")
+        category = category.strip()
+        if not category:
+            raise ValueError("category must not be empty")
+        if not _DATE_RE.match(date):
+            raise ValueError(f"date must be YYYY-MM-DD, got {date!r}")
+        try:
+            _date.fromisoformat(date)
+        except ValueError:
+            raise ValueError(f"date is not a real calendar date: {date!r}") from None
+        return Expense(value, category, description, date)
diff --git a/tests/test_exporters.py b/tests/test_exporters.py
new file mode 100644
index 0000000..a05381e
--- /dev/null
+++ b/tests/test_exporters.py
@@ -0,0 +1,38 @@
+import json
+
+import pytest
+
+from expense_tracker.cli import main
+from expense_tracker.exporters import EXPORTERS
+from expense_tracker.models import Expense
+
+
+def sample():
+    return [
+        Expense(10.0, "food", "lunch", "2026-11-01"),
+        Expense(5.5, "transport", "bus", "2026-11-02"),
+    ]
+
+
+def test_registry_has_all_formats():
+    assert set(EXPORTERS) == {"csv", "json", "md"}
+
+
+def test_csv_render():
+    out = EXPORTERS["csv"].render(sample())
+    assert out.splitlines()[0] == "date,category,amount,description"
+    assert out.splitlines()[1] == "2026-11-01,food,10.0,lunch"
+
+
+def test_json_render_total():
+    assert json.loads(EXPORTERS["json"].render(sample()))["total"] == 15.5
+
+
+def test_md_render_total():
+    assert EXPORTERS["md"].render(sample()).endswith("**Total:** 15.50\n")
+
+
+def test_unknown_format_exits_nonzero(tmp_path):
+    with pytest.raises(SystemExit) as exc:
+        main(["--file", str(tmp_path / "d.json"), "export", "xml", str(tmp_path / "x")])
+    assert exc.value.code == 1
diff --git a/tests/test_mitigations.py b/tests/test_mitigations.py
new file mode 100644
index 0000000..2dced44
--- /dev/null
+++ b/tests/test_mitigations.py
@@ -0,0 +1,70 @@
+"""Regression tests for risk-register mitigations M1 (R-01) and M2 (R-02)."""
+
+import csv
+import io
+
+import pytest
+
+from expense_tracker import storage
+from expense_tracker.cli import main
+from expense_tracker.exporters import EXPORTERS
+from expense_tracker.models import Expense
+
+# ---------- M1 / R-01: input validation at the CLI boundary ----------
+
+BAD_INPUTS = [
+    ("-50", "2026-11-05"),     # negative amount
+    ("0", "2026-11-05"),       # zero amount
+    ("nan", "2026-11-05"),     # not a number
+    ("inf", "2026-11-05"),     # infinite
+    ("abc", "2026-11-05"),     # not numeric
+    ("10", "2026-13-45"),      # impossible date
+    ("10", "2026-2-30"),       # wrong format and impossible
+    ("10", "05.11.2026"),      # wrong format
+]
+
+
+@pytest.mark.parametrize("amount,date", BAD_INPUTS)
+def test_add_rejects_invalid_input_and_does_not_write(tmp_path, capsys, amount, date):
+    data = tmp_path / "e.json"
+    with pytest.raises(SystemExit) as exc:
+        main(["--file", str(data), "add", amount, "food", "x", "--date", date])
+    assert exc.value.code == 2
+    assert "error:" in capsys.readouterr().err
+    assert storage.load(data) == []          # nothing was persisted
+
+
+def test_add_rejects_empty_category(tmp_path):
+    with pytest.raises(SystemExit):
+        main(["--file", str(tmp_path / "e.json"), "add", "5", "  ", "x", "--date", "2026-11-01"])
+
+
+def test_valid_add_still_works_and_summary_survives(tmp_path, capsys):
+    data = str(tmp_path / "e.json")
+    main(["--file", data, "add", "12.50", "food", "lunch", "--date", "2026-11-01"])
+    with pytest.raises(SystemExit):  # a bad record must not break later summaries
+        main(["--file", data, "add", "10", "food", "x", "--date", "2026-13-45"])
+    main(["--file", data, "summary", "--month", "2026-11"])
+    out = capsys.readouterr().out
+    assert "TOTAL" in out and "12.50" in out
+
+
+def test_expense_create_normalises_values():
+    e = Expense.create(" 7.25 ", " food ", "taxi", "2026-11-03")
+    assert e == Expense(7.25, "food", "taxi", "2026-11-03")
+
+
+# ---------- M2 / R-02: CSV formula injection ----------
+
+@pytest.mark.parametrize("payload", ["=1+2", "+SUM(A1)", "-2+3", "@cmd", "\t=1", "\r=1"])
+def test_csv_neutralises_formula_prefixes(payload):
+    out = EXPORTERS["csv"].render([Expense(5.0, payload, payload, "2026-11-01")])
+    row = list(csv.reader(io.StringIO(out)))[1]
+    assert row[1] == "'" + payload       # category
+    assert row[3] == "'" + payload       # description
+
+
+def test_csv_leaves_normal_text_untouched():
+    out = EXPORTERS["csv"].render([Expense(5.0, "food", "dinner, with friends", "2026-11-01")])
+    row = list(csv.reader(io.StringIO(out)))[1]
+    assert row == ["2026-11-01", "food", "5.0", "dinner, with friends"]
```

# Appendix D — Check logs (verbatim)

**evidence/01_baseline_checks.txt**

```text
# Check run: baseline — 2026-11-23T00:19:08+05:00 — commit 5f85206
# Python 3.13.18, pytest 9.1.1, ruff 0.16.9, mypy 2.3.1 (compiled: yes)

$ python3 -m pytest -q

==================================== ERRORS ====================================
_____________________ ERROR collecting tests/test_basic.py _____________________
ImportError while importing test module '/home/claude/expense-tracker/tests/test_basic.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/local/lib/python3.13/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_basic.py:1: in <module>
    from expense_tracker import storage
E   ModuleNotFoundError: No module named 'expense_tracker'
=========================== short test summary info ============================
ERROR tests/test_basic.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.11s
[exit code: 2]

$ PYTHONPATH=src python3 -m pytest -q
....                                                                     [100%]
4 passed in 0.01s
[exit code: 0]

$ ruff check .
I001 [*] Import block is un-sorted or un-formatted
 --> src/expense_tracker/models.py:1:1
  |
1 | from dataclasses import dataclass, asdict
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
help: Organize imports
  |
  - from dataclasses import dataclass, asdict
1 + from dataclasses import asdict, dataclass
2 |
  |

DTZ007 Naive datetime constructed using `datetime.datetime.strptime()` without %z
  --> src/expense_tracker/report.py:8:13
   |
 6 |     result = []
 7 |     for e in expenses:
 8 |         d = datetime.strptime(e.date, "%Y-%m-%d")
   |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 9 |         if d.strftime("%Y-%m") == month:
10 |             result.append(e)
   |
help: Call `.replace(tzinfo=<timezone>)` or `.astimezone()` to convert to an aware datetime

Found 2 errors.
[*] 1 fixable with the `--fix` option.
[exit code: 1]

$ mypy src
Success: no issues found in 5 source files
[exit code: 0]

$ PYTHONPATH=src python3 -m expense_tracker --help | head -3
/usr/local/bin/python3: No module named expense_tracker.__main__; 'expense_tracker' is a package and cannot be directly executed
[exit code: 0]

$ pip wheel . --no-deps --no-build-isolation -q -w /tmp/dist_baseline && ls /tmp/dist_baseline
expense_tracker-0.1.0-py3-none-any.whl
[exit code: 0]

```

**evidence/03_mitigation_tests_before.txt**

```text
$ python3 -m pytest -q tests/test_mitigations.py   # BEFORE mitigation (commit fba7d24)
FAILED tests/test_mitigations.py::test_add_rejects_invalid_input_and_does_not_write[-50-2026-11-05]
FAILED tests/test_mitigations.py::test_add_rejects_invalid_input_and_does_not_write[0-2026-11-05]
FAILED tests/test_mitigations.py::test_add_rejects_invalid_input_and_does_not_write[nan-2026-11-05]
FAILED tests/test_mitigations.py::test_add_rejects_invalid_input_and_does_not_write[inf-2026-11-05]
FAILED tests/test_mitigations.py::test_add_rejects_invalid_input_and_does_not_write[abc-2026-11-05]
FAILED tests/test_mitigations.py::test_add_rejects_invalid_input_and_does_not_write[10-2026-13-45]
FAILED tests/test_mitigations.py::test_add_rejects_invalid_input_and_does_not_write[10-2026-2-30]
FAILED tests/test_mitigations.py::test_add_rejects_invalid_input_and_does_not_write[10-05.11.2026]
FAILED tests/test_mitigations.py::test_add_rejects_empty_category
FAILED tests/test_mitigations.py::test_valid_add_still_works_and_summary_survives
FAILED tests/test_mitigations.py::test_expense_create_normalises_values
FAILED tests/test_mitigations.py::test_csv_neutralises_formula_prefixes[=1+2]
FAILED tests/test_mitigations.py::test_csv_neutralises_formula_prefixes[+SUM(A1)]
FAILED tests/test_mitigations.py::test_csv_neutralises_formula_prefixes[-2+3]
FAILED tests/test_mitigations.py::test_csv_neutralises_formula_prefixes[@cmd]
FAILED tests/test_mitigations.py::test_csv_neutralises_formula_prefixes[\t=1]
FAILED tests/test_mitigations.py::test_csv_neutralises_formula_prefixes[\r=1]
17 failed, 1 passed in 0.09s
[exit code: 1]
```

**evidence/06_final_checks.txt**

```text
# Check run: final — 2026-11-23T00:22:38+05:00 — commit 3a7a43d
# Python 3.13.18, pytest 9.1.1, ruff 0.16.9, mypy 2.3.1 (compiled: yes)

$ python3 -m pytest -q
...........................                                              [100%]
27 passed in 0.06s
[exit code: 0]

$ PYTHONPATH=src python3 -m pytest -q
...........................                                              [100%]
27 passed in 0.05s
[exit code: 0]

$ ruff check .
All checks passed!
[exit code: 0]

$ mypy src
Success: no issues found in 7 source files
[exit code: 0]

$ PYTHONPATH=src python3 -m expense_tracker --help
usage: expense-tracker [-h] [--file FILE] {add,list,summary,export} ...

positional arguments:
  {add,list,summary,export}

options:
  -h, --help            show this help message and exit
  --file FILE
[exit code: 0]

$ pip wheel . --no-deps --no-build-isolation -q -w /tmp/dist_final && ls /tmp/dist_final
expense_tracker-0.1.0-py3-none-any.whl
[exit code: 0]

```

**evidence/04_golden_comparison.txt**

```text
$ diff -r golden_baseline golden_final   # AC1–AC3: outputs of baseline (5f85206) vs final for the same valid dataset
[exit code: 0]  (0 = byte-identical: data.json, list.txt, summary_nov.txt, summary_all.txt, out.csv, out.json, out.md)
```

**evidence/05_ac5_backward_compat.txt**

```text
$ PYTHONPATH=src python3 -m expense_tracker --file <baseline data.json created by v0.1.0> list   # AC5
1. 2026-11-01 food              10.00  lunch
2. 2026-11-02 transport          5.50  bus
3. 2026-10-30 food              20.00  dinner, with friends
[exit code: 0]
identical to baseline list.txt
```

**evidence/08_residual_legacy_bad_date.txt**

```text
$ python3 -m expense_tracker --file legacy.json summary --month 2026-11   # legacy file containing a bad date written by v0.1.0
ValueError: time data '2026-13-45' does not match format '%Y-%m-%d'
[exit code: 1]
```

