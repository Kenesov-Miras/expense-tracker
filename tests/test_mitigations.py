"""Regression tests for risk-register mitigations M1 (R-01) and M2 (R-02)."""

import csv
import io

import pytest

from expense_tracker import storage
from expense_tracker.cli import main
from expense_tracker.exporters import EXPORTERS
from expense_tracker.models import Expense

# ---------- M1 / R-01: input validation at the CLI boundary ----------

BAD_INPUTS = [
    ("-50", "2026-11-05"),     # negative amount
    ("0", "2026-11-05"),       # zero amount
    ("nan", "2026-11-05"),     # not a number
    ("inf", "2026-11-05"),     # infinite
    ("abc", "2026-11-05"),     # not numeric
    ("10", "2026-13-45"),      # impossible date
    ("10", "2026-2-30"),       # wrong format and impossible
    ("10", "05.11.2026"),      # wrong format
]


@pytest.mark.parametrize("amount,date", BAD_INPUTS)
def test_add_rejects_invalid_input_and_does_not_write(tmp_path, capsys, amount, date):
    data = tmp_path / "e.json"
    with pytest.raises(SystemExit) as exc:
        main(["--file", str(data), "add", amount, "food", "x", "--date", date])
    assert exc.value.code == 2
    assert "error:" in capsys.readouterr().err
    assert storage.load(data) == []          # nothing was persisted


def test_add_rejects_empty_category(tmp_path):
    with pytest.raises(SystemExit):
        main(["--file", str(tmp_path / "e.json"), "add", "5", "  ", "x", "--date", "2026-11-01"])


def test_valid_add_still_works_and_summary_survives(tmp_path, capsys):
    data = str(tmp_path / "e.json")
    main(["--file", data, "add", "12.50", "food", "lunch", "--date", "2026-11-01"])
    with pytest.raises(SystemExit):  # a bad record must not break later summaries
        main(["--file", data, "add", "10", "food", "x", "--date", "2026-13-45"])
    main(["--file", data, "summary", "--month", "2026-11"])
    out = capsys.readouterr().out
    assert "TOTAL" in out and "12.50" in out


def test_expense_create_normalises_values():
    e = Expense.create(" 7.25 ", " food ", "taxi", "2026-11-03")
    assert e == Expense(7.25, "food", "taxi", "2026-11-03")


# ---------- M2 / R-02: CSV formula injection ----------

@pytest.mark.parametrize("payload", ["=1+2", "+SUM(A1)", "-2+3", "@cmd", "\t=1", "\r=1"])
def test_csv_neutralises_formula_prefixes(payload):
    out = EXPORTERS["csv"].render([Expense(5.0, payload, payload, "2026-11-01")])
    row = list(csv.reader(io.StringIO(out)))[1]
    assert row[1] == "'" + payload       # category
    assert row[3] == "'" + payload       # description


def test_csv_leaves_normal_text_untouched():
    out = EXPORTERS["csv"].render([Expense(5.0, "food", "dinner, with friends", "2026-11-01")])
    row = list(csv.reader(io.StringIO(out)))[1]
    assert row == ["2026-11-01", "food", "5.0", "dinner, with friends"]
