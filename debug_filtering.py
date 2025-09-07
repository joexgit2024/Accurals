import pandas as pd
from datetime import datetime

# Simulate the exact logic from load_data
try:
    data = pd.read_excel('Input/Actual.xlsx')
    
    # Find datetime columns (monthly data)
    all_monthly_columns = [col for col in data.columns if isinstance(col, datetime)]
    all_monthly_columns.sort()
    
    # Only include columns that have actual data (not all NaN)
    monthly_columns = []
    print('=== FILTERING PROCESS ===')
    for i, col in enumerate(all_monthly_columns[:12]):
        is_all_nan = data[col].isna().all()
        print(f'{i+1:2d}. {col.strftime("%B %Y"):15} | All NaN: {is_all_nan:5} | Include: {not is_all_nan}')
        
        if not data[col].isna().all():  # If column has at least some data
            monthly_columns.append(col)
    
    print(f'\n=== FINAL RESULT ===')
    print(f'Total columns with data: {len(monthly_columns)}')
    if monthly_columns:
        print(f'Date range: {monthly_columns[0].strftime("%B %Y")} - {monthly_columns[-1].strftime("%B %Y")}')
        
        # Calculate next month
        last_month = monthly_columns[-1]
        if last_month.month == 12:
            target_month = 1
            target_year = last_month.year + 1
        else:
            target_month = last_month.month + 1
            target_year = last_month.year
            
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        print(f'Next forecast month: {month_names[target_month]} {target_year}')
        
except Exception as e:
    print(f'Error: {e}')
