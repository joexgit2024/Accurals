"""
HTML Report Generator for Accruals Forecasting System
=====================================================

This script generates beautiful HTML reports that can be shared with colleagues
who don't have access to the web interface. The HTML files open in any browser
and provide a professional, easy-to-read presentation of forecast results.

Usage: python generate_html_report.py
Output: Beautiful HTML report in Output folder
"""

from accruals_main import AccrualsSystem
import sys

def main():
    """Generate only HTML report for sharing"""
    print("Generating HTML Report for Sharing...")
    print("="*50)
    
    # Initialize system
    system = AccrualsSystem()
    
    # Generate forecasts
    if system.generate_forecasts():
        # Export only HTML report
        html_file = system.export_html_report()
        
        # Print summary for reference
        system.print_summary()
        
        print(f"\n✅ HTML Report Generated Successfully!")
        print(f"🌐 File: {html_file}")
        print(f"📧 Share this file with your colleagues")
        print(f"💡 Opens in any web browser - no special software needed")
        print(f"📱 Mobile-friendly responsive design")
        
        # Try to open the HTML file automatically
        try:
            import webbrowser
            webbrowser.open(html_file)
            print(f"🚀 Opening report in your default browser...")
        except:
            print(f"📁 Please open the HTML file manually in your browser")
        
    else:
        print("✗ Report generation failed. Please check your input file.")

if __name__ == "__main__":
    main()
