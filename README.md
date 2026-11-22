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
