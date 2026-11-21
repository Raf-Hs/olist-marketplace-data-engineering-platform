# Technical Decision Records

## TDR-001: Separate local PostgreSQL port (5434)

**Decision**: Use port 5434 for this project's PostgreSQL.
**Reason**: Port 5432/5433 already allocated by other local projects. Avoids
conflicts without modifying other projects.

## TDR-002: pandas for Silver, PySpark for analytics

**Decision**: Use pandas for Silver transformations (dataset fits in memory) and
PySpark to demonstrate distributed processing.
**Reason**: Spark adds overhead for small data; using it where it adds value
(distributed transformations) demonstrates competence without unnecessary complexity.

## TDR-003: Parquet for lake layers

**Decision**: Store Bronze/Silver/Gold as Parquet.
**Reason**: Columnar, compressed, schema-preserving, interoperable with Spark.

## TDR-004: Idempotent overwrite

**Decision**: All steps overwrite outputs.
**Reason**: Reproducible runs; safe re-execution.

## TDR-005: Surrogate keys in warehouse

**Decision**: Use SERIAL surrogate keys, keep natural keys as unique columns.
**Reason**: Decouples warehouse from source key changes and supports SCD later.

## TDR-006: No SCD Type 2

**Decision**: Type 1 overwrite only.
**Reason**: Dimension attributes are static over the observed period; Type 2 adds
complexity without business value here.
