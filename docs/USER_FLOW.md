# User Flow Document
**Project:** ProofSkill AI  
**Version:** 1.0  
**Date:** 2026-10-30  

---

## 1. Candidate Flow (Primary)

```mermaid
flowchart TD
    A[Landing / Login] --> B{Valid Credentials?}
    B -->|No| A
    B -->|Yes| C[Load Resume + Consented Data]
    C --> D[Parse Resume → Skills, Projects, GitHub URLs]
    D --> E{GitHub URL Present?}
    E -->|Yes| F[Fetch Public Repos via GitHub API]
    F --> G[Candidate Selects Repos to Showcase]
    G --> H[Deep Repo Analysis\n(All files: source + docs + config)]
    E -->|No| I[Mark: Alternative Evidence Path]
    H --> J[Evidence Synthesis]
    I --> J
    J --> K[Generate Proof Card\n(Skills + Evidence + Confidence)]
    K --> L[AI Viva / Simulation]
    L --> M{Voice or Text Mode?}
    M -->|Voice| N[AI Speaks Question (ElevenLabs TTS)]
    M -->|Text| O[Display Question + Text Input]
    N --> P[Candidate Speaks → STT (Whisper)]
    O --> Q[Candidate Types Answer]
    P --> R[Evaluate Response → Update Confidence]
    Q --> R
    R --> S{More Questions?}
    S -->|Yes| L
    S -->|No| T[Final Scoring\nPre vs Post Comparison]
    T --> U[Show Candidate Summary\n+ Actionable Gaps]
    U --> V[End Session]
```

---

## 2. Recruiter Flow

```mermaid
flowchart TD
    A[Recruiter Login / Dashboard] --> B[Select Job Description]
    B --> C[View Ranked Candidate List]
    C --> D{Compare Candidates?}
    D -->|Yes| E[Select 2 Candidates]
    E --> F[Side-by-Side Comparison View]
    F --> G[Skill-by-Skill Evidence + Confidence]
    G --> H[Human-Readable Reasons per Rank]
    D -->|No| I[View Single Candidate Proof Card]
    I --> G
    H --> J[Shortlist / Reject with Notes]
    J --> K[Export Report (PDF/JSON)]
    K --> L[Push to IMATS Sandbox]
```

---

## 3. Detailed Step-by-Step

### 3.1 Login & Resume Load
| Step | Actor | Action | System Response |
|------|-------|--------|-----------------|
| 1 | Candidate | Enters `user_id` + `password` | Validate against `users` table |
| 2 | System | Load resume file (PDF/DOCX) from `data/resumes/{user_id}.pdf` | Parse → structured JSON in `resumes` table |
| 3 | System | Extract GitHub URL(s) from resume | Store in `github_links` table |

### 3.2 GitHub Repo Selection (if applicable)
| Step | Actor | Action | System Response |
|------|-------|--------|-----------------|
| 4 | System | Call GitHub API `/users/{username}/repos?visibility=public` | Return repo list (name, description, stars, updated_at) |
| 5 | Candidate | Select 1–N repos via checkboxes | Store selections in `selected_repos` table |
| 6 | System | For each selected repo: clone/fetch → analyze all files | Run analysis pipeline (see §3.3) |

### 3.3 Repo Analysis Pipeline
```
Repo Root
  ├── Source files (.py, .js, .java, .cpp, .ts, .go, .rs, ...)
  ├── Config (package.json, requirements.txt, pom.xml, Cargo.toml, ...)
  ├── Docs (README.md, docs/, *.md, *.rst)
  ├── Tests (test/, tests/, *_test.*, spec/)
  └── .github/, .gitignore, Dockerfile, etc.
```

**Analyzers run in parallel:**
1. **Authorship** — commit history, email mapping, contribution %
2. **Evolution** — commit frequency, LOC growth, complexity trend
3. **Tutorial-Clone Detection** — fingerprint against known templates (create-react-app, next.js starter, django tutorial, etc.)
4. **Code Quality** — structure, testing coverage, type hints, docs, lint
5. **Originality** — AST similarity to known tutorials, copy-paste detection
6. **Skill Mapping** — frameworks, libraries, patterns → skill taxonomy

