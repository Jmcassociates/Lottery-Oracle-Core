from app.core.database import SessionLocal
from app.core.models import DrawRecord

def migrate_tx():
    db = SessionLocal()
    records = db.query(DrawRecord).filter(DrawRecord.state_code == "TX").all()
    count = 0
    for r in records:
        if r.game_name.startswith("Pick3"):
            r.game_name = r.game_name.replace("Pick3", "TexasPick3", 1)
            count += 1
        elif r.game_name.startswith("Daily4"):
            r.game_name = r.game_name.replace("Daily4", "TexasDaily4", 1)
            count += 1
        elif r.game_name == "CashFive":
            r.game_name = "TexasCashFive"
            count += 1
    
    db.commit()
    print(f"Migrated {count} TX records to new game_name prefix.")

if __name__ == "__main__":
    migrate_tx()
