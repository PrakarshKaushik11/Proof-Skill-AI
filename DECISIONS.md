# ProofSkill AI — Architecture and Product Decisions

## 1. Purpose

This document records the important product, architecture, AI, data, security, and development decisions for ProofSkill AI.

The goals are to:
- Keep technical decisions consistent across contributors.
- Explain why a particular approach was selected.
- Document trade-offs and limitations.
- Reduce unnecessary architectural changes.
- Help developers and AI coding agents understand project constraints.
- Distinguish proposed decisions from implementation that has actually been verified.

Individual architectural decisions may also be recorded under `docs/ADR/`.

## 2. Decision Status

Use the following status labels:

- **Proposed:** Recommended approach that may require implementation or confirmation.
- **Accepted:** Agreed project direction.
- **Implemented:** Present in the codebase but not necessarily fully tested.
- **Verified:** Implementation has been checked through appropriate evidence or tests.
- **Superseded:** Replaced by a newer decision.

The status of a decision must not be interpreted as proof that the corresponding feature is operational.

---

## D-001 — Evidence-Based Skill Assessment

**Status:** Accepted

### Decision

Candidate assessments should connect skill claims to available evidence wherever possible.

Evidence may include:
- Resume statements.
- Project descriptions.
- Consented repository evidence.
- Technical interview answers.
- Project viva responses.
- Other explicitly authorized assessment results.

### Rationale

A resume alone does not establish practical proficiency. Evidence-backed explanations can help recruiters understand what has been demonstrated and what remains uncertain.

### Consequences

- Assessment outputs should include evidence references where available.
- Self-reported claims must remain distinguishable from independently verified evidence.
- Missing evidence must not automatically be treated as a lack of ability.
- Recruiter-facing explanations must communicate uncertainty.

---

## D-002 — Human Oversight for Hiring Decisions

**Status:** Accepted

### Decision

ProofSkill AI should assist candidate assessment and recruiter review, not independently make final hiring or rejection decisions.

### Rationale

AI-generated assessments can be incomplete, inconsistent, or incorrect. Hiring decisions require appropriate human judgment and accountability.

### Consequences

- The system should explain the basis of its outputs.
- Scores must not be presented as definitive measures of candidate potential.
- Human review must remain part of hiring-related decision workflows.
- Any thresholds or ranking rules must be documented and job-relevant.

---

## D-003 — Python as the Primary Language

**Status:** Proposed

### Decision

Use Python as the primary language for application logic and AI-related workflows.

### Rationale

Python supports document processing, NLP, model integrations, data processing, and automated testing through a broad ecosystem of libraries.

### Consequences

- Application logic should follow consistent Python conventions.
- Dependencies should be managed through the existing `pyproject.toml`.
- New packages should be added only when they provide a clear benefit.
- Existing implementation choices should be checked before introducing new frameworks.

---

## D-004 — Streamlit for the Initial Interface

**Status:** Proposed

### Decision

Use Streamlit for the initial user interface if it remains compatible with the existing implementation and project requirements.

### Rationale

Streamlit can support rapid development of a hackathon demonstration without requiring a separate frontend application.

### Consequences

- Prioritize a clear end-to-end demonstration flow.
- Keep business logic separate from presentation code where practical.
- Show loading, validation, empty, and error states.
- Clearly distinguish synthetic demo results from real assessments.

### Trade-off

A rapid prototype may need architectural changes if future requirements demand complex user management, extensive frontend customization, or a larger production deployment.

---

## D-005 — SQLite for Initial Local Persistence

**Status:** Proposed

### Decision

Use SQLite for the initial local prototype unless the existing codebase or deployment requirements establish a better option.

### Rationale

SQLite offers a simple local database with minimal setup, making it suitable for early development and demonstrations.

### Consequences

- Use parameterized SQL queries.
- Define a consistent schema and data validation rules.
- Use transactions for related database operations.
- Avoid storing unnecessary raw candidate information.
- Reassess the database choice if concurrency, access control, or deployment needs exceed the prototype's requirements.

### Limitation

The choice of SQLite does not by itself establish that the application has secure persistence, appropriate access controls, or production readiness.

---

## D-006 — Configurable AI Provider

**Status:** Accepted

### Decision

Keep AI provider configuration separate from core application logic.

### Rationale

A configurable provider makes it easier to test different supported models and handle unavailable external services.

### Consequences

