# Execution

## Full pipeline (Bronze -> Silver -> Quality -> Gold)

```bash
python -m src.orchestration.pipeline
```

Steps: ingestion -> silver -> quality checks (gate) -> gold.

Note: the warehouse load is **not** part of this pipeline. Run it separately
(see below) before dbt.

## Individual steps

```bash
python -c "import sys; sys.path.insert(0,'.'); from src.ingestion.ingest import ingest_all; ingest_all()"
python -c "import sys; sys.path.insert(0,'.'); from src.transformations.silver import transform_all; transform_all()"
python -c "import sys; sys.path.insert(0,'.'); from src.quality.checks import run_basic_checks; print(run_basic_checks())"
python -c "import sys; sys.path.insert(0,'.'); from src.transformations.gold import build_gold; build_gold()"
python -c "import sys; sys.path.insert(0,'.'); from src.warehouse.load import load_warehouse; load_warehouse()"
```

## Warehouse

Requires PostgreSQL running (`docker compose up -d`):

```bash
python -c "import sys; sys.path.insert(0,'.'); from src.warehouse.load import load_warehouse; load_warehouse()"
```

## Spark

No committed entry point exists (`run_spark.py` is missing). To run the analytics,
call the module functions manually, e.g.:

```bash
python -c "import sys; sys.path.insert(0,'.'); from src.spark.transformations import run_spark_analytics; print(run_spark_analytics())"
```

Requires Java 17 and `JAVA_HOME` (see `.env.example`).

## dbt

```bash
cd dbt && dbt run && dbt test
```

## Tests

```bash
pytest -q
```
