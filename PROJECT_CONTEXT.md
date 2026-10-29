# ProofSkill AI — Project Context

> **Project:** ProofSkill AI  
> **Hackathon:** IM-105 — Advanced  
> **Organization:** Integraminds  
> **Theme:** AI FRONTIER  
> **Track:** Software  
> **Tagline:** Proof of Skill, Not a Template Resume  
> **Project status:** Planning / Initial documentation

---

## 1. Project Mission

ProofSkill AI is an AI-powered skill verification and candidate assessment platform designed to help recruiters identify capable freshers through demonstrable evidence rather than resume keywords, college prestige, or generic project descriptions.

The platform converts a candidate's resume claims into a structured assessment plan, evaluates demonstrated skills through adaptive interviews and practical assessments, analyses consented project evidence where available, and generates an explainable Candidate Proof Card.

The objective is to make fresher recruitment more evidence-based, transparent, and accessible to candidates from colleges that may not receive frequent recruiter visits.

## 2. Problem Being Solved

Traditional fresher recruitment often relies on resumes containing similar templates, skill lists, and tutorial-style projects. Recruiters screening thousands of applications cannot thoroughly verify every claim.

This creates several problems:

- Candidates can list skills they cannot demonstrate.
- Tutorial-clone projects can appear more impressive than their actual implementation warrants.
- Recruiters may rely too heavily on college reputation or other weak proxies.
- Candidates with strong practical skills but limited access to opportunities can be overlooked.
- Generic interview questions do not establish whether a candidate understands their own projects.

ProofSkill AI addresses these issues by collecting, evaluating, and presenting relevant evidence of demonstrated skills.

## 3. Target Users

### 3.1 Candidates

Freshers and early-career applicants who need to demonstrate their capabilities beyond a traditional resume.

### 3.2 Recruiters

Recruiters screening large numbers of candidates who need transparent, job-specific comparisons supported by assessment evidence.

### 3.3 Candidates Without Public Repositories

Candidates who do not have a GitHub account or public source code must still be able to complete a fair assessment through practical tasks, structured questions, work samples, or scenario-based evaluations.

## 4. Core Product Principles

1. **Evidence over claims:** A resume claim is not proof of proficiency.
2. **Explainability:** Every skill score and recruiter ranking must have a human-readable explanation.
3. **Fair access:** Candidates must not be disadvantaged simply because they lack public repositories or attend less-represented colleges.
4. **Job relevance:** Assessments must measure skills relevant to the target role.
5. **Consent:** Repository analysis requires explicit candidate consent.
6. **Privacy:** Collect and retain only the data required for the assessment.
7. **Human oversight:** Recruiters make the final hiring decisions.
8. **Honest uncertainty:** Missing evidence is not proof of incompetence.
9. **Reproducibility:** Scoring rules, model configurations, and evaluation procedures must be documented.
10. **Verified implementation status:** Planned functionality must never be described as implemented or tested without evidence.

## 5. Main Product Workflow

The intended candidate workflow is:

1. Upload a resume in PDF or DOCX format.
2. Extract resume text and identify claimed skills, tools, projects, experience, education, and certifications.
3. Detect GitHub profile or repository links in the resume and show them to the candidate.
4. If the candidate consents to repository discovery, list eligible repositories from the linked profile and allow the candidate to select which repositories, if any, to assess.
5. After the candidate confirms the selected repository scope, inspect bounded source and project files without executing them.
6. Select a target role and provide a job description.
7. Match claimed skills against the role's requirements.
8. Generate an initial interview plan based on the resume, job description, and available selected-project evidence.
9. Ask adaptive interview questions, one at a time.
10. Collect typed or spoken answers.
11. Evaluate responses using explicit, role-relevant scoring rubrics.
12. Offer follow-up questions based on demonstrated understanding.
13. Generate project-grounded questions and practical tasks asking the candidate to explain code, propose or submit a bounded code change, justify an approach, compare alternatives, and discuss architecture.
14. Offer an equivalent assessment route when repository evidence is unavailable, inaccessible, or declined.
15. Generate a Candidate Proof Card with scores, evidence, confidence estimates, strengths, limitations, and recommendations.

The intended recruiter workflow is:

1. Select or enter a job description.
2. View candidates who have completed relevant assessments.
3. Review evidence-backed skill profiles.
4. Compare two candidates against the same job requirements.
5. Understand the reasons behind each candidate's relative strengths and gaps.
6. Review uncertainty and supporting evidence before making a hiring decision.

## 6. Core Functional Modules

### 6.1 Resume Analysis

Extract structured information from resumes and retain supporting text for each identified claim wherever possible.

