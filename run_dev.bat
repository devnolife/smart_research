@echo off
echo ================================
echo Smart Research Assistant v2
echo ================================

echo.
echo Starting development server...
echo.

cd backend

echo Installing/updating dependencies...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please check your Python installation and internet connection
    pause
    exit /b 1
)

echo.
echo Starting Flask development server...
echo Server will be available at: http://localhost:5000
echo.

python app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start server
    echo Please check the error messages above
    pause
    exit /b 1
)

pause
