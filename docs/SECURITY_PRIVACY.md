# ProofSkill AI — Security and Privacy

**Version:** 1.0  
**Status:** Proposed  
**Applies to:** Candidate data, resumes, assessments, AI providers, repository integrations, and recruiter workflows

---

## 1. Purpose

This document defines the security and privacy safeguards required for ProofSkill AI.

The application may process personal information, resumes, interview answers, project descriptions, repository metadata, and AI-generated evaluations. These data must be handled carefully and used only for documented purposes.

Security and privacy controls must be implemented in application code. Documentation alone does not establish that a control is operational.

## 2. Security Principles

- Collect only information necessary for the assessment.
- Explain why candidate information is being collected.
- Obtain appropriate consent for optional processing.
- Never commit API keys or credentials to source control.
- Treat uploaded files and repository content as untrusted input.
- Validate inputs before processing or storing them.
- Restrict access to candidate records.
- Avoid unnecessary retention of raw personal information.
- Provide an alternative assessment for candidates without public repositories.
- Make AI-generated assessments explainable and reviewable.
- Do not use college name, gender, age, or location as ranking features.
- Clearly distinguish demo data from real candidate data.

## 3. Data Classification

| Classification | Examples | Required handling |
|---|---|---|
| Public | Public project documentation | Validate before use |
| Internal | Application configuration and non-sensitive logs | Restrict access where appropriate |
| Candidate data | Resumes, answers, assessment results | Minimize, protect, and apply retention rules |
| Sensitive operational data | API keys, access tokens, database credentials | Keep in environment configuration or an approved secret store; never log or commit |

Public availability does not mean information can be used without considering consent, purpose, or applicable policies.

## 4. Resume Upload Security

The resume processing service must:

1. Allow only explicitly supported file types.
2. Validate file content rather than trusting the filename or declared MIME type alone.
3. Enforce a configurable upload size limit.
4. Handle malformed and empty documents safely.
5. Avoid executing uploaded content.
6. Use temporary storage carefully and remove temporary files when no longer needed.
7. Avoid logging extracted resume text.
8. Handle parsing errors without exposing internal stack traces.
9. Avoid treating embedded document instructions as trusted AI instructions.

For the MVP, PDF and DOCX support may be sufficient. Scanned-document OCR should be considered optional until implemented and tested.

## 5. Candidate Consent

Candidates should receive clear information about the assessment process and optional data processing.

Consent requirements include:

- Explain what information will be collected.
- Explain why each optional source is requested.
- Request permission before repository analysis.
- Record the scope and status of consent.
- Allow candidates to decline optional repository analysis.
- Provide an alternative assessment path.
- Respect consent revocation for future processing within the relevant scope.
- Document any limitations on deletion or retention.

Repository consent must be separate from any unrelated permission. Access to a public repository must not be treated as blanket permission to collect unrelated candidate information.

## 6. GitHub Repository Security

Repository URLs and file contents must be treated as untrusted input.

Resume-extracted GitHub links are claims, not permission to make network requests. Show each normalized link to the candidate. Obtain an application-recorded consent for public repository discovery before listing repositories, then require candidate selection and confirmation before retrieving source files. A direct repository link does not authorize listing or analyzing the owner's other repositories.

### URL validation

The repository integration should:

- Accept only supported GitHub URLs.
- Reject unexpected schemes such as `file://` and unsupported protocols.
- Reject URLs containing embedded credentials.
- Parse and validate the hostname before making requests.
- Restrict requests to approved GitHub API endpoints.
- Disable automatic redirects or revalidate every redirect destination.
- Apply timeouts and response-size limits.
- Handle rate limits and inaccessible repositories.
- Never fetch arbitrary URLs supplied through repository files.
- Retrieve files only from candidate-selected repositories associated with the approved GitHub host.
- Keep the integration read-only; do not write, commit, or push candidate code changes.
- Bound repository counts, file counts, file sizes, response sizes, and request time.
- Exclude known credential/configuration files and avoid returning or logging detected secrets. Secret scanning is best-effort, not a guarantee.

These measures reduce server-side request forgery (SSRF) and related risks.

### Repository content

- Never execute repository code during analysis.
- Treat proposed candidate code changes as untrusted response content; do not execute them or apply them to the remote repository.
- Treat source files, comments, README text, and configuration files as untrusted data.
- Do not allow repository content to override AI system instructions.
- Avoid downloading unnecessary files.
- Apply file-count and size limits.
- Do not claim authorship solely from commit metadata or repository ownership.

## 7. AI and Prompt-Injection Security

Resumes, repositories, and candidate answers may contain instructions intended to manipulate the AI.

Required safeguards:

- Separate trusted application instructions from user-provided content.
- Tell models to treat supplied content as data, not instructions.
- Never include secrets in prompts.
- Restrict tools and external actions available to the model.
- Validate structured outputs before using them.
- Do not let AI output directly execute SQL, shell commands, or arbitrary code.
- Do not allow model-generated content to bypass consent checks.
- Keep scoring rules and permissions under application control.

Prompt wording is not a complete security boundary. Critical permissions, validation, and access restrictions must be enforced in code.

## 8. API Keys and Secrets

All external credentials must be stored outside source code.

Use `.env.example` to document the expected variable names without including real values.

Example:

```dotenv
APP_MODE=demo
DATABASE_PATH=data/proofskill.db

LLM_API_KEY=
LLM_MODEL=
GITHUB_TOKEN=
IMATS_API_KEY=
```

