"""Ingestion routines for Olist source CSVs."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.config.paths import raw_dir, bronze_dir
from src.ingestion.schemas import OLIST_SCHEMAS, validate_schema, TableSchema
from src.utils.logging import get_logger

logger = get_logger(__name__)


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_source(schema: TableSchema) -> pd.DataFrame:
    """Read a source CSV according to its schema."""
    path = raw_dir() / schema.file_name
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")
    df = pd.read_csv(path)
    errors = validate_schema(df, schema)
    if errors:
        raise ValueError(f"Schema validation failed for {schema.name}: {errors}")
    return df


def ingest_table(schema: TableSchema, run_id: str | None = None) -> dict[str, Any]:
    """Ingest one table into the Bronze layer with metadata."""
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    df = load_source(schema)
    out_dir = bronze_dir() / schema.name
    out_dir.mkdir(parents=True, exist_ok=True)

    # Write parquet (idempotent: overwrite)
    out_path = out_dir / f"{schema.name}.parquet"
    df.to_parquet(out_path, index=False)

    metadata = {
        "table": schema.name,
        "source_file": schema.file_name,
        "row_count": int(len(df)),
        "column_count": int(df.shape[1]),
        "source_hash_sha256": _file_hash(raw_dir() / schema.file_name),
        "ingested_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
    }
    meta_path = out_dir / "metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    logger.info("Ingested %s: %d rows -> %s", schema.name, len(df), out_path)
    return metadata


def ingest_all(run_id: str | None = None) -> list[dict[str, Any]]:
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    results = []
    for name, schema in OLIST_SCHEMAS.items():
        try:
            results.append(ingest_table(schema, run_id=run_id))
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to ingest %s: %s", name, exc)
            raise
    return results
