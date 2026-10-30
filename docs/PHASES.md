# Phase Breakdown & Implementation Plan
**Project:** ProofSkill AI  
**Version:** 1.0  
**Date:** 2026-10-30  
**Total Duration:** 5 Days (Hackathon)  

---

## Phase Overview

| Phase | Focus | Days | Key Deliverable |
|-------|-------|------|-----------------|
| **0** | Setup, Config, DB, Docs | 0.5 | Running repo, schema, config |
| **1** | Auth + Resume Parse + Candidate Dashboard | 1.0 | Login → Parsed Resume UI |
| **2** | GitHub Fetch + Repo Analysis | 1.5 | Repo selection → Analysis JSON |
| **3** | Evidence Synthesis + Proof Card | 0.5 | Complete Proof Card per candidate |
| **4** | Viva Engine (Q Gen + Voice + Eval) | 1.5 | Working voice interview |
| **5** | Scoring + Ranking + Fairness | 0.5 | Ranked list with reasons |
| **6** | Recruiter View + IMATS Integration | 0.5 | Side-by-side + API push |
| **7** | E2E Testing + Polish + Demo | 0.5 | Demo-ready, docs complete |

---

## Phase 0: Foundation (Half Day)

### Goals
- [ ] Repository structure created
- [ ] Virtual env + dependencies installed
- [ ] SQLite schema applied
- [ ] Config system (`.env`, `settings.py`)
- [ ] All documentation files written
- [ ] Basic Streamlit app skeleton with routing

### Tasks
```bash
# 0.1 Create venv & install
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 0.2 Init DB
python src/db/init_db.py

# 0.3 Verify config loads
python -c "from src.config.settings import settings; print(settings.APP_NAME)"

# 0.4 Run empty Streamlit
streamlit run app.py
```

### Files to Create
```
src/
├── config/
│   ├── __init__.py
│   └── settings.py          # Pydantic Settings (see ARCHITECTURE.md)
├── db/
│   ├── __init__.py
│   ├── init_db.py           # Runs DDL from schema.sql
│   └── session.py           # SQLAlchemy / sqlite3 connection pool
├── models/
│   ├── __init__.py
│   └── schemas.py           # Pydantic models (see ARCHITECTURE.md)
├── services/
│   ├── __init__.py
│   ├── auth.py
│   ├── resume_parser.py
│   ├── github_fetcher.py
│   ├── repo_analyzer.py
│   ├── evidence_synthesizer.py
│   ├── viva_engine.py
│   ├── scoring_engine.py
│   └── imats_client.py
├── utils/
│   ├── __init__.py
│   ├── audio.py             # Mic capture, playback
│   ├── github.py            # GitHub API helpers
│   └── fairness.py          # Fairness audit utilities
app.py                       # Streamlit entry + page config
pages/
├── 01_Login.py
├── 02_Candidate_Dashboard.py
├── 03_Viva_Session.py
├── 04_Results.py
└── 05_Recruiter_View.py
components/
├── __init__.py
├── audio.py                 # Streamlit audio components
├── repo_selector.py
└── comparison_table.py
```

### Dependencies (`requirements.txt`)
```txt
# Core
streamlit>=1.30
pydantic>=2.5
pydantic-settings>=2.1
python-dotenv>=1.0

# Database
sqlalchemy>=2.0
alembic>=1.13

# Resume parsing
pdfplumber>=0.10
python-docx>=1.1
spacy>=3.7
# python -m spacy download en_core_web_sm

# GitHub
PyGithub>=2.1
httpx>=0.25

# Audio / Voice
elevenlabs>=0.3
openai-whisper>=20231117
pyaudio>=0.2.14
numpy>=1.26
soundfile>=0.12

# ML / Model
torch>=2.1
transformers>=4.36
accelerate>=0.25
# For fine-tuned model loading

# IMATS / HTTP
httpx>=0.25

# Utilities
tqdm>=4.66
rich>=13.7
pytest>=7.4
pytest-asyncio>=0.23
```

---

