# ProofSkill AI 🚀

**Evidence-Based Skill Assessment for Fresher Recruitment**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Development-orange)]()

ProofSkill AI is an AI-assisted recruitment and skill assessment platform designed to help recruiters understand a fresher candidate's demonstrated technical skills through structured evidence, adaptive interviews, project viva, and explainable job matching.

Instead of relying only on resume claims or educational credentials, ProofSkill AI aims to connect candidate statements with available project evidence and assessment results.

> **Core principle:** Assess demonstrated, job-relevant skills through evidence—not assumptions about the candidate.

**Hackathon:** Deviathon 2.0  
**Problem Statement:** IM-105 Advanced — Integraminds  
**Theme:** AI FRONTIER  
**Track:** Software

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Our Solution](#our-solution)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Fairness and Responsible AI](#fairness-and-responsible-ai)
- [Privacy and Security](#privacy-and-security)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Problem Statement

Freshers often struggle to demonstrate practical skills through a resume alone. Recruiters may have limited time to verify project claims, evaluate technical understanding, and compare candidates consistently.

Traditional screening can overemphasize educational credentials, subjective interviews, or publicly available portfolios. These signals may not fully represent a candidate's actual abilities.

ProofSkill AI aims to make fresher assessment more evidence-based, transparent, and consistent.

## Our Solution

ProofSkill AI is designed to build an explainable skill profile by connecting:

- Resume-derived claims.
- Available project and repository evidence.
- Adaptive technical interview responses.
- Project-specific viva responses.
- Explicit assessment rubrics.
- Requirements from a target job description.

The resulting profile helps recruiters understand which competencies have supporting evidence, which are partially demonstrated, and which still require assessment.

The platform is intended to assist human reviewers, not replace their judgment.

## Key Features

### 1. Resume Intelligence

Extract structured information from PDF, DOCX, and supported text documents.

The intended extraction workflow identifies:
- Technical skills and tools.
- Projects and stated contributions.
- Relevant experience and internships.
- Education and certifications.
- Supporting evidence and uncertainty.

Resume claims remain self-reported unless independently verified.

### 2. Evidence-Linked Skill Profiles

Associate candidate claims with available supporting evidence.

Each skill can be described in terms of:
- Supporting evidence.
- Evidence source.
- Verification status.
- Assessment results.
- Missing information and limitations.

A missing repository or unassessed skill must not automatically be interpreted as an inability.

### 3. Adaptive Technical Interviews

Generate technical questions based on the target role, job description, and available candidate evidence.

The intended interview workflow supports:
- Role-relevant questions.
- Follow-up questions based on previous responses.
- Multiple difficulty levels.
- Question-specific evaluation rubrics.
- Duplicate-question checks.
- Reasonable interview time limits.

### 4. Project-Specific Viva

When a resume contains GitHub links, show the extracted links to the candidate. With consent, list eligible repositories for candidate selection, then analyze only the repositories the candidate explicitly selects.

Generate project-grounded questions and bounded tasks that explore:
- Project purpose and architecture.
- Data flow and component responsibilities.
- Implementation decisions.
- Explaining selected code and proposing or submitting a focused code change.
- The candidate's approach and valid alternative approaches.
- Debugging and edge cases.
- Testing and reliability.
- Security considerations.
- Limitations and future improvements.

Repository code is inspected as untrusted evidence and is never executed or changed on GitHub by the assessment system. A code-change task is submitted as a response or patch for review. When repository evidence is unavailable or declined, conceptual questions or scenario-based assessments provide an alternative.

### 5. Structured Answer Evaluation

Evaluate answers against explicit, question-specific criteria.

Use the canonical 0–4 rubric for individual answers. Skill and overall performance scores are normalized separately to 0–100; see [the scoring framework](docs/SCORING_AND_FAIRNESS.md).

| Score | Meaning |
|---:|---|
| 0 | No relevant answer or fundamentally incorrect reasoning |
| 1 | Limited understanding with major gaps |
| 2 | Partial understanding with important omissions |
| 3 | Correct answer with sound reasoning |
| 4 | Strong answer with relevant depth and trade-offs |

The rubric must be applied consistently. Scores should not depend on accent, confidence, answer length, or one exact wording.

### 6. Explainable Recruiter Matching

Compare available candidate evidence against the requirements of a specific job description.

The intended output explains:
- Supported required skills.
- Partially supported skills.
- Preferred skills with evidence.
- Skills that have not yet been assessed.
- Evidence gaps and recommended follow-up assessments.

Any numerical match score must follow a documented scoring methodology. It must not be invented when the necessary inputs are unavailable.

### 7. Fair Assessment Alternatives

Candidates should have a fair opportunity to demonstrate their abilities even when they lack a public GitHub profile or cannot share a private repository.

Alternative assessments may include:
- Short practical exercises.
- Scenario-based questions.
- Verbal project walkthroughs.
- Structured technical interviews.

---

## How It Works

The intended end-to-end workflow is:

1. **Candidate input:** Supply a resume and any authorized project evidence.
2. **Extraction:** Convert available resume content into structured candidate claims.
3. **Evidence mapping:** Connect claims to available project or assessment evidence.
4. **Repository choice:** Show GitHub links identified in the resume; after explicit consent, list eligible repositories and let the candidate select and confirm which to analyze.
5. **Project inspection:** Inspect bounded files from selected repositories without executing code.
6. **Assessment generation:** Create role-specific questions and evidence-grounded project tasks.
7. **Answer evaluation:** Apply explicit rubrics to explanations, design reasoning, and submitted code changes.
8. **Skill profile:** Summarize demonstrated competencies and evidence gaps.
9. **Recruiter review:** Explain alignment with job requirements and suggest follow-up assessments.

The actual implementation status of each stage must be verified in the source code before it is presented as operational.

## Technology Stack

The documented technical direction includes:

| Component | Technology |
|---|---|
| Programming language | Python |
| Initial web interface | Streamlit |
| Local database | SQLite |
| PDF extraction | PyMuPDF |
| DOCX extraction | python-docx |
| NLP | spaCy |
| Semantic embeddings | Sentence Transformers |
| AI integration | Configurable language-model provider |
| Repository integration | GitHub REST API, with appropriate consent |
| Automated testing | pytest |
| Configuration | Environment variables |

This table describes the intended technology direction. The installed dependencies and working integrations should be confirmed against the actual implementation.

## Project Structure

```text
Proof-Skill-AI/
├── .agents/
├── .github/
│   └── copilot-instructions.md
├── data/
│   ├── MANIFEST.yaml
│   └── README.md
├── deploy/
├── docs/
│   ├── ADR/
│   │   └── 0001-initial-architecture.md
│   ├── AI_MODELS.md
│   ├── AI_STRATEGY.md
│   ├── API_CONTRACTS.md
│   ├── API_SPEC.md
│   ├── ARCHITECTURE.md
│   ├── CHANGELOG.md
│   ├── DATA_DICTIONARY.md
│   ├── DATA_MODEL.md
│   ├── DATASETS.md
│   ├── DEVELOPMENT.md
│   ├── EVALUATION.md
│   ├── PRD.md
│   ├── PRIVACY_AND_SECURITY.md
│   ├── ROADMAP.md
│   ├── RUNBOOK.md
│   ├── SCORING_AND_FAIRNESS.md
│   ├── SECURITY_PRIVACY.md
│   ├── TESTING_AND_EVALUATION.md
│   └── USER_FLOWS.md
├── notebooks/
├── prompts/
│   ├── README.md
│   ├── answer_evaluation.md
│   ├── interview_generation.md
│   ├── project_viva.md
│   ├── recruiter_explanation.md
│   └── resume_extraction.md
├── scripts/
├── src/
├── tests/
├── .env.example
├── AGENTS.md
├── CHANGELOG.md
├── CURRENT_STATE.md
├── DECISIONS.md
├── HANDOFF.md
├── LICENSE
├── PROJECT_CONTEXT.md
├── pyproject.toml
├── README.md
├── SECURITY.md
└── TASKS.md
```

Some directories may remain empty during early development. Their presence does not imply that their planned functionality is implemented.

## Getting Started

### Prerequisites

- Python 3.11, 3.12, or 3.13, subject to dependency compatibility.
- pip.
- Git, if cloning the repository.
- Optional AI-provider credentials for workflows that require a live model.

### 1. Clone the repository

If the project is hosted in a Git repository:

```bash
git clone <YOUR_REPOSITORY_URL>
cd Proof-Skill-AI
```

Replace `<YOUR_REPOSITORY_URL>` with the actual repository URL.

If you already have the project locally, open a terminal in its root directory instead.

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Install the base project and development dependencies:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

For the optional AI and NLP packages defined in `pyproject.toml`:

```bash
pip install -e ".[dev,ai,nlp]"
```

Install optional speech dependencies only when speech transcription is implemented and needed.

If installation fails, check the Python version, operating system requirements, and compatibility of the package versions in `pyproject.toml`.

## Environment Configuration

Copy `.env.example` to `.env` in the project root.

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**macOS/Linux:**

```bash
cp .env.example .env
```

Configure only the values required by the selected workflow.

Important settings may include:
- Application environment and demo mode.
- Database location.
- AI provider and model.
- AI API key and optional base URL.
- Optional GitHub authorization only if a supported workflow requires it; public repository discovery should not require a personal access token. Private repository access is not available without a separately implemented, least-privilege authorization flow.
- Optional speech transcription settings.

Do not commit `.env` or put real credentials in documentation, source code, screenshots, or public repositories.

Environment variables only take effect when the application reads and uses them.

## Running the Application

Start the Streamlit application from the project root:

```powershell
python -m streamlit run app.py
```

The application starts in demo mode by default and uses synthetic data and
deterministic local services when no backend module or external credentials are
configured. Configure `PROOFSKILL_SERVICES_MODULE` only when a compatible
backend service module is available.

## Testing

There are currently no test files under `tests/`. After tests are added, run the suite from the repository root:

```bash
pytest
```

For a coverage report:

```bash
pytest --cov=src --cov-report=term-missing
```

The coverage command requires the configured coverage dependency.

Important test scenarios include:
- Empty or malformed resume content.
- Unsupported or oversized documents.
- Missing environment variables.
- Invalid AI-generated JSON.
- Unknown evidence references.
- Duplicate interview questions.
- Missing repository access.
- Conflicting candidate evidence.
- External-service timeouts.
- Database errors.
- Prompt-injection attempts in supplied content.
- Demo-mode fallback behavior.
- Privacy and authorization checks.

Only report tests as passing after they have actually been executed.

## Fairness and Responsible AI

ProofSkill AI is designed around job-relevant evidence.

The assessment process must not use:
- Protected characteristics to score skills.
- College prestige as a substitute for technical competence.
- Accent, facial appearance, or personality assumptions.
- Public repository availability as the sole measure of skill.
- Missing evidence as automatic proof of inability.

Candidates should receive consistent assessment criteria and reasonable opportunities to demonstrate their competencies.

AI-generated scores and explanations must remain reviewable by humans.

## Privacy and Security

- Process only the information necessary for the assessment.
- Obtain appropriate consent before accessing restricted repositories.
- Do not expose candidate data to unauthorized users.
- Keep credentials outside source code.
- Validate uploads and external service responses.
- Avoid logging raw resumes, secrets, or private repository content unnecessarily.
- Apply appropriate retention and deletion policies.
- Treat all candidate documents and repository contents as untrusted input.

Refer to `SECURITY.md`, `docs/SECURITY_PRIVACY.md`, and `docs/PRIVACY_AND_SECURITY.md` for additional guidance.

## Current Limitations

This checkout is a documentation and configuration scaffold. The `src/` and `tests/` directories are empty, and there is no runnable application or automated test suite yet.

The following items require implementation and verification before they can be claimed as operational:

- End-to-end application startup.
- Resume extraction and evidence mapping.
- Live AI-provider integration.
- Adaptive interview and project viva execution.
- Answer evaluation and score validation.
- Recruiter-facing matching and explanations.
- GitHub integration and consent enforcement.
- Database initialization and access controls.
- Demo fallback behavior.
- Automated test results.
- External hackathon API integration, if required.

No application source is present in this checkout, so these workflows are not implemented here.

## Roadmap

### Phase 1 — Runnable foundation
- Verify dependencies and startup.
- Confirm configuration and database initialization.
- Establish a working demonstration path.

### Phase 2 — Candidate evidence
- Implement or verify resume extraction.
- Structure skill and project claims.
- Track evidence references and uncertainty.

### Phase 3 — AI assessments
- Integrate interview generation.
- Integrate project viva generation.
- Validate model outputs.
- Evaluate answers with consistent rubrics.

### Phase 4 — Recruiter workflow
- Map skills to job requirements.
- Explain supported and unassessed competencies.
- Provide evidence-backed comparisons.
- Keep human review in the process.

### Phase 5 — Quality and integration
- Run automated tests.
- Validate fairness and privacy controls.
- Verify external integrations.
- Document actual performance and limitations.

The roadmap should be updated as work is implemented and verified.

## Contributing

Contributions should follow the existing project architecture and instructions in `AGENTS.md`.

Before making changes:
1. Inspect the relevant code and documentation.
2. Understand existing input/output contracts.
3. Prefer small, focused changes.
4. Add or update relevant tests.
5. Run the relevant checks where possible.
6. Update documentation when behavior changes.
7. Report limitations and unverified functionality honestly.

Avoid adding unnecessary dependencies or creating duplicate modules.

## License

This project includes a `LICENSE` file. Review that file for the applicable license terms.

The software license does not automatically grant permission to use third-party datasets, private repositories, candidate resumes, or personal information.

## Acknowledgments

Built as part of Deviathon 2.0 under the AI FRONTIER theme for problem statement IM-105 Advanced — Integraminds.

---

**ProofSkill AI — Evidence over assumptions. Skills over credentials alone. Human judgment over automated decisions.**
