#!/usr/bin/env python3
"""
MegaMillions Suite - All-in-One Application (Fixed for Local Use)
Complete MegaMillions analysis, generation, and checking system.

Features:
- Generate statistically-informed tickets
- View saved tickets
- Check tickets against historical data
- Update historical database
- Comprehensive analysis and reporting
- Accounts for multiple rule change periods
"""

import json
import csv
import glob
import os
import random
import urllib.request
import re
from datetime import datetime
from collections import Counter, defaultdict

class MegaMillionsSuite:
    def __init__(self):
        """Initialize the MegaMillions Suite."""
        self.data_file = "megamillions_historical_data.txt"
        self.historical_data = []
        self.periods = []
        
        # Current period statistics (Post-April 2025: 1-70, Mega Ball 1-24)
        self.top_white_balls = [3, 10, 31, 14, 17, 46, 8, 20, 64, 66, 38, 29, 22, 15, 42]
        self.top_mega_balls = [22, 11, 18, 24, 9, 4, 13, 19, 1]
        
        # Frequency weights based on analysis
        self.white_ball_weights = {
            3: 9.3, 10: 9.1, 31: 9.0, 14: 8.8, 17: 8.6, 46: 8.5, 8: 8.5, 20: 8.5,
            64: 8.2, 66: 8.2, 38: 8.1, 29: 8.1, 22: 8.0, 15: 8.0, 42: 7.9
        }
        
        self.mega_ball_weights = {
            22: 5.5, 11: 5.2, 18: 5.0, 24: 4.9, 9: 4.5, 4: 4.5, 
            13: 4.5, 19: 4.4, 1: 4.1
        }
        
        # Current format parameters
        self.current_white_range = (1, 70)
        self.current_mega_range = (1, 24)
        self.optimal_odd_counts = [2, 3]
        self.sum_range = (114, 228)
        self.mean_sum = 174
        
        # All possible numbers for current format
        self.all_white_balls = list(range(1, 71))
        self.all_mega_balls = list(range(1, 25))
        
        # Prize tiers (current format)
        self.prize_tiers = {
            (5, True): "JACKPOT! 🎉💰",
            (5, False): "$1,000,000 🏆",
            (4, True): "$10,000 💎",
            (4, False): "$500 💵",
            (3, True): "$200 💵",
            (3, False): "$10 🎫",
            (2, True): "$10 🎫",
            (1, True): "$4 🎫",
            (0, True): "$2 🎫"
        }
        
        # Rule periods for historical analysis
        self.rule_periods = [
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
                'end': datetime(2030, 12, 31),
                'white_range': (1, 70),
                'mega_range': (1, 24),
                'ball_name': 'Mega Ball'
            }
        ]
    
    def show_main_menu(self):
        """Display the main menu."""
        print("\n" + "="*60)
        print("🎰 MEGAMILLIONS SUITE - Statistical Lottery System")
        print("="*60)
        print("1. 🎲 Generate New Tickets")
        print("2. 📋 View Saved Tickets") 
        print("3. 🔍 Check Tickets Against Historical Data")
        print("4. 📊 Update Historical Database")
        print("5. 📈 Show Statistics & Analysis")
        print("6. 🔄 Show Rule Change History")
        print("7. ❓ Help & Information")
        print("8. 🚪 Exit")
        print("="*60)
    
    def update_database(self):
        """Download and update the historical database."""
        print("\n📊 UPDATING MEGAMILLIONS HISTORICAL DATABASE")
        print("="*45)
        
        # Try multiple sources
        sources = [
            ("Virginia Lottery API", "https://www.valottery.com/api/v1/downloadall?gameId=15"),
            ("Texas Lottery", "https://www.texaslottery.com/export/sites/lottery/Games/Mega_Millions/Winning_Numbers/megamillions.csv")
        ]
        
        for source_name, url in sources:
            try:
                print(f"🌐 Trying {source_name}...")
                temp_file = f"temp_megamillions_{source_name.lower().replace(' ', '_')}.csv"
                urllib.request.urlretrieve(url, temp_file)
                
                # Check if we got valid data
                with open(temp_file, 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 100:  # Should have substantial data
                        # Copy to our data file
                        os.rename(temp_file, self.data_file)
                        print(f"✅ Successfully downloaded from {source_name}")
                        print(f"📁 Saved as {self.data_file}")
                        
                        # Load and validate
                        self.load_historical_data()
                        return
                    else:
                        os.remove(temp_file)
                        print(f"❌ {source_name} returned insufficient data")
                        
            except Exception as e:
                print(f"❌ Error downloading from {source_name}: {e}")
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        
        print("💡 Manual update options:")
        print("   1. Download from: https://www.valottery.com/api/v1/downloadall?gameId=15")
        print("   2. Save as 'megamillions_historical_data.txt' in this directory")
    
    def load_historical_data(self):
        """Load historical data from file."""
        self.historical_data = []
        
        # Look for data files in current directory
        possible_files = [
            self.data_file,
            'MegaMillions_9_15_2025.txt',
            'megamillions_data.txt'
        ]
        
        data_file = None
        for fname in possible_files:
            if os.path.exists(fname):
                data_file = fname
                break
        
        if not data_file:
            print(f"⚠️  No historical data file found.")
            print("   Looking for one of these files:")
            for fname in possible_files:
                print(f"   - {fname}")
            print("   Use option 4 to download the database first.")
            return False
        
        try:
            with open(data_file, 'r') as f:
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
                            
                            # Only include current format for checking (2017-present)
                            if draw_date >= datetime(2017, 10, 28):
                                self.historical_data.append({
                                    'date': draw_date,
                                    'white_balls': sorted(numbers),
                                    'mega_ball': mega_ball
                                })
                except (ValueError, IndexError):
                    continue
            
            print(f"📊 Loaded {len(self.historical_data)} historical drawings (current format)")
            print(f"📁 Using data file: {data_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading historical data: {e}")
            return False
    
    def generate_tickets(self):
        """Generate new tickets using statistical algorithms."""
        print("\n🎲 GENERATE NEW MEGAMILLIONS TICKETS")
        print("="*35)
        
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
        print("4. Hot/Cold Analysis (recent trends)")
        print("5. 🧠 Prophet & Pragmatist (Autonomous Combinatorial Wheeling)")
        
        while True:
            try:
                choice = int(input("Choose algorithm (1-5): "))
                if choice in [1, 2, 3, 4, 5]:
                    algorithms = {1: 'frequency', 2: 'pattern', 3: 'balanced', 4: 'hot_cold', 5: 'prophet_wheel'}
                    algorithm = algorithms[choice]
                    break
                else:
                    print("Please enter 1, 2, 3, 4, or 5.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Generate tickets
        print(f"\n🎯 Generating {num_tickets} tickets using {algorithm} algorithm...")
        tickets = []
        
        if algorithm == 'prophet_wheel':
            # JMc - [2026-03-07] - Hooking up the big brain engine.
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
                    'special_ball': draw['mega_ball']
                })
                
            engine = LotteryMathEngine(formatted_history, self.current_white_range[1], self.current_mega_range[1])
            
            print("\n🔮 Prophet: Running Markov Chains & Poisson Overdue Analysis...")
            pool, special_pool = engine.generate_smart_pool(pool_size=15, special_pool_size=3)
            print(f"   [Autonomous Pool Selected]: {pool}")
            print(f"   [Special Balls Selected]: {special_pool}")
            
            print("\n⚙️  Pragmatist: Applying Greedy Combinatorial Wheeling for Maximum Coverage...")
            wheeled_tickets = engine.generate_wheeled_tickets(pool, special_pool, num_tickets)
            
            for w_white, w_special in wheeled_tickets:
                tickets.append({
                    'white_balls': w_white,
                    'mega_ball': w_special,
                    'algorithm': algorithm,
                    'generated_at': datetime.now().isoformat()
                })
        else:
            for i in range(num_tickets):
                if algorithm == 'frequency':
                    white_balls, mega_ball = self._frequency_generation()
                elif algorithm == 'pattern':
                    white_balls, mega_ball = self._pattern_generation()
                elif algorithm == 'hot_cold':
                    white_balls, mega_ball = self._hot_cold_generation()
                else:  # balanced
                    white_balls, mega_ball = self._balanced_generation()
                
                tickets.append({
                    'white_balls': white_balls,
                    'mega_ball': mega_ball,
                    'algorithm': algorithm,
                    'generated_at': datetime.now().isoformat()
                })
        
        # Display tickets
        print(f"\n🎫 YOUR GENERATED MEGAMILLIONS TICKETS:")
        print("-" * 45)
        for i, ticket in enumerate(tickets, 1):
            white_str = " ".join(f"{n:02d}" for n in ticket['white_balls'])
            odd_count = sum(1 for n in ticket['white_balls'] if n % 2 == 1)
            ball_sum = sum(ticket['white_balls'])
            print(f"#{i:02d}: {white_str}   🔴 {ticket['mega_ball']:02d}   "
                  f"({odd_count} odd, sum={ball_sum})")
        
        # Save tickets
        filename = f"megamillions_tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
        
        # Mega ball with weights
        mb_weighted_pool = []
        for num in self.all_mega_balls:
            weight = self.mega_ball_weights.get(num, 3.0)
            mb_weighted_pool.extend([num] * int(weight * 10))
        
        mega_ball = random.choice(mb_weighted_pool)
        return sorted(white_balls), mega_ball
    
    def _pattern_generation(self):
        """Generate following statistical patterns."""
        attempts = 0
        while attempts < 1000:
            white_balls = random.sample(self.all_white_balls, 5)
            odd_count = sum(1 for n in white_balls if n % 2 == 1)
            ball_sum = sum(white_balls)
            
            if (odd_count in self.optimal_odd_counts and 
                self.sum_range[0] <= ball_sum <= self.sum_range[1]):
                mega_ball = random.choice(self.top_mega_balls) if random.random() < 0.6 else random.choice(self.all_mega_balls)
                return sorted(white_balls), mega_ball
            
            attempts += 1
        
        return self._frequency_generation()  # Fallback
    
    def _hot_cold_generation(self):
        """Generate based on recent hot/cold number analysis."""
        # This would analyze recent 50 drawings for hot/cold trends
        # For now, use a variation of frequency with recent bias
        white_balls = []
        
        # Mix of hot numbers (recent frequent) and cold numbers (due to appear)
        hot_numbers = self.top_white_balls[:8]  # Recent hot
        cold_numbers = [n for n in self.all_white_balls if n not in self.top_white_balls[:20]]
        
        # Take 3 from hot, 2 from cold or random
        white_balls.extend(random.sample(hot_numbers, 3))
        remaining_pool = [n for n in self.all_white_balls if n not in white_balls]
        white_balls.extend(random.sample(remaining_pool, 2))
        
        mega_ball = random.choice(self.top_mega_balls) if random.random() < 0.7 else random.choice(self.all_mega_balls)
        return sorted(white_balls), mega_ball
    
    def _balanced_generation(self):
        """Generate using balanced approach."""
        white_balls = []
        
        # Take 2-3 from top frequent
        num_from_top = random.randint(2, 3)
        white_balls.extend(random.sample(self.top_white_balls[:10], num_from_top))
        
        # Ensure good decade distribution
        decades = {
            (1, 10): [n for n in range(1, 11) if n not in white_balls],
            (11, 20): [n for n in range(11, 21) if n not in white_balls],
            (21, 30): [n for n in range(21, 31) if n not in white_balls],
            (31, 40): [n for n in range(31, 41) if n not in white_balls],
            (41, 50): [n for n in range(41, 51) if n not in white_balls],
            (51, 60): [n for n in range(51, 61) if n not in white_balls],
            (61, 70): [n for n in range(61, 71) if n not in white_balls]
        }
        
        # Fill remaining slots with decade diversity
        while len(white_balls) < 5:
            available_decades = [d for d, nums in decades.items() if nums]
            if available_decades:
                chosen_decade = random.choice(available_decades)
                chosen_num = random.choice(decades[chosen_decade])
                white_balls.append(chosen_num)
                # Remove from all decades
                for d_nums in decades.values():
                    if chosen_num in d_nums:
                        d_nums.remove(chosen_num)
            else:
                # Fallback
                remaining = [n for n in self.all_white_balls if n not in white_balls]
                white_balls.append(random.choice(remaining))
        
        # Adjust for odd/even if needed
        odd_count = sum(1 for n in white_balls if n % 2 == 1)
        if odd_count not in self.optimal_odd_counts:
            target_odd = random.choice(self.optimal_odd_counts)
            if odd_count < target_odd:
                # Need more odd
                for i, num in enumerate(white_balls):
                    if num % 2 == 0:  # Even number
                        remaining_odd = [n for n in self.all_white_balls 
                                       if n % 2 == 1 and n not in white_balls]
                        if remaining_odd:
                            white_balls[i] = random.choice(remaining_odd)
                            break
        
        mega_ball = random.choice(self.top_mega_balls) if random.random() < 0.5 else random.choice(self.all_mega_balls)
        return sorted(white_balls), mega_ball
    
    def _show_ticket_analysis(self, tickets):
        """Show quick analysis of generated tickets."""
        if len(tickets) < 2:
            return
        
        print(f"\n📊 QUICK ANALYSIS:")
        print("-" * 20)
        
        # Odd/even distribution
        odd_dist = Counter()
        sums = []
        mbs = []
        
        for ticket in tickets:
            odd_count = sum(1 for n in ticket['white_balls'] if n % 2 == 1)
            odd_dist[f"{odd_count} odd"] += 1
            sums.append(sum(ticket['white_balls']))
            mbs.append(ticket['mega_ball'])
        
        print("Odd/Even Distribution:")
        for pattern, count in odd_dist.most_common():
            pct = (count / len(tickets)) * 100
            print(f"  {pattern}: {count} tickets ({pct:.1f}%)")
        
        print(f"Sum Range: {min(sums)} - {max(sums)} (avg: {sum(sums)/len(sums):.1f})")
        
        mb_dist = Counter(mbs)
        print("Top Mega Balls:")
        for mb, count in mb_dist.most_common(3):
            pct = (count / len(tickets)) * 100
            print(f"  {mb}: {count} times ({pct:.1f}%)")
    
    def view_tickets(self):
        """View saved ticket files."""
        print("\n📋 VIEW SAVED MEGAMILLIONS TICKETS")
        print("="*35)
        
        ticket_files = glob.glob("megamillions_tickets_*.json")
        
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
                    
                    print(f"#{i:02d}: {white_str}   🔴 {ticket['mega_ball']:02d}   "
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
        ticket_files = glob.glob("megamillions_tickets_*.json")
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
                
                print(f"\n🎫 TICKET #{i}: {' '.join(f'{n:02d}' for n in ticket['white_balls'])} 🔴 {ticket['mega_ball']:02d}")
                print(f"   Found {len(matches)} historical wins:")
                
                for match in matches:
                    prize_summary[match['prize']] += 1
                    winning_nums = match['winning_numbers']
                    winning_white = winning_nums[:-1]
                    winning_mb = winning_nums[-1]
                    
                    print(f"   📅 {match['date'].strftime('%Y-%m-%d')}: "
                          f"{' '.join(f'{n:02d}' for n in winning_white)} 🔴 {winning_mb:02d} "
                          f"({match['white_matches']}+MB:{match['mb_match']}) → {match['prize']}")
        
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
                # Rough value calculation
                if "$1,000,000" in prize:
                    total_value += count * 1000000
                elif "$10,000" in prize:
                    total_value += count * 10000
                elif "$500" in prize:
                    total_value += count * 500
                elif "$200" in prize:
                    total_value += count * 200
                elif "$10" in prize:
                    total_value += count * 10
                elif "$4" in prize:
                    total_value += count * 4
                elif "$2" in prize:
                    total_value += count * 2
            
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
        expected_matches = len(tickets) * len(self.historical_data) * 0.0417  # ~4.17% win rate for MegaMillions
        print(f"\n🎲 vs Random Expectation:")
        print(f"   Your tickets: {total_matches} matches")
        print(f"   Random expectation: ~{expected_matches:.1f} matches")
        if expected_matches > 0:
            performance = (total_matches / expected_matches) * 100
            print(f"   Performance: {performance:.1f}% of random")
    
    def _check_single_ticket(self, ticket):
        """Check a single ticket against historical data."""
        ticket_white = sorted(ticket['white_balls'])
        ticket_mb = ticket['mega_ball']
        matches = []
        
        for draw in self.historical_data:
            white_matches = len(set(ticket_white) & set(draw['white_balls']))
            mb_match = (ticket_mb == draw['mega_ball'])
            
            if (white_matches, mb_match) in self.prize_tiers:
                matches.append({
                    'date': draw['date'],
                    'white_matches': white_matches,
                    'mb_match': mb_match,
                    'prize': self.prize_tiers[(white_matches, mb_match)],
                    'winning_numbers': draw['white_balls'] + [draw['mega_ball']]
                })
        
        return matches
    
    def show_statistics(self):
        """Show comprehensive statistics and analysis."""
        print("\n📈 MEGAMILLIONS STATISTICS & ANALYSIS")
        print("="*40)
        
        if not self.historical_data:
            if not self.load_historical_data():
                print("💡 Use option 4 to download historical data first.")
                return
        
        print(f"📊 Historical Data: {len(self.historical_data)} drawings (current format)")
        if self.historical_data:
            print(f"📅 Date Range: {self.historical_data[0]['date'].strftime('%Y-%m-%d')} to {self.historical_data[-1]['date'].strftime('%Y-%m-%d')}")
        
        # Frequency analysis
        all_white_balls = []
        all_mega_balls = []
        
        for draw in self.historical_data:
            all_white_balls.extend(draw['white_balls'])
            all_mega_balls.append(draw['mega_ball'])
        
        white_freq = Counter(all_white_balls)
        mb_freq = Counter(all_mega_balls)
        
        print(f"\n🎯 TOP 15 MOST FREQUENT WHITE BALLS:")
        for i, (num, count) in enumerate(white_freq.most_common(15), 1):
            pct = (count / len(self.historical_data)) * 100
            print(f"  {i:2d}. {num:2d} ({count:3d} times, {pct:.1f}%)")
        
        print(f"\n🔴 TOP 10 MOST FREQUENT MEGA BALLS:")
        for i, (num, count) in enumerate(mb_freq.most_common(10), 1):
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
    
    def show_rule_history(self):
        """Show MegaMillions rule change history."""
        print("\n🔄 MEGAMILLIONS RULE CHANGE HISTORY")
        print("="*40)
        
        for i, period in enumerate(self.rule_periods, 1):
            print(f"\n📊 PERIOD {i}: {period['name']}")
            print(f"   📅 {period['start'].strftime('%Y-%m-%d')} to {period['end'].strftime('%Y-%m-%d')}")
            print(f"   🎯 Format: 5 from {period['white_range'][0]}-{period['white_range'][1]}, "
                  f"{period['ball_name']} {period['mega_range'][0]}-{period['mega_range'][1]}")
            
            # Add historical context
            if period['name'] == 'Big Game Era':
                print("   📝 Original multi-state lottery game")
            elif period['name'] == 'Early Mega Millions':
                print("   📝 Rebranded to Mega Millions, expanded matrix")
            elif period['name'] == 'Mega Millions v2':
                print("   📝 Adjusted for better odds and larger jackpots")
            elif period['name'] == 'Mega Millions v3':
                print("   📝 Major matrix change - more white balls, fewer mega balls")
            elif period['name'] == 'Current Format':
                print("   📝 Current format - balanced matrix for optimal play")
            elif period['name'] == 'New Format 2025':
                print("   📝 Latest changes - reduced mega ball pool")
        
        print(f"\n💡 Current ticket generation uses the '{self.rule_periods[-2]['name']}' period")
        print("   (Most recent period with substantial historical data)")
    
    def show_help(self):
        """Show help and information."""
        print("\n❓ HELP & INFORMATION")
        print("="*25)
        print("""
🎰 MEGAMILLIONS SUITE GUIDE

This application uses statistical analysis of historical MegaMillions data
to generate tickets that follow observed patterns rather than pure randomness.

KEY FEATURES:
• Generate tickets using 4 different algorithms
• View and analyze your saved tickets  
• Check tickets against historical winning numbers
• Update database with latest drawings
• Comprehensive statistical analysis
• Rule change history and period analysis

ALGORITHMS:
1. Frequency-based: Favors numbers that appear most often historically
2. Pattern-based: Follows optimal odd/even and sum patterns
3. Balanced: Combines frequency and pattern approaches (recommended)
4. Hot/Cold: Analyzes recent trends for hot and cold numbers

MEGAMILLIONS HISTORY:
The game has changed multiple times since 1996:
• Started as "Big Game" with different number ranges
• Became "Mega Millions" in 2002
• Multiple matrix changes to optimize jackpots and odds
• Current format: 5 from 1-70, Mega Ball 1-25

IMPORTANT NOTES:
• This is still a game of chance - no system guarantees wins
• Past performance doesn't predict future results
• Use for entertainment and educational purposes
• Always play responsibly

The system focuses on the current format (2017-present) for ticket generation.
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
        print("🎰 Welcome to MegaMillions Suite!")
        print("Statistical Lottery Analysis & Generation System")
        
        while True:
            self.show_main_menu()
            
            try:
                choice = input("\nSelect option (1-8): ").strip()
                
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
                    self.show_rule_history()
                elif choice == '7':
                    self.show_help()
                elif choice == '8':
                    print("\n👋 Thanks for using MegaMillions Suite!")
                    print("Good luck with your tickets! 🍀")
                    break
                else:
                    print("❌ Invalid choice. Please select 1-8.")
                
                if choice != '8':
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                input("Press Enter to continue...")

def main():
    """Main entry point."""
    app = MegaMillionsSuite()
    app.run()

if __name__ == "__main__":
    main()