## Phase 1: Auth + Resume Parse + Dashboard (Day 1)

### 1.1 Auth Service (`src/services/auth.py`)
```python
# Implement:
# - validate_credentials(user_id, password) -> User | None
# - create_session(user) -> token
# - verify_token(token) -> User | None
# - Password hashing with bcrypt
# - JWT tokens (access 15min, refresh 7d)
```

### 1.2 Resume Parser (`src/services/resume_parser.py`)
```python
# Implement:
# - parse(file_path) -> ParsedResume
#   - pdfplumber for PDF, python-docx for DOCX
# - extract_skills(text) -> List[SkillClaim]
#   - spaCy NER + keyword matching against skill taxonomy
# - extract_projects(text) -> List[ProjectClaim]
#   - Section detection + regex for project blocks
# - extract_github_urls(text) -> List[str]
#   - Regex for github.com/...
# - normalize_skills(skills) -> List[NormalizedSkill]
#   - Fuzzy match to canonical skill list (taxonomy.json)
```

### 1.3 Login Page (`pages/01_Login.py`)
```python
# UI:
# - user_id input (text)
# - password input (password)
# - "Login" button → calls AuthService.validate_credentials
# - On success: store user in st.session_state, redirect to dashboard
# - Error handling: invalid creds, missing resume file
```

### 1.4 Candidate Dashboard (`pages/02_Candidate_Dashboard.py`)
```python
# UI Sections:
# 1. Resume Preview (parsed skills, projects, education)
# 2. GitHub Links Found (from resume)
# 3. If GitHub profile URL: "Fetch Repos" button → calls GitHubFetcher
# 4. Repo Selector Component (checkbox grid) → saves to selected_repos
# 5. "Analyze Selected Repos" button → triggers RepoAnalyzer (Phase 2)
# 6. "Generate Proof Card" button (enabled after analysis) → Phase 3
```

### 1.5 Database Integration
- Wire `AuthService` to `users` table
- Wire `ResumeParser` to `resumes` + `github_links` tables
- Wire repo selection to `selected_repos` table

### Acceptance Criteria
- [ ] Login works with pre-generated credentials
- [ ] Resume parses correctly (skills, projects, GitHub URLs)
- [ ] Dashboard shows parsed data cleanly
- [ ] GitHub profile fetch returns public repos
- [ ] Candidate can select repos → saved to DB

---

## Phase 2: GitHub Fetch + Repo Analysis (Day 2–3)

### 2.1 GitHub Fetcher (`src/services/github_fetcher.py`)
```python
class GitHubFetcher:
    def __init__(self, token: str, cache_dir: Path):
        self.client = Github(token)
        self.cache = Cache(cache_dir)
    
    def get_user_repos(self, username: str) -> List[RepoSummary]:
        # Cache 24h, handle rate limits
    
    def download_repo(self, owner: str, repo: str, dest: Path) -> Path:
        # git clone --depth=1 --filter=blob:none
        # Skip if cached and not stale
    
    def get_repo_tree(self, owner: str, repo: str) -> RepoTree:
        # For file listing without full clone
```

### 2.2 Repo Analyzer (`src/services/repo_analyzer.py`)
**Parallel Analyzers (run concurrently with ThreadPoolExecutor):**

```python
class RepoAnalyzer:
    def analyze(self, repo_path: Path) -> RepoAnalysis:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                'authorship': executor.submit(self._analyze_authorship, repo_path),
                'evolution': executor.submit(self._analyze_evolution, repo_path),
                'tutorial_clone': executor.submit(self._detect_tutorial_clone, repo_path),
                'quality': executor.submit(self._assess_code_quality, repo_path),
                'skills': executor.submit(self._map_skills, repo_path),
            }
            return RepoAnalysis(**{k: f.result() for k, f in futures.items()})
```

#### 2.2.1 Authorship Analysis
- `git log --format="%ae %an"` → map emails to candidate
- Primary author % = candidate_commits / total_commits
- Commit frequency, time distribution

