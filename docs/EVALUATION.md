# Evaluation Plan — ProofSkill AI

## 1. Purpose

This document defines how ProofSkill AI should be evaluated for functional correctness, evidence quality, assessment reliability, recruiter usefulness, fairness, privacy, and operational performance.

ProofSkill AI aims to help freshers demonstrate practical skills through resume evidence, project work, technical assessments, and structured interviews. Its outputs should help recruiters understand candidate capabilities without replacing human judgment.

**Evaluation status:** This document defines the evaluation methodology. It does not claim that experiments have been completed or that any particular performance target has been achieved.

## 2. Evaluation Objectives

The evaluation process should answer these questions:

1. Does the application process candidate information correctly?
2. Are extracted skills linked to relevant source evidence?
3. Are technical assessments evaluated against documented rubrics?
4. Are skill profiles explainable and appropriately cautious when evidence is missing?
5. Are candidate comparisons consistent for the same job description?
6. Does AI-generated content remain grounded in the available evidence?
7. Are privacy, authorization, and failure-handling safeguards effective?
8. Does the system behave consistently across different input formats and candidate evidence paths?
9. Can the application be demonstrated reliably without depending entirely on external AI services?
10. What limitations must be resolved before any real-world use?

## 3. Evaluation Principles

- **Evidence first:** Every substantive skill conclusion should be traceable to relevant evidence or an assessment.
- **Reproducibility:** Record dataset versions, model configuration, rubric versions, and evaluation procedures.
- **Honest reporting:** Report actual measured results, not expected or invented performance.
- **Fair comparison:** Use the same job criteria and rubric for candidates in the same comparison.
- **Missing evidence:** Distinguish insufficient evidence from demonstrated lack of ability.
- **Human oversight:** Treat scores and rankings as decision-support signals, not automatic hiring decisions.
- **Privacy:** Use authorized data and minimize exposure of personal information.
- **Uncertainty:** Document limitations, sample sizes, and confidence intervals where appropriate.
- **No unsupported claims:** Synthetic demonstrations must not be presented as real-world validation.

## 4. Evaluation Stages

### Stage 1 — Functional correctness

Verify that implemented workflows accept valid inputs, reject invalid inputs, preserve evidence relationships, and handle expected errors.

### Stage 2 — Component quality

Evaluate resume extraction, skill matching, question generation, rubric-based answer evaluation, and evidence-grounded explanations separately.

### Stage 3 — End-to-end workflows

Test the complete candidate journey from evidence submission through assessment and profile generation, followed by recruiter comparison.

### Stage 4 — Fairness and safety

Check consistency across equivalent evidence, missing-data scenarios, privacy safeguards, and access-control boundaries.

### Stage 5 — Operational readiness

Measure response times, failure rates, dependency availability, and reproducibility under the expected demonstration workload.

## 5. Functional Evaluation

The following checks should be run against the actual implementation.

| Area | Evaluation check | Expected behavior |
|---|---|---|
| Resume ingestion | Valid PDF and DOCX files | Supported content is extracted without crashing. |
| Invalid documents | Corrupt, empty, or unsupported files | A clear validation error is returned. |
| Skill extraction | Known skill mentions | Extracted skills link to relevant source passages where possible. |
| Evidence provenance | Candidate claims and assessed evidence | Source and verification status remain distinguishable. |
| Missing evidence | A skill has no supporting evidence | The system reports insufficient evidence instead of inventing a score. |
| Assessment | Valid response and rubric | The response is evaluated against the configured criteria. |
| Profile generation | Evidence and assessment records are available | The profile preserves supporting evidence and limitations. |
| Candidate comparison | Multiple candidates and one job | The same criteria and rubric are applied consistently. |
| AI failure | Provider timeout or invalid output | The system reports failure or uses an approved fallback. |
| Privacy | Unauthorized access attempt | Sensitive records are not disclosed. |

A check should be marked passed only after it has been executed and its outcome recorded.

## 6. Resume and Skill Extraction

### 6.1 Objectives

