# Final Engineering Assessment

## Original status
Functional end-to-end pipeline with medallion layers, warehouse, Spark, dbt, 5 tests.

## Audit findings
See ENGINEERING_AUDIT.md. Key: CI data dependency, thin test coverage, missing dbt tests, path fragility.

## Improvements implemented
- `create_schema` now resolves DDL via project root (path robust).
- Added pytest markers (`requires_data`, `integration`) and pyproject.toml.
- Data-dependent tests skip gracefully when data is absent.
- Added synthetic unit tests for quality checks.
- Added dbt schema/source tests.
- Updated CI to run unit tests by default and skip data-dependent tests.
- Added audit documents.

## Tests executed
- pytest: 7 passed (2 requires_data skipped in CI, 5 + 2 new unit).
- ruff: all checks passed.
- Full pipeline: RC=0.
- dbt run: OK.

## Remaining technical debt
- CI does not execute data-dependent tests (data not committed).
- Warehouse load not transactional.
- load_fact_orders slow (~2 min) due to mode aggregation.
- No incremental ingestion.

## Production-readiness limitations
- Local-only infrastructure; Azure not implemented.
- No alerting/monitoring beyond logs.
- No SCD Type 2.

## Recommended next milestones
1. Add committed sample dataset for CI integration tests.
2. Transactional warehouse loads.
3. Incremental ingestion with watermarking.
4. Azure implementation (when authorized).