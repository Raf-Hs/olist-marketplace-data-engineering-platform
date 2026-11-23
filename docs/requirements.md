# Requirements

## Functional

- Ingest all Olist source CSVs into a Bronze layer with provenance metadata.
- Standardise and deduplicate into a Silver layer.
- Enforce data quality rules (nulls, uniqueness, ranges, referential integrity).
- Build Gold business aggregations.
- Load a star-schema warehouse into PostgreSQL.
- Provide PySpark analytics and dbt models.
- Provide an end-to-end Python pipeline and a reference Airflow DAG.

## Non-functional

- Idempotent runs (overwrite outputs).
- Reproducible local setup via Docker Compose.
- Automated tests (unit, data quality, integration).
- CI lint and test execution.
- Documentation covering architecture, data model, quality, and operations.

## Out of scope (current)

- Incremental ingestion and watermarking.
- SCD Type 2.
- Transactional multi-table warehouse loads.
- Live cloud deployment.
- Real-time streaming.
