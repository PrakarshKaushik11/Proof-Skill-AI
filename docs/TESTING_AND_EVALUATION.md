TESTING.md# ProofSkill AI — Testing Strategy

**Version:** 1.0  
**Status:** Proposed  
**Testing framework:** pytest  
**Application:** Python and Streamlit  
**Database:** SQLite

---

## 1. Purpose

This document defines the testing strategy for ProofSkill AI.

Testing must verify that the application:

- Processes supported resumes correctly.
- Extracts and matches job-related skills.
- Generates relevant interview questions.
- Evaluates answers using a consistent rubric.
- Produces evidence-backed Proof Cards.
- Compares candidates using the same job requirements.
- Enforces consent and privacy requirements.
- Works without external API credentials in demo mode.
- Handles missing, malformed, and incomplete data safely.

The project must not claim that a feature is tested until the relevant tests have actually been executed.

## 2. Testing Principles

1. Test business logic independently of the user interface.
2. Use synthetic candidate data during development.
3. Prefer deterministic tests for scoring and ranking.
4. Mock external AI and API services in routine tests.
5. Test both successful and failure scenarios.
6. Test missing evidence separately from poor performance.
7. Include fairness and security checks.
8. Keep tests independent of execution order.
9. Do not require paid API keys to run the core test suite.
10. Record actual test results before the final demonstration.

## 3. Testing Levels

### 3.1 Unit Tests

Test individual functions in isolation.

Examples:

- Resume text extraction helpers.
- Job requirement validation.
- Skill matching.
- Score calculation.
- Evidence coverage calculation.
- Proof Card generation.
- Candidate ranking.
- Consent validation.

### 3.2 Integration Tests

Test multiple modules working together.

Examples:

- Resume upload to skill extraction.
- Job description to interview generation.
- Answer submission to evaluation.
- Evaluation records to Proof Card.
- Assessment summaries to recruiter comparison.

Use a temporary SQLite database and mock external providers.

### 3.3 User Interface Tests

Verify that users can:

- Upload a supported resume.
- Enter a job description.
- Start an interview.
- Submit typed answers.
- Review results and evidence.
- Access a Proof Card.
- Compare candidates as an authorized recruiter.
- Use the alternative assessment without a repository.

UI tests may use Streamlit's testing utilities where appropriate.

### 3.4 End-to-End Tests

Run the main workflow from candidate input to recruiter review.

At least one end-to-end test should run entirely with synthetic data and no external credentials.

### 3.5 Evaluation Tests

When an appropriate evaluation dataset is available, compare system outputs with independently reviewed reference results.

Synthetic tests and official dataset evaluation must be reported separately.

---

## 4. Proposed Test Structure

```text
tests/
├── conftest.py
├── unit/
│   ├── test_resume_service.py
│   ├── test_job_service.py
│   ├── test_interview_service.py
│   ├── test_evaluation_service.py
│   ├── test_proof_card_service.py
│   ├── test_recruiter_service.py
│   └── test_consent.py
├── integration/
│   ├── test_candidate_workflow.py
│   ├── test_database.py
│   └── test_demo_mode.py
├── fairness/
│   ├── test_excluded_attributes.py
│   └── test_missing_evidence.py
└── fixtures/
    ├── sample_resume.txt
    ├── sample_job.json
    └── sample_answers.json
```

This is the recommended organization. Adapt paths to the actual application structure.

## 5. Test Environment

Recommended development dependencies:

```text
pytest
pytest-cov
```

Install the project's development dependencies according to its dependency-management approach.

Run the tests using:

```bash
python -m pytest -q
```

Run tests with a coverage report using:

```bash
python -m pytest --cov=src/proofskill --cov-report=term-missing
```

These commands assume the package is located under `src/proofskill`. Update the coverage target if the actual structure differs.

Tests must not require production credentials or access to real candidate records.

## 6. Unit Test Requirements

### 6.1 Resume Processing

Test that:

- Valid PDF files can be processed when PDF support is implemented.
- Valid DOCX files can be processed when DOCX support is implemented.
- Empty documents are handled safely.
- Unsupported file types are rejected.
- Oversized uploads are rejected.
- Malformed documents produce a clear error.
- Temporary files are cleaned up where applicable.
- Embedded instructions are treated as untrusted content.

### 6.2 Job Description Processing

Test that:

- Valid job descriptions produce structured requirements.
- Empty descriptions are rejected or flagged.
- Skill names are normalized consistently.
- Negative weights are rejected.
- Invalid weights are rejected.
- Valid weights are normalized correctly.
- Missing requirements are not silently invented.

### 6.3 Interview Generation

Test that:

- Questions relate to the target job.
- Question counts respect configured limits.
- Invalid model responses are rejected.
- Previously assessed skills are handled correctly.
- Follow-up questions have a documented reason.
- Demo mode produces predictable questions.

### 6.4 Answer Evaluation

Test that:

- Scores remain within the allowed range.
- Invalid score values are rejected.
- Empty answers can be marked not assessed where appropriate.
- Explanations do not reference nonexistent evidence.
- The rubric version is preserved.
- Provider failures do not create fabricated evaluations.
- Demo and live results are distinguishable.

### 6.5 Proof Card Generation

Test that:

- Skill scores match stored evaluations.
- Evidence coverage is calculated correctly.
- Unassessed skills are displayed.
- Provisional scores are labeled.
- Evidence references remain traceable.
- Unsupported claims are not added.
- Synthetic demo results are clearly labeled.

### 6.6 Recruiter Comparison

Test that:

- Candidates use the same job requirements.
- Candidate scores are calculated consistently.
- Incomplete assessments are flagged.
- Missing skills are not silently scored as zero.
- Results are traceable to underlying assessment records.
- Ranking is deterministic for identical inputs and configuration.

