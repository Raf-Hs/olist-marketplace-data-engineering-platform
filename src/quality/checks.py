"""Data quality check helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CheckResult:
    name: str
    passed: bool
    details: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)


def check_not_null(df: pd.DataFrame, columns: list[str]) -> CheckResult:
    failures = {}
    for c in columns:
        n = int(df[c].isna().sum()) if c in df.columns else len(df)
        if n > 0:
            failures[c] = n
    passed = not failures
    return CheckResult(
        name="not_null",
        passed=passed,
        details=f"Nulls found: {failures}" if failures else "No nulls",
        metrics={"null_counts": failures},
    )


def check_unique(df: pd.DataFrame, columns: list[str]) -> CheckResult:
    dup = int(df.duplicated(subset=columns).sum())
    passed = dup == 0
    return CheckResult(
        name="unique",
        passed=passed,
        details=f"{dup} duplicate rows on {columns}",
        metrics={"duplicate_count": dup},
    )


def check_range(df: pd.DataFrame, column: str, min_val=None, max_val=None) -> CheckResult:
    series = df[column]
    bad = 0
    if min_val is not None:
        bad += int((series < min_val).sum())
    if max_val is not None:
        bad += int((series > max_val).sum())
    passed = bad == 0
    return CheckResult(
        name=f"range_{column}",
        passed=passed,
        details=f"{bad} values out of range [{min_val}, {max_val}]",
        metrics={"out_of_range": bad},
    )


def check_referential_integrity(
    child: pd.DataFrame,
    parent: pd.DataFrame,
    fk_col: str,
    pk_col: str,
) -> CheckResult:
    missing = set(child[fk_col].dropna().unique()) - set(parent[pk_col].dropna().unique())
    passed = len(missing) == 0
    return CheckResult(
        name=f"fk_{fk_col}_to_{pk_col}",
        passed=passed,
        details=f"{len(missing)} orphan keys",
        metrics={"orphan_count": len(missing), "sample_orphans": list(missing)[:10]},
    )


def run_basic_checks() -> list[CheckResult]:
    """Run a standard suite of data quality checks on silver data."""
    import pandas as pd

    from src.config.paths import silver_dir

    results: list[CheckResult] = []

    def load(name):
        return pd.read_parquet(silver_dir() / name / f"{name}.parquet")

    customers = load("customers")
    orders = load("orders")
    order_items = load("order_items")
    products = load("products")
    sellers = load("sellers")

    results.append(check_not_null(customers, ["customer_id", "customer_unique_id"]))
    results.append(check_unique(customers, ["customer_id"]))
    results.append(check_not_null(orders, ["order_id", "customer_id", "order_status"]))
    results.append(check_unique(orders, ["order_id"]))
    results.append(check_not_null(order_items, ["order_id", "product_id", "seller_id"]))
    results.append(check_range(order_items, "price", min_val=0))
    results.append(check_range(order_items, "freight_value", min_val=0))
    results.append(check_unique(products, ["product_id"]))
    results.append(check_unique(sellers, ["seller_id"]))
    results.append(check_referential_integrity(orders, customers, "customer_id", "customer_id"))
    results.append(check_referential_integrity(order_items, orders, "order_id", "order_id"))
    results.append(check_referential_integrity(order_items, products, "product_id", "product_id"))
    results.append(check_referential_integrity(order_items, sellers, "seller_id", "seller_id"))

    for r in results:
        status = "PASS" if r.passed else "FAIL"
        logger.info("%s | %s | %s", status, r.name, r.details)
    return results