The system must not invent qualifications, infer unlisted experience, or treat keyword presence as proof of skill.

### 6.2 Job Description Analysis

Identify required and preferred skills, associate them with assessment criteria, and determine which candidate claims require verification.

### 6.3 Adaptive Interview

Generate questions based on claimed skills, job requirements, and available project evidence.

Question difficulty should adapt to demonstrated understanding, not simply to speaking confidence or resume seniority.

### 6.4 Answer Evaluation

Evaluate answers using explicit criteria appropriate to the question type.

Technical evaluations should consider correctness, required concepts, reasoning, and relevance. Scenario evaluations should consider reasoning, feasibility, prioritisation, and role relevance.

### 6.5 Voice Assessment

Where voice input is enabled, transcribe spoken answers and evaluate their content.

Do not infer intelligence, honesty, personality, or psychological confidence from accent, vocal characteristics, speaking speed, or appearance.

### 6.6 Repository Analysis and Project Viva

Extract GitHub profile and repository URLs from the resume as candidate-provided claims. Show the extracted links to the candidate; do not fetch them automatically. After the candidate consents to discovery, retrieve eligible repository metadata from the linked GitHub profile and present the choices in the UI. Analyze only repositories the candidate explicitly selects and confirms.

Inspect a bounded set of relevant source and project files from selected repositories. Ground each code-specific question or task in retrieved evidence and identify its repository and file references. Questions and tasks may ask the candidate to explain code, make or propose a focused change, describe their approach, compare valid alternatives, and reason about architecture, testing, debugging, security, and trade-offs.

A code-change task asks the candidate to submit an explanation, patch, or diff for review; the assessment system must not write to the candidate's GitHub repository or execute candidate code. Repository ownership alone does not establish individual authorship or proficiency.

Never execute uploaded files or arbitrary repository code. Candidates without accessible or selected repositories must have an equivalent non-repository assessment path.

### 6.7 Tutorial-Clone Analysis

Compare candidate project code with available, appropriately licensed reference examples using documented similarity techniques.

Report the similarity evidence, limitations, and uncertainty. Code similarity alone must not be treated as conclusive evidence of plagiarism or tutorial cloning.

### 6.8 Alternative Assessment

Provide practical tasks, work samples, and role-specific scenarios for candidates without public repositories.

The lack of a GitHub profile must not automatically reduce a candidate's score or ranking.

### 6.9 Candidate Proof Card

Present demonstrated skill performance, supporting evidence, evidence confidence, strengths, gaps, and recommendations in a clear, reviewable format.

### 6.10 Recruiter Dashboard

Allow job-specific filtering, evidence review, side-by-side comparison, and explainable ranking.

Ranking must exclude college name, gender, age, and location as features.

## 7. Scoring Terminology

The platform must keep the following measures separate.

### Skill Performance Score

A 0–100 assessment score calculated from relevant interview answers and practical assessment results using documented scoring criteria.

### Evidence Confidence

An estimate of how strongly the available evidence supports a particular skill assessment.

It is not the same as the candidate's psychological confidence and must not be described as a calibrated probability unless calibration has been empirically validated.

### Communication Score

A score based on relevant aspects of answer clarity, structure, comprehensibility, and relevance to the question.

Communication must not be used as a substitute for technical proficiency.

### Overall Assessment Score

A documented combination of eligible assessment components. Its weights must be configurable, justified, and disclosed.

If a component is unavailable, the system must not silently invent a value. Any renormalisation or change in the calculation must be disclosed.

### Recruiter Ranking

A job-specific comparison based on relevant assessment evidence and documented criteria.

A ranking is decision support, not an automatic hiring decision.

## 8. AI and Technology Direction

The initial implementation is planned around the following stack. These are architectural intentions, not confirmation that the components have already been implemented.

- **Programming language:** Python.
- **Initial user interface:** Streamlit.
- **Initial persistence:** SQLite.
- **Resume parsing:** PyMuPDF for PDF and python-docx for DOCX.
- **Optional NLP:** spaCy.
- **Semantic matching:** Sentence Transformers, initially `sentence-transformers/all-MiniLM-L6-v2`.
- **Question generation and answer evaluation:** A configurable LLM API.
- **Voice transcription:** A configurable speech-to-text service.
- **Repository inspection:** GitHub REST API.
- **Testing:** pytest.
- **Configuration:** Environment variables and a documented `.env.example`.

Keep AI providers, model identifiers, prompts, scoring logic, and integrations modular. Avoid unnecessary dependencies and do not train a custom model unless a validated need and suitable data justify it.

The precise implementation must be documented in `docs/ARCHITECTURE.md` and `docs/AI_MODELS.md`.

