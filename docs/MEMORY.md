# Project Memory & Decision Log
**Project:** ProofSkill AI  
**Version:** 1.0  
**Date:** 2026-10-30  
**Purpose:** Track key decisions, rationale, and context for future reference / handoff

---

## 1. Key Architectural Decisions

| Date | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|------------------------|
| 2026-10-30 | Streamlit for frontend | Rapid prototyping, built-in components, Python-native | React/Next.js (too slow for hackathon), Gradio (less flexible) |
| 2026-10-30 | SQLite for database | Zero-config, file-based, sufficient for 400 users, portable | PostgreSQL (overkill), DuckDB (less familiar) |
| 2026-10-30 | ElevenLabs for TTS | Best quality, low latency, generous free tier | OpenAI TTS (good but newer), Coqui TTS (local but lower quality) |
| 2026-10-30 | Whisper large-v3 for STT | Best accuracy for accents, runs locally | Deepgram API (cost), Vosk (lower accuracy) |
| 2026-10-30 | Fine-tuned model in-process (llama.cpp) | No network overhead, works offline, GGUF quantization | vLLM server (more complex), API fallback |
| 2026-10-30 | Random user_id/password per candidate | Matches dataset structure, no auth complexity | OAuth, magic links (unnecessary) |
| 2026-10-30 | Tutorial-clone detection via fingerprints + AST | Deterministic, explainable, no ML needed | Pure ML classifier (needs training data) |

---

## 2. Dataset & Data Handling

### 2.1 Dataset Structure (400 profiles)
```
data/
├── profiles/
│   ├── CAND-0001/
│   │   ├── resume.pdf
│   │   ├── assessment.json
│   │   └── consent.txt
│   └── ...
├── recruiter_labels/
│   ├── JD-001_shortlist.json
│   └── ...
└── skill_taxonomy.json
```

### 2.2 Pre-generated Credentials
- `user_id`: `CAND-{0001..0400}`
- `password`: 12-char random alphanumeric (stored bcrypt-hashed)
- Stored in `users` table at init

### 2.3 Consent Management
- `consent_given` column in `users` table
- Checked before ANY GitHub API call
- UI shows consent status on dashboard

---

## 3. Fairness Implementation Details

### 3.1 Protected Attributes (NEVER used in ranking)
```python
PROTECTED_ATTRIBUTES = [
    "college_name",
    "college_tier", 
    "gender",
    "age",
    "location",
    "caste_category",  # if present
    "disability_status"
]
```

### 3.2 Proxy Detection
- Monitor feature importance for: `resume_template_hash`, `github_username_pattern`, `project_names`
- If any correlate >0.3 with protected attribute → audit

### 3.3 Fairness Audit Checklist (per ranking run)
- [ ] No protected attribute in feature set
- [ ] Disparate impact ratio > 0.8 for all groups
- [ ] No proxy features with high importance
- [ ] Ranking correlation with college tier ≈ 0
- [ ] Report saved to `imats_sync` + `rankings.fairness_audit_json`

---

## 4. GitHub API Strategy

### 4.1 Rate Limit Management
- **Limit**: 5000 req/hr per token
- **Cache**: 24h TTL for repo list, 7d for repo contents
- **Batch**: Fetch all selected repos in parallel (max 5 concurrent)
- **Backoff**: Exponential (1s, 2s, 4s, 8s, max 60s)

### 4.2 Repo Selection UX
- Show: name, description, stars, language, last updated
- Default: select all non-fork, non-archived, updated < 2 years
- Max 5 repos per candidate (analysis time constraint)

### 4.3 Analysis Scope
- **Include**: Source files (<1MB each), config, docs, tests, README
- **Exclude**: `node_modules`, `venv`, `__pycache__`, `.git`, `dist`, `build`, `target`, `vendor`, `*.lock`, `*.min.js`, images, fonts
- **Max repo size**: 500MB (skip larger with warning)

---

## 5. Viva Session Design

### 5.1 Question Distribution (10 questions total)
| Type | Count | When Used |
|------|-------|-----------|
| CODE_WALKTHROUGH | 3 | Has repo evidence |
| ALTERNATIVE_APPROACH | 2 | Has repo evidence |
| DEBUG | 1 | Has repo evidence |
| EXTEND_FEATURE | 1 | Has repo evidence |
| BEHAVIORAL | 2 | Always (soft skills) |
| KNOWLEDGE_CHECK | 1 | Only assessment evidence |

### 5.2 Session Timing
- Intro: 30s
- Per question: 2-3 min (AI speak + candidate answer + eval)
- Total: ~25 min max
- Auto-timeout: 60s per answer (configurable)

### 5.3 Confidence Delta Calibration
| Evaluation Score | Delta |
|------------------|-------|
| 0.9 - 1.0 | +8 to +10 |
| 0.7 - 0.89 | +4 to +7 |
| 0.5 - 0.69 | 0 to +3 |
| 0.3 - 0.49 | -3 to -1 |
| 0.0 - 0.29 | -8 to -4 |

---

## 6. Scoring Weights (Tunable)

