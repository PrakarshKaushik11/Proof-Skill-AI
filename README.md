# ProofSkill AI — IM-105 "Proof Card" System

> **Hackathon Project** | Integraminds | AI FRONTIER Track  
> Transform verifiable evidence into skill profiles — no keyword stuffing, no college bias.

---

## Problem Statement (TL;DR)

Recruiters drown in identical fresher resumes. **ProofSkill AI** builds a **Proof Card** per candidate:
- 📄 Resume parsing → skills + projects + GitHub
- 🔍 **Deep repo analysis** (authorship, evolution, **tutorial-clone detection**)
- 🎤 **AI Viva** — questions generated from *candidate's own code* (voice-first)
- 📊 Every skill claim = evidence + confidence (0-100)
- ⚖️ **Fair ranking** vs JD — zero college/gender/age/location bias
- 🛤️ **Alternative path** for candidates with no GitHub

---

## Architecture Overview

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Candidate  │────▶│  ProofSkill AI   │────▶│  Recruiter  │
│  (Login)    │     │  (Streamlit)     │     │  (Compare)  │
└─────────────┘     └────────┬─────────┘     └──────┬──────┘
                             │                      │
              ┌──────────────┼──────────────┐       │
              ▼              ▼              ▼       ▼
         ┌─────────┐   ┌──────────┐   ┌─────────┐ ┌────────┐
         │ Resume  │   │ GitHub   │   │  Fine-  │ │ IMATS  │
         │ Parser  │──▶│ Fetcher  │──▶│ tuned   │ │ Sandbox│
         └─────────┘   │ + Analyzer│  │ Model   │ └────────┘
                       └────┬─────┘   └────┬────┘
                            ▼              ▼
                       ┌────────────────────────┐
                       │  Evidence Synthesizer  │
                       │  → Proof Card (JSON)   │
                       └───────────┬────────────┘
                                   ▼
                          ┌─────────────────┐
                          │   Viva Engine   │
                          │  (Voice + Eval) │
                          └────────┬────────┘
                                   ▼
                          ┌─────────────────┐
                          │  Scoring Engine │
                          │  + Fairness     │
                          └─────────────────┘
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- GPU with 8GB+ VRAM (recommended for Whisper + fine-tuned model)
- 20GB free disk space
- API Keys: ElevenLabs, GitHub PAT, IMATS (provided)

### Installation
```bash
# Clone & enter
cd ProofSkillAI

# Create venv
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python src/db/init_db.py

# Run!
streamlit run app.py
```

Open http://localhost:8501

---

## Configuration (`.env`)

```bash
# App
SECRET_KEY=your-random-secret-key-here
DEBUG=true

# Database
DATABASE_URL=sqlite:///data/proofskill.db

# GitHub (PAT with public_repo scope)
GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# ElevenLabs TTS
ELEVENLABS_API_KEY=sk_xxxxxxxxxxxx
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Whisper STT
WHISPER_MODEL=large-v3
WHISPER_DEVICE=cuda

# Fine-tuned Model
MODEL_PATH=models/fine_tuned/
MODEL_DEVICE=cuda

# IMATS Sandbox
IMATS_API_URL=https://sandbox.imats.example.com
IMATS_API_KEY=imatssk_xxxxxxxxxxxx

# Paths
RESUME_DIR=data/resumes
REPO_CACHE_DIR=data/repo_cache
EXPORT_DIR=data/exports
```

---

## Project Structure

```
ProofSkillAI/
├── app.py                    # Streamlit entry point
├── requirements.txt
├── .env.example
├── data/
│   ├── resumes/              # Candidate PDF/DOCX files
│   ├── repo_cache/           # Cloned repos (git cache)
│   └── exports/              # Generated reports
├── models/
│   └── fine_tuned/           # Your model weights here
├── src/
│   ├── config/
│   │   └── settings.py       # Pydantic settings
│   ├── db/
│   │   ├── init_db.py        # Schema initialization
│   │   └── session.py        # DB connection
│   ├── models/
│   │   └── schemas.py        # Pydantic data models
│   ├── services/
│   │   ├── auth.py
│   │   ├── resume_parser.py
│   │   ├── github_fetcher.py
│   │   ├── repo_analyzer.py
│   │   ├── evidence_synthesizer.py
│   │   ├── viva_engine.py
│   │   ├── scoring_engine.py
│   │   ├── imats_client.py
│   │   ├── model_client.py
│   │   └── voice_pipeline.py
│   ├── utils/
│   │   ├── audio.py
│   │   ├── github.py
│   │   └── fairness.py
│   └── db/
│       └── schema.sql        # Extracted from DATABASE_SCHEMA.md
├── pages/                    # Streamlit pages
│   ├── 01_Login.py
│   ├── 02_Candidate_Dashboard.py
│   ├── 03_Viva_Session.py
│   ├── 04_Results.py
│   └── 05_Recruiter_View.py
├── components/               # Reusable UI components
│   ├── audio.py
│   ├── repo_selector.py
│   └── comparison_table.py
├── tests/
│   ├── test_e2e.py
│   └── test_model_prompts.py
└── docs/
    ├── PRD.md
    ├── USER_FLOW.md
    ├── ARCHITECTURE.md
    ├── DATABASE_SCHEMA.md
    ├── PHASES.md
    ├── AI_CONTEXT.md
    └── MEMORY.md
```

