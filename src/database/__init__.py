"""
Database initialization module for AI Safety Governance Platform.

The application supports two deployment modes:

* PostgreSQL (production / Docker) selected with ``DATABASE_URL`` or the
  ``POSTGRES_*`` environment variables.
* SQLite (local development and tests) used when no database configuration is
  supplied. The file lives next to the repository root so the documented
  ``uvicorn`` command works without any external services.
"""

import logging
import os
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows local development
    fcntl = None

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = PROJECT_ROOT / "ai_safety_governance.db"

# Create SQLAlchemy base class for models
Base = declarative_base()


def get_database_url() -> str:
    """Resolve the database URL from the environment.

    Resolution order:
    1. ``DATABASE_URL`` (explicit override, recommended for deployments).
    2. ``POSTGRES_*`` variables (Docker Compose sets ``POSTGRES_HOST=db``).
    3. A local SQLite file so development needs no external database.
    """
    explicit_url = os.getenv("DATABASE_URL", "").strip()
    if explicit_url:
        return explicit_url

    if any(
        os.getenv(name)
        for name in (
            "POSTGRES_HOST",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_DB",
        )
    ):
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "ai_safety_governance")
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

    return f"sqlite:///{DEFAULT_SQLITE_PATH}"


def _engine_options(database_url: str) -> dict:
    """Return engine options appropriate for the selected dialect."""
    if database_url.startswith("sqlite"):
        # SQLite connections are bound to the thread that created them by
        # default; FastAPI/TestClient run handlers on a worker thread.
        return {"connect_args": {"check_same_thread": False}}

    return {
        "pool_pre_ping": True,
        "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10")),
    }


DATABASE_URL = get_database_url()

# Initialize database engine
engine = create_engine(DATABASE_URL, future=True, **_engine_options(DATABASE_URL))

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# A multi-worker start (Gunicorn) must not race schema creation/stamping.
# SQLite uses a file lock; PostgreSQL uses a session advisory lock.
_INIT_LOCK_PATH = DEFAULT_SQLITE_PATH.with_name(DEFAULT_SQLITE_PATH.name + ".init.lock")
_POSTGRES_INIT_LOCK_KEY = 728194621


@contextmanager
def _database_init_lock():
    if DATABASE_URL.startswith("sqlite"):
        if fcntl is None or DATABASE_URL.endswith(":memory:"):
            yield
            return
        _INIT_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_INIT_LOCK_PATH, "w", encoding="utf-8") as lock_file:
            fcntl.flock(lock_file, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file, fcntl.LOCK_UN)
        return

    if DATABASE_URL.startswith("postgresql"):
        with engine.connect() as connection:
            connection.execute(text(f"SELECT pg_advisory_lock({_POSTGRES_INIT_LOCK_KEY})"))
            connection.commit()
            try:
                yield
            finally:
                connection.execute(text(f"SELECT pg_advisory_unlock({_POSTGRES_INIT_LOCK_KEY})"))
                connection.commit()
        return

    yield


def _alembic_config():
    """Build an Alembic config that points at the project migrations."""
    from alembic.config import Config

    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "src" / "database" / "migrations"))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    return config


def init_db(create_tables: bool = True) -> None:
    """Initialise the database schema and optional bootstrap data.

    * Versioned databases are upgraded with Alembic so existing installations
      receive new migrations.
    * Brand-new databases are created from the current ORM metadata and stamped
      at the current Alembic head, keeping later migrations usable.
    """
    # Importing models registers every table on Base.metadata.
    from . import models  # noqa: F401

    if not create_tables:
        return

    auto_init = os.getenv("DB_AUTO_INIT", "true").strip().lower() not in {
        "0",
        "false",
        "no",
    }
    if not auto_init:
        logger.info("DB_AUTO_INIT disabled; skipping database schema initialisation")
        return

    with _database_init_lock():
        inspector = inspect(engine)
        if "alembic_version" in inspector.get_table_names():
            from alembic import command

            command.upgrade(_alembic_config(), "head")
            logger.info("Applied pending database migrations")
        else:
            Base.metadata.create_all(bind=engine)
            from alembic import command

            command.stamp(_alembic_config(), "head")
            logger.info("Created database schema and stamped Alembic head")


def get_db():
    """
    Get database session.

    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
