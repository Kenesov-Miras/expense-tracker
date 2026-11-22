# Acceptance criteria (must remain true after every change)

| ID | Criterion | How it is verified |
|---|---|---|
| AC1 | `add` then `list` preserves every field (amount, category, description, date) of a valid expense. | `tests/test_basic.py::test_save_and_load_roundtrip`, golden `list.txt` comparison |
| AC2 | `summary` (with and without `--month`) prints correct per-category totals and grand total for valid data. | `test_totals_by_category`, `test_filter_month`, `test_grand_total`, golden `summary_*.txt` |
| AC3 | `export csv|json|md` output for valid data is byte-identical to the baseline version. | golden comparison of `out.csv`, `out.json`, `out.md` (`diff -r`) + `tests/test_exporters.py` |
| AC4 | The full suite passes from a clean checkout with the documented command `python3 -m pytest -q`. | check log in `evidence/` |
| AC5 | A data file written by the baseline version (v0.1.0) loads unchanged in the new version. | golden `data.json` from baseline is reused by the final run |
