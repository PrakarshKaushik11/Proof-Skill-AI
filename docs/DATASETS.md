# Datasets — ProofSkill AI

## 1. Purpose

This document describes the datasets required, permitted, or proposed for ProofSkill AI.

ProofSkill AI uses candidate-provided information, project evidence, technical assessments, and job descriptions to create evidence-backed skill profiles and support recruiter comparisons.

Dataset availability, provenance, permitted usage, and limitations must be documented before data is used. A dataset mentioned in the hackathon problem statement is not automatically available in this repository.

## 2. Dataset Principles

All datasets used by ProofSkill AI should follow these principles:

- **Provenance:** Record where the data came from and who is responsible for providing it.
- **Permission:** Confirm that the data may be used for the intended purpose.
- **Privacy:** Minimize personal information and protect confidential records.
- **Transparency:** Document schemas, labels, missing values, and known limitations.
- **Reproducibility:** Version datasets and processing configurations where practical.
- **Fairness:** Avoid irrelevant personal attributes as skill-scoring inputs.
- **Integrity:** Do not silently fabricate, alter, or misrepresent evidence.
- **Separation:** Clearly distinguish synthetic examples from real candidate records.

## 3. Dataset Availability

The hackathon problem statement describes a dataset involving anonymized fresher profiles, consented repositories and assessments, recruiter decisions, and job descriptions. The actual dataset files and access permissions must be confirmed independently.

Until they are obtained and validated, treat the official dataset as **unconfirmed**.

Do not report model accuracy, hiring prediction performance, or fairness results based on official data unless the data has actually been accessed and the evaluation has been performed.

## 4. Dataset Categories

### 4.1 Official Hackathon Dataset

**Status:** Availability unconfirmed.

The intended dataset may include:

- Anonymized fresher candidate profiles.
- Candidate-provided or consented project and repository evidence.
- Technical assessment results.
- Historical recruiter decisions.
- Job descriptions and job requirements.
- Relationships between candidates, assessments, roles, and outcomes.

The actual fields, record counts, label definitions, licensing, and permitted uses must be verified against the supplied dataset documentation.

#### Intended use

If authorized and available, the dataset may support:

- Understanding the available data schema.
- Evaluating resume and skill extraction.
- Testing evidence-backed profile generation.
- Evaluating job-requirement matching.
- Comparing model-assisted assessment results with suitable reference labels.
- Measuring ranking quality and relevant fairness indicators.

#### Restrictions

- Do not infer missing schema fields or labels.
- Do not assume recruiter decisions are objective ground truth.
- Do not use historical hiring outcomes as unquestionable measures of candidate ability.
- Do not expose identifiable candidate records.
- Do not redistribute restricted data.
- Follow the dataset's actual license, consent terms, and access conditions.

### 4.2 Synthetic Demo Dataset

**Status:** Permitted as a development approach; actual files must be verified.

Synthetic data consists of artificially generated candidates, job descriptions, evidence records, and assessment responses used to demonstrate application workflows.

Synthetic data may support:

- Candidate profile demonstrations.
- Evidence and scoring interface development.
- Recruiter comparison workflows.
- API and schema testing.
- Error handling and missing-evidence scenarios.
- Deterministic demonstrations without external services.

Synthetic records must be clearly labeled as synthetic.

They must not be presented as real candidates, real recruiter decisions, official hackathon data, or evidence of real-world model performance.

If a synthetic dataset is not yet present in the repository, its planned status should be recorded in `data/MANIFEST.yaml` rather than claiming that the files already exist.

### 4.3 Candidate-Provided Resumes

**Status:** Use only with appropriate permission.

Resumes may be supplied as PDF or DOCX documents, subject to the application's supported formats.

Potential uses include:

- Extracting declared skills.
- Identifying project and experience descriptions.
- Finding evidence passages relevant to a job requirement.

Limitations:

- Resume claims are not independently verified merely because they were extracted.
- Document formatting can affect extraction quality.
- Missing information does not establish that a candidate lacks a skill.
- Personal information should be minimized and protected.

### 4.4 Project and Repository Evidence

**Status:** Use only within the scope authorized by the candidate.

Potential evidence includes project descriptions, source code, repository metadata, documentation, and candidate-selected artifacts.

Repository activity, commit counts, project popularity, and public visibility must not be treated as direct measures of competence.

Candidates without public repositories must have an alternative path through structured assessments, manual project descriptions, or other relevant evidence.

### 4.5 Technical Assessment Data

Assessment data may contain questions, candidate responses, rubric scores, evaluator feedback, and completion status.

Requirements:

- Use documented, job-relevant rubrics.
- Preserve the relationship between a response and its evaluation criteria.
- Distinguish automated evaluations from human-reviewed results.
- Document scoring scales and missing-value semantics.
- Avoid collecting unnecessary sensitive information.
- Provide an appropriate text-based alternative if audio responses are supported.

### 4.6 Job Description Data

Job descriptions define the requirements used to assess candidate evidence.

A job record may include:

- Job title.
- Role description.
- Required skills.
- Skill importance or weighting.
- Assessment criteria.
- Rubric version.

Job requirements and scoring weights should be fixed for a comparison run so that candidates for the same role are evaluated consistently.

## 5. Data Manifest

`data/MANIFEST.yaml` is the central inventory for dataset metadata.

Each entry should document, where applicable:

- Dataset identifier.
- Human-readable name.
- Current status.
- Source or provenance.
- Intended purpose.
- Data format.
- Expected schema.
- Validation requirements.
- Privacy or access restrictions.
- Known limitations.
- File location, if a file actually exists.

The manifest documents dataset status; it does not establish that a referenced file exists, has been validated, or is authorized for use.

Keep manifest entries consistent with the actual repository contents.

## 6. Dataset Status Definitions

Use these status values consistently:

| Status | Meaning |
|---|---|
| `planned` | Intended for future use; files may not exist yet. |
| `synthetic` | Artificially generated data for development or demonstration. |
| `available` | Data exists and has passed the required validation checks. |
| `restricted` | Data exists but access or usage is limited. |
| `deprecated` | Data should no longer be used for new work. |

Do not mark a dataset `available` merely because its name or path appears in a manifest.

## 7. Expected Data Quality Checks

Before using a dataset, perform the checks relevant to its intended purpose.

### Structural validation

- Confirm that referenced files exist.
- Validate file formats and encoding.
- Check required columns and field types.
- Identify duplicate identifiers and broken relationships.
- Validate timestamps, enumerated values, and score ranges.

### Content validation

- Identify missing and malformed records.
- Check for inconsistent skill names and labels.
- Verify that score definitions and rubric versions are documented.
- Inspect whether evidence references point to valid records.
- Identify accidental secrets or personal information.

### Provenance validation

- Confirm the source and permission status.
- Verify the intended use and any restrictions.
- Distinguish candidate claims from assessed or verified evidence.
- Record transformations applied during preprocessing.

Validation results should be documented before the dataset is used for substantive evaluation.

## 8. Data Splitting and Leakage Prevention

If labeled data becomes available for model evaluation, define train, validation, and test partitions before tuning the model.

Recommended safeguards:

- Keep the final test set separate from model selection and tuning.
- Avoid placing records from the same candidate across partitions when that could leak candidate-specific information.
- Consider grouping by job, time period, or other relevant source when evaluating generalization.
- Remove duplicate or near-duplicate examples across partitions where practical.
- Fit preprocessing steps only on the appropriate training data.
- Record split rules, random seeds where applicable, and dataset versions.

If the official problem statement provides a designated held-out set, follow its instructions and do not use that set for model tuning.

## 9. Fairness and Label Limitations

Historical recruiter decisions may reflect past preferences, inconsistent evaluation practices, or structural biases. They should not automatically be treated as objective labels of candidate competence.

Evaluation should distinguish between:

- Skill-assessment quality.
- Job-requirement matching quality.
- Agreement with historical recruiter decisions.
- Ranking quality.
- Fairness across relevant groups, where lawful and appropriate to evaluate.

Do not use college name, gender, age, location, accent, or other irrelevant personal characteristics as proxies for skill.

Any fairness evaluation must document the available data, sample limitations, metric definitions, and uncertainty. Do not claim that a system is unbiased solely because sensitive attributes were omitted from its input fields.

## 10. Privacy, Security, and Retention

- Use anonymized or pseudonymous data where practical.
- Collect only the fields necessary for the intended workflow.
- Obtain appropriate authorization before accessing private repositories.
- Do not commit raw resumes, private repository contents, recordings, or restricted datasets.
- Avoid logging sensitive source data.
- Review external AI provider data-handling terms before transmitting candidate information.
- Define retention and deletion rules before processing real candidate data.
- Restrict access according to the sensitivity of each dataset.

See `docs/PRIVACY_AND_SECURITY.md`, `docs/SECURITY_PRIVACY.md`, and `SECURITY.md` for related requirements.

## 11. Recommended Dataset Workflow

1. Identify the intended use of the dataset.
2. Confirm the source, permission, and restrictions.
3. Record the dataset in `data/MANIFEST.yaml`.
4. Verify that the referenced files exist.
5. Validate structure, content, and provenance.
6. Document preprocessing and known limitations.
7. Create leakage-resistant evaluation partitions when applicable.
8. Run the relevant tests and evaluation procedures.
9. Record actual results without overstating their significance.
10. Update the manifest and documentation when the dataset changes.

## 12. Reporting Results

Every dataset-based evaluation report should identify:

- Dataset name and version.
- Dataset status and provenance.
- Number of records actually used.
- Exclusions and preprocessing steps.
- Evaluation method and metrics.
- Important limitations.
- Whether results came from synthetic or real data.
- Whether any external services or AI models were used.

Never report results from synthetic demo records as measured performance on real candidates.

## 13. Repository References

- `data/MANIFEST.yaml` — dataset inventory and status.
- `data/README.md` — data directory guidelines.
- `docs/DATA_DICTIONARY.md` — field definitions and validation conventions.
- `docs/DATA_MODEL.md` — entities and relationships.
- `docs/SCORING_AND_FAIRNESS.md` — scoring and fairness safeguards.
- `docs/AI_MODELS.md` — model choices and evaluation strategy.
- `docs/EVALUATION.md` — evaluation methodology.
- `docs/TESTING_AND_EVALUATION.md` — testing and validation guidance.
- `docs/PRIVACY_AND_SECURITY.md` — privacy requirements.

## 14. Maintenance

Update this document whenever dataset availability, provenance, licensing, schema, preprocessing, or evaluation use changes.

Before marking a dataset as available or approved, verify the actual files, permissions, validation results, and intended use. Document unresolved issues instead of assuming that missing information is correct.
