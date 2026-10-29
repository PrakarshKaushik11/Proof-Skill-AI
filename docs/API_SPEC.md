# API Specification — ProofSkill AI

- **Project:** ProofSkill AI
- **Version:** 1.0.0
- **Status:** Proposed
- **API style:** REST
- **Base path:** `/api/v1`
- **Primary format:** JSON

## 1. Purpose

This document defines the proposed API contract for ProofSkill AI, an evidence-backed skill assessment platform.

The API supports candidate profile creation, resume analysis, project evidence management, technical assessments, skill profile generation, and recruiter-facing candidate comparisons.

The initial implementation may run as a local Streamlit application with internal Python service functions. The endpoints in this document define a future-compatible interface and must not be considered implemented until corresponding routes and tests exist.

## 2. API Design Principles

- Use consistent resource names and JSON schemas.
- Validate incoming data before processing.
- Separate candidate claims, source evidence, model inferences, and assessment results.
- Return explainable, job-relevant evaluation results.
- Never invent missing evidence.
- Use stable identifiers for resources.
- Apply authorization checks to sensitive operations.
- Avoid exposing internal stack traces or secrets.
- Support graceful handling of unavailable AI providers and external integrations.
- Keep final hiring decisions under human control.

## 3. Base URL and Versioning

For local development, the API base URL may be configured as:

```text
http://localhost:8000/api/v1
```

The host and port are configuration choices, not guaranteed deployment values.

All versioned endpoints use the `/api/v1` prefix. Breaking contract changes should use a new API version or an explicitly documented migration strategy.

Unless otherwise stated:

- Request and response bodies use JSON.
- Resource identifiers are opaque strings.
- Timestamps use ISO 8601 UTC format.
- Missing information is represented explicitly rather than fabricated.
- Error responses use a consistent structure.

## 4. Common Data Conventions

### 4.1 Resource identifiers

Each resource should have a stable, unique identifier. UUIDs are a suitable default.

Examples:

- `candidate_id`
- `job_id`
- `evidence_id`
- `assessment_id`
- `profile_id`

Identifiers must not contain sensitive personal information.

### 4.2 Evidence provenance

Where a result relies on evidence, the API should expose the relevant source reference and evidence type.

Example:

```json
{
  "evidence_id": "ev_example_001",
  "source_type": "resume",
  "source_reference": "resume_section_03",
  "claim": "Experience with Python",
  "verification_status": "candidate_claim",
  "created_at": "2026-10-29T10:00:00Z"
}
```

The values above are illustrative examples, not real candidate records.

Supported verification statuses may include:

- `candidate_claim`
- `observed`
- `assessed`
- `verified`
- `unverified`

The status must reflect the actual verification performed. Extracting a claim from a resume does not independently verify it.

### 4.3 Score representation

Scores must include their scale and meaning.

Example:

```json
{
  "criterion": "python_fundamentals",
  "score": 3,
  "max_score": 4,
  "score_scale": "0-4",
  "evidence_ids": ["ev_example_001"],
  "explanation": "The assessment response correctly explains the relevant concept.",
  "limitations": []
}
```

The example score is illustrative. Actual scores must come from the configured rubric and assessment process.

## 5. Endpoint Summary

The following endpoints define the proposed contract.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Check service availability |
| `POST` | `/candidates` | Create a candidate record |
| `GET` | `/candidates/{candidate_id}` | Retrieve an authorized candidate record |
| `POST` | `/candidates/{candidate_id}/resume` | Submit a resume for processing |
| `GET` | `/candidates/{candidate_id}/evidence` | List authorized evidence records |
| `POST` | `/candidates/{candidate_id}/evidence` | Add candidate-provided evidence |
| `POST` | `/jobs` | Create a job description record |
| `GET` | `/jobs/{job_id}` | Retrieve a job description |
| `POST` | `/assessments` | Create an assessment |
| `POST` | `/assessments/{assessment_id}/responses` | Submit an assessment response |
| `GET` | `/assessments/{assessment_id}` | Retrieve assessment status and results |
| `POST` | `/profiles/generate` | Generate an evidence-backed skill profile |
| `POST` | `/comparisons` | Compare candidates against a job description |

An implementation may expose only a subset of these routes during the hackathon. The endpoint list must be updated as routes are implemented.

## 6. Health Check

### Request

```http
GET /api/v1/health
```

