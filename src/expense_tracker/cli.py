import argparse
import sys

from . import storage
from .exporters import EXPORTERS
from .models import Expense
from .report import filter_month, grand_total, totals_by_category


def cmd_add(args):
    try:
        expense = Expense.create(args.amount, args.category, args.description, args.date)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    expenses = storage.load(args.file)
    expenses.append(expense)
    storage.save(expenses, args.file)
    print("Added.")


def cmd_list(args):
    expenses = storage.load(args.file)
    for i, e in enumerate(expenses, 1):
        print(f"{i}. {e.date} {e.category:<12} {e.amount:>10.2f}  {e.description}")


def cmd_summary(args):
    expenses = storage.load(args.file)
    if args.month:
        expenses = filter_month(expenses, args.month)
    for cat, total in sorted(totals_by_category(expenses).items()):
        print(f"{cat:<12} {total:>10.2f}")
    print(f"{'TOTAL':<12} {grand_total(expenses):>10.2f}")


def cmd_export(args):
    exporter = EXPORTERS.get(args.format)
    if exporter is None:
        print("Unknown format: " + args.format)
        sys.exit(1)
    expenses = storage.load(args.file)
    # newline="" keeps the csv module's \r\n row endings byte-identical to the baseline
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        f.write(exporter.render(expenses))
    print(f"Exported {len(expenses)} expenses to {args.output}")


def build_parser():
    p = argparse.ArgumentParser(prog="expense-tracker")
    p.add_argument("--file", default=storage.DEFAULT_FILE)
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("add")
    a.add_argument("amount")
    a.add_argument("category")
    a.add_argument("description", nargs="?", default="")
    a.add_argument("--date", required=True)
    a.set_defaults(func=cmd_add)

    sub.add_parser("list").set_defaults(func=cmd_list)

    s = sub.add_parser("summary")
    s.add_argument("--month")
    s.set_defaults(func=cmd_summary)

    x = sub.add_parser("export")
    x.add_argument("format")
    x.add_argument("output")
    x.set_defaults(func=cmd_export)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
