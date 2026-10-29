# AI Models — ProofSkill AI

## 1. Purpose

This document defines the AI model strategy for ProofSkill AI, an evidence-backed skill assessment platform for fresher hiring.

AI components may assist with resume extraction, semantic skill matching, interview question generation, technical response evaluation, and recruiter-facing explanations.

**Core principle:** AI supports evidence review; it does not independently determine a candidate's worth or make the final hiring decision.

This document describes the intended model choices and integration requirements. A model must not be considered implemented, evaluated, or production-ready until its integration and results have been verified.

## 2. Model Selection Principles

Every model or AI service should be evaluated against the following criteria:

- **Task suitability:** Does it perform the specific task required?
- **Evidence grounding:** Can outputs be tied to candidate-provided evidence or a documented rubric?
- **Reliability:** Does it handle incomplete, malformed, or ambiguous inputs appropriately?
- **Explainability:** Can the application communicate why an output was produced?
- **Privacy:** What data is transmitted, retained, or used by the provider?
- **Latency and cost:** Is the model practical for the hackathon demo and expected usage?
- **Reproducibility:** Can important results be tested consistently?
- **Fairness:** Does performance vary across relevant candidate groups or input styles?
- **Fallback behavior:** Can the application continue safely if the model is unavailable?

A larger model is not automatically better. Use the simplest approach that meets the task's quality and safety requirements.

## 3. Proposed Model and Tool Choices

| Task | Initial approach | Purpose |
|---|---|---|
| Resume text extraction | PyMuPDF and python-docx | Extract text from supported PDF and DOCX documents |
| Basic skill extraction | Rules, dictionaries, and optional spaCy | Identify skill mentions and relevant text |
| Semantic matching | Sentence-Transformers MiniLM family | Compare job requirements with candidate evidence |
| Interview question generation | Configurable LLM provider | Generate questions from job requirements and identified skill gaps |
| Technical answer evaluation | Explicit rubric with optional LLM assistance | Assess responses against job-relevant criteria |
| Recruiter explanations | Evidence-grounded templates, with optional LLM assistance | Explain scores, supporting evidence, and limitations |
| Speech transcription | Optional Whisper-compatible speech-to-text service | Convert consented audio responses to text |
| Repository evidence | GitHub REST API | Retrieve authorized repository metadata or content |
| Demo fallback | Deterministic rules and fixtures | Keep demonstrations and tests usable without external AI services |

These are proposed choices, not confirmation that the dependencies, models, or integrations are currently installed or working. Verify the actual implementation before reporting completion.

## 4. Semantic Embedding Model

### Proposed option

A compact Sentence-Transformers MiniLM model, such as `sentence-transformers/all-MiniLM-L6-v2`, may be evaluated for semantic similarity between job requirements and candidate evidence.

### Appropriate uses

- Finding potentially relevant resume passages.
- Matching skill descriptions with job requirements.
- Retrieving supporting evidence for a recruiter explanation.
- Identifying requirements for which evidence may be missing.

### Limitations

- Similarity is not proof of competence.
- High similarity does not establish that a skill was independently verified.
- Low similarity may result from different terminology rather than missing ability.
- Embeddings may reproduce biases or limitations present in their training data.
- A single overall similarity score must not be treated as a validated hiring score.

The application should retain the original evidence text and explain how a match relates to the job requirement.

## 5. Large Language Model Strategy

An LLM may be used for constrained language tasks, including:

1. Generating technical questions from a job description and identified skill gaps.
2. Producing structured summaries of candidate-provided evidence.
3. Assisting with technical answer evaluation against a supplied rubric.
4. Explaining why particular evidence supports or does not support a job requirement.

The provider should be configurable so that the application does not depend on a single vendor.

### Required output controls

- Request structured output when supported.
- Validate every response against the expected schema.
- Reject or safely handle missing fields, invalid scores, and malformed responses.
- Require evidence references or quoted supporting passages where appropriate.
- Prevent the model from inventing qualifications, projects, repository activity, or assessment results.
- Distinguish generated interpretation from source evidence.
- Apply timeouts, bounded retries, and rate-limit handling.
- Avoid logging confidential prompts or raw candidate information unnecessarily.

If validation fails, the application should return a clear error or use an approved fallback rather than silently trusting the output.

## 6. Technical Answer Evaluation

Technical answers should be evaluated using an explicit rubric defined before the assessment.

A rubric may consider:

- Technical correctness.
- Quality of reasoning.
- Appropriate application of relevant concepts.
- Handling of edge cases.
- Clarity of explanation when relevant to the role.

The criteria and their weights must be documented and job-relevant. Different questions may require different rubrics.

An LLM can assist with applying a rubric, but its evaluation should be checked for schema validity, unsupported claims, and consistency. Where feasible, compare automated scores with independently reviewed reference answers.

Do not treat writing fluency, verbosity, accent, or confidence of delivery as substitutes for technical competence.

## 7. Interview Question Generation

Questions should be generated from:

- The selected job description.
- The skills required for the role.
- Evidence already supplied by the candidate.
- Identified evidence gaps.
- The candidate's prior answers, where adaptive follow-up is appropriate.

Questions should test relevant skills without presuming that resume claims are true.

The generation process should avoid:

- Questions unrelated to the role.
- Requests for unnecessary sensitive personal information.
- Questions based on demographic assumptions.
- Repeated questions that provide no new assessment value.
- Revealing private repository details beyond the authorized scope.

