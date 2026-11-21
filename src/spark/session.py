"""Spark session factory."""

from __future__ import annotations

import os

from pyspark.sql import SparkSession

from src.config.settings import get_settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


def get_spark(app_name: str = "olist-platform") -> SparkSession:
    settings = get_settings()
    if settings.java_home:
        os.environ.setdefault("JAVA_HOME", settings.java_home)
        os.environ.setdefault("PATH", settings.java_home + "/bin:" + os.environ.get("PATH", ""))
    master = settings.spark_master or "local[*]"
    spark = (
        SparkSession.builder.appName(app_name)
        .master(master)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.driver.memory", "2g")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    logger.info("Spark session created: master=%s", master)
    return spark