These variables are illustrative. Implement only the configuration entries required by the selected integrations.

Security rules:

- Add `.env` to `.gitignore`.
- Never commit real tokens or passwords.
- Never print secret values in logs.
- Avoid placing credentials in URLs.
- Use minimum necessary permissions for external tokens.
- Rotate a credential immediately if it is accidentally exposed.
- Keep demo mode functional without external credentials.

Do not request a GitHub token merely to inspect a public repository.

## 9. Database Security

The SQLite database should:

- Use parameterized queries.
- Enable foreign key enforcement.
- Validate data before writes.
- Restrict access to the database file.
- Avoid storing unnecessary personal information.
- Use transactions for related operations.
- Apply a documented retention and deletion policy.
- Avoid placing the database in a publicly served directory.

For deployments handling real candidate data, assess whether encryption at rest, encrypted backups, stronger authentication, and a managed database are required.

## 10. Authentication and Authorization

If authentication is implemented, the system should:

- Verify user identity before accessing protected records.
- Enforce role-based permissions.
- Separate candidate access from recruiter access.
- Restrict candidates to their own assessment records.
- Restrict recruiters to records they are authorized to review.
- Avoid relying on hidden UI elements as an authorization mechanism.
- Protect sensitive operations such as exports and deletion.

A local hackathon prototype without authentication must be clearly labeled as a demo and must not be exposed as a production service containing real candidate data.

## 11. Fairness and Responsible Use

The system must not:

- Use college name, gender, age, or location to determine candidate rankings.
- Infer technical competence from accent or voice characteristics.
- Automatically reject candidates solely because of an AI score.
- Treat missing evidence as proof of incompetence.
- Treat a lack of GitHub activity as proof of poor coding ability.
- Present similarity alerts as definitive proof of cheating.
- Invent evidence or claim that code was executed when it was not.

Candidates and recruiters should be able to inspect the evidence and limitations behind an evaluation.

## 12. Logging and Monitoring

Logs should help diagnose problems without exposing candidate information.

Recommended log fields:

- Timestamp.
- Event type.
- Request or assessment identifier.
- Component name.
- Error category.
- Provider mode, such as `demo` or `live`.

Avoid logging:

- API keys and access tokens.
- Full resumes.
- Complete interview transcripts unless specifically required and authorized.
- Sensitive candidate information.
- Unnecessary repository content.

Sanitize user-controlled values before logging to prevent log injection.

## 13. Data Retention and Deletion

Define retention rules before collecting real candidate data.

The implementation should:

- Keep only the data required for the documented purpose.
- Delete temporary upload files after processing where practical.
- Support candidate-data deletion or anonymization where appropriate.
- Consider related evidence, evaluations, Proof Cards, exports, and backups.
- Avoid indefinite retention by default.
- Document any records that must be retained for legitimate legal or operational reasons.
- Verify deletion behavior through tests.

Do not claim that data has been completely erased until relevant storage locations and backups have been considered.

## 14. External AI Provider Privacy

Before sending candidate information to an external AI provider:

- Confirm that the provider is approved for the intended use.
- Review its applicable data-handling and retention terms.
- Send only the information necessary for the specific task.
- Avoid sending unnecessary names and contact information.
- Do not send API credentials or internal secrets.
- Document the external processing in the applicable privacy notice.
- Provide a deterministic local demo fallback.

Do not claim that candidate information never leaves the application unless the configured architecture actually guarantees this.

## 15. IMATS Integration Security

Before implementing the official integration:

1. Verify the official endpoint documentation.
2. Confirm the authentication method.
3. Use HTTPS where required and supported.
4. Store credentials outside source control.
5. Validate request and response schemas.
6. Apply timeouts and bounded retries.
7. Avoid sending unnecessary personal information.
8. Follow the official API's data-handling requirements.
9. Use mock responses during offline development.
10. Document whether the final demonstration uses the real integration or a mock.

Never invent credentials, endpoints, or authentication requirements.

## 16. Security Testing Checklist

- [ ] Unsupported file types are rejected.
- [ ] Oversized uploads are rejected.
- [ ] Malformed documents are handled safely.
- [ ] SQL queries use parameters.
- [ ] Secrets are absent from source control.
- [ ] Secret values are not written to logs.
- [ ] Repository URLs are validated.
- [ ] Repository discovery requires recorded candidate consent.
- [ ] Repository file retrieval requires explicit candidate selection.
- [ ] Repository code is never executed.
- [ ] Prompt-injection examples do not bypass application rules.
- [ ] Invalid AI output is rejected.
- [ ] Unauthorized users cannot access protected candidate records.
- [ ] Missing evidence is not silently converted to zero.
- [ ] Candidate deletion and retention behavior are tested.
- [ ] Demo mode runs without external credentials.

## 17. Incident Response

If a security issue is discovered:

1. Stop the affected operation if necessary.
2. Prevent further exposure or unauthorized access.
3. Revoke exposed credentials.
4. Identify affected records and components.
5. Preserve only the diagnostic information needed for investigation.
6. Fix the underlying cause.
7. Test the fix.
8. Document the incident and required follow-up actions.
9. Follow applicable notification obligations where relevant.

## 18. Implementation Status

**Current status:** Proposed security and privacy requirements.

Each safeguard must be verified against the actual implementation before being marked complete. A passing checklist does not replace a comprehensive security review.
