#!/usr/bin/env python3
"""
MegaMillions Historical Analysis - Fixed for Local Use
Properly analyzes MegaMillions data to identify actual rule change periods.
"""

import re
import os
from datetime import datetime
from collections import Counter, defaultdict

def parse_megamillions_data(filename):
    """Parse the MegaMillions data file."""
    print("🔍 ANALYZING MEGAMILLIONS HISTORICAL DATA")
    print("=" * 50)
    
    if not os.path.exists(filename):
        print(f"❌ Data file not found: {filename}")
        print("   Please make sure the MegaMillions data file is in the current directory.")
        return []
    
    drawings = []
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line or 'All information' in line or 'Therefore' in line or 'Results for' in line:
            continue
        
        try:
            # Parse format: "9/12/2025; 17,18,21,42,64; Mega Ball: 7"
            parts = line.split(';')
            if len(parts) >= 3:
                date_str = parts[0].strip()
                numbers_str = parts[1].strip()
                ball_str = parts[2].strip()
                
                # Parse date
                date_parts = date_str.split('/')
                if len(date_parts) == 3:
                    month, day, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                    draw_date = datetime(year, month, day)
                    
                    # Parse numbers
                    numbers = [int(x.strip()) for x in numbers_str.split(',')]
                    
                    # Parse mega/money ball
                    if 'Mega Ball:' in ball_str:
                        mega_ball = int(ball_str.split('Mega Ball:')[1].strip())
                        ball_type = 'Mega Ball'
                    elif 'Money Ball:' in ball_str:
                        mega_ball = int(ball_str.split('Money Ball:')[1].strip())
                        ball_type = 'Money Ball'
                    else:
                        continue
                    
                    drawings.append({
                        'date': draw_date,
                        'numbers': sorted(numbers),
                        'mega_ball': mega_ball,
                        'ball_type': ball_type
                    })
        except (ValueError, IndexError) as e:
            continue
    
    # Sort by date (oldest first)
    drawings.sort(key=lambda x: x['date'])
    
    print(f"✅ Parsed {len(drawings)} drawings")
    if drawings:
        print(f"📅 Date range: {drawings[0]['date'].strftime('%Y-%m-%d')} to {drawings[-1]['date'].strftime('%Y-%m-%d')}")
    
    return drawings

def identify_rule_periods(drawings):
    """Identify MegaMillions rule periods based on known history."""
    print(f"\n🔍 IDENTIFYING MEGAMILLIONS RULE PERIODS")
    print("=" * 45)
    
    # Based on MegaMillions history research
    periods = [
        {
            'name': 'Big Game Era',
            'start': datetime(1996, 9, 6),
            'end': datetime(2002, 5, 14),
            'white_range': (1, 50),
            'mega_range': (1, 25),
            'ball_name': 'Money Ball'
        },
        {
            'name': 'Early Mega Millions',
            'start': datetime(2002, 5, 15),
            'end': datetime(2005, 6, 21),
            'white_range': (1, 52),
            'mega_range': (1, 52),
            'ball_name': 'Mega Ball'
        },
        {
            'name': 'Mega Millions v2',
            'start': datetime(2005, 6, 22),
            'end': datetime(2013, 10, 18),
            'white_range': (1, 56),
            'mega_range': (1, 46),
            'ball_name': 'Mega Ball'
        },
        {
            'name': 'Mega Millions v3',
            'start': datetime(2013, 10, 19),
            'end': datetime(2017, 10, 27),
            'white_range': (1, 75),
            'mega_range': (1, 15),
            'ball_name': 'Mega Ball'
        },
        {
            'name': 'Current Format',
            'start': datetime(2017, 10, 28),
            'end': datetime(2025, 4, 7),
            'white_range': (1, 70),
            'mega_range': (1, 25),
            'ball_name': 'Mega Ball'
        },
        {
            'name': 'New Format 2025',
            'start': datetime(2025, 4, 8),
            'end': datetime(2030, 12, 31),  # Future end date
            'white_range': (1, 70),
            'mega_range': (1, 24),
            'ball_name': 'Mega Ball'
        }
    ]
    
    # Assign drawings to periods
    for period in periods:
        period['drawings'] = []
    
    for drawing in drawings:
        for period in periods:
            if period['start'] <= drawing['date'] <= period['end']:
                period['drawings'].append(drawing)
                break
    
    # Filter out empty periods and display
    active_periods = [p for p in periods if p['drawings']]
    
    for i, period in enumerate(active_periods, 1):
        print(f"\n📊 PERIOD {i}: {period['name']}")
        print(f"   Dates: {period['start'].strftime('%Y-%m-%d')} to {period['end'].strftime('%Y-%m-%d')}")
        print(f"   Format: 5 from {period['white_range'][0]}-{period['white_range'][1]}, "
              f"{period['ball_name']} {period['mega_range'][0]}-{period['mega_range'][1]}")
        print(f"   Drawings: {len(period['drawings'])}")
        
        if period['drawings']:
            actual_start = period['drawings'][0]['date'].strftime('%Y-%m-%d')
            actual_end = period['drawings'][-1]['date'].strftime('%Y-%m-%d')
            print(f"   Actual data: {actual_start} to {actual_end}")
    
    return active_periods

