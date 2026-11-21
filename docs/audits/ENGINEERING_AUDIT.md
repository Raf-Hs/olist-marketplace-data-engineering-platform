# Engineering Audit

## Scope
Audit of `olist-marketplace-data-engineering-platform` (commit 39107df).

## Findings

### Critical
1. **CI data dependency**: Raw and Silver data are gitignored, so data-dependent
   tests (`test_orders_schema_valid`, `test_basic_quality_checks_pass`) fail in CI.
   CI run 44949485794 failed with `FileNotFoundError` on silver parquet.
2. **No CI data bootstrap**: The workflow installs dependencies and runs pytest
   without providing source data.

### High
3. **`create_schema` path fragility**: reads `infra/postgres/init/01_schema.sql`
   relative to CWD; fails if invoked from another directory.
4. **Insufficient test coverage**: only 5 tests; no business-rule, warehouse-integrity,
   idempotency, or failure-scenario tests.
5. **No failure-scenario tests**: missing source file, invalid schema, repeated runs.
6. **dbt lacks tests**: no `unique`/`not_null`/`relationships`/`accepted_values`.

### Medium
7. **transform_geolocation** uses `first` instead of mode for city/state.
8. **load_fact_orders** uses a slow mode lambda for payment_type (~2 min).
9. **No transactional warehouse load**: partial failure leaves inconsistent state.
10. **Geolocation aggregation** changes grain from zip+lat to zip only (documented).

### Low
11. Spark outputs use default partition count (1 partition) - acceptable for this size.
12. Monthly revenue uses Period conversion with tz warning (cosmetic).
13. Airflow DAG is reference-only (documented).
14. Azure components are design-only (intentional, no cost).

## Architecture assessment
Medallion separation is clear. Bronze preserves source + metadata. Silver standardises.
Gold aggregates. Warehouse is star schema. Spark demonstrates distributed processing.
dbt adds a thin SQL layer. Responsibilities are mostly well separated.

## Conclusion
Functional but test/CI gaps prevent "production-ready" claim. Improvements below.