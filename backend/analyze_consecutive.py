import statistics
from app.core.database import SessionLocal
from app.core.models import DrawRecord

def analyze_consecutive(game_name):
    db = SessionLocal()
    draws = db.query(DrawRecord).filter(DrawRecord.game_name == game_name).all()
    
    if not draws:
        print(f"No draws found for {game_name}")
        return

    total_draws = len(draws)
    consecutive_3_count = 0
    consecutive_4_count = 0
    consecutive_5_count = 0
    
    for d in draws:
        wb = sorted([int(x) for x in d.white_balls.split(",")])
        
        # Check for sequences
        max_seq = 1
        current_seq = 1
        for i in range(1, len(wb)):
            if wb[i] == wb[i-1] + 1:
                current_seq += 1
                if current_seq > max_seq:
                    max_seq = current_seq
            else:
                current_seq = 1
                
        if max_seq >= 3:
            consecutive_3_count += 1
        if max_seq >= 4:
            consecutive_4_count += 1
        if max_seq == 5:
            consecutive_5_count += 1

    print(f"{game_name.upper()} CONSECUTIVE NUMBER ANALYSIS ({total_draws} Draws)")
    print("=" * 60)
    print(f"3 in a row (e.g., 4,5,6):    {consecutive_3_count} times ({(consecutive_3_count / total_draws) * 100:.2f}%)")
    print(f"4 in a row (e.g., 4,5,6,7):  {consecutive_4_count} times ({(consecutive_4_count / total_draws) * 100:.2f}%)")
    print(f"5 in a row (e.g., 1,2,3,4,5): {consecutive_5_count} times ({(consecutive_5_count / total_draws) * 100:.2f}%)")
    print("-" * 60)

if __name__ == "__main__":
    analyze_consecutive("Powerball")
    analyze_consecutive("MegaMillions")
