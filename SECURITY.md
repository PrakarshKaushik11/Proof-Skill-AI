# Security Policy — ProofSkill AI

## 1. Overview

ProofSkill AI is designed to support evidence-based skill assessment and fresher recruitment.

Because the project may process resumes, project descriptions, repository evidence, interview responses, and assessment results, security and privacy must be considered throughout development.

This policy describes supported security practices, vulnerability reporting expectations, and safeguards intended to protect application users and their data.

**Security status:** The controls described here are requirements and recommendations. Their actual implementation must be verified in the codebase.

## 2. Supported Versions

ProofSkill AI is currently under development.

| Version | Security support |
|---|---|
| Development version | Security issues should be reported and reviewed |
| Released versions | Support status must be documented for each release |

Until formal releases and support windows are established, no version should be assumed to have guaranteed security maintenance.

## 3. Reporting a Vulnerability

If you discover a security vulnerability, report it privately to the project maintainers through an available private communication channel.

Do not publish exploit details, credentials, private candidate information, or a working exploit in a public issue before the maintainers have had a reasonable opportunity to investigate.

Include the following information when safe to do so:

- A concise description of the vulnerability.
- The affected component or file.
- The potential security impact.
- Reproduction steps using synthetic or authorized test data.
- Relevant logs or screenshots with secrets and personal information removed.
- A suggested mitigation, if known.

Do not include real API keys, passwords, access tokens, private resumes, or confidential repository contents in a report.

### Reporting contact

**Security contact:** Contact the repository maintainers through the private reporting channel provided by the project owner.

A dedicated security email or private reporting URL should be published here once an official contact has been established. Do not assume that a contact address exists if one has not been provided.

### Responsible disclosure

Please:
- Give maintainers reasonable time to investigate and address the issue.
- Avoid accessing or modifying data that does not belong to you.
- Do not disrupt services or perform destructive testing.
- Do not publicly disclose sensitive details before a coordinated disclosure decision.

The project maintainers should acknowledge reports, assess severity, and communicate remediation plans when a suitable reporting channel is available.

## 4. Security Principles

### Least privilege

Grant users, application components, and external integrations only the permissions necessary for their intended tasks.

### Data minimization

Collect, transmit, and retain only the candidate information required for an authorized assessment.

### Defense in depth

Do not rely on a single safeguard. Use validation, access controls, secure configuration, error handling, and testing together.

### Secure defaults

Optional integrations should remain disabled or unavailable until configured. The application should fail safely when required credentials or services are missing.

### Transparency

Clearly distinguish synthetic demo results from real candidate evidence and verified assessment results.

## 5. Secrets and Environment Configuration

- Store credentials in environment variables or an approved secret manager.
- Use `.env.example` only for configuration names and safe placeholder values.
- Never commit real `.env` files, API keys, passwords, private tokens, or database credentials.
- Avoid placing secrets in prompts, source code, logs, screenshots, or documentation.
- Rotate exposed credentials immediately.
- Use separate credentials for development and production where applicable.
- Restrict external API tokens to the minimum permissions required.
- Review repository history if a secret is accidentally committed; deleting it from the latest commit does not guarantee removal from history.

If a secret is exposed, revoke or rotate it first. Then investigate the exposure and clean up the repository as appropriate.

## 6. Candidate Data and Privacy

Candidate information may include resumes, project descriptions, repository content, interview answers, and skill profiles.

The application should:

- Obtain appropriate consent before processing restricted data.
- Limit access to authorized users.
- Avoid storing raw resumes or audio unless necessary and authorized.
- Avoid including sensitive personal data in logs.
- Apply documented retention and deletion policies.
- Prevent one candidate's information from being exposed to another candidate.
- Restrict access to recruiter-facing information according to the application's authorization model.
- Avoid sending unnecessary candidate data to external model providers.
- Clearly disclose relevant external processing when required.

Sensitive personal attributes must not be used as proxies for technical ability.

Do not use gender, age, caste, religion, race, disability, or other protected characteristics to score job-related skills. Avoid inferring such attributes from names, photographs, voice, or other indirect signals.

## 7. File Upload Security

Resume-processing workflows must treat uploaded documents as untrusted input.

Recommended safeguards include:

- Enforce a maximum upload size.
- Allow only supported file types.
- Validate file content rather than trusting the filename or extension alone.
- Handle malformed, encrypted, or unreadable documents safely.
- Use safe file paths and prevent path traversal.
- Avoid executing uploaded files or embedded content.
- Use temporary storage carefully and remove temporary files according to the application's retention policy.
- Handle parsing failures without exposing internal stack traces to users.
- Test files with unexpected structure and oversized content.

PDF and DOCX parsing should be limited to the operations required for text extraction.

### Resume-extracted GitHub links

- Treat a GitHub URL in a resume as a candidate claim, not authorization to access the linked profile.
- Show the extracted URL and obtain consent before making a repository-discovery request.
- Require the candidate to select and confirm repositories before retrieving source files.
- Keep public repository access read-only; do not push assessment tasks or code changes to a candidate repository.
- Never execute inspected repository code or candidate-submitted patches.
- Bound repository/file counts, file sizes, response sizes, and request time.
- Offer an equivalent assessment when repository access is declined or unavailable.

## 8. AI and Prompt Injection Security

Resume text, repository files, job descriptions, and candidate answers are untrusted input.

The AI workflow should:

