"""
Demo Script - Complete Workflow with Database and Accuracy Tracking
==================================================================

This script demonstrates the complete workflow:
1. Generate forecasts (stored in database)
2. Add actual invoice data
3. View accuracy metrics
4. See adaptive learning in action
"""

from accruals_main import AccrualsSystem
from database_manager import DatabaseManager
import pandas as pd

def demo_complete_workflow():
    """Demonstrate the complete forecasting and accuracy tracking workflow"""
    print("="*70)
    print("ACCRUALS FORECASTING SYSTEM - COMPLETE WORKFLOW DEMO")
    print("="*70)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    print("\n1. 📊 CURRENT DATABASE STATUS")
    print("-" * 40)
    versions = db_manager.get_forecast_versions()
    accuracy = db_manager.get_accuracy_summary()
    print(f"Forecast Versions: {len(versions)}")
    print(f"Accuracy Records: {len(accuracy)}")
    
    if len(versions) > 0:
        print("\nRecent Forecast Versions:")
        for _, version in versions.head(3).iterrows():
            print(f"  - {version['version_name']} ({version['target_month']:02d}/{version['target_year']})")
    
    print("\n2. 🎯 FORECAST ACCURACY SUMMARY")
    print("-" * 40)
    if len(accuracy) > 0:
        print("Method Performance Averages:")
        methods = ['simple_avg_accuracy', 'weighted_avg_accuracy', 
                  'trending_avg_accuracy', 'seasonal_forecast_accuracy']
        
        for method in methods:
            if method in accuracy.columns:
                avg_accuracy = accuracy[method].mean()
                method_name = method.replace('_accuracy', '').replace('_', ' ').title()
                print(f"  - {method_name}: {avg_accuracy:.1%}")
        
        print("\nCategory Performance:")
        for _, row in accuracy.iterrows():
            print(f"  - {row['category']}: {row['recommended_accuracy']:.1%}")
    else:
        print("No accuracy data available yet.")
    
    print("\n3. 🤖 ADAPTIVE WEIGHTS STATUS")
    print("-" * 40)
    
    # Check adaptive weights for each category
    categories = ['Consumables - Variable', 'Handling - Variable', 'Storage - Fixed']
    
    for category in categories:
        weights = db_manager.get_adaptive_weights(category)
        print(f"\n{category}:")
        print(f"  Simple: {weights['simple_avg']:.3f}, Weighted: {weights['weighted_avg']:.3f}")
        print(f"  Trending: {weights['trending_avg']:.3f}, Seasonal: {weights['seasonal_forecast']:.3f}")
        print(f"  Confidence: {weights['confidence']:.3f}")
    
    print("\n4. 📈 NEXT STEPS RECOMMENDATIONS")
    print("-" * 40)
    
    if len(versions) == 0:
        print("• Generate your first forecast using the web interface or command line")
    elif len(accuracy) == 0:
        print("• Add actual invoice data to start accuracy tracking")
        print("• Use the web interface Database Management page")
    else:
        print("• ✅ System is fully operational with accuracy tracking")
        print("• Continue adding monthly actual data as invoices arrive")
        print("• Monitor accuracy trends in the web dashboard")
        print("• System will automatically improve forecasting weights")
    
    print("\n5. 🌐 WEB INTERFACE ACCESS")
    print("-" * 40)
    print("Launch the web interface with:")
    print("  python -m streamlit run app.py")
    print("\nThen navigate to:")
    print("  📈 Forecast Accuracy Dashboard - View performance metrics")
    print("  💾 Database Management - Add actual invoice data")
    print("  📊 Version History - Compare forecast versions")
    
    print("\n" + "="*70)
    print("DEMO COMPLETED")
    print("="*70)

def show_sample_accuracy_details():
    """Show detailed accuracy breakdown"""
    print("\n" + "="*50)
    print("DETAILED ACCURACY ANALYSIS")
    print("="*50)
    
    db_manager = DatabaseManager()
    
    # Get detailed accuracy metrics
    import sqlite3
    with sqlite3.connect(db_manager.db_path) as conn:
        detailed_metrics = pd.read_sql_query("""
            SELECT 
                am.category,
                am.actual_amount,
                f.simple_average,
                f.weighted_average,
                f.trending_average,
                f.seasonal_forecast,
                f.recommended_accrual,
                am.simple_avg_accuracy,
                am.seasonal_forecast_accuracy,
                am.recommended_accuracy
            FROM accuracy_metrics am
            JOIN forecasts f ON am.version_id = f.version_id AND am.category = f.category
            WHERE am.version_id = (SELECT MAX(version_id) FROM accuracy_metrics)
            ORDER BY am.category
        """, conn)
    
    if len(detailed_metrics) > 0:
        print("\nLatest Forecast vs Actual Comparison:")
        print("-" * 80)
        
        for _, row in detailed_metrics.iterrows():
            print(f"\n{row['category']}:")
            print(f"  Actual:      ${row['actual_amount']:>10,.2f}")
            print(f"  Simple Avg:  ${row['simple_average']:>10,.2f} ({row['simple_avg_accuracy']:.1%})")
            print(f"  Seasonal:    ${row['seasonal_forecast']:>10,.2f} ({row['seasonal_forecast_accuracy']:.1%})")
            print(f"  Recommended: ${row['recommended_accrual']:>10,.2f} ({row['recommended_accuracy']:.1%})")
        
        # Summary statistics
        total_actual = detailed_metrics['actual_amount'].sum()
        total_recommended = detailed_metrics['recommended_accrual'].sum()
        overall_accuracy = 1 - abs(total_actual - total_recommended) / max(total_actual, total_recommended)
        
        print(f"\nOVERALL SUMMARY:")
        print(f"Total Actual:      ${total_actual:>12,.2f}")
        print(f"Total Recommended: ${total_recommended:>12,.2f}")
        print(f"Overall Accuracy:  {overall_accuracy:>13.1%}")
    else:
        print("No detailed accuracy data available.")

if __name__ == "__main__":
    # Run the demo
    demo_complete_workflow()
    
    # Show detailed analysis
    show_sample_accuracy_details()