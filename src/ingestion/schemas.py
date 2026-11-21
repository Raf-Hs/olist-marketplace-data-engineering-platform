"""Expected schemas for the Olist source datasets."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class ColumnSpec:
    name: str
    dtype: str  # "string", "int", "float", "datetime", "bool"
    nullable: bool = True


@dataclass
class TableSchema:
    name: str
    file_name: str
    columns: list[ColumnSpec]
    primary_key: list[str] = field(default_factory=list)


OLIST_SCHEMAS: dict[str, TableSchema] = {
    "customers": TableSchema(
        name="customers",
        file_name="olist_customers_dataset.csv",
        columns=[
            ColumnSpec("customer_id", "string", False),
            ColumnSpec("customer_unique_id", "string", False),
            ColumnSpec("customer_zip_code_prefix", "int", False),
            ColumnSpec("customer_city", "string", False),
            ColumnSpec("customer_state", "string", False),
        ],
        primary_key=["customer_id"],
    ),
    "orders": TableSchema(
        name="orders",
        file_name="olist_orders_dataset.csv",
        columns=[
            ColumnSpec("order_id", "string", False),
            ColumnSpec("customer_id", "string", False),
            ColumnSpec("order_status", "string", False),
            ColumnSpec("order_purchase_timestamp", "datetime", False),
            ColumnSpec("order_approved_at", "datetime", True),
            ColumnSpec("order_delivered_carrier_date", "datetime", True),
            ColumnSpec("order_delivered_customer_date", "datetime", True),
            ColumnSpec("order_estimated_delivery_date", "datetime", True),
        ],
        primary_key=["order_id"],
    ),
    "order_items": TableSchema(
        name="order_items",
        file_name="olist_order_items_dataset.csv",
        columns=[
            ColumnSpec("order_id", "string", False),
            ColumnSpec("order_item_id", "int", False),
            ColumnSpec("product_id", "string", False),
            ColumnSpec("seller_id", "string", False),
            ColumnSpec("shipping_limit_date", "datetime", True),
            ColumnSpec("price", "float", False),
            ColumnSpec("freight_value", "float", False),
        ],
        primary_key=["order_id", "order_item_id"],
    ),
    "order_payments": TableSchema(
        name="order_payments",
        file_name="olist_order_payments_dataset.csv",
        columns=[
            ColumnSpec("order_id", "string", False),
            ColumnSpec("payment_sequential", "int", False),
            ColumnSpec("payment_type", "string", False),
            ColumnSpec("payment_installments", "int", False),
            ColumnSpec("payment_value", "float", False),
        ],
        primary_key=["order_id", "payment_sequential"],
    ),
    "order_reviews": TableSchema(
        name="order_reviews",
        file_name="olist_order_reviews_dataset.csv",
        columns=[
            ColumnSpec("review_id", "string", False),
            ColumnSpec("order_id", "string", False),
            ColumnSpec("review_score", "int", False),
            ColumnSpec("review_comment_title", "string", True),
            ColumnSpec("review_comment_message", "string", True),
            ColumnSpec("review_creation_date", "datetime", True),
            ColumnSpec("review_answer_timestamp", "datetime", True),
        ],
        primary_key=["review_id"],
    ),
    "products": TableSchema(
        name="products",
        file_name="olist_products_dataset.csv",
        columns=[
            ColumnSpec("product_id", "string", False),
            ColumnSpec("product_category_name", "string", True),
            ColumnSpec("product_name_lenght", "float", True),
            ColumnSpec("product_description_lenght", "float", True),
            ColumnSpec("product_photos_qty", "float", True),
            ColumnSpec("product_weight_g", "float", True),
            ColumnSpec("product_length_cm", "float", True),
            ColumnSpec("product_height_cm", "float", True),
            ColumnSpec("product_width_cm", "float", True),
        ],
        primary_key=["product_id"],
    ),
    "sellers": TableSchema(
        name="sellers",
        file_name="olist_sellers_dataset.csv",
        columns=[
            ColumnSpec("seller_id", "string", False),
            ColumnSpec("seller_zip_code_prefix", "int", False),
            ColumnSpec("seller_city", "string", False),
            ColumnSpec("seller_state", "string", False),
        ],
        primary_key=["seller_id"],
    ),
    "geolocation": TableSchema(
        name="geolocation",
        file_name="olist_geolocation_dataset.csv",
        columns=[
            ColumnSpec("geolocation_zip_code_prefix", "int", False),
            ColumnSpec("geolocation_lat", "float", False),
            ColumnSpec("geolocation_lng", "float", False),
            ColumnSpec("geolocation_city", "string", False),
            ColumnSpec("geolocation_state", "string", False),
        ],
        primary_key=[],
    ),
    "product_category_translation": TableSchema(
        name="product_category_translation",
        file_name="product_category_name_translation.csv",
        columns=[
            ColumnSpec("product_category_name", "string", False),
            ColumnSpec("product_category_name_english", "string", False),
        ],
        primary_key=["product_category_name"],
    ),
}


def validate_schema(df: pd.DataFrame, schema: TableSchema) -> list[str]:
    """Return a list of validation errors (empty if valid)."""
    errors: list[str] = []
    expected = {c.name for c in schema.columns}
    actual = set(df.columns)
    missing = expected - actual
    extra = actual - expected
    if missing:
        errors.append(f"Missing columns: {sorted(missing)}")
    if extra:
        errors.append(f"Unexpected columns: {sorted(extra)}")
    # null checks
    for col in schema.columns:
        if not col.nullable and col.name in df.columns:
            null_count = int(df[col.name].isna().sum())
            if null_count > 0:
                errors.append(f"Column '{col.name}' has {null_count} nulls but is non-nullable")
    return errors
