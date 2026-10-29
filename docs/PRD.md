# ProofSkill AI — Product Requirements Document (PRD)

**Project:** ProofSkill AI  
**Hackathon:** IM-105 — Advanced  
**Organization:** Integraminds  
**Theme:** AI FRONTIER  
**Version:** 1.0  
**Status:** Initial specification  
**Owner:** Project team

---

## 1. Product Overview

ProofSkill AI is an evidence-based skill verification platform for fresher recruitment.

It helps candidates demonstrate their skills through resume-informed interviews, practical assessments, project-specific viva questions, and structured evidence collection. Recruiters use the resulting Candidate Proof Cards to compare candidates against a specific job description.

The platform must distinguish between skills claimed on a resume and skills demonstrated through assessment.

## 2. Problem Statement

Recruiters screening thousands of freshers often encounter resumes with similar templates, keyword lists, and tutorial-style projects. Resume screening alone cannot reliably establish whether a candidate possesses the claimed skills.

ProofSkill AI aims to:

- Verify job-relevant skills through structured assessments.
- Generate questions from the candidate's resume and available project evidence.
- Identify potential tutorial-project similarities using defensible evidence.
- Support candidates without public repositories.
- Explain scores and candidate rankings in human-readable terms.
- Reduce dependence on college prestige and other prohibited ranking features.

## 3. Product Goals

### 3.1 Primary Goals

1. Generate a structured skill profile from an uploaded resume.
2. Match claimed skills against a job description.
3. Conduct adaptive, role-relevant interviews.
4. Evaluate answers using explicit scoring rubrics.
5. Generate a transparent, evidence-backed Candidate Proof Card.
6. Allow recruiters to compare two candidates against the same job description.
7. Provide an alternative assessment path for candidates without GitHub.
8. Extract GitHub links from resumes and let candidates select which linked-profile repositories to assess.
9. Support consent-based, candidate-selected repository analysis and project-grounded questions and code tasks.
10. Make all ranking decisions explainable and exclude prohibited features.

### 3.2 Non-Goals for the Initial MVP

- Fully autonomous hiring or candidate rejection.
- Guaranteed detection of plagiarism or candidate dishonesty.
- Psychological confidence, personality, or intelligence detection from voice.
- Training a large language model from scratch.
- Production-scale multi-tenant enterprise infrastructure.
- A claim of validated recruiter agreement before testing against the official labelled dataset.

## 4. User Personas

### 4.1 Fresher Candidate

Needs a fair opportunity to demonstrate skills beyond resume claims.

Success means the candidate can complete an assessment, understand their scores, see the evidence used, and receive useful recommendations.

### 4.2 Recruiter

Needs to screen candidates efficiently against a defined role.

Success means the recruiter can inspect evidence, compare candidates consistently, understand ranking reasons, and retain responsibility for hiring decisions.

### 4.3 Candidate Without GitHub

Needs an equivalent opportunity to demonstrate relevant capabilities without being penalised for lacking public source code.

Success means the candidate can complete a practical or scenario-based assessment and receive a meaningful Proof Card.

## 5. Core User Journeys

### 5.1 Candidate Assessment Journey

1. Open the candidate assessment page.
2. Upload a PDF or DOCX resume.
3. Review extracted information and correct parsing errors where supported.
4. Select a target role or enter a job description.
5. Review identified skill claims and their source evidence.
6. Choose the assessment route.
7. Provide repository consent if repository analysis is requested.
8. Complete the interview and any assigned practical assessment.
9. Review the evaluation results.
10. Open and export the Candidate Proof Card.

### 5.2 Technical Candidate Journey

1. Complete resume analysis.
2. Review GitHub profile or repository links extracted from the resume.
3. Choose whether to allow repository discovery for the linked GitHub account.
4. Review discovered repositories and select the specific project repositories to assess.
5. Confirm the selected repository scope before source files are retrieved.
6. Review the repository summary and detected limitations.
7. Answer questions and complete bounded tasks grounded in selected project files.
8. Explain implementation, propose or submit a focused code change, discuss the chosen approach and alternatives, and reason about architecture and trade-offs.
9. Receive scores supported by the candidate's responses and selected-repository evidence.

