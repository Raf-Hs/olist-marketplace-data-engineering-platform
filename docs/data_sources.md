# Data Sources

Source: Brazilian E-Commerce Public Dataset by Olist (Kaggle).

Files ingested:

| File | Table | Rows |
|---|---|---|
| olist_customers_dataset.csv | customers | 99,441 |
| olist_orders_dataset.csv | orders | 99,441 |
| olist_order_items_dataset.csv | order_items | 112,650 |
| olist_order_payments_dataset.csv | order_payments | 103,886 |
| olist_order_reviews_dataset.csv | order_reviews | 99,224 |
| olist_products_dataset.csv | products | 32,951 |
| olist_sellers_dataset.csv | sellers | 3,095 |
| olist_geolocation_dataset.csv | geolocation | 1,000,163 |
| product_category_name_translation.csv | product_category_translation | 71 |

## Provenance

Each Bronze table stores a `metadata.json` with source file name, row count,
SHA-256 hash of the source CSV, and ingestion timestamp (UTC).
