# ProofSkill AI — Scoring and Evaluation Framework

**Status:** Proposed  
**Version:** 1.0  
**Applies to:** Candidate assessment, Proof Cards, recruiter comparison

---

## 1. Purpose

ProofSkill AI evaluates how well a candidate demonstrates skills required by a particular job.

The system must distinguish demonstrated ability from the amount and reliability of available evidence. It must not treat a resume keyword, repository link, AI-generated statement, or missing information as conclusive proof of competence.

The framework is designed to provide:

- Job-specific skill assessment.
- Evidence-backed evaluation.
- Consistent interview scoring.
- Explainable candidate comparison.
- Fair treatment of candidates with different backgrounds and portfolios.
- Clear uncertainty and limitations.

Scores are decision-support information, not automatic hiring decisions.

## 2. Scoring Principles

1. Use the same rubric for candidates being compared for the same job.
2. Evaluate skills against explicit job requirements.
3. Link skill claims to identifiable evidence.
4. Separate performance from evidence coverage and confidence.
5. Treat unassessed skills as unknown, not automatically as failed.
6. Never use college name, gender, age, or location as ranking features.
7. Do not penalize candidates solely for lacking GitHub or public projects.
8. Do not infer technical competence from accent, appearance, or vocal characteristics.
9. Keep AI-generated evaluations explainable and reviewable.
10. Record the rubric version used for each assessment.

---

## 3. Assessment Dimensions

### 3.1 Skill Performance

Measures how well the candidate demonstrates a required skill through relevant answers, exercises, project explanations, or other valid evidence.

Score range: `0–100`.

### 3.2 Evidence Coverage

Measures how much of the job's required skill set has been meaningfully assessed.

\[
\text{Coverage} =
100 \times
\frac{\sum_i w_i a_i}{\sum_i w_i}
\]

Where:

- \(w_i\) is the importance weight of required skill \(i\).
- \(a_i = 1\) when the skill has sufficient assessment evidence and \(0\) otherwise.

Coverage indicates how much has been assessed, not how good the candidate is.

### 3.3 Evidence Confidence

Describes how strongly the available sources support a particular assessment.

Suggested labels:

- **High:** Direct, relevant evidence with sufficient detail and corroboration where appropriate.
- **Medium:** Relevant evidence exists, but its depth, specificity, or corroboration is limited.
- **Low:** Evidence is indirect, ambiguous, incomplete, or primarily self-reported.
- **Not assessed:** No meaningful evidence is available.

Confidence is a qualitative evidence assessment. It must not be presented as a statistically calibrated probability unless calibration has actually been measured.

### 3.4 Communication Assessment

Measures how clearly the candidate explains relevant technical concepts, decisions, trade-offs, and limitations.

Communication is evaluated through an explicit rubric. Accent, native language, speech speed, and vocal style must not be treated as indicators of technical ability.

Communication should be weighted according to the job's actual requirements.

---

## 4. Evidence Types

| Evidence type | What it can support | Important limitation |
|---|---|---|
| Resume | Claimed experience, skills, projects | Self-reported; keywords alone are weak evidence |
| Technical interview | Understanding and reasoning | Depends on question quality and assessment conditions |
| Coding exercise | Performance on a defined task | Represents performance on that task, not all coding ability |
| Repository inspection | Visible code, project structure, implementation details | Does not independently prove authorship |
| Project viva | Candidate's explanation of design and trade-offs | Must use consistent questions and rubric |
| Alternative assessment | Demonstrated skills without a public repository | Must use comparable requirements and scoring |
| Certifications | Completion of a course or credential | Does not independently prove practical competence |

Every evidence item should record its source, timestamp where appropriate, related skill, and assessment context.

---

## 5. Interview Evaluation Rubric

Use the following base rubric for each scored answer. This 0–4 rubric is the canonical raw answer scale for ProofSkill AI.

| Score | Level | Description |
|---:|---|---|
| 0 | No usable evidence | No relevant answer or fundamentally incorrect reasoning, when the response is assessable |
| 1 | Beginning | Limited understanding with major gaps |
| 2 | Developing | Partial understanding with important omissions |
| 3 | Competent | Correct answer with sound reasoning |
| 4 | Strong | Relevant depth, trade-offs, or edge cases |

A score of zero should mean that the response provided no usable evidence under the assessment conditions. It must not automatically mean that the candidate lacks the skill.

If an answer cannot be evaluated fairly because of a system error, ambiguous question, or inaccessible accommodation, mark it **not assessed** instead of assigning zero.

### Answer-level score

\[
S_{\text{answer}} = 25 \times r
\]

Where \(r\) is the selected rubric score from 0 to 4. The normalized answer performance score is 0–100; retain the raw 0–4 rubric score and rubric version for traceability.

When an answer has multiple weighted criteria, normalize each criterion by its own maximum, calculate the weighted mean, then multiply by 100 to obtain the 0–100 answer performance score. Do not assign a score to an unevaluable criterion.

### Multiple answers for one skill

Use the weighted mean of valid, assessable answers:

\[
S_{\text{skill}} =
\frac{\sum_j q_j s_j}{\sum_j q_j}
\]

Where:

- \(s_j\) is the percentage score for answer \(j\).
- \(q_j\) is the predefined importance weight of that question.

Do not change question weights after observing a candidate's results.

---

## 6. Job-Specific Skill Weights

Each job description should define required skills and their relative importance.

Example for a hypothetical junior Python developer role:

| Skill | Weight |
|---|---:|
| Python fundamentals | 30% |
| Problem solving | 25% |
| Data structures | 20% |
| SQL and data handling | 15% |
| Project explanation | 10% |
| **Total** | **100%** |