### Successful response

```json
{
  "status": "ok",
  "api_version": "v1"
}
```

The health endpoint should not expose secrets, environment variables, internal file paths, or detailed infrastructure information.

If dependency health is exposed separately, distinguish application availability from optional AI provider or external API availability.

## 7. Candidate Endpoints

### 7.1 Create candidate

`POST /api/v1/candidates`

Creates a candidate record using the minimum information required by the workflow.

Example request:

```json
{
  "display_name": "Demo Candidate",
  "consent": {
    "evidence_processing": true
  }
}
```

Example response — `201 Created`:

```json
{
  "candidate_id": "cand_example_001",
  "status": "created"
}
```

The example name and identifier are fictional. Production implementations should avoid collecting a display name if a pseudonymous identifier is sufficient.

### 7.2 Retrieve candidate

`GET /api/v1/candidates/{candidate_id}`

Returns the candidate record only when the caller is authorized to access it.

Example response:

```json
{
  "candidate_id": "cand_example_001",
  "status": "active",
  "profile_status": "not_generated"
}
```

Do not return raw resumes, private repository contents, or unnecessary personal information through this endpoint.

## 8. Resume Processing

### Request

`POST /api/v1/candidates/{candidate_id}/resume`

Suggested content type: `multipart/form-data`.

Expected file formats for the initial design:

- PDF
- DOCX

The implementation must validate file size, file type, parsing errors, and authorization before processing.

### Successful response

Example — `202 Accepted` for asynchronous processing:

```json
{
  "job_id": "resume_job_example_001",
  "candidate_id": "cand_example_001",
  "status": "queued"
}
```

If processing is synchronous, the implementation may return `200 OK` with the extraction result instead. The chosen behavior must be consistent and documented.

### Processing result

```json
{
  "job_id": "resume_job_example_001",
  "status": "completed",
  "extracted_skills": [
    {
      "name": "Python",
      "evidence_ids": ["ev_example_001"],
      "confidence": 0.91
    }
  ],
  "warnings": []
}
```

Confidence indicates extraction or matching confidence, not the probability that the candidate possesses the skill. The API must document how confidence is calculated.

## 9. Evidence Endpoints

### 9.1 Add evidence

`POST /api/v1/candidates/{candidate_id}/evidence`

Example request:

```json
{
  "source_type": "project_description",
  "title": "Inventory Management Project",
  "content": "A demo project using Python and SQLite."
}
```

Example response — `201 Created`:

```json
{
  "evidence_id": "ev_example_002",
  "candidate_id": "cand_example_001",
  "source_type": "project_description",
  "status": "recorded"
}
```

The application must enforce actual consent and permission requirements server-side for any data source that requires them. A client-supplied boolean is not authorization.

### 9.2 List evidence

`GET /api/v1/candidates/{candidate_id}/evidence`

Example response:

```json
{
  "candidate_id": "cand_example_001",
  "items": [
    {
      "evidence_id": "ev_example_001",
      "source_type": "resume",
      "verification_status": "candidate_claim"
    },
    {
      "evidence_id": "ev_example_002",
      "source_type": "project_description",
      "verification_status": "candidate_claim"
    }
  ]
}
```

Return only evidence records the caller is permitted to view.

### 9.3 Repository evidence

Repository integration should use a dedicated adapter for GitHub or another approved provider.

Requirements:

- Extracted resume links are candidate claims; never fetch a link or enumerate its account's repositories merely because it appears in a resume.
- Obtain and record candidate consent for repository discovery before listing public repositories.
- Present discovered repositories to the candidate and require explicit selection and confirmation before retrieving repository files.
- Analyze only the selected repositories. A direct repository link is offered as a selection and does not authorize enumeration of the owner's other projects.
- Obtain separate, explicit, least-privilege authorization before private repository access; public-only support is the default.
- Request the minimum required permissions.
- Handle unavailable or deleted repositories safely.
- Never expose access tokens in responses or logs.
- Treat repository content as untrusted input.
- Do not execute submitted code during routine evidence collection.
- Do not write, commit, or push assessment changes to a candidate repository.
- Bound repository count, file count, file size, response size, and request time. Exclude known credential/configuration files and avoid returning or logging detected secrets.
- Record which repository metadata or content supports an assessment claim.

Public repository availability must not be a mandatory condition for completing an assessment.

