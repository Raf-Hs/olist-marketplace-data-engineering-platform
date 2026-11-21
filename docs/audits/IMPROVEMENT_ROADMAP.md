# Improvement Roadmap

## Critical
- Fix CI data dependency (skip markers + documented data bootstrap).

## High
- Add warehouse integrity and business-rule tests.
- Add dbt tests (unique/not_null/relationships).
- Make `create_schema` path robust (done).

## Medium
- Optimize `load_fact_orders` payment_type aggregation.
- Consider transactional warehouse load.
- Document geolocation aggregation decision.

## Low
- Spark partition tuning (optional).
- Cosmetic tz warning in Gold monthly revenue.