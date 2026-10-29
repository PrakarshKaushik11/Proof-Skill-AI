# ProofSkill AI — User Flows

**Status:** Proposed  
**Scope:** Intended candidate and recruiter workflows; not implemented in the current repository.

This document summarizes the user journeys for ProofSkill AI. Detailed requirements remain in the [PRD](./PRD.md#5-core-user-journeys); this summary is not evidence that these workflows are operational.

## Candidate Assessment

1. Provide a resume and select or review the target job requirements.
2. Review extracted claims, source references, and any GitHub profile or repository links found in the resume.
3. Decide whether to allow repository discovery for the displayed GitHub link. A link in the resume alone does not authorize network access.
4. Review eligible repositories discovered from the linked profile and select none, one, or multiple repositories.
5. Confirm the selected repositories for analysis. Only the selected repositories and bounded relevant files are inspected.
6. Choose an equivalent practical, scenario-based, or verbal assessment if discovery is declined, no suitable repository is available, or access fails.
7. Complete the role-relevant assessment, including project-grounded questions and bounded tasks where selected-repository evidence is available.
8. Explain code and design decisions, propose or submit a focused code change as a response/patch, and discuss approaches, alternatives, architecture, trade-offs, testing, and edge cases.
9. Review the Proof Card, including demonstrated performance, evidence coverage, confidence, unassessed skills, and limitations.

Resume statements remain claims unless independently assessed or verified. Missing evidence is reported as unassessed, not as proof of inability.

The system reads selected repository files as untrusted evidence. It does not execute code, push changes, or alter candidate repositories.

## Recruiter Review

1. Select the job description and its documented requirements.
2. Review candidates with available assessment results.
3. Compare candidates using the same job criteria and rubric.
4. Inspect the evidence, coverage, uncertainty, and limitations behind each result.
5. Make the hiring decision as a human reviewer.

Candidate comparisons are decision support. They must not use prohibited attributes or turn an AI score into an automatic hiring decision.

## Exceptional and Alternative Paths

- **No repository evidence:** Offer an equivalent job-relevant assessment; do not lower a score solely because a public repository is unavailable.
- **Repository link in resume:** Show the link first; require candidate consent before listing repositories and explicit selection before file analysis.
- **Private or inaccessible repository:** Do not bypass access controls. Offer the alternative assessment unless a separate least-privilege authorization flow is available.
- **Missing or conflicting evidence:** Show the gap or conflict and request further assessment or clarification rather than inventing a score.
- **Unevaluable response:** Preserve an unassessed state when the question, system, or available evidence prevents a fair evaluation.
- **Unavailable optional AI service:** Use a deterministic fallback only where implemented, and clearly label simulated results.

## Related Contracts

- [Product journeys and acceptance criteria](./PRD.md#5-core-user-journeys)
- [Scoring and fairness](./SCORING_AND_FAIRNESS.md)
- [Service contracts](./API_CONTRACTS.md)
- [Proposed API specification](./API_SPEC.md)