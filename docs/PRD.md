# Product Requirements Document (PRD)
**Project:** ProofSkill AI — IM-105 "Proof Card" System  
**Organization:** Integraminds  
**Theme:** AI FRONTIER  
**Track:** Software  
**Version:** 1.0  
**Date:** 2026-10-30  

---

## 1. Problem Statement (Recap)

Recruiters screening freshers at volume face **thousands of near-identical resumes** — same templates, same keyword stuffing, same tutorial projects (todo app, weather app, Netflix clone). They fall back on **CGPA + college name**, shutting out capable students from smaller colleges.

**Core ask:** Build a **"Proof Card"** that turns *verifiable evidence* into a skill profile:
- Assessment results
- Repository analysis (authorship, evolution, beyond-tutorial detection)
- AI-led project viva (questions generated from candidate's own code)
- Every skill claim carries **evidence + confidence level**
- Recruiter comparison view ranked against JD with human-readable reasons
- Candidate sees actionable gaps to strengthen evidence
- **Alternative evidence path** for students with no public code

---

## 2. Users & Personas

| Persona | Goals | Pain Points |
|---------|-------|-------------|
| **Candidate (Fresher)** | Prove real skills, get fair shot, understand gaps | Resume looks same as everyone; no GitHub = invisible |
| **Recruiter (Volume hiring)** | Shortlist accurately, explain decisions, save time | Keyword-stuffed resumes pass ATS, fail interview; college bias |
| **Platform (IMATS)** | Fair, auditable, explainable rankings | Guardrails: no college/gender/age/location in ranking |

---

## 3. Functional Requirements

### 3.1 Authentication & Onboarding
- **FR-01**: Each candidate gets a unique random `user_id` + `password` (pre-generated from dataset)
- **FR-02**: Login loads candidate's resume + consented data automatically
- **FR-03**: Session management with JWT (short expiry, refresh token)

### 3.2 Resume Ingestion & Parsing
- **FR-04**: Parse resume (PDF/DOCX) → structured JSON
- **FR-05**: Extract: skills, projects, education, experience, GitHub URL(s)
- **FR-06**: Tokenize + keyword extraction (skills + projects separately)
- **FR-07**: Normalize skill names (fuzzy match to taxonomy)

### 3.3 GitHub Integration (Optional Path)
- **FR-08**: If GitHub URL provided → fetch public repos via GitHub API
- **FR-09**: Present repo list → candidate selects which to showcase
- **FR-10**: Deep repo analysis (all files: source + docs + config):
  - Authorship signals (commit history, contribution patterns)
  - Evolution analysis (commits over time, complexity growth)
  - Tutorial-clone detection (pattern matching against known templates)
  - Code quality metrics (structure, testing, docs, originality)
- **FR-11**: If project-level GitHub URL in resume → analyze that specific repo directly
- **FR-12**: No GitHub → skip gracefully, mark "alternative evidence path"

### 3.4 Evidence Synthesis & Proof Card Generation
- **FR-13**: Combine resume claims + repo evidence + assessment scores
- **FR-14**: For each skill claim: evidence bundle + confidence score (0–100)
- **FR-15**: Tutorial-clone flag + explanation per project
- **FR-16**: Output: structured Proof Card (JSON + human-readable)

### 3.5 AI-Led Viva / Simulation
- **FR-17**: Generate questions/tasks/scenarios from **candidate's actual evidence** (not generic bank)
- **FR-18**: Question types by evidence:
  - **With GitHub + code**: Code walkthrough, alternative approaches, "why not X", debug scenarios, extend-feature tasks
  - **No GitHub / Non-tech**: Behavioral/situational (STAR), workplace interaction, problem-solving narratives
- **FR-19**: **Voice-first**: AI speaks (ElevenLabs TTS) → candidate speaks → STT (Whisper) → text log
- **FR-20**: Optional text-input mode for specific question types
- **FR-21**: Real-time evaluation per response → running confidence
- **FR-22**: Pre-interview baseline vs post-interview final per skill

### 3.6 Scoring & Ranking
- **FR-23**: Multi-parameter final score: evidence strength, viva performance, assessment, consistency
- **FR-24**: Recruiter comparison view: side-by-side against JD with **human-readable reasons**
- **FR-25**: **Fairness constraint**: Zero weight to college, gender, age, location in ranking
- **FR-26**: Export recruiter report (PDF/JSON)

### 3.7 IMATS Sandbox Integration
- **FR-27**: Push Proof Cards + rankings to IMATS sandbox API
- **FR-28**: Pull recruiter shortlist decisions (30 JDs, labeled) for evaluation

---

## 4. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| **Privacy** | Candidate consent mandatory before repo analysis; data retention policy |
| **Explainability** | Every ranking decision has human-readable reason |
| **Latency** | Resume parse < 5s; Repo analysis < 30s/repo; Viva turn < 3s |
| **Scalability** | Handle 400 parallel candidates (hackathon scale) |
| **Reliability** | Graceful degradation: no GitHub → alternative path; API failures → retry + fallback |
| **Security** | Encrypted credentials, no PII in logs, GitHub tokens scoped read-only |

---

## 5. Success Criteria (From Problem Statement)

| Criterion | Measurement |
|-----------|-------------|
| Tutorial-clone detection | Precision/Recall on labeled sample set |
| Viva question provenance | 100% questions traceable to candidate's own code/repo |
| Evidence + confidence per claim | Every skill claim has ≥1 evidence item + confidence |
| Side-by-side comparison | Recruiter can compare 2 candidates vs 1 JD |
| Alternative evidence path | Candidates with no GitHub get complete Proof Card |
| Fairness | Zero feature importance for college/gender/age/location |
| Recruiter agreement | Correlation with held-out shortlist decisions |
| Candidate understanding | Post-session survey: "I understand my card" ≥ 80% |

---

## 6. Out of Scope (v1)

- Live video interview
- Multi-language resume parsing (English only)
- Private repo access (public only)
- Candidate-candidate comparison (recruiter view only)
- Mobile app (Streamlit web only)

---

## 7. Assumptions & Dependencies

- Dataset: 400 anonymized profiles (resumes + consented repos + assessments)
- Recruiter labels: 30 JDs with shortlist decisions
- Fine-tuned model provided by team (weights + inference script)
- ElevenLabs API key for TTS
- GitHub API token (rate limit: 5000 req/hr)
- IMATS sandbox API docs + credentials available
- Python 3.10+, Streamlit 1.30+, SQLite 3.35+

---

## 8. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GitHub rate limits | High | Medium | Cache repos, batch requests, exponential backoff |
| Fine-tuned model inference latency | Medium | High | Quantize (GGUF/ONNX), batch inference, GPU |
| Voice STT accuracy (accents) | Medium | Medium | Whisper large-v3, allow text fallback |
| Tutorial-clone false positives | Medium | High | Conservative threshold, human-in-loop review |
| Fairness leakage (proxy features) | Low | Critical | Adversarial debiasing, feature audit |

---

## 9. Timeline / Phases (High-Level)

See [PHASES.md](./PHASES.md) for detailed breakdown.

| Phase | Focus | Duration |
|-------|-------|----------|
| 0 | Setup, docs, schema, config | Day 1 |
| 1 | Auth + Resume Parse + DB | Day 1–2 |
| 2 | GitHub Fetch + Repo Analysis | Day 2–3 |
| 3 | Evidence Synthesis + Proof Card | Day 3 |
| 4 | Viva Engine (Q gen + Voice) | Day 3–4 |
| 5 | Scoring + Ranking + Fairness | Day 4 |
| 6 | Recruiter View + IMATS Integration | Day 4–5 |
| 7 | E2E Testing + Polish + Demo Prep | Day 5 |

---

## 10. Acceptance Checklist

- [ ] All FRs implemented and tested
- [ ] Fairness audit passed (no protected attributes in ranking)
- [ ] Tutorial-clone detector validated on labeled set
- [ ] Viva questions 100% traceable to candidate evidence
- [ ] Recruiter side-by-side view functional
- [ ] IMATS sandbox round-trip works
- [ ] Documentation complete (this PRD + all MD files)
- [ ] Demo script ready (3 candidates, 1 JD, live viva)

---

*End of PRD*