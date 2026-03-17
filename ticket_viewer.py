#!/usr/bin/env python3
"""
Powerball Ticket Viewer
Reads and displays tickets from JSON files in a nice format.
"""

import json
import glob
import os
from datetime import datetime

def find_ticket_files():
    """Find all ticket JSON files in the current directory."""
    pattern = "powerball_tickets_*.json"
    files = glob.glob(pattern)
    return sorted(files, reverse=True)  # Most recent first

def format_datetime(iso_string):
    """Convert ISO datetime string to readable format."""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return iso_string

def display_tickets(filename):
    """Display tickets from a JSON file in a nice format."""
    try:
        with open(filename, 'r') as f:
            tickets = json.load(f)
        
        print(f"\n📋 TICKETS FROM: {filename}")
        print("=" * 60)
        
        if not tickets:
            print("No tickets found in file.")
            return
        
        # Show file info
        first_ticket = tickets[0]
        algorithm = first_ticket.get('algorithm', 'unknown')
        generated_time = first_ticket.get('generated_at', 'unknown')
        
        print(f"Algorithm Used: {algorithm.title()}")
        print(f"Generated: {format_datetime(generated_time)}")
        print(f"Total Tickets: {len(tickets)}")
        print("-" * 60)
        
        # Display each ticket
        for i, ticket in enumerate(tickets, 1):
            white_balls = ticket['white_balls']
            powerball = ticket['powerball']
            
            # Format white balls
            white_str = " ".join(f"{n:02d}" for n in white_balls)
            
            # Calculate some stats
            odd_count = sum(1 for n in white_balls if n % 2 == 1)
            ball_sum = sum(white_balls)
            
            print(f"Ticket #{i:02d}: {white_str}   🔴 {powerball:02d}")
            print(f"           Stats: {odd_count} odd, {5-odd_count} even | Sum: {ball_sum}")
            
            if i < len(tickets):  # Don't add line after last ticket
                print()
        
        print("-" * 60)
        
        # Show batch statistics
        all_sums = [sum(ticket['white_balls']) for ticket in tickets]
        all_odds = [sum(1 for n in ticket['white_balls'] if n % 2 == 1) for ticket in tickets]
        all_powerballs = [ticket['powerball'] for ticket in tickets]
        
        print("📊 BATCH STATISTICS:")
        print(f"Sum Range: {min(all_sums)} - {max(all_sums)} (avg: {sum(all_sums)/len(all_sums):.1f})")
        
        # Odd/even distribution
        from collections import Counter
        odd_dist = Counter(all_odds)
        print("Odd/Even Distribution:")
        for odd_count in sorted(odd_dist.keys()):
            count = odd_dist[odd_count]
            pct = (count / len(tickets)) * 100
            print(f"  {odd_count} odd: {count} tickets ({pct:.1f}%)")
        
        # Top Powerballs
        pb_dist = Counter(all_powerballs)
        print("Powerball Distribution:")
        for pb, count in pb_dist.most_common(5):
            pct = (count / len(tickets)) * 100
            print(f"  {pb:2d}: {count} times ({pct:.1f}%)")
        
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON file: {filename}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def main():
    """Main function to view tickets."""
    print("🎱 POWERBALL TICKET VIEWER")
    print("=" * 40)
    
    # Find all ticket files
    ticket_files = find_ticket_files()
    
    if not ticket_files:
        print("❌ No ticket files found in current directory.")
        print("   Looking for files matching: powerball_tickets_*.json")
        return
    
    if len(ticket_files) == 1:
        # Only one file, display it
        display_tickets(ticket_files[0])
    else:
        # Multiple files, let user choose
        print("📁 Found multiple ticket files:")
        for i, filename in enumerate(ticket_files, 1):
            # Get file info
            stat = os.stat(filename)
            size = stat.st_size
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            
            print(f"  {i}. {filename}")
            print(f"     Size: {size} bytes | Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"  {len(ticket_files) + 1}. View all files")
        
        while True:
            try:
                choice = input(f"\nSelect file to view (1-{len(ticket_files) + 1}): ")
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(ticket_files):
                    display_tickets(ticket_files[choice_num - 1])
                    break
                elif choice_num == len(ticket_files) + 1:
                    # View all files
                    for filename in ticket_files:
                        display_tickets(filename)
                        print("\n" + "="*60 + "\n")
                    break
                else:
                    print(f"Please enter a number between 1 and {len(ticket_files) + 1}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                return

if __name__ == "__main__":
    main()
