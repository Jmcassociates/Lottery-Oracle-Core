# JMc - [2026-03-18] - Migration Script: Virginia Game Renaming Protocol (v2).
from sqlalchemy import create_engine, text
from app.core.database import DATABASE_URL

def migrate():
    engine = create_engine(DATABASE_URL)
    
    mapping = {
        "Powerball": "VirginiaPowerball",
        "MegaMillions": "VirginiaMegaMillions",
        "Cash4Life": "VirginiaCash4Life",
        "Cash5": "VirginiaCash5",
        "Pick3 Day": "VirginiaPick3 Day",
        "Pick3 Night": "VirginiaPick3 Night",
        "Pick4 Day": "VirginiaPick4 Day",
        "Pick4 Night": "VirginiaPick4 Night",
        "Pick5 Day": "VirginiaPick5 Day",
        "Pick5 Night": "VirginiaPick5 Night"
    }

    batch_mapping = {
        "Powerball": "VirginiaPowerball",
        "MegaMillions": "VirginiaMegaMillions",
        "Cash4Life": "VirginiaCash4Life",
        "Cash5": "VirginiaCash5",
        "Pick3": "VirginiaPick3",
        "Pick4": "VirginiaPick4",
        "Pick5": "VirginiaPick5"
    }

    with engine.connect() as conn:
        print("Starting Virginia Game Name Migration...")
        
        for old, new in mapping.items():
            result = conn.execute(
                text("UPDATE historical_draws SET game_name = :new, state_code = 'VA' WHERE game_name = :old AND state_code IN ('VA', 'NAT')"),
                {"new": new, "old": old}
            )
            print(f"Updated {result.rowcount} historical_draws from '{old}' to '{new}'")

        for old, new in batch_mapping.items():
            result = conn.execute(
                text("UPDATE saved_ticket_batches SET game_name = :new, state_code = 'VA' WHERE game_name = :old AND state_code IN ('VA', 'NAT')"),
                {"new": new, "old": old}
            )
            print(f"Updated {result.rowcount} saved_ticket_batches from '{old}' to '{new}'")

        conn.commit()
        print("Migration complete.")

if __name__ == "__main__":
    migrate()
