@echo off
REM ============================================================
REM ProofSkill AI - WORKING ONE-CLICK RUNNER (Windows)
REM ============================================================
REM This version handles Windows compilation issues properly
REM ============================================================

setlocal enabledelayedexpansion

echo ============================================================
echo  🎯 ProofSkill AI - Working One-Click Runner
echo ============================================================
echo.

REM Check project root
if not exist "app.py" (
    echo ❌ Error: Run from ProofSkillAI project root (where app.py is)
    pause
    exit /b 1
)

REM ============================================================
REM STEP 1: Create virtual environment
REM ============================================================
echo [1/6] Setting up virtual environment...
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
REM STEP 2: Activate and upgrade pip
REM ============================================================
echo [2/6] Activating environment and upgrading pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel >nul 2>&1

REM ============================================================
REM STEP 3: Install WORKING packages only (no compilation needed)
REM ============================================================
echo [3/6] Installing WORKING packages (pre-compiled wheels only)...

echo    Installing core ML packages...
pip install torch aiohttp edge-tts gradio_client==0.10.0 huggingface-hub==0.20.0 --only-binary=:all: 2>nul
if errorlevel 1 (
    echo    Trying without --only-binary for torch...
    pip install torch aiohttp edge-tts gradio_client==0.10.0 huggingface-hub==0.20.0 2>nul
)

echo    Installing audio & ML packages...
pip install openai-whisper tiktoken numba llvmlite regex --only-binary=:all: 2>nul
if errorlevel 1 (
    pip install openai-whisper tiktoken numba llvmlite regex 2>nul
)

echo    Installing web framework...
pip install streamlit pandas plotly --only-binary=:all: 2>nul
if errorlevel 1 (
    pip install streamlit pandas plotly 2>nul
)

echo    Installing utilities...
pip install PyGithub sqlalchemy python-docx pdfplumber spacy --only-binary=:all: 2>nul
if errorlevel 1 (
    pip install PyGithub sqlalchemy python-docx pdfplumber spacy 2>nul
)

echo    Installing spaCy model...
python -m spacy download en_core_web_sm >nul 2>&1

echo    Trying pyyaml (may need MSVC Build Tools)...
pip install pyyaml 2>nul
if errorlevel 1 (
    echo    ⚠️  pyyaml needs MSVC Build Tools - Gradio TTS will use fallback
    echo    To fix: Install "Microsoft Visual C++ Build Tools" from https://visualstudio.microsoft.com/visual-cpp-build-tools/
)

REM ============================================================
REM STEP 4: Initialize database
REM ============================================================
echo [4/6] Initializing database...
python scripts/load_sample_data.py >nul 2>&1
if errorlevel 1 (
    python -c "import sys; sys.path.insert(0, '.'); from src.db.session import init_db; init_db(); print('Database initialized')"
)

REM ============================================================
REM STEP 5: Quick verification test
REM ============================================================
echo [5/6] Running verification test...
python scripts/minimal_test.py

REM ============================================================
REM STEP 6: Start Streamlit app
REM ============================================================
echo [6/6] Starting ProofSkill AI...
echo.
echo ============================================================
echo ✅ SETUP COMPLETE - Starting Streamlit app...
echo ============================================================
echo.
echo    Access at: http://localhost:8501
echo    Press Ctrl+C to stop
echo.

streamlit run app.py

echo.
echo App stopped. Press any key to exit...
pause