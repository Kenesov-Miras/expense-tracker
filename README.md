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

## For AI agents
Read [AGENTS.md](AGENTS.md) before changing anything. Acceptance criteria:
[docs/ACCEPTANCE_CRITERIA.md](docs/ACCEPTANCE_CRITERIA.md).
