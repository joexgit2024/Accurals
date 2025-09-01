import pandas as pd
from datetime import datetime

# Load data
df = pd.read_excel('Input/Actual.xlsx')

# Get monthly columns
monthly_cols = [col for col in df.columns if isinstance(col, datetime)]
monthly_cols.sort()

print("Monthly columns:")
for i, col in enumerate(monthly_cols):
    print(f"{i}: {col.strftime('%Y-%m')}")

print(f"\nFirst category data:")
category_data = df.iloc[0]
print(f"Category: {category_data['Row Labels']}")

print("\nMonthly values:")
for col in monthly_cols[:10]:  # First 10 months
    value = category_data[col]
    print(f"{col.strftime('%Y-%m')}: {value}")

# Check which months have data
print(f"\nData availability:")
for col in monthly_cols:
    non_null_count = df[col].count()
    print(f"{col.strftime('%Y-%m')}: {non_null_count} categories have data")
