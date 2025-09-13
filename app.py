"""
Web UI for Accruals Forecasting System
=======================================

This creates a simple web interface for the accruals forecasting system.
Users can upload their Excel file and get forecasts through a web browser.

Requirements: pip install streamlit plotly
Usage: streamlit run web_interface.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import base64
import sqlite3
import os

# Import our main forecasting system
from accruals_main import AccrualsSystem
from database_manager import DatabaseManager

def create_download_link(df, filename, text):
    """Create a download link for Excel file"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Forecast_Results', index=False)
    
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">{text}</a>'
    return href

def main():
    st.set_page_config(
        page_title="Accruals Forecasting System",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Accruals Forecasting System")
    st.markdown("### Predict future accruals based on historical spending patterns")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Sidebar for navigation and configuration
    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["🎯 Generate Forecast", "📈 Accuracy Dashboard", "💾 Database Management", "📊 Version History"]
    )
    
    if page == "🎯 Generate Forecast":
        generate_forecast_page(db_manager)
    elif page == "📈 Accuracy Dashboard":
        accuracy_dashboard_page(db_manager)
    elif page == "💾 Database Management":
        database_management_page(db_manager)
    elif page == "📊 Version History":
        version_history_page(db_manager)

def generate_forecast_page(db_manager):
    """Main forecasting page"""
    st.header("🎯 Generate New Forecast")
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # Option to use default file or upload new one
    use_default = st.sidebar.checkbox(
        "Use default file (Input/Actual.xlsx)", 
        value=True,
        help="Check this to use the default Input/Actual.xlsx file"
    )
    
    uploaded_file = None
    if not use_default:
        # File upload
        uploaded_file = st.sidebar.file_uploader(
            "Upload your Excel file",
            type=['xlsx', 'xls'],
            help="Upload your actual spending Excel file"
        )
    
    # Forecast version name
    version_name = st.sidebar.text_input(
        "Forecast Version Name (optional)",
        placeholder="Auto-generated if empty"
    )
    
    # Submit button
    submit_forecast = st.sidebar.button(
        "🚀 Generate Forecast",
        type="primary",
        help="Click to generate forecast with current settings"
    )
    
    # Process forecast when button is clicked
    if submit_forecast:
        try:
            # Determine which file to use
            if use_default:
                # Use default file path
                input_file = "Input/Actual.xlsx"
                
                # Check if default file exists
                if not os.path.exists(input_file):
                    st.error(f"❌ Default file not found: {input_file}")
                    st.info("Please ensure the file exists or upload a new file.")
                    return
                    
                st.info(f"📁 Using default file: {input_file}")
                
            elif uploaded_file is not None:
                # Save uploaded file temporarily
                input_file = "temp_upload.xlsx"
                with open(input_file, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.info(f"📁 Using uploaded file: {uploaded_file.name}")
                
            else:
                st.warning("⚠️ Please either check 'Use default file' or upload an Excel file.")
                return
            
            # Initialize forecasting system
            system = AccrualsSystem(input_file=input_file, enable_database=True)
            
            if system.generate_forecasts():
                # Store with custom version name if provided
                if version_name.strip():
                    system.store_forecast_in_database(version_name.strip())
                
                results_df = pd.DataFrame(system.results)
                
                # Dynamic title with forecast month
                st.header(f"🎯 {system.target_month_name} {system.target_year} Forecast Results")
                st.markdown(f"**Weekly-Adjusted Forecast • {system.get_weeks_in_month(system.target_month)} weeks • Based on {len(system.monthly_columns)} months of historical data**")
                
                # Display data range
                st.info(f"📊 Historical Data: {system.monthly_columns[0].strftime('%B %Y')} - {system.monthly_columns[-1].strftime('%B %Y')}")
                
                # Main dashboard
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric(
                        "Simple Average",
                        f"${results_df['Simple_Average'].sum():,.2f}"
                    )
                
                with col2:
                    st.metric(
                        "Weighted Average", 
                        f"${results_df['Weighted_Average'].sum():,.2f}"
                    )
                
                with col3:
                    st.metric(
                        "Trending Average",
                        f"${results_df['Trending_Average'].sum():,.2f}"
                    )
                
                with col4:
                    st.metric(
                        "Seasonal Forecast",
                        f"${results_df['Seasonal_Forecast'].sum():,.2f}",
                        help="Forecast based on seasonal patterns and trends"
                    )
                
                with col5:
                    st.metric(
                        "RECOMMENDED",
                        f"${results_df['Recommended_Accrual'].sum():,.2f}",
                        help="Average of all four forecasting methods"
                    )
                
                # Charts section
                st.header("📈 Forecast Comparison")
                
                # Bar chart comparing methods
                methods_data = {
                    'Method': ['Simple Average', 'Weighted Average', 'Trending Average', 'Seasonal Forecast', 'Recommended'],
                    'Amount': [
                        results_df['Simple_Average'].sum(),
                        results_df['Weighted_Average'].sum(), 
                        results_df['Trending_Average'].sum(),
                        results_df['Seasonal_Forecast'].sum(),
                        results_df['Recommended_Accrual'].sum()
                    ]
                }
                
                fig_bar = px.bar(
                    methods_data,
                    x='Method',
                    y='Amount',
                    title=f'{system.target_month_name} {system.target_year} Forecast Comparison by Method',
                    color='Method'
                )
                fig_bar.update_layout(yaxis_tickformat='$,.0f')
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Category breakdown
                st.header(f"📋 {system.target_month_name} {system.target_year} Category Breakdown")
                
                # Filter out zero values for cleaner display
                non_zero_results = results_df[results_df['Recommended_Accrual'] > 0]
                
                if len(non_zero_results) > 0:
                    fig_pie = px.pie(
                        non_zero_results,
                        values='Recommended_Accrual',
                        names='Category',
                        title=f'{system.target_month_name} {system.target_year} - Recommended Accruals by Category'
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                # Detailed results table
                st.header(f"📊 {system.target_month_name} {system.target_year} - Detailed Results")
                
                # Display options
                show_columns = st.multiselect(
                    "Select columns to display:",
                    options=results_df.columns.tolist(),
                    default=['Category', 'Simple_Average', 'Weighted_Average', 'Trending_Average', 'Seasonal_Forecast', 'Recommended_Accrual', 'Confidence']
                )
                
                if show_columns:
                    st.dataframe(
                        results_df[show_columns].style.format({
                            col: "${:,.2f}" for col in show_columns 
                            if col in ['Simple_Average', 'Weighted_Average', 'Trending_Average', 'Seasonal_Forecast', 'Recommended_Accrual']
                        }),
                        use_container_width=True
                    )
                
                # Export section
                st.header("💾 Export Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📊 Generate Excel Report"):
                        output_file = system.export_results("forecast_results.xlsx")
                        st.success(f"Excel report generated: {output_file}")
                
                with col2:
                    if st.button("🌐 Generate HTML Report"):
                        html_file = system.export_html_report()
                        st.success(f"HTML report generated: {html_file}")
                        st.info("💡 Share this HTML file with colleagues - they can open it in any web browser!")
                
                with col3:
                    # Download link for CSV
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name=f"accruals_forecast_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                
                # Methodology explanation
                with st.expander("📚 Forecasting Methodology"):
                    st.markdown("""
                    ### Forecasting Methods Used:
                    
                    **1. Simple Average**
                    - Calculates the arithmetic mean of all available historical data
                    - Best for stable, consistent spending patterns
                    
                    **2. Weighted Average** 
                    - Gives more weight to recent months
                    - Better for capturing recent trends and changes
                    
                    **3. Trending Average**
                    - Uses linear regression to extrapolate trends
                    - Accounts for increasing or decreasing spending patterns
                    
                    **Final Recommendation**
                    - Average of all three methods
                    - Provides balanced forecast considering all approaches
                    
                    **Confidence Levels:**
                    - **High**: Low variance in historical data (CV < 0.2)
                    - **Medium**: Moderate variance (CV 0.2-0.5)
                    - **Low**: High variance or insufficient data (CV > 0.5)
                    """)
                
            else:
                st.error("Failed to process the file. Please check the file format.")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    else:
        # Welcome screen
        st.info("👆 Configure your settings and click 'Generate Forecast' to get started")
        
        st.markdown("""
        ### How to use this system:
        
        1. **Configure** your settings in the sidebar:
           - ✅ Use default file (Input/Actual.xlsx) or upload new file
           - 📝 Optional: Enter a custom forecast version name
        2. **Click** the "🚀 Generate Forecast" button
        3. **Review** the forecast results across four different methods
        4. **Analyze** the recommended accruals for the next month
        5. **Export** results to Excel or CSV for further analysis
        
        ### Default File:
        - **Input/Actual.xlsx** - Place your Excel file here to use default option
        
        ### File Requirements:
        - Excel file (.xlsx or .xls)
        - Columns: SAP, GLCode, Row Labels, and monthly data columns
        - Historical spending data for accurate forecasting
        
        ### Quick Start:
        1. Place your Excel file at **Input/Actual.xlsx**
        2. Keep "Use default file" checked
        3. Click "🚀 Generate Forecast"
        """)

def accuracy_dashboard_page(db_manager):
    """Dashboard showing forecast accuracy metrics"""
    st.header("📈 Forecast Accuracy Dashboard")
    
    # Check what data we have
    forecast_versions = db_manager.get_forecast_versions()
    accuracy_df = db_manager.get_accuracy_summary()
    
    # Show current database status
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Forecast Versions", len(forecast_versions))
    with col2:
        st.metric("📥 Accuracy Records", len(accuracy_df))
    with col3:
        if len(forecast_versions) > 0 and len(accuracy_df) == 0:
            st.metric("⚠️ Status", "Need Actual Data", help="Add actual invoice data to calculate accuracy")
        elif len(accuracy_df) > 0:
            st.metric("✅ Status", "Tracking Active")
        else:
            st.metric("📋 Status", "No Data Yet")
    
    if len(accuracy_df) == 0:
        if len(forecast_versions) > 0:
            st.warning("🎯 **Forecasts found but no accuracy data yet!**")
            st.info("""
            **You have forecast data but haven't added actual invoice amounts yet.**
            
            To see accuracy metrics:
            1. Go to **💾 Database Management** page
            2. Use the **📥 Enter Actuals** tab
            3. Add actual invoice data for any month you have forecasts for
            4. Return here to see accuracy comparisons
            
            **Why accuracy tracking matters:**
            - See which forecasting methods work best for your data
            - System learns and improves over time
            - Build confidence in forecast reliability
            """)
            
            # Show available forecast versions
            st.subheader("📊 Available Forecast Versions")
            display_versions = forecast_versions.copy()
            display_versions['created_date'] = pd.to_datetime(display_versions['created_date']).dt.strftime('%Y-%m-%d %H:%M')
            display_versions['target_period'] = display_versions.apply(lambda row: f"{row['target_month']:02d}/{row['target_year']}", axis=1)
            
            st.dataframe(
                display_versions[['version_name', 'target_period', 'created_date', 'notes']],
                use_container_width=True
            )
        else:
            st.info("""
            **No forecast data found.**
            
            To get started:
            1. Go to **🎯 Generate Forecast** page
            2. Generate some forecasts first
            3. Then add actual invoice data to track accuracy
            """)
        return
    
    # Overall accuracy metrics
    st.subheader("📊 Overall Method Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        simple_avg_acc = accuracy_df['simple_avg_accuracy'].mean()
        st.metric("Simple Average", f"{simple_avg_acc:.1%}" if not pd.isna(simple_avg_acc) else "N/A")
    
    with col2:
        weighted_avg_acc = accuracy_df['weighted_avg_accuracy'].mean()
        st.metric("Weighted Average", f"{weighted_avg_acc:.1%}" if not pd.isna(weighted_avg_acc) else "N/A")
    
    with col3:
        trending_avg_acc = accuracy_df['trending_avg_accuracy'].mean()
        st.metric("Trending Average", f"{trending_avg_acc:.1%}" if not pd.isna(trending_avg_acc) else "N/A")
    
    with col4:
        seasonal_acc = accuracy_df['seasonal_forecast_accuracy'].mean()
        st.metric("Seasonal Forecast", f"{seasonal_acc:.1%}" if not pd.isna(seasonal_acc) else "N/A")
    
    # Method comparison chart
    st.subheader("🔍 Method Accuracy Comparison")
    
    method_data = []
    for _, row in accuracy_df.iterrows():
        for method in ['simple_avg_accuracy', 'weighted_avg_accuracy', 'trending_avg_accuracy', 'seasonal_forecast_accuracy']:
            if not pd.isna(row[method]):
                method_data.append({
                    'Category': row['category'],
                    'Method': method.replace('_accuracy', '').replace('_', ' ').title(),
                    'Accuracy': row[method]
                })
    
    if method_data:
        method_df = pd.DataFrame(method_data)
        fig = px.bar(method_df, x='Category', y='Accuracy', color='Method',
                    title="Accuracy by Category and Method",
                    barmode='group')
        fig.update_layout(yaxis_tickformat='.0%')
        st.plotly_chart(fig, use_container_width=True)
    
    # Category-wise performance table
    st.subheader("📋 Category Performance Details")
    
    # Format accuracy columns as percentages
    display_df = accuracy_df.copy()
    accuracy_cols = ['simple_avg_accuracy', 'weighted_avg_accuracy', 'trending_avg_accuracy', 'seasonal_forecast_accuracy', 'recommended_accuracy']
    for col in accuracy_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.1%}" if not pd.isna(x) else "N/A")
    
    st.dataframe(display_df, use_container_width=True)

def database_management_page(db_manager):
    """Page for managing database and entering actual data"""
    st.header("💾 Database Management")
    
    tab1, tab2, tab3 = st.tabs(["📥 Enter Actuals", "🗃️ Database Info", "⚙️ Adaptive Weights"])
    
    with tab1:
        st.subheader("📥 Enter Actual Invoice Data")
        st.markdown("Enter actual invoice data to calculate forecast accuracy and improve future predictions.")
        
        # Show available forecast versions to guide data entry
        forecast_versions = db_manager.get_forecast_versions()
        if len(forecast_versions) > 0:
            st.info("💡 **Available forecast periods:** " + 
                   ", ".join([f"{row['target_month']:02d}/{row['target_year']}" 
                             for _, row in forecast_versions.head(5).iterrows()]))
        
        col1, col2 = st.columns(2)
        
        with col1:
            invoice_month = st.selectbox("Invoice Month", range(1, 13), 
                                       format_func=lambda x: datetime(2000, x, 1).strftime('%B'))
        
        with col2:
            invoice_year = st.number_input("Invoice Year", min_value=2020, max_value=2030, value=2025)
        
        # Show if there are forecasts for this period
        matching_forecasts = forecast_versions[
            (forecast_versions['target_month'] == invoice_month) & 
            (forecast_versions['target_year'] == invoice_year)
        ]
        
        if len(matching_forecasts) > 0:
            st.success(f"✅ Found {len(matching_forecasts)} forecast(s) for {datetime(2000, invoice_month, 1).strftime('%B')} {invoice_year}")
        else:
            st.warning(f"⚠️ No forecasts found for {datetime(2000, invoice_month, 1).strftime('%B')} {invoice_year}")
        
        # Manual entry form
        st.subheader("Manual Data Entry")
        
        with st.form("actual_data_form"):
            category = st.text_input("Category Name")
            actual_amount = st.number_input("Actual Amount", min_value=0.0, step=0.01)
            data_source = st.text_input("Data Source (optional)", placeholder="e.g., Invoice batch #123")
            
            submitted = st.form_submit_button("Add Actual Data")
            
            if submitted and category and actual_amount > 0:
                try:
                    actuals_data = {category: actual_amount}
                    
                    # Create temporary system to access database methods
                    temp_system = AccrualsSystem(enable_database=True)
                    temp_system.store_actuals_in_database(
                        actuals_data, invoice_month, invoice_year, data_source
                    )
                    
                    st.success(f"✓ Added actual data: {category} = ${actual_amount:,.2f} for {invoice_month}/{invoice_year}")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error storing actual data: {str(e)}")
        
        # Quick sample data button for testing
        if st.button("🧪 Add Sample Test Data (September 2025)"):
            sample_data = {
                'Consumables - Variable': 12500.00,
                'Handling - Variable': 33000.00,
                'Management - Fixed': 15000.00,
                'Storage - Fixed': 27000.00,
                'Storage - Variable': 6000.00
            }
            
            try:
                temp_system = AccrualsSystem(enable_database=True)
                temp_system.store_actuals_in_database(sample_data, 9, 2025, "Sample test data")
                st.success("✓ Added sample actual data for September 2025")
                st.rerun()
            except Exception as e:
                st.error(f"Error adding sample data: {str(e)}")
        
        # File upload for batch entry
        st.subheader("Batch Upload from Excel")
        
        uploaded_actuals = st.file_uploader(
            "Upload Excel file with actual data",
            type=['xlsx', 'xls'],
            help="Excel file should have 'Category' and 'Amount' columns"
        )
        
        if uploaded_actuals:
            try:
                actuals_df = pd.read_excel(uploaded_actuals)
                
                if 'Category' in actuals_df.columns and 'Amount' in actuals_df.columns:
                    st.dataframe(actuals_df.head())
                    
                    if st.button("Import Batch Actuals"):
                        actuals_dict = dict(zip(actuals_df['Category'], actuals_df['Amount']))
                        
                        temp_system = AccrualsSystem(enable_database=True)
                        temp_system.store_actuals_in_database(
                            actuals_dict, invoice_month, invoice_year, uploaded_actuals.name
                        )
                        
                        st.success(f"✓ Imported {len(actuals_dict)} actual data entries")
                        st.rerun()
                else:
                    st.error("Excel file must contain 'Category' and 'Amount' columns")
                    
            except Exception as e:
                st.error(f"Error reading Excel file: {str(e)}")
    
    with tab2:
        st.subheader("🗃️ Database Information")
        
        # Database statistics
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # Count records in each table
            tables = ['forecast_versions', 'forecasts', 'actuals', 'accuracy_metrics']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                st.metric(f"{table.replace('_', ' ').title()}", count)
    
    with tab3:
        st.subheader("⚙️ Adaptive Weights")
        st.markdown("View how the system learns from accuracy data to adjust forecasting weights.")
        
        # Get current adaptive weights
        with sqlite3.connect(db_manager.db_path) as conn:
            weights_df = pd.read_sql_query("SELECT * FROM learning_weights ORDER BY category", conn)
        
        if len(weights_df) > 0:
            st.dataframe(weights_df, use_container_width=True)
        else:
            st.info("No adaptive weights calculated yet. Add some actual data to enable learning.")

def version_history_page(db_manager):
    """Page showing forecast version history"""
    st.header("📊 Forecast Version History")
    
    # Get all forecast versions
    versions_df = db_manager.get_forecast_versions()
    
    if len(versions_df) == 0:
        st.info("No forecast versions found. Generate some forecasts to see history.")
        return
    
    # Display version summary
    st.subheader("📋 All Forecast Versions")
    
    # Format dates for display
    display_df = versions_df.copy()
    display_df['created_date'] = pd.to_datetime(display_df['created_date']).dt.strftime('%Y-%m-%d %H:%M')
    display_df['target_period'] = display_df.apply(lambda row: f"{row['target_month']:02d}/{row['target_year']}", axis=1)
    
    # Select columns for display
    display_cols = ['version_id', 'version_name', 'target_period', 'created_date', 'weekly_adjustment', 'notes']
    st.dataframe(display_df[display_cols], use_container_width=True)
    
    # Version comparison
    st.subheader("🔍 Compare Forecast Versions")
    
    selected_versions = st.multiselect(
        "Select versions to compare",
        options=versions_df['version_id'].tolist(),
        format_func=lambda x: f"v{x}: {versions_df[versions_df['version_id']==x]['version_name'].iloc[0]}"
    )
    
    if len(selected_versions) >= 2:
        comparison_data = []
        
        for version_id in selected_versions:
            forecasts_df = db_manager.get_forecasts_by_version(version_id)
            version_info = versions_df[versions_df['version_id'] == version_id].iloc[0]
            
            for _, forecast in forecasts_df.iterrows():
                comparison_data.append({
                    'Version': f"v{version_id}: {version_info['version_name']}",
                    'Category': forecast['category'],
                    'Recommended_Accrual': forecast['recommended_accrual']
                })
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            
            # Pivot for side-by-side comparison
            pivot_df = comparison_df.pivot(index='Category', columns='Version', values='Recommended_Accrual').fillna(0)
            
            st.dataframe(pivot_df.style.format("${:,.2f}"), use_container_width=True)
            
            # Chart comparison
            fig = px.bar(comparison_df, x='Category', y='Recommended_Accrual', color='Version',
                        title="Forecast Comparison Across Versions", barmode='group')
            fig.update_layout(yaxis_tickformat='$,.0f')
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
