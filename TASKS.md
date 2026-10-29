# ProofSkill AI — Development Task Board

> **Project:** ProofSkill AI  
> **Hackathon:** IM-105 — Advanced  
> **Status:** Documentation scaffold; implementation not started
> **Last Updated:** 2026-10-29

## How to Use This Task Board

- `[ ]` means not completed.
- `[x]` means completed and verified.
- Mark a task complete only after implementing it and checking its acceptance criteria.
- Record blocked tasks and their dependencies.
- Update `CURRENT_STATE.md` after meaningful implementation milestones.
- Update `HANDOFF.md` at the end of a substantial coding session.
- Record important architecture changes in `DECISIONS.md` or `docs/ADR/`.
- Do not mark a feature complete solely because its UI exists.

Priority definitions:

- **P0:** Required for the application foundation.
- **P1:** Required for the core candidate assessment.
- **P2:** Required for evidence verification and recruiter workflows.
- **P3:** Required for hackathon evaluation and hardening.
- **P4:** Optional enhancements after the core MVP works.

---

# Phase 0 — Project Foundation

**Priority:** P0  
**Goal:** Establish a reproducible development environment and working application skeleton.

## Tasks

- [x] P0.1 — Inspect the existing repository and documentation.
- [ ] P0.2 — Confirm the initial architecture and technology stack.
- [ ] P0.3 — Create the Python project configuration and dependency list.
- [ ] P0.4 — Create the application package structure.
- [ ] P0.5 — Create configuration management using environment variables.
- [ ] P0.6 — Create `.env.example` without real credentials.
- [x] P0.7 — Add `.gitignore` rules for secrets, local databases, caches, and private datasets.
- [ ] P0.8 — Initialise SQLite and create the initial schema.
- [ ] P0.9 — Create Streamlit navigation and page structure.
- [ ] P0.10 — Add basic logging and error handling.
- [ ] P0.11 — Create the initial pytest configuration.
- [ ] P0.12 — Verify that the application starts without external API credentials.

### Acceptance Criteria

- Dependencies can be installed using documented commands.
- The application launches locally.
- SQLite initialises successfully.
- Missing optional credentials do not prevent demo mode from starting.
- No secrets or private candidate data are committed to Git.

---

# Phase 1 — Resume Parsing and Analysis

**Priority:** P1  
**Goal:** Convert a resume into structured, traceable candidate claims.

## Tasks

- [ ] P1.1 — Implement PDF text extraction using PyMuPDF.
- [ ] P1.2 — Implement DOCX text extraction using python-docx.
- [ ] P1.3 — Validate file type, file size, and parsing errors.
- [ ] P1.4 — Detect empty and image-only PDFs.
- [ ] P1.5 — Add OCR support or a clear OCR-required fallback.
- [ ] P1.6 — Implement initial skill extraction using a maintained skill dictionary and rules.
- [ ] P1.7 — Add optional spaCy-based entity extraction.
- [ ] P1.8 — Implement optional structured LLM extraction.
- [ ] P1.9 — Validate extracted data against a defined schema.
- [ ] P1.10 — Preserve source text for each extracted claim wherever possible.
- [ ] P1.11 — Extract project names, descriptions, tools, and claimed technologies.
- [ ] P1.12 — Distinguish claimed skills from verified skills.
- [ ] P1.13 — Display the extracted profile for candidate review.
- [ ] P1.14 — Persist the resume profile and evidence references.
- [ ] P1.15 — Add unit tests for parsing and extraction.

### Acceptance Criteria

- Supported documents produce a structured profile.
- Unsupported or unreadable files produce useful errors.
- No qualification is invented when information is missing.
- Extracted claims can be traced to resume text where possible.
- All extracted skills initially remain unverified.

---

# Phase 2 — Job Description Analysis

**Priority:** P1  
**Goal:** Identify job requirements and connect them to candidate claims.

## Tasks

- [ ] P2.1 — Build the job-description input form.
- [ ] P2.2 — Extract required and preferred skills.
- [ ] P2.3 — Define a normalised skill taxonomy.
- [ ] P2.4 — Implement exact and synonym-based skill matching.
- [ ] P2.5 — Integrate Sentence-BERT for optional semantic matching.
- [ ] P2.6 — Associate matching results with source evidence.
- [ ] P2.7 — Identify unsupported requirements that need verification.
- [ ] P2.8 — Display the job-match report.
- [ ] P2.9 — Persist job descriptions and matching results.
- [ ] P2.10 — Add tests for matching and missing evidence.

