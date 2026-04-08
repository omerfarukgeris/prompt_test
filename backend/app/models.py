"""
SQLAlchemy ORM models.
OWASP A03: All DB interaction via ORM — parameterized queries only,
           no raw SQL anywhere in the codebase.
OWASP A01: Server-generated UUID primary keys prevent IDOR enumeration
           via sequential integer IDs.
"""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

from app.database import Base


class Record(Base):
    """Represents a single user record in the database."""

    __tablename__ = "records"

    # Server-generated UUID — not predictable/sequential (OWASP A01).
    id = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        nullable=False,
    )
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