- Read credentials and model configuration from environment variables.
- Do not hard-code provider secrets.
- Validate provider configuration before attempting requests.
- Apply timeouts and bounded retries.
- Validate all model outputs before using them.
- Provide deterministic fallback behavior where appropriate.

### Limitation

A provider is not considered integrated merely because configuration variables exist. The actual request, response handling, error behavior, and tests must be verified.

---

## D-007 — Structured Prompt Contracts

**Status:** Accepted

### Decision

Each major AI workflow should have a documented prompt and an explicit input/output contract.

The existing prompt library covers:
- Resume extraction.
- Interview generation.
- Answer evaluation.
- Project viva generation.
- Recruiter explanations.

### Rationale

Separate prompt contracts make workflows easier to test, maintain, and integrate with application code.

### Consequences

- Reuse the relevant existing prompt rather than duplicating its instructions in unrelated modules.
- Validate required fields and data types.
- Verify evidence references.
- Handle malformed or incomplete model responses.
- Coordinate prompt changes with dependent application code.
- Keep schemas consistent between prompts and their consumers.

---

## D-008 — Evidence Status Must Remain Explicit

**Status:** Accepted

### Decision

The system must distinguish self-reported claims, inspected evidence, assessed skills, and information that has not been assessed.

### Rationale

Different evidence sources support different levels of confidence. Combining them without distinction can produce misleading conclusions.

### Consequences

- A resume claim must not automatically become a verified skill.
- Repository access must not automatically establish personal authorship.
- Missing evidence must be labeled as missing or unassessed.
- Conflicting evidence should be surfaced for clarification.
- AI-generated inferences must not be presented as direct observations.

---

## D-009 — Explainable Skill Matching

**Status:** Accepted

### Decision

Candidate-to-job matching should be based on documented job requirements and relevant evidence.

### Rationale

Recruiters should be able to understand why a skill is considered supported, partially supported, or not yet assessed.

### Consequences

- Match scores must follow an explicit methodology.
- Do not invent scores when required inputs are missing.
- Separate required skills from preferred skills.
- Provide evidence references and limitations.
- Do not describe a match score as a probability of future job success unless independently validated for that purpose.

---

## D-010 — Fair Assessment Without Public Repository Access

**Status:** Accepted

### Decision

Candidates without public GitHub repositories must have an alternative opportunity to demonstrate relevant skills.

### Rationale

Public code availability depends on personal choices, privacy, resources, and circumstances. It is not a complete measure of technical ability.

### Consequences

- Support scenario-based questions, practical exercises, or verbal project walkthroughs.
- Do not assign a negative skill conclusion solely because repository evidence is unavailable.
- Make the evidence source clear when comparing assessment results.
- Apply comparable job-relevant criteria across candidates.

---

## D-011 — Fairness Constraints on Candidate Assessment

**Status:** Accepted

### Decision

Use job-relevant evidence and explicit assessment criteria rather than protected characteristics or unrelated personal attributes.

### Rationale

Assessment should focus on demonstrated competencies rather than demographic assumptions or subjective impressions.

### Consequences

Do not use the following as proxies for technical ability:
- Gender, age, caste, religion, race, or other protected characteristics.
- College prestige.
- Family or socioeconomic background.
- Accent, facial appearance, or emotional expression.
- Personality assumptions, charisma, or subjective cultural fit.

Speech transcription, if used, should focus on the technical meaning of an answer rather than accent or vocal characteristics.

---

## D-012 — Consent-Based Repository Access

**Status:** Accepted

### Decision

Repository access must respect candidate consent, repository permissions, and the minimum access needed for the assessment.

### Rationale

Repository contents may be private, confidential, or unrelated to the assessment.

### Consequences

- Request only the necessary permissions.
- Handle inaccessible repositories gracefully.
- Do not expose private repository content to unauthorized users.
- Do not execute repository code merely to inspect it.
- Distinguish repository presence from verified personal contribution.

---

## D-013 — Environment-Based Configuration and Secrets

**Status:** Accepted

### Decision

Store environment-specific configuration and credentials outside application source code.

### Rationale

Hard-coded credentials increase the risk of accidental exposure and make configuration less portable.

### Consequences

- Use `.env.example` for safe configuration documentation.
- Keep real credentials in a local environment file or approved secret manager.
- Never commit real API keys or passwords.
- Validate required configuration at startup.
- Avoid exposing secrets in logs and error messages.

---

## D-014 — Demo Mode and Synthetic Data

