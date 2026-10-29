# ProofSkill AI — Project Handoff

## 1. Project Identity

- **Project:** ProofSkill AI
- **Hackathon:** Deviathon 2.0
- **Problem Statement:** IM-105 Advanced — Integraminds
- **Theme:** AI FRONTIER
- **Track:** Software
- **Primary Language:** Python
- **Initial UI Direction:** Streamlit, subject to existing implementation
- **Current Handoff Status:** Project context and documentation recorded; actual runtime status must be verified.

## 2. Project Overview

ProofSkill AI is designed to support fresher recruitment through evidence-based skill assessment.

The system aims to connect candidate claims, available project evidence, technical assessments, and job requirements into an explainable candidate skill profile.

The goal is to help recruiters understand demonstrated competencies and evidence gaps without relying exclusively on resumes, educational prestige, or subjective impressions.

ProofSkill AI is intended to support human decision-making rather than independently make hiring decisions.

## 3. Core Product Requirements

The intended workflow includes:

1. Resume text extraction.
2. Structured skill and project extraction.
3. Evidence collection from authorized sources.
4. Adaptive technical interview generation.
5. Project-specific viva generation.
6. Candidate answer evaluation using explicit rubrics.
7. Explainable candidate-to-job matching.
8. Recruiter-facing evidence summaries.
9. Fair comparison against consistent job requirements.
10. A usable demo path when optional external services are unavailable.

These are intended capabilities. Verify the implementation before describing any workflow as complete.

## 4. Important Project Principles

### Evidence integrity

- Keep self-reported claims distinct from independently verified evidence.
- Do not invent skills, repository files, assessment results, or scores.
- Do not assume repository access proves candidate authorship.
- Treat missing evidence as unassessed, not proof of inability.
- Make uncertainty visible in assessment results.

### Fairness

- Use job-relevant competencies and explicit scoring rubrics.
- Do not use protected characteristics or unrelated personal information to assess technical ability.
- Do not treat college prestige as a substitute for demonstrated skills.
- Do not infer competence from accent, facial appearance, confidence, or personality.
- Provide alternative assessment opportunities for candidates without public repositories.

### Human oversight

- AI-generated explanations and scores support recruiter review.
- Do not make autonomous hiring or rejection decisions.
- Explain the basis and limitations of assessments.

### Security and privacy

- Use environment variables for credentials.
- Never commit real secrets.
- Obtain appropriate consent before accessing restricted repositories.
- Minimize sensitive data in prompts, logs, and persistent storage.
- Validate uploaded documents, external responses, and model output.

## 5. Repository Structure

The documented repository includes:

- `src/` — application source code.
- `tests/` — automated tests.
- `scripts/` — development and utility scripts.
- `notebooks/` — exploratory work.
- `deploy/` — deployment-related resources.
- `data/` — dataset documentation and manifest.
- `docs/` — requirements, architecture, security, testing, and operational documentation.
- `docs/ADR/` — architectural decision records.
- `prompts/` — AI prompt definitions.
- `.github/` — coding-agent instructions.
- `.agents/` — agent-related project resources.

Important root files include:

- `README.md`
- `PROJECT_CONTEXT.md`
- `CURRENT_STATE.md`
- `TASKS.md`
- `AGENTS.md`
- `DECISIONS.md`
- `CHANGELOG.md`
- `LICENSE`
- `SECURITY.md`
- `pyproject.toml`
- `.env.example`

The directory structure alone does not prove that the application or integrations are operational.

## 6. Important Documentation

Read the relevant existing files before making changes.

