@echo off
echo 🚀 Starting Cryptogeezas Investment Club App...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo 📦 Checking dependencies...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo 📥 Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if sample data should be created
if not exist "data" (
    echo 🎯 First time setup detected!
    echo.
    set /p "create_sample=Do you want to create sample data for testing? (y/n): "
    if /i "%create_sample%"=="y" (
        echo 📊 Creating sample data...
        python init_sample_data.py
        echo.
    )
)

REM Start the Streamlit app
echo 🌐 Starting Streamlit app...
echo 📱 The app will open in your browser automatically
echo 🔗 If it doesn't open, go to: http://localhost:8501
echo.
echo 💡 Press Ctrl+C to stop the application
echo.

streamlit run app.py

pause