The assessment system must not push changes to the candidate's repositories or execute repository code. Code-change tasks are submitted as candidate responses or patches for review.

### 5.3 Candidate Without Public Code

1. Complete resume analysis.
2. Select the available alternative assessment.
3. Complete role-specific practical questions, work samples, or scenario questions.
4. Receive a Proof Card using the evidence actually collected.

Absence of public code must not automatically reduce skill scores.

### 5.4 Recruiter Journey

1. Open the recruiter dashboard.
2. Select a job description.
3. Browse completed candidate assessments.
4. Select two candidates for comparison.
5. Review skill scores, evidence, confidence estimates, and missing evidence.
6. Read the explanation for each comparison or ranking.
7. Make a human hiring decision.

## 6. Functional Requirements

### FR-01: Resume Upload

The system shall:

- Accept PDF and DOCX files.
- Validate file type and configurable size limits.
- Handle corrupted, empty, and unsupported files gracefully.
- Extract available text without executing uploaded content.
- Identify image-only PDFs and explain when OCR is required.
- Avoid unnecessary retention of original files.

**Acceptance criteria:**

- A valid supported document can be uploaded and parsed.
- An invalid or unreadable document produces a helpful error.
- An image-only PDF does not silently produce a misleading empty profile.

### FR-02: Resume Information Extraction

The system shall extract available:

- Claimed technical and non-technical skills.
- Projects and project descriptions.
- Tools and technologies.
- Work experience and internships.
- Education and certifications.
- Relevant supporting text spans.

The system shall preserve the distinction between extracted claims and verified capabilities.

**Acceptance criteria:**

- Extracted claims can be traced to their source text where possible.
- Missing information is represented as unavailable, not invented.
- The system identifies parsing uncertainty or extraction failures.

### FR-03: Job Description Analysis

The system shall accept a job title and job description and identify required and preferred skills.

It shall match these requirements against resume claims and available assessment evidence.

**Acceptance criteria:**

- The user can enter or edit the target job description.
- The system displays matched requirements and unsupported requirements.
- Missing resume keywords do not automatically imply lack of skill.

### FR-04: Interview Question Generation

The system shall generate questions using relevant candidate claims, job requirements, and available project evidence.

Each question shall include:

- Question text.
- Related skill.
- Difficulty.
- Question type.
- Expected answer concepts.
- Scoring rubric.
- Source evidence or reason for asking the question.

**Acceptance criteria:**

- Questions relate to the selected job and candidate profile.
- Project-specific questions reference retrieved repository evidence when applicable.
- Generic questions are not falsely labelled as repository-derived.

### FR-05: Adaptive Interview

The system shall ask one question at a time and use the preceding evaluation to determine an appropriate follow-up.

A configurable interview length shall be provided, with eight questions as the initial default.

**Acceptance criteria:**

- The candidate can submit an answer and proceed.
- Follow-ups respond to demonstrated understanding.
- Repeated questions are avoided where practical.
- The interview handles incomplete answers, skipped questions, and API failures.
- Interview progress survives normal application reruns.

### FR-06: Voice Answers

Where supported, the system shall allow candidates to record spoken answers and transcribe them.

Typed answers must remain available as an alternative.

**Acceptance criteria:**

- Recording requires browser permission.
- Transcription failures do not prevent typed assessment.
- The candidate can review or correct transcription errors where supported.
- Voice characteristics are not used to infer psychological confidence, personality, or intelligence.

### FR-07: Answer Evaluation

The system shall evaluate answers using question-specific rubrics.

For technical questions, criteria may include correctness, expected concepts, reasoning, and relevance.

For scenario questions, criteria may include reasoning, feasibility, prioritisation, and role relevance.

