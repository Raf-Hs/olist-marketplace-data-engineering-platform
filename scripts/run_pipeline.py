"""Convenience entry point for the end-to-end pipeline."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestration.pipeline import run_pipeline

if __name__ == "__main__":
    run_pipeline()
