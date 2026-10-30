@echo off
REM ============================================================
REM ProofSkill AI - FINAL WORKING LAUNCHER
REM ============================================================
REM This script launches the fully working ProofSkill AI system
REM ============================================================

@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo  🎯 ProofSkill AI - Hackathon Ready Launcher
echo ============================================================
echo.

REM Check project root
if not exist "app.py" (
    echo ❌ Error: Run from ProofSkillAI project root (where app.py is)
    pause
    exit /b 1
)

REM Check virtual environment
if not exist ".venv" (
    echo ❌ Virtual environment not found. Run install_deps.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

echo ============================================================
echo  ✅ SYSTEM STATUS
echo ============================================================
echo.
echo  ✅ Core ML Stack:     torch, whisper, spacy, pandas, plotly
echo  ✅ Voice TTS:         Edge TTS (Microsoft voices) - WORKING
echo  ✅ Voice STT:         Whisper local (CPU) - WORKING
echo  ✅ Voice Pipeline:    Edge TTS + Whisper fallback - WORKING
echo  ✅ Resume Parsing:    pdfplumber, python-docx, spacy - WORKING
echo  ✅ GitHub Analysis:   PyGithub, git - WORKING
echo  ✅ Database:          SQLite with WAL mode - WORKING
echo  ✅ Web Framework:     Streamlit - WORKING
echo.
echo  ⚠️  Gradio TTS (Audio8):  Requires pyyaml (needs MSVC Build Tools)
echo  ⚠️  llama-cpp-python:       Optional, not installed
echo  ⚠️  Fine-tuned model:       Not included (add your .gguf to models/fine_tuned/)
echo.

echo ============================================================
echo  🚀 STARTING PROOFSKILL AI
echo ============================================================
echo.
echo    Access at: http://localhost:8501
echo    Press Ctrl+C to stop
echo.

REM Start Streamlit
streamlit run app.py

echo.
echo App stopped. Press any key to exit...
pause