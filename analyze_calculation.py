import pandas as pd
from datetime import datetime
import numpy as np

# Initialize the system
import sys
sys.path.append('.')
from accruals_main import AccrualsSystem

def analyze_calculation():
    system = AccrualsSystem()
    if system.load_data():
        print('=== DETAILED CALCULATION ANALYSIS ===')
        print()
        
        # Get the first category to analyze in detail
        first_row = system.data.iloc[0]
        category = first_row['Row Labels']
        
        print(f'Analyzing: {category}')
        print(f'Target Month: {system.target_month_name} {system.target_year} ({system.get_weeks_in_month(system.target_month)} weeks)')
        print()
        
        # Get historical values
        historical_values = []
        historical_months = []
        
        for month_col in system.monthly_columns:
            value = first_row[month_col]
            if pd.notna(value) and value > 0:
                historical_values.append(value)
                historical_months.append(month_col.strftime('%B %Y'))
        
        print(f'Historical Data ({len(historical_values)} months):')
        for i, (month, value) in enumerate(zip(historical_months, historical_values)):
            month_num = system.monthly_columns[i].month
            weeks = system.get_weeks_in_month(month_num)
            weekly_rate = system.normalize_to_weekly_rate(value, month_num)
            print(f'  {month}: ${value:,.2f} ({weeks} weeks) = ${weekly_rate:.2f}/week')
        
        print()
        
        # Calculate weekly rates
        historical_weekly_rates = []
        for i, value in enumerate(historical_values):
            month_col = system.monthly_columns[i] 
            weekly_rate = system.normalize_to_weekly_rate(value, month_col.month)
            historical_weekly_rates.append(weekly_rate)
        
        # Calculate forecasts
        print('Forecast Calculations:')
        
        # Simple average
        avg_weekly = np.mean(historical_weekly_rates)
        simple_forecast = system.convert_weekly_to_monthly(avg_weekly, system.target_month)
        print(f'  Simple Average: ${avg_weekly:.2f}/week × {system.get_weeks_in_month(system.target_month)} weeks = ${simple_forecast:.2f}')
        
        # Weighted average
        weights = np.arange(1, len(historical_weekly_rates) + 1)
        weighted_avg_weekly = np.average(historical_weekly_rates, weights=weights)
        weighted_forecast = system.convert_weekly_to_monthly(weighted_avg_weekly, system.target_month)
        print(f'  Weighted Average: ${weighted_avg_weekly:.2f}/week × {system.get_weeks_in_month(system.target_month)} weeks = ${weighted_forecast:.2f}')
        
        # Trending
        if len(historical_weekly_rates) >= 2:
            x = np.arange(len(historical_weekly_rates))
            slope, intercept = np.polyfit(x, historical_weekly_rates, 1)
            trend_weekly = slope * len(historical_weekly_rates) + intercept
            trend_forecast = system.convert_weekly_to_monthly(trend_weekly, system.target_month)
            print(f'  Trending Average: ${trend_weekly:.2f}/week × {system.get_weeks_in_month(system.target_month)} weeks = ${trend_forecast:.2f}')
        
        recommendation = (simple_forecast + weighted_forecast + trend_forecast) / 3
        print(f'  RECOMMENDED: ${recommendation:.2f}')

try:
    analyze_calculation()
except Exception as e:
    print(f'Error: {e}')
