# Learning Guide

This guide helps a junior Data Engineer reproduce each component independently.

## 1. Ingestion (`src/ingestion/`)

- **What**: reads source CSVs, validates schemas, writes Bronze Parquet + metadata.
- **Why**: preserve raw data with provenance; fail fast on schema drift.
- **How**: `schemas.py` defines expected columns/types; `ingest.py` reads, validates,
  hashes source file, writes Parquet.
- **Inputs**: CSVs in `data/raw/`. **Outputs**: `data/bronze/<table>/*.parquet`.
- **Run**: `python -c "from src.ingestion.ingest import ingest_all; ingest_all()"`.
- **Test**: `pytest tests/unit/test_schemas.py`.
- **Failures**: missing file, schema mismatch, null in non-nullable column.

## 2. Silver (`src/transformations/silver.py`)

- **What**: standardises types, dedups, aggregates geolocation.
- **Why**: produce clean, analysis-ready datasets.
- **How**: per-table transform functions; writes Parquet.
- **Run**: `from src.transformations.silver import transform_all`.

## 3. Data Quality (`src/quality/checks.py`)

- **What**: null, uniqueness, range, referential integrity checks.
- **Why**: catch data issues before analytics.
- **Run**: `run_basic_checks()`.

## 4. Gold (`src/transformations/gold.py`)

- **What**: business aggregations (revenue, categories, sellers, delivery, payments).
- **Why**: answer business questions directly.

## 5. Warehouse (`src/warehouse/load.py`)

- **What**: loads star schema into PostgreSQL.
- **Why**: optimised analytical queries.
- **Run**: requires running Postgres (docker compose).

## 6. Spark (`src/spark/`)

- **What**: PySpark session + distributed transformations.
- **Why**: demonstrate distributed processing, joins, aggregations, Parquet I/O.
- **Prereq**: Java 17, JAVA_HOME set.

## 7. dbt (`dbt/`)

- **What**: SQL models on top of warehouse.
- **Why**: version-controlled transformations with tests.

## 8. Orchestration (`src/orchestration/pipeline.py`)

- **What**: end-to-end runner with quality gate.

## Concepts to reproduce

Python, pandas, Parquet, SQL, PostgreSQL, Docker, PySpark, dbt, pytest.
