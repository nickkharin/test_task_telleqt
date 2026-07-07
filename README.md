# CSV Import Validation Automation

## Purpose

This automation validates CSV import consistency between:

- `orders.csv` — source CSV file;
- `import_log.txt` — import execution log;
- `imported_orders.csv` — imported data export, simulating database state.

The solution is split into two parts:

- `order_import_validator.py` — helper functions and validation logic;
- `test_order_import_validation.py` — pytest tests.

---

## Requirements

Python 3.9+

Install project dependencies:

```bash
pip install -r requirements.txt
```

The project requires only `pytest`. All other modules used by the validation code are part of the Python standard library.

---

## QA Report

The repository includes a complete QA assessment report:

- `qa_report.pdf`

The report contains:

- requirements review (assumptions, ambiguities, questions, and risks);
- test strategy;
- imported data validation results;
- automation overview;
- bug reports;
- automation execution results;
- overall conclusions.

---

## How to Run

Run the automated validation tests:

```bash
pytest -v test_order_import_validation.py
```
---

## Expected Result

The expected test execution result for the provided data set is:

```text
7 passed, 3 failed
```

The failed tests represent confirmed defects found in the imported data and import summary.

Expected failed tests:

```text
test_rejected_rows_count_matches_expected_rejections
test_invalid_orders_are_not_imported
test_import_log_total_amount_matches_imported_data
```

---

## Defects Detected by Automation

1. The rejected rows count in the import summary is incorrect.
2. Order `1007` with `amount = 0` is imported despite the requirement that amount must be positive.
3. The total imported amount reported in the import summary does not match the actual imported data.

---

## Requirement Gaps Reported by Automation

1. Future-dated orders are accepted, but the expected behavior is not defined in the requirements.
2. Customer ID casing is inconsistent in imported data, while the requirements only state that customer IDs are case-insensitive and do not define storage normalization.
