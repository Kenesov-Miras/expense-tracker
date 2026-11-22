import json

import pytest

from expense_tracker.cli import main
from expense_tracker.exporters import EXPORTERS
from expense_tracker.models import Expense


def sample():
    return [
        Expense(10.0, "food", "lunch", "2026-11-01"),
        Expense(5.5, "transport", "bus", "2026-11-02"),
    ]


def test_registry_has_all_formats():
    assert set(EXPORTERS) == {"csv", "json", "md"}


def test_csv_render():
    out = EXPORTERS["csv"].render(sample())
    assert out.splitlines()[0] == "date,category,amount,description"
    assert out.splitlines()[1] == "2026-11-01,food,10.0,lunch"


def test_json_render_total():
    assert json.loads(EXPORTERS["json"].render(sample()))["total"] == 15.5


def test_md_render_total():
    assert EXPORTERS["md"].render(sample()).endswith("**Total:** 15.50\n")


def test_unknown_format_exits_nonzero(tmp_path):
    with pytest.raises(SystemExit) as exc:
        main(["--file", str(tmp_path / "d.json"), "export", "xml", str(tmp_path / "x")])
    assert exc.value.code == 1
