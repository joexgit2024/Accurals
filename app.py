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

# Import our main forecasting system
from accruals_main import AccrualsSystem

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
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Upload your Excel file",
        type=['xlsx', 'xls'],
        help="Upload your actual spending Excel file"
    )
    
    if uploaded_file is not None:
        try:
            # Save uploaded file temporarily
            with open("temp_upload.xlsx", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Initialize forecasting system
            system = AccrualsSystem(input_file="temp_upload.xlsx")
            
            if system.generate_forecasts():
                results_df = pd.DataFrame(system.results)
                
                # Main dashboard
                col1, col2, col3, col4 = st.columns(4)
                
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
                        "RECOMMENDED",
                        f"${results_df['Recommended_Accrual'].sum():,.2f}",
                        help="Average of all three forecasting methods"
                    )
                
                # Charts section
                st.header("📈 Forecast Comparison")
                
                # Bar chart comparing methods
                methods_data = {
                    'Method': ['Simple Average', 'Weighted Average', 'Trending Average', 'Recommended'],
                    'Amount': [
                        results_df['Simple_Average'].sum(),
                        results_df['Weighted_Average'].sum(), 
                        results_df['Trending_Average'].sum(),
                        results_df['Recommended_Accrual'].sum()
                    ]
                }
                
                fig_bar = px.bar(
                    methods_data,
                    x='Method',
                    y='Amount',
                    title='Forecast Comparison by Method',
                    color='Method'
                )
                fig_bar.update_layout(yaxis_tickformat='$,.0f')
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Category breakdown
                st.header("📋 Category Breakdown")
                
                # Filter out zero values for cleaner display
                non_zero_results = results_df[results_df['Recommended_Accrual'] > 0]
                
                if len(non_zero_results) > 0:
                    fig_pie = px.pie(
                        non_zero_results,
                        values='Recommended_Accrual',
                        names='Category',
                        title='Recommended Accruals by Category'
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                # Detailed results table
                st.header("📊 Detailed Results")
                
                # Display options
                show_columns = st.multiselect(
                    "Select columns to display:",
                    options=results_df.columns.tolist(),
                    default=['Category', 'Simple_Average', 'Weighted_Average', 'Trending_Average', 'Recommended_Accrual', 'Confidence']
                )
                
                if show_columns:
                    st.dataframe(
                        results_df[show_columns].style.format({
                            col: "${:,.2f}" for col in show_columns 
                            if col in ['Simple_Average', 'Weighted_Average', 'Trending_Average', 'Recommended_Accrual']
                        }),
                        use_container_width=True
                    )
                
                # Export section
                st.header("💾 Export Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Generate Excel Report"):
                        output_file = system.export_results("forecast_results.xlsx")
                        st.success(f"Excel report generated: {output_file}")
                
                with col2:
                    # Download link for CSV
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="Download as CSV",
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
                st.error("Failed to process the uploaded file. Please check the file format.")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    else:
        # Welcome screen
        st.info("👆 Upload your Excel file to get started")
        
        st.markdown("""
        ### How to use this system:
        
        1. **Upload** your actual spending Excel file using the sidebar
        2. **Review** the forecast results across three different methods
        3. **Analyze** the recommended accruals for the next month
        4. **Export** results to Excel or CSV for further analysis
        
        ### File Requirements:
        - Excel file (.xlsx or .xls)
        - Columns: SAP, GLCode, Row Labels, and monthly data columns
        - Historical spending data for accurate forecasting
        """)

if __name__ == "__main__":
    main()
