# Data Model

## Star schema

```mermaid
erDiagram
    dim_date ||--o{ fact_order_items : purchase_date_key
    dim_customer ||--o{ fact_order_items : customer_key
    dim_product ||--o{ fact_order_items : product_key
    dim_seller ||--o{ fact_order_items : seller_key
    dim_customer ||--o{ fact_orders : customer_key
    dim_date ||--o{ fact_orders : purchase_date_key
```

## Grain

- `fact_order_items`: one row per item within an order.
- `fact_orders`: one row per order.

## Surrogate keys

Dimensions use surrogate keys (SERIAL). Natural keys are preserved as unique columns
for traceability. Fact tables reference surrogate keys.

## Slowly Changing Dimensions

Not implemented (Type 1 overwrite). Justified: dimension attributes in this dataset
are static for the observed period.
