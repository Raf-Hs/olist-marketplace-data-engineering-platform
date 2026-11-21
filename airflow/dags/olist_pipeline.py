"""Airflow DAG for the Olist marketplace platform (example).

This DAG is provided as a reference. Airflow is not required to run the
pipeline locally; use `python -m src.orchestration.pipeline` instead.
"""

from __future__ import annotations

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from datetime import datetime, timedelta
    AIRFLOW_AVAILABLE = True
except Exception:  # pragma: no cover
    AIRFLOW_AVAILABLE = False
    DAG = None

if AIRFLOW_AVAILABLE:
    from src.ingestion.ingest import ingest_all
    from src.transformations.silver import transform_all
    from src.quality.checks import run_basic_checks
    from src.transformations.gold import build_gold

    default_args = {
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    }

    with DAG(
        dag_id="olist_marketplace_pipeline",
        default_args=default_args,
        start_date=datetime(2026, 1, 1),
        schedule_interval="@daily",
        catchup=False,
        tags=["olist", "medallion"],
    ) as dag:
        t_ingest = PythonOperator(task_id="ingest", python_callable=ingest_all)
        t_silver = PythonOperator(task_id="silver", python_callable=transform_all)
        t_quality = PythonOperator(task_id="quality", python_callable=run_basic_checks)
        t_gold = PythonOperator(task_id="gold", python_callable=build_gold)

        t_ingest >> t_silver >> t_quality >> t_gold
