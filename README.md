# Expense Tracker

A tiny command-line tool to record personal expenses and print summaries.

## Install

```
pip install -e .
```

## Usage

```
python -m expense_tracker add 12.50 food "Lunch" --date 2026-11-01
python -m expense_tracker list
python -m expense_tracker summary --month 2026-11
python -m expense_tracker export csv out.csv
```

Data is saved to `expenses.json` in the current folder.

## Tests

```
pytest
```
