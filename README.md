# Accruals Forecasting System - Documentation

## Overview
This system analyzes historical spending data and generates forecasts for future accruals using three different methodologies. The current setup processes your `Input/Actual.xlsx` file and produces comprehensive Excel reports with forecasting recommendations.

## Current Results Summary (August 2025 Forecast)
Based on your actual spending data from January-July 2025:

**TOTAL RECOMMENDED ACCRUAL: $100,982.39**

### Breakdown by Method:
- **Simple Average**: $102,493.62
- **Weighted Average**: $101,586.89  
- **Trending Average**: $98,866.67
- **Final Recommendation**: $100,982.39 (average of all three)

### Category Breakdown:
- **Consumables - Variable**: $13,581.81 (Medium confidence)
- **Handling - Variable**: $35,684.41 (High confidence)
- **Management - Fixed**: $16,144.65 (High confidence)
- **Storage - Fixed**: $29,107.87 (High confidence)
- **Storage - Variable**: $6,463.65 (Medium confidence)

## Forecasting Methods Explained

### 1. Simple Average
- **What it does**: Calculates the arithmetic mean of historical spending
- **Best for**: Stable, consistent spending patterns
- **Formula**: Sum of historical values ÷ Number of periods

### 2. Weighted Average
- **What it does**: Gives more importance to recent months
- **Best for**: Capturing recent trends and seasonal changes
- **Formula**: Recent months receive higher weights in the calculation

### 3. Trending Average
- **What it does**: Uses linear regression to project future spending based on trends
- **Best for**: Accounts for increasing or decreasing spending patterns
- **Formula**: Extrapolates the linear trend from historical data

## Files Generated

### Excel Reports Created:
1. **`Output/Accruals_Forecast_Final.xlsx`** - Main comprehensive report
   - Executive Summary with totals
   - Detailed forecasts for all categories
   - Individual method sheets
   - Confidence levels for each forecast

2. **`Output/Accruals_Forecast_Report.xlsx`** - Alternative format
3. **`Output/Accruals_Forecast.xlsx`** - Basic forecast summary

## How to Use the System

### Current Command-Line Version:
```powershell
cd c:\Accurals
C:/Users/JX1040/AppData/Local/Microsoft/WindowsApps/python3.12.exe accruals_main.py
```

### Monthly Update Process:
1. Update your `Input/Actual.xlsx` file with new monthly data
2. Run the forecasting system
3. Review the generated Excel reports
4. Use the recommendations for your accrual planning

## Web UI Option - Should You Create One?

### Pros of Creating a Web UI:
✅ **User-friendly interface** - Easier for non-technical users
✅ **Visual charts and graphs** - Better data visualization  
✅ **Interactive exploration** - Filter and drill down into data
✅ **Multi-user access** - Team members can access remotely
✅ **Real-time updates** - Upload new data and get instant results
✅ **Professional presentation** - Better for stakeholder meetings

### Cons of Web UI:
❌ **Additional complexity** - More development and maintenance
❌ **Server requirements** - Need hosting infrastructure
❌ **Security considerations** - File uploads and data protection
❌ **Training needed** - Users need to learn new interface

### Recommendation:

**For Your Current Needs**: The command-line version is perfectly adequate because:
- You're the primary user updating monthly data
- Excel output is familiar and widely used
- Simple monthly process doesn't require complex interface
- Easy to integrate into existing workflows

**Consider Web UI If**:
- Multiple people need to run forecasts
- You want to demo the system to stakeholders
- You need real-time collaboration
- You want interactive charts and dashboards

## Web UI Setup (Optional)

If you decide to create the web interface:

```powershell
# Install additional packages
pip install streamlit plotly

# Run the web interface
streamlit run web_interface.py
```

This will create a local web server at `http://localhost:8501` with:
- File upload interface
- Interactive charts
- Real-time forecasting
- Export capabilitiesC:/Users/JX1040/AppData/Local/Microsoft/WindowsApps/python3.12.exe -m streamlit run web_interface.py

# How to Run the Web Interface

To launch the interactive web dashboard, use the following command in PowerShell or the VS Code terminal:

```
C:/Users/JX1040/AppData/Local/Microsoft/WindowsApps/python3.12.exe -m streamlit run web_interface.py
```

- This will start the Streamlit server and open the dashboard at http://localhost:8501 in your browser.
- You can also double-click `run_web_interface.bat` in the project folder for the same result.

## Advanced Features You Could Add

### 1. Seasonality Adjustment
- Account for seasonal spending patterns
- Holiday and quarter-end adjustments

### 2. Confidence Intervals
- Provide forecast ranges (optimistic/pessimistic scenarios)
- Statistical confidence levels

### 3. Budget Variance Analysis
- Compare forecasts to budget allocations
- Flag significant variances

### 4. Multi-Month Forecasting
- Predict multiple months ahead
- Rolling forecasts with actual updates

### 5. Category Grouping
- Aggregate by cost centers or departments
- Hierarchical forecasting

## Maintenance and Updates

### Monthly Process:
1. Update `Input/Actual.xlsx` with new actuals
2. Run the forecasting script
3. Review Excel reports
4. Archive previous forecasts for comparison

### Quarterly Review:
- Analyze forecast accuracy
- Adjust methodologies if needed
- Update confidence thresholds

## Technical Notes

### System Requirements:
- Python 3.12+
- pandas, numpy, openpyxl, xlsxwriter packages
- Windows PowerShell (current setup)

### File Structure:
```
c:\Accurals/
├── Input/
│   └── Actual.xlsx          # Your monthly spending data
├── Output/                  # Generated forecast reports
├── accruals_main.py        # Main forecasting system
├── web_interface.py        # Optional web UI
└── Documentation.md        # This file
```

## Support and Troubleshooting

### Common Issues:
1. **"File not found"** - Ensure `Input/Actual.xlsx` exists
2. **"No forecast generated"** - Check for valid historical data
3. **"Zero forecasts"** - Verify data format and date columns

### Getting Help:
- Check the console output for error messages
- Verify your Excel file structure matches the expected format
- Ensure sufficient historical data (at least 2-3 months recommended)

---

**Created**: September 1, 2025  
**Last Updated**: September 1, 2025  
**Version**: 1.0
