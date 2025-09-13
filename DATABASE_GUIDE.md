# Database-Enhanced Accruals Forecasting System

## Overview

The enhanced accruals forecasting system now includes comprehensive database functionality to:

- **Store forecast versions** with timestamps and metadata
- **Track actual invoice data** for accuracy validation
- **Calculate accuracy metrics** for each forecasting method
- **Learn from historical performance** through adaptive weights
- **Provide reporting dashboards** for trend analysis

## Key Features

### 🗄️ Database Storage
- **SQLite database** stores all forecasts, actuals, and metrics
- **Version control** for comparing different forecast runs
- **Automatic backup** of all historical data

### 📊 Accuracy Tracking
- **Real-time comparison** of forecasts vs actual invoices
- **Method-specific accuracy** for each forecasting approach
- **Category-level performance** analysis

### 🤖 Adaptive Learning
- **Dynamic weight adjustment** based on historical accuracy
- **Method performance** tracking over time
- **Confidence scoring** for forecast reliability

### 🌐 Enhanced Web Interface
- **Multi-page dashboard** with navigation
- **Accuracy visualization** with charts and metrics
- **Database management** tools for data entry
- **Version comparison** across different forecast runs

## Usage Guide

### 1. Generate Forecasts with Database Storage

```python
from accruals_main import AccrualsSystem

# Initialize with database enabled (default)
system = AccrualsSystem(enable_database=True)

# Generate forecasts (automatically stored in database)
system.generate_forecasts()

# Custom version name (optional)
version_id = system.store_forecast_in_database("Monthly_Forecast_Sept_2025")
```

### 2. Add Actual Invoice Data

```python
# Sample actual data
actual_invoices = {
    'Training & Development': 85000.00,
    'IT Services': 120000.00,
    'Office Supplies': 8500.00
}

# Store actuals (this triggers accuracy calculation)
system.store_actuals_in_database(
    actual_invoices, 
    invoice_month=9, 
    invoice_year=2025,
    data_source="September 2025 Invoice Batch"
)
```

### 3. View Accuracy and Adaptive Weights

```python
from database_manager import DatabaseManager

db = DatabaseManager()

# Get accuracy summary
accuracy_df = db.get_accuracy_summary()
print(accuracy_df)

# Get adaptive weights for a category
weights = db.get_adaptive_weights('IT Services')
print(f"Adaptive weights: {weights}")
```

### 4. Use the Web Interface

Start the enhanced web interface:
```bash
streamlit run app.py
```

**Available Pages:**
- **🎯 Generate Forecast**: Create new forecasts with version naming
- **📈 Accuracy Dashboard**: View accuracy metrics and method comparison
- **💾 Database Management**: Add actual data and view database stats
- **📊 Version History**: Compare different forecast versions

## Database Schema

### Tables
- **forecast_versions**: Metadata for each forecast run
- **forecasts**: Individual category forecasts by version
- **actuals**: Actual invoice data for accuracy calculation
- **accuracy_metrics**: Calculated accuracy for each method
- **method_performance**: Aggregated performance statistics
- **learning_weights**: Adaptive weights for each category

### Automatic Features
- **Version tracking**: Every forecast gets a unique version ID
- **Accuracy calculation**: Automatic when actual data is added
- **Weight adaptation**: System learns from accuracy patterns
- **Performance updates**: Real-time statistics on method effectiveness

## Benefits

### For Analysts
- **Historical tracking** of forecast accuracy
- **Method comparison** to identify best approaches
- **Confidence metrics** for decision making
- **Trend analysis** across multiple forecast periods

### For Management
- **Accuracy reporting** with visual dashboards
- **Method performance** insights for process improvement
- **Version control** for audit trails
- **Predictive reliability** metrics

### For System Evolution
- **Adaptive learning** improves forecasts over time
- **Pattern recognition** in method effectiveness
- **Automatic optimization** of forecast weights
- **Data-driven improvements** to forecasting algorithms

## Advanced Features

### Adaptive Forecasting
The system learns from historical accuracy to automatically adjust method weights:
- **High-performing methods** get higher weights for specific categories
- **Confidence scoring** based on sample size and consistency
- **Dynamic adaptation** as more actual data becomes available

### Batch Processing
- **Excel upload** for bulk actual data entry
- **Automated processing** of invoice files
- **Batch accuracy** calculation across multiple periods

### Reporting & Analytics
- **Export capabilities** for external analysis
- **Chart visualizations** for stakeholder presentations
- **Trend analysis** across time periods
- **Method comparison** statistics

## File Structure

```
c:\Accurals/
├── accruals_main.py          # Enhanced main forecasting system
├── database_manager.py       # Database operations and management
├── app.py                   # Multi-page Streamlit web interface
├── test_database.py         # Database functionality testing
├── accruals_forecasts.db    # SQLite database (created automatically)
├── seasonal_analysis.py     # Seasonal pattern analysis
└── Input/
    └── Actual.xlsx          # Source data file
```

## Getting Started

1. **Install requirements** (if not already done):
   ```bash
   pip install pandas numpy openpyxl xlsxwriter streamlit plotly statsmodels
   ```

2. **Test database functionality**:
   ```bash
   python test_database.py
   ```

3. **Launch web interface**:
   ```bash
   streamlit run app.py
   ```

4. **Upload data** and generate your first forecast with database storage

5. **Add actual data** when invoices arrive to start accuracy tracking

6. **Monitor performance** through the accuracy dashboard

The system will automatically learn and improve forecasting accuracy over time based on the actual vs forecast performance data you provide.