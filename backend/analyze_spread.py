import statistics
from app.core.database import SessionLocal
from app.core.models import DrawRecord

db = SessionLocal()

games_config = {
    "Powerball": {"max": 69},
    "MegaMillions": {"max": 70},
    "Cash4Life": {"max": 60},
    "Cash5": {"max": 45}
}

for game_name, config in games_config.items():
    draws = db.query(DrawRecord).filter(DrawRecord.game_name == game_name).all()
    if not draws:
        print(f"No draws found for {game_name}")
        continue

    buckets = {
        "Starts with 1 or 2": [],
        "Starts 3-10": [],
        "Starts 11-20": [],
        "Starts 21-34": [],
        "Starts 35+": []
    }

    for d in draws:
        wb = sorted([int(x) for x in d.white_balls.split(",")])
        first = wb[0]
        
        if first in [1, 2]:
            buckets["Starts with 1 or 2"].append(wb)
        elif first <= 10:
            buckets["Starts 3-10"].append(wb)
        elif first <= 20:
            buckets["Starts 11-20"].append(wb)
        elif first <= 34:
            buckets["Starts 21-34"].append(wb)
        else:
            buckets["Starts 35+"].append(wb)

    print(f"\n{game_name.upper()} HISTORICAL SPREAD ANALYSIS (1-{config['max']} Matrix)")
    print("=" * 60)
    
    # Calculate zones dynamically
    max_ball = config["max"]
    zone_size = max_ball // 3
    z1_max = zone_size
    z2_max = zone_size * 2

    for name, b_draws in buckets.items():
        if not b_draws: continue
        count = len(b_draws)
        pct = (count / len(draws)) * 100
        
        avg_spread = statistics.mean([d[4] - d[0] for d in b_draws])
        avg_highest = statistics.mean([d[4] for d in b_draws])
        
        low_count = sum(sum(1 for n in d if n <= z1_max) for d in b_draws)
        mid_count = sum(sum(1 for n in d if z1_max < n <= z2_max) for d in b_draws)
        high_count = sum(sum(1 for n in d if n > z2_max) for d in b_draws)
        
        avg_low = low_count / count
        avg_mid = mid_count / count
        avg_high = high_count / count
        
        print(f"[{name}] -> {count} draws ({pct:.1f}% of total)")
        print(f"  Avg Spread (1st to 5th ball): {avg_spread:.1f}")
        print(f"  Avg Highest Ball:             {avg_highest:.1f}")
        print(f"  Zone Distribution:            Low(1-{z1_max}): {avg_low:.1f} balls | Mid({z1_max+1}-{z2_max}): {avg_mid:.1f} balls | High({z2_max+1}-{max_ball}): {avg_high:.1f} balls")
        print("-" * 60)