#### 2.2.2 Evolution Analysis
- `git log --numstat` → LOC added/deleted over time
- Complexity: cyclomatic (radon), cognitive
- Feature addition vs bug fix ratio

#### 2.2.3 Tutorial-Clone Detection (**Critical**)
```python
# Fingerprint known templates:
TEMPLATE_FINGERPRINTS = {
    "create-react-app": {
        "files": ["public/index.html", "src/App.js", "src/index.js"],
        "patterns": ["react-scripts", "testing-library/react"],
        "structure_hash": "abc123..."
    },
    "nextjs-starter": {...},
    "django-tutorial": {...},
    "spring-boot-initializr": {...},
    "express-generator": {...},
    # Add more from labeled dataset
}

def _detect_tutorial_clone(self, repo_path: Path) -> TutorialCloneSignal:
    # 1. Check package.json / requirements.txt for template deps
    # 2. Compare file structure hash
    # 3. AST similarity to template (tree-sitter)
    # 4. Commit history: single initial commit + few changes = suspicious
    # 5. Return score 0-1, is_clone bool, clone_type, confidence
```

#### 2.2.4 Code Quality
- Test coverage (pytest --coverage / jest --coverage)
- Lint score (ruff, eslint)
- Doc coverage (docstrings, README quality)
- Type hints (Python), TypeScript strictness

#### 2.2.5 Skill Mapping
- Parse imports, dependencies, config files
- Map to skill taxonomy: `fastapi` → "FastAPI", `pytest` → "Testing"
- Evidence: file paths, usage patterns

### 2.3 Analysis Trigger & Progress UI
- Dashboard: "Analyze Selected Repos" → background task with progress bar
- Store results in `repo_analyses` table
- Show summary per repo: clone flag, quality, top skills

### Acceptance Criteria
- [ ] Fetches repos from GitHub API (cached, rate-limited)
- [ ] Clones/analyzes repos in <30s each
- [ ] Tutorial-clone detector works on labeled samples
- [ ] All 5 analyzers produce structured JSON
- [ ] Results stored in DB, visible on dashboard

---

## Phase 3: Evidence Synthesis + Proof Card (Day 3)

### 3.1 Evidence Synthesizer (`src/services/evidence_synthesizer.py`)
```python
class EvidenceSynthesizer:
    def synthesize(
        self,
        resume_claims: List[SkillClaim],
        repo_analyses: List[RepoAnalysis],
        assessment_scores: Dict[str, float]
    ) -> ProofCard:
        # 1. Collect all skills from all sources
        # 2. For each skill, gather evidence items
        # 3. Compute confidence per skill (weighted)
        # 4. Flag tutorial clones
        # 5. Generate gap notes
```

**Confidence Formula:**
```
confidence = 
  0.50 * repo_evidence_strength +
  0.30 * assessment_score_normalized +
  0.15 * resume_claim_strength +
  0.05 * viva_baseline (0 initially)
```

**Evidence Weights by Source:**
| Source | Weight | Max Confidence Contribution |
|--------|--------|----------------------------|
| Repo (primary author, complex) | 0.60 | 60 |
| Repo (contributor) | 0.35 | 35 |
| Assessment | 0.30 | 30 |
| Resume claim | 0.10 | 10 |

### 3.2 Alternative Evidence Path (No GitHub)
```python
def synthesize_no_github(
    self,
    resume_claims: List[SkillClaim],
    assessment_scores: Dict[str, float]
) -> ProofCard:
    # Higher weight to assessment (0.60)
    # NLP on resume project descriptions for specificity
    # Mark skills as "needs_verification"
    # Viva will carry more weight later
```

### 3.3 Proof Card UI (`pages/02_Candidate_Dashboard.py` → new tab)
- Render unified skills with confidence bars
- Show evidence bundle per skill (expandable)
- Tutorial clone warnings prominent
- Gap notes actionable
- "Start Viva" button → navigates to Phase 4

