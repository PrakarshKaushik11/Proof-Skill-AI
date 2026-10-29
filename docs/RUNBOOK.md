# Runbook — ProofSkill AI

## 1. Purpose

This runbook explains how to set up, start, operate, troubleshoot, and safely demonstrate ProofSkill AI.

ProofSkill AI helps candidates demonstrate practical skills through resumes, project evidence, technical assessments, and structured interviews. Recruiters can review evidence-backed profiles and compare candidates against job-specific criteria.

This runbook is intended for local development and hackathon demonstrations. It is not a production deployment guide.

**Important:** The procedures describe the intended workflow. Commands and features must be verified against the actual repository before being treated as operational.

## 2. System Overview

The proposed application consists of:

- A Python application and user interface.
- Resume and document processing.
- Candidate evidence management.
- Technical assessment and rubric-based evaluation.
- Evidence-backed skill profile generation.
- Job-specific recruiter comparison.
- Optional AI provider integrations.
- Optional repository and external sandbox integrations.
- SQLite persistence for the initial prototype, if configured.
- Automated tests using pytest, if configured.

Optional external services may be unavailable during a demo. The application should communicate service limitations clearly and use deterministic fallback behavior only where appropriate.

## 3. Prerequisites

Before starting, verify that you have:

- Python installed at a version supported by `pyproject.toml`.
- Git installed.
- The ProofSkill AI repository checked out locally.
- Access to install the declared project dependencies.
- Any required environment variables documented in `.env.example`.

External AI credentials, GitHub access, official datasets, and IMATS sandbox credentials are optional unless the workflow being demonstrated requires them.

Never use real candidate data in an unprotected local demo.

## 4. Start the Application

Run commands from the repository root.

### Step 1: Verify Python

Windows PowerShell:

```powershell
python --version
```

If `python` is unavailable, check whether the Windows Python launcher is installed:

```powershell
py --version
```

Use a Python version compatible with the project's declared requirements.

### Step 2: Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use an approved local execution policy or activate the environment through Command Prompt. Avoid changing system-wide security settings unnecessarily.

### Step 3: Install dependencies

Inspect `pyproject.toml` to confirm the installation method.