```python
SCORING_WEIGHTS = {
    "evidence_strength": 0.35,    # Proof Card confidence
    "viva_performance": 0.35,     # Avg response quality
    "assessment": 0.20,           # External test scores
    "consistency": 0.10,          # Cross-source alignment
}
```

**Rationale:**
- Evidence + Viva = 70% (direct demonstration)
- Assessment = 20% (standardized baseline)
- Consistency = 10% (integrity check)

**No-GitHub Adjustment:**
```python
NO_GITHUB_WEIGHTS = {
    "evidence_strength": 0.20,    # Lower (resume + assessment only)
    "viva_performance": 0.50,     # Higher (viva carries burden)
    "assessment": 0.25,           # Higher
    "consistency": 0.05,
}
```

---

## 7. IMATS Integration Points

### 7.1 API Contract (Assumed)
```json
// POST /api/v1/proof-cards/batch
{
  "proof_cards": [
    {
      "candidate_id": "CAND-0001",
      "unified_skills": [...],
      "tutorial_clone_flags": [...],
      "generated_at": "2026-10-30T10:00:00Z"
    }
  ]
}

// POST /api/v1/rankings/batch
{
  "jd_id": "JD-001",
  "rankings": [
    {"candidate_id": "CAND-0001", "rank": 1, "score": 87.5, "reasons": [...]}
  ]
}
```

### 7.2 Sync Triggers
- Manual "Push to IMATS" button (recruiter view)
- Auto-sync after each ranking computation (optional)
- Audit log in `imats_sync` table

---

## 8. Known Constraints & Workarounds

| Constraint | Workaround |
|------------|------------|
| No GPU on demo machine | Pre-quantize model to 4-bit GGUF; test CPU inference |
| Whisper slow on CPU | Use `base` model for demo; `large-v3` for evaluation |
| GitHub rate limit during demo | Pre-fetch & cache all 400 profiles' repos night before |
| Fine-tuned model not ready | Mock model client returning predefined questions |
| ElevenLabs quota exceeded | Fallback to browser `speechSynthesis` |
| Streamlit single-threaded | Run model in `ThreadPoolExecutor`; use `st.spinner` |

---

## 9. Demo Script (5 Minutes)

### 9.1 Candidate Flow (2 min)
1. **Login** → "CAND-0042" / "xK9mP2qR" (has GitHub)
2. **Dashboard** → Show parsed resume, 3 GitHub repos found
3. **Select Repos** → Pick 2, click "Analyze"
4. **Proof Card** → Show skills with confidence, 1 tutorial clone flagged
5. **Start Viva** → Voice mode

### 9.2 Viva Demo (2 min)
1. **Q1**: Code walkthrough (AI speaks, candidate answers)
2. **Q2**: Alternative approach (shows code snippet)
3. **Live confidence update** visible
4. **Wrap up** → Results page

### 9.3 Recruiter View (1 min)
1. **Select JD** → "JD-005: Backend Engineer"
2. **Ranked list** → Top 5 shown
3. **Compare** → CAND-0042 vs CAND-0017 side-by-side
4. **Reasons** → Human-readable explanations
5. **Push to IMATS** → Success toast

---

## 10. File Ownership & Contacts

| Area | Owner | Contact |
|------|-------|---------|
| Auth + Resume Parse | Backend 1 | - |
| GitHub + Repo Analysis | Backend 1 | - |
| Evidence + Proof Card | Backend 1 | - |
| Viva Engine + Voice | Backend 2 | - |
| Scoring + Fairness | Backend 2 | - |
| Recruiter View + IMATS | Backend 2 | - |
| Streamlit UI | Frontend | - |
| Model Integration | ML Lead | - |
| Tutorial-Clone Detector | ML Lead | - |

---

## 11. Post-Hackathon Roadmap

| Priority | Item |
|----------|------|
| P0 | Production hardening (auth, rate limits, monitoring) |
| P0 | Private repo support (GitHub App + installation) |
| P1 | Multi-language resume parsing |
| P1 | Candidate portal (track progress over time) |
| P1 | Recruiter dashboard (analytics, bias reports) |
| P2 | Video viva (with avatar) |
| P2 | Integration with ATS (Greenhouse, Lever) |
| P3 | Mobile app |
| P3 | Team collaboration features |

---

## 12. Troubleshooting Quick Reference

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| "Model not found" | Wrong path in `.env` | Check `MODEL_PATH` |
| "CUDA OOM" | Model too large | Use 4-bit GGUF, reduce `n_ctx` |
| "GitHub 403" | Token invalid/expired | Regenerate PAT with `public_repo` scope |
| "ElevenLabs 401" | API key wrong | Check `ELEVENLABS_API_KEY` |
| "Whisper slow" | Running on CPU | Ensure `WHISPER_DEVICE=cuda` |
| "Streamlit froze" | Model blocking main thread | Use `ThreadPoolExecutor` |
| "DB locked" | Concurrent writes | Use connection pool, WAL mode |
| "Fairness audit fails" | Proxy feature leaking | Check feature importance, remove |

---

*End of Memory Log — Update as decisions evolve*