# ProofSkill AI — AI Strategy

**Version:** 1.0  
**Status:** Proposed  
**Primary language:** Python  
**Default interface:** Streamlit

---

## 1. Purpose

ProofSkill AI uses AI to help assess job-related skills through resumes, interviews, project evidence, and structured evaluations.

The AI layer must provide useful assessments without treating model-generated output as unquestionable truth.

This strategy defines:

- Which AI techniques are appropriate for each task.
- How models and providers are selected.
- How prompts and structured outputs are managed.
- How evaluations are validated.
- How the application behaves when an AI provider is unavailable.
- How model quality, fairness, privacy, and cost are evaluated.

**Important:** The models mentioned in this document are candidates for implementation, not a claim that they are already integrated.

## 2. AI Design Principles

1. Use the simplest approach that solves the task reliably.
2. Prefer structured, evidence-grounded outputs over unrestricted text generation.
3. Keep scoring rubrics independent of the model provider.
4. Separate skill performance, evidence coverage, and evidence confidence.
5. Validate AI-generated outputs before displaying or storing them.
6. Never fabricate evidence to complete a response.
7. Treat resumes, repositories, and candidate answers as untrusted input.
8. Provide a deterministic fallback for the hackathon demo.
9. Avoid demographic inference and irrelevant personal attributes.
10. Keep human review available for consequential decisions.

## 3. AI Task and Model Mapping

| Task | Initial approach | Optional model or tool |
|---|---|---|
| Resume text extraction | PDF/DOCX parsers | OCR for scanned documents |
| Skill extraction | Rules and structured LLM extraction | spaCy |
| Skill and evidence matching | Keyword baseline and semantic similarity | Sentence Transformers MiniLM |
| Interview question generation | Configured LLM with a question schema | Hosted LLM or local Llama |
| Answer evaluation | Fixed rubric plus structured LLM evaluation | Configured LLM |
| Adaptive question selection | Rules based on assessed skills and prior answers | LLM-assisted selection |
| Repository analysis | GitHub API and static file inspection | CodeBERT or GraphCodeBERT for specific experiments |
| Spoken-answer transcription | Speech-to-text service | Whisper |
| Candidate comparison | Deterministic scoring formulas | Scikit-learn for validated experiments |
| Demo fallback | Rules and fixed synthetic examples | No external model required |

Avoid using a large language model for tasks that deterministic code can handle more transparently, such as calculating weighted averages or validating score ranges.

## 4. Recommended MVP Strategy

### Stage 1 — Deterministic Baseline

Implement these capabilities before relying on an LLM:

- Resume text extraction.
- Job description input and basic skill normalization.
- Evidence records.
- Fixed interview rubrics.
- Score calculations.
- Evidence coverage calculations.
- Proof Card generation.
- Recruiter comparison.
- Demo-mode outputs.

This baseline ensures the application remains usable when external services are unavailable.

### Stage 2 — LLM-Assisted Features

Add an LLM provider for:

- Generating role-specific interview questions.
- Extracting structured skills from unstructured text.
- Evaluating candidate answers against a fixed rubric.
- Explaining scores using supplied evidence.
- Generating follow-up questions.

The LLM must not independently determine the final recruiter ranking.

### Stage 3 — Semantic Matching

Use a sentence-embedding model to compare job requirements with candidate evidence.

A possible starting model is `sentence-transformers/all-MiniLM-L6-v2`.

Semantic similarity should be treated as a relevance signal, not proof that a candidate possesses a skill.

For example, a high similarity score between a job requirement and a resume sentence does not establish practical competence. Interview or task evidence may still be necessary.

### Stage 4 — Optional Advanced Features

Consider adding:

- Speech-to-text.
- Repository-specific question generation.
- Code similarity analysis.
- More advanced ranking models after collecting appropriate evaluation data.

These features should not delay a working end-to-end MVP.

---

## 5. AI Provider Interface

Create a common provider interface so application services do not depend directly on one vendor.

The interface may support operations such as:

