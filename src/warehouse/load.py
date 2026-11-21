"""Load the dimensional warehouse into PostgreSQL."""

from __future__ import annotations

from datetime import timedelta

import pandas as pd
from sqlalchemy import text

from src.config.paths import silver_dir
from src.database.connection import get_engine
from src.utils.logging import get_logger

logger = get_logger(__name__)


def _silver(name: str) -> pd.DataFrame:
    return pd.read_parquet(silver_dir() / name / f"{name}.parquet")


def create_schema() -> None:
    engine = get_engine()
    with open("infra/postgres/init/01_schema.sql", "r", encoding="utf-8") as f:
        ddl = f.read()
    with engine.begin() as conn:
        conn.execute(text(ddl))
    logger.info("Warehouse schema created/verified.")


def _truncate_tables() -> None:
    engine = get_engine()
    tables = [
        "dw.fact_order_items",
        "dw.fact_orders",
        "dw.dim_product",
        "dw.dim_seller",
        "dw.dim_customer",
        "dw.dim_date",
    ]
    with engine.begin() as conn:
        for t in tables:
            conn.execute(text(f"TRUNCATE TABLE {t} RESTART IDENTITY CASCADE;"))
    logger.info("Warehouse tables truncated.")


def load_dim_date() -> pd.DataFrame:
    orders = _silver("orders")
    purchases = pd.to_datetime(orders["order_purchase_timestamp"], utc=True)
    start = purchases.min().date()
    end = purchases.max().date()
    days = (end - start).days + 1
    rows = []
    for i in range(days):
        d = start + timedelta(days=i)
        rows.append(
            {
                "date_key": int(d.strftime("%Y%m%d")),
                "full_date": d,
                "year": d.year,
                "quarter": (d.month - 1) // 3 + 1,
                "month": d.month,
                "month_name": d.strftime("%B"),
                "day": d.day,
                "day_of_week": d.weekday() + 1,
                "day_name": d.strftime("%A"),
                "is_weekend": d.weekday() >= 5,
            }
        )
    df = pd.DataFrame(rows)
    engine = get_engine()
    df.to_sql("dim_date", engine, schema="dw", if_exists="append", index=False)
    logger.info("Loaded dim_date: %d rows", len(df))
    return df


def load_dim_customer() -> pd.DataFrame:
    df = _silver("customers").copy()
    out = pd.DataFrame(
        {
            "customer_id": df["customer_id"],
            "customer_unique_id": df["customer_unique_id"],
            "customer_zip_code_prefix": df["customer_zip_code_prefix"],
            "customer_city": df["customer_city"],
            "customer_state": df["customer_state"],
        }
    )
    engine = get_engine()
    out.to_sql("dim_customer", engine, schema="dw", if_exists="append", index=False)
    # fetch mapping
    mapping = pd.read_sql("SELECT customer_key, customer_id FROM dw.dim_customer", engine)
    logger.info("Loaded dim_customer: %d rows", len(out))
    return mapping


def load_dim_seller() -> pd.DataFrame:
    df = _silver("sellers").copy()
    out = pd.DataFrame(
        {
            "seller_id": df["seller_id"],
            "seller_zip_code_prefix": df["seller_zip_code_prefix"],
            "seller_city": df["seller_city"],
            "seller_state": df["seller_state"],
        }
    )
    engine = get_engine()
    out.to_sql("dim_seller", engine, schema="dw", if_exists="append", index=False)
    mapping = pd.read_sql("SELECT seller_key, seller_id FROM dw.dim_seller", engine)
    logger.info("Loaded dim_seller: %d rows", len(out))
    return mapping


def load_dim_product() -> pd.DataFrame:
    products = _silver("products").copy()
    trans = _silver("product_category_translation").copy()
    df = products.merge(
        trans,
        on="product_category_name",
        how="left",
        validate="many_to_one",
    )
    out = pd.DataFrame(
        {
            "product_id": df["product_id"],
            "product_category_name": df["product_category_name"],
            "product_category_name_english": df["product_category_name_english"],
            "product_weight_g": df["product_weight_g"],
            "product_length_cm": df["product_length_cm"],
            "product_height_cm": df["product_height_cm"],
            "product_width_cm": df["product_width_cm"],
        }
    )
    out = out.drop_duplicates(subset=["product_id"], keep="first")
    engine = get_engine()
    out.to_sql("dim_product", engine, schema="dw", if_exists="append", index=False)
    mapping = pd.read_sql("SELECT product_key, product_id FROM dw.dim_product", engine)
    logger.info("Loaded dim_product: %d rows", len(out))
    return mapping