**Acceptance criteria:**

- Each evaluation contains a score, criterion breakdown, explanation, and evidence.
- Missing concepts are identified without inventing statements the candidate did not make.
- Model output is validated before being saved.
- Demo-mode results are explicitly labelled as demo evaluations.

### FR-08: GitHub Repository Analysis

The system shall identify GitHub profile and repository URLs in extracted resume text and show them to the candidate. It shall not fetch repository information merely because a link appears in a resume.

After the candidate consents to repository discovery, the system shall list eligible repositories associated with the linked GitHub profile. The candidate shall choose and confirm the repositories to analyze. The system may then inspect repository metadata and a bounded set of files from selected repositories.

**Acceptance criteria:**

- Extracted URLs are restricted to valid GitHub profile or repository links; unrelated URLs are not fetched.
- Repository discovery and selected-repository analysis have clear, recorded consent and purpose.
- The candidate can select none, one, or multiple eligible repositories; unselected repositories are not analyzed.
- Repository/file counts, file sizes, and request time are bounded.
- Questions and practical tasks reference retrieved files or code excerpts.
- A code-change task is submitted as an answer or patch; the system does not write to GitHub or execute candidate code.
- Repository ownership is not treated as proof of individual authorship.
- API limits, missing repositories, and access failures are handled gracefully.
- Private repositories are unavailable unless a separate, least-privilege authorization flow is explicitly implemented.

### FR-09: Tutorial-Clone Detection

The system shall compare available source code against a labelled or otherwise documented reference set.

Possible techniques include token similarity, fingerprints, and language-specific syntax analysis.

**Acceptance criteria:**

- The output identifies the comparison method and available evidence.
- Similarity scores are not presented as conclusive plagiarism findings.
- Shared boilerplate and common algorithms are considered limitations.
- Accuracy claims are made only after evaluation against appropriate labelled data.

### FR-10: Alternative Assessment

The system shall support candidates without public repositories through role-relevant practical tasks, work samples, or scenarios.

**Acceptance criteria:**

- A candidate can complete the workflow without a GitHub account.
- Lack of public code does not automatically reduce the score.
- The resulting Proof Card identifies which assessment evidence was available.

### FR-11: Candidate Proof Card

The system shall generate a structured report containing:

- Candidate reference ID.
- Target job title.
- Overall assessment score.
- Skill-wise scores.
- Supporting evidence.
- Evidence confidence and limitations.
- Assessment questions and answers.
- Evaluation breakdowns.
- Strengths and improvement areas.
- Unverified claims.
- Recommendations.

**Acceptance criteria:**

- Every skill score can be traced to relevant evidence.
- Unsupported claims remain unverified.
- Missing evidence is disclosed.
- The overall score is reproducible from documented scoring rules.
- Exported reports preserve the same scores and evidence as the displayed report.

### FR-12: Recruiter Dashboard

The system shall display saved assessments and support candidate filtering by job and assessment status.

**Acceptance criteria:**

- Saved candidate assessments can be opened.
- Filters return the appropriate records.
- Candidate information is not fabricated.
- Access to sensitive candidate data is appropriately controlled.

### FR-13: Candidate Comparison and Ranking

The system shall compare two candidates against the same job description using relevant assessment evidence.

**Acceptance criteria:**

- Both candidates are evaluated using consistent job-specific criteria.
- Each comparison includes human-readable reasons.
- Missing or uncertain evidence is visible.
- College name, gender, age, and location are excluded from ranking features.
- Recruiters retain responsibility for hiring decisions.

### FR-14: Persistence and Data Management

The system shall persist candidate records, assessment sessions, questions, answers, scores, and evidence references.

**Acceptance criteria:**

- Results survive application restarts.
- Database relationships remain consistent.
- Duplicate records are handled safely.
- Candidate data can be deleted according to the documented retention policy.

### FR-15: Demo Mode

The application shall support a local demonstration without external model API credentials.

**Acceptance criteria:**

