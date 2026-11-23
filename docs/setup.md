# Setup

## Prerequisites

- Python 3.11+ (project targets 3.11; tested here on 3.12)
- Docker & Docker Compose (for PostgreSQL)
- Java 17 (for Spark), with `JAVA_HOME` set

## Steps

1. Create virtual environment and install dependencies:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and adjust values (default Postgres port 5434).
3. Start PostgreSQL:
   ```bash
   docker compose up -d
   ```
4. Run the pipeline:
   ```bash
   python -m src.orchestration.pipeline
   ```
5. (Optional) Warehouse load:
   ```bash
   python -c "import sys; sys.path.insert(0,'.'); from src.warehouse.load import load_warehouse; load_warehouse()"
   ```
6. (Optional) Spark analytics (requires Java 17):
   ```bash
   python -c "import sys; sys.path.insert(0,'.'); from src.spark.transformations import run_spark_analytics; print(run_spark_analytics())"
   ```
7. (Optional) dbt:
   ```bash
   cd dbt && dbt run && dbt test
   ```

## Notes

- `run_spark.py` is referenced in older docs but is not present in the repository.
- Raw CSVs are not versioned; download the Olist dataset from Kaggle into
  `data/raw/` if missing.
