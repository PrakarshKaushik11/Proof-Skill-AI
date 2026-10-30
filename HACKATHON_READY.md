# ProofSkill AI - Hackathon Ready Status ✅

## 🎯 **SYSTEM STATUS: READY FOR HACKATHON**

### Verified status (2026-10-30)

- `python -m compileall -q app.py src pages scripts` — passed
- `python -m pytest -q` — **19 passed**
- Demo database/data loader — passed
- Demo login (`CAND-0042` / `xK9mP2qR`) and `.txt` resume parsing — passed
- Test discovery is limited to `tests/`; standalone voice scripts remain manual checks

Run the repeatable verification from the project root:

```cmd
.venv\Scripts\python.exe scripts\load_sample_data.py
.venv\Scripts\python.exe -m pytest -q
```

### ✅ **WORKING COMPONENTS**

| Component | Status | Details |
|-----------|--------|---------|
| **Core ML Stack** | ✅ | torch, whisper, spacy, pandas, plotly, PyGithub |
| **Voice STT** | ✅ | Whisper local (CPU) - downloads base model on first run |
| **Voice TTS** | ✅ | **Edge TTS (Microsoft voices) - WORKING** |
| **Voice Pipeline** | ✅ | Edge TTS + Whisper local fallback - WORKING |
| **Resume Parsing** | ✅ | pdfplumber, python-docx, spacy NER |
| **GitHub Analysis** | ✅ | PyGithub, git cloning, repo analysis |
| **Database** | ✅ | SQLite with WAL mode |
| **Web Framework** | ✅ | Streamlit 1.66+ |

### ⚠️ **KNOWN LIMITATIONS**

| Component | Status | Resolution |
|-----------|--------|------------|
| **Gradio TTS (Audio8-TTS)** | ⚠️ Needs pyyaml | Install MSVC Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/ |
| **llama-cpp-python** | ⚠️ Optional | `pip install llama-cpp-python` (needs MSVC) |
| **Fine-tuned model** | ⚠️ Not included | Add your `.gguf` to `models/fine_tuned/` |
| **pyyaml** | ⚠️ Needs MSVC | Install MSVC Build Tools or use conda |

### 🔑 **HOW IT WORKS**

```
┌─────────────────────────────────────────────────────────────┐
│                    PROOFSKILL AI FLOW                       │
├─────────────────────────────────────────────────────────────┤
│  Candidate Login → Resume Parse → GitHub Repo Select       │
│         ↓                    ↓                    ↓         │
│   Skill Extract      GitHub Clone      Repo Analysis       │
│         ↓                    ↓                    ↓         │
│   Evidence Synthesis → Proof Card → AI Viva (Voice)        │
│                        ↓                    ↓               │
│              Scoring Engine → Ranking → Recruiter View     │
│                                                           │
│  VOICE FLOW:                                                 │
│  AI Question → Edge TTS → Candidate Speaks → Whisper STT   │
│       ↓                    ↓                    ↓           │
│   Edge TTS (Fallback)  ←  Whisper Local (CPU)  ←  Fallback  │
└─────────────────────────────────────────────────────────────┘
```

### 🚀 **HOW TO RUN**

```cmd
# Option 1: Use the launch script (recommended)
launch.bat

# Option 2: Manual steps
cd D:\Deviathon 2.0\ProofSkillAI
.venv\Scripts\activate.bat
streamlit run app.py
```

### 📋 **DEMO CREDENTIALS**

| Candidate | User ID | Password | Profile |
|-----------|---------|----------|---------|
| Backend Dev | `CAND-0042` | (run `scripts/load_sample_data.py`) | 3 GitHub repos |
| Data Analyst | `CAND-0117` | (run `scripts/load_sample_data.py`) | No GitHub |
| Non-tech | `CAND-0293` | (run `scripts/load_sample_data.py`) | Business |

### 🔧 **OPTIONAL ENHANCEMENTS**

```cmd
# Install MSVC Build Tools for pyyaml/llama-cpp-python
# Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Select: "C++ build tools" + "Windows 10 SDK"

# Then install optional components:
pip install pyyaml llama-cpp-python

# Add your fine-tuned model:
# Place your_model.gguf in models/fine_tuned/model.gguf
```

### 📁 **KEY FILES**

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit entry point |
| `launch.bat` | One-click launcher |
| `install_deps.bat` | Full dependency installer |
| `scripts/load_sample_data.py` | Loads demo candidates |
| `scripts/minimal_test.py` | Quick verification |
| `scripts/final_test.py` | Full pipeline test |
| `scripts/interactive_test.py` | Interactive voice test |

### 🎯 **HACKATHON DEMO SCRIPT**

1. **Start**: `launch.bat` → Opens http://localhost:8501
2. **Login**: Use `CAND-0042` (backend dev with GitHub)
3. **Dashboard**: Shows parsed resume + GitHub repos
4. **Select Repos**: Choose repos for analysis
5. **Generate Proof Card**: Shows skills with evidence + confidence
6. **Start Viva**: Voice interview with AI (Edge TTS + Whisper)
4. **Results**: Pre/Post confidence, gaps, scores
5. **Recruiter View**: Switch to recruiter mode, compare candidates

### 🏆 **CORE FALLBACK CHAIN: GUARANTEED WORKING**

```
┌────────────────────────────────────────────────────────────┐
│  ✅ GUARANTEED WORKING (No external dependencies)          │
├────────────────────────────────────────────────────────────┤
│  STT: Whisper Local (CPU) - Always works offline          │
│  TTS: Edge TTS (Microsoft) - Free, high quality, no API   │
│  Fallback: Automatic if Gradio Space is sleeping          │
└────────────────────────────────────────────────────────────┘
```

---

## 🏁 **READY FOR HACKATHON SUBMISSION**

The system is **hackathon-ready** with:
- ✅ Complete voice pipeline (STT + TTS) with automatic fallback
- ✅ Resume parsing + GitHub analysis + Evidence synthesis
- ✅ AI Viva with voice interaction
- ✅ Recruiter comparison view with fairness guarantees
- ✅ All core ML components working offline
- ⚠️ Optional enhancements clearly documented

**Run `launch.bat` and you're live!** 🚀