```python
generate_questions(
    job_requirements,
    candidate_evidence,
    assessed_skills,
)
```

```python
evaluate_answer(
    question,
    candidate_answer,
    rubric,
    supporting_context,
)
```

```python
extract_skills(
    document_text,
    allowed_skill_vocabulary,
)
```

These are illustrative function signatures. Final interfaces should use validated schemas and consistent error handling.

The provider layer should expose:

- A live implementation for the configured provider.
- A deterministic fallback implementation.
- Clear timeout and error behavior.
- Model and prompt version metadata where available.
- A way to validate returned structured data.

Do not scatter provider-specific SDK calls throughout the UI or scoring modules.

## 6. Prompt Design

Prompts should be task-specific, concise, and explicit about the evidence the model may use.

### 6.1 Interview Question Generation

The model should receive:

- Job requirements.
- Relevant candidate evidence.
- Skills already assessed.
- Allowed question types.
- Difficulty requirements.
- The required output schema.

The model should return questions that evaluate job-relevant skills and avoid unnecessary repetition.

The model must not assume that a skill is demonstrated merely because it appears in a resume.

### 6.2 Answer Evaluation

The evaluator should receive:

- The exact interview question.
- The candidate's answer.
- The scoring rubric.
- The relevant skill being assessed.
- Any explicitly permitted supporting context.

The evaluator should return:

- A score from 0 to 10, or a not-assessed status.
- A short explanation.
- Specific strengths in the answer.
- Important gaps or inaccuracies.
- Evidence references.
- An uncertainty or confidence label.

The evaluator must not invent facts, penalize irrelevant personal characteristics, or use a candidate's background as a substitute for evaluating the answer.

### 6.3 Evidence-Grounded Explanations

Proof Card explanations should be generated only from stored assessment results and their supporting evidence.

If evidence is unavailable, the model should say that the skill has not been assessed sufficiently.

It must not create fictional projects, achievements, code contributions, or interview responses.

## 7. Structured Output Validation

Use a defined schema for each AI task.

For answer evaluation, an illustrative output is:

```json
{
  "status": "assessed",
  "score": 3,
  "max_score": 4,
  "score_scale": "0-4",
  "explanation": "The answer correctly explains the main concept but omits an important limitation.",
  "strengths": [
    "Correct core explanation"
  ],
  "gaps": [
    "Does not discuss the relevant edge case"
  ],
  "evidence_references": [
    "answer-001"
  ],
  "evidence_confidence": "medium"
}
```

The application must validate:

- Required fields.
- Correct data types.
- Allowed status and confidence values.
- Score boundaries.
- Evidence-reference validity.
- Maximum text lengths where appropriate.

If validation fails, retry only within configured limits or use a clearly identified fallback. Never silently accept malformed output.

## 8. Adaptive Interview Logic

The initial adaptive interview should use transparent rules.

Example:

1. Select required skills that have not been assessed.
2. Generate or select a question for the highest-priority unassessed skill.
3. Evaluate the answer against the rubric.
4. Identify a material gap or an unclear explanation.
5. Select a follow-up question when useful.
6. Stop when the question limit is reached or sufficient coverage is achieved.

The system must not endlessly generate follow-up questions or repeatedly test the same skill without a clear reason.

Adaptive behavior should improve assessment coverage, not deliberately make the interview harder for a particular candidate.

## 9. Fallback Strategy

Demo mode must work without an API key or internet access.

| Situation | Expected behavior |
|---|---|
| API key missing | Use demo mode or show a configuration message |
| Provider unavailable | Use the deterministic fallback where supported |
| Request times out | Stop the request and return a clear status |
| Invalid model output | Validate, retry within limits, or fall back |
| Embedding model unavailable | Use a documented keyword-based baseline |
| Repository inaccessible | Offer manual project information or alternative assessment |
| Speech transcription fails | Allow typed answers |
| Official dataset unavailable | Use clearly labeled synthetic test data |

Fallback results must be labeled accurately. The application must not imply that a live model evaluated an answer when a rule-based or precomputed result was used.

