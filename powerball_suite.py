#!/usr/bin/env python3
"""
Powerball Suite - All-in-One Application
Complete Powerball analysis, generation, and checking system.

Features:
- Generate statistically-informed tickets
- View saved tickets
- Check tickets against historical data
- Update historical database
- Comprehensive analysis and reporting
"""

import json
import csv
import glob
import os
import random
import urllib.request
from datetime import datetime
from collections import Counter, defaultdict

class PowerballSuite:
    def __init__(self):
        """Initialize the Powerball Suite."""
        self.data_file = "powerball_historical_data.csv"
        self.historical_data = []
        
        # Statistical data from analysis (2015-Present)
        self.top_white_balls = [61, 21, 23, 33, 69, 64, 27, 62, 32, 63, 36, 53, 59, 20, 37]
        self.top_powerballs = [4, 21, 24, 18, 25, 9, 14, 5, 20, 3]
        
        self.white_ball_weights = {
            61: 9.3, 21: 9.0, 23: 9.0, 33: 8.7, 69: 8.6, 64: 8.5, 27: 8.4, 
            62: 8.3, 32: 8.3, 63: 8.3, 36: 8.2, 53: 8.1, 59: 8.0, 20: 7.9, 37: 7.9
        }
        
        self.powerball_weights = {
            4: 4.8, 21: 4.7, 24: 4.6, 18: 4.6, 25: 4.5, 9: 4.4, 14: 4.4, 
            5: 4.3, 20: 4.2, 3: 3.9
        }
        
        self.optimal_odd_counts = [2, 3]
        self.sum_range = (148, 206)
        self.all_white_balls = list(range(1, 70))
        self.all_powerballs = list(range(1, 27))
        
        # Prize tiers
        self.prize_tiers = {
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
    
    def show_main_menu(self):
        """Display the main menu."""
        print("\n" + "="*60)
        print("🎱 POWERBALL SUITE - Statistical Lottery System")
        print("="*60)
        print("1. 🎲 Generate New Tickets")
        print("2. 📋 View Saved Tickets") 
        print("3. 🔍 Check Tickets Against Historical Data")
        print("4. 📊 Update Historical Database")
        print("5. 📈 Show Statistics & Analysis")
        print("6. ❓ Help & Information")
        print("7. 🚪 Exit")
        print("="*60)
    
    def update_database(self):
        """Download and update the historical database."""
        print("\n📊 UPDATING HISTORICAL DATABASE")
        print("="*40)
        
        url = "https://www.texaslottery.com/export/sites/lottery/Games/Powerball/Winning_Numbers/powerball.csv"
        
        try:
            print("🌐 Downloading latest data from Texas Lottery...")
            urllib.request.urlretrieve(url, self.data_file)
            print(f"✅ Successfully downloaded to {self.data_file}")
            
            # Load and validate the data
            self.load_historical_data()
            print(f"✅ Database updated with {len(self.historical_data)} drawings")
            
        except Exception as e:
            print(f"❌ Error updating database: {e}")
            print("💡 You can manually download from:")
            print(f"   {url}")
    
    def load_historical_data(self):
        """Load historical data from CSV file."""
        self.historical_data = []
        
        if not os.path.exists(self.data_file):
            print(f"⚠️  Historical data file not found: {self.data_file}")
            print("   Use option 4 to download the database first.")
            return False
        
        try:
            with open(self.data_file, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 11:
                        try:
                            month, day, year = int(row[1]), int(row[2]), int(row[3])
                            white_balls = [int(row[i]) for i in range(4, 9)]
                            powerball = int(row[9])
                            
                            draw_date = datetime(year, month, day)
                            
                            # Only current format (2015-present)
                            if draw_date >= datetime(2015, 10, 4):
                                self.historical_data.append({
                                    'date': draw_date,
                                    'white_balls': sorted(white_balls),
                                    'powerball': powerball
                                })
                        except (ValueError, IndexError):
                            continue
            
            print(f"📊 Loaded {len(self.historical_data)} historical drawings")
            return True
            
        except Exception as e:
            print(f"❌ Error loading historical data: {e}")
            return False
    
    def generate_tickets(self):
        """Generate new tickets using statistical algorithms."""
        print("\n🎲 GENERATE NEW TICKETS")
        print("="*30)
        
        # Get number of tickets
        while True:
            try:
                num_tickets = int(input("How many tickets to generate? "))
                if num_tickets > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get algorithm choice
        print("\nSelect algorithm:")
        print("1. Frequency-based (uses historical frequency weights)")
        print("2. Pattern-based (follows optimal statistical patterns)")
        print("3. Balanced (recommended - combines strategies)")
        print("4. 🧠 Prophet & Pragmatist (Autonomous Combinatorial Wheeling)")
        
        while True:
            try:
                choice = int(input("Choose algorithm (1-4): "))
                if choice in [1, 2, 3, 4]:
                    algorithms = {1: 'frequency', 2: 'pattern', 3: 'balanced', 4: 'prophet_wheel'}
                    algorithm = algorithms[choice]
                    break
                else:
                    print("Please enter 1, 2, 3, or 4.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Generate tickets
        print(f"\n🎯 Generating {num_tickets} tickets using {algorithm} algorithm...")
        tickets = []
        
        if algorithm == 'prophet_wheel':
            # JMc - [2026-03-07] - Hooking up the big brain engine for Powerball.
            from lottery_math_engine import LotteryMathEngine
            
            if not self.historical_data:
                print("⚠️  The Prophet algorithm requires historical data to function.")
                if not self.load_historical_data():
                    print("❌ Aborting. Please download the historical database first.")
                    return
            
            # Format the history for the engine
            formatted_history = []
            for draw in self.historical_data:
                formatted_history.append({
                    'date': draw['date'],
                    'white_balls': draw['white_balls'],
                    'special_ball': draw['powerball']
                })
                
            engine = LotteryMathEngine(formatted_history, self.all_white_balls[-1], self.all_powerballs[-1])
            
            print("\n🔮 Prophet: Running Markov Chains & Poisson Overdue Analysis...")
            pool, special_pool = engine.generate_smart_pool(pool_size=15, special_pool_size=3)
            print(f"   [Autonomous Pool Selected]: {pool}")
            print(f"   [Special Balls Selected]: {special_pool}")
            
            print("\n⚙️  Pragmatist: Applying Greedy Combinatorial Wheeling for Maximum Coverage...")
            wheeled_tickets = engine.generate_wheeled_tickets(pool, special_pool, num_tickets)
            
            for w_white, w_special in wheeled_tickets:
                tickets.append({
                    'white_balls': w_white,
                    'powerball': w_special,
                    'algorithm': algorithm,
                    'generated_at': datetime.now().isoformat()
                })
        else:
            for i in range(num_tickets):
                if algorithm == 'frequency':
                    white_balls, powerball = self._frequency_generation()
                elif algorithm == 'pattern':
                    white_balls, powerball = self._pattern_generation()
                else:  # balanced
                    white_balls, powerball = self._balanced_generation()
                
                tickets.append({
                    'white_balls': white_balls,
                    'powerball': powerball,
                    'algorithm': algorithm,
                    'generated_at': datetime.now().isoformat()
                })
        
        # Display tickets
        print(f"\n🎫 YOUR GENERATED TICKETS:")
        print("-" * 40)
        for i, ticket in enumerate(tickets, 1):
            white_str = " ".join(f"{n:02d}" for n in ticket['white_balls'])
            odd_count = sum(1 for n in ticket['white_balls'] if n % 2 == 1)
            ball_sum = sum(ticket['white_balls'])
            print(f"#{i:02d}: {white_str}   🔴 {ticket['powerball']:02d}   "
                  f"({odd_count} odd, sum={ball_sum})")
        
        # Save tickets
        filename = f"powerball_tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(tickets, f, indent=2)
        
        print(f"\n💾 Tickets saved to: {filename}")
        
        # Show quick analysis
        self._show_ticket_analysis(tickets)
    
    def _frequency_generation(self):
        """Generate using frequency weights."""
        white_balls = []
        weighted_pool = []
        
        for num in self.all_white_balls:
            weight = self.white_ball_weights.get(num, 5.0)
            weighted_pool.extend([num] * int(weight * 10))
        
        while len(white_balls) < 5:
            selected = random.choice(weighted_pool)
            if selected not in white_balls:
                white_balls.append(selected)
        
        pb_weighted_pool = []
        for num in self.all_powerballs:
            weight = self.powerball_weights.get(num, 3.0)
            pb_weighted_pool.extend([num] * int(weight * 10))
        
        powerball = random.choice(pb_weighted_pool)
        return sorted(white_balls), powerball
    
    def _pattern_generation(self):
        """Generate following statistical patterns."""
        attempts = 0
        while attempts < 1000:
            white_balls = random.sample(self.all_white_balls, 5)
            odd_count = sum(1 for n in white_balls if n % 2 == 1)
            ball_sum = sum(white_balls)
            
            if (odd_count in self.optimal_odd_counts and 
                self.sum_range[0] <= ball_sum <= self.sum_range[1]):
                powerball = random.choice(self.top_powerballs) if random.random() < 0.6 else random.choice(self.all_powerballs)
                return sorted(white_balls), powerball
            
            attempts += 1
        
        return self._frequency_generation()  # Fallback
    
    def _balanced_generation(self):
        """Generate using balanced approach."""
        white_balls = []
        
        # Take 2-3 from top frequent
        num_from_top = random.randint(2, 3)
        white_balls.extend(random.sample(self.top_white_balls[:10], num_from_top))
        
        # Fill remaining
        remaining = [n for n in self.all_white_balls if n not in white_balls]
        white_balls.extend(random.sample(remaining, 5 - len(white_balls)))
        
        # Adjust for odd/even if needed
        odd_count = sum(1 for n in white_balls if n % 2 == 1)
        if odd_count not in self.optimal_odd_counts:
            target_odd = random.choice(self.optimal_odd_counts)
            if odd_count < target_odd:
                # Need more odd
                for i, num in enumerate(white_balls):
                    if num % 2 == 0:  # Even number
                        odd_candidates = [n for n in remaining if n % 2 == 1]
                        if odd_candidates:
                            white_balls[i] = random.choice(odd_candidates)
                            break
        
        powerball = random.choice(self.top_powerballs) if random.random() < 0.5 else random.choice(self.all_powerballs)
        return sorted(white_balls), powerball
    
    def _show_ticket_analysis(self, tickets):
        """Show quick analysis of generated tickets."""
        if len(tickets) < 2:
            return
        
        print(f"\n📊 QUICK ANALYSIS:")
        print("-" * 20)
        
        # Odd/even distribution
        odd_dist = Counter()
        sums = []
        pbs = []
        
        for ticket in tickets:
            odd_count = sum(1 for n in ticket['white_balls'] if n % 2 == 1)
            odd_dist[f"{odd_count} odd"] += 1
            sums.append(sum(ticket['white_balls']))
            pbs.append(ticket['powerball'])
        
        print("Odd/Even Distribution:")
        for pattern, count in odd_dist.most_common():
            pct = (count / len(tickets)) * 100
            print(f"  {pattern}: {count} tickets ({pct:.1f}%)")
        
        print(f"Sum Range: {min(sums)} - {max(sums)} (avg: {sum(sums)/len(sums):.1f})")
        
        pb_dist = Counter(pbs)
        print("Top Powerballs:")
        for pb, count in pb_dist.most_common(3):
            pct = (count / len(tickets)) * 100
            print(f"  {pb}: {count} times ({pct:.1f}%)")
    
    def view_tickets(self):
        """View saved ticket files."""
        print("\n📋 VIEW SAVED TICKETS")
        print("="*25)
        
        ticket_files = glob.glob("powerball_tickets_*.json")
        
        if not ticket_files:
            print("❌ No saved ticket files found.")
            print("   Generate some tickets first (option 1).")
            return
        
        if len(ticket_files) == 1:
            self._display_ticket_file(ticket_files[0])
        else:
            print(f"📁 Found {len(ticket_files)} ticket files:")
            for i, filename in enumerate(ticket_files, 1):
                stat = os.stat(filename)
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                print(f"  {i}. {filename} ({mod_time.strftime('%Y-%m-%d %H:%M')})")
            
            print(f"  {len(ticket_files) + 1}. View all files")
            
            while True:
                try:
                    choice = int(input(f"Select file (1-{len(ticket_files) + 1}): "))
                    if 1 <= choice <= len(ticket_files):
                        self._display_ticket_file(ticket_files[choice - 1])
                        break
                    elif choice == len(ticket_files) + 1:
                        for filename in ticket_files:
                            self._display_ticket_file(filename)
                            print()
                        break
                    else:
                        print(f"Please enter 1-{len(ticket_files) + 1}")
                except ValueError:
                    print("Please enter a valid number")
    
    def _display_ticket_file(self, filename):
        """Display tickets from a specific file."""
        try:
            with open(filename, 'r') as f:
                tickets = json.load(f)
            
            print(f"\n📋 {filename}")
            print("-" * 50)
            
            if tickets:
                first_ticket = tickets[0]
                algorithm = first_ticket.get('algorithm', 'unknown')
                generated_time = first_ticket.get('generated_at', 'unknown')
                
                print(f"Algorithm: {algorithm.title()}")
                print(f"Generated: {self._format_datetime(generated_time)}")
                print(f"Count: {len(tickets)} tickets")
                print("-" * 30)
                
                for i, ticket in enumerate(tickets, 1):
                    white_str = " ".join(f"{n:02d}" for n in ticket['white_balls'])
                    odd_count = sum(1 for n in ticket['white_balls'] if n % 2 == 1)
                    ball_sum = sum(ticket['white_balls'])
                    
                    print(f"#{i:02d}: {white_str}   🔴 {ticket['powerball']:02d}   "
                          f"({odd_count} odd, sum={ball_sum})")
            else:
                print("No tickets in file.")
                
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    
    def check_tickets(self):
        """Check tickets against historical data."""
        print("\n🔍 CHECK TICKETS AGAINST HISTORICAL DATA")
        print("="*45)
        
        # Load historical data if not already loaded
        if not self.historical_data:
            if not self.load_historical_data():
                print("💡 Use option 4 to download historical data first.")
                return
        
        # Find ticket files
        ticket_files = glob.glob("powerball_tickets_*.json")
        if not ticket_files:
            print("❌ No ticket files found.")
            print("   Generate some tickets first (option 1).")
            return
        
        # Select ticket file
        if len(ticket_files) == 1:
            ticket_file = ticket_files[0]
        else:
            print(f"📁 Found {len(ticket_files)} ticket files:")
            for i, f in enumerate(ticket_files, 1):
                print(f"  {i}. {f}")
            
            while True:
                try:
                    choice = int(input(f"Select file (1-{len(ticket_files)}): "))
                    if 1 <= choice <= len(ticket_files):
                        ticket_file = ticket_files[choice - 1]
                        break
                    else:
                        print(f"Please enter 1-{len(ticket_files)}")
                except ValueError:
                    print("Please enter a valid number")
        
        # Load and check tickets
        try:
            with open(ticket_file, 'r') as f:
                tickets = json.load(f)
            
            print(f"\n🎫 Checking {len(tickets)} tickets against {len(self.historical_data)} historical drawings...")
            self._analyze_ticket_performance(tickets)
            
        except Exception as e:
            print(f"❌ Error loading tickets: {e}")
    
    def _analyze_ticket_performance(self, tickets):
        """Analyze ticket performance against historical data."""
        print("\n🔍 ANALYSIS RESULTS:")
        print("="*30)
        
        total_matches = 0
        prize_summary = defaultdict(int)
        winning_tickets = 0
        
        for i, ticket in enumerate(tickets, 1):
            matches = self._check_single_ticket(ticket)
            
            if matches:
                winning_tickets += 1
                total_matches += len(matches)
                
                print(f"\n🎫 TICKET #{i}: {' '.join(f'{n:02d}' for n in ticket['white_balls'])} 🔴 {ticket['powerball']:02d}")
                print(f"   Found {len(matches)} historical wins:")
                
                for match in matches:
                    prize_summary[match['prize']] += 1
                    winning_nums = match['winning_numbers']
                    winning_white = winning_nums[:-1]
                    winning_pb = winning_nums[-1]
                    
                    print(f"   📅 {match['date'].strftime('%Y-%m-%d')}: "
                          f"{' '.join(f'{n:02d}' for n in winning_white)} 🔴 {winning_pb:02d} "
                          f"({match['white_matches']}+PB:{match['pb_match']}) → {match['prize']}")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print("-" * 20)
        print(f"Total tickets: {len(tickets)}")
        print(f"Winning tickets: {winning_tickets}")
        print(f"Total matches: {total_matches}")
        
        if prize_summary:
            print(f"\n🏆 PRIZES WON:")
            total_value = 0
            for prize, count in sorted(prize_summary.items(), key=lambda x: x[1], reverse=True):
                print(f"   {prize}: {count} times")
                # Rough value calculation (excluding jackpots)
                if "$1,000,000" in prize:
                    total_value += count * 1000000
                elif "$50,000" in prize:
                    total_value += count * 50000
                elif "$100" in prize:
                    total_value += count * 100
                elif "$7" in prize:
                    total_value += count * 7
                elif "$4" in prize:
                    total_value += count * 4
            
            if total_value > 0:
                print(f"\n💰 Estimated total winnings: ${total_value:,}")
                cost = len(tickets) * len(self.historical_data) * 2  # $2 per ticket per drawing
                print(f"💸 Cost if played historically: ${cost:,}")
                if cost > 0:
                    roi = ((total_value - cost) / cost) * 100
                    print(f"📈 ROI: {roi:.1f}%")
        else:
            print("❌ No winning matches found")
        
        # Performance comparison
        expected_matches = len(tickets) * len(self.historical_data) * 0.0347  # ~3.47% win rate
        print(f"\n🎲 vs Random Expectation:")
        print(f"   Your tickets: {total_matches} matches")
        print(f"   Random expectation: ~{expected_matches:.1f} matches")
        if expected_matches > 0:
            performance = (total_matches / expected_matches) * 100
            print(f"   Performance: {performance:.1f}% of random")
    
    def _check_single_ticket(self, ticket):
        """Check a single ticket against historical data."""
        ticket_white = sorted(ticket['white_balls'])
        ticket_pb = ticket['powerball']
        matches = []
        
        for draw in self.historical_data:
            white_matches = len(set(ticket_white) & set(draw['white_balls']))
            pb_match = (ticket_pb == draw['powerball'])
            
            if (white_matches, pb_match) in self.prize_tiers:
                matches.append({
                    'date': draw['date'],
                    'white_matches': white_matches,
                    'pb_match': pb_match,
                    'prize': self.prize_tiers[(white_matches, pb_match)],
                    'winning_numbers': draw['white_balls'] + [draw['powerball']]
                })
        
        return matches
    
    def show_statistics(self):
        """Show comprehensive statistics and analysis."""
        print("\n📈 STATISTICS & ANALYSIS")
        print("="*30)
        
        if not self.historical_data:
            if not self.load_historical_data():
                print("💡 Use option 4 to download historical data first.")
                return
        
        print(f"📊 Historical Data: {len(self.historical_data)} drawings")
        print(f"📅 Date Range: {self.historical_data[0]['date'].strftime('%Y-%m-%d')} to {self.historical_data[-1]['date'].strftime('%Y-%m-%d')}")
        
        # Frequency analysis
        all_white_balls = []
        all_powerballs = []
        
        for draw in self.historical_data:
            all_white_balls.extend(draw['white_balls'])
            all_powerballs.append(draw['powerball'])
        
        white_freq = Counter(all_white_balls)
        pb_freq = Counter(all_powerballs)
        
        print(f"\n🎯 TOP 10 MOST FREQUENT WHITE BALLS:")
        for i, (num, count) in enumerate(white_freq.most_common(10), 1):
            pct = (count / len(self.historical_data)) * 100
            print(f"  {i:2d}. {num:2d} ({count:3d} times, {pct:.1f}%)")
        
        print(f"\n🔴 TOP 10 MOST FREQUENT POWERBALLS:")
        for i, (num, count) in enumerate(pb_freq.most_common(10), 1):
            pct = (count / len(self.historical_data)) * 100
            print(f"  {i:2d}. {num:2d} ({count:3d} times, {pct:.1f}%)")
        
        # Odd/even analysis
        odd_counts = []
        sums = []
        
        for draw in self.historical_data:
            odd_count = sum(1 for n in draw['white_balls'] if n % 2 == 1)
            odd_counts.append(odd_count)
            sums.append(sum(draw['white_balls']))
        
        odd_dist = Counter(odd_counts)
        print(f"\n⚖️  ODD/EVEN DISTRIBUTION:")
        for odd_count in range(6):
            count = odd_dist.get(odd_count, 0)
            if count > 0:
                pct = (count / len(self.historical_data)) * 100
                print(f"  {odd_count} odd, {5-odd_count} even: {count:3d} times ({pct:.1f}%)")
        
        print(f"\n➕ SUM STATISTICS:")
        print(f"  Range: {min(sums)} - {max(sums)}")
        print(f"  Average: {sum(sums)/len(sums):.1f}")
        print(f"  Optimal range: {self.sum_range[0]} - {self.sum_range[1]}")
    
    def show_help(self):
        """Show help and information."""
        print("\n❓ HELP & INFORMATION")
        print("="*25)
        print("""
🎱 POWERBALL SUITE GUIDE

This application uses statistical analysis of historical Powerball data
to generate tickets that follow observed patterns rather than pure randomness.

KEY FEATURES:
• Generate tickets using 3 different algorithms
• View and analyze your saved tickets  
• Check tickets against historical winning numbers
• Update database with latest drawings
• Comprehensive statistical analysis

ALGORITHMS:
1. Frequency-based: Favors numbers that appear most often historically
2. Pattern-based: Follows optimal odd/even and sum patterns
3. Balanced: Combines frequency and pattern approaches (recommended)

IMPORTANT NOTES:
• This is still a game of chance - no system guarantees wins
• Past performance doesn't predict future results
• Use for entertainment and educational purposes
• Always play responsibly

The system analyzes data from October 2015 to present (current Powerball format).
        """)
    
    def _format_datetime(self, iso_string):
        """Format datetime string for display."""
        try:
            dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return iso_string
    
    def run(self):
        """Main application loop."""
        print("🎱 Welcome to Powerball Suite!")
        print("Statistical Lottery Analysis & Generation System")
        
        while True:
            self.show_main_menu()
            
            try:
                choice = input("\nSelect option (1-7): ").strip()
                
                if choice == '1':
                    self.generate_tickets()
                elif choice == '2':
                    self.view_tickets()
                elif choice == '3':
                    self.check_tickets()
                elif choice == '4':
                    self.update_database()
                elif choice == '5':
                    self.show_statistics()
                elif choice == '6':
                    self.show_help()
                elif choice == '7':
                    print("\n👋 Thanks for using Powerball Suite!")
                    print("Good luck with your tickets! 🍀")
                    break
                else:
                    print("❌ Invalid choice. Please select 1-7.")
                
                if choice != '7':
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                input("Press Enter to continue...")

def main():
    """Main entry point."""
    app = PowerballSuite()
    app.run()

if __name__ == "__main__":
    main()
