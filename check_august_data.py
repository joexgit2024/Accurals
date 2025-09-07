import pandas as pd
from datetime import datetime

try:
    df = pd.read_excel('Input/Actual.xlsx')
    
    # Find date columns with data
    date_cols = [col for col in df.columns if isinstance(col, datetime)]
    date_cols = [col for col in date_cols if not df[col].isna().all()]
    date_cols.sort()
    
    print('=== ACTUAL DATA BY MONTH ===')
    print(f'Categories: {len(df)}')
    print()
    
    # Show each category's data for the last few months
    for idx, row in df.iterrows():
        category = row['Row Labels']
        print(f'{category}:')
        
        # Show last 6 months or all available months
        recent_months = date_cols[-6:] if len(date_cols) >= 6 else date_cols
        
        for month_col in recent_months:
            value = row[month_col]
            month_name = month_col.strftime('%b %Y')
            if pd.isna(value):
                print(f'  {month_name}: $0.00 (no data)')
            else:
                print(f'  {month_name}: ${value:,.2f}')
        
        print()
        
except Exception as e:
    print(f'Error: {e}')
