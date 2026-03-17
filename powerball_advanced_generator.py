#!/usr/bin/env python3
"""
Advanced Powerball Ticket Generation System
Multiple algorithms based on comprehensive statistical analysis of historical data.
"""

import random
import pandas as pd
import numpy as np
from collections import Counter
import json
from datetime import datetime

class PowerballGenerator:
    def __init__(self):
        """Initialize the generator with statistical data from analysis."""
        
        # Current period (2015-Present) statistics
        self.top_white_balls = [61, 21, 23, 33, 69, 64, 27, 62, 32, 63, 36, 53, 59, 20, 37]
        self.top_powerballs = [4, 21, 24, 18, 25, 9, 14, 5, 20, 3]
        
        # Frequency weights (higher = more likely to be selected)
        self.white_ball_weights = {
            61: 9.3, 21: 9.0, 23: 9.0, 33: 8.7, 69: 8.6, 64: 8.5, 27: 8.4, 
            62: 8.3, 32: 8.3, 63: 8.3, 36: 8.2, 53: 8.1, 59: 8.0, 20: 7.9, 37: 7.9
        }
        
        self.powerball_weights = {
            4: 4.8, 21: 4.7, 24: 4.6, 18: 4.6, 25: 4.5, 9: 4.4, 14: 4.4, 
            5: 4.3, 20: 4.2, 3: 3.9
        }
        
        # Statistical patterns
        self.optimal_odd_counts = [2, 3]  # Most common odd/even distributions
        self.sum_range = (148, 206)
        self.mean_sum = 177
        
        # Decade distribution preferences (based on analysis)
        self.decade_preferences = {
            (1, 10): 0.85,   # Slightly underrepresented
            (11, 20): 0.90,  # Slightly underrepresented  
            (21, 30): 1.10,  # Slightly overrepresented
            (31, 40): 1.05,  # Balanced
            (41, 50): 0.95,  # Slightly underrepresented
            (51, 60): 1.00,  # Balanced
            (61, 69): 1.15   # Overrepresented (new numbers)
        }
        
        # All possible numbers
        self.all_white_balls = list(range(1, 70))
        self.all_powerballs = list(range(1, 27))
        
    def _get_decade(self, number):
        """Get the decade group for a number."""
        if 1 <= number <= 10:
            return (1, 10)
        elif 11 <= number <= 20:
            return (11, 20)
        elif 21 <= number <= 30:
            return (21, 30)
        elif 31 <= number <= 40:
            return (31, 40)
        elif 41 <= number <= 50:
            return (41, 50)
        elif 51 <= number <= 60:
            return (51, 60)
        elif 61 <= number <= 69:
            return (61, 69)
        return None
    
    def frequency_based_generation(self):
        """Generate numbers based on historical frequency analysis."""
        white_balls = []
        
        # Create weighted selection pool
        weighted_pool = []
        for num in self.all_white_balls:
            weight = self.white_ball_weights.get(num, 5.0)  # Default weight for less frequent numbers
            weighted_pool.extend([num] * int(weight * 10))  # Scale weights
        
        # Select 5 unique white balls
        while len(white_balls) < 5:
            selected = random.choice(weighted_pool)
            if selected not in white_balls:
                white_balls.append(selected)
        
        # Generate Powerball with weights
        pb_weighted_pool = []
        for num in self.all_powerballs:
            weight = self.powerball_weights.get(num, 3.0)
            pb_weighted_pool.extend([num] * int(weight * 10))
        
        powerball = random.choice(pb_weighted_pool)
        
        return sorted(white_balls), powerball
    
    def pattern_based_generation(self):
        """Generate numbers following optimal statistical patterns."""
        attempts = 0
        max_attempts = 1000
        
        while attempts < max_attempts:
            white_balls = []
            
            # Ensure good decade distribution
            decades_used = {}
            for decade in self.decade_preferences:
                decades_used[decade] = 0
            
            # Select numbers with decade awareness
            while len(white_balls) < 5:
                # Choose a decade based on preferences
                decade_choices = []
                for decade, preference in self.decade_preferences.items():
                    # Limit numbers per decade (max 2-3 per decade for balance)
                    if decades_used[decade] < 2:
                        decade_choices.extend([decade] * int(preference * 10))
                
                if not decade_choices:
                    break
                    
                chosen_decade = random.choice(decade_choices)
                decade_min, decade_max = chosen_decade
                
                # Select a number from this decade
                decade_numbers = [n for n in range(decade_min, decade_max + 1) 
                                if n not in white_balls]
                if decade_numbers:
                    # Prefer frequent numbers within the decade
                    decade_weights = []
                    for num in decade_numbers:
                        weight = self.white_ball_weights.get(num, 5.0)
                        decade_weights.extend([num] * int(weight))
                    
                    selected = random.choice(decade_weights)
                    white_balls.append(selected)
                    decades_used[chosen_decade] += 1
            
            if len(white_balls) < 5:
                # Fill remaining slots randomly
                remaining = [n for n in self.all_white_balls if n not in white_balls]
                white_balls.extend(random.sample(remaining, 5 - len(white_balls)))
            
            # Check if pattern meets criteria
            odd_count = sum(1 for n in white_balls if n % 2 == 1)
            ball_sum = sum(white_balls)
            
            if (odd_count in self.optimal_odd_counts and 
                self.sum_range[0] <= ball_sum <= self.sum_range[1]):
                
                # Generate Powerball
                powerball = random.choice(self.top_powerballs) if random.random() < 0.6 else random.choice(self.all_powerballs)
                return sorted(white_balls), powerball
            
            attempts += 1
        
        # Fallback to frequency-based if pattern matching fails
        return self.frequency_based_generation()
    
    def balanced_generation(self):
        """Generate numbers with balanced approach combining multiple strategies."""
        # Mix of strategies
        strategy = random.choice(['frequency', 'pattern', 'hybrid'])
        
        if strategy == 'frequency':
            return self.frequency_based_generation()
        elif strategy == 'pattern':
            return self.pattern_based_generation()
        else:  # hybrid
            white_balls = []
            
            # Take 2-3 numbers from top frequent
            num_from_top = random.randint(2, 3)
            white_balls.extend(random.sample(self.top_white_balls[:10], num_from_top))
            
            # Take 1-2 numbers from medium frequency (positions 11-30)
            medium_freq = self.top_white_balls[10:] + [n for n in range(1, 70) 
                                                     if n not in self.top_white_balls[:15]]
            num_from_medium = random.randint(1, 2)
            available_medium = [n for n in medium_freq if n not in white_balls]
            white_balls.extend(random.sample(available_medium, min(num_from_medium, len(available_medium))))
            
            # Fill remaining with random selection ensuring pattern compliance
            while len(white_balls) < 5:
                remaining = [n for n in self.all_white_balls if n not in white_balls]
                candidate = random.choice(remaining)
                white_balls.append(candidate)
                
                # Check if we need to adjust for odd/even balance
                if len(white_balls) == 5:
                    odd_count = sum(1 for n in white_balls if n % 2 == 1)
                    if odd_count not in self.optimal_odd_counts:
                        # Replace last number to fix odd/even balance
                        white_balls.pop()
                        target_odd = random.choice(self.optimal_odd_counts)
                        current_odd = sum(1 for n in white_balls if n % 2 == 1)
                        
                        if current_odd < target_odd:
                            # Need more odd numbers
                            odd_candidates = [n for n in remaining if n % 2 == 1]
                            if odd_candidates:
                                white_balls.append(random.choice(odd_candidates))
                            else:
                                white_balls.append(candidate)  # Fallback
                        else:
                            # Need more even numbers
                            even_candidates = [n for n in remaining if n % 2 == 0]
                            if even_candidates:
                                white_balls.append(random.choice(even_candidates))
                            else:
                                white_balls.append(candidate)  # Fallback
            
            # Generate Powerball with mixed strategy
            if random.random() < 0.5:
                powerball = random.choice(self.top_powerballs)
            else:
                powerball = random.choice(self.all_powerballs)
            
            return sorted(white_balls), powerball
    
    def generate_tickets(self, num_tickets, algorithm='balanced'):
        """Generate multiple tickets using specified algorithm."""
        tickets = []
        algorithms = {
            'frequency': self.frequency_based_generation,
            'pattern': self.pattern_based_generation,
            'balanced': self.balanced_generation
        }
        
        if algorithm not in algorithms:
            algorithm = 'balanced'
        
        generator_func = algorithms[algorithm]
        
        for _ in range(num_tickets):
            white_balls, powerball = generator_func()
            tickets.append({
                'white_balls': white_balls,
                'powerball': powerball,
                'algorithm': algorithm,
                'generated_at': datetime.now().isoformat()
            })
        
        return tickets
    
    def analyze_generated_tickets(self, tickets):
        """Analyze the characteristics of generated tickets."""
        analysis = {
            'total_tickets': len(tickets),
            'odd_even_distribution': Counter(),
            'sum_distribution': [],
            'powerball_distribution': Counter(),
            'decade_distribution': Counter()
        }
        
        for ticket in tickets:
            white_balls = ticket['white_balls']
            powerball = ticket['powerball']
            
            # Odd/even analysis
            odd_count = sum(1 for n in white_balls if n % 2 == 1)
            analysis['odd_even_distribution'][f"{odd_count} odd, {5-odd_count} even"] += 1
            
            # Sum analysis
            analysis['sum_distribution'].append(sum(white_balls))
            
            # Powerball analysis
            analysis['powerball_distribution'][powerball] += 1
            
            # Decade analysis
            for num in white_balls:
                decade = self._get_decade(num)
                if decade:
                    analysis['decade_distribution'][f"{decade[0]}-{decade[1]}"] += 1
        
        # Calculate statistics
        sums = analysis['sum_distribution']
        analysis['sum_stats'] = {
            'mean': np.mean(sums),
            'median': np.median(sums),
            'std': np.std(sums),
            'min': min(sums),
            'max': max(sums)
        }
        
        return analysis

