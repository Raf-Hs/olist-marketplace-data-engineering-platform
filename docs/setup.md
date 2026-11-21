# Setup

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Java 17 (for Spark)

## Steps

1. Create virtual environment and install dependencies.
2. Copy `.env.example` to `.env` and adjust values (default port 5434).
3. Start PostgreSQL: `docker compose up -d`.
4. Run the pipeline: `python -m src.orchestration.pipeline`.
5. (Optional) Spark analytics: `python run_spark.py` (set JAVA_HOME).
6. (Optional) dbt: `cd dbt && dbt run`.
