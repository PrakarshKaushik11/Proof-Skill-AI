# Changelog — ProofSkill AI

All notable changes to ProofSkill AI are documented in this file.

This changelog follows a simplified Keep a Changelog format. Version numbers and dates should be updated when releases are actually made.

## [Unreleased]

### Project Documentation
- Defined the project scope for evidence-based fresher skill assessment.
- Documented product requirements, intended users, and core workflows.
- Documented the proposed application architecture and data model.
- Added guidance for scoring, fairness, privacy, security, and human oversight.
- Documented the AI prompt library and expected structured outputs.
- Documented evaluation, testing, development, and operational considerations.
- Added project guidance for AI coding agents.
- Documented environment configuration using `.env.example`.
- Documented data manifest and dataset-handling expectations.

### AI Assessment Design
- Specified resume extraction requirements with evidence traceability.
- Specified adaptive technical interview generation.
- Specified project-specific viva generation.
- Specified answer evaluation using explicit scoring rubrics.
- Specified recruiter-facing explanations for candidate-to-job alignment.
- Defined handling for missing evidence, uncertain claims, and invalid model output.
- Established requirements for structured response validation.

### Fairness and Privacy
- Defined rules for distinguishing self-reported claims from verified evidence.
- Established requirements for job-relevant, explainable skill assessment.
- Documented alternative assessment paths for candidates without public repositories.
- Established safeguards against demographic inference and irrelevant personal attributes.
- Documented consent, data minimization, and secure handling of candidate information.
- Established human review as a requirement for hiring-related decisions.

### Development and Quality
- Documented expected testing scenarios and failure handling.
- Defined guidance for configurable AI providers and optional integrations.
- Documented demo-mode expectations and the distinction between synthetic and real evidence.
- Established guidelines for environment-based secrets and safe configuration.

### Implementation Status
- The items above describe documented requirements and design work.
- They do not, by themselves, establish that the corresponding application features, integrations, or tests have been implemented or verified.
- Implementation status should be updated after inspecting the codebase and running the relevant tests.

### Repository Housekeeping
- Added ignore rules for local secrets, private candidate data, Python and test artifacts, and local databases.
- Recorded that the current repository contains no application source files or automated tests.
- Replaced the task-board date placeholder with the current audit date.
- Standardized raw answer rubrics on 0–4 and distinguished them from normalized 0–100 performance scores.
- Corrected malformed Markdown headings and JSON code fences in documentation and prompts.
- Added the missing user-flow summary with implementation status clearly marked as proposed.

### GitHub Project Assessment Design
- Documented resume-based GitHub link extraction, consent-gated public repository discovery, and explicit candidate repository selection.
- Added evidence-grounded project questions and bounded code/design tasks, including candidate-submitted patch responses.
- Specified read-only access, no code execution, bounded retrieval, provenance, and an equivalent assessment path.
- Kept the workflow documented as proposed; no application integration was implemented.

## Change Entry Template

Use the following structure for future changes:

### Added
- Describe newly implemented functionality.

### Changed
- Describe changes to existing behavior or interfaces.

### Fixed
- Describe confirmed bug fixes.

### Security
- Describe relevant security or privacy improvements.

### Tests
- Describe tests added or modified and report actual execution results.

### Documentation
- Describe meaningful documentation updates.

## Release History

No formal release entries have been recorded in this changelog yet.

When a release is made, add its version, date, and verified changes above the unreleased section.
