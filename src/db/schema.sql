-- ProofSkill AI Database Schema
-- Extracted from docs/DATABASE_SCHEMA.md
-- Run with: python src/db/init_db.py

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ============================================================
-- USERS & AUTH
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id       TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    resume_path   TEXT NOT NULL,
    candidate_name TEXT NOT NULL DEFAULT 'Candidate',
    consent_given INTEGER NOT NULL DEFAULT 0,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_resume_path ON users(resume_path);

-- ============================================================
-- RECRUITER AUTHENTICATION
-- ============================================================
CREATE TABLE IF NOT EXISTS recruiter_users (
    email         TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- PARSED RESUME DATA
-- ============================================================
CREATE TABLE IF NOT EXISTS resumes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    raw_text      TEXT NOT NULL,
    parsed_json   TEXT NOT NULL,
    skills_json   TEXT NOT NULL,
    projects_json TEXT NOT NULL,
    education_json TEXT NOT NULL,
    experience_json TEXT NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);

-- ============================================================
-- GITHUB LINKS EXTRACTED FROM RESUME
-- ============================================================
CREATE TABLE IF NOT EXISTS github_links (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    url         TEXT NOT NULL,
    link_type   TEXT NOT NULL,
    extracted_from TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_github_links_user_id ON github_links(user_id);

-- ============================================================
-- CANDIDATE-SELECTED REPOS
-- ============================================================
CREATE TABLE IF NOT EXISTS selected_repos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    github_url_id INTEGER REFERENCES github_links(id) ON DELETE SET NULL,
    owner         TEXT NOT NULL,
    repo_name     TEXT NOT NULL,
    repo_full_name TEXT NOT NULL,
    description   TEXT,
    stars         INTEGER DEFAULT 0,
    language      TEXT,
    updated_at    TIMESTAMP,
    selected_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analysis_status TEXT DEFAULT 'pending',
    UNIQUE(user_id, repo_full_name)
);

CREATE INDEX IF NOT EXISTS idx_selected_repos_user_id ON selected_repos(user_id);
CREATE INDEX IF NOT EXISTS idx_selected_repos_status ON selected_repos(analysis_status);

-- ============================================================
-- REPO ANALYSIS RESULTS
-- ============================================================
CREATE TABLE IF NOT EXISTS repo_analyses (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    selected_repo_id  INTEGER NOT NULL REFERENCES selected_repos(id) ON DELETE CASCADE,
    user_id           TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    analysis_json     TEXT NOT NULL,
    authorship_score  REAL,
    evolution_score   REAL,
    tutorial_clone_score REAL,
    quality_score     REAL,
    is_tutorial_clone INTEGER DEFAULT 0,
    clone_type        TEXT,
    clone_confidence  REAL,
    skills_json       TEXT NOT NULL,
    analyzed_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analysis_duration_ms INTEGER,
    UNIQUE(selected_repo_id)
);

CREATE INDEX IF NOT EXISTS idx_repo_analyses_user_id ON repo_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_repo_analyses_clone ON repo_analyses(is_tutorial_clone);

-- ============================================================
-- PROOF CARDS
-- ============================================================
CREATE TABLE IF NOT EXISTS proof_cards (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    card_json       TEXT NOT NULL,
    unified_skills_json TEXT NOT NULL,
    tutorial_clone_flags_json TEXT NOT NULL,
    overall_confidence REAL,
    evidence_coverage  REAL,
    generated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version         INTEGER DEFAULT 1,
    UNIQUE(user_id, version)
);

CREATE INDEX IF NOT EXISTS idx_proof_cards_user_id ON proof_cards(user_id);

-- ============================================================
-- VIVA SESSIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS viva_sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    proof_card_id   INTEGER NOT NULL REFERENCES proof_cards(id) ON DELETE CASCADE,
    mode            TEXT NOT NULL,
    question_count  INTEGER DEFAULT 0,
    current_question INTEGER DEFAULT 0,
    status          TEXT DEFAULT 'initialized',
    session_json    TEXT NOT NULL,
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP,
    duration_seconds INTEGER,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_viva_sessions_user_id ON viva_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_viva_sessions_status ON viva_sessions(status);

