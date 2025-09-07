from accruals_main import AccrualsSystem

# Test the actual system
system = AccrualsSystem()
print('Loading data...')
if system.load_data():
    print(f'Monthly columns found: {len(system.monthly_columns)}')
    for i, col in enumerate(system.monthly_columns):
        print(f'{i+1}. {col.strftime("%B %Y")}')
else:
    print('Failed to load data')
