"""
Excel Utilities for Accruals Forecasting System
==============================================

This module provides enhanced Excel export functionality with auto-fit columns,
formatting, and professional styling for all worksheets.
"""

import pandas as pd
import numpy as np


def auto_fit_columns(worksheet, dataframe, start_col=0):
    """
    Auto-fit columns in an Excel worksheet based on content length
    
    Args:
        worksheet: xlsxwriter worksheet object
        dataframe: pandas DataFrame
        start_col: starting column index (default 0)
    """
    for i, col in enumerate(dataframe.columns):
        # Calculate max length considering both data and header
        max_len = max(
            dataframe[col].astype(str).map(len).max() if len(dataframe) > 0 else 0,
            len(str(col))
        )
        
        # Add some padding and set reasonable limits
        adjusted_width = min(max(max_len + 3, 10), 50)
        worksheet.set_column(start_col + i, start_col + i, adjusted_width)


def format_currency_columns(workbook, worksheet, dataframe, currency_columns):
    """
    Apply currency formatting to specified columns
    
    Args:
        workbook: xlsxwriter workbook object
        worksheet: xlsxwriter worksheet object
        dataframe: pandas DataFrame
        currency_columns: list of column names to format as currency
    """
    currency_format = workbook.add_format({'num_format': '$#,##0.00'})
    
    for col_name in currency_columns:
        if col_name in dataframe.columns:
            col_idx = dataframe.columns.get_loc(col_name)
            # Apply to data range (excluding header)
            worksheet.set_column(col_idx, col_idx, None, currency_format)


def add_header_formatting(workbook, worksheet, num_columns):
    """
    Add professional header formatting
    
    Args:
        workbook: xlsxwriter workbook object
        worksheet: xlsxwriter worksheet object
        num_columns: number of columns to format
    """
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    # Apply header formatting to first row
    worksheet.set_row(0, 20, header_format)


def create_enhanced_excel_export(results_data, output_file, title="Accruals Forecast Report"):
    """
    Create an enhanced Excel export with professional formatting and auto-fit columns
    
    Args:
        results_data: List of dictionaries containing forecast results
        output_file: Output file path
        title: Report title
    """
    
    # Convert results to DataFrame
    df = pd.DataFrame(results_data)
    
    # Calculate totals for summary
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
        
        # Define currency columns
        currency_cols = ['Simple_Average', 'Weighted_Average', 'Trending_Average', 
                        'Recommended_Accrual', 'Historical_Average', 'Historical_Total', 'Total_Amount']
        
        # 1. Executive Summary Sheet
        summary_data.to_excel(writer, sheet_name='Executive_Summary', index=False)
        ws_summary = writer.sheets['Executive_Summary']
        auto_fit_columns(ws_summary, summary_data)
        format_currency_columns(workbook, ws_summary, summary_data, ['Total_Amount'])
        add_header_formatting(workbook, ws_summary, len(summary_data.columns))
        
        # 2. Detailed Forecasts Sheet
        df.to_excel(writer, sheet_name='Detailed_Forecasts', index=False)
        ws_detailed = writer.sheets['Detailed_Forecasts']
        auto_fit_columns(ws_detailed, df)
        format_currency_columns(workbook, ws_detailed, df, currency_cols)
        add_header_formatting(workbook, ws_detailed, len(df.columns))
        
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
            auto_fit_columns(ws_method, method_df)
            format_currency_columns(workbook, ws_method, method_df, [method_col])
            add_header_formatting(workbook, ws_method, len(method_df.columns))
        
        # 4. Confidence Analysis Sheet
        confidence_summary = df.groupby('Confidence').agg({
            'Recommended_Accrual': ['count', 'sum', 'mean'],
            'Historical_Months': 'mean'
        }).round(2)
        
        confidence_summary.columns = ['Count', 'Total_Amount', 'Average_Amount', 'Avg_Historical_Months']
        confidence_summary = confidence_summary.reset_index()
        
        confidence_summary.to_excel(writer, sheet_name='Confidence_Analysis', index=False)
        ws_confidence = writer.sheets['Confidence_Analysis']
        auto_fit_columns(ws_confidence, confidence_summary)
        format_currency_columns(workbook, ws_confidence, confidence_summary, ['Total_Amount', 'Average_Amount'])
        add_header_formatting(workbook, ws_confidence, len(confidence_summary.columns))
        
        # 5. Category Performance Sheet (if historical data available)
        if 'Recent_Values' in df.columns:
            performance_data = []
            for _, row in df.iterrows():
                if row['Recent_Values'] and len(row['Recent_Values']) > 1:
                    recent_vals = row['Recent_Values']
                    trend = 'Increasing' if recent_vals[-1] > recent_vals[0] else 'Decreasing'
                    volatility = np.std(recent_vals) / np.mean(recent_vals) if np.mean(recent_vals) > 0 else 0
                    
                    performance_data.append({
                        'Category': row['Category'],
                        'Trend': trend,
                        'Volatility': round(volatility, 2),
                        'Latest_Value': recent_vals[-1] if recent_vals else 0,
                        'Recommended_Accrual': row['Recommended_Accrual']
                    })
            
            if performance_data:
                performance_df = pd.DataFrame(performance_data)
                performance_df.to_excel(writer, sheet_name='Category_Performance', index=False)
                ws_performance = writer.sheets['Category_Performance']
                auto_fit_columns(ws_performance, performance_df)
                format_currency_columns(workbook, ws_performance, performance_df, ['Latest_Value', 'Recommended_Accrual'])
                add_header_formatting(workbook, ws_performance, len(performance_df.columns))
    
    return output_file


def export_to_multiple_formats(results_data, base_filename="accruals_forecast"):
    """
    Export results to multiple formats (Excel, CSV, etc.)
    
    Args:
        results_data: List of dictionaries containing forecast results
        base_filename: Base filename without extension
    
    Returns:
        Dictionary with file paths for each format
    """
    import os
    
    # Ensure output directory exists
    os.makedirs('Output', exist_ok=True)
    
    # Create DataFrame
    df = pd.DataFrame(results_data)
    
    # Generate timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    file_paths = {}
    
    # Enhanced Excel export
    excel_file = f"Output/{base_filename}_{timestamp}.xlsx"
    create_enhanced_excel_export(results_data, excel_file)
    file_paths['excel'] = excel_file
    
    # CSV export
    csv_file = f"Output/{base_filename}_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    file_paths['csv'] = csv_file
    
    # Summary text file
    txt_file = f"Output/{base_filename}_summary_{timestamp}.txt"
    with open(txt_file, 'w') as f:
        f.write("ACCRUALS FORECAST SUMMARY\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Recommended Accrual: ${df['Recommended_Accrual'].sum():,.2f}\n\n")
        
        f.write("BREAKDOWN BY CATEGORY:\n")
        f.write("-" * 40 + "\n")
        for _, row in df.iterrows():
            if row['Recommended_Accrual'] > 0:
                f.write(f"{row['Category']:<30} ${row['Recommended_Accrual']:>10,.2f}\n")
    
    file_paths['summary'] = txt_file
    
    return file_paths
