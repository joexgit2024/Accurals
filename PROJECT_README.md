# 📊 Accruals Forecasting System

A comprehensive Python-based system for predicting future accruals based on historical spending patterns using multiple forecasting methodologies.

## 🎯 **Overview**

This system analyzes historical spending data and generates accurate forecasts for future accruals using three different statistical methods:

- **Simple Average**: Basic average of historical spending
- **Weighted Average**: Recent months weighted more heavily  
- **Trending Average**: Linear trend extrapolation

**Final Recommendation**: Average of all three methods for balanced forecasting

## 📈 **Key Features**

- ✅ **Multiple Forecasting Methods**: Three different statistical approaches
- ✅ **Weekly Adjustment Algorithm**: Accounts for 4-week vs 5-week month differences
- ✅ **Professional Excel Reports**: Auto-fitted columns with currency formatting
- ✅ **Beautiful HTML Reports**: Shareable web-format reports for colleagues
- ✅ **Web Interface**: Interactive dashboard with charts and graphs
- ✅ **Confidence Levels**: Data quality indicators (High/Medium/Low)
- ✅ **Easy Monthly Updates**: Simple workflow for regular forecasting
- ✅ **Category Analysis**: Detailed breakdown by expense categories

## 🚀 **Quick Start**

### **Option 1: Command Line (Recommended for regular use)**
```bash
python accruals_main.py
```
*Generates both Excel and HTML reports*

### **Option 2: HTML Report Only (Perfect for sharing)**
```bash
python generate_html_report.py
```
*Creates beautiful HTML report for colleagues*

### **Option 3: Web Interface (Great for presentations)**
```bash
python -m streamlit run app.py
```

### **Option 4: Batch Files (Windows)**
- Double-click `run_forecast.bat` for Excel + HTML reports
- Double-click `generate_html_report.bat` for HTML report only
- Double-click `run_web_interface.bat` for web dashboard

## 📋 **Requirements**

```bash
pip install pandas numpy openpyxl xlsxwriter
# For web interface (optional):
pip install streamlit plotly
```

## 📁 **Project Structure**

```
Accurals/
├── Input/
│   └── Actual.xlsx              # Your monthly spending data
├── Output/                      # Generated forecast reports
├── accruals_main.py            # Main forecasting system
├── app.py                      # Interactive web dashboard
├── run_forecast.bat            # Windows batch file for easy execution
├── run_web_interface.bat       # Web interface launcher
└── README.md                   # This file
```

## 💼 **Usage Workflow**

1. **Update Data**: Add new month's actuals to `Input/Actual.xlsx`
2. **Run Forecast**: Execute the system using any of the methods above
3. **Review Results**: Check Excel reports in `Output/` folder
4. **Use Recommendations**: Apply forecasted accruals to your planning

## 📊 **Sample Results**

**August 2025 Forecast Example (Weekly-Adjusted):**
- Simple Average: $93,477.70
- Weighted Average: $92,728.20
- Trending Average: $90,479.71
- **RECOMMENDED: $92,228.53**

*Note: Results include weekly adjustment for calendar month differences*

## 🎨 **Web Interface Features**

- 📊 Interactive dashboard with real-time calculations
- 📈 Bar charts comparing forecasting methods
- 🥧 Pie charts showing category breakdowns
- 📋 Filterable data tables
- 💾 Multiple export options (Excel, CSV)
- 📚 Built-in methodology documentation

## 🔧 **Technical Details**

### **Forecasting Methods**

1. **Simple Average (Weekly-Adjusted)**
   - Arithmetic mean of normalized weekly rates
   - Adjusted for 4-week vs 5-week month patterns
   - Best for stable spending patterns

2. **Weighted Average (Weekly-Adjusted)**
   - Recent months receive higher weights on weekly rates
   - Better for capturing trends with calendar normalization

3. **Trending Average (Weekly-Adjusted)**
   - Linear regression on normalized weekly rates
   - Accounts for increasing/decreasing patterns
   - Eliminates calendar month bias

### **Weekly Adjustment Algorithm**
- **5-Week Months**: January, April, July, October
- **4-Week Months**: All other months
- **Process**: Historical values → Weekly rates → Forecasting → Target month conversion

### **Confidence Calculation**
- **High**: Coefficient of Variation < 0.2
- **Medium**: CV between 0.2-0.5  
- **Low**: CV > 0.5 or insufficient data

## 📈 **Excel Report Features**

- ✅ Auto-fitted columns for optimal readability
- ✅ Professional formatting with headers and borders
- ✅ Currency formatting for all financial data
- ✅ Multiple worksheets with detailed breakdowns
- ✅ Summary sheets with totals and recommendations

## 🌐 **Web Interface Setup**

1. Install dependencies: `pip install streamlit plotly`
2. Run: `python -m streamlit run app.py`
3. Open browser to: `http://localhost:8501`
4. Upload Excel file and view interactive results

## 🤝 **Contributing**

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 **License**

This project is open source and available under the MIT License.

## 🆘 **Support**

For issues or questions:
1. Check the documentation in the `README.md` files
2. Verify your Excel file format matches the expected structure
3. Ensure sufficient historical data (2-3 months minimum recommended)

---

**Created**: September 2025  
**Author**: joexgit2024  
**Version**: 1.0