Evaluate whether the system accurately extracts skill mentions and relevant resume information without confusing candidate claims with verified capabilities.

### 6.2 Metrics

When a labeled reference set is available, use:

- **Precision:** The proportion of extracted skill mentions that are correct.
- **Recall:** The proportion of reference skill mentions that are successfully extracted.
- **F1 score:** The harmonic mean of precision and recall.
- **Field-level accuracy:** Accuracy for structured fields such as project titles or qualification dates, where applicable.

For skill extraction:

\[
\text{Precision}=\frac{TP}{TP+FP}
\]

\[
\text{Recall}=\frac{TP}{TP+FN}
\]

\[
F1=2\cdot\frac{\text{Precision}\cdot\text{Recall}}{\text{Precision}+\text{Recall}}
\]

Here, \(TP\), \(FP\), and \(FN\) represent true positives, false positives, and false negatives.

If a denominator is zero, report the metric as undefined or follow a documented evaluation convention. Do not silently interpret undefined values as perfect performance.

### 6.3 Test cases

Include resumes with:

- Different document layouts.
- Skills listed in tables and bullet points.
- Synonyms and alternate technology names.
- Missing or incomplete sections.
- Repeated skill mentions.
- Unsupported or malformed documents.
- Text that mentions a skill without demonstrating its use.

Extraction metrics measure extraction quality, not actual candidate competence.

## 7. Semantic Skill Matching

### 7.1 Objectives

Evaluate whether candidate evidence is relevant to the requirements of a particular job.

### 7.2 Metrics

Where labeled relevance judgments are available, consider:

- Precision at \(k\) (P@k).
- Recall at \(k\) (R@k).
- Mean reciprocal rank (MRR).
- Normalized discounted cumulative gain (NDCG).
- Human-reviewed relevance and evidence-grounding rates.

Use these metrics to evaluate retrieval and ordering of relevant evidence, not as direct measures of candidate ability.

### 7.3 Validation checks

- Relevant evidence should be retrievable even when wording differs.
- Irrelevant evidence should not be presented as strong support.
- Missing evidence should remain visible.
- Similarity scores must have a documented interpretation.
- Changes in job requirements should affect matching in an explainable way.
- The same inputs and configuration should produce reproducible results where deterministic behavior is expected.

Semantic similarity alone does not establish that a candidate possesses a skill.

## 8. Technical Assessment Quality

### 8.1 Rubric-based evaluation

Technical answers should be scored against explicit, job-relevant rubrics.

Possible dimensions include:

- Technical correctness.
- Reasoning and problem-solving.
- Appropriate use of concepts.
- Handling of edge cases.
- Explanation of relevant trade-offs.

Only include dimensions that are appropriate for the question and role.

### 8.2 Reference evaluation

Where practical, have qualified human reviewers score a representative sample using the same rubric.

Compare automated scores with human-reviewed reference scores using:

- Mean absolute error (MAE).
- Root mean squared error (RMSE), where appropriate.
- Weighted kappa or another suitable agreement statistic for ordinal ratings.
- Exact agreement and agreement within one rubric level.

Human review is itself subject to disagreement. Document the rubric, reviewer instructions, disagreement resolution procedure, and reference-label limitations.

### 8.3 Content safeguards

Check that the evaluation:

- Does not reward verbosity over correctness without justification.
- Does not penalize accent or speaking style.
- Does not invent missing details in an answer.
- Explains scores using the response and rubric.
- Distinguishes unanswered questions from incorrect answers.
- Does not treat a transcription error as a technical error without review.

## 9. Interview Question Generation

Generated questions should be evaluated for:

- Job relevance.
- Alignment with the target skill.
- Technical correctness.
- Clarity and answerability.
- Appropriate difficulty.
- Duplication and redundancy.
- Unsupported assumptions about the candidate.
- Privacy and safety.

Use human review and a documented checklist for representative samples.

For adaptive interviews, verify that follow-up questions respond to the candidate's previous answer and do not merely repeat an earlier question.