## 10. Fairness and Responsible Evaluation

The AI layer must:

- Exclude college name, gender, age, and location from scoring prompts and ranking inputs.
- Avoid inferring demographic attributes from names, writing style, or speech.
- Avoid inferring intelligence or technical ability from accent or voice characteristics.
- Apply the same rubric to comparable candidates.
- Distinguish missing evidence from poor performance.
- Support alternative assessments for candidates without public repositories.
- Provide explanations that recruiters can inspect.
- Avoid automatically rejecting candidates based solely on an AI-generated score.

Fairness testing must cover both the deterministic scoring code and the behavior of any configured model.

Passing a limited set of fairness tests does not prove that the entire system is free of bias.

## 11. Security and Prompt Injection

Uploaded documents, repository files, and candidate answers may contain malicious or irrelevant instructions.

Treat all such content as data, not as instructions to the AI system.

Required safeguards:

- Separate system instructions from candidate-provided content.
- Explicitly instruct the model to ignore instructions embedded in supplied documents.
- Do not allow document content to change scoring rules or reveal secrets.
- Never send API keys or internal credentials in model prompts.
- Validate all model outputs.
- Avoid executing candidate-provided code.
- Restrict external network access to approved integrations.
- Limit the amount of untrusted content included in prompts.

Prompt instructions alone are not a complete security boundary. Enforce permissions and validation in application code.

## 12. Cost, Latency, and Reliability

The MVP should minimize unnecessary model calls.

Recommended practices:

- Generate questions in small batches where appropriate.
- Avoid repeatedly extracting the same document when its content has not changed.
- Cache reusable non-sensitive computations when safe.
- Set request timeouts and retry limits.
- Keep deterministic calculations outside the LLM.
- Track approximate usage and latency when provider metadata is available.
- Do not store raw candidate content in diagnostic logs.

Model selection should consider quality, latency, cost, data-handling terms, and deployment requirements rather than benchmark scores alone.

## 13. AI Evaluation Plan

Before relying on AI outputs:

1. Prepare representative synthetic resumes, job descriptions, questions, and answers.
2. Define expected behavior using the scoring rubric.
3. Test strong, partial, incorrect, ambiguous, and empty answers.
4. Measure structured-output validity.
5. Compare repeated evaluations for consistency.
6. Review whether explanations are supported by the supplied evidence.
7. Test prompt-injection examples.
8. Test fairness-related invariance requirements.
9. Compare model-assisted evaluation with human-reviewed examples where available.
10. Record limitations and results.

Potential metrics include:

- Structured-output validity rate.
- Agreement with human-reviewed rubric scores.
- Skill extraction precision and recall.
- Evidence-reference validity rate.
- Repeated-evaluation consistency.
- Average response latency.
- Cost per completed assessment.

Do not claim performance thresholds or benchmark results until they have been measured.

## 14. Model Versioning

For each model-assisted evaluation, store relevant metadata where available:

- Provider identifier.
- Model identifier.
- Prompt version.
- Rubric version.
- Evaluation timestamp.
- Input and output schema versions.
- Whether the result came from live mode or fallback mode.

Avoid storing secrets or unnecessary copies of candidate content.

Changes to prompts, model versions, or scoring rubrics should be tested before being used in a formal comparison.

## 15. Implementation Checklist

- [ ] Create the provider interface.
- [ ] Implement a deterministic fallback provider.
- [ ] Add structured output schemas and validation.
- [ ] Implement interview question generation.
- [ ] Implement rubric-based answer evaluation.
- [ ] Add evidence-grounded explanations.
- [ ] Implement adaptive question selection.
- [ ] Add timeouts and error handling.
- [ ] Add prompt-injection safeguards.
- [ ] Test behavior without API credentials.
- [ ] Test scoring and fairness requirements.
- [ ] Record model and rubric versions.
- [ ] Document known limitations.

## 16. Current Status

**Status:** Proposed AI strategy.

Model choices, provider integrations, evaluation results, and performance claims must be updated only after implementation and testing.
