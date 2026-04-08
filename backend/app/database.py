"""
Database configuration module.
OWASP A02: Secure configuration via environment variables.
OWASP A03: All queries go through SQLAlchemy ORM — no raw SQL.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/recordsdb",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,          # detect stale connections
    pool_size=10,
    max_overflow=20,
    connect_args={"connect_timeout": 10},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """
    FastAPI dependency that yields a DB session and guarantees it is
    closed afterwards, even on exceptions (OWASP A10: resource cleanup).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
