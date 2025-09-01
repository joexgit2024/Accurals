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
- ✅ **Professional Excel Reports**: Auto-fitted columns with currency formatting
- ✅ **Web Interface**: Interactive dashboard with charts and graphs
- ✅ **Confidence Levels**: Data quality indicators (High/Medium/Low)
- ✅ **Easy Monthly Updates**: Simple workflow for regular forecasting
- ✅ **Category Analysis**: Detailed breakdown by expense categories

## 🚀 **Quick Start**

### **Option 1: Command Line (Recommended for regular use)**
```bash
python accruals_main.py
```

### **Option 2: Web Interface (Great for presentations)**
```bash
python -m streamlit run web_interface.py
```

### **Option 3: Batch Files (Windows)**
- Double-click `run_forecast.bat` for Excel reports
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
├── web_interface.py            # Interactive web dashboard
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

**August 2025 Forecast Example:**
- Simple Average: $102,493.62
- Weighted Average: $101,586.89
- Trending Average: $98,866.67
- **RECOMMENDED: $100,982.39**

## 🎨 **Web Interface Features**

- 📊 Interactive dashboard with real-time calculations
- 📈 Bar charts comparing forecasting methods
- 🥧 Pie charts showing category breakdowns
- 📋 Filterable data tables
- 💾 Multiple export options (Excel, CSV)
- 📚 Built-in methodology documentation

## 🔧 **Technical Details**

### **Forecasting Methods**

1. **Simple Average**
   - Arithmetic mean of historical data
   - Best for stable spending patterns

2. **Weighted Average**
   - Recent months receive higher weights
   - Better for capturing trends

3. **Trending Average**
   - Linear regression extrapolation
   - Accounts for increasing/decreasing patterns

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
2. Run: `python -m streamlit run web_interface.py`
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
