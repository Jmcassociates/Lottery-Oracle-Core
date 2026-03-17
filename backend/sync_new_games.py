from app.core.database import SessionLocal
from app.services.fetchers import (
    VirginiaCash4LifeFetcher,
    VirginiaCash5Fetcher,
    VirginiaPick5Fetcher,
    VirginiaPick4Fetcher,
    VirginiaPick3Fetcher
)

def sync_new_games():
    db = SessionLocal()
    fetchers = [
        VirginiaCash4LifeFetcher(),
        VirginiaCash5Fetcher(),
        VirginiaPick5Fetcher(),
        VirginiaPick4Fetcher(),
        VirginiaPick3Fetcher()
    ]
    
    for fetcher in fetchers:
        print(f"Syncing {fetcher.game_name}...")
        fetcher.sync_to_db(db)

    print("All new games synced successfully!")

if __name__ == "__main__":
    sync_new_games()
