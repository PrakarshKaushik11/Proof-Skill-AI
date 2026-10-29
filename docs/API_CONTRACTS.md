# ProofSkill AI — API Contracts

**Version:** 1.0  
**Status:** Proposed  
**Application type:** Python modular application  
**Initial interface:** Streamlit  
**External API:** IMATS sandbox integration, subject to documentation and access verification

---

## 1. Purpose

This document defines the interfaces between ProofSkill AI modules and the expected contracts for external integrations.

The initial MVP uses Python functions and service modules rather than requiring a separate HTTP backend. A REST API can be introduced later if the deployment architecture requires it.

The contracts cover:

- Resume processing.
- Job description analysis.
- Interview question generation.
- Answer evaluation.
- Evidence and Proof Card generation.
- Repository analysis.
- Recruiter comparison.
- Optional external integrations.

## 2. General Contract Rules

Every service should:

1. Accept validated inputs.
2. Return predictable, documented output structures.
3. Raise or return documented errors.
4. Avoid directly modifying Streamlit UI state.
5. Avoid exposing secrets or unnecessary personal information.
6. Be independently testable.
7. Support mock dependencies where practical.

Use Python type hints and structured schemas. Validate data at service boundaries.

Use consistent timestamps in UTC when timestamps are required.

### Common error categories

| Error code | Meaning |
|---|---|
| `INVALID_INPUT` | Input does not meet the required schema |
| `UNSUPPORTED_FILE` | File type is unsupported |
| `EXTRACTION_FAILED` | Document text could not be extracted |
| `NOT_FOUND` | Requested record does not exist |
| `CONSENT_REQUIRED` | Required consent has not been granted |
| `PROVIDER_UNAVAILABLE` | External AI provider is unavailable |
| `INVALID_PROVIDER_OUTPUT` | Provider response failed validation |
| `INTEGRATION_UNAVAILABLE` | External integration is unavailable |
| `ASSESSMENT_INCOMPLETE` | Required assessment evidence is missing |

Services should provide a human-readable message alongside an error code. Do not expose stack traces, API keys, or internal credentials to users.

---

## 3. Shared Data Structures

The following Python definitions illustrate the intended contract types. They can later be implemented using dataclasses or Pydantic models.

```python
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class ServiceError:
    code: str
    message: str
    retryable: bool = False


@dataclass
class EvidenceReference:
    source_type: str
    source_id: str | None
    skill_name: str
    excerpt: str | None = None


@dataclass
class SkillRequirement:
    skill_name: str
    weight: float
    required: bool = True


@dataclass
class SkillResult:
    skill_name: str
    performance_score: float | None
    evidence_coverage: float
    evidence_confidence: Literal[
        "low", "medium", "high", "not_assessed"
    ]
    status: Literal["assessed", "not_assessed"]
    evidence: list[EvidenceReference] = field(
        default_factory=list
    )
    explanation: str | None = None
```

These structures are proposed contracts. Validate all numeric values and enumerations before accepting or storing them.

---

## 4. Resume Service

**Suggested module:** `src/proofskill/services/resume_service.py`

### Function: `extract_resume_text`

**Input**

- Uploaded file bytes or a supported file object.
- Filename and detected content type.
- Configured upload size limit.

**Output**

```python
{
    "status": "success",
    "text": "Extracted resume text...",
    "content_type": "application/pdf",
    "warnings": []
}
```

**Requirements**

- Support PDF and DOCX.
- Validate file size and format.
- Handle empty or unreadable documents.
- Never execute uploaded content.
- Return a clear error when extraction fails.
- Do not claim OCR support until it is implemented.

### Function: `extract_candidate_evidence`

**Input**

- Extracted resume text.
- Optional allowed skill vocabulary.

**Output**

```python
{
    "skills": [
        {
            "skill_name": "Python",
            "evidence": [
                {
                    "source_type": "resume",
                    "excerpt": "Built a Python data processing project."
                }
            ]
        }
    ],
    "github_links": [
        {
            "url": "https://github.com/example-user",
            "link_type": "profile",
            "source_type": "resume",
            "verification_status": "candidate_claim"
        }
    ],
    "warnings": []
}
```

