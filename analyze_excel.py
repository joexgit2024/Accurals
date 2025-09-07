import pandas as pd
from datetime import datetime

try:
    df = pd.read_excel('Input/Actual.xlsx')
    print('=== EXCEL FILE ANALYSIS ===')
    print(f'Total columns: {len(df.columns)}')
    print(f'Total rows: {len(df)}')
    print()
    
    print('=== ALL COLUMNS ===')
    for i, col in enumerate(df.columns):
        col_type = type(col).__name__
        print(f'{i+1:2d}. {col} ({col_type})')
    
    print()
    print('=== DATE COLUMNS ONLY ===')
    date_cols = [col for col in df.columns if isinstance(col, datetime)]
    date_cols.sort()
    
    print(f'Found {len(date_cols)} date columns:')
    for i, col in enumerate(date_cols):
        print(f'{i+1:2d}. {col.strftime("%Y-%m-%d (%B %Y)")}')
    
    if date_cols:
        print()
        print('=== DATE RANGE ===')
        print(f'First month: {date_cols[0].strftime("%B %Y")}')
        print(f'Last month: {date_cols[-1].strftime("%B %Y")}')
        
        # Calculate next month
        last = date_cols[-1]
        if last.month == 12:
            next_month = 1
            next_year = last.year + 1
        else:
            next_month = last.month + 1
            next_year = last.year
            
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        print(f'Next month to forecast: {month_names[next_month]} {next_year}')
        
        print()
        print('=== SAMPLE DATA FOR FIRST CATEGORY ===')
        if len(df) > 0:
            first_row = df.iloc[0]
            print(f'Category: {first_row.get("Row Labels", "N/A")}')
            for col in date_cols[-6:]:  # Show last 6 months
                value = first_row.get(col, 0)
                print(f'{col.strftime("%b %Y")}: ${value:,.2f}')
        
except Exception as e:
    print(f'Error: {e}')
