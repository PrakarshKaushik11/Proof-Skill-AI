# System Architecture
**Project:** ProofSkill AI  
**Version:** 1.0  
**Date:** 2026-10-30  

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STREAMLIT FRONTEND                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Login     │  │  Candidate  │  │   Viva      │  │  Recruiter  │        │
│  │   Page      │  │  Dashboard  │  │   Session   │  │   View      │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND SERVICES (Python)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Auth      │  │  Resume     │  │  GitHub     │  │  Repo       │        │
│  │   Service   │  │  Parser     │  │  Fetcher    │  │  Analyzer   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │               │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐        │
│  │ Evidence    │  │  Viva       │  │  Scoring    │  │  IMATS      │        │
│  │ Synthesizer │  │  Engine     │  │  Engine     │  │  Client     │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  SQLite     │  │  File       │  │  Model      │  │  Cache      │        │
│  │  Database   │  │  Storage    │  │  Weights    │  │  (Redis/    │        │
│  │             │  │  (resumes,  │  │  (fine-     │  │   in-mem)   │        │
│  │             │  │   repos)    │  │   tuned)    │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL APIs                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  GitHub     │  │  ElevenLabs │  │  Whisper    │  │  IMATS      │        │
│  │  API        │  │  TTS        │  │  STT        │  │  Sandbox    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Details

### 2.1 Frontend (Streamlit)
| Module | File | Responsibility |
|--------|------|----------------|
| `app.py` | Entry point, routing, session state |
| `pages/01_Login.py` | Credentials input, validation |
| `pages/02_Candidate_Dashboard.py` | Resume view, repo selection, proof card preview |
| `pages/03_Viva_Session.py` | Voice/text interview UI, real-time feedback |
| `pages/04_Results.py` | Pre/post comparison, gaps, final score |
| `pages/05_Recruiter_View.py` | JD input, ranked list, side-by-side comparison |
| `components/audio.py` | Mic capture, playback, ElevenLabs integration |
| `components/repo_selector.py` | Checkbox grid for repo selection |

### 2.2 Backend Services

#### Auth Service (`src/services/auth.py`)
```python
class AuthService:
    def validate_credentials(user_id: str, password: str) -> Optional[User]
    def create_session(user: User) -> SessionToken
    def verify_token(token: str) -> Optional[User]
    def hash_password(password: str) -> str
    def verify_password(password: str, hash: str) -> bool
```

#### Resume Parser (`src/services/resume_parser.py`)
```python
class ResumeParser:
    def parse(file_path: Path) -> ParsedResume
    def extract_skills(text: str) -> List[Skill]
    def extract_projects(text: str) -> List[Project]
    def extract_github_urls(text: str) -> List[str]
    def normalize_skills(skills: List[str]) -> List[NormalizedSkill]
```

#### GitHub Fetcher (`src/services/github_fetcher.py`)
```python
class GitHubFetcher:
    def __init__(self, token: str, cache: Cache)
    def get_user_repos(username: str) -> List[RepoSummary]
    def get_repo_contents(owner: str, repo: str) -> RepoTree
    def download_repo(owner: str, repo: str, dest: Path) -> Path
    # Rate limit handling, exponential backoff, caching
```

#### Repo Analyzer (`src/services/repo_analyzer.py`)
```python
class RepoAnalyzer:
    def analyze(repo_path: Path) -> RepoAnalysis
    # Parallel analyzers:
    def _analyze_authorship(self, repo_path: Path) -> AuthorshipSignal
    def _analyze_evolution(self, repo_path: Path) -> EvolutionSignal
    def _detect_tutorial_clone(self, repo_path: Path) -> TutorialCloneSignal
    def _assess_code_quality(self, repo_path: Path) -> QualitySignal
    def _map_skills(self, repo_path: Path) -> List[SkillEvidence]
```

#### Evidence Synthesizer (`src/services/evidence_synthesizer.py`)
```python
class EvidenceSynthesizer:
    def synthesize(
        resume_claims: List[Claim],
        repo_evidence: List[RepoAnalysis],
        assessment_scores: Dict[str, float]
    ) -> ProofCard
    def compute_confidence(claim: Claim, evidence: List[Evidence]) -> float
    def flag_tutorial_clones(repo_analyses: List[RepoAnalysis]) -> List[CloneFlag]
```

#### Viva Engine (`src/services/viva_engine.py`)
```python
class VivaEngine:
    def __init__(self, model: FineTunedModel, tts: ElevenLabsClient, stt: WhisperClient)
    def generate_questions(proof_card: ProofCard) -> List[VivaQuestion]
    def evaluate_response(question: VivaQuestion, answer: str) -> Evaluation
    def run_session(proof_card: ProofCard, mode: VoiceMode) -> VivaResult
    # Question types: CODE_WALKTHROUGH, ALTERNATIVE_APPROACH, DEBUG, EXTEND, BEHAVIORAL
```

#### Scoring Engine (`src/services/scoring_engine.py`)
```python
class ScoringEngine:
    def compute_final_score(proof_card: ProofCard, viva_result: VivaResult) -> FinalScore
    def compute_pre_post_comparison(baseline: ProofCard, viva_result: VivaResult) -> Comparison
    def rank_candidates(candidates: List[CandidateScore], jd: JobDescription) -> List[RankedCandidate]
    def generate_reasons(ranked: RankedCandidate) -> List[str]  # Human-readable
    def audit_fairness(ranked: List[RankedCandidate]) -> FairnessReport
```

