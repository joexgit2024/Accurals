@echo off
echo ================================================
echo    HTML Report Generator
echo ================================================
echo.
echo Generating beautiful HTML report for sharing...
echo.

cd /d "c:\Accurals"
C:/Users/JX1040/AppData/Local/Microsoft/WindowsApps/python3.12.exe generate_html_report.py

echo.
echo ================================================
echo HTML report generated!
echo The file will open automatically in your browser.
echo Share it with colleagues via email or file sharing.
echo ================================================
echo.
pause