| File | Purpose |
|---|---|
| `PROJECT_CONTEXT.md` | Overall project context |
| `CURRENT_STATE.md` | Current implementation status |
| `TASKS.md` | Work items and priorities |
| `AGENTS.md` | Coding and repository rules |
| `DECISIONS.md` | Technical and product decisions |
| `CHANGELOG.md` | Recorded changes |
| `README.md` | Project overview and setup instructions |
| `docs/PRD.md` | Product requirements |
| `docs/ARCHITECTURE.md` | Proposed architecture |
| `docs/DATA_MODEL.md` | Data entities and relationships |
| `docs/SCORING_AND_FAIRNESS.md` | Assessment scoring and fairness |
| `docs/AI_STRATEGY.md` | AI workflow strategy |
| `docs/AI_MODELS.md` | Model selection and configuration |
| `docs/API_CONTRACTS.md` | API contract guidance |
| `docs/API_SPEC.md` | API specification |
| `docs/PRIVACY_AND_SECURITY.md` | Privacy and security guidance |
| `docs/SECURITY_PRIVACY.md` | Additional security documentation |
| `docs/TESTING_AND_EVALUATION.md` | Testing and evaluation guidance |
| `docs/EVALUATION.md` | Evaluation requirements |
| `docs/DEVELOPMENT.md` | Development guidance |
| `docs/RUNBOOK.md` | Operational guidance |
| `docs/USER_FLOWS.md` | User workflow definitions |
| `data/MANIFEST.yaml` | Dataset manifest |
| `data/README.md` | Dataset usage guidance |
| `prompts/README.md` | Prompt library overview |

## 7. Prompt Library

The existing prompt files define the intended AI behavior for:

- `prompts/resume_extraction.md`
- `prompts/interview_generation.md`
- `prompts/answer_evaluation.md`
- `prompts/project_viva.md`
- `prompts/recruiter_explanation.md`

Before changing AI-related code:

1. Read the relevant prompt.
2. Inspect the code that consumes its output.
3. Confirm the expected input and output schema.
4. Preserve valid evidence references and verification status.
5. Validate model output before using or storing it.
6. Update relevant tests if behavior changes.

Do not assume that prompt files are already connected to the application.

## 8. Technical Direction

The documented technical direction includes:

- Python application logic.
- Streamlit for an initial interface, if appropriate.
- SQLite for initial local persistence.
- PyMuPDF for PDF processing.
- `python-docx` for DOCX processing.
- spaCy and Sentence Transformers for NLP tasks.
- A configurable LLM integration.
- GitHub API access when authorized.
- Optional speech-to-text processing.
- pytest for automated testing.

Check `pyproject.toml` and the existing source code to determine which dependencies are installed and which integrations are implemented.

Do not introduce a new framework or major dependency without a clear reason.

## 9. Environment and Secrets

`.env.example` documents intended environment configuration.

Before running the project:

1. Inspect the current setup instructions in `README.md` and `docs/DEVELOPMENT.md`.
2. Confirm the supported Python version and dependencies.
3. Create a local environment file from the template if required.
4. Configure only the credentials needed for the selected workflow.
5. Keep real credentials out of version control.
6. Confirm that demo mode behaves appropriately when optional services are unavailable.

Do not assume that blank AI-provider settings or placeholder values establish a live integration.

## 10. Recommended Continuation Procedure

The next developer or coding agent should proceed in this order.

### Step 1 — Inspect the implementation

- Review `src/`.
- Review `pyproject.toml`.
- Inspect the existing test suite.
- Check startup instructions and current configuration.
- Identify implemented, partially implemented, and missing workflows.

Do not rewrite existing modules before understanding their purpose.

### Step 2 — Establish a runnable baseline

- Install dependencies using the documented project procedure.
- Run the supported startup command.
- Record actual startup errors.
- Verify configuration and database initialization.
- Confirm the demo workflow, if implemented.

Do not invent a startup command if the repository does not establish one.

### Step 3 — Compare code with requirements

Use `TASKS.md`, `CURRENT_STATE.md`, and `docs/PRD.md` to identify the highest-priority gaps.

Prefer small, testable changes that advance the main demonstration workflow.

### Step 4 — Verify AI integration

