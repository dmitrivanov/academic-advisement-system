import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

def normalize_database_url(value: str) -> str:
    """Use the PostgreSQL driver installed by this project on every host."""
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+psycopg2://", 1)
    if value.startswith("postgresql+psycopg://"):
        return value.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg2://", 1)
    return value


DATABASE_URL = normalize_database_url(
    os.environ.get("DATABASE_URL", "sqlite:///./advisor.db")
)

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
