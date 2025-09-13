from accruals_main import AccrualsSystem
import pandas as pd

print('=== SEASONAL FORECAST COMPARISON ===')
system = AccrualsSystem()
if system.generate_forecasts():
    df = pd.DataFrame(system.results)
    
    print(f'Target Month: {system.target_month_name} {system.target_year}')
    print(f'Historical Range: {system.monthly_columns[0].strftime("%B %Y")} - {system.monthly_columns[-1].strftime("%B %Y")}')
    print()
    
    # Calculate totals for each method
    simple_total = df['Simple_Average'].sum()
    weighted_total = df['Weighted_Average'].sum()
    trending_total = df['Trending_Average'].sum()
    seasonal_total = df['Seasonal_Forecast'].sum()
    recommended_total = df['Recommended_Accrual'].sum()
    
    print('📊 FORECAST TOTALS BY METHOD:')
    print(f'  Simple Average:    ${simple_total:8,.2f}')
    print(f'  Weighted Average:  ${weighted_total:8,.2f}')
    print(f'  Trending Average:  ${trending_total:8,.2f}')
    print(f'  🌟 Seasonal Forecast: ${seasonal_total:8,.2f}')
    print(f'  RECOMMENDED (4-method avg): ${recommended_total:8,.2f}')
    
    print('\n📋 CATEGORY BREAKDOWN:')
    print('Category'.ljust(25), 'Simple'.rjust(10), 'Weighted'.rjust(10), 'Trending'.rjust(10), 'Seasonal'.rjust(10), 'Final'.rjust(10))
    print('-' * 85)
    
    for _, row in df.iterrows():
        print(f"{row['Category'][:24]:25} ${row['Simple_Average']:8,.0f} ${row['Weighted_Average']:8,.0f} ${row['Trending_Average']:8,.0f} ${row['Seasonal_Forecast']:8,.0f} ${row['Recommended_Accrual']:8,.0f}")
    
    print('\n🔍 SEASONAL IMPACT ANALYSIS:')
    for _, row in df.iterrows():
        category = row['Category']
        seasonal = row['Seasonal_Forecast']
        simple = row['Simple_Average']
        diff = seasonal - simple
        pct_diff = (diff / simple * 100) if simple > 0 else 0
        
        impact = "📈 Higher" if diff > 0 else "📉 Lower" if diff < 0 else "➡️ Same"
        print(f"  {category[:30]:30} {impact} by ${diff:6,.0f} ({pct_diff:+5.1f}%)")
        
    print(f'\n🎯 OVERALL SEASONAL ADJUSTMENT: ${seasonal_total - simple_total:+,.2f} vs Simple Average')