import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

def analyze_seasonal_patterns():
    """Analyze seasonal patterns in accruals data"""
    try:
        # Load data
        df = pd.read_excel('Input/Actual.xlsx')
        print("=== SEASONAL PATTERN ANALYSIS ===\n")
        
        # Get date columns with data
        date_cols = [col for col in df.columns if isinstance(col, datetime)]
        date_cols = [col for col in date_cols if not df[col].isna().all()]
        date_cols.sort()
        
        print(f"Data range: {date_cols[0].strftime('%B %Y')} - {date_cols[-1].strftime('%B %Y')}")
        print(f"Total months: {len(date_cols)}\n")
        
        # Analyze each category for seasonal patterns
        categories = df['Row Labels'].tolist()
        
        seasonal_analysis = {}
        
        for category in categories:
            print(f"🔍 Analyzing: {category}")
            
            # Get category data
            cat_data = df[df['Row Labels'] == category]
            if len(cat_data) == 0:
                continue
                
            # Extract time series data
            values = []
            dates = []
            
            for date_col in date_cols:
                value = cat_data[date_col].iloc[0]
                if pd.notna(value) and value > 0:
                    values.append(float(value))
                    dates.append(date_col)
            
            if len(values) < 4:  # Need at least 4 points for analysis
                print(f"  ⚠️  Insufficient data ({len(values)} points)\n")
                continue
            
            # Create time series
            ts = pd.Series(values, index=dates)
            
            # Basic statistics
            print(f"  📊 Data points: {len(values)}")
            print(f"  💰 Average: ${np.mean(values):,.2f}")
            print(f"  📈 Trend: {calculate_trend(values)}")
            print(f"  🔄 Volatility (CV): {np.std(values)/np.mean(values):.2%}")
            
            # Seasonal analysis (if enough data)
            if len(values) >= 8:  # Need enough data for seasonal decomposition
                try:
                    # Quarterly seasonality (period=3 for quarterly in monthly data)
                    seasonal_strength = analyze_seasonality(values, period=3)
                    print(f"  🌟 Quarterly pattern strength: {seasonal_strength:.2%}")
                    
                    # Monthly patterns
                    monthly_patterns = analyze_monthly_patterns(dates, values)
                    print(f"  📅 Monthly pattern detected: {monthly_patterns}")
                    
                    seasonal_analysis[category] = {
                        'data': values,
                        'dates': dates,
                        'seasonal_strength': seasonal_strength,
                        'monthly_patterns': monthly_patterns,
                        'trend': calculate_trend(values),
                        'volatility': np.std(values)/np.mean(values)
                    }
                    
                except Exception as e:
                    print(f"  ❌ Seasonal analysis failed: {e}")
            else:
                print(f"  ⚠️  Need more data for seasonal analysis (have {len(values)}, need 8+)")
            
            print()
        
        # Overall seasonal summary
        print("=== SEASONAL SUMMARY ===")
        if seasonal_analysis:
            avg_seasonal_strength = np.mean([cat['seasonal_strength'] for cat in seasonal_analysis.values()])
            print(f"📊 Average seasonal strength: {avg_seasonal_strength:.2%}")
            
            # Identify most seasonal categories
            seasonal_cats = [(cat, data['seasonal_strength']) for cat, data in seasonal_analysis.items()]
            seasonal_cats.sort(key=lambda x: x[1], reverse=True)
            
            print("\n🏆 Most seasonal categories:")
            for cat, strength in seasonal_cats:
                print(f"  {cat}: {strength:.2%}")
        
        return seasonal_analysis
        
    except Exception as e:
        print(f"Error in seasonal analysis: {e}")
        return {}

def calculate_trend(values):
    """Calculate trend direction and strength"""
    if len(values) < 2:
        return "Insufficient data"
    
    x = np.arange(len(values))
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
    
    if abs(slope) < np.std(values) * 0.1:  # Very small slope
        return "Stable"
    elif slope > 0:
        return f"Increasing ({slope:.1f}/month)"
    else:
        return f"Decreasing ({slope:.1f}/month)"

def analyze_seasonality(values, period=3):
    """Analyze seasonal patterns"""
    try:
        # Convert to pandas series for seasonal decomposition
        ts = pd.Series(values)
        
        if len(ts) < 2 * period:
            return 0.0
            
        # Simple seasonal strength calculation
        # Compare variance of seasonal vs. residual components
        seasonal_var = 0.0
        if len(values) >= period:
            # Calculate period-over-period differences
            seasonal_diffs = []
            for i in range(period, len(values)):
                seasonal_diffs.append(abs(values[i] - values[i-period]))
            
            if seasonal_diffs:
                overall_var = np.var(values)
                seasonal_var = 1 - (np.var(seasonal_diffs) / overall_var) if overall_var > 0 else 0
                
        return max(0, min(1, seasonal_var))
        
    except Exception:
        return 0.0

def analyze_monthly_patterns(dates, values):
    """Analyze patterns by month"""
    try:
        monthly_avg = {}
        for date, value in zip(dates, values):
            month = date.month
            if month not in monthly_avg:
                monthly_avg[month] = []
            monthly_avg[month].append(value)
        
        # Calculate average by month
        month_averages = {}
        for month, vals in monthly_avg.items():
            month_averages[month] = np.mean(vals)
        
        if len(month_averages) < 3:
            return "Insufficient data"
        
        # Find highest and lowest months
        max_month = max(month_averages.items(), key=lambda x: x[1])
        min_month = min(month_averages.items(), key=lambda x: x[1])
        
        month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        return f"Peak: {month_names[max_month[0]]}, Low: {month_names[min_month[0]]}"
        
    except Exception:
        return "Analysis failed"

if __name__ == "__main__":
    patterns = analyze_seasonal_patterns()