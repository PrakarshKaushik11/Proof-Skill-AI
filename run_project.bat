@echo off
REM ============================================================
REM ProofSkill AI - ONE-CLICK PROJECT RUNNER
REM ============================================================
REM This script sets up the entire project and runs it
REM Run: run_project.bat
REM ============================================================

echo ============================================================
echo  🎯 ProofSkill AI - One-Click Project Runner
echo ============================================================
echo.

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: Run this from the ProofSkillAI project root directory
    echo    (where app.py is located)
    pause
    exit /b 1
)

REM ============================================================
REM STEP 1: Create virtual environment if needed
REM ============================================================
echo [1/7] Checking virtual environment...
if not exist ".venv" (
    echo    Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo    Virtual environment exists ✓
)

REM ============================================================
REM STEP 2: Activate virtual environment
REM ============================================================
echo [2/7] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

REM ============================================================
REM STEP 3: Upgrade pip and install build tools
REM ============================================================
echo [3/7] Upgrading pip and installing build dependencies...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1

REM Install MSVC-compatible packages first
echo    Installing core dependencies...
pip install --only-binary=:all: pyyaml aiohttp multidict frozenlist yarl attrs aiohappyeyeballs aiosignal >nul 2>&1

REM ============================================================
REM STEP 4: Install core ML dependencies
REM ============================================================
echo [4/7] Installing ML dependencies (this may take a few minutes)... 
pip install torch aiohttp edge-tts gradio_client==0.10.0 huggingface-hub==0.20.0 >nul 2>&1

echo    Installing Whisper and audio libraries...
pip install openai-whisper tiktoken numba llvmlite regex >nul 2>&1

echo    Installing web framework and utilities...
pip install streamlit pandas plotly >nul 2>&1

echo    Installing GitHub and database libraries...
pip install PyGithub sqlalchemy python-docx pdfplumber spacy >nul 2>&1

echo    Downloading spaCy model...
python -m spacy download en_core_web_sm >nul 2>&1

REM ============================================================
REM STEP 5: Install optional dependencies
REM ============================================================
echo [5/7] Installing optional dependencies...
pip install llama-cpp-python >nul 2>&1
if errorlevel 1 (
    echo    ⚠️  llama-cpp-python needs MSVC Build Tools (optional)
)

REM ============================================================
REM STEP 6: Initialize database and sample data
REM ============================================================
echo [6/7] Initializing database and sample data...
python scripts/load_sample_data.py >nul 2>&1
if errorlevel 1 (
    echo    Initializing database directly...
    python -c "
import sys
sys.path.insert(0, '.')
from src.db.session import init_db
init_db()
print('Database initialized')
"
)

REM ============================================================
REM STEP 7: Run quick verification test
REM ============================================================
echo [7/7] Running quick verification test...
python scripts/minimal_test.py

echo.
echo ============================================================
echo ✅ SETUP COMPLETE!
echo ============================================================
echo.
echo Starting ProofSkill AI Streamlit app...
echo    Access at: http://localhost:8501
echo    Press Ctrl+C to stop
echo.

REM Start the Streamlit app
streamlit run app.py

echo.
echo App stopped. Press any key to exit...
pause