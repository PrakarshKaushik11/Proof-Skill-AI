# Development Guide — ProofSkill AI

## 1. Overview

This guide explains how to set up, develop, test, and maintain ProofSkill AI locally.

ProofSkill AI is an AI-assisted skill assessment platform that combines candidate-provided information, project evidence, technical assessments, and job requirements to generate explainable skill profiles.

The project is designed for a hackathon prototype. Its architecture should remain modular, testable, privacy-conscious, and suitable for incremental development.

**Implementation note:** Follow the actual repository structure and installed dependencies. Documented or planned functionality must not be treated as implemented until verified in the codebase.

## 2. Prerequisites

Install the following tools:

- Python version compatible with `pyproject.toml`.
- Git for version control.
- A code editor such as Visual Studio Code.
- Internet access when installing dependencies or using external services.

Optional tools depend on the features being developed:

- GitHub credentials for authorized repository integration.
- An API key for a configured LLM provider.
- Access to the official IMATS sandbox, if its documentation and credentials are available.

Do not assume that external credentials or official datasets are available.

## 3. Repository Structure

The repository contains the following documented areas:

| Path | Purpose |
|---|---|
| `.github/` | GitHub Copilot instructions and related configuration. |
| `.agents/` | Agent-related project resources, if configured. |
| `data/` | Dataset manifest and data handling documentation. |
| `deploy/` | Deployment-related resources. |
| `docs/` | Requirements, architecture, API contracts, evaluation, and development documentation. |
| `docs/ADR/` | Architecture decision records. |
| `notebooks/` | Exploratory analysis and experiments. |
| `prompts/` | Prompt templates and prompt documentation. |
| `scripts/` | Development and maintenance scripts. |
| `src/` | Application source code. |
| `tests/` | Automated tests. |
| `.env.example` | Example environment variable names and placeholder values. |
| `pyproject.toml` | Python project metadata, dependencies, and tool configuration. |
| `README.md` | Main project overview and entry-point documentation. |
| `TASKS.md` | Implementation task tracking. |
| `CURRENT_STATE.md` | Current implementation status. |
| `HANDOFF.md` | Project handoff notes. |
| `DECISIONS.md` | Project decisions. |

This table describes the repository layout; it does not imply that every directory already contains executable code.

## 4. Local Setup

Run the following commands from the repository root.

### Windows PowerShell

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use an approved local execution policy or activate the environment from Command Prompt instead. Do not weaken system-wide security settings unnecessarily.

### Windows Command Prompt

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

### Install the project

First inspect `pyproject.toml` to confirm the project's dependency and installation configuration.

If it supports editable installation, run:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

If development dependencies are defined through an optional extra, install the extra actually declared in `pyproject.toml`. Do not assume an extra name without checking the configuration.

If editable installation is not configured, install dependencies using the project's documented method.

## 5. Environment Configuration

Use `.env.example` as the reference for required environment variables.

If the project uses a local `.env` file, create one locally and populate it with appropriate values. Never commit real credentials.

Typical configuration categories may include:

- Application environment.
- Database location.
- AI provider and model identifier.
- AI provider API key.
- GitHub integration credentials.
- External sandbox configuration.
- Request timeouts and retry limits.
- Demo mode.

These are configuration categories, not guaranteed environment variable names. Use the exact names expected by the implementation.

### Configuration rules

- Keep secrets out of source code and version control.
- Validate required configuration during application startup.
- Provide clear errors when optional integrations are unavailable.
- Avoid printing environment variables or credentials in logs.
- Keep demo mode clearly separated from production integrations.
- Do not silently substitute fabricated results for failed external requests.

## 6. Running the Application

The actual entry point must be confirmed from the files in `src/`, the root `README.md`, and `pyproject.toml`.

If the project configures a Streamlit entry point, use the actual configured file:

```bash
python -m streamlit run path/to/actual_entrypoint.py
```

Replace the placeholder with an existing application file. Do not create or assume a root-level `app.py` unless that file is part of the actual project.

If the application uses another entry point, follow its documented command instead.

## 7. Development Workflow

Use this workflow for each feature:

1. Read `PROJECT_CONTEXT.md`, `CURRENT_STATE.md`, and the relevant feature documentation.
2. Check `TASKS.md` to identify the intended scope and current status.
3. Inspect the existing source code before modifying it.
4. Define expected inputs, outputs, validation rules, and failure behavior.
5. Implement the smallest coherent change.
6. Add or update tests.
7. Run the relevant checks.
8. Update documentation if the contract or behavior changed.
9. Update the task status only after verifying the result.
10. Record significant architectural decisions in the existing decision documentation.

Avoid implementing undocumented features that expand scope without a clear reason.

## 8. Coding Standards

### Python

- Follow PEP 8 conventions.
- Use descriptive names for functions, variables, and classes.
- Add type hints to public functions where practical.
- Keep functions focused on a single responsibility.
- Separate UI logic from business rules and data access.
- Prefer explicit validation over silent coercion.
- Handle expected exceptions with actionable error messages.
- Avoid broad exception handling that hides defects.
- Use the standard logging module where logging is required.
- Keep external service calls behind clear adapter functions.

### Project structure

Place code in the existing modules under `src/` according to their responsibility.

Suggested boundaries include:

- Presentation and UI.
- Resume and document processing.
- Evidence ingestion and provenance.
- Skill extraction and semantic matching.
- Assessment and rubric evaluation.
- Profile generation.
- Recruiter comparison.
- Database access.
- AI provider integration.
- External API integration.

These are logical boundaries, not instructions to create new files or directories automatically. Reuse the existing structure wherever possible.

### Configuration

- Avoid hard-coded credentials.
- Centralize configurable values.
- Validate score scales and enum values.
- Use documented defaults for optional services.
- Keep deterministic test behavior independent of live AI services.

## 9. AI and Evidence Handling

AI-generated content must remain distinguishable from source evidence.

When developing AI-assisted features:

- Validate model outputs before using them.
- Preserve source references for extracted claims and evaluation results.
- Avoid inventing qualifications, projects, or repository activity.
- Treat uploaded documents and repository content as untrusted input.
- Do not let instructions embedded in candidate documents override trusted application instructions.
- Handle missing evidence explicitly.
- Distinguish candidate claims from assessed or independently verified capabilities.
- Use deterministic fallbacks only when they can perform the requested task safely.
- Clearly label synthetic data and demo outputs.

Embeddings and language models may assist with matching and explanations, but semantic similarity alone does not prove competence.

## 10. Privacy and Security

Before implementing data-processing features:

- Confirm the intended use of the data.
- Obtain appropriate permission for candidate documents, private repositories, and recordings.
- Collect only necessary information.
- Validate uploads and restrict file size and supported formats.
- Avoid logging sensitive content.
- Do not execute candidate-submitted code during routine evidence ingestion.
- Review external provider data-handling terms before sending candidate information.
- Protect candidate records with appropriate access controls.
- Define retention and deletion behavior for real candidate data.

See `docs/PRIVACY_AND_SECURITY.md`, `docs/SECURITY_PRIVACY.md`, and `SECURITY.md`.

## 11. Testing

Use pytest if it is configured in the project.

Run the test suite:

```bash
python -m pytest
```

Run tests with more detailed output:

```bash
python -m pytest -v
```

Run a specific existing test file:

```bash
python -m pytest path/to/existing_test_file.py -v
```

Replace the placeholder with an actual test file.

### Recommended test coverage

- Resume parsing and malformed document handling.
- Skill extraction and evidence provenance.
- Score bounds and rubric consistency.
- Missing-evidence behavior.
- Job-specific candidate comparisons.
- AI provider errors and malformed outputs.
- Authorization and access control.
- File upload validation.
- Privacy-sensitive logging.
- Deterministic demo workflows.
- External integration failures.

A test command should be reported as successful only after it has actually completed successfully.

## 12. Code Quality Checks

Inspect `pyproject.toml` for the project's configured formatters, linters, and type checkers.

If the relevant tools are installed and configured, run them using the project's declared settings.

Examples of common commands include:

```bash
python -m compileall src
```

This checks Python files for syntax and compilation errors but does not prove that the application works correctly.

For tools such as Ruff, Black, or mypy, use the commands and configurations actually declared by the project. Do not add tools solely because they appear in this guide.

## 13. Data and Dataset Workflow

Before using any dataset:

