@echo off
REM ProofSkill AI - Windows Launcher
REM Run with: run.bat

echo ============================================
echo  🎯 ProofSkill AI - Starting Up
echo ============================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

REM Download spaCy model if needed
echo Checking spaCy model...
python -c "import spacy; spacy.load('en_core_web_sm')" 2>nul
if errorlevel 1 (
    echo Downloading spaCy model...
    python -m spacy download en_core_web_sm
    if errorlevel 1 (
        echo Failed to download spaCy model
        pause
        exit /b 1
    )
)

REM Check .env file
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Copy .env.example to .env and fill in your API keys
    echo.
    copy .env.example .env
)

REM Initialize database if needed
if not exist "data\proofskill.db" (
    echo Initializing database...
    python scripts\load_sample_data.py
    if errorlevel 1 (
        echo Failed to initialize database
        pause
        exit /b 1
    )
)

REM Start Streamlit
echo.
echo ============================================
echo  ✅ All checks passed! Starting Streamlit...
echo ============================================
echo.
streamlit run app.py

pause