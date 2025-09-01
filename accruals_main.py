"""
Accruals Forecasting System - Main Module
==========================================

This system provides three forecasting methods for accrual predictions:
1. Simple Average: Basic average of historical spending
2. Weighted Average: Recent months weighted more heavily  
3. Trending Average: Linear trend extrapolation

Usage: python accruals_main.py
Output: Excel workbook with multiple scenarios and recommendations
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

class AccrualsSystem:
    def __init__(self, input_file='Input/Actual.xlsx'):
        self.input_file = input_file
        self.data = None
        self.monthly_columns = []
        self.results = []
        
    def load_data(self):
        """Load and validate the input Excel file"""
        try:
            self.data = pd.read_excel(self.input_file)
            
            # Find datetime columns (monthly data)
            self.monthly_columns = [col for col in self.data.columns if isinstance(col, datetime)]
            self.monthly_columns.sort()
            
            print(f"✓ Loaded data: {len(self.data)} categories, {len(self.monthly_columns)} months")
            return True
            
        except FileNotFoundError:
            print(f"✗ Error: Could not find input file '{self.input_file}'")
            return False
        except Exception as e:
            print(f"✗ Error loading data: {str(e)}")
            return False
    
    def analyze_category(self, row):
        """Analyze a single expense category and generate forecasts"""
        category = row['Row Labels']
        
        # Extract historical spending (exclude future months)
        historical_values = []
        for month_col in self.monthly_columns[:7]:  # Jan-Jul 2025
            value = row[month_col]
            if pd.notna(value) and value > 0:
                historical_values.append(float(value))
        
        if len(historical_values) == 0:
            return self._zero_forecast(row)
        
        # Method 1: Simple Average
        simple_avg = np.mean(historical_values)
        
        # Method 2: Weighted Average (recent months get higher weight)
        n = len(historical_values)
        weights = np.arange(1, n + 1) / sum(range(1, n + 1))
        weighted_avg = np.average(historical_values, weights=weights)
        
        # Method 3: Trending Average
        if len(historical_values) >= 2:
            # Linear regression for trend
            x = np.arange(len(historical_values))
            coeffs = np.polyfit(x, historical_values, 1)
            trend_forecast = coeffs[0] * len(historical_values) + coeffs[1]
            trend_forecast = max(0, trend_forecast)  # No negative forecasts
        else:
            trend_forecast = simple_avg
        
        # Final recommendation (average of three methods)
        recommendation = (simple_avg + weighted_avg + trend_forecast) / 3
        
        return {
            'Category': category,
            'SAP_Code': row['SAP'],
            'GL_Code': row['GLCode'],
            'Historical_Months': len(historical_values),
            'Historical_Average': round(np.mean(historical_values), 2),
            'Historical_Total': round(sum(historical_values), 2),
            'Simple_Average': round(simple_avg, 2),
            'Weighted_Average': round(weighted_avg, 2),
            'Trending_Average': round(trend_forecast, 2),
            'Recommended_Accrual': round(recommendation, 2),
            'Confidence': self._calculate_confidence(historical_values),
            'Recent_Values': [round(v, 2) for v in historical_values[-3:]]
        }
    
    def _zero_forecast(self, row):
        """Handle categories with no historical data"""
        return {
            'Category': row['Row Labels'],
            'SAP_Code': row['SAP'],
            'GL_Code': row['GLCode'],
            'Historical_Months': 0,
            'Historical_Average': 0,
            'Historical_Total': 0,
            'Simple_Average': 0,
            'Weighted_Average': 0,
            'Trending_Average': 0,
            'Recommended_Accrual': 0,
            'Confidence': 'No Data',
            'Recent_Values': []
        }
    
    def _calculate_confidence(self, values):
        """Calculate confidence level based on data consistency"""
        if len(values) < 2:
            return 'Low'
        
        cv = np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
        
        if cv < 0.2:
            return 'High'
        elif cv < 0.5:
            return 'Medium'
        else:
            return 'Low'
    
    def generate_forecasts(self):
        """Generate forecasts for all categories"""
        if not self.load_data():
            return False
        
        print("Generating forecasts...")
        self.results = []
        
        for idx, row in self.data.iterrows():
            forecast = self.analyze_category(row)
            self.results.append(forecast)
        
        return True
    
    def export_results(self, output_file=None):
        """Export results to Excel with enhanced formatting and auto-fit columns"""
        os.makedirs('Output', exist_ok=True)
        
        # Generate unique filename if not specified
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'Output/Accruals_Forecast_{timestamp}.xlsx'
        
        df = pd.DataFrame(self.results)
        
        # Calculate totals
        totals = {
            'Simple_Average_Total': df['Simple_Average'].sum(),
            'Weighted_Average_Total': df['Weighted_Average'].sum(),
            'Trending_Average_Total': df['Trending_Average'].sum(),
            'Recommended_Total': df['Recommended_Accrual'].sum()
        }
        
        # Create summary data
        summary_data = pd.DataFrame([
            {'Method': 'Simple Average', 'Total_Amount': totals['Simple_Average_Total'], 
             'Description': 'Average of historical spending'},
            {'Method': 'Weighted Average', 'Total_Amount': totals['Weighted_Average_Total'], 
             'Description': 'Recent months weighted more heavily'},
            {'Method': 'Trending Average', 'Total_Amount': totals['Trending_Average_Total'], 
             'Description': 'Linear trend extrapolation'},
            {'Method': 'RECOMMENDED', 'Total_Amount': totals['Recommended_Total'], 
             'Description': 'Average of all three methods'}
        ])
        
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Define formats
            currency_format = workbook.add_format({'num_format': '$#,##0.00'})
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            })
            
            # 1. Executive Summary Sheet
            summary_data.to_excel(writer, sheet_name='Executive_Summary', index=False)
            ws_summary = writer.sheets['Executive_Summary']
            
            # Auto-fit columns for Executive Summary
            for i, col in enumerate(summary_data.columns):
                max_len = max(
                    summary_data[col].astype(str).map(len).max() if len(summary_data) > 0 else 0,
                    len(str(col))
                )
                adjusted_width = min(max(max_len + 3, 12), 50)
                ws_summary.set_column(i, i, adjusted_width)
            
            # Format currency column
            ws_summary.set_column(1, 1, 15, currency_format)
            ws_summary.set_row(0, 20, header_format)
            
            # 2. Detailed Forecasts Sheet
            df.to_excel(writer, sheet_name='Detailed_Forecasts', index=False)
            ws_detailed = writer.sheets['Detailed_Forecasts']
            
            # Auto-fit columns for Detailed Forecasts
            currency_cols = ['Simple_Average', 'Weighted_Average', 'Trending_Average', 'Recommended_Accrual', 'Historical_Average', 'Historical_Total']
            
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).map(len).max() if len(df) > 0 else 0,
                    len(str(col))
                )
                adjusted_width = min(max(max_len + 3, 12), 50)
                
                # Apply currency formatting for financial columns
                if col in currency_cols:
                    ws_detailed.set_column(i, i, 15, currency_format)
                else:
                    ws_detailed.set_column(i, i, adjusted_width)
            
            ws_detailed.set_row(0, 20, header_format)
            
            # 3. Method-specific sheets
            methods = [
                ('Simple_Average', 'Simple Average Method'),
                ('Weighted_Average', 'Weighted Average Method'),
                ('Trending_Average', 'Trending Average Method')
            ]
            
            for method_col, sheet_name in methods:
                method_df = df[['Category', 'SAP_Code', 'GL_Code', method_col, 'Confidence', 'Historical_Months']].copy()
                method_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                ws_method = writer.sheets[sheet_name]
                
                # Auto-fit columns for method sheets
                for i, col in enumerate(method_df.columns):
                    max_len = max(
                        method_df[col].astype(str).map(len).max() if len(method_df) > 0 else 0,
                        len(str(col))
                    )
                    adjusted_width = min(max(max_len + 3, 12), 50)
                    
                    # Apply currency formatting for the method column
                    if col == method_col:
                        ws_method.set_column(i, i, 15, currency_format)
                    else:
                        ws_method.set_column(i, i, adjusted_width)
                
                ws_method.set_row(0, 20, header_format)
        
        print(f"✓ Results exported to: {output_file}")
        return output_file
    
    def print_summary(self):
        """Print summary to console"""
        if not self.results:
            print("No results to display")
            return
        
        df = pd.DataFrame(self.results)
        
        print("\n" + "="*80)
        print("ACCRUALS FORECAST SUMMARY - AUGUST 2025")
        print("="*80)
        print(f"Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Categories analyzed: {len(self.results)}")
        
        print(f"\nFORECAST TOTALS:")
        print(f"Simple Average:    ${df['Simple_Average'].sum():>12,.2f}")
        print(f"Weighted Average:  ${df['Weighted_Average'].sum():>12,.2f}")
        print(f"Trending Average:  ${df['Trending_Average'].sum():>12,.2f}")
        print(f"RECOMMENDED:       ${df['Recommended_Accrual'].sum():>12,.2f}")
        
        print(f"\nCATEGORY BREAKDOWN:")
        print("-" * 80)
        for result in self.results:
            if result['Recommended_Accrual'] > 0:
                print(f"{result['Category']:<40} ${result['Recommended_Accrual']:>10,.2f} ({result['Confidence']})")
        
        print("="*80)

def main():
    """Main execution function"""
    print("Starting Accruals Forecasting System...")
    print("="*50)
    
    # Initialize system
    system = AccrualsSystem()
    
    # Generate forecasts
    if system.generate_forecasts():
        # Export results
        output_file = system.export_results()
        
        # Print summary
        system.print_summary()
        
        print(f"\n✓ Process completed successfully!")
        print(f"📊 Excel report: {output_file}")
        
    else:
        print("✗ Forecasting failed. Please check your input file.")

if __name__ == "__main__":
    main()
