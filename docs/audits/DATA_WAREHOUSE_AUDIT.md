# Data Warehouse Audit

## Grain
- `fact_order_items`: one row per order item (112,650 rows) - correct.
- `fact_orders`: one row per order (99,441 rows) - correct.

## Referential integrity (verified)
- orders.customer_id -> customers: 0 orphans.
- order_items.order_id -> orders: 0 orphans.
- order_items.product_id -> products: 0 orphans.
- order_items.seller_id -> sellers: 0 orphans.
- fact_order_items customer/product/seller/date keys: populated.

## Row counts
dim_date=774, dim_customer=99,441, dim_seller=3,095, dim_product=32,951,
fact_order_items=112,650, fact_orders=99,441.

## Duplicate business records
- No duplicate order_id in fact_orders (unique constraint).
- No duplicate PKs in dimensions.

## Null foreign keys
- fact_orders.customer_key: 0 nulls (verified).
- fact_order_items keys: 0 nulls (verified).

## Date dimension coverage
- 774 days covering order purchase range. No gaps.

## Revenue
- fact_order_items.total_item_value = price + freight_value.
- Sum matches Gold monthly revenue (verified).

## Risks
- Warehouse load truncates and reloads (not transactional across tables).
- `approved_at`/delivered timestamps coerced; invalid become null.