### Acceptance Criteria

- A recruiter or candidate can enter a job description.
- Matching results identify the evidence supporting each match.
- Semantic similarity is not presented as a proficiency score.
- Missing resume keywords do not automatically imply a lack of skill.

---

# Phase 3 — Interview Question Generation

**Priority:** P1  
**Goal:** Generate relevant questions from the resume and job requirements.

## Tasks

- [ ] P3.1 — Define the interview-question schema.
- [ ] P3.2 — Implement rule-based question templates for demo mode.
- [ ] P3.3 — Implement LLM-based question generation.
- [ ] P3.4 — Generate questions by skill and difficulty.
- [ ] P3.5 — Generate project-specific questions when evidence is available.
- [ ] P3.6 — Generate role-specific scenario questions for non-technical candidates.
- [ ] P3.7 — Include expected answer concepts and scoring rubrics.
- [ ] P3.8 — Validate generated questions and reject malformed responses.
- [ ] P3.9 — Prevent repeated questions where practical.
- [ ] P3.10 — Add configurable interview length.
- [ ] P3.11 — Persist questions and their source evidence.
- [ ] P3.12 — Test generation with and without API credentials.

### Acceptance Criteria

- Questions relate to the candidate's claims and target job.
- Each question has a related skill, difficulty, and scoring rubric.
- Repository-specific questions are not generated without repository evidence.
- Demo mode works without claiming to use a real LLM.

---

# Phase 4 — Adaptive Interview and Answer Evaluation

**Priority:** P1  
**Goal:** Conduct interviews and assess demonstrated knowledge.

## Tasks

- [ ] P4.1 — Build the one-question-at-a-time interview interface.
- [ ] P4.2 — Implement answer submission and validation.
- [ ] P4.3 — Implement rule-based demo evaluation.
- [ ] P4.4 — Implement LLM-based answer evaluation.
- [ ] P4.5 — Define technical and scenario-specific rubrics.
- [ ] P4.6 — Calculate criterion-level scores.
- [ ] P4.7 — Record supporting evidence and missing concepts.
- [ ] P4.8 — Generate follow-up questions from previous answers.
- [ ] P4.9 — Implement adaptive difficulty rules.
- [ ] P4.10 — Preserve progress across Streamlit reruns.
- [ ] P4.11 — Handle timeouts, retries, and model errors.
- [ ] P4.12 — Add tests for scoring and adaptive behaviour.

### Acceptance Criteria

- Candidates can complete an interview.
- Every evaluation has a score, explanation, and rubric breakdown.
- Follow-up questions use the previous answer and relevant skill.
- Demo evaluations are explicitly labelled.
- No unsupported psychological confidence score is generated.

---

# Phase 5 — Voice Interview

**Priority:** P2  
**Goal:** Allow candidates to answer through voice when supported.

## Tasks

- [ ] P5.1 — Select and document the browser recording approach.
- [ ] P5.2 — Implement microphone permission handling.
- [ ] P5.3 — Implement audio submission and validation.
- [ ] P5.4 — Integrate a configurable speech-to-text service.
- [ ] P5.5 — Display transcription to the candidate.
- [ ] P5.6 — Allow correction of transcription errors where supported.
- [ ] P5.7 — Connect transcribed answers to the evaluation pipeline.
- [ ] P5.8 — Retain typed answers as a fallback.
- [ ] P5.9 — Document recording retention and deletion behaviour.
- [ ] P5.10 — Test recording and transcription failures.

### Acceptance Criteria

- Voice answers can be transcribed when the service is configured.
- Candidates can complete the interview without using voice.
- Failed transcription does not silently produce a fabricated answer.
- Audio is handled according to the documented privacy policy.

---

# Phase 6 — GitHub Analysis and Project Viva

**Priority:** P2  
**Goal:** Generate viva questions from real repository evidence.

## Tasks