Do not claim question quality based only on the number of questions generated.

## 10. Evidence-Grounded Explanations

A profile or recruiter explanation should accurately represent the available evidence.

Evaluate:

- **Evidence support:** Are factual claims supported by the referenced source?
- **Citation correctness:** Do evidence references point to the intended records?
- **Completeness:** Are important limitations and missing evidence disclosed?
- **Calibration:** Does the explanation avoid overstating certainty?
- **Clarity:** Can a recruiter understand why a criterion received its score?
- **Consistency:** Does the explanation agree with the stored score and rubric?

Unsupported claims about qualifications, projects, repository activity, or assessment performance should be treated as defects.

If automated factuality scoring is used, supplement it with human review rather than treating the automated metric as definitive.

## 11. Recruiter Comparison and Ranking

Candidate comparison should be evaluated against a single job description and a fixed scoring configuration.

### Checks

- Every candidate is evaluated using the same criteria.
- Rubric versions and weights are consistent within the comparison.
- Missing evidence is disclosed.
- Scores remain within their configured scales.
- Explanations agree with criterion-level results.
- Irrelevant personal attributes do not affect scoring.
- Small changes in irrelevant formatting do not cause unexplained ranking changes.
- The system does not imply that a rank guarantees future job performance.

### Ranking metrics

If suitable, authorized reference judgments exist, use metrics such as NDCG, MRR, or pairwise ranking agreement.

Historical recruiter decisions should not automatically be treated as objective ground truth. They may reflect inconsistent preferences or historical bias.

Ranking quality must be evaluated separately from assessment accuracy and fairness.

## 12. Fairness Evaluation

Fairness evaluation must be appropriate to the available data, lawful, and supported by adequate sample sizes.

### 12.1 Consistency tests

Create controlled examples in which job-relevant evidence remains the same while irrelevant wording or formatting changes.

Check whether the resulting:

- Extracted skills.
- Criterion scores.
- Evidence explanations.
- Candidate comparisons.

remain materially consistent.

### 12.2 Group-based analysis

If lawful and appropriate evaluation data is available, compare relevant error rates and outcome distributions across groups.

Potential analyses include:

- False-positive and false-negative rates.
- Assessment score distributions.
- Ranking outcomes.
- Missing-evidence rates.
- Performance of alternative assessment paths.

Document group sizes, uncertainty, data limitations, and metric definitions. Do not infer sensitive attributes from names, voice, or other indirect signals to conduct these analyses.

### 12.3 Fairness safeguards

- Exclude college name, gender, age, location, and other irrelevant personal characteristics from skill scoring.
- Do not infer personality, honesty, or competence from accent, appearance, or vocal characteristics.
- Offer alternatives to public repository evidence.
- Distinguish missing evidence from poor performance.
- Keep the evaluation rubric consistent for candidates applying to the same role.

Fairness cannot be established solely by removing sensitive fields or passing a small set of examples.

## 13. Privacy and Security Evaluation

Test that:

- Unauthorized users cannot access protected candidate records.
- Private repository data requires appropriate authorization.
- Upload validation rejects unsupported or malformed inputs.
- Logs do not expose credentials or unnecessary personal information.
- External AI requests follow documented data-handling requirements.
- Candidate-submitted content cannot override trusted application instructions.
- Errors do not reveal internal stack traces or secrets.
- Retention and deletion behavior follows the documented policy.
- Synthetic demo data is clearly identified.

Any unresolved critical privacy or security issue should block use with real candidate data until it is addressed.

## 14. Operational Evaluation

Measure operational performance under a documented test environment.

| Metric | Definition |
|---|---|
| End-to-end latency | Time from request initiation to completed result. |
| p50 latency | Median response time. |
| p95 latency | Response time at the 95th percentile. |
| Error rate | Proportion of requests that fail. |
| Provider failure rate | Proportion of external AI or integration calls that fail. |
| Fallback rate | Proportion of requests using fallback behavior. |
| Cost per evaluation | Estimated service cost per completed assessment, where applicable. |
| Reproducibility | Consistency of results under the same inputs and configuration. |

