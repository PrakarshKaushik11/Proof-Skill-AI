# ProofSkill AI — Development Roadmap

**Project:** ProofSkill AI  
**Track:** Software  
**Theme:** AI Frontier  
**Problem ID:** IM-105 Advanced  
**Status:** Planned  
**Timeline:** To be finalized based on hackathon deadline and team size

---

## 1. Roadmap Objectives

This roadmap defines the order in which ProofSkill AI will be developed, tested, and prepared for demonstration.

The project will prioritize a working end-to-end candidate assessment workflow over building many disconnected features.

The core workflow is:

1. Candidate uploads a resume.
2. Recruiter or candidate provides a job description.
3. The system extracts skills and identifies supporting evidence.
4. The system generates relevant interview questions.
5. Candidate answers questions and receives evidence-based evaluation.
6. The system generates a Proof Card.
7. Recruiters compare candidates against the same job description.
8. The system explains its assessment and applies fairness safeguards.

Repository analysis and alternative assessments will extend the core workflow.

## 2. Development Principles

- **Build incrementally:** Each milestone should leave the application runnable.
- **Evidence before claims:** Skills must be linked to resume, repository, assessment, or other available evidence.
- **Transparent scoring:** Display scoring criteria and limitations instead of unexplained rankings.
- **Fairness by design:** Exclude college name, gender, age, and location from scoring and ranking.
- **Consent first:** Request permission before accessing a candidate's repository or other optional data.
- **Fallback-friendly:** The demo should work without paid API keys, external services, or the official dataset.
- **Reproducibility:** Use fixed demo data and predictable fallback behavior for presentations.
- **Honest integration claims:** Do not claim official IMATS integration or validated dataset performance until verified.

## 3. Milestones

### M0 — Project Foundation

**Priority:** Must-have

**Planned work**
- Establish the application entry point and project configuration.
- Add dependency management and `.env.example`.
- Create the database schema and initialization flow.
- Add reusable configuration, logging, and error-handling utilities.
- Create demo mode with sample candidate and job data.
- Add initial tests and setup instructions.

**Acceptance criteria**
- The application starts using documented commands.
- The database initializes successfully.
- Demo mode works without API credentials.
- Missing configuration produces a clear message rather than crashing.

### M1 — Resume and Job Description Analysis

**Priority:** Must-have

**Planned work**
- Support PDF and DOCX resume uploads.
- Extract text and handle empty or unreadable documents.
- Accept pasted or uploaded job descriptions.
- Identify skills, projects, education, and relevant experience.
- Map extracted skills to supporting evidence where available.
- Compare candidate evidence against job requirements.

**Acceptance criteria**
- Supported resumes can be parsed.
- Unreadable files produce a useful error.
- Skill matches include supporting evidence or are explicitly marked as inferred.
- Missing evidence is not presented as proof of missing ability.

### M2 — Adaptive Interview Engine

**Priority:** Must-have

**Planned work**
- Generate interview questions from the job description and candidate evidence.
- Support technical, conceptual, and project-based questions.
- Provide typed-answer submission.
- Evaluate answers using configurable criteria.
- Adapt later questions based on previous answers.
- Store questions, answers, evaluation results, and evidence references.

**Acceptance criteria**
- Questions are relevant to the selected role.
- The interview can run without voice input.
- Scores include explanations and evaluation criteria.
- The system distinguishes observed performance from uncertain inferences.
- A deterministic fallback works when an LLM service is unavailable.

### M3 — Proof Card and Evidence-Based Scoring

**Priority:** Must-have

**Planned work**
- Create a candidate Proof Card.
- Summarize demonstrated skills and supporting evidence.
- Show interview performance and assessment coverage.
- Display evidence confidence separately from skill performance.
- Include limitations and missing evidence.
- Make scoring criteria understandable to candidates and recruiters.

**Acceptance criteria**
- The Proof Card is generated from stored assessment data.
- Each displayed claim is traceable to its available source.
- Missing data is not silently converted into a zero score.
- Confidence is not represented as a guarantee of candidate ability.

### M4 — Repository Analysis and Alternative Assessment

**Priority:** Important

**Planned work**
- Extract and display GitHub profile/repository links from resumes without fetching them automatically.
- Request consent before public repository discovery; present discovered repositories for candidate selection and confirmation.
- Retrieve bounded metadata and relevant files only from selected repositories.
- Generate evidence-grounded viva questions and tasks for code explanation, focused changes, approach comparisons, and architecture.
- Accept candidate changes as explanation or patch/diff responses; do not write to GitHub or execute code.
- Compare interview explanations with the submitted project evidence.
- Offer an alternative assessment for candidates without GitHub or a public portfolio.

**Acceptance criteria**
- Candidates can decline discovery or select no repositories.
- A resume link alone triggers no network access; only selected repositories are analyzed.
- The assessment remains usable without GitHub.
- Repository access failures are handled gracefully.
- Repository claims are supported by inspected evidence.
- Project-specific questions and tasks cite selected-repository evidence.
- Repository access remains read-only and candidate code is never executed.
- No unsupported claim of authorship or plagiarism is made solely from repository metadata.

### M5 — Recruiter Dashboard and Fair Comparison

**Priority:** Must-have

**Planned work**
- Display candidate Proof Cards.
- Compare candidates against the same job description.
- Show skill coverage, evidence quality, assessment results, and limitations.
- Explain ranking factors.
- Exclude protected or irrelevant demographic information from scoring.
- Allow recruiters to inspect the evidence behind a score.

**Acceptance criteria**
- Candidates are evaluated using the same job requirements and scoring rubric.
- Rankings are explainable and reproducible for the same stored inputs.
- College name, gender, age, and location do not affect the ranking calculation.
- Recruiters can review the underlying evidence before making a decision.
- The system presents recommendations as decision support, not automatic hiring decisions.

