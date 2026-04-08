"""
FastAPI application entry point.

Security controls applied:
  OWASP A01 – Broken Access Control   : CORS restricted to known origins only.
  OWASP A02 – Security Misconfiguration: Security headers on every response;
                                         generic error messages to clients.
  OWASP A05 – Injections              : All DB access via ORM (see models.py).
  OWASP A06 – Insecure Design         : Rate limiting via SlowAPI (100 req/min).
  OWASP A09 – Logging & Monitoring    : Structured logging of create events;
                                        sensitive content is NEVER logged.
  OWASP A10 – Exceptional Conditions  : Global 500 handler hides stack traces.
"""
import logging
from typing import List

from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.models import Base, Record
from app.schemas import RecordCreate, RecordOut

# Create tables on startup (idempotent — safe to run multiple times).
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# Logging — INFO level, timestamp included, sensitive data never logged.
# OWASP A09: log security-relevant events, never log sensitive payloads.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate limiter — 100 requests per minute per IP.
# OWASP A06: throttle to harden against brute-force and DoS.
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Records API",
    # Disable automatic /docs and /redoc in a hardened deployment by setting
    # docs_url=None / redoc_url=None via env var if desired.
    docs_url="/docs",
    redoc_url="/redoc",
)

# Attach SlowAPI state and its built-in 429 handler.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# CORS — restricted to known frontend origins only.
# OWASP A01: never use allow_origins=["*"] in production.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:80",
        "http://frontend",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Security-headers middleware.
# OWASP A02: harden HTTP responses against common browser-based attacks.
# ---------------------------------------------------------------------------
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


# ---------------------------------------------------------------------------
# Global exception handler — generic message, no stack trace exposed.
# OWASP A10 / A02: never leak internal details to the client.
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Full exception is logged server-side for debugging.
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health", tags=["health"])
async def health_check():
    """Liveness probe — returns immediately without touching the DB."""
    return {"status": "ok"}


@app.get(
    "/api/records",
    response_model=List[RecordOut],
    tags=["records"],
    summary="List all records",
)
@limiter.limit("100/minute")
async def list_records(request: Request, db: Session = Depends(get_db)):
    """
    Returns up to 1000 records ordered by creation date (newest first).
    OWASP A03: ORM query only — no raw SQL.
    """
    records = (
        db.query(Record)
        .order_by(Record.created_at.desc())
        .limit(1000)
        .all()
    )
    return records


@app.post(
    "/api/records",
    response_model=RecordOut,
    status_code=status.HTTP_201_CREATED,
    tags=["records"],
    summary="Create a new record",
)
@limiter.limit("100/minute")
async def create_record(
    request: Request,
    payload: RecordCreate,
    db: Session = Depends(get_db),
):
    """
    Creates a new record.
    OWASP A03: input validated by Pydantic before reaching the DB layer.
    OWASP A09: logs the title only — content is NEVER logged.
    """
    new_record = Record(title=payload.title, content=payload.content)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    # Log title only — never log content (may contain sensitive user data).
    logger.info("Record created: %s", payload.title)

    return new_record
