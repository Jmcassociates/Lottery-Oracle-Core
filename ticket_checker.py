#!/usr/bin/env python3
"""
Powerball Ticket Checker
Checks generated tickets against historical winning numbers to find matches.
"""

import json
import csv
import glob
from datetime import datetime
from collections import defaultdict

# Powerball prize tiers (current format since 2015)
PRIZE_TIERS = {
    (5, True): "JACKPOT! 🎉💰",
    (5, False): "$1,000,000 🏆",
    (4, True): "$50,000 💎",
    (4, False): "$100 💵",
    (3, True): "$100 💵",
    (3, False): "$7 🎫",
    (2, True): "$7 🎫",
    (1, True): "$4 🎫",
    (0, True): "$4 🎫"
}

def load_historical_data(csv_file):
    """Load historical winning numbers from CSV file."""
    historical_draws = []
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 11:  # Texas format: Game, Month, Day, Year, Num1-5, PB, PowerPlay
                    try:
                        # Parse the row
                        game, month, day, year = row[0], int(row[1]), int(row[2]), int(row[3])
                        white_balls = [int(row[i]) for i in range(4, 9)]  # Positions 4-8
                        powerball = int(row[9])
                        
                        # Create date
                        draw_date = datetime(year, month, day)
                        
                        # Only include current format (2015-present)
                        if draw_date >= datetime(2015, 10, 4):
                            historical_draws.append({
                                'date': draw_date,
                                'white_balls': sorted(white_balls),
                                'powerball': powerball
                            })
                    except (ValueError, IndexError):
                        continue  # Skip malformed rows
        
        print(f"✅ Loaded {len(historical_draws)} historical draws (2015-present)")
        return historical_draws
        
    except FileNotFoundError:
        print(f"❌ Historical data file not found: {csv_file}")
        return []
    except Exception as e:
        print(f"❌ Error loading historical data: {e}")
        return []

def check_ticket_matches(ticket, historical_draws):
    """Check a single ticket against all historical draws."""
    ticket_white = sorted(ticket['white_balls'])
    ticket_pb = ticket['powerball']
    
    matches = []
    
    for draw in historical_draws:
        draw_white = draw['white_balls']
        draw_pb = draw['powerball']
        
        # Count matching white balls
        white_matches = len(set(ticket_white) & set(draw_white))
        
        # Check Powerball match
        pb_match = (ticket_pb == draw_pb)
        
        # Determine prize tier
        if (white_matches, pb_match) in PRIZE_TIERS:
            prize = PRIZE_TIERS[(white_matches, pb_match)]
            matches.append({
                'date': draw['date'],
                'white_matches': white_matches,
                'pb_match': pb_match,
                'prize': prize,
                'winning_numbers': draw_white + [draw_pb]
            })
    
    return matches

