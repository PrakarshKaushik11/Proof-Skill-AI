# Data Dictionary — ProofSkill AI

## 1. Purpose

This document defines the meaning, expected format, and usage of the principal data fields in ProofSkill AI.

The data dictionary supports consistent data processing across candidate profiles, resume extraction, project evidence, technical assessments, job descriptions, scoring, and recruiter comparisons.

**Status:** Proposed schema reference. Field names and types must be verified against the actual implementation before being treated as an authoritative database schema.

## 2. General Conventions

| Convention | Description |
|---|---|
| Identifiers | Use stable, unique, non-guessable identifiers. UUIDs are recommended. |
| Timestamps | Use ISO 8601 timestamps in UTC. |
| Text | Store UTF-8 text and validate length limits. |
| Scores | Always document the scale, rubric, and interpretation. |
| Missing values | Use `null` or an explicit missing-evidence status as appropriate. |
| Collections | Use arrays in JSON responses and suitable related tables in a relational database. |
| Provenance | Preserve the source of extracted claims and assessment results. |
| Sensitive data | Collect only what is necessary for the intended workflow. |

The examples in this document are illustrative and do not represent real candidates.

## 3. Candidate

Represents a person participating in a skill assessment.

| Field | Type | Required | Description |
|---|---|---|---|
| `candidate_id` | String / UUID | Yes | Unique candidate identifier. |
| `display_name` | String, nullable | No | Optional name shown in the interface. |
| `status` | Enum | Yes | Candidate record state, such as `active` or `archived`. |
| `created_at` | Datetime | Yes | Time the record was created. |
| `updated_at` | Datetime | Yes | Time the record was last updated. |

### Rules

- Use `candidate_id` for internal relationships instead of a person's name.
- Do not require a real name when a pseudonymous identifier is sufficient.
- Do not store unnecessary demographic or sensitive personal attributes.
- Apply access controls to every candidate record.

## 4. Job Description

Represents a role against which candidate evidence can be assessed.

| Field | Type | Required | Description |
|---|---|---|---|
| `job_id` | String / UUID | Yes | Unique job identifier. |
| `title` | String | Yes | Job title. |
| `description` | String | Yes | Role description and responsibilities. |
| `required_skills` | Array | Yes | Job-relevant skill criteria. |
| `created_at` | Datetime | Yes | Creation timestamp. |
| `updated_at` | Datetime | Yes | Last modification timestamp. |

### Required skill item

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | String | Yes | Skill or competency name. |
| `importance` | Number | Yes | Documented job-specific importance value. |
| `description` | String, nullable | No | Expected capability or criterion. |

If importance uses a bounded scale, validate its range and document how values are normalized. The same job and rubric configuration must be applied consistently when comparing candidates.

## 5. Evidence

Represents information used to support or evaluate a candidate skill.

| Field | Type | Required | Description |
|---|---|---|---|
| `evidence_id` | String / UUID | Yes | Unique evidence identifier. |
| `candidate_id` | String / UUID | Yes | Candidate associated with the evidence. |
| `source_type` | Enum | Yes | Origin of the evidence. |
| `title` | String, nullable | No | Short evidence title. |
| `content` | String, nullable | No | Relevant extracted text or description. |
| `source_reference` | String, nullable | No | Reference to the originating document section, artifact, or resource. |
| `verification_status` | Enum | Yes | Current evidence verification state. |
| `consent_reference` | String, nullable | No | Reference to applicable consent or authorization records. |
| `created_at` | Datetime | Yes | Creation timestamp. |

### Supported source types

Suggested values:

- `resume`
- `project_description`
- `repository`
- `technical_assessment`
- `interview_response`
- `uploaded_artifact`
- `manual_entry`

The implementation may support additional values. Unsupported values should be rejected or handled explicitly.

### Verification status

| Value | Meaning |
|---|---|
| `candidate_claim` | Information stated by the candidate but not independently verified. |
| `observed` | Evidence directly observed from an identified source. |
| `assessed` | Evidence evaluated using a documented assessment process. |
| `verified` | Evidence independently checked using an appropriate verification method. |
| `unverified` | Verification status is unknown or insufficient. |

A status must reflect the actual verification process. A model-generated summary is not independent verification.

A GitHub link extracted from a resume remains a `candidate_claim` until any permitted repository metadata or file content is retrieved through the consent and selection flow. Repository discovery consent does not establish a candidate's selection of a repository or authorship of its contents.

## 6. Extracted Skill

Represents a skill identified from candidate evidence.

| Field | Type | Required | Description |
|---|---|---|---|
| `skill_id` | String / UUID | Yes | Unique skill record identifier. |
| `candidate_id` | String / UUID | Yes | Associated candidate. |
| `name` | String | Yes | Normalized skill name. |
| `evidence_ids` | Array of identifiers | Yes | Evidence records supporting the skill mention. |
| `extraction_method` | Enum / String | Yes | Method used to identify the skill. |
| `confidence` | Number, nullable | No | Confidence in extraction or matching, where available. |
| `created_at` | Datetime | Yes | Creation timestamp. |

### Rules