-- ============================================================
-- VIVA RESPONSES
-- ============================================================
CREATE TABLE IF NOT EXISTS viva_responses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      INTEGER NOT NULL REFERENCES viva_sessions(id) ON DELETE CASCADE,
    question_id     TEXT NOT NULL,
    question_type   TEXT NOT NULL,
    skill           TEXT NOT NULL,
    question_prompt TEXT NOT NULL,
    answer_text     TEXT NOT NULL,
    answer_audio_path TEXT,
    evaluation_json TEXT NOT NULL,
    score           REAL,
    confidence_delta REAL,
    response_time_ms INTEGER,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_viva_responses_session_id ON viva_responses(session_id);
CREATE INDEX IF NOT EXISTS idx_viva_responses_skill ON viva_responses(skill);

-- ============================================================
-- FINAL SCORES
-- ============================================================
CREATE TABLE IF NOT EXISTS final_scores (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    viva_session_id     INTEGER REFERENCES viva_sessions(id) ON DELETE SET NULL,
    proof_card_id       INTEGER NOT NULL REFERENCES proof_cards(id) ON DELETE CASCADE,
    evidence_strength   REAL NOT NULL,
    viva_performance    REAL NOT NULL,
    assessment_score    REAL NOT NULL,
    consistency         REAL NOT NULL,
    total_score         REAL NOT NULL,
    skill_scores_json   TEXT NOT NULL,
    reasons_json        TEXT NOT NULL,
    pre_viva_confidence_json TEXT NOT NULL,
    post_viva_confidence_json TEXT NOT NULL,
    computed_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_final_scores_user_id ON final_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_final_scores_total ON final_scores(total_score DESC);

-- ============================================================
-- RECRUITER JOB DESCRIPTIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS recruiter_jds (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    jd_id           TEXT NOT NULL UNIQUE,
    title           TEXT NOT NULL,
    company         TEXT,
    description     TEXT NOT NULL,
    required_skills_json TEXT NOT NULL,
    preferred_skills_json TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- RANKINGS
-- ============================================================
CREATE TABLE IF NOT EXISTS rankings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    jd_id           TEXT NOT NULL REFERENCES recruiter_jds(jd_id) ON DELETE CASCADE,
    user_id         TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    final_score_id  INTEGER NOT NULL REFERENCES final_scores(id) ON DELETE CASCADE,
    rank            INTEGER NOT NULL,
    score           REAL NOT NULL,
    comparison_json TEXT NOT NULL,
    reasons_json    TEXT NOT NULL,
    fairness_audit_json TEXT,
    ranked_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(jd_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_rankings_jd_id ON rankings(jd_id);
CREATE INDEX IF NOT EXISTS idx_rankings_rank ON rankings(jd_id, rank);

-- ============================================================
-- IMATS SYNC AUDIT LOG
-- ============================================================
CREATE TABLE IF NOT EXISTS imats_sync (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sync_type       TEXT NOT NULL,
    payload_json    TEXT NOT NULL,
    response_json   TEXT,
    status          TEXT NOT NULL,
    error_message   TEXT,
    synced_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_imats_sync_type ON imats_sync(sync_type);
CREATE INDEX IF NOT EXISTS idx_imats_sync_status ON imats_sync(status);

-- ============================================================
-- VIEWS
-- ============================================================

CREATE VIEW IF NOT EXISTS candidate_summary AS
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

CREATE VIEW IF NOT EXISTS jd_candidate_counts AS
SELECT 
    j.jd_id,
    j.title,
    COUNT(r.user_id) as candidate_count
FROM recruiter_jds j
LEFT JOIN rankings r ON r.jd_id = j.jd_id
GROUP BY j.jd_id, j.title;

-- ============================================================
-- TRIGGERS
-- ============================================================
CREATE TRIGGER IF NOT EXISTS trg_users_updated_at
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE user_id = NEW.user_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_resumes_updated_at
AFTER UPDATE ON resumes
BEGIN
    UPDATE resumes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_proof_cards_updated_at
AFTER UPDATE ON proof_cards
BEGIN
    UPDATE proof_cards SET generated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;