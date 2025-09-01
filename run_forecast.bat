@echo off
echo ================================================
echo    Accruals Forecasting System
echo ================================================
echo.
echo Running forecast analysis...
echo.

cd /d "c:\Accurals"
C:/Users/JX1040/AppData/Local/Microsoft/WindowsApps/python3.12.exe accruals_main.py

echo.
echo ================================================
echo Process completed!
echo.
echo Opening Output folder...
start "" "c:\Accurals\Output"
echo.
echo ================================================
echo.
pause
