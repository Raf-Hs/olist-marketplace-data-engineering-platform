"""SQLAlchemy engine factory for PostgreSQL."""

from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.config.settings import get_settings


def get_engine() -> Engine:
    settings = get_settings()
    url = settings.database_url
    return create_engine(url, pool_pre_ping=True)


def check_connection(engine: Engine | None = None) -> str:
    eng = engine or get_engine()
    with eng.connect() as conn:
        return conn.execute(text("SELECT version()")).scalar_one()
