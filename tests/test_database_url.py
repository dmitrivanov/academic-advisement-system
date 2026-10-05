from database import normalize_database_url
from sqlalchemy import create_engine


def test_render_postgres_urls_use_installed_psycopg2_driver():
    suffix = "user:password@host.example/advisor"
    assert normalize_database_url(f"postgres://{suffix}") == f"postgresql+psycopg2://{suffix}"
    assert normalize_database_url(f"postgresql://{suffix}") == f"postgresql+psycopg2://{suffix}"
    assert normalize_database_url(f"postgresql+psycopg://{suffix}") == f"postgresql+psycopg2://{suffix}"
    engine = create_engine(normalize_database_url(f"postgresql+psycopg://{suffix}"))
    assert engine.dialect.driver == "psycopg2"


def test_sqlite_url_is_unchanged():
    assert normalize_database_url("sqlite:///./advisor.db") == "sqlite:///./advisor.db"
