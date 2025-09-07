from accruals_main import AccrualsSystem
import pandas as pd

print('=== QUICK VERIFICATION ===')
system = AccrualsSystem()
if system.generate_forecasts():
    df = pd.DataFrame(system.results)
    total = df['Recommended_Accrual'].sum()
    print(f'Target Month: {system.target_month_name} {system.target_year}')
    print(f'Historical Range: {system.monthly_columns[0].strftime("%B %Y")} - {system.monthly_columns[-1].strftime("%B %Y")}')
    print(f'Total Recommended: ${total:,.2f}')
    print()
    print('Category Details:')
    for _, row in df.iterrows():
        print(f'  {row["Category"]}: ${row["Recommended_Accrual"]:,.2f}')