For each AI workflow:
- Check input construction.
- Check prompt selection.
- Validate output structure.
- Verify evidence references.
- Handle timeouts and invalid responses.
- Confirm fallback behavior.
- Test missing or ambiguous inputs.

### Step 5 — Verify end-to-end behavior

Where implemented, test the flow from resume input through evidence extraction, assessment, scoring, and recruiter explanation.

Ensure synthetic demo results are visibly labeled and are not confused with verified candidate evidence.

### Step 6 — Record the actual state

Update `CURRENT_STATE.md`, `TASKS.md`, and other relevant existing documentation based on verified findings.

Record tests only when they have actually been executed.

## 11. Suggested Priority Order

Priorities should be confirmed against the real codebase.

1. **Runnable baseline:** Ensure the application starts reliably.
2. **Resume workflow:** Extract and display structured information with evidence references.
3. **Assessment workflow:** Generate and validate interview and viva questions.
4. **Answer evaluation:** Apply explicit rubrics and validate scores.
5. **Recruiter workflow:** Explain job alignment and evidence gaps.
6. **Demo reliability:** Provide a clear, usable path without mandatory external credentials where feasible.
7. **Testing and security:** Verify error handling, privacy, authorization, and output validation.
8. **External integrations:** Verify actual service contracts before claiming integration success.

Do not build every optional feature before the core demonstration path is reliable.

## 12. Testing Expectations

Use the existing pytest configuration.

Test applicable scenarios such as:

- Empty or malformed resume text.
- Unsupported and oversized documents.
- Missing environment variables.
- Invalid model output.
- Unavailable external services.
- Unknown evidence references.
- Duplicate questions.
- Missing repository access.
- Conflicting candidate evidence.
- Prompt-injection content in supplied documents.
- Invalid scoring values.
- Database failures.
- Unauthorized candidate-data access.
- Demo-mode fallback behavior.

Report the actual results, including failures and untested areas.

## 13. Integration Constraints

For external services, including AI providers, GitHub, speech transcription, and the IMATS sandbox API:

- Follow the real documented interface.
- Do not invent endpoints or credentials.
- Respect authorization and consent.
- Handle rate limits and timeouts.
- Validate response schemas.
- Distinguish mock responses from live responses.
- Document integration status honestly.

The existence of an environment variable, prompt, or architecture document is not evidence of a successful integration.

## 14. Change and File Management Rules

- Prefer the smallest correct change.
- Reuse existing files and modules where practical.
- Do not modify unrelated functionality.
- Do not create additional files unless explicitly requested or genuinely necessary and authorized.
- If the user asks for content for one existing file, provide content for that file only.
- Preserve compatibility with documented interfaces.
- Update relevant tests and documentation when behavior changes.
- Never expose secrets in source code, logs, or generated documentation.

## 15. Handoff Checklist

Before handing work to another developer, record:

- [ ] Current application startup status.
- [ ] Features verified to work.
- [ ] Features implemented but not yet verified.
- [ ] Features still planned or blocked.
- [ ] Commands actually executed.
- [ ] Tests actually run and their results.
- [ ] Required environment variables, without exposing secrets.
- [ ] Known bugs and limitations.
- [ ] External integrations that remain unverified.
- [ ] The next recommended task.

Do not mark an item complete based solely on documentation or generated code.

## 16. Current Handoff Caveat

This handoff captures the documented project context and intended development approach.

The actual implementation status, working startup command, test results, model-provider connectivity, GitHub integration, and IMATS sandbox connectivity must be confirmed from the repository and execution environment.

The next contributor should establish a verified baseline before making major architectural changes.

## 17. Final Instruction

Continue ProofSkill AI as a careful engineering collaborator.

Preserve evidence integrity, fairness, privacy, and explainability. Follow the existing architecture where practical, verify behavior before claiming success, and prioritize a reliable end-to-end demonstration over unnecessary complexity.

**The objective is a working, explainable, and trustworthy assessment workflow—not merely a large collection of documentation or AI-generated code.**
