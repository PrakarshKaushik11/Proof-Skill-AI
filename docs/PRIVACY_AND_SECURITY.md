# Privacy and Security — ProofSkill AI

## 1. Purpose

This document defines privacy and security requirements for ProofSkill AI, an AI-assisted platform that helps candidates demonstrate practical skills through resumes, project evidence, technical assessments, and structured interviews.

Candidate information can be sensitive, and assessment outputs may influence employment opportunities. The system must therefore minimize data collection, restrict access, protect evidence, communicate limitations, and keep final hiring decisions under human control.

**Status:** Security and privacy requirements for the project. Controls must be verified against the actual implementation before being described as implemented.

## 2. Core Principles

ProofSkill AI follows these principles:

- **Data minimization:** Collect only information necessary for a defined purpose.
- **Purpose limitation:** Use information only for authorized purposes.
- **Consent and authorization:** Obtain appropriate permission before accessing candidate-controlled data or optional input sources.
- **Least privilege:** Grant only the access required for a workflow.
- **Transparency:** Explain what data is collected, how it is used, and which AI services may process it.
- **Evidence integrity:** Preserve the distinction between candidate claims, observed evidence, assessed results, and model-generated interpretations.
- **Human oversight:** Do not make final hiring decisions automatically.
- **Secure defaults:** Keep optional integrations disabled until configured and authorized.
- **Accountability:** Document access, retention, known limitations, and security incidents where applicable.

## 3. Data Classification

| Classification | Examples | Required handling |
|---|---|---|
| Public | Public project documentation, approved public job descriptions | Check for secrets and licensing restrictions before publishing. |
| Internal | Application configuration, development notes, non-sensitive logs | Restrict access to project collaborators as appropriate. |
| Confidential | Candidate resumes, assessment responses, skill profiles, recruiter evaluations | Limit access, minimize retention, and protect against unauthorized disclosure. |
| Restricted | Credentials, access tokens, private repository content, sensitive recordings, restricted datasets | Apply strict access controls, secure storage, and approved processing only. |

A public GitHub repository may still contain personal information or secrets. Public availability does not automatically authorize unrestricted reuse.

## 4. Data Collection and Minimization

The application may process:

- Candidate-provided resume content.
- Declared skills and project descriptions.
- Authorized repository evidence.
- Technical assessment questions and responses.
- Structured evaluation results.
- Job descriptions and job-relevant criteria.
- Consent and authorization records needed to manage access.

Collect only fields required for the selected workflow.

Avoid collecting or storing unnecessary:

- Government identification numbers.
- Home addresses and personal contact details.
- Financial information.
- Sensitive demographic attributes.
- Raw audio or video recordings.
- Private repository content unrelated to the assessment.

Use pseudonymous candidate identifiers where practical. A pseudonymous identifier is not sufficient by itself to anonymize a record if the person can still be identified through linked data.

## 5. Consent and Authorization

Before processing candidate-controlled evidence, the application should communicate the purpose and relevant data-handling practices.

### Candidate resumes

- Explain why the resume is being processed.
- Limit processing to the intended assessment workflow.
- Avoid reusing resume data for unrelated purposes without an appropriate basis and permission.

### Private repositories

- Obtain explicit authorization before accessing a private repository.
- Request the minimum permissions necessary.
- Do not assume that providing a public repository URL grants access to private content.
- Stop accessing a source when authorization is withdrawn, subject to applicable requirements for already processed records.

### Audio and speech-to-text

- Make audio input optional.
- Explain when audio is recorded or sent to an external transcription service.
- Provide a text-based alternative.
- Avoid retaining raw audio when it is not needed.

A checkbox or client-submitted consent flag must not be treated as sufficient authorization for every operation. The application must enforce relevant permissions on the server side.

## 6. Candidate Data Lifecycle

The intended data lifecycle is:

1. **Collection:** Accept only supported inputs and required fields.
2. **Validation:** Check file types, size limits, field formats, and authorization.
3. **Processing:** Extract or assess evidence for the stated purpose.
4. **Storage:** Store only required records with appropriate access controls.
5. **Presentation:** Show authorized users relevant evidence and assessment results.
6. **Retention:** Keep data only for the documented period.
7. **Deletion:** Delete or de-identify data according to the applicable retention and deletion policy.

Retention periods must be defined before processing real candidate data. Do not promise immediate or complete deletion unless the implementation can deliver it, including for applicable derived records, logs, backups, and external services.

## 7. Storage Security

For the initial prototype, SQLite may be used for local persistence.

The use of SQLite does not automatically secure candidate information. Apply the following safeguards:

- Store the database in an appropriate location with restricted filesystem permissions.
- Do not commit databases containing real candidate data.
- Keep database files and backups out of public repositories.
- Avoid storing raw resumes or recordings when extracted, minimized data is sufficient.
- Protect sensitive files and backups using appropriate encryption and access controls.
- Use parameterized database queries.
- Validate all inputs before database operations.
- Keep development fixtures separate from real candidate data.

If the application is deployed for multiple users or production use, reassess database access, encryption, backup security, auditability, and operational controls.

## 8. File Upload Security