#### IMATS Client (`src/services/imats_client.py`)
```python
class IMATSClient:
    def push_proof_cards(cards: List[ProofCard]) -> Response
    def push_rankings(rankings: List[RankedCandidate]) -> Response
    def pull_shortlist_decisions(jd_ids: List[str]) -> List[ShortlistDecision]
```

---

## 3. Data Models (Pydantic)

```python
# src/models/schemas.py

class User(BaseModel):
    user_id: str
    password_hash: str
    resume_path: str
    created_at: datetime

class ParsedResume(BaseModel):
    raw_text: str
    skills: List[SkillClaim]
    projects: List[ProjectClaim]
    github_urls: List[str]
    education: List[Education]
    experience: List[Experience]

class SkillClaim(BaseModel):
    name: str
    level: Literal["beginner", "intermediate", "advanced"]
    source: Literal["resume", "assessment", "repo"]
    confidence: float = 0.0

class RepoAnalysis(BaseModel):
    repo_id: str
    name: str
    authorship: AuthorshipSignal
    evolution: EvolutionSignal
    tutorial_clone: TutorialCloneSignal
    quality: QualitySignal
    skill_evidence: List[SkillEvidence]

class ProofCard(BaseModel):
    candidate_id: str
    unified_skills: List[UnifiedSkill]
    tutorial_clone_flags: List[CloneFlag]
    generated_at: datetime

class UnifiedSkill(BaseModel):
    skill: str
    final_confidence: float
    evidence_bundle: List[EvidenceItem]
    gap_notes: Optional[str]

class VivaQuestion(BaseModel):
    id: str
    type: QuestionType
    skill: str
    prompt: str
    context: Dict  # code snippet, repo file, scenario
    expected_signals: List[str]

class VivaResult(BaseModel):
    candidate_id: str
    responses: List[ResponseEvaluation]
    overall_performance: float
    skill_deltas: Dict[str, float]  # pre vs post confidence

class FinalScore(BaseModel):
    candidate_id: str
    evidence_strength: float
    viva_performance: float
    assessment_score: float
    consistency: float
    total: float
    reasons: List[str]

class RankedCandidate(BaseModel):
    candidate_id: str
    score: FinalScore
    rank: int
    comparison_notes: Dict[str, str]  # per skill vs JD
```

---

## 4. Database Schema (SQLite)

See [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) for full DDL.

**Core Tables:**
- `users` — credentials, resume path
- `resumes` — parsed JSON, extracted entities
- `github_links` — URLs from resume
- `selected_repos` — candidate's chosen repos
- `repo_analyses` — full analysis JSON per repo
- `proof_cards` — synthesized evidence + confidence
- `viva_sessions` — questions, responses, evaluations
- `final_scores` — multi-param breakdown
- `recruiter_jds` — job descriptions
- `rankings` — candidate rankings per JD
- `imats_sync` — audit log for IMATS pushes

---

## 5. Configuration (`src/config/settings.py`)

```python
class Settings(BaseSettings):
    # App
    APP_NAME: str = "ProofSkill AI"
    DEBUG: bool = True
    SECRET_KEY: str
    
    # Database
    DATABASE_URL: str = "sqlite:///data/proofskill.db"
    
    # GitHub
    GITHUB_TOKEN: str
    GITHUB_API_BASE: str = "https://api.github.com"
    GITHUB_RATE_LIMIT: int = 5000
    
    # ElevenLabs
    ELEVENLABS_API_KEY: str
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel
    
    # Whisper
    WHISPER_MODEL: str = "large-v3"
    WHISPER_DEVICE: str = "cuda"  # or "cpu"
    
    # Fine-tuned Model
    MODEL_PATH: str = "models/fine_tuned/"
    MODEL_DEVICE: str = "cuda"
    MODEL_MAX_LENGTH: int = 4096
    
    # IMATS
    IMATS_API_URL: str
    IMATS_API_KEY: str
    
    # Fairness
    PROTECTED_ATTRIBUTES: List[str] = ["college", "gender", "age", "location"]
    
    # Paths
    RESUME_DIR: Path = Path("data/resumes")
    REPO_CACHE_DIR: Path = Path("data/repo_cache")
    EXPORT_DIR: Path = Path("data/exports")
    
    class Config:
        env_file = ".env"
```

---

## 6. Security & Privacy

| Measure | Implementation |
|---------|----------------|
| Credentials | bcrypt hash, JWT (HS256, 15min access / 7d refresh) |
| GitHub Token | Read-only, stored in env, never logged |
| PII | Anonymized in dataset; no PII in logs or model inputs |
| Consent | `consent_given` flag checked before any repo fetch |
| Data Retention | Auto-delete repo clones after analysis; keep only JSON results |
| IMATS | Only ProofCard + rankings (no raw resume/repo data) |

---

## 7. Deployment (Hackathon)

```
Local machine (GPU preferred)
├── streamlit run app.py --server.port 8501
├── python -m src.services.model_server  # Optional: separate model inference
└── ngrok http 8501  # For external access if needed
```

**Requirements:**
- Python 3.10+
- GPU with 8GB+ VRAM (for fine-tuned model + Whisper)
- 20GB free disk (repo caches, model weights)
- ElevenLabs API key, GitHub token, IMATS credentials

---

## 8. Observability

| Metric | Tool |
|--------|------|
| Request latency | `time` decorators + Streamlit metrics |
| Model inference time | Custom logging in `FineTunedModel` |
| GitHub API calls | Counter in `GitHubFetcher` |
| Errors | `logging` + Streamlit `st.error` |
| Fairness audit | `FairnessReport` JSON per ranking run |

---

*End of Architecture*