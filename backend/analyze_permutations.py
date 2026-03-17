import statistics
from collections import Counter
from app.core.database import SessionLocal
from app.core.models import DrawRecord

def analyze_pick_game(game_base_name, num_digits):
    db = SessionLocal()
    
    # Combine Day and Night for analysis
    draws = db.query(DrawRecord).filter(DrawRecord.game_name.like(f"{game_base_name}%")).all()
    if not draws:
        print(f"No draws found for {game_base_name}")
        return

    total_draws = len(draws)
    
    # Metrics
    sums = []
    repeating_counts = {
        "All Unique": 0,
        "One Pair (e.g. 1-1-2)": 0,
        "Two Pairs (e.g. 1-1-2-2)": 0, # For Pick 4/5
        "Three of a kind": 0,
        "Four of a kind": 0,
        "Five of a kind": 0
    }
    
    for d in draws:
        digits = [int(x) for x in d.white_balls.split(",")]
        if len(digits) != num_digits:
            continue
            
        sums.append(sum(digits))
        
        counts = list(Counter(digits).values())
        counts.sort(reverse=True)
        
        if counts[0] == 1:
            repeating_counts["All Unique"] += 1
        elif counts[0] == 2 and (len(counts) == 1 or counts[1] != 2):
            repeating_counts["One Pair (e.g. 1-1-2)"] += 1
        elif counts[0] == 2 and len(counts) > 1 and counts[1] == 2:
            repeating_counts["Two Pairs (e.g. 1-1-2-2)"] += 1
        elif counts[0] == 3:
            repeating_counts["Three of a kind"] += 1
        elif counts[0] == 4:
            repeating_counts["Four of a kind"] += 1
        elif counts[0] == 5:
            repeating_counts["Five of a kind"] += 1

    print(f"\n{game_base_name.upper()} HISTORICAL PERMUTATION ANALYSIS ({total_draws} Draws)")
    print("=" * 60)
    
    # 1. Sum Distribution
    sum_counter = Counter(sums)
    most_common_sums = sum_counter.most_common(5)
    avg_sum = statistics.mean(sums)
    print(f"Average Sum: {avg_sum:.1f}")
    print("Top 5 Most Common Sums:")
    for s, count in most_common_sums:
        pct = (count / total_draws) * 100
        print(f"  Sum {s}: {count} times ({pct:.1f}%)")
        
    # 2. Repeating Digits
    print("\nRepeating Digits Distribution:")
    for k, v in repeating_counts.items():
        if v > 0:
            pct = (v / total_draws) * 100
            print(f"  {k}: {v} times ({pct:.1f}%)")

if __name__ == "__main__":
    analyze_pick_game("Pick3", 3)
    analyze_pick_game("Pick4", 4)
    analyze_pick_game("Pick5", 5)
