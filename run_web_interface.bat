@echo off
echo ================================================
echo    Accruals Forecasting - Web Interface
echo ================================================
echo.
echo Starting web interface...
echo Open your browser to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the web server
echo ================================================
echo.

cd /d "c:\Accurals"
C:/Users/JX1040/AppData/Local/Microsoft/WindowsApps/python3.12.exe -m streamlit run web_interface.py

pause
