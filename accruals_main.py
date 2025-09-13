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
from database_manager import DatabaseManager

class AccrualsSystem:
    def __init__(self, input_file='Input/Actual.xlsx', enable_database=True):
        self.input_file = input_file
        self.data = None
        self.monthly_columns = []
        self.results = []
        self.enable_database = enable_database
        
        # Initialize database manager if enabled
        if self.enable_database:
            self.db_manager = DatabaseManager()
            print("✓ Database manager initialized")
        else:
            self.db_manager = None
        
    def load_data(self):
        """Load and validate the input Excel file"""
        try:
            self.data = pd.read_excel(self.input_file)
            
            # Find datetime columns (monthly data)
            all_monthly_columns = [col for col in self.data.columns if isinstance(col, datetime)]
            all_monthly_columns.sort()
            
            # Only include columns that have actual data (not all NaN)
            self.monthly_columns = []
            for col in all_monthly_columns:
                if not self.data[col].isna().all():  # If column has at least some data
                    self.monthly_columns.append(col)
            
            # Determine the next month to forecast
            if self.monthly_columns:
                last_month = self.monthly_columns[-1]
                # Calculate next month
                if last_month.month == 12:
                    self.target_month = 1  # January of next year
                    self.target_year = last_month.year + 1
                else:
                    self.target_month = last_month.month + 1
                    self.target_year = last_month.year
                
                # Store target month name for display
                month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                              'July', 'August', 'September', 'October', 'November', 'December']
                self.target_month_name = month_names[self.target_month]
            else:
                self.target_month = 8  # Default fallback
                self.target_year = 2025
                self.target_month_name = 'August'
            
            print(f"✓ Loaded data: {len(self.data)} categories, {len(self.monthly_columns)} months with data")
            print(f"✓ Data range: {self.monthly_columns[0].strftime('%B %Y')} - {self.monthly_columns[-1].strftime('%B %Y')}")
            print(f"✓ Next month to forecast: {self.target_month_name} {self.target_year}")
            return True
            
        except FileNotFoundError:
            print(f"✗ Error: Could not find input file '{self.input_file}'")
            return False
        except Exception as e:
            print(f"✗ Error loading data: {str(e)}")
            return False
    
    def get_weeks_in_month(self, month):
        """Get number of weeks in a month (4 or 5 week pattern)"""
        # Jan=1, Feb=2, ..., Dec=12
        five_week_months = [1, 4, 7, 10]  # Jan, Apr, Jul, Oct
        return 5 if month in five_week_months else 4
    
    def normalize_to_weekly_rate(self, value, month):
        """Convert monthly value to weekly rate"""
        weeks_in_month = self.get_weeks_in_month(month)
        return value / weeks_in_month if value > 0 else 0
    
    def convert_weekly_to_monthly(self, weekly_rate, target_month):
        """Convert weekly rate to monthly value"""
        weeks_in_target_month = self.get_weeks_in_month(target_month)
        return weekly_rate * weeks_in_target_month
    
    def analyze_category(self, row):
        """Analyze a single expense category and generate forecasts with weekly normalization"""
        category = row['Row Labels']
        
        # Extract historical spending with weekly normalization
        historical_values = []
        historical_weekly_rates = []
        historical_months = []
        
        for i, month_col in enumerate(self.monthly_columns):  # Use all available months
            value = row[month_col]
            if pd.notna(value) and value > 0:
                month_num = month_col.month
                weekly_rate = self.normalize_to_weekly_rate(float(value), month_num)
                
                historical_values.append(float(value))
                historical_weekly_rates.append(weekly_rate)
                historical_months.append(month_num)
        
        if len(historical_values) == 0:
            return self._zero_forecast(row)
        
        # Use dynamic target month 
        target_month = self.target_month
        
        # Method 1: Simple Average (based on weekly rates)
        avg_weekly_rate = np.mean(historical_weekly_rates)
        simple_avg = self.convert_weekly_to_monthly(avg_weekly_rate, target_month)
        
        # Method 2: Weighted Average (recent months get higher weight)
        n = len(historical_weekly_rates)
        weights = np.arange(1, n + 1) / sum(range(1, n + 1))
        weighted_avg_weekly = np.average(historical_weekly_rates, weights=weights)
        weighted_avg = self.convert_weekly_to_monthly(weighted_avg_weekly, target_month)
        
        # Method 3: Trending Average (based on weekly rates)
        if len(historical_weekly_rates) >= 2:
            # Linear regression for trend on weekly rates
            x = np.arange(len(historical_weekly_rates))
            coeffs = np.polyfit(x, historical_weekly_rates, 1)
            trend_weekly_rate = coeffs[0] * len(historical_weekly_rates) + coeffs[1]
            trend_weekly_rate = max(0, trend_weekly_rate)  # No negative forecasts
            trend_forecast = self.convert_weekly_to_monthly(trend_weekly_rate, target_month)
        else:
            trend_forecast = simple_avg
        
        # Method 4: Seasonal Forecast (based on seasonal patterns)
        seasonal_forecast = self._calculate_seasonal_forecast(
            historical_values, historical_months, target_month, avg_weekly_rate
        )
        
        # Get adaptive weights if database is enabled
        if self.enable_database and self.db_manager:
            weights = self.db_manager.get_adaptive_weights(category)
            recommendation = (
                simple_avg * weights['simple_avg'] +
                weighted_avg * weights['weighted_avg'] +
                trend_forecast * weights['trending_avg'] +
                seasonal_forecast * weights['seasonal_forecast']
            )
            confidence_modifier = weights['confidence']
        else:
            # Final recommendation (equal weight average of four methods)
            recommendation = (simple_avg + weighted_avg + trend_forecast + seasonal_forecast) / 4
            confidence_modifier = 0.5
        
        return {
            'Category': category,
            'SAP_Code': row['SAP'],
            'GL_Code': row['GLCode'],
            'Historical_Months': len(historical_values),
            'Historical_Average': round(np.mean(historical_values), 2),
            'Historical_Total': round(sum(historical_values), 2),
            'Avg_Weekly_Rate': round(avg_weekly_rate, 2),
            'Simple_Average': round(simple_avg, 2),
            'Weighted_Average': round(weighted_avg, 2),
            'Trending_Average': round(trend_forecast, 2),
            'Seasonal_Forecast': round(seasonal_forecast, 2),
            'Recommended_Accrual': round(recommendation, 2),
            'Target_Month_Weeks': self.get_weeks_in_month(target_month),
            'Confidence': self._calculate_confidence(historical_values),
            'Recent_Values': [round(v, 2) for v in historical_values[-3:]],
            'Weekly_Adjustment': 'Applied (4/5 week normalization)'
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
            'Avg_Weekly_Rate': 0,
            'Simple_Average': 0,
            'Weighted_Average': 0,
            'Trending_Average': 0,
            'Seasonal_Forecast': 0,
            'Recommended_Accrual': 0,
            'Target_Month_Weeks': self.get_weeks_in_month(self.target_month),
            'Confidence': 'No Data',
            'Recent_Values': [],
            'Weekly_Adjustment': 'Not Applied (No Data)'
        }
    
    def _calculate_seasonal_forecast(self, historical_values, historical_months, target_month, fallback_weekly_rate):
        """Calculate seasonal forecast based on historical patterns"""
        try:
            if len(historical_values) < 4:  # Need sufficient data for seasonal analysis
                # Fallback to simple average approach
                return self.convert_weekly_to_monthly(fallback_weekly_rate, target_month)
            
            # Create monthly patterns from historical data
            monthly_patterns = {}
            for i, month in enumerate(historical_months):
                if month not in monthly_patterns:
                    monthly_patterns[month] = []
                monthly_patterns[month].append(historical_values[i])
            
            # Calculate average for each month
            monthly_averages = {}
            for month, values in monthly_patterns.items():
                monthly_averages[month] = np.mean(values)
            
            # Check if we have data for the target month
            if target_month in monthly_averages:
                # Direct seasonal forecast - use historical average for this month
                seasonal_value = monthly_averages[target_month]
                
                # Apply weekly adjustment to seasonal forecast
                target_weeks = self.get_weeks_in_month(target_month)
                seasonal_weekly_rate = seasonal_value / target_weeks
                return seasonal_weekly_rate * target_weeks
            
            # If no direct data for target month, interpolate from seasonal patterns
            if len(monthly_averages) >= 3:
                # Calculate seasonal index for each month
                overall_average = np.mean(list(monthly_averages.values()))
                seasonal_indices = {month: avg/overall_average for month, avg in monthly_averages.items()}
                
                # Estimate seasonal index for target month
                target_seasonal_index = self._estimate_seasonal_index(target_month, seasonal_indices)
                
                # Apply seasonal adjustment to overall average
                seasonal_forecast = overall_average * target_seasonal_index
                
                # Apply weekly adjustment
                target_weeks = self.get_weeks_in_month(target_month)
                return (seasonal_forecast / target_weeks) * target_weeks
            
            # Fallback if not enough seasonal data
            return self.convert_weekly_to_monthly(fallback_weekly_rate, target_month)
            
        except Exception as e:
            # Fallback on error
            return self.convert_weekly_to_monthly(fallback_weekly_rate, target_month)
    
    def _estimate_seasonal_index(self, target_month, seasonal_indices):
        """Estimate seasonal index for target month based on available patterns"""
        try:
            # If we have adjacent months, interpolate
            available_months = sorted(seasonal_indices.keys())
            
            if not available_months:
                return 1.0
            
            # Find closest months
            closest_month = min(available_months, key=lambda x: abs(x - target_month))
            return seasonal_indices[closest_month]
            
        except Exception:
            return 1.0  # Neutral seasonal effect
    
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
        
        print("Generating weekly-adjusted forecasts...")
        print("Weekly pattern: Jan/Apr/Jul/Oct = 5 weeks, Others = 4 weeks")
        self.results = []
        
        for idx, row in self.data.iterrows():
            forecast = self.analyze_category(row)
            self.results.append(forecast)
        
        # Store in database if enabled
        if self.enable_database and self.db_manager:
            self.store_forecast_in_database()
        
        return True
    
    def store_forecast_in_database(self, version_name=None):
        """Store forecast results in database with version control"""
        if not self.db_manager:
            return None
            
        # Generate version name if not provided
        if version_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            version_name = f"Auto_Forecast_{timestamp}"
        
        # Create forecast version
        version_id = self.db_manager.create_forecast_version(
            version_name=version_name,
            target_month=self.target_month,
            target_year=self.target_year,
            data_file_path=os.path.abspath(self.input_file),
            weekly_adjustment=True,  # Our system uses weekly adjustment
            auto_fit=True,
            parameters={
                "monthly_columns_count": len(self.monthly_columns),
                "data_range_start": self.monthly_columns[0].strftime('%Y-%m-%d') if self.monthly_columns else None,
                "data_range_end": self.monthly_columns[-1].strftime('%Y-%m-%d') if self.monthly_columns else None,
                "forecast_methods": ["Simple_Average", "Weighted_Average", "Trending_Average", "Seasonal_Forecast"]
            },
            notes=f"Automatic forecast for {self.target_month_name} {self.target_year}"
        )
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(self.results)
        
        # Store forecasts
        self.db_manager.store_forecasts(version_id, results_df)
        
        print(f"✓ Forecast stored in database (Version ID: {version_id})")
        return version_id
    
    def store_actuals_in_database(self, actuals_data, invoice_month, invoice_year, data_source=None):
        """Store actual invoice data in database
        
        Args:
            actuals_data: Dictionary or Series with category -> amount mapping
            invoice_month: Month of the invoices (1-12)
            invoice_year: Year of the invoices
            data_source: Source file or description
        """
        if not self.db_manager:
            print("Database not enabled - cannot store actuals")
            return
            
        # Convert to pandas Series if it's a dict
        if isinstance(actuals_data, dict):
            actuals_series = pd.Series(actuals_data)
        else:
            actuals_series = actuals_data
            
        self.db_manager.store_actuals(
            actuals_series, 
            invoice_month, 
            invoice_year, 
            data_source or "Manual entry"
        )
        
        print(f"✓ Actual data stored for {invoice_month}/{invoice_year}")
        
        # Auto-calculate accuracy for recent forecasts
        self.calculate_forecast_accuracy(invoice_month, invoice_year)
    
    def calculate_forecast_accuracy(self, actual_month, actual_year):
        """Calculate accuracy for forecasts matching the actual month/year"""
        if not self.db_manager:
            return
            
        # Find forecast versions for this target month/year
        versions_df = self.db_manager.get_forecast_versions(actual_month, actual_year)
        
        for _, version in versions_df.iterrows():
            version_id = version['version_id']
            print(f"Calculating accuracy for version {version_id}: {version['version_name']}")
            
            self.db_manager.calculate_accuracy_metrics(version_id, actual_month, actual_year)
        
        # Update adaptive weights based on new accuracy data
        self.db_manager.update_adaptive_weights()
        print("✓ Adaptive weights updated based on latest accuracy data")
    
    def get_adaptive_forecast(self, category_data):
        """Generate forecast using adaptive weights based on historical accuracy"""
        if not self.db_manager:
            # Fallback to equal weights
            return {
                'simple_avg': 0.25,
                'weighted_avg': 0.25,
                'trending_avg': 0.25,
                'seasonal_forecast': 0.25,
                'confidence': 0.5
            }
            
        category = category_data.get('Category', 'Unknown')
        return self.db_manager.get_adaptive_weights(category)
    
    def export_html_report(self, output_file=None):
        """Export results to a beautiful HTML report"""
        os.makedirs('Output', exist_ok=True)
        
        # Generate unique filename if not specified
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'Output/Accruals_Forecast_Report_{timestamp}.html'
        
        df = pd.DataFrame(self.results)
        
        # Calculate totals
        totals = {
            'Simple_Average_Total': df['Simple_Average'].sum(),
            'Weighted_Average_Total': df['Weighted_Average'].sum(),
            'Trending_Average_Total': df['Trending_Average'].sum(),
            'Recommended_Total': df['Recommended_Accrual'].sum()
        }
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accruals Forecast Report - {datetime.now().strftime('%B %Y')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        .metric-card.recommended {{
            background: linear-gradient(135deg, #FF6B6B, #FF8E8E);
            color: white;
        }}
        .metric-title {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .metric-card.recommended .metric-title {{
            color: rgba(255,255,255,0.9);
        }}
        .metric-value {{
            font-size: 2.2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .metric-card.recommended .metric-value {{
            color: white;
        }}
        .section {{
            padding: 30px;
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
            margin-bottom: 25px;
            font-size: 1.8em;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .info-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }}
        .info-card h3 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
        }}
        .table-container {{
            overflow-x: auto;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #4CAF50;
            color: white;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .currency {{
            text-align: right;
            font-weight: 600;
            color: #2c3e50;
        }}
        .confidence-high {{ background: #d4edda; color: #155724; padding: 4px 8px; border-radius: 4px; }}
        .confidence-medium {{ background: #fff3cd; color: #856404; padding: 4px 8px; border-radius: 4px; }}
        .confidence-low {{ background: #f8d7da; color: #721c24; padding: 4px 8px; border-radius: 4px; }}
        .footer {{
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .methodology {{
            background: #e8f4fd;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .chart-placeholder {{
            background: #f8f9fa;
            border: 2px dashed #ccc;
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            color: #666;
            margin: 20px 0;
        }}
        @media (max-width: 768px) {{
            .metrics {{
                grid-template-columns: 1fr;
            }}
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            .header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Accruals Forecast Report</h1>
            <p>Weekly-Adjusted Predictions for {datetime.now().strftime('%B %Y')}</p>
            <p>Generated on {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-title">Simple Average</div>
                <div class="metric-value">${totals['Simple_Average_Total']:,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Weighted Average</div>
                <div class="metric-value">${totals['Weighted_Average_Total']:,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Trending Average</div>
                <div class="metric-value">${totals['Trending_Average_Total']:,.2f}</div>
            </div>
            <div class="metric-card recommended">
                <div class="metric-title">RECOMMENDED ACCRUAL</div>
                <div class="metric-value">${totals['Recommended_Total']:,.2f}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Forecasting Summary</h2>
            <div class="info-grid">
                <div class="info-card">
                    <h3>🎯 Methodology</h3>
                    <p>Three forecasting methods with weekly adjustment algorithm for improved accuracy.</p>
                    <p><strong>Weekly Pattern:</strong> Jan/Apr/Jul/Oct = 5 weeks, Others = 4 weeks</p>
                </div>
                <div class="info-card">
                    <h3>📊 Analysis Period</h3>
                    <p><strong>Historical Data:</strong> {len(self.monthly_columns)} months ({self.monthly_columns[0].strftime('%B %Y')} - {self.monthly_columns[-1].strftime('%B %Y')})</p>
                    <p><strong>Forecast Target:</strong> {self.target_month_name} {self.target_year} ({self.get_weeks_in_month(self.target_month)} weeks)</p>
                    <p><strong>Categories Analyzed:</strong> {len(df)} expense categories</p>
                </div>
                <div class="info-card">
                    <h3>🔍 Data Quality</h3>
                    <p><strong>High Confidence:</strong> {len(df[df['Confidence'] == 'High'])} categories</p>
                    <p><strong>Medium Confidence:</strong> {len(df[df['Confidence'] == 'Medium'])} categories</p>
                    <p><strong>Low Confidence:</strong> {len(df[df['Confidence'] == 'Low'])} categories</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Detailed Category Breakdown</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Weekly Rate</th>
                            <th>Simple Average</th>
                            <th>Weighted Average</th>
                            <th>Trending Average</th>
                            <th>Recommended</th>
                            <th>Confidence</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # Add table rows
        for _, row in df.iterrows():
            confidence_class = f"confidence-{row['Confidence'].lower().replace(' ', '-')}"
            html_content += f"""
                        <tr>
                            <td><strong>{row['Category']}</strong></td>
                            <td class="currency">${row.get('Avg_Weekly_Rate', 0):,.2f}/week</td>
                            <td class="currency">${row['Simple_Average']:,.2f}</td>
                            <td class="currency">${row['Weighted_Average']:,.2f}</td>
                            <td class="currency">${row['Trending_Average']:,.2f}</td>
                            <td class="currency"><strong>${row['Recommended_Accrual']:,.2f}</strong></td>
                            <td><span class="{confidence_class}">{row['Confidence']}</span></td>
                        </tr>
"""
        
        html_content += f"""
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="section">
            <h2>🔬 Methodology Explanation</h2>
            <div class="methodology">
                <h3>Weekly Adjustment Algorithm</h3>
                <p>To improve forecast accuracy, the system normalizes historical spending to weekly rates before applying forecasting methods:</p>
                <ol>
                    <li><strong>Normalization:</strong> Monthly values ÷ Number of weeks = Weekly rate</li>
                    <li><strong>Forecasting:</strong> Apply statistical methods to weekly rates</li>
                    <li><strong>Conversion:</strong> Weekly rate × Target month weeks = Final forecast</li>
                </ol>
                <p><strong>5-Week Months:</strong> January, April, July, October<br>
                <strong>4-Week Months:</strong> February, March, May, June, August, September, November, December</p>
            </div>
            
            <div class="info-grid">
                <div class="info-card">
                    <h3>Simple Average Method</h3>
                    <p>Calculates the arithmetic mean of normalized weekly rates. Best for stable, consistent spending patterns.</p>
                </div>
                <div class="info-card">
                    <h3>Weighted Average Method</h3>
                    <p>Gives more weight to recent months when calculating weekly rates. Better for capturing recent trends.</p>
                </div>
                <div class="info-card">
                    <h3>Trending Average Method</h3>
                    <p>Uses linear regression on weekly rates to project future trends. Accounts for increasing or decreasing patterns.</p>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by Accruals Forecasting System v2.0 | Weekly-Adjusted Algorithm</p>
            <p>📧 For questions or support, contact your Finance Team</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Write HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ HTML report exported to: {output_file}")
        return output_file
    
    def export_results(self, output_file=None):
        """Export results to Excel with enhanced formatting and auto-fit columns"""
        os.makedirs('Output', exist_ok=True)
        
        # Generate unique filename if not specified
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'Output/Accruals_Forecast_{timestamp}.xlsx'
        else:
            # Ensure the file goes to the Output directory
            if not output_file.startswith('Output/'):
                output_file = f'Output/{output_file}'
        
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
            currency_cols = ['Simple_Average', 'Weighted_Average', 'Trending_Average', 'Recommended_Accrual', 'Historical_Average', 'Historical_Total', 'Avg_Weekly_Rate']
            
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
                method_df = df[['Category', 'SAP_Code', 'GL_Code', method_col, 'Confidence', 'Historical_Months', 'Target_Month_Weeks', 'Weekly_Adjustment']].copy()
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
        print(f"ACCRUALS FORECAST SUMMARY - {self.target_month_name.upper()} {self.target_year} (WEEKLY-ADJUSTED)")
        print("="*80)
        print(f"Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Categories analyzed: {len(self.results)}")
        print(f"Weekly adjustment: Jan/Apr/Jul/Oct = 5 weeks, Others = 4 weeks")
        print(f"Target month ({self.target_month_name}): {self.get_weeks_in_month(self.target_month)} weeks")
        
        print(f"\nFORECAST TOTALS:")
        print(f"Simple Average:    ${df['Simple_Average'].sum():>12,.2f}")
        print(f"Weighted Average:  ${df['Weighted_Average'].sum():>12,.2f}")
        print(f"Trending Average:  ${df['Trending_Average'].sum():>12,.2f}")
        print(f"RECOMMENDED:       ${df['Recommended_Accrual'].sum():>12,.2f}")
        
        print(f"\nCATEGORY BREAKDOWN (Weekly-Adjusted):")
        print("-" * 80)
        for result in self.results:
            if result['Recommended_Accrual'] > 0:
                avg_weekly = result.get('Avg_Weekly_Rate', 0)
                print(f"{result['Category']:<40} ${result['Recommended_Accrual']:>10,.2f} ({result['Confidence']}) [${avg_weekly:.2f}/week]")
        
        print("="*80)

def main():
    """Main execution function"""
    print("Starting Accruals Forecasting System...")
    print("="*50)
    
    # Initialize system
    system = AccrualsSystem()
    
    # Generate forecasts
    if system.generate_forecasts():
        # Export Excel results
        excel_file = system.export_results()
        
        # Export HTML results
        html_file = system.export_html_report()
        
        # Print summary
        system.print_summary()
        
        print(f"\n✓ Process completed successfully!")
        print(f"📊 Excel report: {excel_file}")
        print(f"🌐 HTML report: {html_file}")
        print(f"💡 Share the HTML file with colleagues - opens in any browser!")
        
    else:
        print("✗ Forecasting failed. Please check your input file.")

if __name__ == "__main__":
    main()
