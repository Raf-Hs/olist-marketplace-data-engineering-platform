# Execution

## Full pipeline

```bash
python -m src.orchestration.pipeline
```

Steps: ingestion -> silver -> quality checks -> gold.

## Individual steps

```bash
python -c "import sys; sys.path.insert(0,'.'); from src.ingestion.ingest import ingest_all; ingest_all()"
python -c "import sys; sys.path.insert(0,'.'); from src.transformations.silver import transform_all; transform_all()"
python -c "import sys; sys.path.insert(0,'.'); from src.quality.checks import run_basic_checks; print(run_basic_checks())"
python -c "import sys; sys.path.insert(0,'.'); from src.transformations.gold import build_gold; build_gold()"
python -c "import sys; sys.path.insert(0,'.'); from src.warehouse.load import load_warehouse; load_warehouse()"
```

## Spark

```bash
JAVA_HOME=/home/rafa/.local/jdk/jdk-17.0.13+11 python run_spark.py
```

## dbt

```bash
cd dbt && dbt run && dbt test
```

## Tests

```bash
pytest -q
```