## 9. Data and Evaluation

The IM-105 problem statement describes:

- 400 anonymised fresher profiles with resumes, consented repositories, and assessment results.
- Recruiter shortlist decisions associated with 30 job descriptions.
- A held-out evaluation set.

The actual files, schemas, access permissions, and split definitions must be confirmed before implementation of the evaluation pipeline.

Do not fabricate access to these datasets or invent benchmark results.

Use authorised data and preserve held-out data for final evaluation. Avoid training or tuning on held-out labels.

Evaluation should cover:

- Resume extraction accuracy.
- Skill-claim evidence quality.
- Answer-evaluation agreement with human reviewers.
- Tutorial-clone detection performance on labelled references.
- Recruiter shortlist agreement.
- Ranking fairness.
- Candidate comprehension of the Proof Card.
- Reliability and reproducibility.

Every reported metric must specify its dataset, methodology, sample size, and limitations.

## 10. Fairness, Privacy, and Security Constraints

The ranking pipeline must not use the following features:

- College name or college prestige.
- Gender.
- Age.
- Location.

The system must also examine potential indirect proxies and evaluate outcomes across appropriate groups where lawful, ethical, and supported by authorised data.

Other requirements:

- Obtain explicit consent before repository analysis.
- Validate uploaded files and external URLs.
- Never execute candidate-provided code.
- Keep secrets out of source control.
- Avoid storing unnecessary resume text, recordings, and personal information.
- Restrict access to candidate records.
- Document data retention and deletion procedures.
- Treat external documents, repository contents, and model outputs as untrusted inputs.
- Do not expose one candidate's private evidence to another candidate.
- Provide a human-review mechanism for uncertain or disputed findings.

Detailed requirements belong in `docs/PRIVACY_AND_SECURITY.md` and `docs/SCORING_AND_FAIRNESS.md`.

## 11. External Dependencies

Full hackathon functionality may depend on:

- Official Integraminds dataset access.
- IMATS sandbox API documentation and credentials.
- Optional LLM provider credentials.
- Optional speech-to-text credentials.
- GitHub API access and rate limits.
- Appropriate permissions and licences for reference datasets.

Implement a clearly labelled demo mode so core workflows can be tested without external API credentials.

Never represent mock outputs as real model evaluations or official benchmark results.

## 12. Development Conventions

- Inspect the existing code before modifying it.
- Keep UI, business logic, data access, and AI integrations separated.
- Use type hints, meaningful names, and small, testable functions.
- Validate inputs and model outputs.
- Use parameterised database queries.
- Add tests when implementing or changing behaviour.
- Update documentation when architecture, scoring, configuration, or external interfaces change.
- Record significant technical decisions.
- Maintain `CURRENT_STATE.md`, `TASKS.md`, and `HANDOFF.md` as the project evolves.
- Report actual test results and clearly disclose untested behaviour.
- Do not mark a planned feature as complete without implementation evidence.

## 13. Source of Truth and Conflict Resolution

Use the following precedence:

1. The official IM-105 problem statement and verified organiser requirements define the challenge constraints.
2. This file defines the project's mission and cross-cutting principles.
3. `docs/PRD.md` defines product requirements and acceptance criteria.
4. `docs/ARCHITECTURE.md` and approved architecture decisions define the intended technical design.
5. The actual code and automated tests establish what is currently implemented and verified.
6. `CURRENT_STATE.md`, `TASKS.md`, and `HANDOFF.md` record the latest development status.

If these sources conflict, do not silently invent a resolution. Identify the conflict, explain its impact, and update the appropriate documentation after the decision is made.

## 14. Definition of Success

ProofSkill AI should help recruiters answer:

- What does the candidate claim to know?
- What evidence supports each claim?
- How well did the candidate demonstrate the relevant skill?
- How reliable and complete is the evidence?
- What should be verified next?
- Why is this candidate a relevant match for the job?

The final product should make candidate capabilities easier to understand without treating resumes, AI scores, college reputation, or repository ownership as definitive proof of ability.

## 15. Four-Member Implementation Plan

This is the proposed division of implementation ownership, not a status report. The repository is currently a documentation scaffold; all implementation tasks remain pending until built and verified. Work can proceed in parallel after the shared interfaces and data contracts are agreed.

### Part 1 — Core Application and Backend

**Owner:** Prakarsh Kaushik  
**Role:** Primary owner of the non-AI application implementation and integration.

Responsibilities:

- Establish the Python/Streamlit project structure, configuration, local demo mode, SQLite persistence, and shared service interfaces.
- Implement resume file validation and PDF/DOCX text extraction, candidate/job/evidence persistence, and deterministic skill-to-evidence matching.
- Implement consent-recorded GitHub link validation, public repository discovery, candidate-selected repository retrieval, and bounded read-only file inspection.
- Implement deterministic score aggregation and Proof Card data services, preserving missing or unassessed values rather than converting them to zero.
- Integrate the AI, data, and UI modules through the agreed contracts and keep application errors visible and actionable.

Primary task-board areas: Phase 0; backend portions of Phases 1, 2, 6, 8, and 10.

### Part 2 — AI and Machine Learning

**Owner:** Lakshay Kumar  
**Role:** Primary owner of AI/ML behavior.

Responsibilities:

- Implement structured resume claim and skill extraction, job-requirement extraction, and optional semantic matching through the shared AI/provider abstraction.
- Implement role- and evidence-grounded interview question generation, adaptive follow-ups, and answer evaluation against the documented 0–4 rubric.
- Implement project-viva question and task generation from selected repository evidence, including code explanation, focused change proposals, patch/diff responses, approach comparisons, and architecture reasoning.
- Validate model output schemas, score bounds, evidence references, and allowed values; treat resume, repository, and answer content as untrusted input.
- Provide deterministic or clearly labeled fallback behavior where required, and distinguish simulated output from live-model results.

Primary task-board areas: AI/ML portions of Phases 1–4, 6, and 8. Provider calls must use the shared abstraction; do not add provider-specific calls to UI modules.

### Part 3 — Streamlit UI/UX

**Owner:** Om Upadhyay  
**Role:** Primary owner of candidate and recruiter user experience.

Responsibilities:

- Build clear Streamlit navigation and the candidate flow for resume upload, job requirements, extracted-claim review, and interview completion.
- Build the GitHub consent and repository-selection screens: display extracted links, explain discovery, show eligible repositories, and require explicit selection before analysis.
- Present project questions/tasks and collect explanations or patch/diff responses without implying that submitted code was run or applied.
- Build Proof Card and recruiter comparison views that show evidence, coverage, confidence, unassessed skills, limitations, and human-review boundaries.
- Provide accessible loading, empty, success, error, and demo-mode states; keep business logic and database access in service modules.

Primary task-board areas: P0.9 and UI portions of Phases 1–4, 6, 8, and 9.

### Part 4 — Quality, Fairness, and Delivery

**Owner:** Titiksha Garg  
**Role:** Cross-cutting validation and delivery owner.

Responsibilities:

- Turn product requirements into a concise acceptance checklist and test scenarios before integration.
- Add or coordinate integration and end-to-end tests for the main candidate flow, demo mode, consent/selection boundaries, malformed inputs, and external-service failures.
- Verify fairness invariants: missing evidence remains unassessed, public repository access is not a prerequisite, and excluded attributes do not affect ranking.
- Review privacy/security behavior, including secrets handling, candidate-data exposure, read-only GitHub access, bounded retrieval, and no execution of repository code or candidate patches.
- Maintain accurate setup/demo instructions and status reporting; prepare a synthetic-data demo and record actual test results and remaining limitations.

Primary task-board areas: Phases 10–12 and cross-cutting acceptance/testing. Each implementation owner remains responsible for unit tests of their own code; Titiksha coordinates shared regression checks rather than acting as the only tester.

### Shared Integration Sequence

1. **Agree on contracts:** Prakarsh defines service/data boundaries; Lakshay documents AI input/output schemas; Om maps screens to those contracts; Titiksha derives acceptance checks from the PRD.
2. **Build in parallel:** Prakarsh develops core services, Lakshay develops AI services against agreed schemas, Om builds Streamlit pages against service interfaces or temporary mocks, and Titiksha prepares fixtures and tests.
3. **Integrate incrementally:** Connect one complete workflow at a time—resume and role input, interview and evaluation, optional GitHub project assessment, then Proof Card and recruiter review.
4. **Verify the demo:** Run the documented tests and a fresh demo-mode walkthrough; fix blockers and update `CURRENT_STATE.md` and `TASKS.md` only from verified results.

### Team Working Rules

- Each part has one directly responsible owner; agree on shared-file changes before editing the same module.
- Keep interfaces, schemas, rubric scale, and consent semantics consistent with the existing PRD and API contracts.
- Use synthetic candidate data in development and demos. Do not use real candidate data without appropriate authorization.
- Merge work only after relevant tests pass; report exactly what was implemented, mocked, tested, and left incomplete.
- The owners above indicate intended responsibility, not completed work or a guarantee of equal task volume. Rebalance after the first integration checkpoint if actual effort differs.