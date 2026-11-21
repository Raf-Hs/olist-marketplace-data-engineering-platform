# Operations

## Logging

Structured logging via `src/utils/logging.py`, level controlled by `LOG_LEVEL`.

## Failure handling

- Ingestion validates schemas before writing; failures raise and halt the pipeline.
- Data quality checks raise `RuntimeError` if any fail.
- Warehouse load is transactional per table (to_sql).

## Monitoring (Azure)

Azure Monitor would collect pipeline metrics and alerts. Locally, logs are stdout.

## Backup

PostgreSQL data persists in the `postgres_data` Docker volume. Raw CSVs are the
source of truth and can regenerate all layers.
