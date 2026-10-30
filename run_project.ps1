# ============================================================
# ProofSkill AI - ONE-CLICK PROJECT RUNNER (PowerShell)
# ============================================================
# Run: .\run_project.ps1
# Or: PowerShell -ExecutionPolicy Bypass -File .\run_project.ps1
# ============================================================

param(
    [switch]$SkipTests,
    [switch]$SkipInstall,
    [switch]$DevMode
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  🎯 ProofSkill AI - One-Click Project Runner" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check project root
if (-not (Test-Path "app.py")) {
    Write-Error "❌ Run this from the ProofSkillAI project root (where app.py is)"
    exit 1
}

function Write-Step($step, $total, $message) {
    Write-Host "[$step/$total] $message" -ForegroundColor Yellow
}

function Write-Success($message) {
    Write-Host "  ✅ $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "  ⚠️  $message" -ForegroundColor Yellow
}

function Write-ErrorMsg($message) {
    Write-Host "  ❌ $message" -ForegroundColor Red
}

# STEP 1: Virtual Environment
Write-Step 1 7 "Checking virtual environment..."
if (-not (Test-Path ".venv")) {
    Write-Host "  Creating virtual environment..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { Write-ErrorMsg "Failed to create venv"; exit 1 }
} else {
    Write-Success "Virtual environment exists"
}

# STEP 2: Activate
Write-Step 2 7 "Activating virtual environment..."
& .venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) { Write-ErrorMsg "Failed to activate venv"; exit 1 }
Write-Success "Virtual environment activated"

# STEP 3: Upgrade pip and install binary packages
Write-Step 3 7 "Upgrading pip and installing build dependencies..."
python -m pip install --upgrade pip setuptools wheel | Out-Null

Write-Host "  Installing pre-compiled packages..."
$binaryPackages = @("pyyaml", "aiohttp", "multidict", "frozenlist", "yarl", "attrs", "aiohappyeyeballs", "aiosignal")
foreach ($pkg in $binaryPackages) {
    pip install --only-binary=:all: $pkg 2>$null | Out-Null
}
Write-Success "Binary packages installed"

# STEP 4: Core ML dependencies
Write-Step 4 7 "Installing ML dependencies..."
$mlPackages = @(
    "torch", "aiohttp", "edge-tts", 
    "gradio_client==0.10.0", "huggingface-hub==0.20.0",
    "openai-whisper", "tiktoken", "numba", "llvmlite", "regex",
    "streamlit", "pandas", "plotly",
    "PyGithub", "sqlalchemy", "python-docx", "pdfplumber", "spacy"
)
pip install $mlPackages 2>$null | Out-Null
Write-Success "ML dependencies installed"

# STEP 5: SpaCy model
Write-Step 5 7 "Downloading spaCy model..."
python -m spacy download en_core_web_sm 2>$null | Out-Null
Write-Success "spaCy model ready"

# STEP 6: Optional dependencies
Write-Step 6 7 "Installing optional dependencies..."
try {
    pip install llama-cpp-python 2>$null | Out-Null
    Write-Success "llama-cpp-python installed"
} catch {
    Write-Warning "llama-cpp-python needs MSVC Build Tools (optional)"
}

# STEP 7: Database & Tests
Write-Step 7 7 "Initializing database and running tests..."
try {
    python scripts/load_sample_data.py 2>$null | Out-Null
} catch {
    python -c "import sys; sys.path.insert(0, '.'); from src.db.session import init_db; init_db(); print('Database initialized')" | Out-Null
}
Write-Success "Database initialized"

if (-not $SkipTests) {
    Write-Host "  Running quick verification..."
    python scripts/minimal_test.py
}

# FINAL
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✅ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting ProofSkill AI Streamlit app..." -ForegroundColor Cyan
Write-Host "   Access at: http://localhost:8501" -ForegroundColor Gray
Write-Host "   Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Start Streamlit
streamlit run app.py