import pandas as pd
import numpy as np
from datetime import datetime
import os

def simple_forecast():
    print("Starting Accruals Forecasting System...")
    
    # Load data
    df = pd.read_excel('Input/Actual.xlsx')
    print(f"Loaded {len(df)} expense categories")
    
    # Get monthly columns
    monthly_columns = [col for col in df.columns if isinstance(col, datetime)]
    monthly_columns.sort()
    print(f"Found {len(monthly_columns)} monthly columns")
    
    results = []
    
    for idx, row in df.iterrows():
        category = row['Row Labels']
        
        # Get last 6 months of actual data
        recent_values = []
        for month_col in monthly_columns[-7:-1]:  # Exclude August (last column)
            value = row[month_col]
            if pd.notna(value) and value > 0:
                recent_values.append(value)
        
        if recent_values:
            # Simple average
            simple_avg = np.mean(recent_values)
            
            # Weighted average (more weight on recent)
            weights = np.arange(1, len(recent_values) + 1)
            weights = weights / weights.sum()
            weighted_avg = np.average(recent_values, weights=weights)
            
            # Simple trend
            if len(recent_values) >= 2:
                trend = (recent_values[-1] - recent_values[0]) / (len(recent_values) - 1)
                trending_avg = recent_values[-1] + trend
            else:
                trending_avg = simple_avg
            
            # Recommendation (average of three methods)
            recommendation = (simple_avg + weighted_avg + trending_avg) / 3
            
            results.append({
                'Category': category,
                'Simple_Average': round(simple_avg, 2),
                'Weighted_Average': round(weighted_avg, 2),
                'Trending_Average': round(trending_avg, 2),
                'Recommended_Accrual': round(recommendation, 2),
                'Historical_Values': [round(v, 2) for v in recent_values[-3:]]
            })
    
    # Print results
    print("\n" + "="*80)
    print("ACCRUALS FORECAST SUMMARY - AUGUST 2025")
    print("="*80)
    
    total_recommended = sum([r['Recommended_Accrual'] for r in results])
    print(f"TOTAL RECOMMENDED ACCRUAL: ${total_recommended:,.2f}")
    
    print(f"\nBREAKDOWN BY CATEGORY:")
    print("-" * 80)
    
    for result in results:
        print(f"\n{result['Category']}:")
        print(f"  Simple Average:     ${result['Simple_Average']:8,.2f}")
        print(f"  Weighted Average:   ${result['Weighted_Average']:8,.2f}")
        print(f"  Trending Average:   ${result['Trending_Average']:8,.2f}")
        print(f"  RECOMMENDED:        ${result['Recommended_Accrual']:8,.2f}")
        print(f"  Recent History:     {result['Historical_Values']}")
    
    # Export to Excel
    if not os.path.exists('Output'):
        os.makedirs('Output')
    
    df_results = pd.DataFrame(results)
    with pd.ExcelWriter('Output/Accruals_Forecast.xlsx', engine='xlsxwriter') as writer:
        df_results.to_excel(writer, sheet_name='Forecast_Summary', index=False)
        
        # Add a totals sheet
        totals = {
            'Method': ['Simple Average', 'Weighted Average', 'Trending Average', 'RECOMMENDED'],
            'Total_Amount': [
                sum([r['Simple_Average'] for r in results]),
                sum([r['Weighted_Average'] for r in results]),
                sum([r['Trending_Average'] for r in results]),
                sum([r['Recommended_Accrual'] for r in results])
            ]
        }
        
        df_totals = pd.DataFrame(totals)
        df_totals.to_excel(writer, sheet_name='Totals_Summary', index=False)
    
    print(f"\n{'='*80}")
    print("Excel report saved to: Output/Accruals_Forecast.xlsx")
    print("="*80)

if __name__ == "__main__":
    simple_forecast()
