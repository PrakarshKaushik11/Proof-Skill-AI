# src/db/session.py
"""
Database connection management using SQLAlchemy.
Provides session factory and initialization.
"""
from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.config.settings import settings


# Create engine with SQLite optimizations
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30,
    },
    poolclass=StaticPool,
    echo=settings.DEBUG,
)

# Enable WAL mode and other pragmas
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA cache_size=10000;")
    cursor.execute("PRAGMA temp_store=MEMORY;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Session:
    """Dependency for FastAPI-style dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Session:
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Initialize database schema from schema.sql."""
    schema_path = Path(__file__).parent / "schema.sql"
    
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    sql = schema_path.read_text(encoding="utf-8")

    # SQLite's executescript correctly handles trigger bodies, whose
    # statements contain semicolons and cannot be split safely by text.
    raw_connection = engine.raw_connection()
    try:
        raw_connection.executescript(sql)
        columns = {
            row[1] for row in raw_connection.execute("PRAGMA table_info(users)").fetchall()
        }
        if "candidate_name" not in columns:
            raw_connection.execute(
                "ALTER TABLE users ADD COLUMN candidate_name TEXT NOT NULL DEFAULT 'Candidate'"
            )
        raw_connection.commit()
    finally:
        raw_connection.close()
    
    print(f"Database initialized at {settings.DATABASE_URL}")


def drop_db() -> None:
    """Drop all tables (use with caution!)."""
    from src.models.schemas import Base
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped")


if __name__ == "__main__":
    init_db()