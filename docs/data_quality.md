# Data Quality

## Rules enforced

- Non-null primary keys.
- Unique primary keys.
- Non-negative prices and freight values.
- Referential integrity: orders.customer_id -> customers.customer_id;
  order_items.order_id -> orders.order_id; order_items.product_id -> products.product_id;
  order_items.seller_id -> sellers.seller_id.

## Deduplication decisions

- customers/sellers/products/orders: dedup by primary key, keep first occurrence.
- order_reviews: dedup by review_id.
- geolocation: dedup exact rows, then aggregate to one row per zip prefix (median lat/lng).
- No rows are silently dropped; dedup counts are logged.

## Null handling

- Nulls in optional fields (review comments, delivery dates, product dimensions) are
  preserved. Mandatory fields are validated as non-null.
- Datetime parsing uses `errors="coerce"`; invalid values become null and are logged.

## Automated checks

`src/quality/checks.py` implements 13 checks in `run_basic_checks()`;
`tests/data_quality/test_quality.py` asserts they pass. See [testing.md](testing.md).
