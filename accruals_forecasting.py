import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class AccrualsForecasting:
    def __init__(self, file_path='Input/Actual.xlsx'):
        """
        Initialize the accruals forecasting system
        """
        self.file_path = file_path
        self.df = None
        self.monthly_columns = []
        self.load_data()
    
    def load_data(self):
        """
        Load and prepare the actual spending data
        """
        try:
            self.df = pd.read_excel(self.file_path)
            
            # Identify monthly columns (datetime columns)
            self.monthly_columns = [col for col in self.df.columns if isinstance(col, datetime)]
            self.monthly_columns.sort()
            
            print(f"Loaded data with {len(self.df)} expense categories")
            print(f"Monthly data from {self.monthly_columns[0].strftime('%Y-%m')} to {self.monthly_columns[-1].strftime('%Y-%m')}")
            
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def get_actual_data_summary(self):
        """
        Get summary of actual spending data
        """
        summary = []
        
        for idx, row in self.df.iterrows():
            category = row['Row Labels']
            sap_code = row['SAP']
            gl_code = row['GLCode']
            
            # Get monthly actual values
            monthly_data = {}
            for month_col in self.monthly_columns:
                value = row[month_col]
                monthly_data[month_col.strftime('%Y-%m')] = value if pd.notna(value) else 0
            
            summary.append({
                'Category': category,
                'SAP_Code': sap_code,
                'GL_Code': gl_code,
                'Monthly_Data': monthly_data
            })
        
        return summary
    
    def simple_average_forecast(self, months_to_use=6):
        """
        Simple average forecasting method
        """
        forecasts = []
        
        for idx, row in self.df.iterrows():
            category = row['Row Labels']
            
            # Get recent actual values (excluding NaN)
            recent_values = []
            for month_col in self.monthly_columns[-months_to_use:]:
                value = row[month_col]
                if pd.notna(value) and value > 0:
                    recent_values.append(value)
            
            if recent_values:
                forecast = np.mean(recent_values)
            else:
                forecast = 0
            
            forecasts.append({
                'Category': category,
                'Method': 'Simple Average',
                'Months_Used': len(recent_values),
                'August_2025_Forecast': round(forecast, 2),
                'Historical_Values': recent_values[-3:] if len(recent_values) >= 3 else recent_values
            })
        
        return forecasts
    
    def weighted_average_forecast(self, months_to_use=6):
        """
        Weighted average forecasting method (more weight on recent months)
        """
        forecasts = []
        
        for idx, row in self.df.iterrows():
            category = row['Row Labels']
            
            # Get recent actual values (excluding NaN)
            recent_values = []
            for month_col in self.monthly_columns[-months_to_use:]:
                value = row[month_col]
                if pd.notna(value) and value > 0:
                    recent_values.append(value)
            
            if recent_values:
                # Create weights (more recent = higher weight)
                n = len(recent_values)
                weights = np.arange(1, n + 1)
                weights = weights / weights.sum()
                
                forecast = np.average(recent_values, weights=weights)
            else:
                forecast = 0
            
            forecasts.append({
                'Category': category,
                'Method': 'Weighted Average',
                'Months_Used': len(recent_values),
                'August_2025_Forecast': round(forecast, 2),
                'Historical_Values': recent_values[-3:] if len(recent_values) >= 3 else recent_values
            })
        
        return forecasts
    
    def trending_average_forecast(self, months_to_use=6):
        """
        Trending average forecasting method (linear trend extrapolation)
        """
        forecasts = []
        
        for idx, row in self.df.iterrows():
            category = row['Row Labels']
            
            # Get recent actual values with their positions
            recent_data = []
            positions = []
            
            for i, month_col in enumerate(self.monthly_columns[-months_to_use:]):
                value = row[month_col]
                if pd.notna(value) and value > 0:
                    recent_data.append(value)
                    positions.append(i)
            
            if len(recent_data) >= 2:
                # Calculate linear trend
                x = np.array(positions)
                y = np.array(recent_data)
                
                # Linear regression
                A = np.vstack([x, np.ones(len(x))]).T
                m, b = np.linalg.lstsq(A, y, rcond=None)[0]
                
                # Forecast for next period
                next_position = months_to_use
                forecast = m * next_position + b
                
                # Ensure forecast is not negative
                forecast = max(0, forecast)
            elif len(recent_data) == 1:
                forecast = recent_data[0]
            else:
                forecast = 0
            
            forecasts.append({
                'Category': category,
                'Method': 'Trending Average',
                'Months_Used': len(recent_data),
                'August_2025_Forecast': round(forecast, 2),
                'Historical_Values': recent_data[-3:] if len(recent_data) >= 3 else recent_data,
                'Trend_Direction': 'Increasing' if len(recent_data) >= 2 and m > 0 else 'Decreasing' if len(recent_data) >= 2 and m < 0 else 'Stable'
            })
        
        return forecasts
    
    def generate_comprehensive_forecast(self):
        """
        Generate forecasts using all three methods
        """
        print("Generating comprehensive accruals forecast...")
        print("=" * 60)
        
        # Get forecasts from all methods
        simple_forecasts = self.simple_average_forecast()
        weighted_forecasts = self.weighted_average_forecast()
        trending_forecasts = self.trending_average_forecast()
        
        # Combine results
        combined_results = []
        
        for i in range(len(simple_forecasts)):
            category = simple_forecasts[i]['Category']
            
            simple_amount = simple_forecasts[i]['August_2025_Forecast']
            weighted_amount = weighted_forecasts[i]['August_2025_Forecast']
            trending_amount = trending_forecasts[i]['August_2025_Forecast']
            
            # Calculate recommendation (average of the three methods)
            recommendation = (simple_amount + weighted_amount + trending_amount) / 3
            
            # Determine confidence level based on variance
            amounts = [simple_amount, weighted_amount, trending_amount]
            variance = np.var(amounts)
            
            if variance < 1000:
                confidence = "High"
            elif variance < 10000:
                confidence = "Medium"
            else:
                confidence = "Low"
            
            combined_results.append({
                'Category': category,
                'Simple_Average': simple_amount,
                'Weighted_Average': weighted_amount,
                'Trending_Average': trending_amount,
                'Recommended_Accrual': round(recommendation, 2),
                'Confidence_Level': confidence,
                'Variance': round(variance, 2),
                'Historical_Data': simple_forecasts[i]['Historical_Values']
            })
        
        return combined_results
    
    def export_to_excel(self, results, output_file='Output/Accruals_Forecast.xlsx'):
        """
        Export results to Excel workbook with multiple scenarios
        """
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            
            # Summary sheet with recommendations
            summary_df = pd.DataFrame(results)
            summary_df.to_excel(writer, sheet_name='Summary_Recommendations', index=False)
            
            # Simple Average details
            simple_details = []
            simple_forecasts = self.simple_average_forecast()
            for forecast in simple_forecasts:
                simple_details.append({
                    'Category': forecast['Category'],
                    'Method': forecast['Method'],
                    'Forecast_Amount': forecast['August_2025_Forecast'],
                    'Months_Used': forecast['Months_Used'],
                    'Historical_Values': str(forecast['Historical_Values'])
                })
            
            simple_df = pd.DataFrame(simple_details)
            simple_df.to_excel(writer, sheet_name='Simple_Average', index=False)
            
            # Weighted Average details
            weighted_details = []
            weighted_forecasts = self.weighted_average_forecast()
            for forecast in weighted_forecasts:
                weighted_details.append({
                    'Category': forecast['Category'],
                    'Method': forecast['Method'],
                    'Forecast_Amount': forecast['August_2025_Forecast'],
                    'Months_Used': forecast['Months_Used'],
                    'Historical_Values': str(forecast['Historical_Values'])
                })
            
            weighted_df = pd.DataFrame(weighted_details)
            weighted_df.to_excel(writer, sheet_name='Weighted_Average', index=False)
            
            # Trending Average details
            trending_details = []
            trending_forecasts = self.trending_average_forecast()
            for forecast in trending_forecasts:
                trending_details.append({
                    'Category': forecast['Category'],
                    'Method': forecast['Method'],
                    'Forecast_Amount': forecast['August_2025_Forecast'],
                    'Months_Used': forecast['Months_Used'],
                    'Trend_Direction': forecast['Trend_Direction'],
                    'Historical_Values': str(forecast['Historical_Values'])
                })
            
            trending_df = pd.DataFrame(trending_details)
            trending_df.to_excel(writer, sheet_name='Trending_Average', index=False)
            
            # Original data for reference
            original_summary = self.get_actual_data_summary()
            original_df = pd.DataFrame(original_summary)
            original_df.to_excel(writer, sheet_name='Original_Data', index=False)
        
        print(f"Excel report exported to: {output_file}")
    
    def print_summary_report(self, results):
        """
        Print a summary report to console
        """
        print("\n" + "="*80)
        print("ACCRUALS FORECAST SUMMARY - AUGUST 2025")
        print("="*80)
        
        total_simple = sum([r['Simple_Average'] for r in results])
        total_weighted = sum([r['Weighted_Average'] for r in results])
        total_trending = sum([r['Trending_Average'] for r in results])
        total_recommended = sum([r['Recommended_Accrual'] for r in results])
        
        print(f"\nTOTAL ACCRUALS BY METHOD:")
        print(f"Simple Average:     ${total_simple:,.2f}")
        print(f"Weighted Average:   ${total_weighted:,.2f}")
        print(f"Trending Average:   ${total_trending:,.2f}")
        print(f"RECOMMENDED TOTAL:  ${total_recommended:,.2f}")
        
        print(f"\nDETAILED BREAKDOWN BY CATEGORY:")
        print("-" * 80)
        
        for result in results:
            print(f"\nCategory: {result['Category']}")
            print(f"  Simple Average:     ${result['Simple_Average']:8,.2f}")
            print(f"  Weighted Average:   ${result['Weighted_Average']:8,.2f}")
            print(f"  Trending Average:   ${result['Trending_Average']:8,.2f}")
            print(f"  RECOMMENDED:        ${result['Recommended_Accrual']:8,.2f}")
            print(f"  Confidence Level:   {result['Confidence_Level']}")
            print(f"  Recent History:     {result['Historical_Data']}")

def main():
    """
    Main function to run the accruals forecasting system
    """
    # Initialize the forecasting system
    forecaster = AccrualsForecasting()
    
    # Generate comprehensive forecast
    results = forecaster.generate_comprehensive_forecast()
    
    # Print summary report
    forecaster.print_summary_report(results)
    
    # Export to Excel
    forecaster.export_to_excel(results)
    
    print(f"\n{'='*80}")
    print("ACCRUALS FORECASTING COMPLETED")
    print("Check the Output folder for the detailed Excel report.")
    print("="*80)

if __name__ == "__main__":
    main()
