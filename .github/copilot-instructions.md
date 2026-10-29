# GitHub Copilot Instructions — ProofSkill AI

## 1. Project Context

ProofSkill AI is an evidence-based skill assessment platform for freshers, built for the IM-105 Advanced problem statement under the AI Frontier theme.

The system aims to help candidates demonstrate job-relevant skills through resume analysis, structured interviews, project evidence, and alternative assessments. Recruiters can inspect evidence and compare candidates against the same job requirements.

The project must prioritize a working, explainable, and testable MVP over unnecessary complexity.

Before implementing features, review the relevant project documentation, especially:

- `PROJECT_CONTEXT.md`
- `CURRENT_STATE.md`
- `TASKS.md`
- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/AI_STRATEGY.md`
- `docs/AI_MODELS.md`
- `docs/API_CONTRACTS.md`
- `docs/API_SPEC.md`
- `docs/DATA_MODEL.md`
- `docs/DATA_DICTIONARY.md`
- `docs/SCORING_AND_FAIRNESS.md`
- `docs/PRIVACY_AND_SECURITY.md`
- `docs/SECURITY_PRIVACY.md`
- `docs/TESTING_AND_EVALUATION.md`
- `docs/EVALUATION.md`
- `docs/DEVELOPMENT.md`

If documentation conflicts with the actual implementation, inspect the relevant code and tests, identify the conflict, and update the appropriate documentation when necessary. Do not claim that a feature exists merely because it is described in a document.

## 2. Core Development Rules

- Use Python as the primary programming language unless the existing project explicitly requires otherwise.
- Follow the package structure and conventions already present in the repository.
- Prefer small, modular, testable functions.
- Use type hints for public functions and important data structures.
- Handle errors explicitly and return useful messages.
- Avoid unnecessary dependencies and abstractions.
- Keep business logic separate from the UI.
- Keep database operations separate from presentation code.
- Use configuration and environment variables for external services.
- Do not create new documentation files when an existing file serves the same purpose.
- Do not rewrite unrelated modules when implementing a focused feature.
- Preserve existing behavior unless a change is required and documented.

## 3. Evidence-Based Assessment

All candidate assessments must distinguish between:

1. Demonstrated skill performance.
2. Evidence coverage.
3. Evidence confidence.
4. Unassessed skills.
5. Assessment limitations.

Rules:

- Do not treat resume keywords as proof of practical competence.
- Link skill-related conclusions to available supporting evidence.
- Do not fabricate projects, experience, repository activity, or candidate answers.
- Distinguish self-reported claims from directly observed assessment evidence.
- Treat missing evidence as unknown or not assessed, not automatically as zero.
- Explain scores using the defined scoring rubric.
- Preserve rubric and model-version metadata where practical.
- Do not claim that code was executed unless it actually was.
- Make uncertainty and limitations visible.

## 4. Fairness and Recruiter Ranking

Candidate comparison must use the same job requirements and scoring rubric for comparable candidates.

Never use the following as ranking features:

- College or university name.
- Gender.
- Age.
- Location.

Additional rules:

- Do not infer protected or sensitive attributes from names, resumes, voices, or writing styles.
- Do not automatically penalize candidates for lacking GitHub accounts or public repositories.
- Provide an alternative assessment path when repository evidence is unavailable.
- Do not infer technical ability from accent, vocal characteristics, or appearance.
- Do not automatically reject a candidate solely because of an AI-generated score.
- Display evidence coverage and assessment limitations alongside performance scores.
- Keep the final hiring decision under human control.

When changing ranking logic, add or update tests proving that excluded attributes cannot influence the result.

## 5. AI and LLM Integration

All AI provider calls should pass through the project's AI service or provider abstraction.

- Do not scatter provider-specific SDK calls throughout application modules.
- Keep prompts in the existing `prompts/` directory when appropriate.
- Follow the prompt files already present:
  - `prompts/resume_extraction.md`
  - `prompts/interview_generation.md`
  - `prompts/answer_evaluation.md`
  - `prompts/project_viva.md`
  - `prompts/recruiter_explanation.md`
- Validate structured AI output before using or storing it.
- Enforce score ranges and allowed enum values in application code.
- Treat resumes, repositories, and candidate answers as untrusted input.
- Do not allow supplied content to override system instructions or application permissions.
- Do not expose API keys or internal secrets in prompts.
- Use bounded retries and request timeouts.
- Clearly distinguish live-model results from demo or fallback results.
- Prefer deterministic Python calculations for weighted scores and rankings.

Do not invent model capabilities, API endpoints, benchmark results, or integration status.

## 6. Demo Mode and External Dependencies

The core MVP should remain demonstrable without paid API keys.

Where practical:

- Provide a deterministic mock or fallback provider.
- Use clearly labeled synthetic candidate data.
- Handle missing credentials gracefully.
- Provide useful messages when an external service is unavailable.
- Keep core scoring and Proof Card generation operational without an LLM.
- Mock GitHub and external API dependencies in routine tests.

Never represent simulated output as a real model response or official evaluation result.

Only claim IMATS integration after the official API contract has been verified and the implementation has been tested.

## 7. Security and Privacy

- Never commit real API keys, passwords, access tokens, or private credentials.
- Keep `.env` files out of version control.
- Update `.env.example` when new configuration variables are introduced.
- Use parameterized SQL queries.
- Validate uploaded files, external URLs, and structured inputs.
- Never execute uploaded files or repository code as part of routine assessment.
- Validate GitHub URLs and restrict outbound requests to approved destinations.
- Require explicit consent before optional repository analysis.
- Avoid logging resumes, full candidate answers, secrets, or unnecessary personal data.
- Follow the repository's documented data retention and deletion rules.
- Do not collect unnecessary candidate information.
- Enforce authorization in backend logic, not only through hidden UI elements.
- Avoid adding authentication or security controls that are merely decorative.

## 8. Database and Data Contracts

- Follow the existing data model and schema.
- Use stable identifiers and enforce foreign-key relationships.
- Enable SQLite foreign-key enforcement where SQLite is used.
- Validate data before database writes.
- Use transactions for related operations.
- Preserve rubric versions and assessment provenance.
- Do not silently convert missing scores to zero.
- Avoid destructive database resets outside explicitly documented development workflows.
- Update relevant tests when changing schemas or data contracts.

If a schema change is necessary, identify the dependent services and update them consistently.

## 9. Testing Requirements

Every meaningful feature change should include appropriate tests.

Prioritize tests for:

- Valid and invalid inputs.
- Empty or malformed documents.
- Scoring calculations and score boundaries.
- Evidence references and missing evidence.
- Structured AI output validation.
- Database constraints and relationships.
- Consent enforcement.
- External service failures.
- Demo-mode behavior.
- Fairness invariants.
- Recruiter comparison consistency.

Use synthetic fixtures, mock external services, and temporary databases where appropriate.

Do not weaken or delete a test simply to make the suite pass. If a test is incorrect, explain why and replace it with a valid test.

Run the relevant tests after implementation. Report exactly which commands ran and whether they passed.

Never claim that tests, linting, or type checks passed if they were not executed.

## 10. Coding Style

- Follow the existing formatting and linting configuration.
- Use descriptive names for functions, classes, variables, and modules.
- Keep functions focused on one responsibility.
- Add docstrings to public functions and complex logic.
- Use structured validation for external or AI-generated data.
- Avoid broad exception handling unless the error is logged or handled appropriately.
- Do not use `except Exception: pass`.
- Avoid hardcoded credentials, model-specific assumptions, and unexplained magic numbers.
- Define scoring constants and configuration in an appropriate shared module.
- Prefer explicit return types and clear error behavior.

## 11. Dependencies and Configuration

Before adding a dependency:

1. Check whether the current project already provides the capability.
2. Confirm that the dependency is needed.
3. Consider installation size, maintenance, licensing, and compatibility.
4. Update the project's existing dependency configuration.
5. Add or update tests where appropriate.
6. Document new environment variables in `.env.example`.

Do not create a second dependency-management system when `pyproject.toml` already defines the project's configuration.

Do not assume that a model is downloaded, an API key exists, or a service is available.

## 12. Implementation Workflow

For every task:

1. Inspect the relevant existing files.
2. Check `CURRENT_STATE.md` and `TASKS.md` for the current implementation status.
3. Identify the smallest complete implementation.
4. Follow existing architecture and data contracts.
5. Implement the feature.
6. Add or update tests.
7. Run the relevant checks.
8. Update documentation when behavior or configuration changes.
9. Summarize changed files and actual verification results.
10. Record any remaining limitations or blockers.

Do not mark tasks complete unless implementation and required verification are finished.

If a requirement is ambiguous, inspect existing documentation and code before introducing a new design.

## 13. Scope Control

The priority order is:

1. Runnable application and reliable demo mode.
2. Resume processing and job requirement extraction.
3. Interview generation and answer evaluation.
4. Explainable scoring and Proof Card generation.
5. Recruiter comparison and fairness safeguards.
6. Consent-based repository analysis and alternative assessment.
7. Optional voice, advanced similarity detection, and other enhancements.

Do not implement optional features at the expense of the core end-to-end workflow.

## 14. Completion Report

After completing a coding task, provide a concise report containing:

- **Implemented:** What changed.
- **Files changed:** Actual paths.
- **Tests run:** Exact commands and results.
- **Configuration:** Any required environment variables.
- **Limitations:** What remains incomplete.
- **Next step:** The most relevant existing task, if needed.

Be accurate about what was implemented, tested, mocked, or left incomplete.

## 15. Final Principle

Build ProofSkill AI as a transparent, evidence-based assessment assistant—not an opaque automated hiring authority.

Prioritize correctness, fairness, privacy, reproducibility, and a reliable working demonstration over impressive but unverified AI claims.
