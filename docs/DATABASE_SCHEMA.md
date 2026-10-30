# Database Schema (SQLite)
**Project:** ProofSkill AI  
**Version:** 1.0  
**Date:** 2026-10-30  

---

## 1. ER Diagram (Text)

```
users ──────< resumes >──────< github_links
  │              │
  │              ├────< selected_repos >──── repo_analyses
  │              │
  │              └────< proof_cards >──────< viva_sessions >──── final_scores
  │                                                    │
  └────────────────────────────────────────────────────┘
                              │
                              ▼
                       recruiter_jds ────< rankings
                              │
                              ▼
                        imats_sync
```

---

## 2. DDL Statements

```sql
-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- ============================================================
-- USERS & AUTH
-- ============================================================
CREATE TABLE users (
    user_id       TEXT PRIMARY KEY,           -- e.g., "CAND-0001"
    password_hash TEXT NOT NULL,              -- bcrypt
    resume_path   TEXT NOT NULL,              -- relative to data/resumes/
    consent_given INTEGER NOT NULL DEFAULT 0, -- 1 = consent for repo analysis
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_resume_path ON users(resume_path);

-- ============================================================
-- PARSED RESUME DATA
-- ============================================================
CREATE TABLE resumes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    raw_text      TEXT NOT NULL,              -- full extracted text
    parsed_json   TEXT NOT NULL,              -- full ParsedResume JSON
    skills_json   TEXT NOT NULL,              -- List[SkillClaim] JSON
    projects_json TEXT NOT NULL,              -- List[ProjectClaim] JSON
    education_json TEXT NOT NULL,             -- List[Education] JSON
    experience_json TEXT NOT NULL,            -- List[Experience] JSON
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_resumes_user_id ON resumes(user_id);

-- ============================================================
-- GITHUB LINKS EXTRACTED FROM RESUME
-- ============================================================
CREATE TABLE github_links (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    url         TEXT NOT NULL,                -- full GitHub URL
    link_type   TEXT NOT NULL,                -- 'profile', 'project', 'repo'
    extracted_from TEXT NOT NULL,             -- 'skills', 'projects', 'contact'
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_github_links_user_id ON github_links(user_id);

-- ============================================================
-- CANDIDATE-SELECTED REPOS (from profile fetch)
-- ============================================================
CREATE TABLE selected_repos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    github_url_id INTEGER REFERENCES github_links(id) ON DELETE SET NULL,
    owner         TEXT NOT NULL,              -- GitHub username/org
    repo_name     TEXT NOT NULL,
    repo_full_name TEXT NOT NULL,             -- owner/repo_name
    description   TEXT,
    stars         INTEGER DEFAULT 0,
    language      TEXT,
    updated_at    TIMESTAMP,                  -- GitHub pushed_at
    selected_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analysis_status TEXT DEFAULT 'pending',   -- pending, running, done, failed
    UNIQUE(user_id, repo_full_name)
);

CREATE INDEX idx_selected_repos_user_id ON selected_repos(user_id);
CREATE INDEX idx_selected_repos_status ON selected_repos(analysis_status);

-- ============================================================
-- REPO ANALYSIS RESULTS (one per selected repo)
-- ============================================================
CREATE TABLE repo_analyses (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    selected_repo_id  INTEGER NOT NULL REFERENCES selected_repos(id) ON DELETE CASCADE,
    user_id           TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Full analysis as JSON (RepoAnalysis model)
    analysis_json     TEXT NOT NULL,
    
    -- Extracted key signals for querying
    authorship_score  REAL,                   -- 0-1
    evolution_score   REAL,
    tutorial_clone_score REAL,               -- 0-1 (higher = more likely clone)
    quality_score     REAL,
    
    -- Tutorial clone details
    is_tutorial_clone INTEGER DEFAULT 0,
    clone_type        TEXT,                   -- e.g., 'create-react-app', 'django-tutorial'
    clone_confidence  REAL,
    
    -- Skill evidence summary (denormalized for queries)
    skills_json       TEXT NOT NULL,          -- List[SkillEvidence] JSON
    
    analyzed_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analysis_duration_ms INTEGER,             -- for performance tracking
    
    UNIQUE(selected_repo_id)
);

CREATE INDEX idx_repo_analyses_user_id ON repo_analyses(user_id);
CREATE INDEX idx_repo_analyses_clone ON repo_analyses(is_tutorial_clone);

-- ============================================================
-- PROOF CARDS (synthesized evidence)
-- ============================================================
CREATE TABLE proof_cards (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Full ProofCard JSON
    card_json       TEXT NOT NULL,
    
    -- Denormalized for recruiter queries
    unified_skills_json TEXT NOT NULL,        -- List[UnifiedSkill] JSON
    tutorial_clone_flags_json TEXT NOT NULL,  -- List[CloneFlag] JSON
    
    -- Overall metrics
    overall_confidence REAL,                  -- avg confidence across skills
    evidence_coverage  REAL,                  -- % skills with repo evidence
    
    generated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version         INTEGER DEFAULT 1,        -- for re-generation tracking
    
    UNIQUE(user_id, version)
);

CREATE INDEX idx_proof_cards_user_id ON proof_cards(user_id);

-- ============================================================
-- VIVA SESSIONS
-- ============================================================
CREATE TABLE viva_sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    proof_card_id   INTEGER NOT NULL REFERENCES proof_cards(id) ON DELETE CASCADE,
    
    -- Session config
    mode            TEXT NOT NULL,            -- 'voice', 'text', 'hybrid'
    question_count  INTEGER DEFAULT 0,
    current_question INTEGER DEFAULT 0,
    status          TEXT DEFAULT 'initialized', -- initialized, in_progress, completed, failed
    
    -- Full session log
    session_json    TEXT NOT NULL,            -- VivaSession JSON
    
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP,
    duration_seconds INTEGER,
    
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_viva_sessions_user_id ON viva_sessions(user_id);
CREATE INDEX idx_viva_sessions_status ON viva_sessions(status);

-- ============================================================
-- VIVA RESPONSES (one per question)
-- ============================================================
CREATE TABLE viva_responses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      INTEGER NOT NULL REFERENCES viva_sessions(id) ON DELETE CASCADE,
    question_id     TEXT NOT NULL,            -- from VivaQuestion.id
    question_type   TEXT NOT NULL,            -- code_walkthrough, alternative, debug, extend, behavioral
    skill           TEXT NOT NULL,
    
    -- Input
    question_prompt TEXT NOT NULL,
    answer_text     TEXT NOT NULL,            -- transcribed or typed
    answer_audio_path TEXT,                   -- path to saved audio (optional)
    
    -- Evaluation
    evaluation_json TEXT NOT NULL,            -- ResponseEvaluation JSON
    score           REAL,                     -- 0-1
    confidence_delta REAL,                    -- change in skill confidence
    
    response_time_ms INTEGER,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_viva_responses_session_id ON viva_responses(session_id);
CREATE INDEX idx_viva_responses_skill ON viva_responses(skill);

-- ============================================================
-- FINAL SCORES
-- ============================================================
CREATE TABLE final_scores (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    viva_session_id     INTEGER REFERENCES viva_sessions(id) ON DELETE SET NULL,
    proof_card_id       INTEGER NOT NULL REFERENCES proof_cards(id) ON DELETE CASCADE,
    
    -- Component scores (0-100)
    evidence_strength   REAL NOT NULL,
    viva_performance    REAL NOT NULL,
    assessment_score    REAL NOT NULL,
    consistency         REAL NOT NULL,
    
    -- Weighted total
    total_score         REAL NOT NULL,
    
    -- Breakdown
    skill_scores_json   TEXT NOT NULL,        -- Dict[skill, score] JSON
    reasons_json        TEXT NOT NULL,        -- List[str] JSON (human-readable)
    
    -- Pre/Post comparison
    pre_viva_confidence_json TEXT NOT NULL,   -- Dict[skill, conf] JSON
    post_viva_confidence_json TEXT NOT NULL,  -- Dict[skill, conf] JSON
    
    computed_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_final_scores_user_id ON final_scores(user_id);
CREATE INDEX idx_final_scores_total ON final_scores(total_score DESC);

-- ============================================================
-- RECRUITER JOB DESCRIPTIONS
-- ============================================================
CREATE TABLE recruiter_jds (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    jd_id           TEXT NOT NULL UNIQUE,     -- e.g., "JD-001"
    title           TEXT NOT NULL,
    company         TEXT,
    description     TEXT NOT NULL,            -- full JD text
    required_skills_json TEXT NOT NULL,       -- List[SkillRequirement] JSON
    preferred_skills_json TEXT,               -- List[SkillRequirement] JSON
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- RANKINGS (candidates ranked against a JD)
-- ============================================================
CREATE TABLE rankings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    jd_id           TEXT NOT NULL REFERENCES recruiter_jds(jd_id) ON DELETE CASCADE,
    user_id         TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    final_score_id  INTEGER NOT NULL REFERENCES final_scores(id) ON DELETE CASCADE,
    
    rank            INTEGER NOT NULL,         -- 1 = best
    score           REAL NOT NULL,            -- total_score from final_scores
    
    -- Per-skill comparison vs JD
    comparison_json TEXT NOT NULL,            -- Dict[skill, ComparisonDetail] JSON
    
    -- Human-readable reasons for this rank
    reasons_json    TEXT NOT NULL,            -- List[str] JSON
    
    -- Fairness audit
    fairness_audit_json TEXT,                 -- FairnessReport JSON
    
    ranked_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(jd_id, user_id)
);

CREATE INDEX idx_rankings_jd_id ON rankings(jd_id);
CREATE INDEX idx_rankings_rank ON rankings(jd_id, rank);

-- ============================================================
-- IMATS SYNC AUDIT LOG
-- ============================================================
CREATE TABLE imats_sync (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sync_type       TEXT NOT NULL,            -- 'proof_cards', 'rankings', 'shortlist_pull'
    payload_json    TEXT NOT NULL,            -- what was sent/received
    response_json   TEXT,                     -- API response
    status          TEXT NOT NULL,            -- 'success', 'failed', 'partial'
    error_message   TEXT,
    synced_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_imats_sync_type ON imats_sync(sync_type);
CREATE INDEX idx_imats_sync_status ON imats_sync(status);

-- ============================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================

-- Candidate summary for recruiter list view
CREATE VIEW candidate_summary AS
SELECT 
    u.user_id,
    fs.total_score,
    pc.overall_confidence,
    pc.evidence_coverage,
    vs.status as viva_status,
    vs.completed_at as viva_completed_at
FROM users u
LEFT JOIN final_scores fs ON fs.user_id = u.user_id
LEFT JOIN proof_cards pc ON pc.user_id = u.user_id AND pc.version = 1
LEFT JOIN viva_sessions vs ON vs.user_id = u.user_id AND vs.status = 'completed'
WHERE fs.id = (SELECT MAX(id) FROM final_scores WHERE user_id = u.user_id);

-- JD with candidate count
CREATE VIEW jd_candidate_counts AS
SELECT 
    j.jd_id,
    j.title,
    COUNT(r.user_id) as candidate_count
FROM recruiter_jds j
LEFT JOIN rankings r ON r.jd_id = j.jd_id
GROUP BY j.jd_id, j.title;

-- ============================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================
CREATE TRIGGER trg_users_updated_at
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE user_id = NEW.user_id;
END;

CREATE TRIGGER trg_resumes_updated_at
AFTER UPDATE ON resumes
BEGIN
    UPDATE resumes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER trg_proof_cards_updated_at
AFTER UPDATE ON proof_cards
BEGIN
    UPDATE proof_cards SET generated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

---

## 3. JSON Column Schemas (Reference)

### `resumes.parsed_json` → `ParsedResume`
```json
{
  "raw_text": "...",
  "skills": [{"name": "Python", "level": "intermediate", "source": "resume", "confidence": 0}],
  "projects": [{"name": "E-commerce API", "description": "...", "tech_stack": ["Python", "FastAPI"]}],
  "github_urls": ["https://github.com/user/repo"],
  "education": [{"degree": "B.Tech", "college": "XYZ", "year": 2024}],
  "experience": []
}
```

### `repo_analyses.analysis_json` → `RepoAnalysis`
```json
{
  "repo_id": "repo-123",
  "name": "ecommerce-api",
  "authorship": {"score": 0.92, "commits": 47, "primary_author": true},
  "evolution": {"score": 0.78, "duration_days": 60, "complexity_trend": "increasing"},
  "tutorial_clone": {"score": 0.15, "is_clone": false, "clone_type": null, "confidence": 0.85},
  "quality": {"score": 0.82, "has_tests": true, "has_docs": true, "lint_score": 0.9},
  "skill_evidence": [
    {"skill": "Python", "evidence_type": "implementation", "confidence": 0.9, "files": ["main.py", "models.py"]},
    {"skill": "FastAPI", "evidence_type": "framework_usage", "confidence": 0.85, "files": ["api/routes.py"]}
  ]
}
```

### `proof_cards.card_json` → `ProofCard`
```json
{
  "candidate_id": "CAND-0001",
  "unified_skills": [
    {
      "skill": "Python",
      "final_confidence": 92,
      "evidence_bundle": [
        {"type": "repo", "source": "ecommerce-api", "detail": "47 commits, primary author", "weight": 0.6},
        {"type": "assessment", "source": "coding_test", "detail": "Score: 88/100", "weight": 0.3},
        {"type": "resume", "source": "resume", "detail": "Listed as primary language", "weight": 0.1}
      ],
      "tutorial_clone_flag": false,
      "gap_notes": "Add async/await patterns in a project"
    }
  ],
  "tutorial_clone_flags": [],
  "generated_at": "2026-10-30T10:00:00Z"
}
```

### `final_scores.skill_scores_json`
```json
{
  "Python": {"evidence": 92, "viva": 88, "assessment": 85, "consistency": 90, "total": 89.5},
  "FastAPI": {"evidence": 85, "viva": 82, "assessment": 0, "consistency": 88, "total": 82.1},
  "SQL": {"evidence": 45, "viva": 60, "assessment": 70, "consistency": 55, "total": 54.2}
}
```

### `rankings.comparison_json`
```json
{
  "Python": {"jd_required": "advanced", "candidate_level": "intermediate", "gap": "moderate", "evidence": "Strong repo + viva"},
  "FastAPI": {"jd_required": "intermediate", "candidate_level": "intermediate", "gap": "none", "evidence": "Direct project experience"},
  "AWS": {"jd_required": "beginner", "candidate_level": "none", "gap": "high", "evidence": "No mention in resume/repo"}
}
```

### `rankings.fairness_audit_json`
```json
{
  "protected_attributes_checked": ["college", "gender", "age", "location"],
  "feature_importance": {"college": 0.0, "gender": 0.0, "age": 0.0, "location": 0.0},
  "proxy_check": {"passed": true, "suspected_proxies": []},
  "disparate_impact": {"by_college": {"tier1": 0.52, "tier2": 0.48, "tier3": 0.51}, "passed": true}
}
```

---

## 4. Migration / Init Script

```python
# src/db/init_db.py
import sqlite3
from pathlib import Path

