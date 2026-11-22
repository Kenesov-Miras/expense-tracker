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
