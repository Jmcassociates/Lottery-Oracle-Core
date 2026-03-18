from app.core.database import SessionLocal
from app.services.fetchers import (
    TexasCashFiveFetcher,
    TexasPick3Fetcher,
    TexasDaily4Fetcher
)

def sync_texas():
    db = SessionLocal()
    fetchers = [
        TexasCashFiveFetcher(),
        TexasPick3Fetcher(),
        TexasDaily4Fetcher()
    ]
    
    for fetcher in fetchers:
        print(f"Syncing {fetcher.game_name}...")
        fetcher.sync_to_db(db)

    print("All Texas games synced successfully!")

if __name__ == "__main__":
    sync_texas()