### Acceptance Criteria
- [ ] Every skill has confidence 0-100 + evidence list
- [ ] Tutorial clones flagged with explanation
- [ ] No-GitHub path produces valid Proof Card
- [ ] JSON output matches schema
- [ ] UI renders clearly

---

## Phase 4: Viva Engine (Day 3–4) — **Most Complex**

### 4.1 Fine-Tuned Model Integration
```python
# src/services/model_client.py
class FineTunedModel:
    def __init__(self, model_path: str, device: str):
        # Load tokenizer + model (GGUF/ONNX preferred for speed)
        # Implement generate(prompt, max_tokens, temperature)
    
    def generate_questions(self, proof_card: ProofCard) -> List[VivaQuestion]:
        # Prompt template includes:
        # - Unified skills with evidence
        # - Repo analysis details (code snippets, clone flags)
        # - Question type distribution
        # Output: structured JSON list
    
    def evaluate_response(self, question: VivaQuestion, answer: str) -> ResponseEvaluation:
        # Prompt: question + answer + expected signals
        # Output: score 0-1, feedback, confidence_delta, signals_matched
```

### 4.2 Question Generation Strategy
```python
def generate_questions(proof_card: ProofCard) -> List[VivaQuestion]:
    questions = []
    
    for skill in proof_card.unified_skills:
        evidence = skill.evidence_bundle
        
        # Has repo evidence → technical questions
        if any(e.type == "repo" for e in evidence):
            repo_evidence = [e for e in evidence if e.type == "repo"]
            for repo in repo_evidence:
                questions.extend([
                    code_walkthrough(skill, repo),
                    alternative_approach(skill, repo),
                    debug_scenario(skill, repo),
                    extend_feature(skill, repo),
                ])
        
        # Has assessment only → knowledge questions
        elif any(e.type == "assessment" for e in evidence):
            questions.append(knowledge_check(skill))
        
        # Resume only → behavioral / situational
        else:
            questions.append(behavioral_scenario(skill))
    
    # Add 2-3 general behavioral questions
    questions.extend(general_behavioral())
    
    # Shuffle, limit to 8-12 questions
    return select_balanced(questions, max_count=10)
```

### 4.3 Voice Pipeline
```python
# src/services/voice_pipeline.py
class VoicePipeline:
    def __init__(self, elevenlabs_key: str, whisper_model: str, device: str):
        self.tts = ElevenLabsClient(elevenlabs_key)
        self.stt = WhisperModel(whisper_model, device)
    
    async def speak(self, text: str) -> bytes:
        return await self.tts.text_to_speech(text, voice_id=settings.ELEVENLABS_VOICE_ID)
    
    def transcribe(self, audio_path: Path) -> str:
        return self.stt.transcribe(audio_path).text
```

### 4.4 Viva Session Page (`pages/03_Viva_Session.py`)
**State Machine:**
```
INIT → INTRO_SPEAKING → QUESTION_SPEAKING → LISTENING → TRANSCRIBING 
  → EVALUATING → FEEDBACK_SHOWING → NEXT_QUESTION → ... → WRAP_UP
```

**UI Components:**
- Audio playback (AI question)
- Mic recorder (candidate answer) — WebRTC via `streamlit-webrtc` or `st.audio_input`
- Text fallback input (always visible)
- Real-time status: "AI is speaking...", "Listening...", "Evaluating..."
- Progress: "Question 3 of 10"
- Live confidence meter per skill

### 4.5 Evaluation & Confidence Update
```python
# After each response:
evaluation = model.evaluate_response(question, answer)
skill = question.skill
delta = evaluation.confidence_delta  # e.g., +5, -3
proof_card.unified_skills[skill].final_confidence += delta
proof_card.unified_skills[skill].evidence_bundle.append(
    EvidenceItem(type="viva", detail=answer, weight=0.2, confidence=evaluation.score)
)
# Persist updated proof_card to DB
```

### Acceptance Criteria
- [ ] Model loads, generates questions from Proof Card
- [ ] Questions reference specific code/repo details
- [ ] TTS plays audio, STT transcribes accurately
- [ ] Text fallback works
- [ ] Each response evaluated, confidence updated
- [ ] Session completes → VivaResult stored

