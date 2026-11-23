# Testing

## Test suite

| File | Type | Count | Requires |
|---|---|---|---|
| `tests/unit/test_schemas.py` | unit | 3 | none (data optional) |
| `tests/unit/test_quality_checks.py` | unit | 6 | none |
| `tests/data_quality/test_quality.py` | data quality | 1 | silver data |
| `tests/integration/test_connection.py` | integration | 1 | PostgreSQL |

Total: 11 tests.

## Markers

- `requires_data`: needs raw/silver data files.
- `integration`: needs a running PostgreSQL instance.

## Running

```bash
pytest -q
pytest -q -m "not requires_data"
pytest -q -m "requires_data"
```

## Current status in this environment

- 10 tests pass without PostgreSQL.
- `tests/integration/test_connection.py` fails without a running Postgres
  (port 5434).
- Data-dependent tests pass because `data/silver/` is present locally.
- In CI, raw/silver data are gitignored, so data-dependent tests are skipped.
