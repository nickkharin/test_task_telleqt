CSV import allows customers to upload sales orders.

Columns:

order_id
customer_id
order_date
currency
amount

Rules:

1. order_id should be unique.

2. amount should be positive.

3. Supported currencies:
USD
EUR
GBP

4. Orders older than 365 days should not be imported.

5. Import should continue even if some rows are invalid.

6. Import summary should show:

- total rows
- imported rows
- rejected rows
- total imported amount

7. Duplicate orders should not be imported.

8. Customer IDs are case insensitive.
