"""Database engine, session factory, and table initialisation."""

from contextlib import contextmanager
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Base

DATABASE_URL = "sqlite:///./research_agent.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    # Echo SQL in debug mode — set to False for production silence
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager that opens a session, commits on success, rolls back on error."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Create all tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)
