import json
import os

from .models import Expense

DEFAULT_FILE = "expenses.json"


def load(path=DEFAULT_FILE):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Expense.from_dict(item) for item in data]


def save(expenses, path=DEFAULT_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump([e.to_dict() for e in expenses], f, indent=2)