def analyze_current_period(periods):
    """Analyze the most recent period with substantial data."""
    # Find the period with the most recent substantial data
    current_period = None
    for period in reversed(periods):
        if len(period['drawings']) >= 50:  # Need substantial data
            current_period = period
            break
    
    if not current_period:
        current_period = periods[-1]  # Fallback to most recent
    
    print(f"\n🎯 CURRENT PERIOD ANALYSIS: {current_period['name']}")
    print("=" * 60)
    print(f"Format: 5 from {current_period['white_range'][0]}-{current_period['white_range'][1]}, "
          f"{current_period['ball_name']} {current_period['mega_range'][0]}-{current_period['mega_range'][1]}")
    print(f"Drawings analyzed: {len(current_period['drawings'])}")
    
    if len(current_period['drawings']) < 10:
        print("⚠️  Insufficient data for reliable analysis. Using previous period data.")
        # Find previous period with more data
        for period in reversed(periods[:-1]):
            if len(period['drawings']) >= 100:
                current_period = period
                print(f"📊 Using {period['name']} data instead ({len(period['drawings'])} drawings)")
                break
    
    # Frequency analysis
    all_whites = []
    all_megas = []
    
    for drawing in current_period['drawings']:
        all_whites.extend(drawing['numbers'])
        all_megas.append(drawing['mega_ball'])
    
    white_freq = Counter(all_whites)
    mega_freq = Counter(all_megas)
    
    print(f"\n🔢 TOP 15 MOST FREQUENT WHITE BALLS:")
    for i, (num, count) in enumerate(white_freq.most_common(15), 1):
        pct = (count / len(current_period['drawings'])) * 100
        print(f"  {i:2d}. {num:2d} ({count:3d} times, {pct:.1f}%)")
    
    print(f"\n🔴 TOP 10 MOST FREQUENT {current_period['ball_name']}S:")
    for i, (num, count) in enumerate(mega_freq.most_common(10), 1):
        pct = (count / len(current_period['drawings'])) * 100
        print(f"  {i:2d}. {num:2d} ({count:3d} times, {pct:.1f}%)")
    
    # Odd/even analysis
    odd_counts = []
    sums = []
    
    for drawing in current_period['drawings']:
        odd_count = sum(1 for n in drawing['numbers'] if n % 2 == 1)
        odd_counts.append(odd_count)
        sums.append(sum(drawing['numbers']))
    
    odd_dist = Counter(odd_counts)
    print(f"\n⚖️  ODD/EVEN DISTRIBUTION:")
    for odd_count in range(6):
        count = odd_dist.get(odd_count, 0)
        if count > 0:
            pct = (count / len(current_period['drawings'])) * 100
            print(f"  {odd_count} odd, {5-odd_count} even: {count:3d} times ({pct:.1f}%)")
    
    print(f"\n➕ SUM STATISTICS:")
    print(f"  Range: {min(sums)} - {max(sums)}")
    print(f"  Average: {sum(sums)/len(sums):.1f}")
    print(f"  Median: {sorted(sums)[len(sums)//2]:.1f}")
    
    # Decade analysis for current format
    if current_period['white_range'][1] == 70:  # Current 1-70 format
        decades = {
            '1-10': [n for n in all_whites if 1 <= n <= 10],
            '11-20': [n for n in all_whites if 11 <= n <= 20],
            '21-30': [n for n in all_whites if 21 <= n <= 30],
            '31-40': [n for n in all_whites if 31 <= n <= 40],
            '41-50': [n for n in all_whites if 41 <= n <= 50],
            '51-60': [n for n in all_whites if 51 <= n <= 60],
            '61-70': [n for n in all_whites if 61 <= n <= 70]
        }
        
        print(f"\n📊 DECADE DISTRIBUTION:")
        for decade, numbers in decades.items():
            count = len(numbers)
            expected = len(current_period['drawings']) * 5 * (10/70)  # Expected for 10 numbers out of 70
            if decade == '61-70':
                expected = len(current_period['drawings']) * 5 * (10/70)  # Only 10 numbers in this range
            pct = (count / (len(current_period['drawings']) * 5)) * 100
            print(f"  {decade}: {count:3d} times ({pct:.1f}%) - Expected: {expected:.1f}")
    
    # Generate recommendations
    top_whites = [num for num, _ in white_freq.most_common(15)]
    top_megas = [num for num, _ in mega_freq.most_common(10)]
    
    # Find most common odd/even patterns
    most_common_odd = odd_dist.most_common(2)
    optimal_odds = [count for count, _ in most_common_odd]
    
    # Conservative sum range (middle 80%)
    sorted_sums = sorted(sums)
    sum_10th = sorted_sums[len(sorted_sums)//10]
    sum_90th = sorted_sums[9*len(sorted_sums)//10]
    
    recommendations = {
        'period_name': current_period['name'],
        'white_range': current_period['white_range'],
        'mega_range': current_period['mega_range'],
        'ball_name': current_period['ball_name'],
        'top_whites': top_whites,
        'top_megas': top_megas,
        'optimal_odd_counts': optimal_odds,
        'sum_range': (sum_10th, sum_90th),
        'mean_sum': int(sum(sums)/len(sums)),
        'drawing_count': len(current_period['drawings'])
    }
    
    print(f"\n💡 RECOMMENDATIONS FOR TICKET GENERATION:")
    print(f"  Focus on white balls: {', '.join(map(str, top_whites[:10]))}")
    print(f"  Focus on {current_period['ball_name']}s: {', '.join(map(str, top_megas[:5]))}")
    print(f"  Optimal odd/even: {optimal_odds[0]} or {optimal_odds[1] if len(optimal_odds) > 1 else optimal_odds[0]} odd")
    print(f"  Target sum range: {sum_10th} - {sum_90th}")
    
    return recommendations, periods

def main():
    """Main analysis function."""
    # Look for the data file in current directory
    possible_filenames = [
        'MegaMillions_9_15_2025.txt',
        'megamillions_data.txt',
        'megamillions_historical_data.txt'
    ]
    
    filename = None
    for fname in possible_filenames:
        if os.path.exists(fname):
            filename = fname
            break
    
    if not filename:
        print("❌ No MegaMillions data file found in current directory.")
        print("   Looking for one of these files:")
        for fname in possible_filenames:
            print(f"   - {fname}")
        print("\n   Please make sure your MegaMillions data file is in the current directory.")
        return None
    
    print(f"📁 Using data file: {filename}")
    
    # Parse the data
    drawings = parse_megamillions_data(filename)
    
    if not drawings:
        print("❌ No valid drawings found in data file.")
        return None
    
    # Identify rule periods
    periods = identify_rule_periods(drawings)
    
    # Analyze current period
    recommendations, all_periods = analyze_current_period(periods)
    
    # Save analysis results
    import json
    
    analysis_data = {
        'total_drawings': len(drawings),
        'periods': [],
        'current_recommendations': recommendations
    }
    
    for period in all_periods:
        period_data = {
            'name': period['name'],
            'start_date': period['start'].isoformat(),
            'end_date': period['end'].isoformat(),
            'white_range': period['white_range'],
            'mega_range': period['mega_range'],
            'ball_name': period['ball_name'],
            'drawing_count': len(period['drawings'])
        }
        analysis_data['periods'].append(period_data)
    
    with open('megamillions_analysis_results.json', 'w') as f:
        json.dump(analysis_data, f, indent=2)
    
    print(f"\n✅ Analysis complete! Results saved to 'megamillions_analysis_results.json'")
    print(f"📊 Ready to build MegaMillions Suite with {len(periods)} identified periods")
    
    return analysis_data

if __name__ == "__main__":
    main()
