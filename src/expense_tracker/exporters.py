"""Export formats (Strategy pattern).

Each exporter turns a list of expenses into the text of one output file.
Exporters are pure (no file I/O), so they can be unit-tested directly;
the CLI only picks a strategy from ``EXPORTERS`` and writes the result.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Protocol

from .models import Expense
from .report import grand_total


class Exporter(Protocol):
    def render(self, expenses: list[Expense]) -> str: ...


# Cells starting with these characters are interpreted as formulas by
# Excel / LibreOffice / Google Sheets (OWASP "CSV Injection").
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _safe_cell(text: str) -> str:
    """Neutralise spreadsheet formulas in user-controlled text (risk R-02)."""
    return "'" + text if text.startswith(_FORMULA_PREFIXES) else text


class CsvExporter:
    def render(self, expenses: list[Expense]) -> str:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["date", "category", "amount", "description"])
        for e in expenses:
            writer.writerow([e.date, _safe_cell(e.category), e.amount, _safe_cell(e.description)])
        return buf.getvalue()


class JsonExporter:
    def render(self, expenses: list[Expense]) -> str:
        payload = {"expenses": [e.to_dict() for e in expenses], "total": grand_total(expenses)}
        return json.dumps(payload, indent=2)


class MarkdownExporter:
    def render(self, expenses: list[Expense]) -> str:
        lines = ["| date | category | amount | description |", "|---|---|---|---|"]
        for e in expenses:
            lines.append(f"| {e.date} | {e.category} | {e.amount:.2f} | {e.description} |")
        return "\n".join(lines) + f"\n\n**Total:** {grand_total(expenses):.2f}\n"


EXPORTERS: dict[str, Exporter] = {
    "csv": CsvExporter(),
    "json": JsonExporter(),
    "md": MarkdownExporter(),
}
