@echo off
chcp 65001 > nul
echo ===== QA4U3 App Setup =====

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs
set LOG_FILE=logs\setup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set LOG_FILE=%LOG_FILE: =0%

echo Setup started at %date% %time% > %LOG_FILE%
echo ===== QA4U3 App Setup ===== >> %LOG_FILE%

REM Check Python installation
echo [Step 1/4] Checking Python...
echo [Step 1/4] Checking Python... >> %LOG_FILE%
python --version >> %LOG_FILE% 2>&1
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python. | tee -a %LOG_FILE%
    pause
    exit /b 1
)

REM Create virtual environment
echo [Step 2/4] Creating virtual environment...
echo [Step 2/4] Creating virtual environment... >> %LOG_FILE%
python -m venv .venv >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment. | tee -a %LOG_FILE%
    pause
    exit /b 1
)

REM Activate virtual environment
echo [Step 3/4] Activating virtual environment...
echo [Step 3/4] Activating virtual environment... >> %LOG_FILE%
call .venv\Scripts\activate >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment. | tee -a %LOG_FILE%
    pause
    exit /b 1
)

REM Install dependencies
echo [Step 4/4] Installing packages...
echo [Step 4/4] Installing packages... >> %LOG_FILE%

echo Upgrading pip...
echo Upgrading pip... >> %LOG_FILE%
python -m pip install --upgrade pip >> %LOG_FILE% 2>&1

echo Installing streamlit...
echo Installing streamlit... >> %LOG_FILE%
pip install streamlit>=1.20 >> %LOG_FILE% 2>&1

echo Installing dimod...
echo Installing dimod... >> %LOG_FILE%
pip install dimod>=0.10.11 >> %LOG_FILE% 2>&1

echo Installing dwave-neal...
echo Installing dwave-neal... >> %LOG_FILE%
pip install dwave-neal==0.6.0 >> %LOG_FILE% 2>&1

echo.
echo Setup completed successfully!
echo Installation logs saved to: %LOG_FILE%
echo.
echo Virtual environment is activated and packages are installed.
echo To run the application: streamlit run app.py
echo.

echo Setup completed at %date% %time% >> %LOG_FILE%
echo All logs saved to: %LOG_FILE% >> %LOG_FILE%

pause