### M6 — Voice Assessment and Advanced Similarity Checks

**Priority:** Stretch

**Planned work**
- Add speech-to-text for spoken answers.
- Provide a typed-answer alternative.
- Explore similarity checks for suspiciously similar submissions.
- Review false-positive risks and document limitations.
- Add export options for Proof Cards if time permits.

**Acceptance criteria**
- Voice is optional.
- Equivalent typed answers remain supported.
- Accent, gender, and vocal characteristics are not used to infer technical competence.
- Similarity alerts are treated as review signals, not proof of cheating.
- Optional features do not break the core assessment workflow.

### M7 — Evaluation and Validation

**Priority:** Must-have before making performance claims

**Planned work**
- Create representative synthetic test data if official data is unavailable.
- Test parsing, scoring, interview generation, ranking, and fallback behavior.
- Evaluate against the official anonymized dataset if access is granted.
- Use a held-out evaluation set where available.
- Measure ranking quality, evidence coverage, error rates, and fairness-related outcomes.
- Record limitations and known failure cases.

**Acceptance criteria**
- Automated tests run successfully.
- Evaluation data and methods are documented.
- Results distinguish synthetic testing from official dataset evaluation.
- No benchmark result is claimed without a reproducible measurement.
- Fairness testing is documented, including limitations caused by unavailable demographic or outcome data.

### M8 — Integration and Final Demo

**Priority:** Must-have for release readiness

**Planned work**
- Verify the IMATS sandbox API documentation and credentials.
- Implement integration only after the interface is confirmed.
- Keep a mock adapter for offline demonstrations.
- Prepare a complete candidate-to-recruiter demonstration.
- Add setup instructions, screenshots, known limitations, and troubleshooting guidance.
- Perform a final clean-install test.

**Acceptance criteria**
- The demo can be run using the documented steps.
- The main workflow works with demo data.
- External service failures do not make the entire demo unusable.
- Official integration is clearly distinguished from mock integration.
- No real candidate data or credentials are exposed in the repository.

## 4. Suggested Hackathon Schedule

This is an illustrative schedule, not a fixed commitment. Adjust it according to the actual deadline and team size.

| Time window | Focus | Target milestone |
|---|---|---|
| Day 1 | Setup, configuration, database, demo mode | M0 |
| Days 2–3 | Resume parsing and job matching | M1 |
| Days 4–5 | Adaptive interview and answer evaluation | M2 |
| Day 6 | Proof Card and scoring explanations | M3 |
| Days 7–8 | Repository analysis and alternative path | M4 |
| Day 9 | Recruiter comparison and fairness checks | M5 |
| Day 10 | Testing, evaluation, documentation, final demo | M7–M8 |

If time is limited, complete the core workflow before implementing voice or advanced similarity detection.

## 5. Feature Priorities

### P0 — Essential

- Runnable application and documented setup
- Demo mode
- Resume upload and parsing
- Job description input
- Skill extraction and evidence mapping
- Adaptive interview with typed answers
- Explainable assessment
- Proof Card
- Recruiter comparison
- Fairness safeguards
- Basic automated tests

### P1 — Important

- Consent-based repository analysis
- Repository-specific viva
- Alternative assessment without GitHub
- Persistent assessment history
- Improved document handling
- Evaluation reports

### P2 — Optional

- Voice input
- Advanced code similarity detection
- Proof Card PDF export
- Additional authentication and deployment features
- More sophisticated ranking models

## 6. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Official dataset is unavailable | Use clearly labeled synthetic demo data; do not claim official validation |
| IMATS API access is unavailable | Use a mock adapter and document the missing integration |
| LLM API key or network is unavailable | Provide deterministic demo responses |
| Resume parsing fails | Show a clear error and allow manual text entry |
| LLM evaluation is inconsistent | Use a defined rubric, structured output, and stored evaluation results |
| Repository is private or inaccessible | Explain the issue and offer the alternative assessment |
| Similarity detection flags legitimate work | Use alerts for human review, not automatic penalties |
| Sensitive candidate data is exposed | Minimize collection, obtain consent, and avoid logging secrets or unnecessary personal data |
| Ranking introduces unfairness | Exclude irrelevant personal attributes and test the ranking pipeline |
| Too many features threaten delivery | Protect the P0 scope and defer stretch features |

## 7. Release Readiness Checklist

Before the final demonstration:

- [ ] The application starts from a clean environment.
- [ ] Installation and run instructions have been tested.
- [ ] Demo mode works without external credentials.
- [ ] Resume parsing and job description input work.
- [ ] Interview questions and typed answers work.
- [ ] Evaluation criteria and score explanations are visible.
- [ ] The Proof Card shows evidence and limitations.
- [ ] Recruiter comparison uses the same job requirements.
- [ ] Fairness safeguards are tested.
- [ ] Repository analysis is consent-based.
- [ ] The alternative assessment works without GitHub.
- [ ] Automated tests have been run and results recorded.
- [ ] Official dataset results are claimed only if actually measured.
- [ ] IMATS integration is labeled accurately.
- [ ] No secrets or real candidate data are committed.
- [ ] Known limitations are documented.

## 8. Roadmap Maintenance

- Update milestone status as work progresses.
- Record important design decisions and changes.
- Add new tasks to `TASKS.md` before expanding scope.
- Do not mark a milestone complete until its acceptance criteria have been tested.
- Prioritize a reliable end-to-end demo over unfinished advanced features.

**Current status:** Planned. Milestone completion must be updated based on actual implementation and test results.
