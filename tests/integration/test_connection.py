from src.database.connection import check_connection


def test_postgres_connection():
    version = check_connection()
    assert "PostgreSQL" in version