Resume statements and links are self-reported evidence. Extracting a GitHub URL must not trigger a network request or automatically label a skill or repository as verified.

GitHub links must be parsed and normalized against the approved `github.com` host. Reject unsupported schemes, embedded credentials, non-GitHub hosts, and malformed owner/repository paths.

---

## 5. Job Description Service

**Suggested module:** `src/proofskill/services/job_service.py`

### Function: `parse_job_requirements`

**Input**

- Job title.
- Job description.
- Optional configured skill vocabulary.

**Output**

```python
{
    "job_title": "Junior Python Developer",
    "requirements": [
        {
            "skill_name": "Python",
            "weight": 30.0,
            "required": True
        },
        {
            "skill_name": "Problem solving",
            "weight": 25.0,
            "required": True
        }
    ],
    "warnings": []
}
```

**Requirements**

- Validate that weights are numeric and non-negative.
- Normalize valid weights to a total of 100 before scoring.
- Do not silently invent requirements.
- Flag descriptions that do not contain enough information.
- Keep the final requirement set inspectable by the user.

---

## 6. Interview Service

**Suggested module:** `src/proofskill/services/interview_service.py`

### Function: `generate_questions`

**Input**

- Job requirements.
- Candidate evidence.
- Skills already assessed.
- Maximum question count.
- Configured question types and difficulty rules.

**Output**

```python
{
    "questions": [
        {
            "skill_name": "Python",
            "question_text": "Explain how a Python dictionary is used.",
            "question_type": "technical",
            "difficulty": "beginner",
            "weight": 1.0
        }
    ],
    "provider_mode": "demo",
    "warnings": []
}
```

**Requirements**

- Generate job-relevant questions.
- Avoid unnecessary repetition.
- Return a bounded number of questions.
- Validate every question before display.
- Clearly distinguish live AI generation from demo fallback.

### Function: `select_follow_up`

**Input**

- Current question.
- Validated evaluation of the previous answer.
- Skills still requiring assessment.
- Remaining question budget.

**Output**

```python
{
    "action": "ask_follow_up",
    "skill_name": "Python",
    "reason": "An important concept needs clarification"
}
```

Allowed actions should be explicitly defined, such as `ask_follow_up`, `assess_next_skill`, and `finish`.

Adaptive logic must follow the same rubric for comparable candidates.

---

## 7. Evaluation Service

**Suggested module:** `src/proofskill/services/evaluation_service.py`

### Function: `evaluate_answer`

**Input**

- Interview question.
- Candidate answer.
- Skill being evaluated.
- Versioned scoring rubric.
- Permitted supporting context.

**Output**

```python
{
    "status": "assessed",
    "skill_name": "Python",
    "score": 3,
    "max_score": 4,
    "score_scale": "0-4",
    "explanation": "The answer covers the main concept but misses an edge case.",
    "strengths": [
        "Correct core explanation"
    ],
    "gaps": [
        "Does not discuss an important edge case"
    ],
    "evidence_references": [
        "answer-001"
    ],
    "evidence_confidence": "medium",
    "rubric_version": "1.0",
    "provider_mode": "demo"
}
```

**Requirements**

- Validate the score range.
- Validate the response schema.
- Include evidence references where available.
- Support `not_assessed` when evaluation is not possible.
- Do not transform provider errors into a fabricated score.
- Do not use irrelevant demographic attributes.
- Store rubric and model metadata where available.

The evaluation service should return the raw 0–4 rubric score and its scale. Any normalized 0–100 performance score must be calculated separately using the documented scoring method.

---

## 8. Scoring Service

**Suggested module:** `src/proofskill/services/evaluation_service.py` or a dedicated scoring module.

### Function: `calculate_skill_score`

**Input**

- Valid answer evaluations for one skill.
- Predefined question weights.

**Output**

```python
{
    "skill_name": "Python",
    "performance_score": 80.0,
    "status": "assessed",
    "evidence_confidence": "medium"
}
```

### Function: `calculate_assessment_summary`

**Input**

- Job skill requirements.
- Candidate skill results.
- Assessment rubric version.

