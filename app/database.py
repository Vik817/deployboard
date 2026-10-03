"""Database setup: engine, session factory, and the declarative Base.

Using SQLite for local dev. To move to Postgres later, change DATABASE_URL
to a postgresql:// connection string and drop the connect_args line below —
that's the only change needed here.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./deployboard.db"

# check_same_thread is a SQLite-only quirk: it lets the connection be used
# across threads, which FastAPI needs. It does NOT apply to Postgres.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session and guarantees it's closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
