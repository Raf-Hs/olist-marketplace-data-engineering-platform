# Implementation Inventory

Audit date: 2026-11-23 (local working tree).

## Implemented and verified in this environment

| Component | Location | Evidence |
|---|---|---|
| Ingestion + schemas | `src/ingestion/` | `OLIST_SCHEMAS` (9 tables), `validate_schema`, `ingest_all` |
| Bronze layer | `data/bronze/` | 9 directories, parquet + `metadata.json` (hash, row count, timestamp) |
| Silver transforms | `src/transformations/silver.py` | 9 transform functions, dedup logging, geolocation aggregation |
| Silver outputs | `data/silver/` | 9 parquet datasets (verified row counts) |
| Quality checks | `src/quality/checks.py` | 13 checks in `run_basic_checks` |
| Quality tests | `tests/data_quality/test_quality.py`, `tests/unit/test_quality_checks.py` | Passing locally (data present) |
| Gold aggregations (pandas) | `src/transformations/gold.py` | 6 functions, outputs in `data/gold/` |
| Spark transformations | `src/spark/` | session + analytics; output parquet present |
| Warehouse schema | `infra/postgres/init/01_schema.sql` | 6 tables (4 dims, 2 facts) |
| Warehouse loader | `src/warehouse/load.py` | create schema, truncate, load all tables |
| dbt project | `dbt/` | 2 models, sources + schema tests |
| Orchestration | `src/orchestration/pipeline.py` | ingestion -> silver -> quality gate -> gold |
| Airflow DAG (reference) | `airflow/dags/olist_pipeline.py` | 4 tasks, dependency chain |
| CI | `.github/workflows/ci.yml` | lint + unit + conditional data tests |
| Config/paths/logging | `src/config/`, `src/utils/logging.py` | env-based settings, centralised paths |
| Tests | `tests/` | 11 tests (10 pass without Postgres) |
| Documentation | `docs/` | architecture, data model, quality, etc. |

## Partially implemented or unverified here

- **Warehouse load**: code present but Postgres was not running in this environment;
  row counts are taken from `docs/audits/DATA_WAREHOUSE_AUDIT.md` (audited, not
  re-verified here).
- **Spark entry point**: no `run_spark.py` or `__main__` block in
  `src/spark/transformations.py`; invocation is manual. Output parquet exists,
  indicating the analytics ran at least once.
- **Python version**: project targets 3.11 (`pyproject.toml`); this environment
  runs 3.12. Unit tests pass under 3.12; 3.11 execution is not verified here.
- **dbt coverage**: only 2 models (`stg_fact_order_items`, `mart_revenue_by_month`)
  on top of the warehouse; limited mart coverage.
- **Monitoring/alerting**: design only (Azure). Local execution logs to stdout.
- **Geolocation city/state**: uses `first` after grouping (not mode); documented
  as a known simplification.

## Missing

- `run_spark.py` (referenced by README/setup/execution docs).
- Warehouse load step in the main Python pipeline (`run_pipeline` stops at Gold).
- Transactional multi-table warehouse loads.
- Incremental ingestion / watermarking.
- SCD Type 2.
- Committed sample dataset for CI integration tests.
- `LICENSE` file.
- `CONTRIBUTING.md`.

## Proposed documentation structure (implemented)

```text
docs/
  README.md                 # documentation index
  business_context.md
  requirements.md
  architecture.md
  data_model.md
  data_dictionary.md
  data_sources.md
  data_quality.md
  execution.md
  testing.md
  operations.md
  technical_decisions.md
  azure_architecture.md
  implementation_inventory.md
  documentation_gaps.md
  limitations.md
  LEARNING_GUIDE.md
  audits/
  assets/
```

## Claims requiring verification

- Data warehouse row counts and referential integrity (audit report, not re-run here).
- "CI run 44949485794 failed" historical claim in `docs/audits/ENGINEERING_AUDIT.md`.
- "ruff: all checks passed" (ruff not invoked in this environment).
- Spark output generation path (no entry point in repository).
- `.env` password differs from `.env.example` placeholder (expected for local dev).
