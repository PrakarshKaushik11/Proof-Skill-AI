# ProofSkill AI — Current State

**Project:** ProofSkill AI  
**Hackathon:** Deviathon 2.0  
**Problem Statement:** IM-105 Advanced — Integraminds  
**Theme:** AI FRONTIER  
**Track:** Software  
**Status:** Documentation scaffold; application implementation not started
**Last Updated:** 2026-10-29

---

## 1. Project Summary

ProofSkill AI is designed to help recruiters evaluate fresher candidates using evidence-backed skills, structured technical assessments, project understanding, and job-specific requirements.

The system aims to make candidate evaluation more transparent by connecting resume claims with available repository evidence and assessment results.

The intended outcome is an explainable skill profile that supports recruiter review rather than an opaque, automated hiring decision.

## 2. Problem Being Addressed

Traditional fresher recruitment may rely heavily on resumes, educational credentials, and subjective interviews. These signals do not always provide sufficient evidence of practical skills.

ProofSkill AI aims to address this problem by:

- Extracting structured skills and project claims from resumes.
- Connecting claims to available supporting evidence.
- Generating adaptive technical interviews.
- Creating project-specific viva questions.
- Evaluating answers against explicit rubrics.
- Explaining candidate-to-job alignment.
- Supporting candidates who do not have public GitHub repositories.
- Promoting consistent, fair, and evidence-based assessments.

These are project objectives, not a statement that every feature is already operational.

## 3. Repository and Documentation Status

The repository currently contains project documentation, prompt definitions, configuration examples, and directories intended for application code, tests, scripts, notebooks, and deployment resources. The `src/`, `tests/`, `scripts/`, `deploy/`, `notebooks/`, and `.agents/` directories are empty; no application or test code is present.

Documented files include:

