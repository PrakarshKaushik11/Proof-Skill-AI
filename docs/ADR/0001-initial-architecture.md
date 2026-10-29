# ADR 0001: Initial Architecture for ProofSkill AI

- **Status:** Accepted — initial design
- **Date:** 2026-10-29
- **Decision owners:** ProofSkill AI team
- **Scope:** Initial hackathon implementation

## 1. Context

ProofSkill AI is an AI-assisted skill assessment platform designed to help freshers demonstrate their practical abilities through multiple forms of evidence.

Traditional screening may over-rely on resumes, educational background, or unstructured interviews. These signals do not always provide sufficient evidence of practical competence.

The system aims to combine candidate-provided resume information, project evidence, technical assessments, and structured interviews into an explainable skill profile. Recruiters should be able to compare candidates against the same job-specific criteria while retaining responsibility for final hiring decisions.

The initial architecture must be practical for a hackathon, straightforward to demonstrate, and extensible enough to support more advanced integrations later.

## 2. Decision Drivers

The architecture should:

1. Support a working end-to-end demonstration with limited setup.
2. Keep candidate evidence separate from inferred skills and assessment scores.
3. Provide explainable, job-relevant evaluation results.
4. Support candidates who do not have public GitHub repositories.
5. Protect candidate data and require authorization for private evidence.
6. Avoid making unsupported claims when information is missing.
7. Allow optional AI providers without making the application entirely dependent on one provider.
8. Support deterministic tests and a demo mode when external services are unavailable.
9. Keep data processing modular so individual components can be tested independently.
10. Avoid fully automated hiring decisions.

## 3. Decision

Use a modular Python application with a lightweight user interface, explicit service boundaries, and a local persistence layer for the initial implementation.

The proposed stack is:

| Layer | Initial choice | Responsibility |
|---|---|---|
| User interface | Streamlit | Candidate and recruiter workflows |
| Application logic | Python modules | Orchestrate workflows and enforce rules |
| Resume processing | PyMuPDF and python-docx | Extract text from supported documents |
| Text processing | Rule-based extraction with optional spaCy | Identify skills, qualifications, and evidence |
| Semantic matching | Sentence-Transformers MiniLM, when available | Compare skill and job-description text |
| AI generation | Configurable LLM provider | Generate questions and evidence-based explanations |
| Speech processing | Optional speech-to-text integration | Convert consented audio responses into text |
| Repository evidence | GitHub REST API, with authorization | Retrieve permitted repository metadata or content |
| Persistence | SQLite for the initial prototype | Store structured application records |
| Validation | pytest | Test scoring, parsing, privacy safeguards, and workflows |
| External integration | Configurable IMATS sandbox adapter | Connect to the supplied sandbox contract when available |

These are architectural choices for the initial design, not claims that every integration has already been implemented or verified. Actual dependencies and available services must be confirmed against the repository and the hackathon environment.

## 4. High-Level Architecture

The application is divided into the following logical components:

1. **Presentation layer:** Collects inputs and displays candidate profiles, evidence, assessments, and recruiter comparisons.
2. **Workflow layer:** Coordinates resume ingestion, assessment, profile generation, and job-specific comparison.
3. **Evidence processing layer:** Extracts and normalizes information from resumes, project descriptions, repository evidence, and assessment responses.
4. **Assessment layer:** Applies documented rubrics to technical answers and other job-relevant evidence.
5. **Scoring layer:** Calculates transparent criterion-level scores and identifies missing or insufficient evidence.
6. **AI adapter layer:** Provides optional question generation, semantic analysis, and explanations through configurable providers.
7. **Persistence layer:** Stores structured records with stable identifiers and appropriate access controls.
8. **Integration layer:** Encapsulates external API calls, including repository and IMATS sandbox integrations.
9. **Evaluation layer:** Validates outputs, runs regression tests, and measures quality and fairness.

The components should communicate through explicit functions or service interfaces rather than embedding all business logic in the UI.

