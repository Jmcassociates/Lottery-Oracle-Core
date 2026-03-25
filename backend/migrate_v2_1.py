import os
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JMc - [2026-03-18] - Migration Script v2.1
# Re-aligns National games with the NAT state code and correct game names.

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lottery.db")

def migrate():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        logger.info(f"Connected to {DATABASE_URL}. Commencing migration v2.1...")
        
        # 1. Re-align Powerball
        try:
            res = conn.execute(text(
                "UPDATE historical_draws SET game_name = 'Powerball', state_code = 'NAT' "
                "WHERE game_name = 'VirginiaPowerball'"
            ))
            conn.commit()
            logger.info(f"Re-aligned {res.rowcount} Powerball records to NAT.")
        except Exception as e:
            logger.error(f"Error re-aligning Powerball: {e}")

        # 2. Re-align MegaMillions
        try:
            res = conn.execute(text(
                "UPDATE historical_draws SET game_name = 'MegaMillions', state_code = 'NAT' "
                "WHERE game_name = 'VirginiaMegaMillions'"
            ))
            conn.commit()
            logger.info(f"Re-aligned {res.rowcount} MegaMillions records to NAT.")
        except Exception as e:
            logger.error(f"Error re-aligning MegaMillions: {e}")

        logger.info("Migration v2.1 complete.")

if __name__ == "__main__":
    migrate()
