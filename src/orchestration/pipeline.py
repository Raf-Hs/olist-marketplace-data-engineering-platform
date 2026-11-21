"""End-to-end pipeline orchestration (Python)."""

from __future__ import annotations

from src.utils.logging import get_logger

logger = get_logger(__name__)


def run_pipeline() -> None:
    logger.info("=== Pipeline start ===")

    from src.ingestion.ingest import ingest_all

    ingest_all()
    logger.info("Ingestion complete.")

    from src.transformations.silver import transform_all

    transform_all()
    logger.info("Silver complete.")

    from src.quality.checks import run_basic_checks

    results = run_basic_checks()
    failed = [r for r in results if not r.passed]
    if failed:
        raise RuntimeError(f"Data quality checks failed: {[r.name for r in failed]}")
    logger.info("Data quality checks passed.")

    from src.transformations.gold import build_gold

    build_gold()
    logger.info("Gold complete.")

    logger.info("=== Pipeline complete ===")


if __name__ == "__main__":
    run_pipeline()
