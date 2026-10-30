#!/usr/bin/env python
"""
ProofSkill AI - Quick Start Script
Run with: python run.py
"""
import sys
import subprocess
from pathlib import Path


def check_requirements():
    """Check if all requirements are installed."""
    try:
        import streamlit
        import pydantic
        import sqlalchemy
        import pdfplumber
        import docx
        import spacy
        import github
        import elevenlabs
        import whisper
        print("✅ All core dependencies installed")
        try:
            import llama_cpp
            print("✅ Optional llama-cpp-python installed")
        except ImportError:
            print("⚠️ Optional llama-cpp-python not installed; mock model will be used")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False


def check_spacy_model():
    """Check if spaCy model is downloaded."""
    try:
        import spacy
        spacy.load("en_core_web_sm")
        print("✅ spaCy model loaded")
        return True
    except OSError:
        print("❌ spaCy model 'en_core_web_sm' not found")
        print("Run: python -m spacy download en_core_web_sm")
        return False


def check_env_file():
    """Check if .env file exists."""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file found")
        return True
    else:
        print("⚠️  .env file not found")
        print("Copy .env.example to .env and fill in your API keys:")
        print("  cp .env.example .env")
        return False


def check_model():
    """Check if fine-tuned model exists."""
    model_path = Path("models/fine_tuned")
    if model_path.exists() and any(model_path.iterdir()):
        print("✅ Fine-tuned model found")
        return True
    else:
        print("⚠️  No fine-tuned model found in models/fine_tuned/")
        print("The app will use mock model for development")
        return False


def check_database():
    """Check if database exists."""
    db_path = Path("data/proofskill.db")
    if db_path.exists():
        print("✅ Database initialized")
        return True
    else:
        print("⚠️  Database not initialized")
        print("Run: python scripts/load_sample_data.py")
        return False


def main():
    print("=" * 50)
    print("🎯 ProofSkill AI - System Check")
    print("=" * 50)
    
    checks = [
        ("Dependencies", check_requirements),
        ("spaCy Model", check_spacy_model),
        ("Environment", check_env_file),
        ("Fine-tuned Model", check_model),
        ("Database", check_database),
    ]
    
    all_passed = True
    for name, check_fn in checks:
        print(f"\n🔍 Checking {name}...")
        if not check_fn():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All checks passed! Starting Streamlit...")
        print("=" * 50)
        # Start Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    main()