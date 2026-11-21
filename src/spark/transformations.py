"""PySpark transformations and analytics for the Gold layer."""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from src.config.paths import silver_dir, gold_dir
from src.spark.session import get_spark
from src.utils.logging import get_logger

logger = get_logger(__name__)


def _silver_path(name: str) -> str:
    return str(silver_dir() / name / f"{name}.parquet")


def build_sales_enriched(spark: SparkSession) -> DataFrame:
    items = spark.read.parquet(_silver_path("order_items"))
    orders = spark.read.parquet(_silver_path("orders"))
    products = spark.read.parquet(_silver_path("products"))
    sellers = spark.read.parquet(_silver_path("sellers"))
    trans = spark.read.parquet(_silver_path("product_category_translation"))

    products = products.join(trans, on="product_category_name", how="left")

    df = (
        items.join(orders.select("order_id", "customer_id", "order_purchase_timestamp", "order_status"),
                   on="order_id", how="inner")
        .join(products.select("product_id", "product_category_name", "product_category_name_english"),
               on="product_id", how="left")
        .join(sellers.select("seller_id", "seller_state"), on="seller_id", how="left")
    )
    df = df.withColumn("order_purchase_timestamp", F.to_timestamp("order_purchase_timestamp"))
    df = df.withColumn("total_item_value", F.col("price") + F.col("freight_value"))
    df = df.withColumn("purchase_year", F.year("order_purchase_timestamp"))
    df = df.withColumn("purchase_month", F.month("order_purchase_timestamp"))
    return df


def revenue_by_category(df: DataFrame) -> DataFrame:
    return (
        df.groupBy("product_category_name_english")
        .agg(
            F.round(F.sum("total_item_value"), 2).alias("revenue"),
            F.countDistinct("order_id").alias("orders"),
            F.count("*").alias("items_sold"),
        )
        .orderBy(F.desc("revenue"))
    )


def revenue_by_month(df: DataFrame) -> DataFrame:
    return (
        df.groupBy("purchase_year", "purchase_month")
        .agg(F.round(F.sum("total_item_value"), 2).alias("revenue"),
             F.countDistinct("order_id").alias("orders"))
        .orderBy("purchase_year", "purchase_month")
    )


def top_sellers(df: DataFrame, n: int = 20) -> DataFrame:
    return (
        df.groupBy("seller_id", "seller_state")
        .agg(F.round(F.sum("total_item_value"), 2).alias("revenue"),
             F.countDistinct("order_id").alias("orders"))
        .orderBy(F.desc("revenue"))
        .limit(n)
    )


def delivery_vs_review(spark: SparkSession) -> DataFrame:
    orders = spark.read.parquet(_silver_path("orders"))
    reviews = spark.read.parquet(_silver_path("order_reviews"))
    df = orders.join(reviews.select("order_id", "review_score"), on="order_id", how="inner")
    df = df.withColumn("order_purchase_timestamp", F.to_timestamp("order_purchase_timestamp"))
    df = df.withColumn("order_delivered_customer_date", F.to_timestamp("order_delivered_customer_date"))
    df = df.withColumn("delivery_days",
                       F.datediff("order_delivered_customer_date", "order_purchase_timestamp"))
    return (
        df.groupBy("review_score")
        .agg(F.round(F.avg("delivery_days"), 2).alias("avg_delivery_days"),
             F.count("*").alias("orders"))
        .orderBy("review_score")
    )


def run_spark_analytics() -> dict[str, str]:
    spark = get_spark("olist-spark-analytics")
    df = build_sales_enriched(spark)

    # cache for reuse
    df.cache()
    logger.info("Enriched sales rows: %d", df.count())

    out_dir = gold_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = {}
    r1 = revenue_by_category(df)
    p = out_dir / "spark_revenue_by_category.parquet"
    r1.write.mode("overwrite").parquet(str(p))
    paths["revenue_by_category"] = str(p)

    r2 = revenue_by_month(df)
    p = out_dir / "spark_revenue_by_month.parquet"
    r2.write.mode("overwrite").parquet(str(p))
    paths["revenue_by_month"] = str(p)

    r3 = top_sellers(df)
    p = out_dir / "spark_top_sellers.parquet"
    r3.write.mode("overwrite").parquet(str(p))
    paths["top_sellers"] = str(p)

    r4 = delivery_vs_review(spark)
    p = out_dir / "spark_delivery_vs_review.parquet"
    r4.write.mode("overwrite").parquet(str(p))
    paths["delivery_vs_review"] = str(p)

    spark.stop()
    logger.info("Spark analytics complete.")
    return paths