Record hardware, software versions, model identifiers, network conditions, and test volume when reporting performance.

Do not report latency or cost estimates as measured results unless they were measured.

## 15. Dataset and Experimental Design

Before model evaluation:

1. Confirm dataset provenance and permission.
2. Inspect the actual schema and label definitions.
3. Remove or account for duplicates.
4. Document preprocessing and exclusions.
5. Establish training, validation, and test splits where model training or tuning is involved.
6. Prevent candidate-level or source-level leakage where relevant.
7. Keep a designated held-out set separate from model selection.
8. Record model versions, prompt versions, rubric versions, and configuration.
9. Save evaluation outputs with suitable privacy protections.
10. Document limitations and reproducibility details.

If the hackathon supplies a designated held-out dataset, follow its instructions and do not use it for tuning.

See `docs/DATASETS.md` and `docs/TESTING_AND_EVALUATION.md` for related requirements.

## 16. Demo Evaluation

A hackathon demonstration should show an end-to-end workflow using clearly labeled synthetic or otherwise authorized data.

Recommended demo checklist:

- [ ] A candidate can submit or enter evidence.
- [ ] The application extracts or records relevant skill evidence.
- [ ] Evidence sources are visible.
- [ ] A technical assessment can be completed or demonstrated.
- [ ] Scores use a documented rubric.
- [ ] Missing evidence is represented honestly.
- [ ] A skill profile includes explanations and limitations.
- [ ] A recruiter can compare candidates against the same job criteria.
- [ ] AI provider failures are handled safely.
- [ ] Demo outputs are distinguishable from live model results.
- [ ] No real candidate information or secrets are exposed.

Mark each item complete only after the corresponding behavior has been demonstrated.

## 17. Acceptance Criteria

Before a feature is considered ready for demonstration, verify that:

- Its main workflow works with valid inputs.
- Invalid inputs produce understandable errors.
- Scores respect the configured rubric.
- Evidence references resolve correctly.
- Missing evidence is not fabricated.
- Candidate comparisons use consistent criteria.
- External dependency failures do not silently produce false results.
- Relevant tests pass.
- Known limitations are documented.

Before use in a real hiring workflow, additional validation, privacy review, fairness assessment, access controls, and human oversight are required.

Passing demo acceptance criteria does not establish production readiness.

## 18. Results Reporting Template

Use this template when recording an actual evaluation run:

| Field | Value |
|---|---|
| Evaluation date | Record actual date |
| Dataset and version | Record actual dataset |
| Dataset type | Synthetic / authorized real data |
| Number of records | Record actual count |
| Model and version | Record actual configuration |
| Prompt version | Record version if applicable |
| Rubric version | Record actual version |
| Evaluation method | Describe procedure |
| Metrics | Report measured values |
| Test failures | Record actual failures |
| Limitations | Document known limitations |
| Reviewer | Record authorized reviewer or team |
| Status | Pass / Fail / Inconclusive |

Do not fill this template with assumed performance figures.

## 19. Related Documentation

- `docs/AI_MODELS.md` — AI model choices and integration strategy.
- `docs/AI_STRATEGY.md` — AI workflow and safeguards.
- `docs/DATASETS.md` — dataset provenance and usage.
- `docs/DATA_DICTIONARY.md` — field definitions.
- `docs/DATA_MODEL.md` — data entities and relationships.
- `docs/SCORING_AND_FAIRNESS.md` — scoring and fairness rules.
- `docs/TESTING_AND_EVALUATION.md` — test strategy and validation.
- `docs/PRIVACY_AND_SECURITY.md` — privacy requirements.
- `docs/ARCHITECTURE.md` — system architecture.

## 20. Maintenance

Update this document when evaluation metrics, datasets, model versions, scoring rubrics, or acceptance criteria change.

Record actual findings and unresolved limitations. Do not describe a feature as accurate, fair, reliable, or production-ready without appropriate supporting evidence.