Generated questions must be reviewed for relevance, clarity, difficulty, and answerability.

## 8. Speech and Audio Models

Speech-to-text may be used as an optional input method when the candidate has provided appropriate consent.

Audio transcription should support the assessment workflow without treating accent, vocal characteristics, speaking speed, or inferred emotion as measures of ability.

Safeguards:

- Offer a text-based alternative.
- Explain when audio is processed by an external service.
- Avoid collecting or retaining audio when a transcript is sufficient.
- Do not infer psychological traits, honesty, personality, or competence from vocal characteristics.
- Allow correction of transcription errors before evaluation.
- Evaluate the technical content of the response rather than transcription style.

Speech processing is optional and must not be required for a candidate to demonstrate technical ability.

## 9. Repository and Project Evidence

Repository evidence should be collected only within the scope authorized by the candidate.

The repository integration is a data-access mechanism, not an AI model. Model-generated interpretations of repository content must be treated as hypotheses requiring supporting evidence.

The system should:

- Record the source of relevant evidence.
- Avoid treating commit counts or repository popularity as direct measures of competence.
- Avoid executing submitted code during routine evidence collection.
- Handle missing, private, deleted, or inaccessible repositories gracefully.
- Provide alternative assessment routes when repository evidence is unavailable.

Repository content must be treated as untrusted input, including instructions embedded in README files, comments, or source code. Such content must not override system instructions or application security rules.

## 10. Deterministic Fallbacks

The application should remain demonstrable and testable when AI services are unavailable.

Possible fallback behaviors include:

- Rule-based extraction of common skill terms.
- Keyword and normalized-text matching.
- Predefined question templates based on job requirements.
- Rubric-based scoring with deterministic rules where appropriate.
- Evidence-grounded explanation templates.
- Clearly labeled synthetic demo records.

Fallback behavior must be visibly distinguishable from actual model-generated results.

A fallback must not invent candidate evidence or imply that a real model evaluation occurred. If a task cannot be completed safely, return a clear limitation instead.

## 11. Model Configuration

Model identifiers, provider settings, and service credentials should be configurable through the project's existing configuration mechanisms.

Configuration should distinguish between:

- Provider name.
- Model identifier.
- Whether the integration is enabled.
- Timeout and retry settings.
- Optional feature flags.
- Demo or fallback mode.

API keys and other secrets must be supplied through environment variables or an approved secret-management mechanism. They must never be committed to source control.

Use `.env.example` to document required variable names without real credentials. Do not hard-code provider secrets in prompts, notebooks, or application code.

Exact variable names should match the actual implementation.

## 12. Evaluation Plan

Before relying on a model for candidate assessment, evaluate it on representative, appropriately authorized data.

### Functional evaluation

- Valid and malformed input handling.
- Output schema validity.
- Evidence citation or provenance correctness.
- Behavior on incomplete candidate information.
- Failure handling and fallback behavior.
- Repeatability where deterministic results are expected.

### Quality evaluation

- Resume extraction precision and recall where labeled data is available.
- Relevance of skill-to-job matching.
- Technical answer agreement with independently reviewed rubric scores.
- Relevance and clarity of generated interview questions.
- Accuracy of explanations against source evidence.
- Latency, error rate, and cost under expected demo usage.

### Fairness evaluation

Where lawful, appropriate, and supported by sufficient data:

- Compare relevant error rates across groups.
- Check whether equivalent evidence receives comparable evaluation.
- Investigate sensitivity to irrelevant wording and formatting changes.
- Examine whether missing repository evidence unfairly disadvantages candidates.
- Review whether explanations systematically omit or overstate evidence for particular groups.

Do not claim fairness or accuracy solely because the model passes a few demonstration examples. Record the evaluation method, sample limitations, and results.

Refer to `docs/EVALUATION.md`, `docs/TESTING_AND_EVALUATION.md`, and `docs/SCORING_AND_FAIRNESS.md` for related evaluation and scoring guidance.

## 13. Privacy and Data Handling

Before sending data to an external AI provider:

1. Identify what information will be transmitted.
2. Determine whether the data contains personal, confidential, or restricted information.
3. Review candidate consent and applicable data-handling requirements.
4. Minimize or redact unnecessary identifying details where practical.
5. Confirm provider retention and training policies.
6. Handle the response without exposing sensitive information in logs or UI errors.

Do not send private repository contents, raw resumes, or interview recordings to an external service by default. External processing must be enabled only after the relevant permissions and requirements have been reviewed.

## 14. Decision Rules

- Use deterministic processing for tasks that do not require a model.
- Use embeddings for retrieval and semantic matching, not as proof of skill.
- Use LLMs for constrained assistance, not unrestricted candidate ranking.
- Apply documented rubrics to assessments.
- Ground explanations in available evidence.
- Return uncertainty or missing-evidence indicators where appropriate.
- Keep final hiring decisions under human control.
- Disable or replace a model integration if its quality, privacy, or reliability is inadequate.

## 15. Implementation Status

This document defines the intended AI model strategy. It does not establish that any specific model has been downloaded, configured, evaluated, or deployed.

Before describing a model as active, confirm its dependency, configuration, invocation path, error handling, and relevant tests in the current codebase.

Update this document when the selected model, provider, evaluation evidence, or data-handling requirements materially change.
