#!/usr/bin/env python
"""
ProofSkill AI - ONE-FILE PROJECT RUNNER
=======================================
Run everything with: python run_all.py

This single script:
1. Creates virtual environment
2. Installs all dependencies
3. Sets up database & sample data  
4. Runs verification tests
5. Starts the Streamlit app

Usage:
    python run_all.py              # Full setup + run
    python run_all.py --dev        # Development mode (skip some installs)
    python run_all.py --test-only  # Run tests only
    python run_all.py --install-only # Install only, don't run app
"""

import sys
import subprocess
import os
import venv
import shutil
from pathlib import Path

# ─── Configuration ────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()
VENV_DIR = PROJECT_ROOT / ".venv"
REQUIREMENTS_CORE = [
    "torch", "aiohttp", "edge-tts", 
    "openai-whisper", "tiktoken", "numba", "llvmlite", "regex",
    "streamlit", "pandas", "plotly",
    "PyGithub", "sqlalchemy", "python-docx", "pdfplumber", "spacy",
]
REQUIREMENTS_BINARY = [
    "aiohttp", "multidict", "frozenlist", 
    "yarl", "attrs", "aiohappyeyeballs", "aiosignal"
]
# These packages are optional: Edge TTS and the remote/API fallbacks keep the
# application usable when native builds or third-party spaces are unavailable.
OPTIONAL_REQUIREMENTS = []
SPACY_MODEL = "en_core_web_sm"

# ─── Helpers ──────────────────────────────────────────────────
def run_cmd(cmd, cwd=None, capture=False, desc=None):
    """Run command with nice output."""
    if desc:
        print(f"\n  🔧 {desc}...")
    try:
        # Use list form for better path handling on Windows
        if isinstance(cmd, list):
            cmd_str = " ".join(f'"{c}"' if " " in c else c for c in cmd)
        else:
            cmd_str = cmd
        
        result = subprocess.run(
            cmd_str, shell=True, cwd=cwd or PROJECT_ROOT,
            capture_output=capture, text=True
        )
        if result.returncode != 0 and not capture:
            print(f"  ❌ Failed: {cmd_str[:80]}...")
            if result.stderr:
                print(f"     Error: {result.stderr[:200]}")
            return False
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def pip_install(python_exe, packages, binary_only=False, desc=None):
    """Install packages via pip."""
    if not packages:
        return True
    pkg_str = " ".join(packages)
    pip_cmd = f'"{python_exe}" -m pip install'
    if binary_only:
        pip_cmd += " --only-binary=:all:"
    pip_cmd += f" {pkg_str}"
    return run_cmd(pip_cmd, desc=desc or f"Installing {len(packages)} packages")

def ensure_venv():
    """Create virtual environment if needed."""
    if not VENV_DIR.exists():
        print("  📦 Creating virtual environment...")
        venv.create(VENV_DIR, with_pip=True)
    
    # Determine python executable in venv
    if os.name == 'nt':
        python_exe = VENV_DIR / "Scripts" / "python.exe"
    else:
        python_exe = VENV_DIR / "bin" / "python"
    
    if not python_exe.exists():
        print(f"  ❌ Virtual environment not found at {python_exe}")
        return None
    
    return str(python_exe)

def install_dependencies(python_exe, dev_mode=False):
    """Install all dependencies."""
    print("\n  📦 Installing dependencies...")
    
    # Upgrade pip first
    run_cmd([python_exe, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    
    # Binary packages first (no compilation needed)
    print("  📦 Installing pre-compiled packages...")
    pip_install(python_exe, REQUIREMENTS_BINARY, binary_only=True, desc="Installing binary packages")
    
    # Core ML packages
    print("  🧠 Installing ML packages...")
    pip_install(python_exe, REQUIREMENTS_CORE, desc="Installing ML packages")
    
    # Optional native integrations are intentionally not installed by default.
    # llama-cpp-python has no reliable Python 3.15 Windows wheel and its source
    # build is vulnerable to Windows path-length failures.
    if OPTIONAL_REQUIREMENTS and not dev_mode:
        print("  🔧 Installing optional packages...")
        pip_install(python_exe, OPTIONAL_REQUIREMENTS, desc="Installing optional packages")
    
    # SpaCy model
    print("  📥 Downloading spaCy model...")
    run_cmd([python_exe, "-m", "spacy", "download", SPACY_MODEL], desc="Downloading spaCy model")

def setup_database(python_exe):
    """Initialize database and sample data."""
    print("\n  🗄️  Setting up database...")
    # Try the script first
    result = run_cmd([python_exe, "scripts/load_sample_data.py"], capture=True)
    if not result:
        # Fallback: direct init
        run_cmd([python_exe, "-c", "import sys; sys.path.insert(0, '.'); from src.db.session import init_db; init_db(); print('Database initialized')"])

def run_tests(python_exe):
    """Run verification tests."""
    print("\n  🧪 Running verification tests...")
    return run_cmd([python_exe, "scripts/minimal_test.py"])

def start_app(python_exe):
    """Start Streamlit app."""
    print("\n  🚀 Starting ProofSkill AI...")
    print("     Access at: http://localhost:8501")
    print("     Press Ctrl+C to stop\n")
    try:
        subprocess.run([python_exe, "-m", "streamlit", "run", "app.py"], cwd=PROJECT_ROOT)
    except KeyboardInterrupt:
        print("\n\n  👋 App stopped by user")

# ─── Main ─────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="ProofSkill AI - One-File Runner")
    parser.add_argument("--dev", action="store_true", help="Development mode (skip optional deps)")
    parser.add_argument("--test-only", action="store_true", help="Run tests only")
    parser.add_argument("--install-only", action="store_true", help="Install only, don't run app")
    parser.add_argument("--no-venv", action="store_true", help="Use current Python (no venv)")
    args = parser.parse_args()

    print("=" * 60)
    print("  🎯 ProofSkill AI - One-Click Project Runner")
    print("=" * 60)

    # Check project root
    if not (PROJECT_ROOT / "app.py").exists():
        print("❌ Error: Run from ProofSkillAI project root (where app.py is)")
        sys.exit(1)

    # Get Python executable
    global VENV_PYTHON
    if args.no_venv:
        VENV_PYTHON = sys.executable
        print("  ⚠️  Using system Python (no virtual environment)")
    else:
        VENV_PYTHON = ensure_venv()
        if not VENV_PYTHON:
            sys.exit(1)
        print(f"  ✅ Using: {VENV_PYTHON}")

    # Install dependencies
    if not args.test_only:
        install_dependencies(VENV_PYTHON, dev_mode=args.dev)
        setup_database(VENV_PYTHON)

    # Run tests
    test_passed = run_tests(VENV_PYTHON)
    
    if not test_passed:
        print("\n  ⚠️  Some tests failed, but continuing...")

    if args.install_only:
        print("\n  ✅ Installation complete!")
        return

    # Start app
    start_app(VENV_PYTHON)

if __name__ == "__main__":
    main()


    