---

## Key Features Implemented

| Feature | Status | Location |
|---------|--------|----------|
| Random credential login | ✅ | `src/services/auth.py`, `pages/01_Login.py` |
| Resume parsing (PDF/DOCX) | ✅ | `src/services/resume_parser.py` |
| GitHub repo fetch + selection | ✅ | `src/services/github_fetcher.py`, `components/repo_selector.py` |
| Deep repo analysis (5 analyzers) | ✅ | `src/services/repo_analyzer.py` |
| Tutorial-clone detection | ✅ | `repo_analyzer.py:_detect_tutorial_clone` |
| Evidence synthesis + Proof Card | ✅ | `src/services/evidence_synthesizer.py` |
| AI Viva (voice + text) | ✅ | `src/services/viva_engine.py`, `src/services/voice_pipeline.py` |
| Question generation from code | ✅ | `model_client.py:generate_questions` |
| Response evaluation + confidence | ✅ | `model_client.py:evaluate_response` |
| Multi-param scoring | ✅ | `src/services/scoring_engine.py` |
| Fairness audit (protected attrs) | ✅ | `src/utils/fairness.py` |
| Recruiter side-by-side view | ✅ | `pages/05_Recruiter_View.py` |
| IMATS sandbox integration | ✅ | `src/services/imats_client.py` |

---

## Documentation

| Doc | Description |
|-----|-------------|
| [PRD.md](docs/PRD.md) | Product Requirements Document |
| [USER_FLOW.md](docs/USER_FLOW.md) | Detailed user flows & data flow |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture, components, APIs |
| [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) | SQLite DDL + JSON schemas |
| [PHASES.md](docs/PHASES.md) | 5-day phase breakdown with tasks |
| [AI_CONTEXT.md](docs/AI_CONTEXT.md) | Model integration, prompts, voice config |
| [MEMORY.md](docs/MEMORY.md) | Decision log, constraints, demo script |

---

## Demo Credentials (Pre-generated)

| Candidate | User ID | Password | Profile |
|-----------|---------|----------|---------|
| With GitHub | `CAND-0042` | `xK9mP2qR` | 3 repos, 1 tutorial clone |
| No GitHub | `CAND-0117` | `vL8nB4wT` | Assessment only |
| Non-tech | `CAND-0293` | `pQ3rM7zX` | Business analyst |

---

## Evaluation Checklist (Judging Criteria)

- [ ] **Tutorial-clone detection** validated on labeled sample set
- [ ] **Viva questions** 100% traceable to candidate's own repo/code
- [ ] **Every skill claim** shows evidence + confidence level
- [ ] **Side-by-side comparison** works for 2 candidates vs 1 JD
- [ ] **Alternative evidence path** works (no-GitHub candidate completes flow)
- [ ] **Fairness** — zero feature importance for college/gender/age/location
- [ ] **Recruiter agreement** measurable on held-out shortlist decisions
- [ ] **Candidate understands** their Proof Card (post-session survey)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `sqlite3.OperationalError: database is locked` | Enable WAL mode: `PRAGMA journal_mode=WAL;` |
| `CUDA out of memory` | Use 4-bit GGUF model, reduce `n_ctx` in `.env` |
| `GitHub API 403` | Check `GITHUB_TOKEN` has `public_repo` scope |
| `ElevenLabs quota exceeded` | Fallback to browser TTS (auto-enabled) |
| `Whisper slow` | Set `WHISPER_MODEL=base` for demo |
| Streamlit UI freezes | Ensure model runs in `ThreadPoolExecutor` |

---

## License

Hackathon project — Integraminds IM-105.  
All code & documentation for competition use only.

---

## Team

Built with ❤️ for Deviathon 2.0 by the ProofSkill AI team.

**Stack:** Python • Streamlit • SQLite • llama.cpp • ElevenLabs • Whisper • PyGithub