1. Review `data/README.md` and `data/MANIFEST.yaml`.
2. Confirm that the referenced files exist.
3. Check provenance and usage permissions.
4. Validate the schema and required fields.
5. Identify missing values and duplicate records.
6. Document preprocessing and limitations.
7. Keep sensitive datasets out of Git unless explicitly approved.
8. Clearly label synthetic data.

Do not assume the official hackathon dataset is available. Use synthetic fixtures for development only when clearly labeled, and do not report their results as real-world performance.

## 14. Prompt Development

Prompt templates are maintained under the existing `prompts/` directory.

When modifying a prompt:

- State the task and expected output clearly.
- Define the required output structure.
- Require evidence-grounded conclusions.
- Explain how to handle missing or contradictory evidence.
- Treat candidate-provided content as untrusted input.
- Avoid irrelevant personal characteristics.
- Test normal, incomplete, ambiguous, and adversarial inputs.
- Update relevant documentation when the prompt changes its output contract.

Prompt changes should be evaluated against representative test cases before being relied upon in assessments.

## 15. External Integrations

External services may include AI providers, GitHub, speech-to-text services, or the IMATS sandbox.

Before enabling an integration:

1. Confirm the official API documentation.
2. Validate credentials and required permissions.
3. Define request and response schemas.
4. Configure reasonable timeouts.
5. Handle rate limits and service failures.
6. Avoid logging sensitive payloads.
7. Validate external responses before storing or displaying them.
8. Provide a clear unavailable state when a service cannot be reached.

Never invent sandbox endpoints, credentials, or response formats.

## 16. Troubleshooting

### Python command not found

Verify that Python is installed and available on the system PATH.

```bash
python --version
```

If your installation uses the Python launcher on Windows, try:

```powershell
py --version
```

### Dependency installation fails

- Confirm that the virtual environment is active.
- Check the Python version required by `pyproject.toml`.
- Review the installation error and dependency constraints.
- Avoid installing arbitrary package versions without checking compatibility.

### Application entry point cannot be found

- Confirm the current working directory is the repository root.
- Inspect the existing files under `src/`.
- Check `README.md` and `pyproject.toml` for the configured entry point.
- Do not assume a file exists because a command example references it.

### AI provider is unavailable

- Check whether the integration is enabled.
- Confirm the required environment variables are configured.
- Verify network access and provider availability.
- Check timeout and rate-limit errors.
- Use a deterministic fallback only if it is appropriate for the operation.
- Do not present fallback output as a live-model result.

### Tests fail

- Read the complete error message.
- Identify whether the failure comes from application code, configuration, fixtures, or an external dependency.
- Reproduce the failure with the smallest relevant test.
- Fix the underlying issue instead of weakening assertions without justification.
- Re-run the affected tests and the broader test suite when appropriate.

## 17. Git and Change Management

Before committing a change:

- Review the diff.
- Remove debugging statements and accidental local configuration.
- Confirm that no secrets or restricted data are included.
- Run the relevant tests.
- Update documentation where behavior has changed.
- Use a descriptive commit message.

Never commit real `.env` credentials, private resumes, restricted datasets, or raw private repository content.

## 18. Definition of Done

A feature may be marked complete when:

- Its intended behavior is implemented.
- Inputs are validated.
- Expected errors are handled.
- Relevant automated tests pass.
- Privacy and security implications are addressed.
- Documentation reflects actual behavior.
- Known limitations are recorded.
- The result has been verified in the intended environment.

If a requirement is only partially implemented, record it as partial rather than complete.

## 19. Related Documentation

- `README.md` — project overview and startup instructions.
- `PROJECT_CONTEXT.md` — project goals and context.
- `CURRENT_STATE.md` — current implementation status.
- `TASKS.md` — implementation tasks.
- `HANDOFF.md` — handoff notes.
- `docs/ARCHITECTURE.md` — system architecture.
- `docs/AI_MODELS.md` — model strategy.
- `docs/API_SPEC.md` — proposed API specification.
- `docs/DATA_DICTIONARY.md` — data field definitions.
- `docs/DATASETS.md` — dataset guidance.
- `docs/SCORING_AND_FAIRNESS.md` — scoring and fairness principles.
- `docs/TESTING_AND_EVALUATION.md` — testing and evaluation.
- `docs/PRIVACY_AND_SECURITY.md` — privacy requirements.
