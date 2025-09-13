"""
Test script for database functionality
=====================================

This script demonstrates the database features including:
- Storing forecast results
- Adding actual data
- Calculating accuracy metrics
- Viewing adaptive weights
"""

from accruals_main import AccrualsSystem
from database_manager import DatabaseManager
import pandas as pd
from datetime import datetime

def test_database_functionality():
    """Test the complete database workflow"""
    print("="*60)
    print("TESTING DATABASE FUNCTIONALITY")
    print("="*60)
    
    # Initialize system with database enabled
    print("\n1. Initializing system with database...")
    system = AccrualsSystem(enable_database=True)
    
    # Generate forecasts (this will auto-store in database)
    print("\n2. Generating forecasts...")
    if system.generate_forecasts():
        print("✓ Forecasts generated and stored in database")
        
        # Get the latest version ID
        versions_df = system.db_manager.get_forecast_versions()
        if len(versions_df) > 0:
            latest_version = versions_df.iloc[0]
            print(f"✓ Latest version: {latest_version['version_name']} (ID: {latest_version['version_id']})")
            
            # Simulate adding actual data for the forecast month
            print("\n3. Adding sample actual data...")
            
            # Example actual data (you would replace this with real invoice data)
            sample_actuals = {
                'Training & Development': 85000.00,
                'IT Services': 120000.00,
                'Office Supplies': 8500.00,
                'Professional Services': 95000.00,
                'Maintenance': 45000.00
            }
            
            # Store actuals for the target month
            system.store_actuals_in_database(
                sample_actuals, 
                system.target_month, 
                system.target_year,
                "Test data for accuracy calculation"
            )
            
            print(f"✓ Stored actual data for {system.target_month}/{system.target_year}")
            
            # Get accuracy summary
            print("\n4. Calculating accuracy metrics...")
            accuracy_df = system.db_manager.get_accuracy_summary()
            
            if len(accuracy_df) > 0:
                print("✓ Accuracy metrics calculated:")
                print(accuracy_df[['category', 'simple_avg_accuracy', 'weighted_avg_accuracy', 
                                'trending_avg_accuracy', 'seasonal_forecast_accuracy']].head())
            
            # Show adaptive weights
            print("\n5. Checking adaptive weights...")
            for category in ['Training & Development', 'IT Services']:
                weights = system.db_manager.get_adaptive_weights(category)
                print(f"   {category}:")
                print(f"     Simple: {weights['simple_avg']:.2f}, Weighted: {weights['weighted_avg']:.2f}")
                print(f"     Trending: {weights['trending_avg']:.2f}, Seasonal: {weights['seasonal_forecast']:.2f}")
                print(f"     Confidence: {weights['confidence']:.2f}")
            
        else:
            print("✗ No forecast versions found in database")
    else:
        print("✗ Failed to generate forecasts")
    
    print("\n" + "="*60)
    print("DATABASE TEST COMPLETED")
    print("="*60)

def show_database_summary():
    """Show summary of database contents"""
    print("\n" + "="*40)
    print("DATABASE SUMMARY")
    print("="*40)
    
    db_manager = DatabaseManager()
    
    # Show forecast versions
    versions_df = db_manager.get_forecast_versions()
    print(f"Forecast Versions: {len(versions_df)}")
    
    if len(versions_df) > 0:
        print("Recent versions:")
        for _, version in versions_df.head(3).iterrows():
            print(f"  - {version['version_name']} ({version['target_month']}/{version['target_year']})")
    
    # Show accuracy summary
    accuracy_df = db_manager.get_accuracy_summary()
    print(f"\nAccuracy Records: {len(accuracy_df)}")
    
    if len(accuracy_df) > 0:
        avg_accuracy = accuracy_df['recommended_accuracy'].mean()
        print(f"Average Recommended Accuracy: {avg_accuracy:.1%}")
    
    print("="*40)

if __name__ == "__main__":
    # Run the database test
    test_database_functionality()
    
    # Show summary
    show_database_summary()
    
    print("\n💡 To view the web interface with database features:")
    print("   python -m streamlit run app.py")
    print("\n📊 Database file created: accruals_forecasts.db")
    print("   You can open this with any SQLite browser to explore the data")