## 5. Core Workflow

The intended end-to-end workflow is:

1. A candidate provides a resume or enters their skills and project details manually.
2. The application extracts candidate claims and preserves references to their source evidence where possible.
3. The candidate may provide project or repository evidence with the required authorization.
4. The application generates or selects job-relevant technical questions.
5. The candidate completes an assessment using supported input methods.
6. The assessment service evaluates responses against a documented rubric.
7. The profile service consolidates evidence, assessment results, confidence, and evidence gaps.
8. A recruiter selects a job description and reviews candidate evidence against its requirements.
9. The application presents explainable comparisons and limitations, leaving the final decision to the recruiter.

Candidates without repository evidence must have an alternative path through manual project descriptions, uploaded artifacts, or structured technical assessments.

## 6. Evidence and Scoring Principles

The system must distinguish between:

- **Candidate claim:** Information stated by the candidate.
- **Observed evidence:** Information extracted from an authorized source or assessment.
- **Assessment result:** A rubric-based evaluation of observed work or responses.
- **Model inference:** An AI-generated interpretation that may contain errors.
- **Verified fact:** Information checked against an appropriate source or validation process.

These categories must not be treated as interchangeable.

Scores should be based on documented, job-relevant criteria. Each displayed score should provide an explanation of its contributing evidence, limitations, and missing information where applicable.

The scoring process must not use college name, gender, age, location, accent, or other irrelevant personal attributes as proxies for ability. Protected or sensitive attributes must not be inferred for scoring.

If evidence is insufficient, the system should report that limitation rather than fabricate evidence or assign unwarranted certainty.

Detailed scoring rules are maintained in `docs/SCORING_AND_FAIRNESS.md`.

## 7. AI Provider Strategy

AI capabilities should be accessed through adapter functions with defined inputs and outputs.

This approach allows the application to:

- Switch providers without rewriting the workflow layer.
- Validate structured model outputs.
- Handle rate limits, unavailable services, and malformed responses.
- Use deterministic fallback behavior for demonstrations and tests.
- Record which processing method produced a result.
- Separate AI-generated explanations from authoritative application records.

AI-generated questions, summaries, and explanations must be treated as suggestions that require validation. They must not invent candidate achievements, repository activity, citations, or assessment results.

The application must not claim that a model is accurate or unbiased without evaluation evidence.

## 8. Data Storage

SQLite is the proposed initial persistence mechanism because it is lightweight and suitable for a local prototype.

Records should use stable identifiers and explicit relationships for candidates, job descriptions, evidence items, assessments, and generated profiles.

The design should support:

- Provenance for evidence items.
- Timestamps for relevant operations.
- Separation of raw evidence from derived scores.
- Minimal retention of sensitive information.
- Controlled access to candidate records.
- Future migration to a more suitable database if deployment requirements grow.

Raw documents, recordings, and private repository contents should not be retained longer than necessary. The exact storage policy must be defined before processing real candidate data.

Dataset sources and status are documented in `data/MANIFEST.yaml` and `docs/DATASETS.md`. A manifest entry does not prove that a dataset is available.

## 9. Privacy and Security

The initial implementation must follow these principles:

1. Obtain appropriate consent before accessing private repositories or recording assessment responses.
2. Request only the permissions needed for the selected workflow.
3. Keep secrets in environment variables and never commit real credentials.
4. Avoid logging raw resumes, private code, recordings, or unnecessary personal data.
5. Validate file types and handle parsing failures safely.
6. Treat uploaded documents, repository content, and model outputs as untrusted input.
7. Do not execute candidate-submitted code as part of ordinary evidence extraction.
8. Avoid sending confidential candidate information to external AI providers without reviewing permissions and data-handling requirements.
9. Provide a non-repository assessment path for candidates who cannot or do not wish to connect GitHub.
10. Keep human review central to hiring decisions.