def init_db(db_path: Path = Path("data/proofskill.db")):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Read and execute schema.sql
    schema_path = Path(__file__).parent.parent / "docs" / "DATABASE_SCHEMA.md"
    # Extract SQL from markdown (or maintain separate schema.sql)
    # For now, exec from string above
    
    with open(Path(__file__).parent / "schema.sql", "r") as f:
        sql = f.read()
    
    conn.executescript(sql)
    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")

if __name__ == "__main__":
    init_db()
```

---

## 5. Usage Notes

| Table | Write Path | Read Path |
|-------|------------|-----------|
| `users` | Auth setup (pre-hackathon) | Login, all joins |
| `resumes` | Resume parser (Phase 1) | Candidate dashboard, proof card |
| `github_links` | Resume parser | Repo selection page |
| `selected_repos` | Candidate UI (Phase 2) | Repo analyzer, proof card |
| `repo_analyses` | Repo analyzer (Phase 2) | Evidence synthesizer |
| `proof_cards` | Evidence synthesizer (Phase 3) | Viva engine, recruiter view |
| `viva_sessions` | Viva engine (Phase 4) | Results page, final scoring |
| `viva_responses` | Viva engine (per question) | Final scoring, analytics |
| `final_scores` | Scoring engine (Phase 5) | Recruiter rankings, IMATS |
| `recruiter_jds` | Pre-loaded (30 JDs) | Recruiter view, ranking |
| `rankings` | Scoring engine (Phase 5) | Recruiter view, IMATS push |
| `imats_sync` | IMATS client (Phase 6) | Audit, debugging |

---

*End of Database Schema*