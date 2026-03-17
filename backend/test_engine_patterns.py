import sys
from app.core.database import SessionLocal
from app.core.models import DrawRecord
from app.services.engine import LotteryMathEngine, PatternScouter

def run_test():
    db = SessionLocal()
    
    for game in ["Powerball", "MegaMillions"]:
        print(f"\n--- TESTING ENGINE FOR {game} ---")
        records = db.query(DrawRecord).filter(DrawRecord.game_name == game).order_by(DrawRecord.draw_date.asc()).all()
        
        formatted_history = []
        previous_jackpots = set()
        for r in records:
            wb = [int(x) for x in r.white_balls.split(",")]
            formatted_history.append({"date": r.draw_date, "white_balls": wb, "special_ball": r.special_ball})
            previous_jackpots.add(f"{r.white_balls}:{r.special_ball}")

        white_max = 69 if game == "Powerball" else 70
        special_max = 26 if game == "Powerball" else 24
        
        engine = LotteryMathEngine(game, formatted_history, white_max, special_max, previous_jackpots)
        pool, special_pool = engine.generate_smart_pool(pool_size=15, special_pool_size=3)
        print(f"Smart Pool generated: {pool}")
        
        num_to_generate = 20
        tickets = engine.generate_wheeled_tickets(pool, special_pool, num_to_generate)
        
        print(f"Generated {len(tickets)} tickets.")
        
        all_passed = True
        for i, t in enumerate(tickets):
            wb = sorted(t['white_balls'])
            odd_count = sum(1 for n in wb if n % 2 != 0)
            even_count = 5 - odd_count
            
            # Check Patterns
            is_valid = PatternScouter.is_valid_pattern(tuple(wb), game, white_max)
            pattern_str = f"O:{odd_count} E:{even_count} | Start:{wb[0]}"
            
            if not is_valid:
                print(f"  [!] Ticket #{i+1} FAIL Pattern: {wb} [{t['special_ball']}] | {pattern_str}")
                all_passed = False
            else:
                print(f"  [✓] Ticket #{i+1} PASS: {wb} [{t['special_ball']}] | {pattern_str}")
                
            # Check Historical Collision
            if engine.is_historical_jackpot(tuple(wb), t['special_ball']):
                print(f"  [CRITICAL] Ticket #{i+1} is a historical jackpot! FAIL.")
                all_passed = False

        if all_passed:
            print(f"SUCCESS: All {game} tickets adhere to the high-probability distribution matrix.")
        else:
            print(f"FAILURE: Some {game} tickets deviated from the matrix constraints.")

if __name__ == "__main__":
    run_test()
