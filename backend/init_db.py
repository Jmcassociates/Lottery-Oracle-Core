#!/usr/bin/env python3
import logging
from app.core.database import engine, Base, get_db
from app.core.models import DrawRecord
from app.core.config import GAMES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init():
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    
    db = next(get_db())
    
    for game_name, config in GAMES.items():
        count = db.query(DrawRecord).filter(DrawRecord.game_name.startswith(game_name)).count()
        if count == 0:
            logger.info(f"Database empty for {game_name}. Running initial sync...")
            fetcher = config["fetcher"]()
            fetcher.sync_to_db(db)
        else:
            logger.info(f"Database already contains {count} records for {game_name}. Skipping initial sync.")

if __name__ == "__main__":
    init()