### Proposed repository discovery and selection contract

These are proposed operations, not implemented routes. They may be exposed as API routes or internal service calls in a Streamlit MVP.

1. After resume extraction, show any normalized GitHub links and ask the candidate whether to discover repositories. Do not fetch links before this choice.
2. With a valid server-side consent record, list only public repository metadata associated with the accepted GitHub profile link. Return the list for candidate review; do not retrieve source files at this stage.
3. Accept the candidate's explicit selection of zero or more returned repository identifiers. Store the selected scope and confirmation against the assessment.
4. Retrieve bounded files only from selected repositories and only after confirming the applicable analysis consent.

The discovery request must reference an application-recorded consent record, not trust a client-supplied `consent_confirmed` boolean. If discovery is declined, unavailable, or yields no selected repository, continue with an equivalent non-repository assessment.

### Project-grounded assessment tasks

After selected files are inspected, the assessment generator may create questions and bounded tasks such as explaining a file or data flow, proposing a code change, submitting a patch/diff, describing an implementation approach, comparing alternatives, and discussing architecture, testing, debugging, and trade-offs.

Each task must cite actual repository/file evidence or be clearly marked as general role-based. Candidate code changes are submitted as responses for review. The system does not modify the remote repository or execute candidate code.

## 10. Job Description Endpoints

### 10.1 Create job

`POST /api/v1/jobs`

Example request:

```json
{
  "title": "Junior Python Developer",
  "description": "Develop and maintain Python applications.",
  "required_skills": [
    {
      "name": "Python",
      "importance": 5
    },
    {
      "name": "SQL",
      "importance": 4
    },
    {
      "name": "Testing",
      "importance": 3
    }
  ]
}
```

`importance` is an example job-specific weighting scale from 1 to 5. The implementation must validate the allowed range and define how weights are normalized.

### Successful response

```json
{
  "job_id": "job_example_001",
  "status": "created"
}
```

### 10.2 Retrieve job

`GET /api/v1/jobs/{job_id}`

Returns the job description and its required skill criteria, subject to authorization.

The same job definition and scoring configuration should be used when comparing candidates for the same evaluation run.

## 11. Assessment Endpoints

### 11.1 Create assessment

`POST /api/v1/assessments`

Example request:

```json
{
  "candidate_id": "cand_example_001",
  "job_id": "job_example_001",
  "assessment_type": "technical",
  "skill_targets": [
    "Python",
    "SQL"
  ]
}
```

Example response — `201 Created`:

```json
{
  "assessment_id": "assess_example_001",
  "status": "created",
  "assessment_type": "technical"
}
```

The server must verify that the caller is authorized to create an assessment for the specified candidate.

### 11.2 Submit response

`POST /api/v1/assessments/{assessment_id}/responses`

Example request:

```json
{
  "question_id": "question_example_001",
  "response_text": "A Python dictionary stores key-value pairs.",
  "input_mode": "text"
}
```

Example response:

```json
{
  "assessment_id": "assess_example_001",
  "question_id": "question_example_001",
  "status": "submitted"
}
```

If audio is supported, transcription must be an optional input path with appropriate consent and a text alternative.

### 11.3 Retrieve assessment

`GET /api/v1/assessments/{assessment_id}`

Example response:

```json
{
  "assessment_id": "assess_example_001",
  "status": "completed",
  "results": [
    {
      "criterion": "python_fundamentals",
      "score": 3,
      "max_score": 4,
      "score_scale": "0-4",
      "evidence_ids": ["ev_example_003"],
      "explanation": "The response correctly identifies the key-value structure.",
      "limitations": []
    }
  ]
}
```

A result must not be marked `completed` until the configured evaluation process has finished successfully.

## 12. Skill Profile Generation

### Request

`POST /api/v1/profiles/generate`

Example request:

```json
{
  "candidate_id": "cand_example_001",
  "job_id": "job_example_001"
}
```

The service should collect authorized evidence and relevant assessment results, then generate a structured profile.

### Example response