Resume and artifact uploads must be treated as untrusted input.

Required controls include:

- Allow only explicitly supported file formats.
- Enforce configurable file-size limits.
- Validate file contents rather than trusting the filename or MIME type alone.
- Handle corrupt, encrypted, malformed, and oversized documents safely.
- Use generated internal filenames rather than trusting user-supplied paths.
- Prevent path traversal and unsafe file access.
- Avoid executing uploaded files.
- Apply processing timeouts and resource limits.
- Avoid logging raw file contents.
- Remove temporary files according to the retention policy.

Document parsers can encounter malformed or malicious files. Keep dependencies updated and isolate risky processing where practical.

## 9. GitHub and Repository Security

Repository evidence must be collected only within the authorized scope.

- Show GitHub URLs extracted from resumes before making any network request; an extracted link is not consent.
- Obtain candidate consent before discovering public repositories from a linked profile.
- Show discovered repositories and require explicit selection and confirmation before retrieving source files.
- A direct repository URL is not permission to enumerate the owner's other repositories.
- Public repositories are the default. Private repository access requires a separate, least-privilege authorization flow.
- Keep GitHub access read-only. Candidate code changes are submitted as assessment responses or patches, not pushed to the repository.
- Bound repository/file counts, file sizes, response sizes, and request time.
- Offer an equivalent assessment if discovery is declined or repository access is unavailable.

- Use official APIs and documented authentication flows.
- Request the minimum required permissions.
- Never embed access tokens in source code, prompts, or frontend assets.
- Keep credentials in environment variables or an approved secret manager.
- Handle expired credentials, revoked permissions, rate limits, and inaccessible repositories safely.
- Do not execute candidate-submitted code as part of ordinary evidence collection.
- Do not expose private source code in recruiter-facing explanations unless explicitly authorized and necessary.
- Avoid treating commit counts, repository popularity, or public visibility as direct measures of competence.

Repository files may contain malicious instructions, scripts, or embedded secrets. Treat all repository content as untrusted data.

## 10. AI Provider Security

ProofSkill AI may use external language models, embedding models, or speech-to-text services.

Before enabling an external provider:

1. Identify the exact data sent to the provider.
2. Confirm that the processing is authorized for the intended purpose.
3. Review retention, logging, training, and data-location terms where relevant.
4. Minimize or redact unnecessary identifying information where practical.
5. Keep provider credentials outside source control.
6. Validate the provider's response before storing or displaying it.
7. Define safe behavior for timeouts, malformed outputs, and provider outages.

Do not send confidential candidate information to an external AI service by default.

### AI-generated output

- Treat model output as untrusted until validated.
- Do not allow candidate documents or repository content to override trusted instructions.
- Preserve references to supporting evidence.
- Distinguish generated explanations from verified facts.
- Do not invent candidate achievements, qualifications, or assessment results.
- Do not treat semantic similarity as proof of competence.
- Do not claim that an AI output is accurate or fair without appropriate evaluation.

## 11. Prompt Injection and Untrusted Content

Resume text, repository files, uploaded artifacts, and assessment responses may contain instructions intended to manipulate an AI model.

To reduce risk:

- Separate trusted system instructions from candidate-provided content.
- Treat retrieved text as evidence, not executable instructions.
- Restrict model output to the requested task and expected schema.
- Validate output fields, values, and evidence references.
- Do not allow model output to trigger privileged actions without independent authorization.
- Do not place secrets in prompts.
- Test adversarial inputs and malicious embedded instructions.

Prompt-level safeguards alone are not a complete security boundary. Authorization and validation must be enforced in application code.

## 12. Authentication and Access Control

Any deployment that handles real candidate data must implement appropriate authentication and resource-level authorization.

Requirements:

- Verify the caller's identity where authentication is required.
- Check permissions on every sensitive resource operation.
- Restrict candidate access to the records they are authorized to view.
- Restrict recruiter access according to the applicable workflow and policy.
- Never trust a client-supplied candidate identifier as proof of permission.
- Use least-privilege access for database and external-service credentials.
- Protect administrative operations.
- Apply rate limits to sensitive or expensive operations.
- Avoid exposing whether a protected record exists when that information is sensitive.

A local demo mode may use simplified access for synthetic data, but it must not be presented as production-grade authentication.

## 13. Secrets and Configuration

Secrets include API keys, access tokens, database credentials, and signing keys.

- Use `.env.example` to document required variable names with placeholder values.
- Keep actual credentials in local configuration or an approved secret manager.
- Do not commit `.env` files containing secrets.
- Do not print secrets during startup or error handling.
- Rotate exposed credentials promptly.
- Revoke credentials that are no longer needed.
- Use separate credentials for development and production where applicable.
- Avoid embedding server-side credentials in client-visible code.

If a secret is accidentally committed, deleting it from the latest commit is not sufficient. Revoke or rotate it and address the repository history and exposure risk.

## 14. Logging and Monitoring

Logs should support debugging and security review without unnecessarily exposing candidate information.

Recommended log fields include:

- Timestamp.
- Request or correlation identifier.
- Operation name.
- Safe error code.
- Processing duration.
- External provider status where relevant.