- `README.md`
- `PROJECT_CONTEXT.md`
- `TASKS.md`
- `AGENTS.md`
- `HANDOFF.md`
- `DECISIONS.md`
- `CHANGELOG.md`
- `.env.example`
- `pyproject.toml`
- `.github/copilot-instructions.md`
- `data/MANIFEST.yaml`
- `data/README.md`
- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/DATA_MODEL.md`
- `docs/SCORING_AND_FAIRNESS.md`
- `docs/AI_STRATEGY.md`
- `docs/AI_MODELS.md`
- `docs/API_CONTRACTS.md`
- `docs/API_SPEC.md`
- `docs/DATA_DICTIONARY.md`
- `docs/DATASETS.md`
- `docs/DEVELOPMENT.md`
- `docs/EVALUATION.md`
- `docs/PRIVACY_AND_SECURITY.md`
- `docs/SECURITY_PRIVACY.md`
- `docs/TESTING_AND_EVALUATION.md`
- `docs/RUNBOOK.md`
- `docs/USER_FLOWS.md`
- `docs/CHANGELOG.md`
- `docs/ADR/0001-initial-architecture.md`
- `prompts/README.md`
- `prompts/resume_extraction.md`
- `prompts/interview_generation.md`
- `prompts/answer_evaluation.md`
- `prompts/project_viva.md`
- `prompts/recruiter_explanation.md`

The repository also contains directories for `src`, `tests`, `scripts`, `notebooks`, `deploy`, `.agents`, and `docs/ADR`.

**Important:** The presence of a directory or documentation file does not prove that application code, integrations, or tests are complete. In this checkout, the application and test directories are empty.

## 4. Planned Technical Direction

The documented technical direction includes:

| Component | Intended approach |
|---|---|
| Programming language | Python |
| Initial interface | Streamlit, where appropriate |
| Local persistence | SQLite |
| Resume processing | PyMuPDF and `python-docx` |
| NLP and semantic matching | spaCy and Sentence Transformers |
| AI assessment | Configurable language-model integration |
| Repository evidence | GitHub API with appropriate consent |
| Speech transcription | Optional, when configured |
| Automated testing | pytest |
| Configuration | Environment variables and `.env.example` |

The actual implementation and installed dependencies must be verified before treating this table as the final running stack.

## 5. Intended Core Workflows

### 5.1 Resume extraction

Extract skills, projects, experience, education, and relevant claims from supplied resume text.

Expected safeguards:
- Preserve evidence references.
- Distinguish self-reported claims from independently verified information.
- Handle missing or malformed text.
- Avoid inventing candidate qualifications.

### 5.2 Evidence collection

Associate candidate claims with available assessment and repository evidence.

Expected safeguards:
- Respect consent and access permissions.
- Do not assume repository presence proves authorship.
- Record unavailable evidence as unavailable.
- Provide alternatives for candidates without public repositories.

### 5.3 Adaptive technical interview

Generate role-specific questions and follow-ups based on available evidence and previous answers.

Expected safeguards:
- Use clear evaluation criteria.
- Avoid unnecessary duplicate questions.
- Adjust difficulty reasonably.
- Keep questions relevant to the target role.

### 5.4 Project viva

Generate questions about project purpose, architecture, implementation, debugging, testing, and improvements.

Expected safeguards:
- Refer only to supplied code or repository evidence.
- Never invent file paths or implementation details.
- Offer conceptual or scenario-based alternatives when code is unavailable.

### 5.5 Answer evaluation

Evaluate answers using explicit, question-specific rubrics.

Expected safeguards:
- Explain scores.
- Accept technically valid alternative answers.
- Distinguish incorrect answers from ambiguous questions.
- Do not score candidates based on accent, confidence, or answer length alone.

### 5.6 Recruiter explanation

Summarize how available evidence relates to the requirements of a specific job.

Expected safeguards:
- Explain supported and unassessed skills.
- Preserve the supplied scoring methodology.
- Do not invent match percentages.
- Require human review for hiring-related decisions.

## 6. AI and Data Integrity

The project's documented AI approach emphasizes:

- Structured model inputs and outputs.
- JSON parsing and schema validation.
- Evidence traceability.
- Explicit treatment of uncertainty.
- Bounded retries for recoverable errors.
- Deterministic fallback behavior where appropriate.
- Separation of model-generated explanations from verified facts.
- Protection against instructions embedded in untrusted documents.

Actual prompt integration, model selection, validation, and fallback behavior must be confirmed in the implementation.

## 7. Fairness, Privacy, and Security

The intended safeguards include:

- Job-relevant assessment criteria.
- Consistent scoring rubrics.
- No demographic inference for skill evaluation.
- No use of college prestige as a substitute for demonstrated skills.
- No personality or competence inference from accent or appearance.
- Consent before accessing restricted repositories.
- Data minimization and appropriate retention controls.
- Environment-based secret management.
- Validation of uploaded files and model outputs.
- Human oversight rather than autonomous hiring decisions.

These safeguards require implementation and testing; documentation alone does not establish enforcement.

## 8. Configuration and Integrations

The existing `.env.example` documents configuration options for the application, database, AI provider, embeddings, GitHub integration, assessment defaults, privacy controls, speech transcription, and testing.

Current configuration values and supported integrations should be checked against the actual code.

Do not assume that an external AI provider, GitHub integration, speech transcription service, or IMATS sandbox API is connected simply because configuration variables or documentation exist.

Real credentials must not be committed to version control.

## 9. Verified Versus Unverified Status

Based on the repository structure and documentation available for this project, the following distinction is necessary:

| Area | Current documented status |
|---|---|
| Project objectives | Documented |
| Prompt definitions | Present in the documented repository structure |
| Architecture and data design | Documented |
| Fairness and privacy requirements | Documented |
| Environment template | Present |
| Application source code | No files present under `src/` |
| Application startup and Streamlit UI | Not implemented |
| Database initialization | Not implemented |
| Resume extraction execution | Not implemented |
| Live AI provider integration | Not implemented |
| GitHub integration | Not implemented |
| Interview and viva execution | Not implemented |
| Answer scoring execution | Not implemented |
| Recruiter matching execution | Not implemented |
| Automated test files | No files present under `tests/` |
| Automated test results | No tests available to run |
| Deployment | Not verified here |
| IMATS sandbox integration | Not verified here |

“Not implemented” above reflects the absence of application source files in this checkout; the documentation describes intended behavior, not an operational feature.

## 10. Recommended Implementation Priorities

Use these priorities after checking the current codebase and `TASKS.md`.

### Priority 1 — Establish a runnable baseline

- Inspect the existing source code and project configuration.
- Confirm dependency installation.
- Verify the application's startup command.
- Confirm that demo mode works without optional external credentials.
- Resolve startup errors before adding more features.

### Priority 2 — Complete the main candidate workflow

- Implement or verify resume upload and text extraction.
- Normalize extracted information into the documented data model.
- Display extracted claims with their evidence status.
- Handle empty, malformed, and unsupported files.

### Priority 3 — Complete assessment workflows

- Connect interview generation to its prompt contract.
- Connect project viva generation to available evidence.
- Validate model responses.
- Implement answer evaluation with explicit rubrics.
- Add deterministic fallback behavior for unavailable model services.

### Priority 4 — Complete recruiter workflow

- Map skills to job-description requirements.
- Explain evidence supporting each match.
- Distinguish missing evidence from missing ability.
- Provide transparent comparison using the same criteria for each candidate.
- Keep human review in the decision process.

### Priority 5 — Verify quality and integrations

- Run relevant automated tests.
- Test malformed inputs and unavailable services.
- Verify privacy and authorization controls.
- Confirm scoring behavior against representative cases.
- Validate external integrations against their real documented contracts.
- Document actual results and remaining limitations.

These are recommended priorities, not a claim that the listed work is necessarily unfinished.

## 11. Definition of Current Readiness

The project should be considered ready for a live demonstration only after verifying that:

- The application starts successfully.
- The primary workflow can be completed end to end.
- Demo data is clearly labeled as synthetic.
- AI failures are handled gracefully.
- Candidate evidence and scores are traceable.
- No secrets are exposed.
- Relevant tests have been run and their results recorded.
- Unsupported features are clearly identified.
- Human oversight and fairness constraints are reflected in actual behavior.

A production-readiness claim requires additional security, reliability, privacy, and operational validation.

## 12. Immediate Next Action

Inspect the existing source files, dependency configuration, and test suite to establish the actual implementation status.

Update this file when there is new verified information, such as:
- A successfully executed startup command.
- A completed end-to-end workflow.
- An integration confirmed against a real service.
- A test suite run with recorded results.
- A resolved bug or known limitation.

Keep this document concise enough for contributors and coding agents to understand the project's real state quickly.

## 13. Maintenance Rule

Update `CURRENT_STATE.md` whenever a material implementation milestone changes the project's verified status.

Clearly distinguish:
- Implemented and verified.
- Implemented but not yet verified.
- Planned.
- Blocked.
- Not applicable.

Never mark a feature complete based solely on its documentation, a generated code snippet, or the presence of a configuration variable.
