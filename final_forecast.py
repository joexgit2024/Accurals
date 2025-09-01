import pandas as pd
import numpy as np
from datetime import datetime
import os

def create_accruals_forecast():
    """
    Create comprehensive accruals forecast with multiple scenarios
    """
    try:
        # Load the actual spending data
        df = pd.read_excel('Input/Actual.xlsx')
        
        # Identify monthly columns (datetime objects)
        monthly_columns = []
        for col in df.columns:
            if isinstance(col, datetime):
                monthly_columns.append(col)
        
        monthly_columns.sort()
        
        # Create results list
        forecast_results = []
        
        for idx, row in df.iterrows():
            category = row['Row Labels']
            sap_code = row['SAP']
            gl_code = row['GLCode']
            
            # Extract actual spending data (first 7 months of 2025)
            actual_values = []
            month_names = []
            
            for month_col in monthly_columns[:7]:  # Jan to July 2025
                value = row[month_col]
                month_name = month_col.strftime('%Y-%m')
                month_names.append(month_name)
                
                if pd.notna(value):
                    actual_values.append(float(value))
                else:
                    actual_values.append(0.0)
            
            # Filter out zero values for calculation
            non_zero_values = [v for v in actual_values if v > 0]
            
            if len(non_zero_values) > 0:
                # Method 1: Simple Average
                simple_avg = sum(non_zero_values) / len(non_zero_values)
                
                # Method 2: Weighted Average (more weight on recent months)
                if len(non_zero_values) >= 2:
                    weights = list(range(1, len(non_zero_values) + 1))
                    weight_sum = sum(weights)
                    weighted_avg = sum(val * weight for val, weight in zip(non_zero_values, weights)) / weight_sum
                else:
                    weighted_avg = simple_avg
                
                # Method 3: Trending Average (linear trend)
                if len(non_zero_values) >= 3:
                    # Simple linear trend using first and last values
                    months_span = len(non_zero_values) - 1
                    if months_span > 0:
                        trend_rate = (non_zero_values[-1] - non_zero_values[0]) / months_span
                        trending_avg = non_zero_values[-1] + trend_rate
                    else:
                        trending_avg = non_zero_values[-1]
                    
                    # Ensure trending forecast is not negative
                    trending_avg = max(0, trending_avg)
                else:
                    trending_avg = simple_avg
                
                # Final recommendation (average of three methods)
                recommendation = (simple_avg + weighted_avg + trending_avg) / 3
                
            else:
                # No historical data available
                simple_avg = weighted_avg = trending_avg = recommendation = 0
            
            # Prepare result
            result = {
                'Category': category,
                'SAP_Code': sap_code,
                'GL_Code': gl_code,
                'Jan_2025': actual_values[0] if len(actual_values) > 0 else 0,
                'Feb_2025': actual_values[1] if len(actual_values) > 1 else 0,
                'Mar_2025': actual_values[2] if len(actual_values) > 2 else 0,
                'Apr_2025': actual_values[3] if len(actual_values) > 3 else 0,
                'May_2025': actual_values[4] if len(actual_values) > 4 else 0,
                'Jun_2025': actual_values[5] if len(actual_values) > 5 else 0,
                'Jul_2025': actual_values[6] if len(actual_values) > 6 else 0,
                'Simple_Average_Forecast': round(simple_avg, 2),
                'Weighted_Average_Forecast': round(weighted_avg, 2),
                'Trending_Average_Forecast': round(trending_avg, 2),
                'Recommended_August_Accrual': round(recommendation, 2),
                'Data_Points_Used': len(non_zero_values)
            }
            
            forecast_results.append(result)
        
        # Create Excel output
        if not os.path.exists('Output'):
            os.makedirs('Output')
        
        # Convert to DataFrame
        results_df = pd.DataFrame(forecast_results)
        
        # Calculate totals
        total_simple = results_df['Simple_Average_Forecast'].sum()
        total_weighted = results_df['Weighted_Average_Forecast'].sum()
        total_trending = results_df['Trending_Average_Forecast'].sum()
        total_recommended = results_df['Recommended_August_Accrual'].sum()
        
        # Create summary totals
        summary_data = {
            'Forecasting_Method': ['Simple Average', 'Weighted Average', 'Trending Average', 'RECOMMENDED ACCRUAL'],
            'Total_Amount': [total_simple, total_weighted, total_trending, total_recommended],
            'Description': [
                'Average of historical non-zero values',
                'Weighted average giving more weight to recent months',
                'Linear trend extrapolation from historical data',
                'Average of all three forecasting methods'
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        
        # Export to Excel with multiple sheets
        with pd.ExcelWriter('Output/Accruals_Forecast_Report.xlsx', engine='xlsxwriter') as writer:
            
            # Summary sheet
            summary_df.to_excel(writer, sheet_name='Executive_Summary', index=False)
            
            # Auto-fit columns for Executive Summary
            worksheet_summary = writer.sheets['Executive_Summary']
            for i, col in enumerate(summary_df.columns):
                max_len = max(
                    summary_df[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet_summary.set_column(i, i, max_len)
            
            # Detailed forecasts
            results_df.to_excel(writer, sheet_name='Detailed_Forecasts', index=False)
            
            # Auto-fit columns for Detailed Forecasts
            worksheet_detailed = writer.sheets['Detailed_Forecasts']
            for i, col in enumerate(results_df.columns):
                max_len = max(
                    results_df[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet_detailed.set_column(i, i, max_len)
            
            # Individual method sheets
            simple_method = results_df[['Category', 'SAP_Code', 'GL_Code', 'Simple_Average_Forecast', 'Data_Points_Used']].copy()
            simple_method.to_excel(writer, sheet_name='Simple_Average_Method', index=False)
            
            # Auto-fit columns for Simple Average Method
            worksheet_simple = writer.sheets['Simple_Average_Method']
            for i, col in enumerate(simple_method.columns):
                max_len = max(
                    simple_method[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet_simple.set_column(i, i, max_len)
            
            weighted_method = results_df[['Category', 'SAP_Code', 'GL_Code', 'Weighted_Average_Forecast', 'Data_Points_Used']].copy()
            weighted_method.to_excel(writer, sheet_name='Weighted_Average_Method', index=False)
            
            # Auto-fit columns for Weighted Average Method
            worksheet_weighted = writer.sheets['Weighted_Average_Method']
            for i, col in enumerate(weighted_method.columns):
                max_len = max(
                    weighted_method[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet_weighted.set_column(i, i, max_len)
            
            trending_method = results_df[['Category', 'SAP_Code', 'GL_Code', 'Trending_Average_Forecast', 'Data_Points_Used']].copy()
            trending_method.to_excel(writer, sheet_name='Trending_Average_Method', index=False)
            
            # Auto-fit columns for Trending Average Method
            worksheet_trending = writer.sheets['Trending_Average_Method']
            for i, col in enumerate(trending_method.columns):
                max_len = max(
                    trending_method[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet_trending.set_column(i, i, max_len)
            
            # Historical data for reference
            historical_data = results_df[['Category', 'SAP_Code', 'GL_Code', 'Jan_2025', 'Feb_2025', 'Mar_2025', 'Apr_2025', 'May_2025', 'Jun_2025', 'Jul_2025']].copy()
            historical_data.to_excel(writer, sheet_name='Historical_Actuals', index=False)
            
            # Auto-fit columns for Historical Actuals
            worksheet_historical = writer.sheets['Historical_Actuals']
            for i, col in enumerate(historical_data.columns):
                max_len = max(
                    historical_data[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet_historical.set_column(i, i, max_len)
        
        # Print summary to console
        print("="*80)
        print("ACCRUALS FORECASTING SYSTEM - AUGUST 2025 PROJECTIONS")
        print("="*80)
        print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Input File: Input/Actual.xlsx")
        print(f"Categories Analyzed: {len(forecast_results)}")
        print("")
        
        print("TOTAL FORECASTS BY METHOD:")
        print(f"  Simple Average:      ${total_simple:>12,.2f}")
        print(f"  Weighted Average:    ${total_weighted:>12,.2f}")
        print(f"  Trending Average:    ${total_trending:>12,.2f}")
        print(f"  RECOMMENDED TOTAL:   ${total_recommended:>12,.2f}")
        print("")
        
        print("CATEGORY BREAKDOWN:")
        print("-" * 80)
        for result in forecast_results:
            if result['Recommended_August_Accrual'] > 0:
                print(f"{result['Category']:<35} ${result['Recommended_August_Accrual']:>10,.2f}")
        
        print("")
        print("="*80)
        print("EXCEL REPORT GENERATED: Output/Accruals_Forecast_Report.xlsx")
        print("="*80)
        
        return results_df
        
    except Exception as e:
        print(f"Error in forecasting: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    create_accruals_forecast()