- Treat embedded instructions as content, not as authority over system rules.
- Never reveal API keys, hidden system instructions, or unrelated candidate data.
- Validate model-generated JSON against the expected schema.
- Verify evidence references against supplied records.
- Reject malformed or unsupported assessment results.
- Use bounded retries for recoverable failures.
- Avoid automatically executing model-generated code, SQL, shell commands, or other instructions.
- Keep access to external tools and sensitive records controlled by application-side authorization.

Prompt instructions alone are not a complete security boundary. Enforce access control, validation, and permissions in application code.

## 9. External Integrations

For AI providers, GitHub, speech transcription, and other external services:

- Use HTTPS where supported.
- Protect tokens and credentials.
- Request the minimum necessary permissions.
- Apply request timeouts and bounded retries.
- Handle rate limits and authorization failures.
- Validate response schemas.
- Avoid logging sensitive request or response bodies.
- Respect candidate consent and repository visibility.
- Do not assume that a repository's presence proves authorship.
- Do not execute repository code merely to inspect it.

External integrations must follow their actual documented API contracts. Configuration variables alone do not establish that an integration is operational or secure.

## 10. Database and Application Security

For database and application operations:

- Use parameterized SQL queries.
- Validate and normalize input.
- Apply appropriate authorization checks before reading or modifying candidate records.
- Avoid exposing internal exceptions in user-facing messages.
- Use transactions for related database changes.
- Protect stored data and database files according to the deployment environment.
- Avoid hard-coded administrative credentials.
- Keep debug mode disabled in production.
- Review dependencies for known vulnerabilities.
- Avoid unnecessary network exposure of development services.

SQLite may be suitable for a local prototype, but the application must still protect access to database files and sensitive records.

## 11. Logging and Error Handling

Logs should help diagnose operational issues without unnecessarily exposing candidate data.

Do not log:
- API keys or passwords.
- Full raw resumes without a justified need.
- Private repository contents.
- Sensitive personal information.
- Full authentication tokens.
- Confidential model inputs or outputs by default.

Recommended practices:
- Log meaningful error categories and relevant non-sensitive identifiers.
- Return understandable error messages to users.
- Keep internal exception details out of public responses.
- Avoid swallowing failures silently.
- Ensure fallback behavior does not fabricate verified evidence.

## 12. Authentication and Authorization

If the application provides user accounts or recruiter access, implement server-side authentication and authorization.

- Verify access permissions on every protected operation.
- Do not rely on hiding buttons or pages as an authorization mechanism.
- Prevent unauthorized access to candidate profiles, assessments, and repository evidence.
- Protect session and authentication tokens.
- Apply appropriate session expiration and logout behavior.
- Separate candidate and recruiter permissions where required.

If authentication is not yet implemented, do not expose sensitive candidate data through a publicly accessible deployment.

## 13. Demo Mode

Demo mode should remain safe and clearly identifiable.

- Use synthetic candidate profiles and assessment responses.
- Label simulated results as demo data.
- Never present mock results as verified candidate evidence.
- Avoid embedding real credentials in sample data.
- Do not expose real candidate records through demonstration screens.
- Keep optional external services disabled until configured.
- Ensure fallback results follow the application's expected schema.

A successful demonstration does not establish production security.

## 14. Dependency and Supply-Chain Security

- Review new dependencies before adding them.
- Prefer established packages and supported versions.
- Avoid unnecessary packages.
- Review dependency advisories periodically.
- Use controlled dependency updates.
- Test compatibility after upgrading packages.
- Do not install packages from untrusted sources.
- Investigate suspicious package behavior before use.

The dependency configuration should reflect the packages actually required by the application.

## 15. Security Testing

Test security-relevant behavior during development and before deployment.

Recommended scenarios include:

- Missing or invalid environment configuration.
- Oversized and malformed uploads.
- Unexpected file content.
- SQL injection attempts.
- Path traversal attempts.
- Unauthorized candidate-record access.
- Prompt-injection content in resumes or repository files.
- Invalid model JSON and fabricated evidence references.
- External API timeouts and rate limits.
- Secret leakage in logs or error messages.
- Missing repository consent.
- Demo-mode separation from live data.
- Dependency vulnerability checks.

Use synthetic or explicitly authorized test data. Avoid destructive testing against production systems.

Report tests as passing only after executing them and reviewing their actual results.

## 16. Deployment Checklist

Before exposing an instance beyond local development, verify:

- [ ] Debug mode is disabled.
- [ ] Secrets are stored securely.
- [ ] No credentials are committed to version control.
- [ ] Sensitive candidate records have appropriate access controls.
- [ ] File uploads are validated and size-limited.
- [ ] Database access is restricted.
- [ ] External integrations use appropriate permissions.
- [ ] Model outputs are validated before use.
- [ ] Logs do not unnecessarily expose personal information.
- [ ] Demo data is distinguishable from real data.
- [ ] Retention and deletion requirements are documented.
- [ ] Relevant security tests have been run.
- [ ] Known limitations are documented.
- [ ] The deployment has been reviewed for its intended threat model.

A checked item should reflect a verified control, not merely a planned implementation.

## 17. Scope and Limitations

This policy documents expected security practices for ProofSkill AI. It is not a certification, penetration-test report, or guarantee that the application is secure.

Actual security depends on the implementation, dependencies, deployment environment, permissions, and operational practices.

Any security issue discovered during implementation should be addressed in the relevant code and tests, with the applicable existing documentation updated afterward.

## 18. Policy Maintenance

Review this policy when:
- New data sources are introduced.
- Authentication or authorization changes.
- External integrations are added.
- Candidate-data retention changes.
- New upload or model-processing capabilities are introduced.
- A security incident or significant vulnerability is discovered.

Keep this file consistent with the actual application behavior and the project's privacy documentation.
