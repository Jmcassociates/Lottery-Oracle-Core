from app.core.database import SessionLocal
from app.core.models import DrawRecord
from app.services.fetchers import TexasCashFiveFetcher

def purge_and_sync():
    db = SessionLocal()
    
    # Delete all TexasCashFive records
    deleted = db.query(DrawRecord).filter(DrawRecord.game_name == "TexasCashFive").delete()
    db.commit()
    print(f"Purged {deleted} legacy TexasCashFive records.")
    
    # Resync with the new fetcher rules (only after 2018-09-23)
    fetcher = TexasCashFiveFetcher()
    print(f"Resyncing TexasCashFive with strictly modern matrix data...")
    new_count = fetcher.sync_to_db(db)
    print(f"Sync complete. Added {new_count} validated modern draws.")

if __name__ == "__main__":
    purge_and_sync()
