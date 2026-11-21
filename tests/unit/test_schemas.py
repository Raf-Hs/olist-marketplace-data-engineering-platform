import pandas as pd

from src.ingestion.schemas import OLIST_SCHEMAS, validate_schema


def test_orders_schema_valid():
    from src.config.paths import raw_dir
    df = pd.read_csv(raw_dir() / "olist_orders_dataset.csv")
    schema = OLIST_SCHEMAS["orders"]
    errors = validate_schema(df, schema)
    assert errors == [], errors


def test_validate_schema_missing_column():
    df = pd.DataFrame({"a": [1]})
    from src.ingestion.schemas import ColumnSpec, TableSchema
    schema = TableSchema(name="t", file_name="x.csv", columns=[ColumnSpec("a", "int"), ColumnSpec("b", "int", False)])
    errors = validate_schema(df, schema)
    assert any("Missing columns" in e for e in errors)


def test_all_schemas_have_primary_key_or_not():
    for s in OLIST_SCHEMAS.values():
        assert s.file_name.endswith(".csv")