Avoid logging:

- Raw resumes.
- Private repository contents.
- Full assessment responses unless specifically authorized and necessary.
- Audio recordings or transcripts by default.
- API keys and access tokens.
- Sensitive personal attributes.
- Confidential prompts containing candidate information.

Restrict log access and define retention periods. Error messages displayed to users should not reveal stack traces, internal paths, credentials, or sensitive data.

## 15. Fairness and Responsible Assessment

Security and privacy controls must support fair, evidence-based evaluation.

- Do not use college name, gender, age, location, accent, or other irrelevant personal characteristics as proxies for ability.
- Do not infer personality, honesty, or psychological traits from voice or appearance.
- Provide an alternative to public repository evidence.
- Distinguish insufficient evidence from demonstrated lack of skill.
- Apply the same documented rubric to candidates being compared for the same role.
- Keep evidence, model inference, and assessment scores distinguishable.
- Explain limitations and uncertainty to recruiters.
- Keep final hiring decisions under human control.

Removing sensitive attributes from a scoring input does not by itself establish fairness. Evaluate the system for inconsistent errors and outcomes where lawful, appropriate, and supported by sufficient data.

## 16. Error Handling and Availability

When an external service or AI provider fails:

- Return a clear and safe error status.
- Use bounded retries where appropriate.
- Avoid duplicate submissions during retries.
- Use deterministic fallback behavior only when suitable for the task.
- Clearly distinguish fallback output from live-model output.
- Do not fabricate successful results to keep a demo running.
- Preserve completed records where possible.
- Avoid exposing sensitive request content in error messages.

The application should fail safely when it cannot evaluate evidence reliably.

## 17. Data Integrity

Maintain integrity across evidence records, scores, and profiles.

- Use stable identifiers and validated relationships.
- Preserve source references for extracted claims.
- Record the rubric version used for each assessment result.
- Avoid silently overwriting previous evaluation results.
- Validate score ranges and status transitions.
- Prevent unauthorized modification of candidate evidence.
- Record relevant changes where auditability is required.
- Ensure recruiter explanations agree with the stored results.

A generated profile must not be represented as independently verified when it is based only on candidate claims or model-generated interpretation.

## 18. Security Testing

Security checks should cover:

- Unauthorized candidate record access.
- Cross-candidate data exposure.
- Invalid or oversized file uploads.
- Malformed document handling.
- Path traversal attempts.
- SQL injection risks.
- Secret leakage in logs and errors.
- Prompt injection through candidate documents.
- Repository permission and token handling.
- AI provider failures and invalid responses.
- Access-control enforcement for recruiter comparisons.
- Retention and deletion behavior.

Record test outcomes and unresolved risks. Do not mark a control as implemented merely because it is described in this document.

## 19. Incident Response

If a suspected privacy or security incident occurs:

1. Stop the affected processing or revoke the affected access where appropriate.
2. Protect relevant evidence needed to investigate the incident.
3. Identify the affected data, systems, credentials, and users.
4. Rotate or revoke exposed credentials.
5. Assess the scope and potential impact.
6. Follow applicable organizational and legal notification requirements.
7. Document corrective actions.
8. Verify that the underlying issue has been addressed before restoring the affected workflow.

Do not include sensitive candidate data or credentials in incident reports unless necessary and appropriately protected.

## 20. Deployment Checklist

Before deploying an environment that handles real candidate data, verify:

- [ ] Authentication and resource-level authorization are enabled.
- [ ] Secrets are configured outside source control.
- [ ] Transport security is configured appropriately.
- [ ] Database and file access are restricted.
- [ ] Upload limits and input validation are enforced.
- [ ] External AI processing has been reviewed and authorized.
- [ ] Retention and deletion procedures are defined.
- [ ] Logs exclude unnecessary sensitive information.
- [ ] Backups and recovery procedures are appropriately protected.
- [ ] Security and privacy tests have been executed.
- [ ] Candidate-facing data-processing notices are available.
- [ ] Known risks and limitations have been documented.
- [ ] Human review remains part of hiring decisions.

Mark each item complete only after verifying the actual deployment.

## 21. Related Documentation

- `SECURITY.md` — repository security reporting and guidance.
- `docs/SECURITY_PRIVACY.md` — additional security and privacy requirements.
- `docs/AI_MODELS.md` — AI model choices and limitations.
- `docs/AI_STRATEGY.md` — AI workflow and safeguards.
- `docs/API_SPEC.md` — proposed API contracts.
- `docs/DATA_DICTIONARY.md` — data field definitions.
- `docs/DATASETS.md` — dataset provenance and usage.
- `docs/SCORING_AND_FAIRNESS.md` — scoring and fairness principles.
- `docs/TESTING_AND_EVALUATION.md` — testing and evaluation.
- `docs/ARCHITECTURE.md` — system architecture.

## 22. Maintenance

Review this document whenever data sources, AI providers, authentication mechanisms, storage arrangements, or deployment environments change.

Privacy and security requirements must be verified against the implementation. If a control is missing, document it as a gap and prioritize remediation before processing real candidate data.