- [ ] P6.1 — Extract and display resume-linked GitHub URLs; obtain consent before repository discovery.
- [ ] P6.2 — Validate GitHub repository URLs.
- [ ] P6.3 — Implement bounded GitHub API requests.
- [ ] P6.4 — Retrieve repository metadata and file listings.
- [ ] P6.5 — Retrieve selected source files safely.
- [ ] P6.6 — Analyse programming languages and project structure.
- [ ] P6.7 — Inspect available commit history without assuming individual authorship.
- [ ] P6.8 — Extract relevant code evidence and file paths.
- [ ] P6.9 — Generate questions grounded in retrieved source code.
- [ ] P6.10 — Store repository-analysis provenance and limitations.
- [ ] P6.11 — Handle inaccessible repositories and rate limits.
- [ ] P6.12 — Test repository URL validation and evidence mapping.
- [ ] P6.13 — List eligible repositories after discovery consent and let the candidate select and confirm repositories.
- [ ] P6.14 — Persist discovery consent and per-repository selection provenance.
- [ ] P6.15 — Generate evidence-grounded tasks for code explanation, focused change proposals, patch/diff responses, approach comparisons, and architecture reasoning.
- [ ] P6.16 — Accept candidate explanations or patches as response artifacts without writing to GitHub or executing code.
- [ ] P6.17 — Test declined consent, empty selections, unselected repository exclusion, bounded retrieval, and no-write/no-execution behavior.

### Acceptance Criteria

- Repository discovery requires recorded candidate consent; file retrieval requires explicit candidate selection and confirmation.
- Only selected repositories are analyzed, within documented metadata, file, size, and time limits.
- Every code-specific viva question references actual retrieved evidence.
- Code-change tasks accept candidate explanations or patch/diff responses; the system neither writes to GitHub nor executes repository or candidate code.
- Repository ownership is not treated as proof of authorship.
- Candidates without accessible repositories can use an alternative assessment.

---

# Phase 7 — Tutorial-Clone Detection

**Priority:** P2  
**Goal:** Identify potential similarities between candidate code and labelled reference projects.

## Tasks

- [ ] P7.1 — Confirm the availability and licence of reference code datasets.
- [ ] P7.2 — Define code normalisation rules.
- [ ] P7.3 — Implement token-based similarity.
- [ ] P7.4 — Implement code fingerprints or another documented comparison method.
- [ ] P7.5 — Add AST-based comparison for supported languages where feasible.
- [ ] P7.6 — Build a labelled-reference comparison pipeline.
- [ ] P7.7 — Report matching files and code regions.
- [ ] P7.8 — Account for boilerplate, shared libraries, and common algorithms.
- [ ] P7.9 — Evaluate precision and recall using labelled data.
- [ ] P7.10 — Document limitations and uncertainty.

### Acceptance Criteria

- Similarity results are reproducible.
- The system provides evidence for reported similarities.
- No unsupported plagiarism conclusion is produced.
- Detection accuracy is reported only after evaluation against labelled references.

---

# Phase 8 — Proof Card and Scoring

**Priority:** P1  
**Goal:** Generate a transparent assessment report.

## Tasks

- [ ] P8.1 — Define the Proof Card data schema.
- [ ] P8.2 — Implement skill-specific performance scoring.
- [ ] P8.3 — Implement evidence-strength estimation.
- [ ] P8.4 — Implement communication scoring.
- [ ] P8.5 — Document overall-score calculation.
- [ ] P8.6 — Handle unavailable assessment components explicitly.
- [ ] P8.7 — Link each score to supporting evidence.
- [ ] P8.8 — Generate strengths and improvement recommendations.
- [ ] P8.9 — Display unverified claims and missing evidence.
- [ ] P8.10 — Implement JSON export.
- [ ] P8.11 — Add optional PDF export.
- [ ] P8.12 — Test score calculations and report consistency.

### Acceptance Criteria

- Every score can be traced to the relevant assessment evidence.
- Skill performance and evidence confidence remain separate.
- Missing scores are not silently invented.
- The displayed and exported reports contain consistent results.

---

# Phase 9 — Recruiter Dashboard and Candidate Comparison

**Priority:** P2  
**Goal:** Help recruiters compare candidates against a shared job description.

## Tasks

- [ ] P9.1 — Build the recruiter dashboard.
- [ ] P9.2 — Implement candidate listing and filtering.
- [ ] P9.3 — Implement candidate assessment detail views.
- [ ] P9.4 — Build a side-by-side comparison view.
- [ ] P9.5 — Implement configurable job-specific ranking.
- [ ] P9.6 — Generate human-readable ranking explanations.
- [ ] P9.7 — Show evidence gaps and uncertainty.
- [ ] P9.8 — Exclude prohibited ranking features.
- [ ] P9.9 — Add fairness and ranking regression tests.
- [ ] P9.10 — Add human-review indicators.

### Acceptance Criteria

- Two candidates can be compared against the same job description.
- Ranking explanations reference job-relevant assessment evidence.
- College name, gender, age, and location are excluded from ranking inputs.
- Recruiters retain responsibility for the final hiring decision.