**Status:** Accepted

### Decision

Where demo mode is supported, use clearly labeled synthetic data and predictable fallback behavior for unavailable optional services.

### Rationale

A hackathon demonstration should remain usable when external credentials, network access, or model services are unavailable.

### Consequences

- Mark synthetic profiles and simulated assessments clearly.
- Never present synthetic evidence as verified candidate evidence.
- Keep demo behavior separate from live integrations.
- Ensure fallback results follow the expected application schema.
- Report actual integration status honestly.

---

## D-015 — Automated Testing with pytest

**Status:** Proposed

### Decision

Use pytest for automated testing, subject to the existing test configuration.

### Rationale

Automated tests help identify regressions in extraction, validation, scoring, persistence, and error handling.

### Consequences

Tests should cover:
- Normal inputs and expected outputs.
- Missing and malformed inputs.
- Invalid model responses.
- Evidence-reference validation.
- Fairness and privacy constraints.
- External-service failures.
- Database errors.
- Demo-mode behavior.

A test must not be reported as passing unless it has actually been executed and its result confirmed.

---

## D-016 — Avoid Unnecessary Dependencies

**Status:** Accepted

### Decision

Prefer the existing dependency set and introduce new packages only when needed.

### Rationale

Unnecessary dependencies increase installation time, compatibility risks, maintenance effort, and the possibility of environment-specific failures.

### Consequences

- Inspect `pyproject.toml` before adding packages.
- Prefer lightweight alternatives when they satisfy the requirement.
- Avoid downloading large models unless the feature requires them.
- Document meaningful dependency changes.
- Test the application after changing dependencies.

---

## D-017 — Data Minimization and Privacy

**Status:** Accepted

### Decision

Process and retain only the candidate data needed for the documented assessment purpose.

### Rationale

Resume documents, repository content, and assessment responses may contain personal or confidential information.

### Consequences

- Avoid storing raw documents or audio unless necessary and authorized.
- Use candidate identifiers where practical.
- Restrict access to candidate records.
- Avoid unnecessary sensitive information in prompts and logs.
- Follow the project's retention and deletion policies.
- Review external model-provider data handling before sending candidate information.

---

## D-018 — No Unsupported Claims About Integrations

**Status:** Accepted

### Decision

External integrations must be implemented and verified against their actual contracts before being described as operational.

### Rationale

Configuration templates and design documents do not establish that a service is connected or working.

### Consequences

- Do not invent API endpoints, credentials, or response fields.
- Validate external request and response formats.
- Handle timeouts, rate limits, and authorization failures.
- Distinguish mock responses from live responses.
- Record actual integration and test status in the project documentation.

This applies to AI providers, GitHub, speech transcription, and the IMATS sandbox API.

---

## D-019 — Small, Focused Changes

**Status:** Accepted

### Decision

Prefer the smallest correct change that satisfies the requested task.

### Rationale

Focused changes reduce regression risk and make code review easier.

### Consequences

- Inspect existing files before editing.
- Reuse established modules and interfaces.
- Avoid duplicating functionality.
- Do not modify unrelated files without a clear need.
- Do not create additional files unless explicitly requested or genuinely necessary and authorized.
- Update relevant documentation when behavior changes.

---

## D-020 — Implementation Status Must Be Evidence-Based

**Status:** Accepted

### Decision

Project status documents must distinguish planned, implemented, and verified functionality.

### Rationale

Accurate status reporting is essential for development, testing, handoffs, and hackathon demonstrations.

### Consequences

- A documented design is not proof of implementation.
- A code snippet is not proof of successful execution.
- Installed dependencies are not proof of a working integration.
- Tests must have actual results before being reported as passing.
- Known limitations must be communicated explicitly.

---

## 3. Revisiting Decisions

A decision may be revisited when:
- Requirements materially change.
- The current approach causes a verified technical problem.
- Testing reveals unacceptable limitations.
- Deployment constraints require a different architecture.
- A more appropriate option offers a clear benefit.

When changing a significant decision:

1. Explain the problem with the current approach.
2. Describe the proposed alternative.
3. Identify compatibility and migration risks.
4. Update the relevant existing documentation.
5. Record the decision change in the changelog when appropriate.

Do not silently replace established interfaces or architectural choices.

## 4. Current Implementation Caveat

This document records project direction and decision rationale. It does not establish that every decision has been implemented or verified.

The actual source code, configuration, tests, and integration results determine the current implementation status.

