import statistics
from collections import Counter
from app.core.database import SessionLocal
from app.core.models import DrawRecord

def analyze():
    db = SessionLocal()
    draws = db.query(DrawRecord).filter(DrawRecord.game_name == 'NewYorkLotto').all()
    
    if not draws:
        print("No draws found for NewYorkLotto")
        return
        
    print(f"Total Draws Analyzed: {len(draws)}")
    
    odd_even_ratios = Counter()
    max_consecutives = Counter()
    start_balls = []
    
    for draw in draws:
        white_balls = [int(x) for x in draw.white_balls.split(',')]
        white_balls.sort()
        
        # Odd/Even
        odds = sum(1 for n in white_balls if n % 2 != 0)
        evens = len(white_balls) - odds
        odd_even_ratios[f"{odds}:{evens}"] += 1
        
        # Consecutive
        max_seq = 1
        current_seq = 1
        for i in range(1, len(white_balls)):
            if white_balls[i] == white_balls[i-1] + 1:
                current_seq += 1
                if current_seq > max_seq:
                    max_seq = current_seq
            else:
                current_seq = 1
        max_consecutives[max_seq] += 1
        
        # Start ball
        start_balls.append(white_balls[0])
        
    print("\n--- Odd:Even Ratios ---")
    for ratio, count in odd_even_ratios.most_common():
        pct = (count / len(draws)) * 100
        print(f"  {ratio}: {count} times ({pct:.1f}%)")
        
    print("\n--- Max Consecutive Sequences ---")
    for seq, count in sorted(max_consecutives.items()):
        pct = (count / len(draws)) * 100
        print(f"  {seq} in a row: {count} times ({pct:.1f}%)")
        
    print("\n--- Starting Ball Distribution ---")
    print(f"  Average Start Ball: {statistics.mean(start_balls):.1f}")
    
    # Calculate % starting <= 25
    under_26 = sum(1 for x in start_balls if x <= 25)
    pct = (under_26 / len(draws)) * 100
    print(f"  Starts <= 25: {under_26} times ({pct:.1f}%)")
    
    under_15 = sum(1 for x in start_balls if x <= 15)
    pct2 = (under_15 / len(draws)) * 100
    print(f"  Starts <= 15: {under_15} times ({pct2:.1f}%)")

if __name__ == "__main__":
    analyze()
