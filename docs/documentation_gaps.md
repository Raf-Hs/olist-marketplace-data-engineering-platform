# Documentation Gaps

Status of documentation accuracy against the implementation.

## Resolved / accurate

- `docs/data_quality.md` correctly points to `tests/data_quality/test_quality.py`.
- `docs/data_sources.md` row counts match source CSVs (verified).
- `docs/data_dictionary.md` matches `infra/postgres/init/01_schema.sql`.
- `.gitignore` ignores raw/generated data and keeps `data/samples/`.
- `.env.example` present and consistent with settings.

## Open gaps

1. **Spark entry point mismatch**: README, setup, and execution docs reference
   `run_spark.py`, which is not in the repository. Documented as a limitation;
   manual invocation via `src.spark.transformations` functions is required.
2. **Warehouse not in main pipeline**: `src/orchestration/pipeline.py` runs through
   Gold only. Docs now state that warehouse load is a separate step.
3. **Python version**: docs say 3.11; this environment uses 3.12. Clarified as
   target vs. tested.
4. **No documentation index**: added `docs/README.md`.
5. **No consolidated limitations doc**: added `docs/limitations.md`.
6. **No test documentation**: added `docs/testing.md`.
7. **Audit docs not linked from README**: README now links to `docs/` index.
8. **Verified metrics scattered**: README now centralises key verified metrics.
9. **Unused sample data**: `data/samples/sample_order.json` is not consumed by any
   module; documented as sample only.