---

## Phase 5: Scoring + Ranking + Fairness (Day 4)

### 5.1 Scoring Engine (`src/services/scoring_engine.py`)
```python
class ScoringEngine:
    WEIGHTS = {
        "evidence_strength": 0.35,
        "viva_performance": 0.35,
        "assessment": 0.20,
        "consistency": 0.10,
    }
    
    def compute_final_score(self, proof_card: ProofCard, viva_result: VivaResult) -> FinalScore:
        # Component scores 0-100
        evidence = proof_card.overall_confidence
        viva = viva_result.overall_performance * 100
        assessment = mean(proof_card.assessment_scores.values()) * 100 if proof_card.assessment_scores else 50
        consistency = self._compute_consistency(proof_card, viva_result)
        
        total = sum(
            self.WEIGHTS[k] * v for k, v in {
                "evidence_strength": evidence,
                "viva_performance": viva,
                "assessment": assessment,
                "consistency": consistency
            }.items()
        )
        
        return FinalScore(
            evidence_strength=evidence,
            viva_performance=viva,
            assessment=assessment,
            consistency=consistency,
            total=total,
            reasons=self._generate_reasons(proof_card, viva_result),
            skill_scores=self._per_skill_scores(proof_card, viva_result),
            pre_viva_confidence={s.skill: s.final_confidence for s in proof_card.unified_skills},
            post_viva_confidence={...}  # after viva deltas
        )
    
    def _compute_consistency(self, card: ProofCard, viva: VivaResult) -> float:
        # Correlation between claimed vs demonstrated
        # High if viva confirms repo evidence
        # Low if viva contradicts or resume-only claims fail
```

### 5.2 Ranking Against JD
```python
def rank_candidates(candidates: List[CandidateScore], jd: JobDescription) -> List[RankedCandidate]:
    # For each candidate, compute match per required/preferred skill
    # Weight by JD importance
    # Sort by weighted match * final_score
    # Generate per-skill comparison + human-readable reasons
```

### 5.3 Fairness Audit (`src/utils/fairness.py`)
```python
def audit_fairness(ranked: List[RankedCandidate], users: List[User]) -> FairnessReport:
    # 1. Ensure protected attributes NOT in ranking features
    # 2. Check disparate impact by college tier, gender, etc.
    # 3. Proxy detection (e.g., college → proxy for resources)
    # 4. Return report with pass/fail + details
    
    # Hard constraint: if any protected attribute has |correlation| > 0.1 with rank → FAIL
```

### 5.4 Results Page (`pages/04_Results.py`)
- Pre vs Post confidence comparison (bar chart)
- Final score breakdown (radar chart)
- Skill-by-skill detail
- Actionable gaps for candidate
- "Export Report" button

### Acceptance Criteria
- [ ] Final score computed with all 4 components
- [ ] Ranking works for 30 JDs
- [ ] Human-readable reasons per rank
- [ ] Fairness audit passes (zero protected attribute influence)
- [ ] Results UI clear for candidate

---

## Phase 6: Recruiter View + IMATS (Day 4–5)

### 6.1 Recruiter View (`pages/05_Recruiter_View.py`)
```python
# UI:
# 1. JD Selector (dropdown of 30 JDs)
# 2. Ranked Candidate Table (name hidden, ID only, score, key skills)
# 3. "Compare" checkboxes → select 2 → Side-by-Side View
# 4. Side-by-Side:
#    - Skill columns with confidence bars
#    - Evidence summary per skill
#    - Viva performance per skill
#    - Rank reasons
# 5. "Shortlist" / "Reject" buttons with notes
# 6. "Push to IMATS" button
```

