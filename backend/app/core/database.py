from sqlalchemy import create_engine, TypeDecorator, Text
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
import json
import os
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Custom hybrid VectorType that works natively with pgvector on PostgreSQL and serializes as JSON on SQLite
class VectorType(TypeDecorator):
    impl = Text
    cache_ok = True

    def __init__(self, dim=384, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dim = dim

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            try:
                from pgvector.sqlalchemy import Vector
                return dialect.type_descriptor(Vector(self.dim))
            except ImportError:
                return dialect.type_descriptor(Text())
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        # In SQLite or fallback dialects, store as JSON list
        if isinstance(value, (list, tuple)):
            return json.dumps(list(value))
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            if hasattr(value, "tolist"):
                return value.tolist()
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return value
        return value

# Determine active database URL: try PostgreSQL first, fall back to SQLite if unreachable
DATABASE_URL = settings.DATABASE_URL
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args=connect_args
    )
    # Test connection
    with engine.connect() as conn:
        logger.info(f"Connected to database successfully: {DATABASE_URL}")
except Exception as e:
    if settings.ENVIRONMENT.lower() == "production":
        logger.error("Could not connect to production PostgreSQL database.")
        raise
    logger.warning(f"Could not connect to {DATABASE_URL} ({e}). Falling back to local SQLite: {settings.SQLITE_FALLBACK_URL}")
    DATABASE_URL = settings.SQLITE_FALLBACK_URL
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