---

# Phase 10 — Data, Privacy, and Security

**Priority:** P0/P1  
**Goal:** Protect candidate data and make the application safe to operate.

## Tasks

- [ ] P10.1 — Define the database schema and relationships.
- [ ] P10.2 — Implement persistent storage and migrations where needed.
- [ ] P10.3 — Use parameterised database queries.
- [ ] P10.4 — Protect API credentials using environment variables.
- [ ] P10.5 — Add input validation and upload limits.
- [ ] P10.6 — Implement candidate record deletion.
- [ ] P10.7 — Document data retention and deletion.
- [ ] P10.8 — Minimise sensitive information in application logs.
- [ ] P10.9 — Implement repository consent checks.
- [ ] P10.10 — Review privacy and security controls.

### Acceptance Criteria

- Secrets are not committed to Git.
- Candidate records can be deleted according to policy.
- Untrusted files and repository code are never executed.
- Sensitive data is not exposed unnecessarily in logs or recruiter views.

---

# Phase 11 — Testing and Hackathon Validation

**Priority:** P3  
**Goal:** Verify functionality and measure performance on appropriate datasets.

## Tasks

- [ ] P11.1 — Add unit tests for core business logic.
- [ ] P11.2 — Add integration tests for the assessment workflow.
- [ ] P11.3 — Test demo mode without external API credentials.
- [ ] P11.4 — Test database persistence and deletion.
- [ ] P11.5 — Test invalid and adversarial input.
- [ ] P11.6 — Test ranking-feature exclusions.
- [ ] P11.7 — Obtain and validate the official hackathon dataset.
- [ ] P11.8 — Establish a documented training/development/held-out evaluation protocol.
- [ ] P11.9 — Measure answer-evaluation agreement.
- [ ] P11.10 — Evaluate tutorial-clone detection on labelled references.
- [ ] P11.11 — Measure agreement with held-out recruiter shortlist decisions.
- [ ] P11.12 — Evaluate ranking fairness.
- [ ] P11.13 — Collect feedback on candidate understanding of Proof Cards.
- [ ] P11.14 — Document measured results and limitations.

### Acceptance Criteria

- Core tests run successfully in the documented environment.
- Evaluation procedures are reproducible.
- Held-out labels are not used for tuning.
- All benchmark claims are supported by actual measurements.

---

# Phase 12 — Documentation and Delivery

**Priority:** P3

## Tasks

- [ ] P12.1 — Complete README setup instructions.
- [ ] P12.2 — Complete architecture and API documentation.
- [ ] P12.3 — Complete model and prompt documentation.
- [ ] P12.4 — Document scoring and fairness methodology.
- [ ] P12.5 — Document datasets, licences, and provenance.
- [ ] P12.6 — Document deployment and troubleshooting.
- [ ] P12.7 — Update CURRENT_STATE.md.
- [ ] P12.8 — Update HANDOFF.md.
- [ ] P12.9 — Verify a fresh installation using the README.
- [ ] P12.10 — Prepare a hackathon demo scenario.
- [ ] P12.11 — Confirm IMATS integration requirements and test the integration where access permits.

### Acceptance Criteria

- Another developer can set up the project using the documented instructions.
- Known limitations and missing external dependencies are disclosed.
- The demonstration uses clearly labelled real or synthetic data.
- The final submission does not claim unverified features or metrics.

---

# Phase 13 — Optional Enhancements

**Priority:** P4

- [ ] Add authentication and role-based access control.
- [ ] Add asynchronous processing for lengthy assessments.
- [ ] Add more programming-language parsers.
- [ ] Add richer practical assessment environments.
- [ ] Add improved semantic search and evidence retrieval.
- [ ] Add production database support.
- [ ] Add monitoring and operational metrics.
- [ ] Add additional accessibility and localisation support.

These enhancements must not delay the core MVP unless they are required by verified hackathon constraints.

---

# Definition of Done

A task may be marked complete only when:

1. Its required behaviour is implemented.
2. Relevant acceptance criteria are satisfied.
3. Appropriate tests have been run.
4. Documentation is updated where necessary.
5. Known limitations are recorded.
6. The task status is reflected in CURRENT_STATE.md.

At the end of a substantial work session:

- Update CURRENT_STATE.md.
- Update TASKS.md.
- Update HANDOFF.md.
- Record important technical decisions.
- Report actual test results and remaining blockers.

Never claim that a feature, integration, benchmark, or test has succeeded without evidence.