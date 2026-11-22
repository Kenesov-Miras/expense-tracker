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