```json
{
  "profile_id": "profile_example_001",
  "candidate_id": "cand_example_001",
  "job_id": "job_example_001",
  "status": "completed",
  "skills": [
    {
      "name": "Python",
      "performance_score": 80,
      "performance_score_scale": "0-100",
      "evidence_ids": ["ev_example_001", "ev_example_003"],
      "confidence": 0.82,
      "limitations": []
    },
    {
      "name": "SQL",
      "performance_score": null,
      "performance_score_scale": "0-100",
      "evidence_ids": [],
      "confidence": null,
      "limitations": [
        "Insufficient evidence to evaluate this skill."
      ]
    }
  ],
  "overall_limitations": [
    "Scores reflect the available evidence and configured assessment rubric."
  ]
}
```

Scores and confidence values above are illustrative only.

Rules:

- Do not assign a fabricated score to a skill with insufficient evidence.
- Define whether each score comes from an assessment rubric, verified observation, or another documented method.
- Preserve links to supporting evidence.
- Distinguish missing evidence from demonstrated lack of skill.
- Avoid combining incompatible score scales without a documented normalization method.

## 13. Recruiter Comparison

### Request

`POST /api/v1/comparisons`

Example request:

```json
{
  "job_id": "job_example_001",
  "candidate_ids": [
    "cand_example_001",
    "cand_example_002"
  ]
}
```

The caller must be authorized to access all candidate records included in the request.

### Example response

```json
{
  "job_id": "job_example_001",
  "status": "completed",
  "criteria": [
    "Python",
    "SQL",
    "Testing"
  ],
  "candidates": [
    {
      "candidate_id": "cand_example_001",
      "criterion_results": [
        {
          "criterion": "Python",
          "performance_score": 80,
          "performance_score_scale": "0-100",
          "evidence_ids": ["ev_example_001"]
        }
      ],
      "missing_evidence": [
        "SQL"
      ],
      "explanation": "Available evidence supports Python fundamentals; SQL evidence is insufficient."
    }
  ],
  "limitations": [
    "Comparisons reflect the configured job criteria and available evidence.",
    "The output is decision support, not an automatic hiring decision."
  ]
}
```

This example omits some fields for brevity. A real response should return consistent criterion results for every candidate.

### Comparison rules

- Compare candidates against the same job criteria and rubric.
- Do not silently change weights between candidates.
- Treat missing evidence explicitly.
- Do not use college name, gender, age, location, accent, or other irrelevant personal characteristics as scoring inputs.
- Keep ranking logic documented and testable.
- Show explanations and limitations alongside any aggregate score.
- Require human review for hiring decisions.

## 14. Error Handling

Errors should use a consistent JSON response format.