If editable installation is configured, run:

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
```

Install any development extras only if they are explicitly defined in the project configuration.

### Step 4: Configure the environment

Review `.env.example` and configure the variables required by the actual application.

If a local `.env` file is used, populate it with local values. Do not commit credentials or real candidate data.

Check that:

- Required configuration values are present.
- Optional AI integrations are configured only when needed.
- Demo mode is explicitly identified.
- No secret is printed to the terminal or application logs.

### Step 5: Identify the application entry point

Inspect:

- `README.md`
- `pyproject.toml`
- The existing files under `src/`
- `CURRENT_STATE.md`

If the project uses Streamlit, run the actual configured entry-point file:

```powershell
python -m streamlit run path\to\existing_entrypoint.py
```

Replace the placeholder with an existing file. Do not assume a root-level `app.py` exists.

If the project uses a different entry point, follow the command defined by the implementation.

### Step 6: Verify startup

Confirm that:

- The application starts without an unhandled exception.
- The terminal reports any required configuration errors clearly.
- The UI is accessible at the address shown by the application.
- Optional service failures are reported accurately.
- No sensitive information appears in startup logs.

Do not report the application as running until startup has been verified.

## 5. Pre-Demo Checklist

Before presenting the project:

- [ ] The application starts successfully.
- [ ] The expected environment is active.
- [ ] Required dependencies are installed.
- [ ] The selected demo data is available and clearly labeled.
- [ ] No real candidate information is exposed.
- [ ] No credentials or secrets are visible.
- [ ] The main candidate workflow has been tested.
- [ ] The assessment workflow has been tested.
- [ ] Evidence references and score explanations are visible where implemented.
- [ ] The recruiter comparison uses consistent job criteria.
- [ ] Missing evidence is handled without fabricating a score.
- [ ] External service failures have been considered.
- [ ] Relevant automated tests have been run.
- [ ] Known limitations are ready to explain.

Only check items that have actually been verified.

## 6. Recommended Demo Workflow

Use synthetic data or other explicitly authorized data.

### Candidate workflow

1. Open the application.
2. Select or create a demo candidate, if supported.
3. Upload a supported resume or enter candidate information manually.
4. Review extracted skill claims and their source evidence.
5. Add a project description or authorized repository evidence, if supported.
6. Complete a technical assessment, if implemented.
7. Review the generated skill profile and its limitations.

### Recruiter workflow

1. Select a job description.
2. Review the required skills and evaluation criteria.
3. Open the candidate profiles.
4. Compare evidence against the same job-specific rubric.
5. Review supporting evidence, missing information, and explanations.
6. Treat the results as decision support rather than an automatic hiring decision.

Do not demonstrate a feature as functional if it has not been implemented or verified.

## 7. Demo Data Rules

Before using any demo dataset:

1. Check `data/README.md`.
2. Review `data/MANIFEST.yaml`.
3. Confirm that the referenced files actually exist.
4. Confirm whether the data is synthetic, authorized real data, or restricted data.
5. Validate the expected schema.
6. Avoid exposing personal information or secrets.

Synthetic data must not be represented as official hackathon data or real recruiter decisions.

The availability of the official hackathon dataset must be verified independently.

## 8. AI Provider Operations

If an AI provider is configured, verify the following before a demo:

- The provider and model identifiers match the application configuration.
- Credentials are present without being exposed.
- A small, non-sensitive test request succeeds.
- Response validation is working.
- Timeout and failure handling behave as expected.
- The UI distinguishes live-model output from fallback output.

If the provider is unavailable:

1. Check the configured provider and model.
2. Confirm required environment variables are present.
3. Check network connectivity and provider availability.
4. Review safe error messages and rate-limit responses.
5. Use demo fallback behavior only if it is implemented and appropriate.
6. Otherwise, report the feature as unavailable.

Never fabricate a successful model result to keep a demonstration moving.

## 9. Repository Integration Operations

If GitHub integration is enabled:

- Confirm that the correct credentials and permissions are configured.
- Use only repositories the candidate has authorized for the intended workflow.
- Check API rate limits and permission errors.
- Do not expose private repository content in logs or public screens.
- Do not execute candidate-submitted code during routine evidence collection.
- Provide an alternative assessment path if repository access fails.

If a repository cannot be accessed, record the limitation and continue with another permitted evidence source where possible.

## 10. Database and Local State

If SQLite persistence is configured:

- Confirm the database location from the actual application configuration.
- Keep database files containing real candidate information out of version control.
- Restrict filesystem access appropriately.
- Avoid manually editing production or active database files.
- Back up data only when necessary and protect the backup.
- Follow the documented retention and deletion policy.

Do not delete database files as a generic troubleshooting step; doing so may permanently remove candidate records.

For a synthetic demo, use the project's approved fixture or reset procedure if one exists.

## 11. Common Troubleshooting

### Python is not recognized

Check the installation and PATH configuration.

```powershell
python --version
```

If appropriate, try:

```powershell
py --version
```

### Dependency installation fails

- Confirm that the virtual environment is active.
- Check the supported Python version.
- Inspect the error and dependency constraints in `pyproject.toml`.
- Retry only after addressing the underlying issue.

### The application entry point is missing

- Confirm the current directory is the repository root.
- Inspect the existing files in `src/`.
- Review `README.md` and `pyproject.toml`.
- Use the actual entry point rather than creating or assuming a new one.

### A resume cannot be processed

- Confirm that the format is supported.
- Check whether the file is corrupt, encrypted, or empty.
- Verify file-size limits.
- Inspect the sanitized error message.
- Avoid printing the entire document into logs for debugging.

### Skill extraction appears incorrect

- Inspect the extracted text.
- Check the source passage and extraction method.
- Distinguish a missing skill mention from missing competence.
- Add a regression test for the failure.
- Correct the extraction logic or document the limitation.

### Assessment scores are invalid

- Confirm that the expected rubric version is configured.
- Validate score boundaries and required fields.
- Verify that the response was associated with the correct question.
- Check whether the result was generated by a model or deterministic fallback.
- Do not manually change a score merely to make the demo look better.

### AI provider returns an error

- Confirm the provider configuration.
- Check credentials and network availability.
- Inspect rate-limit and timeout errors.
- Verify output schema validation.
- Use an approved fallback only when appropriate.

### Recruiter comparison is inconsistent

- Confirm that all candidates use the same job description.
- Check the rubric version and criterion weights.
- Inspect missing-evidence handling.
- Verify that explanations agree with the underlying scores.
- Add a test reproducing the inconsistency.

### Tests fail

Run the test suite:

```powershell
python -m pytest -v
```

If pytest is configured and installed:

1. Read the failure output.
2. Identify the affected component.
3. Reproduce the issue with the smallest relevant test.
4. Fix the underlying defect.
5. Re-run the affected test and broader suite as appropriate.

Do not claim that tests passed unless the command completed successfully.

## 12. Safe Shutdown

When finishing a demo or development session:

1. Stop the application using its normal shutdown procedure.
2. Confirm that no required background task is still running.
3. Close the terminal or development session as appropriate.
4. Do not leave exposed credentials in terminal history, shared logs, or screenshots.
5. Store any necessary artifacts only in approved locations.
6. Follow the project's retention policy for temporary candidate data.

Do not delete persistent records unless the relevant deletion action is intended and authorized.

## 13. Security Incident Procedure

If credentials, private candidate data, or restricted repository content are exposed:

1. Stop the affected workflow if necessary.
2. Revoke or rotate exposed credentials.
3. Identify the affected files, systems, and data.
4. Restrict further access.
5. Preserve relevant incident evidence securely.
6. Follow applicable notification and reporting requirements.
7. Document corrective actions.
8. Verify the fix before resuming the affected workflow.

Do not paste secrets or private candidate data into public issue trackers or shared debugging conversations.

## 14. Operational Status Reporting

When reporting the state of the project, distinguish between:

- **Implemented:** Corresponding code exists.
- **Tested:** Relevant checks were executed.
- **Verified:** The intended behavior was observed in the relevant environment.
- **Partially implemented:** Some functionality exists but important work remains.
- **Planned:** The functionality is documented but not confirmed as implemented.
- **Blocked:** Progress depends on an unresolved issue or external requirement.

Update `CURRENT_STATE.md` and `TASKS.md` when the actual project status changes.

## 15. Related Documentation

- `README.md` — project overview and startup instructions.
- `CURRENT_STATE.md` — verified implementation status.
- `TASKS.md` — planned and active implementation tasks.
- `HANDOFF.md` — project handoff information.
- `docs/DEVELOPMENT.md` — local development workflow.
- `docs/ARCHITECTURE.md` — system architecture.
- `docs/AI_MODELS.md` — AI provider and model strategy.
- `docs/API_SPEC.md` — proposed API contract.
- `docs/DATASETS.md` — dataset handling guidance.
- `docs/TESTING_AND_EVALUATION.md` — testing procedures.
- `docs/PRIVACY_AND_SECURITY.md` — privacy and security requirements.

## 16. Maintenance

Update this runbook when startup commands, environment variables, database configuration, external integrations, or operational procedures change.

All procedures should be verified against the actual implementation before being treated as reliable operational instructions.
