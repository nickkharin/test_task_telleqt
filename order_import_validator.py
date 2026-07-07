import csv
import re
from datetime import datetime
from decimal import Decimal
from pathlib import Path


SUPPORTED_CURRENCIES = {"USD", "EUR", "GBP"}


def read_csv(file_path):
    with open(file_path, newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def to_decimal(value):
    return Decimal(str(value).strip())


def to_date(value):
    return datetime.strptime(value.strip(), "%Y-%m-%d").date()


def parse_import_log(file_path):
    text = Path(file_path).read_text(encoding="utf-8", errors="replace")

    def extract_int(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return int(match.group(1)) if match else None

    def extract_decimal(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return Decimal(match.group(1)) if match else None

    return {
        "total_rows": extract_int(r"total\s+rows\s*[:=]\s*(\d+)"),
        "imported_rows": extract_int(r"imported\s+rows\s*[:=]\s*(\d+)"),
        "rejected_rows": extract_int(r"rejected\s+rows\s*[:=]\s*(\d+)"),
        "total_imported_amount": extract_decimal(
            r"imported\s+amount\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)"
        ),
    }


def get_order_id(row):
    return row["order_id"].strip()


def get_order_ids(rows):
    return [get_order_id(row) for row in rows]


def get_amount(row):
    return to_decimal(row["amount"])


def get_currency(row):
    return row["currency"].strip()


def get_order_date(row):
    return to_date(row["order_date"])


def calculate_total_amount(rows):
    return sum(get_amount(row) for row in rows)


def find_duplicate_order_ids(rows):
    seen = set()
    duplicates = set()

    for row in rows:
        order_id = get_order_id(row)

        if order_id in seen:
            duplicates.add(order_id)

        seen.add(order_id)

    return sorted(duplicates)


def classify_source_orders(source_rows, run_date):
    valid_rows = []
    rejected_rows = []
    seen_order_ids = set()

    for row in source_rows:
        order_id = get_order_id(row)
        amount = get_amount(row)
        currency = get_currency(row)
        order_date = get_order_date(row)

        rejection_reasons = []

        if order_id in seen_order_ids:
            rejection_reasons.append("duplicate_order_id")

        if amount <= Decimal("0"):
            rejection_reasons.append("non_positive_amount")

        if currency not in SUPPORTED_CURRENCIES:
            rejection_reasons.append("unsupported_currency")

        if (run_date - order_date).days > 365:
            rejection_reasons.append("older_than_365_days")

        if rejection_reasons:
            rejected_rows.append(
                {
                    "order_id": order_id,
                    "reasons": rejection_reasons,
                    "row": row,
                }
            )
        else:
            valid_rows.append(row)
            seen_order_ids.add(order_id)

    return valid_rows, rejected_rows


def find_future_dated_orders(rows, run_date):
    return [
        get_order_id(row)
        for row in rows
        if get_order_date(row) > run_date
    ]


def find_customer_id_case_conflicts(rows):
    customer_ids = {}

    for row in rows:
        original = row["customer_id"].strip()
        normalized = original.lower()
        customer_ids.setdefault(normalized, set()).add(original)

    return {
        normalized: sorted(values)
        for normalized, values in customer_ids.items()
        if len(values) > 1
    }