Example:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid fields.",
    "details": [
      {
        "field": "assessment_type",
        "issue": "Unsupported value."
      }
    ],
    "request_id": "req_example_001"
  }
}
```

`request_id` is an example correlation identifier. Do not expose stack traces, credentials, raw prompts, or sensitive candidate information in error responses.

### Recommended status codes

| Status | Meaning |
|---|---|
| `200 OK` | Request completed successfully |
| `201 Created` | Resource created |
| `202 Accepted` | Processing accepted but not yet complete |
| `400 Bad Request` | Malformed request |
| `401 Unauthorized` | Authentication is required or invalid |
| `403 Forbidden` | Caller lacks permission |
| `404 Not Found` | Resource does not exist or must not be disclosed |
| `409 Conflict` | Resource state conflicts with the request |
| `413 Content Too Large` | Upload exceeds configured limits |
| `415 Unsupported Media Type` | Unsupported file or content type |
| `422 Unprocessable Entity` | Request structure is valid but values fail validation |
| `429 Too Many Requests` | Rate limit exceeded |
| `500 Internal Server Error` | Unexpected server error |
| `502 Bad Gateway` | External provider returned an unusable response |
| `503 Service Unavailable` | Service or required dependency is unavailable |
| `504 Gateway Timeout` | Upstream operation timed out |

The implementation should use status codes consistently and avoid revealing whether a protected resource exists when that information itself is sensitive.

## 15. Authentication and Authorization

Production deployments must enforce authentication and resource-level authorization.

Requirements:

- Candidate users may access only their own records unless another explicitly authorized workflow applies.
- Recruiters may access only records permitted by the application's access policy.
- Every endpoint handling sensitive data must verify authorization server-side.
- Never trust a client-supplied candidate ID as proof of access.
- Protect credentials and tokens in transit and at rest.
- Apply rate limits to sensitive and expensive operations.
- Use least-privilege access for external integrations.

Authentication details depend on the final deployment environment. Local development may use a controlled demo mode, but demo mode must not be mistaken for production security.

## 16. Input Validation and File Safety

The API must:

- Validate required fields, lengths, types, enumerated values, and score ranges.
- Restrict uploaded file size and supported formats.
- Handle corrupt, encrypted, or unsupported documents safely.
- Treat document text and repository content as untrusted input.
- Protect against path traversal and unsafe file handling.
- Avoid executing uploaded files or candidate-submitted code.
- Apply timeouts and resource limits to expensive parsing and AI operations.
- Sanitize data displayed in the UI.
- Prevent prompt injection in evidence content from overriding trusted system instructions.

## 17. AI Provider and External Service Failures

When an AI provider or external integration fails:

1. Record a safe operational error without logging sensitive content.
2. Apply bounded retries only when appropriate.
3. Use a deterministic fallback if it can safely perform the requested task.
4. Return an explicit unavailable or failed status if no valid fallback exists.
5. Never represent a fallback result as a successful live-model evaluation.
6. Preserve completed records and avoid duplicate submissions when retrying requests.

External API credentials must be stored in environment variables or an approved secret-management service.

## 18. IMATS Sandbox Integration

The IMATS sandbox integration should be implemented behind a dedicated adapter.

Before integration, confirm:

- The official base URL.
- Authentication requirements.
- Supported endpoints and HTTP methods.
- Required request and response schemas.
- Rate limits and timeout requirements.
- Error formats and retry guidance.
- Data-sharing and consent requirements.

Do not invent endpoint paths, credentials, response schemas, or authentication behavior for the sandbox.

The adapter should validate external responses and translate them into internal application structures. External failures must not silently produce fabricated assessment results.

## 19. Idempotency and Duplicate Requests

For operations that create costly or sensitive resources, consider supporting an idempotency key.

When implemented:

- Scope keys to the authorized caller and operation.
- Store enough information to recognize a repeated request.
- Return the prior result for a valid retry where appropriate.
- Reject reuse of the same key with a materially different request.
- Define key expiration and retention.

Do not advertise idempotency support until it is implemented and tested.

## 20. Logging and Observability

Logs should support debugging without collecting unnecessary candidate data.

Recommended fields:

- Request ID.
- Timestamp.
- Endpoint or operation.
- Response status.
- Duration.
- Safe error code.
- External provider status where relevant.

Avoid logging:

- API keys and access tokens.
- Raw resumes or interview recordings.
- Private repository content.
- Full candidate responses unless specifically authorized and necessary.
- Sensitive personal attributes.
- Confidential prompts containing candidate data.

Use structured logs and apply appropriate access and retention controls.

## 21. Testing Requirements

Each implemented endpoint should have tests for:

- Successful requests.
- Missing and invalid fields.
- Invalid identifiers.
- Unauthorized access.
- Resource-level permission checks.
- Malformed or oversized uploads.
- External service failures.
- Invalid model output.
- Missing evidence.
- Duplicate requests where applicable.
- Safe error responses.
- Correct evidence references and score scales.

Integration tests should use mock providers or controlled fixtures when external services are unavailable.

See `docs/TESTING_AND_EVALUATION.md` for broader testing guidance.

## 22. Implementation Status and Contract Maintenance

This document describes the proposed API contract. It does not confirm that the listed endpoints exist or that authentication, idempotency, logging, or external integrations are implemented.

When an endpoint is implemented:

1. Confirm its actual route and method.
2. Validate request and response schemas.
3. Add success and failure tests.
4. Verify authorization and privacy controls.
5. Update this specification if implementation details differ.
6. Document breaking changes and compatibility requirements.

Keep `docs/API_CONTRACTS.md` aligned with this document so the API contract is not duplicated inconsistently.

## 23. Related Documentation

- `docs/API_CONTRACTS.md` — API contracts and integration details.
- `docs/ARCHITECTURE.md` — application components and boundaries.
- `docs/AI_MODELS.md` — model selection and integration strategy.
- `docs/AI_STRATEGY.md` — AI workflow and decision principles.
- `docs/DATA_MODEL.md` — application data entities.
- `docs/SCORING_AND_FAIRNESS.md` — scoring and fairness safeguards.
- `docs/PRIVACY_AND_SECURITY.md` — privacy requirements.
- `docs/SECURITY_PRIVACY.md` — security controls.
- `docs/TESTING_AND_EVALUATION.md` — testing and evaluation requirements.