**Output**

```python
{
    "performance_score": 78.0,
    "score_status": "provisional",
    "evidence_coverage": 80.0,
    "unassessed_skills": [
        "SQL"
    ],
    "rubric_version": "1.0"
}
```

The values above are illustrative.

**Requirements**

- Use deterministic calculations.
- Reject invalid weights and scores.
- Exclude unassessed skills from the assessed-skill average while explicitly flagging them.
- Never silently convert missing evidence to zero.
- Use the same job weights for candidates being compared.
- Keep evidence coverage separate from performance.

---

## 9. Proof Card Service

**Suggested module:** `src/proofskill/services/proof_card_service.py`

### Function: `generate_proof_card`

**Input**

- Candidate assessment summary.
- Job requirements.
- Skill-level results.
- Supporting evidence references.
- Known limitations.

**Output**

```python
{
    "candidate_id": "demo-candidate-001",
    "job_id": "demo-job-python-001",
    "performance_score": 78.0,
    "score_status": "provisional",
    "evidence_coverage": 80.0,
    "strengths": [
        "Python fundamentals"
    ],
    "needs_assessment": [
        "SQL"
    ],
    "evidence": [],
    "limitations": [
        "One required skill remains unassessed."
    ],
    "rubric_version": "1.0"
}
```

**Requirements**

- Generate summaries from stored assessment results.
- Preserve evidence references.
- Display limitations and unassessed skills.
- Avoid unsupported claims.
- Use a versioned schema.
- Never present synthetic demo data as a real candidate result.

---

## 10. Repository Service

**Suggested module:** `src/proofskill/services/repository_service.py`

### Function: `analyze_repository`

**Input**

- Candidate-selected repository URL.
- Valid consent record covering analysis of that selected repository.
- Allowed file types and file-size limits.
- Maximum repository file count and response size.

**Output**

```python
{
    "status": "completed",
    "repository_metadata": {},
    "findings": [],
    "limitations": [
        "Repository metadata does not independently prove authorship."
    ]
}
```

**Requirements**

- Analyze only repositories selected and confirmed by the candidate.
- Verify consent scope before each discovery or analysis operation; a client-provided boolean is not authorization.
- Validate the URL and restrict outbound requests to supported GitHub URLs.
- Use safe HTTP requests with timeouts and bounded responses.
- Use read-only public GitHub access by default; private repositories require a separate, least-privilege authorization flow.
- Do not execute repository code.
- Do not write, commit, or push changes to the candidate's repository.
- Exclude credential files and avoid returning or logging detected secrets.
- Handle rate limits and private repositories.
- Do not request credentials to inspect public repositories.
- Avoid claiming that a candidate authored every file.
- Offer the alternative assessment when repository access is unavailable.

### Function: `discover_candidate_repositories`

**Input**

- GitHub profile or repository URL extracted from the resume.
- Valid consent record covering repository discovery.

**Output**

```python
{
    "account": "example-user",
    "repositories": [
        {
            "full_name": "example-user/task-api",
            "html_url": "https://github.com/example-user/task-api",
            "description": "Example project",
            "language": "Python",
            "visibility": "public"
        }
    ],
    "selection_required": True,
    "limitations": []
}
```

**Requirements**

- Do not fetch a profile or enumerate repositories before valid discovery consent.
- Show discovered metadata to the candidate and require them to select repositories before retrieving files.
- Do not analyze repositories the candidate did not select.
- Do not imply that profile ownership proves authorship or skill.
- Handle a direct repository link by offering that repository as a selectable option; do not silently expand it into analysis of the owner's other repositories.
- Do not enumerate private repositories without a separate, explicit authorization flow.

### Function: `generate_repository_viva`

**Input**

- Inspected repository findings.
- Candidate-visible project context.
- Required skills.
- Selected-repository evidence references.
- Task types and assessment time limit.

**Output**

A structured set of questions and practical tasks grounded in selected repository evidence.

Question/task types may include explaining a code path, debugging a described issue, proposing a focused code change, submitting a patch or diff, justifying an approach, comparing valid alternatives, and explaining architecture or trade-offs.

