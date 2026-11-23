# Limitations and Open Questions

## Known limitations

- Azure components are documented as architecture only; no paid resources created.
- Airflow DAG is reference-only; local execution uses the Python pipeline.
- Dataset is loaded from local CSVs (Kaggle download required for fresh data).
- Warehouse load is a separate manual step; it is not part of `run_pipeline`.
- Spark has no committed entry point (`run_spark.py` is missing).
- No incremental ingestion; all runs overwrite.
- No SCD Type 2; dimensions are Type 1 overwrite.
- Warehouse loads are not transactional across tables.
- `load_fact_orders` payment_type aggregation uses a slow mode lambda.
- Geolocation city/state uses `first`, not mode.
- Monitoring is stdout logs only.
- No LICENSE file.

## Open questions

- Which entry point produced the existing Spark parquet outputs?
- Were the audited warehouse row counts reproduced after the latest code change?
  (Postgres not available in this environment.)
- Is Python 3.11 still the intended runtime, or should support be declared as 3.11+?
- Should `data/samples/sample_order.json` be wired into any module or removed?
- Should warehouse load be integrated into the main pipeline?