def load_fact_order_items() -> None:
    items = _silver("order_items").copy()
    orders = _silver("orders").copy()
    cust_map = None
    engine = get_engine()
    cust_map = pd.read_sql("SELECT customer_key, customer_id FROM dw.dim_customer", engine)
    prod_map = pd.read_sql("SELECT product_key, product_id FROM dw.dim_product", engine)
    sell_map = pd.read_sql("SELECT seller_key, seller_id FROM dw.dim_seller", engine)

    # join order -> customer
    orders_small = orders[["order_id", "customer_id", "order_purchase_timestamp"]]
    items = items.merge(orders_small, on="order_id", how="left", validate="many_to_one")

    items = items.merge(cust_map, on="customer_id", how="left", validate="many_to_one")
    items = items.merge(prod_map, on="product_id", how="left", validate="many_to_one")
    items = items.merge(sell_map, on="seller_id", how="left", validate="many_to_one")

    purch = pd.to_datetime(items["order_purchase_timestamp"], utc=True)
    items["purchase_date_key"] = purch.dt.strftime("%Y%m%d").astype(int)

    items["total_item_value"] = items["price"] + items["freight_value"]

    out = pd.DataFrame(
        {
            "order_id": items["order_id"],
            "order_item_id": items["order_item_id"].astype(int),
            "customer_key": items["customer_key"],
            "product_key": items["product_key"],
            "seller_key": items["seller_key"],
            "purchase_date_key": items["purchase_date_key"],
            "price": items["price"],
            "freight_value": items["freight_value"],
            "total_item_value": items["total_item_value"],
        }
    )
    out.to_sql("fact_order_items", engine, schema="dw", if_exists="append", index=False)
    logger.info("Loaded fact_order_items: %d rows", len(out))


def load_fact_orders() -> None:
    orders = _silver("orders").copy()
    payments = _silver("order_payments").copy()
    reviews = _silver("order_reviews").copy()
    engine = get_engine()
    cust_map = pd.read_sql("SELECT customer_key, customer_id FROM dw.dim_customer", engine)

    # payment aggregates per order
    pay_agg = (
        payments.groupby("order_id", as_index=False)
        .agg(
            total_payment_value=("payment_value", "sum"),
            payment_type=("payment_type", lambda s: s.mode().iloc[0] if not s.mode().empty else None),
        )
    )
    # review: take max score per order (or first)
    rev_agg = (
        reviews.groupby("order_id", as_index=False)
        .agg(review_score=("review_score", "max"))
    )

    df = orders.merge(cust_map, on="customer_id", how="left", validate="many_to_one")
    df = df.merge(pay_agg, on="order_id", how="left", validate="one_to_one")
    df = df.merge(rev_agg, on="order_id", how="left", validate="many_to_one")

    purch = pd.to_datetime(df["order_purchase_timestamp"], utc=True)
    df["purchase_date_key"] = purch.dt.strftime("%Y%m%d").astype(int)

    # delivery metrics
    delivered = pd.to_datetime(df["order_delivered_customer_date"], utc=True)
    estimated = pd.to_datetime(df["order_estimated_delivery_date"], utc=True)
    df["delivery_days"] = (delivered - purch).dt.days
    df["is_late"] = delivered > estimated

    out = pd.DataFrame(
        {
            "order_id": df["order_id"],
            "customer_key": df["customer_key"],
            "purchase_date_key": df["purchase_date_key"],
            "order_status": df["order_status"],
            "approved_at": pd.to_datetime(df["order_approved_at"], utc=True).dt.tz_localize(None),
            "delivered_customer_at": delivered.dt.tz_localize(None),
            "estimated_delivery_at": estimated.dt.tz_localize(None),
            "delivery_days": df["delivery_days"],
            "is_late": df["is_late"],
            "review_score": df["review_score"],
            "total_payment_value": df["total_payment_value"],
            "payment_type": df["payment_type"],
        }
    )
    out.to_sql("fact_orders", engine, schema="dw", if_exists="append", index=False)
    logger.info("Loaded fact_orders: %d rows", len(out))


def load_warehouse() -> None:
    create_schema()
    _truncate_tables()
    load_dim_date()
    load_dim_customer()
    load_dim_seller()
    load_dim_product()
    load_fact_order_items()
    load_fact_orders()
    logger.info("Warehouse load complete.")