---

## 7. Scoring Tests

Scoring calculations should be tested independently of any AI model.

### Example: Weighted Average

Given two assessed skills:

- Python: 80 points with a weight of 60%.
- SQL: 70 points with a weight of 40%.

Expected weighted performance score:

\[
(80 \times 0.60) + (70 \times 0.40) = 76
\]

Expected result: `76.0`.

### Example: Evidence Coverage

Suppose a job has four equally weighted required skills and three have been assessed.

\[
\text{Coverage} = \frac{3}{4}\times100 = 75\%
\]

Expected result: `75.0`.

### Required scoring checks

- [ ] Weighted averages match expected values.
- [ ] Zero and maximum valid scores are handled correctly.
- [ ] Negative scores are rejected.
- [ ] Scores above the maximum are rejected.
- [ ] Invalid weights are rejected.
- [ ] All-unassessed inputs produce an appropriate not-assessed status.
- [ ] Missing skills are flagged.
- [ ] Coverage remains separate from performance.
- [ ] Provisional results are labeled.
- [ ] Floating-point results are compared using suitable tolerances.

## 8. Fairness Tests

The ranking calculation must exclude college name, gender, age, and location.

Test this property by creating equivalent assessment records that differ only in an excluded attribute, then confirming that the computed scores and ranking features remain unchanged.

Also test that:

- Candidates without public repositories can complete an alternative assessment.
- Lack of a GitHub account does not automatically lower skill performance.
- Missing evidence is not treated as evidence of poor ability.
- The same rubric is used for candidates assessed against the same job.
- Accent and vocal characteristics are not used as technical scoring features.
- Irrelevant personal information is not included in model evaluation prompts.

These tests verify defined software behavior; they do not establish that the complete system is free from bias.

## 9. Privacy and Security Tests

Verify that:

- Repository analysis cannot begin without the required consent.
- Unsupported file types are rejected.
- Oversized uploads are rejected.
- Database queries use parameterized SQL.
- External URLs are validated before requests.
- Repository code is never executed.
- API secrets are not included in logs or responses.
- Prompt injection in resumes or repositories does not override application rules.
- Unauthorized users cannot access protected candidate records when authentication is implemented.
- Deletion and retention rules behave as documented.

Security-sensitive tests should use synthetic data and mock external services.

## 10. AI Provider Tests

Use a fake provider to test the application independently of real LLM services.

Test scenarios:

| Scenario | Expected behavior |
|---|---|
| Valid structured output | Accept after validation |
| Missing required fields | Reject or retry within configured limits |
| Invalid score | Reject the evaluation |
| Timeout | Return a controlled error or documented fallback |
| Missing API key | Use demo mode or explain the configuration requirement |
| Malformed response | Do not store an invalid evaluation |
| Unsupported evidence reference | Reject or flag the response |
| Provider unavailable | Keep the rest of the application usable where possible |

Live-provider smoke tests may be run separately and should require explicit configuration.

## 11. Database Tests

Use a temporary database for tests.

Verify that:

- Database initialization succeeds from a clean state.
- Foreign key enforcement is enabled.
- Invalid relationships are rejected.
- Assessment records link to the correct candidate and job.
- Answers link to valid questions.
- Evaluations preserve rubric versions.
- Proof Card versions obey their uniqueness constraint.
- Transactions do not leave partially written records after a failure.
- Schema changes do not silently destroy existing data.

Tests should not modify the developer's real database.

## 12. End-to-End Acceptance Test

The following workflow should pass using demo data:

1. Start the application without API credentials.
2. Select or create a synthetic candidate.
3. Load a synthetic resume.
4. Enter a sample job description.
5. Extract skills and supporting evidence.
6. Generate interview questions.
7. Submit typed answers.
8. Evaluate answers using the configured demo provider.
9. Generate a Proof Card.
10. Inspect skill scores, evidence coverage, and limitations.
11. Compare candidates for the same job.
12. Verify that incomplete evidence is visibly flagged.

**Expected outcome:** The workflow completes without requiring an external AI provider, GitHub credentials, or the official dataset.

## 13. Evaluation Dataset Testing

If the official anonymized dataset becomes available, use it only according to the applicable access and usage requirements.

Before evaluation:

- Confirm dataset provenance and permitted use.
- Inspect the schema and data quality.
- Identify duplicate or leakage risks.
- Separate development and held-out evaluation data.
- Avoid using held-out labels to tune the model.
- Record the evaluation configuration.

Potential metrics include:

- Skill extraction precision and recall.
- Agreement with human-reviewed assessment scores.
- Ranking quality against valid reference outcomes.
- Evidence coverage.
- Invalid output rate.
- Evaluation latency and cost.
- Fairness-related performance differences, when appropriate data and authorization are available.

Do not claim official dataset performance unless the evaluation was actually completed and the methodology is documented.

## 14. Test Reporting

For each test run, record:

- Date and environment.
- Code version or commit.
- Command executed.
- Number of tests passed and failed.
- Coverage report, if generated.
- Known failures and limitations.
- Whether external services were mocked or live.

Do not describe the test suite as passing if it has not been executed successfully.

## 15. Definition of Done

A feature is ready for demonstration when:

- Its main behavior is implemented.
- Inputs and outputs are validated.
- Expected failure cases are handled.
- Relevant automated tests pass.
- Privacy and fairness requirements are addressed.
- Documentation matches the actual implementation.
- The feature works in demo mode where required.

## 16. Implementation Status

**Current status:** Proposed testing strategy.

Update this document as the test suite is implemented. Record actual results rather than anticipated results.
