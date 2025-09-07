from accruals_main import AccrualsSystem
import pandas as pd
import numpy as np

# Test with all data (including August)
print('=== WITH AUGUST DATA (8 months) ===')
system_with_aug = AccrualsSystem()
if system_with_aug.load_data():
    system_with_aug.generate_forecasts()
    df_with_aug = pd.DataFrame(system_with_aug.results)
    total_with_aug = df_with_aug['Recommended_Accrual'].sum()
    print(f'Months used: {len(system_with_aug.monthly_columns)}')
    print(f'Last month: {system_with_aug.monthly_columns[-1].strftime("%B %Y")}')
    print(f'Total forecast: ${total_with_aug:,.2f}')
    print('Category breakdown:')
    for _, row in df_with_aug.iterrows():
        print(f'  {row["Category"]}: ${row["Recommended_Accrual"]:,.2f}')

print('\n' + '='*50)

# Simulate without August by manually removing it
print('=== WITHOUT AUGUST DATA (7 months) ===')
try:
    # Load data manually and exclude August
    data = pd.read_excel('Input/Actual.xlsx')
    
    # Remove August column
    aug_2025 = pd.Timestamp('2025-08-01')
    if aug_2025 in data.columns:
        data_no_aug = data.drop(columns=[aug_2025])
        
        # Save temporarily
        data_no_aug.to_excel('temp_no_august.xlsx', index=False)
        
        # Test system without August
        system_no_aug = AccrualsSystem(input_file='temp_no_august.xlsx')
        if system_no_aug.load_data():
            system_no_aug.generate_forecasts()
            df_no_aug = pd.DataFrame(system_no_aug.results)
            total_no_aug = df_no_aug['Recommended_Accrual'].sum()
            print(f'Months used: {len(system_no_aug.monthly_columns)}')
            print(f'Last month: {system_no_aug.monthly_columns[-1].strftime("%B %Y")}')
            print(f'Total forecast: ${total_no_aug:,.2f}')
            
            print('\n=== DIFFERENCE ===')
            print(f'With August:    ${total_with_aug:,.2f}')
            print(f'Without August: ${total_no_aug:,.2f}')
            print(f'Difference:     ${total_with_aug - total_no_aug:,.2f}')
            
        # Cleanup
        import os
        os.remove('temp_no_august.xlsx')
    
except Exception as e:
    print(f'Error in comparison: {e}')