def analyze_ticket_performance(tickets, historical_draws):
    """Analyze all tickets against historical data."""
    print("\n🔍 CHECKING TICKETS AGAINST HISTORICAL WINS...")
    print("=" * 60)
    
    total_matches = 0
    prize_summary = defaultdict(int)
    ticket_results = []
    
    for i, ticket in enumerate(tickets, 1):
        matches = check_ticket_matches(ticket, historical_draws)
        
        if matches:
            total_matches += len(matches)
            print(f"\n🎫 TICKET #{i}: {' '.join(f'{n:02d}' for n in ticket['white_balls'])} PB:{ticket['powerball']:02d}")
            print(f"   Found {len(matches)} historical matches:")
            
            for match in matches:
                prize_summary[match['prize']] += 1
                winning_nums = match['winning_numbers']
                winning_white = winning_nums[:-1]
                winning_pb = winning_nums[-1]
                
                print(f"   📅 {match['date'].strftime('%Y-%m-%d')}: "
                      f"{' '.join(f'{n:02d}' for n in winning_white)} PB:{winning_pb:02d} "
                      f"({match['white_matches']} + PB:{match['pb_match']}) → {match['prize']}")
        
        ticket_results.append({
            'ticket_num': i,
            'ticket': ticket,
            'matches': matches,
            'match_count': len(matches)
        })
    
    # Summary statistics
    print(f"\n📊 SUMMARY STATISTICS")
    print("=" * 40)
    print(f"Total tickets checked: {len(tickets)}")
    print(f"Tickets with matches: {sum(1 for r in ticket_results if r['match_count'] > 0)}")
    print(f"Total historical matches: {total_matches}")
    
    if prize_summary:
        print(f"\n🏆 PRIZE BREAKDOWN:")
        for prize, count in sorted(prize_summary.items(), key=lambda x: x[1], reverse=True):
            print(f"   {prize}: {count} times")
    else:
        print(f"\n❌ No winning matches found in historical data")
    
    # Performance metrics
    if len(tickets) > 0 and len(historical_draws) > 0:
        match_rate = (sum(r['match_count'] for r in ticket_results) / len(tickets) / len(historical_draws)) * 100
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"   Average matches per ticket: {sum(r['match_count'] for r in ticket_results) / len(tickets):.2f}")
        print(f"   Match rate: {match_rate:.6f}% (matches per ticket per draw)")
        
        # Compare to random expectation
        print(f"\n🎲 COMPARISON TO RANDOM:")
        print(f"   Your tickets found {total_matches} matches")
        print(f"   Random expectation: ~{len(tickets) * len(historical_draws) * 0.0347:.1f} matches")
        print(f"   (Based on ~3.47% chance of any prize per ticket)")
    
    return ticket_results

def find_files():
    """Find ticket JSON files and historical CSV file."""
    ticket_files = glob.glob("powerball_tickets_*.json")
    csv_files = glob.glob("*powerball*.csv")
    
    return ticket_files, csv_files

def main():
    """Main function to check tickets."""
    print("🎱 POWERBALL TICKET CHECKER")
    print("=" * 40)
    print("Checking your generated tickets against historical winning numbers...")
    
    # Find files
    ticket_files, csv_files = find_files()
    
    if not ticket_files:
        print("❌ No ticket JSON files found.")
        print("   Looking for: powerball_tickets_*.json")
        return
    
    if not csv_files:
        print("❌ No historical CSV files found.")
        print("   Looking for: *powerball*.csv")
        return
    
    # Select files
    if len(ticket_files) == 1:
        ticket_file = ticket_files[0]
    else:
        print(f"\n📁 Found {len(ticket_files)} ticket files:")
        for i, f in enumerate(ticket_files, 1):
            print(f"   {i}. {f}")
        
        while True:
            try:
                choice = int(input(f"Select ticket file (1-{len(ticket_files)}): "))
                if 1 <= choice <= len(ticket_files):
                    ticket_file = ticket_files[choice - 1]
                    break
                else:
                    print(f"Please enter 1-{len(ticket_files)}")
            except ValueError:
                print("Please enter a number")
    
    if len(csv_files) == 1:
        csv_file = csv_files[0]
    else:
        print(f"\n📁 Found {len(csv_files)} CSV files:")
        for i, f in enumerate(csv_files, 1):
            print(f"   {i}. {f}")
        
        while True:
            try:
                choice = int(input(f"Select CSV file (1-{len(csv_files)}): "))
                if 1 <= choice <= len(csv_files):
                    csv_file = csv_files[choice - 1]
                    break
                else:
                    print(f"Please enter 1-{len(csv_files)}")
            except ValueError:
                print("Please enter a number")
    
    print(f"\n📋 Using ticket file: {ticket_file}")
    print(f"📊 Using historical data: {csv_file}")
    
    # Load data
    try:
        with open(ticket_file, 'r') as f:
            tickets = json.load(f)
        print(f"✅ Loaded {len(tickets)} tickets")
    except Exception as e:
        print(f"❌ Error loading tickets: {e}")
        return
    
    historical_draws = load_historical_data(csv_file)
    if not historical_draws:
        return
    
    # Analyze tickets
    results = analyze_ticket_performance(tickets, historical_draws)
    
    print(f"\n✨ Analysis complete!")
    print(f"Remember: This shows what WOULD have happened if you played these")
    print(f"tickets in past drawings. Past performance doesn't predict future results!")

if __name__ == "__main__":
    main()
