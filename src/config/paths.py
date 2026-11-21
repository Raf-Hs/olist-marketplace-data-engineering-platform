"""Centralised path resolution for the platform."""

from __future__ import annotations

from pathlib import Path

import os


def project_root() -> Path:
    """Return the project root directory."""
    env_root = os.getenv("PROJECT_ROOT")
    if env_root:
        return Path(env_root).resolve()
    # Default: parent of src/
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    env_dir = os.getenv("DATA_DIR")
    if env_dir:
        p = Path(env_dir)
        if not p.is_absolute():
            p = project_root() / p
        return p.resolve()
    return project_root() / "data"


RAW_DIR = None  # resolved lazily below


def raw_dir() -> Path:
    return data_dir() / "raw"


def bronze_dir() -> Path:
    return data_dir() / "bronze"


def silver_dir() -> Path:
    return data_dir() / "silver"


def gold_dir() -> Path:
    return data_dir() / "gold"


def samples_dir() -> Path:
    return data_dir() / "samples"