Detailed controls are documented in `docs/PRIVACY_AND_SECURITY.md`, `docs/SECURITY_PRIVACY.md`, and `SECURITY.md`.

## 10. Testing and Evaluation

Testing should cover both individual components and complete workflows.

Minimum areas include:

- Resume parsing for supported file formats.
- Handling of empty, malformed, and oversized inputs.
- Skill extraction and evidence provenance.
- Scoring calculations and rubric boundaries.
- Missing evidence and low-confidence results.
- Job-description matching.
- AI provider failure and fallback behavior.
- Repository authorization and error handling.
- Privacy-sensitive logging and data access.
- Consistency of candidate comparisons for the same job.
- Fairness checks across relevant groups when lawful, appropriate, and supported by adequate data.
- Reproducibility of deterministic demo scenarios.

Evaluation results must be measured and reported. Synthetic demo performance must not be presented as evidence of real-world hiring accuracy.

See `docs/TESTING_AND_EVALUATION.md` and `docs/EVALUATION.md` for further guidance.

## 11. Alternatives Considered

### Alternative A: Fully monolithic implementation

**Description:** Put the UI, parsing, scoring, and AI calls into a single application file.

**Reason not selected:** This can be quick initially but makes testing, debugging, provider replacement, and maintenance harder. A modular structure provides clearer boundaries without requiring a complex deployment.

### Alternative B: Microservices from the beginning

**Description:** Deploy each component as a separate service.

**Reason not selected:** The operational overhead is unnecessary for the initial hackathon scope. Service boundaries can be maintained in code, with separate deployment considered only when justified.

### Alternative C: LLM-only candidate scoring

**Description:** Ask an LLM to assign an overall candidate score from their resume.

**Reason not selected:** This makes scores harder to reproduce and explain, can overstate unsupported claims, and does not provide adequate control over fairness. The selected approach uses documented criteria, evidence-aware scoring, and optional AI assistance.

### Alternative D: GitHub-only assessment

**Description:** Assess candidates exclusively through public repositories.

**Reason not selected:** Not all candidates have public repositories, and repository availability or activity is not a reliable standalone measure of ability. Multiple evidence paths are required.

### Alternative E: Mandatory cloud infrastructure

**Description:** Require hosted databases and external services for every run.

**Reason not selected:** This increases setup complexity and makes the demo dependent on network access and credentials. A local-first prototype with optional integrations is more practical for initial development.

## 12. Consequences

### Positive consequences

- The prototype can be developed and demonstrated with a relatively small setup.
- Scoring and evidence processing can be tested independently.
- AI providers can be changed without redesigning the entire application.
- Demo mode can remain usable when external services are unavailable.
- Evidence provenance and scoring explanations are first-class design concerns.
- Alternative assessment paths reduce unnecessary dependence on public repositories.

### Trade-offs and limitations

- Local SQLite storage is not automatically suitable for multi-user production deployment.
- Semantic similarity does not prove that a candidate possesses a skill.
- Resume parsing and AI-generated assessments can make mistakes.
- External API availability, permissions, rate limits, and data policies may constrain integrations.
- Fairness and validity require empirical evaluation, not architecture alone.
- Additional access controls and operational safeguards will be needed before production use.

## 13. Implementation Status

This ADR records the intended architecture. It does not establish that all components, integrations, safeguards, or evaluation procedures are implemented.

Before treating a component as complete, verify that its code exists, tests pass, and the relevant behavior has been exercised. Update this ADR or related documentation if implementation choices materially change.

## 14. Review Conditions

Revisit this decision when:

- The official dataset or IMATS sandbox contract becomes available.
- The prototype requires multi-user or production deployment.
- Privacy or retention requirements change.
- Evaluation reveals limitations in the scoring or evidence model.
- An external service introduces material cost, reliability, or data-handling constraints.
- The implementation diverges materially from this architecture.

When a material architecture change is made, document the reason and its consequences in a subsequent architecture decision record.
