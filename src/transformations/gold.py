"""Gold-layer business-ready aggregations (pandas)."""

from __future__ import annotations

import pandas as pd

from src.config.paths import gold_dir, silver_dir
from src.utils.logging import get_logger

logger = get_logger(__name__)


def _silver(name: str) -> pd.DataFrame:
    return pd.read_parquet(silver_dir() / name / f"{name}.parquet")


def _write(name: str, df: pd.DataFrame) -> None:
    out_dir = gold_dir() / name
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_dir / f"{name}.parquet", index=False)
    logger.info("Gold %s: %d rows", name, len(df))


def gold_revenue_overview() -> pd.DataFrame:
    items = _silver("order_items")
    orders = _silver("orders")
    items = items.merge(
        orders[["order_id", "order_purchase_timestamp", "order_status"]], on="order_id", how="left"
    )
    items["order_purchase_timestamp"] = pd.to_datetime(items["order_purchase_timestamp"], utc=True)
    items["total_item_value"] = items["price"] + items["freight_value"]
    # monthly revenue
    monthly = (
        items.assign(month=items["order_purchase_timestamp"].dt.to_period("M").astype(str))
        .groupby("month", as_index=False)
        .agg(
            revenue=("total_item_value", "sum"),
            orders=("order_id", "nunique"),
            items=("order_id", "size"),
        )
    )
    monthly["revenue"] = monthly["revenue"].round(2)
    _write("gold_monthly_revenue", monthly)
    return monthly


def gold_category_performance() -> pd.DataFrame:
    items = _silver("order_items")
    products = _silver("products")
    trans = _silver("product_category_translation")
    products = products.merge(trans, on="product_category_name", how="left")
    df = items.merge(
        products[["product_id", "product_category_name", "product_category_name_english"]],
        on="product_id",
        how="left",
    )
    df["total_item_value"] = df["price"] + df["freight_value"]
    cat = (
        df.groupby("product_category_name_english", as_index=False)
        .agg(
            revenue=("total_item_value", "sum"),
            items_sold=("product_id", "size"),
            orders=("order_id", "nunique"),
        )
        .sort_values("revenue", ascending=False)
    )
    cat["revenue"] = cat["revenue"].round(2)
    _write("gold_category_performance", cat)
    return cat


def gold_seller_performance() -> pd.DataFrame:
    items = _silver("order_items")
    sellers = _silver("sellers")
    df = items.merge(sellers, on="seller_id", how="left")
    df["total_item_value"] = df["price"] + df["freight_value"]
    sel = (
        df.groupby(["seller_id", "seller_city", "seller_state"], as_index=False)
        .agg(
            revenue=("total_item_value", "sum"),
            items_sold=("product_id", "size"),
            orders=("order_id", "nunique"),
        )
        .sort_values("revenue", ascending=False)
    )
    sel["revenue"] = sel["revenue"].round(2)
    _write("gold_seller_performance", sel)
    return sel


def gold_delivery_performance() -> pd.DataFrame:
    orders = _silver("orders").copy()
    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"], utc=True
    )
    orders["order_delivered_customer_date"] = pd.to_datetime(
        orders["order_delivered_customer_date"], utc=True
    )
    orders["order_estimated_delivery_date"] = pd.to_datetime(
        orders["order_estimated_delivery_date"], utc=True
    )
    orders["delivery_days"] = (
        orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]
    ).dt.days
    orders["is_late"] = (
        orders["order_delivered_customer_date"] > orders["order_estimated_delivery_date"]
    )
    delivered = orders[orders["order_status"] == "delivered"]
    agg = pd.DataFrame(
        {
            "total_orders": [len(orders)],
            "delivered_orders": [len(delivered)],
            "canceled_orders": [int((orders["order_status"] == "canceled").sum())],
            "avg_delivery_days": [round(delivered["delivery_days"].mean(), 2)],
            "late_delivery_pct": [round(delivered["is_late"].mean() * 100, 2)],
        }
    )
    _write("gold_delivery_kpis", agg)
    return agg


def gold_payment_behavior() -> pd.DataFrame:
    payments = _silver("order_payments")
    agg = payments.groupby("payment_type", as_index=False).agg(
        transactions=("order_id", "size"),
        total_value=("payment_value", "sum"),
        avg_installments=("payment_installments", "mean"),
    )
    agg["total_value"] = agg["total_value"].round(2)
    agg["avg_installments"] = agg["avg_installments"].round(2)
    _write("gold_payment_behavior", agg)
    return agg


def gold_review_delivery() -> pd.DataFrame:
    orders = _silver("orders").copy()
    reviews = _silver("order_reviews").copy()
    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"], utc=True
    )
    orders["order_delivered_customer_date"] = pd.to_datetime(
        orders["order_delivered_customer_date"], utc=True
    )
    orders["delivery_days"] = (
        orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]
    ).dt.days
    df = reviews.merge(orders[["order_id", "delivery_days"]], on="order_id", how="left")
    agg = df.groupby("review_score", as_index=False).agg(
        avg_delivery_days=("delivery_days", "mean"), orders=("order_id", "size")
    )
    agg["avg_delivery_days"] = agg["avg_delivery_days"].round(2)
    _write("gold_review_delivery", agg)
    return agg


def build_gold() -> None:
    gold_revenue_overview()
    gold_category_performance()
    gold_seller_performance()
    gold_delivery_performance()
    gold_payment_behavior()
    gold_review_delivery()
    logger.info("Gold layer build complete.")
