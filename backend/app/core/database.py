from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# JMc - [2026-03-07] - Using a local SQLite database file, easily volume-mounted in Docker.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lottery.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} # Required for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
