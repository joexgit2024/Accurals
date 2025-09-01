import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def analyze_actual_data():
    """
    Analyze the actual spending data to understand its structure
    """
    try:
        # Read the Excel file
        df = pd.read_excel('Input/Actual.xlsx')
        
        print("Data structure analysis:")
        print("=" * 50)
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst few rows:")
        print(df.head())
        print("\nData types:")
        print(df.dtypes)
        print("\nBasic statistics:")
        print(df.describe())
        
        # Check for any date columns
        print("\nSample data:")
        for col in df.columns:
            print(f"{col}: {df[col].iloc[0] if len(df) > 0 else 'No data'}")
            
        return df
        
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

if __name__ == "__main__":
    data = analyze_actual_data()