### 6.2 IMATS Client (`src/services/imats_client.py`)
```python
class IMATSClient:
    def __init__(self, base_url: str, api_key: str):
        self.client = httpx.AsyncClient(base_url=base_url, headers={"Authorization": f"Bearer {api_key}"})
    
    async def push_proof_cards(self, cards: List[ProofCard]) -> Response:
        # POST /api/v1/proof-cards/batch
    
    async def push_rankings(self, rankings: List[RankedCandidate]) -> Response:
        # POST /api/v1/rankings/batch
    
    async def pull_shortlist_decisions(self, jd_ids: List[str]) -> List[ShortlistDecision]:
        # GET /api/v1/shortlist-decisions?jd_ids=...
```

### 6.3 Sync UI
- "Sync All to IMATS" button on recruiter view
- Progress + result log
- Audit trail in `imats_sync` table

### Acceptance Criteria
- [ ] Recruiter sees ranked list per JD
- [ ] Side-by-side comparison works
- [ ] Rank reasons visible and accurate
- [ ] IMATS push succeeds (proof cards + rankings)
- [ ] IMATS pull retrieves shortlist decisions

---

## Phase 7: E2E Testing + Polish + Demo (Day 5)

### 7.1 End-to-End Test Script
```python
# tests/test_e2e.py
def test_full_flow():
    # 1. Login as candidate
    # 2. Verify resume parsed
    # 3. Select repos (if any)
    # 4. Run analysis
    # 5. Generate proof card
    # 6. Run viva (mock voice)
    # 7. Get final score
    # 8. Login as recruiter
    # 9. View ranking for JD
    # 10. Compare two candidates
    # 11. Push to IMATS (mock)
    assert all_steps_pass
```

### 7.2 Test on Labeled Dataset
- Run tutorial-clone detector on 400 profiles → measure precision/recall
- Run viva on subset → verify questions trace to candidate code
- Compare rankings vs recruiter shortlist → compute agreement

### 7.3 Demo Prep
- 3 candidate personas ready (with GitHub, without, non-tech)
- 1 JD for live demo
- Scripted flow: Login → Dashboard → Viva (2 mins) → Results → Recruiter View
- Backup: recorded video if live voice fails

### 7.4 Documentation Finalization
- [ ] All MD files complete
- [ ] README.md with run instructions
- [ ] Architecture diagram (Mermaid → PNG)
- [ ] API docs (if any)

### Acceptance Criteria
- [ ] Full flow works for 3+ candidates
- [ ] Tutorial-clone detection validated
- [ ] Viva questions 100% traceable
- [ ] Fairness audit passes
- [ ] IMATS round-trip works
- [ ] Demo runs smoothly

---

## Daily Schedule (5 Days)

| Time | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 |
|------|-------|-------|-------|-------|-------|
| 9-12 | Phase 0, 1.1-1.3 | Phase 2.1-2.2 | Phase 3, 4.1 | Phase 5 | Phase 7 |
| 12-1 | Lunch | Lunch | Lunch | Lunch | Lunch |
| 1-5 | Phase 1.4-1.5 | Phase 2.2-2.3 | Phase 4.2-4.5 | Phase 6 | Demo + Polish |
| 5-7 | Buffer / Bugfix | Buffer / Bugfix | Buffer / Bugfix | Buffer / Bugfix | Submit |

---

## Risk Buffer Allocation

| Risk | Buffer Time | Mitigation |
|------|-------------|------------|
| Fine-tuned model loading issues | 4 hrs | Have ONNX/GGUF fallback; CPU inference |
| Whisper STT accuracy | 2 hrs | Allow text-only mode; pre-record answers |
| GitHub rate limits | 1 hr | Aggressive caching; mock data for demo |
| Tutorial-clone false positives | 3 hrs | Conservative threshold; manual override UI |
| IMATS API changes | 2 hrs | Mock client for demo; flexible payload |

---

## Team Parallelization (if multiple people)

| Person | Primary | Secondary |
|--------|---------|-----------|
| Backend 1 | Phase 1, 2, 3 | Phase 5 |
| Backend 2 | Phase 4 (Viva + Voice) | Phase 6 |
| Frontend | All Streamlit pages | Components, UX polish |
| ML/Quality | Tutorial-clone detector | Fairness audit, evaluation |

---

*End of Phases*