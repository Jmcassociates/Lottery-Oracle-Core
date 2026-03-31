from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# JMc - [2026-03-07] - Using a local SQLite database file, easily volume-mounted in Docker.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lottery.db")

# JMc - [2026-03-18] - Cloud Run PostgreSQL requires omitting the SQLite-specific thread check.
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# JMc - [2026-03-31] - Hardening connection pool for Cloud Run.
# Default limits are too high for a small Postgres instance with multiple workers.
engine = create_engine(
    DATABASE_URL, 
    connect_args=connect_args,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
