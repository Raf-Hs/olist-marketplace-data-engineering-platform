select
    order_id,
    order_item_id,
    customer_key,
    product_key,
    seller_key,
    purchase_date_key,
    price,
    freight_value,
    total_item_value
from {{ source('dw', 'fact_order_items') }}