- Resume parsing and supported workflows can be tested locally.
- Deterministic fallback questions and scoring are clearly labelled.
- Mock outputs are not presented as real model evaluations.
- External-service limitations are explained.

## 7. Proof Card Scoring Requirements

The MVP shall keep three distinct measurements:

1. Skill performance score.
2. Evidence confidence.
3. Communication score.

The overall assessment formula must be documented and configurable.

If the initial implementation uses weighted components, weights and missing-component handling must be visible in the methodology.

No model-generated confidence estimate may be described as statistically calibrated without validation.

The platform must not interpret answer length, accent, or speaking confidence as proof of technical competence.

## 8. Fairness and Privacy Requirements

- Exclude college name, gender, age, and location from ranking features.
- Obtain explicit consent before repository analysis.
- Minimise collection and retention of personal data.
- Protect API credentials and candidate records.
- Avoid logging raw resumes or unnecessary personal information.
- Allow candidates to understand the evidence and methodology behind their scores.
- Provide alternative assessments for candidates without public repositories.
- Include human review for uncertain or disputed results.

Detailed implementation requirements are specified in `docs/SCORING_AND_FAIRNESS.md` and `docs/PRIVACY_AND_SECURITY.md`.

## 9. Non-Functional Requirements

### Reliability

The application must handle invalid input, missing API credentials, network errors, and malformed model responses without losing saved assessment data unnecessarily.

### Maintainability

The system shall separate UI, business logic, persistence, and model integrations into testable modules.

### Security

The application must validate external input, protect secrets, use parameterised database queries, and never execute candidate-provided code.

### Explainability

Scores and rankings must have human-readable explanations linked to relevant evidence.

### Reproducibility

The system shall record appropriate model configuration, scoring-rule version, and evaluation metadata for completed assessments.

### Usability

Candidates should be able to understand the next action, review their results, and distinguish claims from verified evidence.

## 10. Out of Scope for the Initial MVP

The following are not required for the first working release:

- Fully autonomous hiring decisions.
- Guaranteed plagiarism detection.
- Psychological profiling from voice or video.
- Custom foundation-model training.
- Unvalidated production-scale predictive hiring.
- Claims of fairness or recruiter agreement unsupported by evaluation.

## 11. External Dependencies and Assumptions

The final hackathon implementation may require:

- The official Integraminds fresher dataset.
- Labelled recruiter decisions associated with the supplied job descriptions.
- IMATS sandbox API documentation and credentials.
- Optional model-provider credentials.
- Authorised reference datasets for tutorial-clone analysis.

The existence of these resources in the problem statement does not mean they are already available locally. Their access, schema, permissions, and usage terms must be confirmed.

## 12. MVP Acceptance Gate

The initial MVP is ready for demonstration when:

1. A resume can be uploaded and analysed.
2. A job description can be supplied.
3. Relevant interview questions can be generated.
4. Answers can be submitted and evaluated.
5. Follow-up questions can adapt to previous answers.
6. The candidate receives a transparent Proof Card.
7. A technical candidate can opt into repository-based analysis.
8. A candidate without GitHub can complete an alternative assessment.
9. A recruiter can compare two candidates against one job description.
10. Ranking excludes prohibited features and provides reasons.
11. Data persists across application restarts.
12. Core automated tests pass.
13. The application runs in clearly labelled demo mode without API credentials.

A feature is not considered complete merely because a UI element exists. Its behaviour must be implemented and tested.

## 13. Success Metrics

The project should be evaluated using:

- Resume information extraction quality.
- Evidence-to-skill mapping quality.
- Agreement between automated and human answer evaluations.
- Tutorial-clone detection precision and recall on labelled references.
- Agreement with held-out recruiter shortlist decisions.
- Ranking fairness under the documented evaluation protocol.
- Candidate understanding of the Proof Card.
- Reliability of the end-to-end assessment workflow.

No target metric is considered achieved until it has been measured using a documented methodology and appropriate data.