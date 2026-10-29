# Data Directory

## Purpose

The `data/` directory contains dataset documentation, dataset manifests, and approved data assets used by ProofSkill AI.

ProofSkill AI uses evidence-backed skill assessment to help candidates demonstrate their abilities through resumes, project evidence, technical assessments, and structured interviews. Data must be handled carefully to protect candidate privacy and reduce unfair or unsupported conclusions.

## Directory Guidelines

- `MANIFEST.yaml` is the source of truth for documenting dataset metadata, status, provenance, intended use, and validation requirements.
- Keep large datasets and private candidate records out of Git unless explicitly approved.
- Use synthetic or anonymized data for local development and demonstrations.
- Do not commit API keys, access tokens, private resumes, raw interview recordings, or personally identifiable information.
- Do not describe planned datasets as available until their files have been obtained, validated, and approved.
- Follow the project’s privacy, security, scoring, and evaluation documentation before using candidate data.

## Dataset Status

Dataset entries in `MANIFEST.yaml` should clearly distinguish between these states:

| Status | Meaning |
|---|---|
| `planned` | Intended for future use; files may not exist yet. |
| `synthetic` | Artificially generated data for development or demonstration. |
| `available` | Data exists and has passed the required validation checks. |
| `restricted` | Data exists but access or usage is limited. |
| `deprecated` | Data should no longer be used for new work. |

Only use a dataset for a workflow when its status and access conditions permit that use.

## Data Categories

ProofSkill AI may work with the following categories of data:

### 1. Candidate Profiles

Structured candidate information required for skill assessment, such as a pseudonymous candidate identifier and declared skills.

Use only fields necessary for the assessment. Avoid collecting demographic or personal details that are not required for the intended workflow.

### 2. Resume Evidence

Extracted skills, qualifications, experience, and project claims from candidate-provided resumes.

- Preserve the source document’s meaning.
- Distinguish extracted claims from independently verified evidence.
- Record extraction uncertainty where practical.
- Do not treat a resume claim as proof of practical competence by itself.

### 3. Project and Repository Evidence

Candidate-provided project descriptions, repository metadata, code samples, and relevant implementation evidence.

- Access private repositories only with explicit authorization.
- Do not expose repository secrets or unrelated personal information.
- Treat repository activity as supporting evidence, not a direct measure of candidate ability.
- Provide an alternative assessment path for candidates who do not have a public GitHub profile.

### 4. Assessment Results

Structured technical answers, coding task results, interview responses, and evaluator feedback.

- Evaluate responses against job-relevant rubrics.
- Keep evidence, rubric scores, and generated explanations distinguishable.
- Do not infer personality, honesty, or psychological traits from voice, accent, appearance, or speaking style.

### 5. Job Descriptions

Role requirements used to compare candidate evidence against a specific opportunity.

Job descriptions should identify relevant skills and their importance. Candidate comparisons should use the same job-specific criteria for the same role.

## Data Quality and Validation

Before using a dataset:

1. Confirm that the referenced file exists.
2. Verify that its provenance and permitted usage are documented.
3. Check required fields, data types, and unique identifiers.
4. Detect missing values, duplicate records, malformed entries, and inconsistent labels.
5. Check for accidental personal information and secrets.
6. Confirm that labels and assessment scores have documented meanings.
7. Record validation results and known limitations.
8. Ensure that the dataset is appropriate for its intended evaluation or demonstration.

Invalid or unverified data must not silently become trusted evidence.

## Synthetic and Official Data

Synthetic data may be used to demonstrate the application before an approved official dataset is available.

Synthetic records must be clearly identified as synthetic and must not be presented as real candidates, actual recruiter decisions, or measured model performance.

The hackathon problem statement describes anonymized fresher profiles, consented project evidence, assessments, recruiter decisions, and job descriptions. The availability of those official assets must be verified separately. Do not assume they are present in this repository.

## Privacy and Security

- Apply data minimization: collect and retain only what is necessary.
- Use pseudonymous identifiers where possible.
- Obtain appropriate consent before accessing candidate-controlled repositories or collecting assessment evidence.
- Restrict access to sensitive datasets.
- Avoid logging raw resumes, private source code, interview transcripts, credentials, or other sensitive information.
- Define retention and deletion practices before processing real candidate data.
- Do not upload confidential candidate data to external AI services unless the relevant permissions and data-handling requirements have been reviewed.
- Follow `docs/PRIVACY_AND_SECURITY.md`, `docs/SECURITY_PRIVACY.md`, and `SECURITY.md` for applicable project guidance.

## Adding a Dataset

When adding or updating a dataset:

1. Add or update its entry in `MANIFEST.yaml`.
2. Use a descriptive dataset identifier and an accurate status.
3. Document the source, intended purpose, permitted usage, and known limitations.
4. Record the expected schema and validation requirements.
5. Keep private or large files out of version control unless explicitly approved.
6. Validate the data before marking it as available.
7. Update the relevant evaluation or development documentation if the dataset changes the workflow.

A manifest entry documents a dataset; it does not establish that the referenced file exists or that access has been granted.

## Repository Safety

Never commit the following without explicit approval:

- Raw resumes or personally identifiable candidate records.
- Private interview recordings or transcripts.
- Private repository contents or access tokens.
- Production database exports.
- Secrets, credentials, or API keys.
- Restricted or licensed datasets that cannot be redistributed.

Use `.env.example` for documenting required environment variable names, and keep real values in a local environment configuration that is not committed.

## Related Documentation

- `data/MANIFEST.yaml` — dataset metadata and status.
- `docs/DATASETS.md` — dataset sources and usage.
- `docs/DATA_DICTIONARY.md` — field definitions.
- `docs/DATA_MODEL.md` — application data entities.
- `docs/SCORING_AND_FAIRNESS.md` — scoring principles and fairness safeguards.
- `docs/TESTING_AND_EVALUATION.md` — validation and evaluation guidance.
- `docs/PRIVACY_AND_SECURITY.md` — privacy and security guidance.
- `docs/SECURITY_PRIVACY.md` — additional security and privacy guidance.

If documentation conflicts, verify the current implementation and record the discrepancy rather than assuming that a planned feature or dataset is already available.
