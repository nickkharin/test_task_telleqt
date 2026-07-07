from datetime import datetime

import pytest

from order_import_validator import (
    calculate_total_amount,
    classify_source_orders,
    find_customer_id_case_conflicts,
    find_duplicate_order_ids,
    get_order_ids,
    parse_import_log,
    read_csv,
)


SOURCE_FILE = "orders.csv"
IMPORTED_FILE = "imported_orders.csv"
IMPORT_LOG_FILE = "import_log.log"

RUN_DATE = datetime.strptime("2026-07-06", "%Y-%m-%d").date()


@pytest.fixture(scope="session")
def source_rows():
    return read_csv(SOURCE_FILE)


@pytest.fixture(scope="session")
def imported_rows():
    return read_csv(IMPORTED_FILE)


@pytest.fixture(scope="session")
def import_log():
    return parse_import_log(IMPORT_LOG_FILE)


@pytest.fixture(scope="session")
def expected_valid_rows(source_rows):
    valid_rows, _ = classify_source_orders(source_rows, RUN_DATE)
    return valid_rows


@pytest.fixture(scope="session")
def expected_rejected_rows(source_rows):
    _, rejected_rows = classify_source_orders(source_rows, RUN_DATE)
    return rejected_rows


def test_total_rows_count_matches_import_log(source_rows, import_log):
    assert import_log["total_rows"] == len(source_rows), (
        f"Expected {len(source_rows)} total rows in the import log, "
        f"but found {import_log['total_rows']}."
    )


def test_imported_rows_count_matches_import_log(imported_rows, import_log):
    assert import_log["imported_rows"] == len(imported_rows), (
        f"Expected {len(imported_rows)} imported rows, "
        f"but the log reports {import_log['imported_rows']}."
    )


def test_rejected_rows_count_matches_expected_rejections(
    expected_rejected_rows,
    import_log,
):
    assert import_log["rejected_rows"] == len(expected_rejected_rows), (
        f"Expected {len(expected_rejected_rows)} rejected rows based on validation rules, "
        f"but the log reports {import_log['rejected_rows']}."
    )


def test_imported_data_does_not_contain_duplicate_order_ids(imported_rows):
    duplicate_order_ids = find_duplicate_order_ids(imported_rows)

    assert duplicate_order_ids == [], (
        f"Duplicate order IDs were found in imported data: {duplicate_order_ids}."
    )


def test_all_expected_valid_orders_are_imported(
    expected_valid_rows,
    imported_rows,
):
    expected_ids = set(get_order_ids(expected_valid_rows))
    actual_ids = set(get_order_ids(imported_rows))

    missing_ids = expected_ids - actual_ids

    assert missing_ids == set(), (
        f"Some valid orders were not imported: {sorted(missing_ids)}."
    )


def test_invalid_orders_are_not_imported(
    expected_valid_rows,
    imported_rows,
):
    expected_ids = set(get_order_ids(expected_valid_rows))
    actual_ids = set(get_order_ids(imported_rows))

    unexpected_ids = actual_ids - expected_ids

    assert unexpected_ids == set(), (
        f"Invalid orders were imported: {sorted(unexpected_ids)}."
    )


def test_imported_amount_matches_expected_amount(
    expected_valid_rows,
    imported_rows,
):
    expected_amount = calculate_total_amount(expected_valid_rows)
    actual_amount = calculate_total_amount(imported_rows)

    assert actual_amount == expected_amount, (
        f"Expected imported amount {expected_amount}, "
        f"but found {actual_amount}."
    )


def test_import_log_total_amount_matches_imported_data(
    imported_rows,
    import_log,
):
    actual_amount = calculate_total_amount(imported_rows)

    assert import_log["total_imported_amount"] == actual_amount, (
        f"Import log reports total amount {import_log['total_imported_amount']}, "
        f"but imported data contains {actual_amount}."
    )


def test_future_dated_imported_orders_are_reported_as_requirement_gap(
    source_rows,
    imported_rows,
):
    imported_ids = set(get_order_ids(imported_rows))

    future_imported_ids = [
        row["order_id"].strip()
        for row in source_rows
        if row["order_id"].strip() in imported_ids
        and row["order_date"].strip() > "2026-07-06"
    ]

    assert future_imported_ids == ["1011"], (
        f"Expected future-dated imported order ['1011'], "
        f"but found {future_imported_ids}."
    )


def test_customer_id_case_conflicts_are_reported_as_requirement_gap(imported_rows):
    conflicts = find_customer_id_case_conflicts(imported_rows)

    assert conflicts == {
        "cust009": ["CUST009", "cust009"]
    }, (
        f"Unexpected customer ID casing conflicts: {conflicts}."
    )