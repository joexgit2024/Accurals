import pandas as pd
from datetime import datetime

try:
    df = pd.read_excel('Input/Actual.xlsx')
    
    # Find all date columns
    all_date_cols = [col for col in df.columns if isinstance(col, datetime)]
    all_date_cols.sort()
    
    print('=== ALL DATE COLUMNS ===')
    for i, col in enumerate(all_date_cols[:12]):  # Show first 12 months
        print(f'{i+1:2d}. {col.strftime("%Y-%m-%d (%B %Y)")}')
    
    print('\n=== DATA CHECK BY MONTH ===')
    for i, col in enumerate(all_date_cols[:12]):
        has_data = not df[col].isna().all()
        any_nonzero = (df[col] > 0).any() if has_data else False
        total_value = df[col].sum() if has_data else 0
        
        print(f'{col.strftime("%B %Y"):15} | Has Data: {has_data:5} | Non-zero: {any_nonzero:5} | Total: ${total_value:10,.2f}')
    
    print('\n=== AUGUST 2025 DETAILED CHECK ===')
    aug_2025 = datetime(2025, 8, 1)
    if aug_2025 in df.columns:
        aug_col = df[aug_2025]
        print('August 2025 values:')
        for idx, row in df.iterrows():
            category = row['Row Labels']
            aug_value = row[aug_2025]
            print(f'  {category}: ${aug_value} (NaN: {pd.isna(aug_value)})')
        
        print(f'\nAugust summary:')
        print(f'  All NaN: {aug_col.isna().all()}')
        print(f'  Any > 0: {(aug_col > 0).any()}')
        print(f'  Total: ${aug_col.sum()}')
    else:
        print('August 2025 column not found!')
        
except Exception as e:
    print(f'Error: {e}')
