# Data Dictionary

## Silver tables

Standardised versions of source tables with normalised types and deduplicated keys.
Column names match the source. Datetime columns are UTC-aware.

## Warehouse (dw schema)

### dim_date
date_key (PK), full_date, year, quarter, month, month_name, day, day_of_week,
day_name, is_weekend.

### dim_customer
customer_key (PK), customer_id (unique), customer_unique_id, customer_zip_code_prefix,
customer_city, customer_state.

### dim_seller
seller_key (PK), seller_id (unique), seller_zip_code_prefix, seller_city, seller_state.

### dim_product
product_key (PK), product_id (unique), product_category_name,
product_category_name_english, product_weight_g, product_length_cm,
product_height_cm, product_width_cm.

### fact_order_items (grain: one row per order item)
order_item_key (PK), order_id, order_item_id, customer_key (FK), product_key (FK),
seller_key (FK), purchase_date_key (FK), price, freight_value, total_item_value.

### fact_orders (grain: one row per order)
order_key (PK), order_id (unique), customer_key (FK), purchase_date_key (FK),
order_status, approved_at, delivered_customer_at, estimated_delivery_at,
delivery_days, is_late, review_score, total_payment_value, payment_type.