def main():
    """Main function to run the advanced ticket generator."""
    print("ADVANCED POWERBALL TICKET GENERATOR")
    print("=" * 50)
    print("Based on comprehensive statistical analysis of historical data")
    print("\nAvailable algorithms:")
    print("1. Frequency-based: Uses historical frequency weights")
    print("2. Pattern-based: Follows optimal statistical patterns")
    print("3. Balanced: Combines multiple strategies (recommended)")
    
    generator = PowerballGenerator()
    
    # Get user input
    while True:
        try:
            num_tickets = int(input("\nEnter number of tickets to generate: "))
            if num_tickets > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    print("\nSelect algorithm:")
    print("1. Frequency-based")
    print("2. Pattern-based") 
    print("3. Balanced (recommended)")
    
    while True:
        try:
            choice = int(input("Enter choice (1-3): "))
            if choice in [1, 2, 3]:
                algorithms = {1: 'frequency', 2: 'pattern', 3: 'balanced'}
                algorithm = algorithms[choice]
                break
            else:
                print("Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Generate tickets
    print(f"\nGenerating {num_tickets} tickets using {algorithm} algorithm...\n")
    tickets = generator.generate_tickets(num_tickets, algorithm)
    
    # Display tickets
    for i, ticket in enumerate(tickets, 1):
        white_balls = ticket['white_balls']
        powerball = ticket['powerball']
        white_str = " ".join(f"{n:02d}" for n in white_balls)
        print(f"Ticket #{i:02d}: {white_str}   PB: {powerball:02d}")
    
    # Show analysis
    if num_tickets >= 5:
        print(f"\n--- TICKET ANALYSIS ---")
        analysis = generator.analyze_generated_tickets(tickets)
        
        print(f"Odd/Even Distribution:")
        for pattern, count in analysis['odd_even_distribution'].most_common():
            percentage = (count / num_tickets) * 100
            print(f"  {pattern}: {count} tickets ({percentage:.1f}%)")
        
        print(f"\nSum Statistics:")
        stats = analysis['sum_stats']
        print(f"  Mean: {stats['mean']:.1f}")
        print(f"  Range: {stats['min']} - {stats['max']}")
        print(f"  Target range: 148-206 ✓" if 148 <= stats['mean'] <= 206 else f"  Target range: 148-206 ✗")
        
        print(f"\nTop Powerballs Generated:")
        for pb, count in analysis['powerball_distribution'].most_common(5):
            percentage = (count / num_tickets) * 100
            print(f"  {pb:2d}: {count} times ({percentage:.1f}%)")
    
    # Save tickets to file
    filename = f"powerball_tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(tickets, f, indent=2)
    
    print(f"\nTickets saved to: {filename}")
    print("Good luck! 🍀")

if __name__ == "__main__":
    main()
