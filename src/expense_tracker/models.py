from dataclasses import dataclass, asdict


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