**Output per repo:** `RepoAnalysis` JSON with findings + confidence per signal.

### 3.4 Evidence Synthesis → Proof Card
```
ProofCard {
  candidate_id,
  resume_claims: [ {skill, claimed_level, source: "resume"} ],
  repo_evidence: [ {repo_id, skill, evidence_type, confidence, details} ],
  assessment_scores: {skill: score},
  unified_skills: [ {
      skill,
      final_confidence,        // 0-100
      evidence_bundle: [...],
      tutorial_clone_flag: bool,
      gap_notes: "Add a project demonstrating X"
  } ],
  generated_at
}
```

### 3.5 Viva / Simulation Session
**Question Generation Strategy:**
```
Input: ProofCard.unified_skills + RepoAnalysis details
→ Fine-tuned model generates:
   - Technical: "Walk me through auth flow in repo X"
   - Alternative: "How would you handle rate-limiting differently?"
   - Debug: "This function throws on empty input — fix it"
   - Extend: "Add pagination to this endpoint"
   - Behavioral: "Tell me about a conflict in a team project"
```

**Session State Machine:**
```
IDLE → INTRO → QUESTION_ASKED → WAITING_RESPONSE → EVALUATING → NEXT_QUESTION → ... → WRAP_UP → SCORING
```

**Voice Pipeline:**
```
AI Question (text) → ElevenLabs TTS → Audio Playback
Candidate Speech → Mic Capture → Whisper STT → Text
Text → Evaluator (fine-tuned model) → {score, feedback, confidence_delta}
```

### 3.6 Final Scoring
```
FinalScore = weighted_sum(
  evidence_strength: 0.35,      // Proof Card confidence
  viva_performance: 0.35,       // Avg response quality
  assessment: 0.20,             // External test scores
  consistency: 0.10             // Resume vs repo vs viva alignment
)
```

### 3.7 Recruiter Comparison View
| Column | Candidate A | Candidate B |
|--------|-------------|-------------|
| Skill: Python | ★★★★☆ (92%) | ★★★☆☆ (78%) |
| Evidence | Repo: django-api (auth, ORM) | Resume only |
| Viva | Strong on async patterns | Couldn't explain GIL |
| Rank Reason | "Deep repo evidence + strong viva" | "Limited evidence, viva gaps" |

---

## 4. Alternative Evidence Path (No GitHub)

| Evidence Source | Weight | Notes |
|-----------------|--------|-------|
| Assessment scores | 0.40 | Primary signal |
| Resume project descriptions (NLP) | 0.25 | Parse for specificity |
| Viva behavioral/situational | 0.25 | STAR responses evaluated |
| Self-reported + verification quiz | 0.10 | Quick fact-check questions |

---

## 5. Edge Cases & Error Handling

| Scenario | Handling |
|----------|----------|
| GitHub API rate limited | Cache 24h; show cached data; allow manual repo URL |
| Repo too large (>500MB) | Analyze only source files < 1MB each; skip vendor/node_modules |
| Candidate mic fails | Auto-switch to text mode; log fallback |
| Fine-tuned model OOM | Fallback to quantized version; queue requests |
| IMATS API down | Queue + retry; local backup of rankings |

---

## 6. Data Flow Summary

```
Dataset (400 profiles)
    │
    ▼
[Auth DB] ← user_id/password
    │
    ▼
[Resume Parser] → skills, projects, github_urls
    │
    ├─→ [GitHub Fetcher] → [Repo Analyzer] → RepoEvidence
    │
    ▼
[Evidence Synthesizer] → ProofCard
    │
    ▼
[Viva Engine] ← Fine-tuned Model + ElevenLabs + Whisper
    │
    ▼
[Scorer] → FinalScore + PrePostComparison
    │
    ├─→ [Candidate View] Summary + Gaps
    │
    └─→ [Recruiter View] Ranking + Comparison + Reasons
           │
           ▼
      [IMATS Sandbox API]
```

---

*End of User Flow*