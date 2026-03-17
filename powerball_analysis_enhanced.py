#!/usr/bin/env python3
"""
Enhanced Powerball Lottery Data Analysis
Analyzes historical Powerball winning numbers accounting for game rule changes over time.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

# Define Powerball rule change periods
POWERBALL_PERIODS = {
    "Period 1 (2010-2012)": {
        "start": "2010-02-03",
        "end": "2012-01-14", 
        "white_balls": (1, 59),
        "powerball": (1, 39),
        "description": "Original format: 5 from 1-59, Powerball 1-39"
    },
    "Period 2 (2012-2015)": {
        "start": "2012-01-15",
        "end": "2015-10-03",
        "white_balls": (1, 59),
        "powerball": (1, 35),
        "description": "Price doubled, Powerball reduced: 5 from 1-59, Powerball 1-35"
    },
    "Period 3 (2015-Present)": {
        "start": "2015-10-04",
        "end": "2025-12-31",
        "white_balls": (1, 69),
        "powerball": (1, 26),
        "description": "Current format: 5 from 1-69, Powerball 1-26"
    }
}

def load_and_clean_data(filename):
    """Load and clean the Powerball data with period classification"""
    print("Loading complete Powerball data...")
    
    # Read the Texas Lottery CSV format
    df = pd.read_csv(filename, header=None)
    
    # The format is: Game, Month, Day, Year, Num1, Num2, Num3, Num4, Num5, Powerball, PowerPlay
    df.columns = ['Game', 'Month', 'Day', 'Year', 'Num1', 'Num2', 'Num3', 'Num4', 'Num5', 'Powerball', 'PowerPlay']
    
    # Create proper date column
    df['Draw_Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
    
    # Sort by date
    df = df.sort_values('Draw_Date').reset_index(drop=True)
    
    # Create sorted white balls list
    df['White_Balls'] = df[['Num1', 'Num2', 'Num3', 'Num4', 'Num5']].values.tolist()
    df['White_Balls_Sorted'] = df['White_Balls'].apply(sorted)
    
    # Classify each drawing by period
    def classify_period(date):
        for period_name, period_info in POWERBALL_PERIODS.items():
            start_date = pd.to_datetime(period_info['start'])
            end_date = pd.to_datetime(period_info['end'])
            if start_date <= date <= end_date:
                return period_name
        return "Unknown"
    
    df['Period'] = df['Draw_Date'].apply(classify_period)
    
    print(f"Loaded {len(df)} drawings from {df['Draw_Date'].min()} to {df['Draw_Date'].max()}")
    
    # Show period breakdown
    period_counts = df['Period'].value_counts()
    print("\nDrawings by period:")
    for period, count in period_counts.items():
        if period in POWERBALL_PERIODS:
            print(f"  {period}: {count} drawings")
            print(f"    {POWERBALL_PERIODS[period]['description']}")
    
    return df

def analyze_by_period(df):
    """Analyze patterns separately for each rule period"""
    print("\n=== PERIOD-SPECIFIC ANALYSIS ===")
    
    period_analysis = {}
    
    for period_name in POWERBALL_PERIODS.keys():
        period_df = df[df['Period'] == period_name].copy()
        if len(period_df) == 0:
            continue
            
        print(f"\n--- {period_name} ---")
        print(f"Drawings: {len(period_df)}")
        print(f"Date range: {period_df['Draw_Date'].min()} to {period_df['Draw_Date'].max()}")
        
        # White ball frequency analysis for this period
        white_balls = []
        for _, row in period_df.iterrows():
            white_balls.extend(row['White_Balls'])
        
        white_freq = Counter(white_balls)
        powerball_freq = Counter(period_df['Powerball'].tolist())
        
        # Get the valid ranges for this period
        period_info = POWERBALL_PERIODS[period_name]
        white_min, white_max = period_info['white_balls']
        pb_min, pb_max = period_info['powerball']
        
        print(f"White ball range: {white_min}-{white_max}")
        print(f"Powerball range: {pb_min}-{pb_max}")
        
        # Most/least frequent numbers
        print(f"Most frequent white balls:")
        for num, count in white_freq.most_common(5):
            percentage = (count / len(period_df)) * 100
            print(f"  {num:2d}: {count:3d} times ({percentage:.1f}%)")
        
        print(f"Most frequent Powerballs:")
        for num, count in powerball_freq.most_common(5):
            percentage = (count / len(period_df)) * 100
            print(f"  {num:2d}: {count:3d} times ({percentage:.1f}%)")
        
        # Odd/even analysis
        period_df['Odd_Count'] = period_df['White_Balls_Sorted'].apply(lambda x: sum(1 for n in x if n % 2 == 1))
        odd_distribution = period_df['Odd_Count'].value_counts().sort_index()
        
        print(f"Odd/even distribution:")
        for odd_count in range(6):
            count = odd_distribution.get(odd_count, 0)
            if count > 0:
                percentage = (count / len(period_df)) * 100
                print(f"  {odd_count} odd: {count:3d} times ({percentage:.1f}%)")
        
        # Sum analysis
        period_df['White_Ball_Sum'] = period_df['White_Balls_Sorted'].apply(sum)
        sum_stats = period_df['White_Ball_Sum'].describe()
        print(f"Sum statistics: Mean={sum_stats['mean']:.1f}, Median={sum_stats['50%']:.1f}")
        
        period_analysis[period_name] = {
            'df': period_df,
            'white_freq': white_freq,
            'powerball_freq': powerball_freq,
            'drawings_count': len(period_df)
        }
    
    return period_analysis

def analyze_transition_effects(df):
    """Analyze how patterns changed between periods"""
    print("\n=== TRANSITION ANALYSIS ===")
    
    # Compare frequency patterns between periods
    current_period = df[df['Period'] == 'Period 3 (2015-Present)'].copy()
    previous_period = df[df['Period'] == 'Period 2 (2012-2015)'].copy()
    
    if len(current_period) > 0 and len(previous_period) > 0:
        print("Comparing Period 2 (2012-2015) vs Period 3 (2015-Present)")
        
        # White balls that were valid in both periods (1-59)
        common_white_balls = []
        for _, row in current_period.iterrows():
            common_white_balls.extend([n for n in row['White_Balls'] if n <= 59])
        
        prev_white_balls = []
        for _, row in previous_period.iterrows():
            prev_white_balls.extend(row['White_Balls'])
        
        current_freq = Counter(common_white_balls)
        prev_freq = Counter(prev_white_balls)
        
        # Find numbers that changed frequency significantly
        print("\nNumbers with significant frequency changes (1-59 range):")
        for num in range(1, 60):
            if num in current_freq and num in prev_freq:
                current_rate = current_freq[num] / len(current_period) * 100
                prev_rate = prev_freq[num] / len(previous_period) * 100
                change = current_rate - prev_rate
                if abs(change) > 0.5:  # More than 0.5% change
                    print(f"  {num:2d}: {prev_rate:.1f}% → {current_rate:.1f}% ({change:+.1f}%)")
        
        # Powerball comparison (1-26 range only)
        current_pb = Counter([pb for pb in current_period['Powerball'] if pb <= 26])
        prev_pb = Counter([pb for pb in previous_period['Powerball'] if pb <= 26])
        
        print("\nPowerball frequency changes (1-26 range):")
        for num in range(1, 27):
            if num in current_pb and num in prev_pb:
                current_rate = current_pb[num] / len(current_period) * 100
                prev_rate = prev_pb[num] / len(previous_period) * 100
                change = current_rate - prev_rate
                if abs(change) > 1.0:  # More than 1% change
                    print(f"  {num:2d}: {prev_rate:.1f}% → {current_rate:.1f}% ({change:+.1f}%)")

def create_period_visualizations(period_analysis):
    """Create visualizations comparing different periods"""
    print("\n=== CREATING PERIOD COMPARISON VISUALIZATIONS ===")
    
    fig, axes = plt.subplots(3, 2, figsize=(16, 18))
    fig.suptitle('Powerball Analysis by Rule Period', fontsize=16, fontweight='bold')
    
    colors = ['skyblue', 'lightcoral', 'lightgreen']
    period_names = list(period_analysis.keys())
    
    # 1. White ball frequency comparison (for numbers 1-59, common to all periods)
    ax = axes[0, 0]
    for i, (period_name, data) in enumerate(period_analysis.items()):
        white_freq = data['white_freq']
        common_nums = [n for n in range(1, 60) if n in white_freq]
        common_freqs = [white_freq[n] / data['drawings_count'] * 100 for n in common_nums]
        
        ax.plot(common_nums, common_freqs, alpha=0.7, label=period_name.split('(')[0].strip(), 
                color=colors[i % len(colors)], linewidth=2)
    
    ax.set_title('White Ball Frequency Comparison (1-59)')
    ax.set_xlabel('Number')
    ax.set_ylabel('Frequency (%)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. Powerball frequency comparison (for numbers 1-26, common to periods 2&3)
    ax = axes[0, 1]
    for i, (period_name, data) in enumerate(period_analysis.items()):
        if 'Period 1' in period_name:
            continue  # Skip period 1 as it had different Powerball range
        
        pb_freq = data['powerball_freq']
        common_nums = [n for n in range(1, 27) if n in pb_freq]
        common_freqs = [pb_freq[n] / data['drawings_count'] * 100 for n in common_nums]
        
        ax.bar([n + i*0.3 for n in common_nums], common_freqs, width=0.3, alpha=0.7, 
               label=period_name.split('(')[0].strip(), color=colors[i % len(colors)])
    
    ax.set_title('Powerball Frequency Comparison (1-26)')
    ax.set_xlabel('Powerball Number')
    ax.set_ylabel('Frequency (%)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. Odd/even distribution by period
    ax = axes[1, 0]
    for i, (period_name, data) in enumerate(period_analysis.items()):
        period_df = data['df']
        odd_counts = period_df['Odd_Count'].value_counts().sort_index()
        percentages = (odd_counts / len(period_df) * 100).values
        
        ax.bar([x + i*0.25 for x in odd_counts.index], percentages, width=0.25, alpha=0.7,
               label=period_name.split('(')[0].strip(), color=colors[i % len(colors)])
    
    ax.set_title('Odd Numbers Distribution by Period')
    ax.set_xlabel('Number of Odd Numbers')
    ax.set_ylabel('Frequency (%)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. Sum distribution by period
    ax = axes[1, 1]
    for i, (period_name, data) in enumerate(period_analysis.items()):
        period_df = data['df']
        ax.hist(period_df['White_Ball_Sum'], bins=30, alpha=0.5, 
                label=period_name.split('(')[0].strip(), color=colors[i % len(colors)])
    
    ax.set_title('Sum Distribution by Period')
    ax.set_xlabel('Sum of White Balls')
    ax.set_ylabel('Frequency')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 5. Timeline of average sums
    ax = axes[2, 0]
    for period_name, data in period_analysis.items():
        period_df = data['df']
        monthly_avg = period_df.groupby(period_df['Draw_Date'].dt.to_period('M'))['White_Ball_Sum'].mean()
        ax.plot(monthly_avg.index.astype(str), monthly_avg.values, 
                label=period_name.split('(')[0].strip(), linewidth=2, alpha=0.8)
    
    ax.set_title('Average Sum Trend Over Time by Period')
    ax.set_xlabel('Month')
    ax.set_ylabel('Average Sum')
    ax.legend()
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3)
    
    # 6. Current period detailed analysis (most recent)
    current_data = period_analysis['Period 3 (2015-Present)']
    current_df = current_data['df']
    
    ax = axes[2, 1]
    # Show frequency of numbers 60-69 (new in current period)
    new_numbers = []
    for _, row in current_df.iterrows():
        new_numbers.extend([n for n in row['White_Balls'] if n >= 60])
    
    if new_numbers:
        new_freq = Counter(new_numbers)
        nums = sorted(new_freq.keys())
        freqs = [new_freq[n] / len(current_df) * 100 for n in nums]
        
        ax.bar(nums, freqs, alpha=0.7, color='purple')
        ax.set_title('New Numbers Frequency (60-69)\nCurrent Period Only')
        ax.set_xlabel('Number')
        ax.set_ylabel('Frequency (%)')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('powerball_period_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved period analysis visualization as 'powerball_period_analysis.png'")
    
    return fig

def generate_period_aware_recommendations(period_analysis):
    """Generate recommendations based on current period patterns"""
    print("\n=== PERIOD-AWARE RECOMMENDATIONS ===")
    
    current_period = period_analysis['Period 3 (2015-Present)']
    current_df = current_period['df']
    
    print("Based on current period (2015-Present) analysis:")
    print(f"Total drawings analyzed: {len(current_df)}")
    
    # Most frequent numbers in current period
    white_freq = current_period['white_freq']
    pb_freq = current_period['powerball_freq']
    
    print(f"\nTop 10 most frequent white balls (1-69):")
    for i, (num, count) in enumerate(white_freq.most_common(10), 1):
        percentage = (count / len(current_df)) * 100
        print(f"  {i:2d}. {num:2d} ({count:3d} times, {percentage:.1f}%)")
    
    print(f"\nTop 10 most frequent Powerballs (1-26):")
    for i, (num, count) in enumerate(pb_freq.most_common(10), 1):
        percentage = (count / len(current_df)) * 100
        print(f"  {i:2d}. {num:2d} ({count:3d} times, {percentage:.1f}%)")
    
    # Optimal odd/even distribution
    odd_distribution = current_df['Odd_Count'].value_counts().sort_index()
    most_common_odd = odd_distribution.idxmax()
    print(f"\nMost common odd/even split: {most_common_odd} odd, {5-most_common_odd} even")
    print(f"  Occurred in {odd_distribution[most_common_odd]} drawings ({odd_distribution[most_common_odd]/len(current_df)*100:.1f}%)")
    
    # Sum range recommendations
    sum_stats = current_df['White_Ball_Sum'].describe()
    print(f"\nSum recommendations:")
    print(f"  Target range: {sum_stats['25%']:.0f} - {sum_stats['75%']:.0f}")
    print(f"  Sweet spot: {sum_stats['mean']:.0f} ± {sum_stats['std']:.0f}")
    
    return {
        'top_white_balls': [num for num, _ in white_freq.most_common(15)],
        'top_powerballs': [num for num, _ in pb_freq.most_common(10)],
        'optimal_odd_count': most_common_odd,
        'sum_range': (int(sum_stats['25%']), int(sum_stats['75%'])),
        'mean_sum': int(sum_stats['mean'])
    }

def main():
    """Main analysis function"""
    print("ENHANCED POWERBALL LOTTERY STATISTICAL ANALYSIS")
    print("Accounting for Rule Changes Over Time")
    print("=" * 60)
    
    # Load data
    df = load_and_clean_data('texas_powerball_complete.csv')
    
    # Perform period-specific analysis
    period_analysis = analyze_by_period(df)
    
    # Analyze transitions between periods
    analyze_transition_effects(df)
    
    # Create visualizations
    fig = create_period_visualizations(period_analysis)
    
    # Generate recommendations
    recommendations = generate_period_aware_recommendations(period_analysis)
    
    # Save processed data
    df.to_csv('powerball_enhanced_analysis.csv', index=False)
    print(f"\nSaved enhanced analysis data to 'powerball_enhanced_analysis.csv'")
    
    print(f"\nAnalysis complete! Ready for algorithm development.")
    
    return df, period_analysis, recommendations

if __name__ == "__main__":
    df, period_analysis, recommendations = main()