These values are illustrative. Actual weights should be derived from the job requirements and reviewed by a human.

Weights must be normalized so their total is 100%.

The system should flag missing or invalid weights rather than silently inventing them.

---

## 7. Overall Performance Score

When all required skills have valid assessments, calculate a weighted performance score:

\[
S_{\text{performance}} =
\frac{\sum_i w_i s_i}{\sum_i w_i}
\]

Where:

- \(w_i\) is the weight of skill \(i\).
- \(s_i\) is the assessed skill score on a 0–100 scale.

When a required skill has not been assessed, do not silently treat it as zero. Report the assessed score alongside coverage and mark the missing skills.

If a partial score is calculated using only assessed skills, label it **provisional performance score** and display the coverage percentage prominently. Do not compare candidates as though their scores have identical coverage when they do not.

---

## 8. Proof Card Metrics

Each Proof Card should show separate fields for:

- Overall performance score, if sufficiently assessed.
- Provisional score, when only part of the skill set has been assessed.
- Evidence coverage.
- Evidence confidence by skill.
- Demonstrated strengths.
- Skills requiring further assessment.
- Evidence sources.
- Interview assessment summary.
- Repository findings, if consented and available.
- Known limitations.
- Assessment rubric version.

Example:

```text
Candidate: Demo Candidate 001
Role: Junior Python Developer

Performance score: 78/100 (provisional)
Evidence coverage: 80%
Evidence confidence: Medium

Demonstrated strengths:
- Python fundamentals
- Explaining project design decisions

Needs further assessment:
- SQL query optimization

Sources:
- Technical interview
- Submitted project description

Limitations:
- No repository was assessed.
- One required skill remains unassessed.
```

All values in this example are illustrative, not actual assessment results.

---

## 9. Recruiter Ranking

Recruiter ranking must be job-specific and based on the same scoring rubric for all candidates in the comparison.

The initial implementation should:

1. Validate that all candidates are evaluated against the same job requirements.
2. Calculate skill performance using fixed job-specific weights.
3. Display evidence coverage and confidence separately.
4. Flag incomplete assessments.
5. Show the main evidence supporting each score.
6. Allow recruiters to inspect individual skill results.
7. Preserve a human decision-making step.

### Ranking safeguards

- Exclude college name, gender, age, and location from scoring inputs.
- Do not infer ability from a candidate's name or demographic background.
- Do not award extra points merely for having a public GitHub account.
- Do not interpret missing data as negative evidence.
- Do not hide incomplete assessments behind a single aggregate score.
- Do not present ranking order as a guarantee of job performance.

When evidence coverage differs substantially between candidates, flag the comparison as incomplete and recommend additional assessment before making a strong ranking claim.

---

## 10. Fairness and Bias Testing

The implementation should include tests to verify that excluded fields cannot affect scores or rankings.

### Required tests

- Changing a candidate's college name does not change their score.
- Changing an excluded demographic field does not change their ranking.
- Removing an optional GitHub URL does not automatically reduce the candidate's skill score.
- Candidates without a public repository can complete an alternative assessment.
- Missing evidence is represented explicitly.
- Equivalent evidence is evaluated using the same rubric.
- AI prompts do not instruct the model to consider protected or irrelevant personal attributes.

Where lawful, authorized, and appropriate evaluation data is available, conduct additional fairness analysis. Document data limitations and avoid claiming that the system is bias-free based only on software tests.

---

## 11. AI Evaluation Requirements

AI-assisted scoring must follow these rules:

- Use a defined rubric and structured output schema.
- Ask the model to cite the specific answer or evidence it evaluated.
- Reject malformed or incomplete outputs.
- Avoid allowing resume instructions or repository content to override system rules.
- Store the model and rubric version when available.
- Make fallback and simulated results clearly identifiable.
- Test repeated evaluations for consistency.
- Support human review and correction.

The AI should assess the substance of the response, not whether the candidate agrees with a preferred opinion.

The system must not fabricate evidence, invent project details, or claim to have executed code that it did not execute.

---

## 12. Recommended Evaluation Record

An evaluation record should contain fields similar to these:

```json
{
  "assessment_id": "demo-assessment-001",
  "skill": "Python fundamentals",
  "rubric_version": "1.0",
  "performance_score": 80,
  "evidence_coverage": 100,
  "evidence_confidence": "medium",
  "evidence_references": [
    "answer-001"
  ],
  "explanation": "The answer correctly explains the core concept but omits one relevant limitation.",
  "status": "assessed"
}
```

This is an illustrative schema. Production identifiers should be generated by the application, and actual records must be validated before storage.

The `performance_score` and `evidence_coverage` fields represent different concepts and must not be combined without an explicit, documented reason.

---

## 13. Validation Plan

Before using scores in a demonstration or making performance claims:

- [ ] Test the rubric against representative sample answers.
- [ ] Test malformed and empty answers.
- [ ] Verify the handling of unassessed skills.
- [ ] Verify score calculations with unit tests.
- [ ] Verify that job weights sum to 100%.
- [ ] Test ranking with identical candidate inputs.
- [ ] Test excluded demographic fields.
- [ ] Test candidates without repositories.
- [ ] Inspect AI-generated explanations for unsupported claims.
- [ ] Compare AI evaluations with human-reviewed examples where available.
- [ ] Document evaluation results and known limitations.
- [ ] Clearly distinguish synthetic testing from official dataset evaluation.

---

## 14. Implementation Status

**Current status:** Proposed scoring framework.

The formulas and rubric in this document are design choices, not validated hiring predictors. They must be implemented, tested, and reviewed before being described as production-ready.

The system provides structured evidence to support human judgment. It does not independently determine whether a candidate should be hired.