- Skill extraction detects a mention; it does not establish competence.
- Confidence must have a documented interpretation and valid range.
- If confidence is expressed between 0 and 1, validate that range.
- Preserve the link between each extracted skill and its source evidence.
- Do not silently convert missing evidence into a negative skill judgment.

## 7. Assessment

Represents a structured evaluation assigned to a candidate.

| Field | Type | Required | Description |
|---|---|---|---|
| `assessment_id` | String / UUID | Yes | Unique assessment identifier. |
| `candidate_id` | String / UUID | Yes | Candidate taking the assessment. |
| `job_id` | String / UUID, nullable | No | Job associated with the assessment. |
| `assessment_type` | Enum | Yes | Assessment category. |
| `status` | Enum | Yes | Current processing or completion state. |
| `rubric_version` | String | Yes | Version of the scoring rubric. |
| `created_at` | Datetime | Yes | Assessment creation timestamp. |
| `completed_at` | Datetime, nullable | No | Completion timestamp. |

### Assessment types

Suggested values:

- `technical`
- `project_viva`
- `structured_interview`
- `coding`
- `manual_review`

### Assessment status

Suggested values:

- `created`
- `in_progress`
- `submitted`
- `processing`
- `completed`
- `failed`
- `cancelled`

The actual implementation must define permitted state transitions. A failed assessment must not be represented as successfully completed.

## 8. Assessment Question

Represents a question presented during an assessment.

| Field | Type | Required | Description |
|---|---|---|---|
| `question_id` | String / UUID | Yes | Unique question identifier. |
| `assessment_id` | String / UUID | Yes | Parent assessment. |
| `question_text` | String | Yes | Question shown to the candidate. |
| `target_skill` | String | Yes | Skill or competency being evaluated. |
| `difficulty` | Enum, nullable | No | Configured difficulty level. |
| `rubric_reference` | String | Yes | Reference to the expected evaluation criteria. |
| `generation_method` | Enum / String | Yes | How the question was generated or selected. |

Suggested difficulty values are `easy`, `medium`, and `hard`.

Generated questions should be validated for relevance, clarity, and answerability before use.

## 9. Assessment Response

Represents a candidate's response to an assessment question.

| Field | Type | Required | Description |
|---|---|---|---|
| `response_id` | String / UUID | Yes | Unique response identifier. |
| `assessment_id` | String / UUID | Yes | Associated assessment. |
| `question_id` | String / UUID | Yes | Question being answered. |
| `response_text` | String, nullable | Conditional | Text response, when applicable. |
| `input_mode` | Enum | Yes | Input method used. |
| `transcript_status` | Enum, nullable | No | Transcription state for audio input, if supported. |
| `submitted_at` | Datetime | Yes | Submission timestamp. |

Suggested input modes include `text`, `audio_transcription`, and `code`.

Audio must be optional, require appropriate consent, and have a text alternative. Voice characteristics and accent must not be used as proxies for technical competence.

## 10. Criterion Score

Represents the result of evaluating a candidate against one documented criterion.

| Field | Type | Required | Description |
|---|---|---|---|
| `score_id` | String / UUID | Yes | Unique score identifier. |
| `candidate_id` | String / UUID | Yes | Candidate being evaluated. |
| `job_id` | String / UUID, nullable | No | Job context, if applicable. |
| `assessment_id` | String / UUID, nullable | No | Assessment supporting the score. |
| `criterion` | String | Yes | Skill or criterion evaluated. |
| `score` | Number, nullable | Conditional | Raw answer/criterion score on the canonical 0–4 rubric. |
| `max_score` | Number | Yes | Maximum raw rubric score; 4 for this project. |
| `rubric_version` | String | Yes | Rubric used to calculate the score. |
| `evidence_ids` | Array of identifiers | Yes | Supporting evidence references. |
| `explanation` | String | Yes | Explanation of the score. |
| `limitations` | Array of strings | Yes | Known limitations or evidence gaps. |
| `created_at` | Datetime | Yes | Score creation timestamp. |

### Scoring rules

- A score must be within the documented scale.
- Raw answer and criterion scores use the 0–4 rubric; normalized skill performance uses a separate 0–100 field.
- A missing score must not be silently converted to zero.
- `null` may represent insufficient evidence or an unevaluated criterion.
- The meaning of a score must be consistent within the same rubric version.
- Every score should identify its supporting evidence where available.
- A score must not claim greater certainty than the evidence supports.

## 11. Skill Profile

Represents a consolidated, evidence-backed view of candidate skills.

| Field | Type | Required | Description |
|---|---|---|---|
| `profile_id` | String / UUID | Yes | Unique profile identifier. |
| `candidate_id` | String / UUID | Yes | Candidate associated with the profile. |
| `job_id` | String / UUID, nullable | No | Job context for a role-specific profile. |
| `status` | Enum | Yes | Profile generation state. |
| `skills` | Array | Yes | Skill-level results and evidence references. |
| `overall_limitations` | Array of strings | Yes | Profile-level caveats. |
| `created_at` | Datetime | Yes | Profile creation timestamp. |
| `updated_at` | Datetime | Yes | Last update timestamp. |

Each skill item may include:

- `name`
- `performance_score` on a 0–100 scale, or `null` when not assessed
- `evidence_ids`
- `confidence`
- `limitations`

A profile must distinguish candidate claims from assessed or independently verified capabilities. It should not present a missing skill record as proof that the candidate lacks the skill.

## 12. Candidate Comparison

Represents a comparison of candidates against one job description and one scoring configuration.

| Field | Type | Required | Description |
|---|---|---|---|
| `comparison_id` | String / UUID | Yes | Unique comparison identifier. |
| `job_id` | String / UUID | Yes | Job used for comparison. |
| `candidate_ids` | Array of identifiers | Yes | Candidates included in the comparison. |
| `rubric_version` | String | Yes | Scoring rubric used. |
| `status` | Enum | Yes | Comparison processing state. |
| `results` | Array | Yes | Criterion-level candidate results. |
| `limitations` | Array of strings | Yes | Comparison caveats. |
| `created_at` | Datetime | Yes | Comparison creation timestamp. |

Comparison results should use the same criteria and rubric for all candidates in a comparison run.

The comparison must disclose missing evidence and relevant limitations. It is decision support, not an automatic hiring decision.

## 13. Consent and Authorization

Consent and authorization records should be handled separately from ordinary candidate evidence when the implementation requires an auditable record.

Suggested fields:

| Field | Type | Description |
|---|---|---|
| `consent_id` | String / UUID | Unique consent record identifier. |
| `candidate_id` | String / UUID | Candidate associated with the record. |
| `purpose` | String / Enum | Specific data-processing purpose. |
| `status` | Enum | Consent state. |
| `recorded_at` | Datetime | Time consent was recorded. |
| `withdrawn_at` | Datetime, nullable | Time consent was withdrawn, if applicable. |
| `policy_version` | String, nullable | Version of the notice or policy presented. |

A consent record does not automatically grant access to every data source. Private repository access, external provider processing, and audio recording may require distinct permissions.

## 14. External Processing Job

Long-running tasks may use a job record if asynchronous processing is implemented.

| Field | Type | Required | Description |
|---|---|---|---|
| `job_id` | String / UUID | Yes | Unique processing job identifier. |
| `job_type` | Enum / String | Yes | Operation being performed. |
| `resource_id` | String / UUID | Yes | Resource associated with the operation. |
| `status` | Enum | Yes | Processing state. |
| `created_at` | Datetime | Yes | Creation timestamp. |
| `completed_at` | Datetime, nullable | No | Completion timestamp. |
| `error_code` | String, nullable | No | Safe machine-readable failure code. |

This processing-job entity is distinct from the job-description entity. The implementation should use unambiguous names if both exist in the same database.

## 15. Common Validation Rules

The application should enforce these rules consistently:

1. Required identifiers must be present and valid.
2. Foreign-key references must point to existing, authorized resources.
3. Timestamps must use the documented format.
4. Scores must respect their configured minimum and maximum values.
5. Confidence values must use a documented scale.
6. Enum fields must reject unsupported values.
7. Evidence references must resolve to records the caller is authorized to access.
8. Uploaded documents must pass file-type, size, and parsing checks.
9. Missing evidence must remain distinguishable from a negative assessment.
10. AI-generated content must be validated before it is stored as a structured result.
11. Sensitive personal data must not be collected unless necessary and appropriately authorized.
12. Errors must not expose credentials, private source content, or internal stack traces.

## 16. Data Minimization and Retention

- Store only the information necessary for the intended assessment.
- Use pseudonymous identifiers where practical.
- Avoid retaining raw documents or audio longer than required.
- Restrict access to candidate evidence and assessment results.
- Avoid logging raw resumes, private repository contents, recordings, or secrets.
- Define deletion and retention behavior before processing real candidate data.
- Keep synthetic demo data clearly labeled as synthetic.

## 17. Example Relationships

The logical relationships are:

- One candidate may have multiple evidence records.
- One candidate may have multiple assessments.
- One assessment may contain multiple questions and responses.
- One candidate may have multiple criterion scores.
- One candidate may have multiple skill profiles over time.
- One job description may be used in multiple candidate comparisons.
- One comparison may include multiple authorized candidates.

These are logical relationships; exact database cardinality and constraints must be confirmed in the implementation.

## 18. Related Documentation

- `data/MANIFEST.yaml` — dataset metadata and status.
- `data/README.md` — data directory and handling guidelines.
- `docs/DATA_MODEL.md` — entities and relationships.
- `docs/DATASETS.md` — dataset sources and usage.
- `docs/API_SPEC.md` — proposed API request and response formats.
- `docs/API_CONTRACTS.md` — API contracts and integration details.
- `docs/SCORING_AND_FAIRNESS.md` — scoring principles and fairness safeguards.
- `docs/PRIVACY_AND_SECURITY.md` — privacy requirements.
- `docs/TESTING_AND_EVALUATION.md` — testing and evaluation guidance.

## 19. Maintenance

Update this dictionary when data fields, enum values, validation rules, or relationships change.

Before treating a field as implemented, verify its actual presence in the application schema and confirm that the documented type, meaning, and validation rules match the code.
