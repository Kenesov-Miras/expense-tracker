import math
import re
from dataclasses import asdict, dataclass
from datetime import date as _date

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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

    @staticmethod
    def create(amount: str, category: str, description: str, date: str) -> "Expense":
        """Build an Expense from raw user input, rejecting invalid values (risk R-01)."""
        try:
            value = float(amount)
        except ValueError:
            raise ValueError(f"amount must be a number, got {amount!r}") from None
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"amount must be a positive finite number, got {amount!r}")
        category = category.strip()
        if not category:
            raise ValueError("category must not be empty")
        if not _DATE_RE.match(date):
            raise ValueError(f"date must be YYYY-MM-DD, got {date!r}")
        try:
            _date.fromisoformat(date)
        except ValueError:
            raise ValueError(f"date is not a real calendar date: {date!r}") from None
        return Expense(value, category, description, date)
