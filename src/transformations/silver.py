"""Silver-layer transformations: standardise, clean, validate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config.paths import bronze_dir, silver_dir
from src.utils.logging import get_logger

logger = get_logger(__name__)


def _read_bronze(name: str) -> pd.DataFrame:
    path = bronze_dir() / name / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Bronze parquet not found: {path}")
    return pd.read_parquet(path)


def _write_silver(name: str, df: pd.DataFrame) -> Path:
    out_dir = silver_dir() / name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{name}.parquet"
    df.to_parquet(out_path, index=False)
    logger.info("Silver %s: %d rows -> %s", name, len(df), out_path)
    return out_path


def _strip_strings(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype("string").str.strip()
    return df


def transform_customers() -> pd.DataFrame:
    df = _read_bronze("customers").copy()
    df = _strip_strings(df)
    # dedup by primary key
    before = len(df)
    df = df.drop_duplicates(subset=["customer_id"], keep="first")
    logger.info("customers dedup: %d -> %d", before, len(df))
    return df


def transform_sellers() -> pd.DataFrame:
    df = _read_bronze("sellers").copy()
    df = _strip_strings(df)
    before = len(df)
    df = df.drop_duplicates(subset=["seller_id"], keep="first")
    logger.info("sellers dedup: %d -> %d", before, len(df))
    return df


def transform_products() -> pd.DataFrame:
    df = _read_bronze("products").copy()
    df = _strip_strings(df)
    # normalise category to lowercase-ish trim; keep nulls
    if "product_category_name" in df.columns:
        df["product_category_name"] = df["product_category_name"].astype("string").str.strip()
    before = len(df)
    df = df.drop_duplicates(subset=["product_id"], keep="first")
    logger.info("products dedup: %d -> %d", before, len(df))
    return df


def transform_category_translation() -> pd.DataFrame:
    df = _read_bronze("product_category_translation").copy()
    df = _strip_strings(df)
    return df


def transform_orders() -> pd.DataFrame:
    df = _read_bronze("orders").copy()
    df = _strip_strings(df)
    for col in [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
    # dedup by order_id (keep last completed? keep first)
    before = len(df)
    df = df.drop_duplicates(subset=["order_id"], keep="first")
    logger.info("orders dedup: %d -> %d", before, len(df))
    return df


def transform_order_items() -> pd.DataFrame:
    df = _read_bronze("order_items").copy()
    df = _strip_strings(df)
    if "shipping_limit_date" in df.columns:
        df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"], errors="coerce", utc=True)
    # ensure numeric
    for col in ["price", "freight_value"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["order_item_id"] = pd.to_numeric(df["order_item_id"], errors="coerce").astype("Int64")
    return df


def transform_order_payments() -> pd.DataFrame:
    df = _read_bronze("order_payments").copy()
    df = _strip_strings(df)
    for col in ["payment_value"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["payment_sequential"] = pd.to_numeric(df["payment_sequential"], errors="coerce").astype("Int64")
    df["payment_installments"] = pd.to_numeric(df["payment_installments"], errors="coerce").astype("Int64")
    return df


def transform_order_reviews() -> pd.DataFrame:
    df = _read_bronze("order_reviews").copy()
    df = _strip_strings(df)
    for col in ["review_creation_date", "review_answer_timestamp"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
    df["review_score"] = pd.to_numeric(df["review_score"], errors="coerce").astype("Int64")
    # dedup by review_id
    before = len(df)
    df = df.drop_duplicates(subset=["review_id"], keep="first")
    logger.info("reviews dedup: %d -> %d", before, len(df))
    return df


def transform_geolocation() -> pd.DataFrame:
    df = _read_bronze("geolocation").copy()
    # dedup identical rows
    before = len(df)
    df = df.drop_duplicates()
    logger.info("geolocation dedup: %d -> %d", before, len(df))
    # aggregate to one row per zip prefix (median lat/lng) for warehouse use
    agg = (
        df.groupby("geolocation_zip_code_prefix", as_index=False, sort=False)
        .agg(
            geolocation_lat=("geolocation_lat", "median"),
            geolocation_lng=("geolocation_lng", "median"),
            geolocation_city=("geolocation_city", "first"),
            geolocation_state=("geolocation_state", "first"),
        )
    )
    return agg


TRANSFORMS = {
    "customers": transform_customers,
    "sellers": transform_sellers,
    "products": transform_products,
    "product_category_translation": transform_category_translation,
    "orders": transform_orders,
    "order_items": transform_order_items,
    "order_payments": transform_order_payments,
    "order_reviews": transform_order_reviews,
    "geolocation": transform_geolocation,
}


def transform_all() -> dict[str, Path]:
    out = {}
    for name, fn in TRANSFORMS.items():
        df = fn()
        out[name] = _write_silver(name, df)
    return out