Every repository-specific item must reference inspected evidence. A code-change task is returned by the candidate as an answer or patch for review; the system does not apply or execute it. Questions must not assume that a candidate personally wrote every inspected line.

---

## 11. Alternative Assessment Service

**Suggested module:** `src/proofskill/services/alternative_assessment_service.py`

### Function: `create_alternative_assessment`

**Input**

- Job requirements.
- Skills requiring assessment.
- Configured task templates.

**Output**

```python
{
    "assessment_type": "guided_project_explanation",
    "tasks": [],
    "rubric_version": "1.0",
    "status": "created"
}
```

**Requirements**

- Work without a GitHub account or public portfolio.
- Evaluate the same job-relevant skills where possible.
- Use an explicit and comparable rubric.
- Record the assessment method so recruiters can interpret results fairly.
- Do not automatically lower a candidate's score for lacking public projects.

---

## 12. Recruiter Service

**Suggested module:** `src/proofskill/services/recruiter_service.py`

### Function: `compare_candidates`

**Input**

- Job identifier.
- Completed or explicitly provisional candidate assessment summaries.
- Versioned scoring rules.

**Output**

```python
{
    "job_id": "demo-job-python-001",
    "rubric_version": "1.0",
    "comparisons": [
        {
            "candidate_id": "demo-candidate-001",
            "performance_score": 78.0,
            "score_status": "provisional",
            "evidence_coverage": 80.0,
            "unassessed_skills": [
                "SQL"
            ],
            "explanation": "Strong evidence in assessed Python skills; SQL remains unassessed."
        }
    ],
    "warnings": [
        "Provisional results require careful comparison."
    ]
}
```

**Requirements**

- Use the same job requirements and rubric.
- Exclude college name, gender, age, and location from ranking features.
- Display evidence coverage and unassessed skills.
- Make explanations traceable to actual results.
- Avoid treating an incomplete score as directly equivalent to a fully assessed score.
- Support human review instead of automatic rejection.

---

## 13. AI Provider Contract

**Suggested module:** `src/proofskill/ai/provider.py`

A provider should implement the operations required by the application, such as:

- `generate_questions`
- `evaluate_answer`
- `extract_skills`

The live provider and deterministic fallback should return compatible schemas.

Provider metadata should identify the execution mode as `live` or `demo`. Do not claim that a live model was used when a fallback generated the result.

Every provider call should have:

- Input validation.
- A timeout.
- Bounded retry behavior.
- Output validation.
- A documented error path.

---

## 14. IMATS Integration Contract

**Suggested module:** `src/proofskill/integrations/imats_client.py`

The exact contract must be derived from the official IMATS documentation.

Before implementation, confirm:

- Base URL and supported endpoints.
- Authentication method.
- Request and response schemas.
- Rate limits and timeout expectations.
- Required payload fields.
- Error codes and retry rules.
- Data retention and submission requirements.

Until these details are confirmed, use a mock adapter with clearly labeled demo responses.

Do not invent endpoint URLs, authentication headers, or request schemas.

---

## 15. External API Error Handling

External integrations should map provider-specific failures into documented application errors.

Examples:

- Timeout → `INTEGRATION_UNAVAILABLE`
- Invalid provider output → `INVALID_PROVIDER_OUTPUT`
- Missing repository consent → `CONSENT_REQUIRED`
- Unsupported upload → `UNSUPPORTED_FILE`

Error messages should tell the user what happened and, where possible, how to proceed.

Do not expose raw secrets, credentials, internal stack traces, or private provider responses in the UI.

---

## 16. Contract Testing

Each service should have tests for:

- Valid input and expected output.
- Missing required fields.
- Invalid types and score ranges.
- Empty inputs.
- External service failures.
- Malformed AI responses.
- Fallback behavior.
- Consent enforcement.
- Unassessed skills.
- Evidence-reference validity.

Integration tests should use mock providers and a temporary database so they can run without paid API keys or external network access.

---

## 17. Implementation Status

**Current status:** Proposed contracts.

The contracts should be updated alongside implementation. Changes to schemas must be reflected in their callers and tests.

The application should remain runnable after each completed milestone.
