import os
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JMc - [2026-03-18] - Migration Script v2.0
# Adds administrative and passwordless support to the Cloud SQL schema.

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lottery.db")

def migrate():
    engine = create_engine(DATABASE_URL)
    
    logger.info(f"Connected to {DATABASE_URL}. Commencing migration...")
    
    # 1. Add is_admin column
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0"))
            conn.commit()
            logger.info("Added is_admin column.")
        except Exception as e:
            logger.warning(f"Could not add is_admin (likely exists): {e}")

    # 2. Add is_active column
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1"))
            conn.commit()
            logger.info("Added is_active column.")
        except Exception as e:
            logger.warning(f"Could not add is_active (likely exists): {e}")

    # 3. Add last_login column
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN last_login TIMESTAMP WITH TIME ZONE"))
            conn.commit()
            logger.info("Added last_login column.")
        except Exception as e:
            logger.warning(f"Could not add last_login (likely exists): {e}")

    # 4. Make hashed_password nullable (Postgres specific)
    if DATABASE_URL.startswith("postgresql"):
        with engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL"))
                conn.commit()
                logger.info("Updated hashed_password to be nullable.")
            except Exception as e:
                logger.error(f"Failed to drop NOT NULL constraint: {e}")
    
    # 5. Bootstrap the master admin (You)
    with engine.connect() as conn:
        try:
            conn.execute(text("UPDATE users SET is_admin = 1 WHERE email = 'james@moderncyph3r.com'"))
            conn.commit()
            logger.info("James McCabe promoted to Lead Architect (Admin status locked).")
        except Exception as e:
            logger.warning(f"Could not bootstrap admin: {e}")

    logger.info("Migration v2.0 complete.")

if __name__ == "__main__":
    migrate()
