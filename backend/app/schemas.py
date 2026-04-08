"""
Pydantic schemas for request validation and response serialization.
OWASP A03: Strict input validation — length bounds enforced by Pydantic
           before data ever reaches the database layer.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecordCreate(BaseModel):
    """Payload accepted when creating a new record.

    Pydantic enforces:
      - title: 1–200 characters (non-empty, bounded)
      - content: 1–5000 characters (non-empty, bounded)

    Server-side validation is the authoritative source of truth
    (OWASP A03: never rely on client-side validation alone).
    """

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=5000)


class RecordOut(BaseModel):
    """Shape of record data returned to the client."""

    id: UUID
    title: str
    content: str
    created_at: datetime

    # Enable ORM-mode so SQLAlchemy model instances can be serialized
    # directly without an intermediate dict conversion.
    model_config = ConfigDict(from_attributes=True)
