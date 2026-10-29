"""Recruiter comparison construction.

Comparison is a service-level concern (same job criteria, same rubric, excluded
ranking factors), so it lives here rather than inside a Streamlit page.
"""

from __future__ import annotations

from proofskill.ui.services.contracts import (
    ComparisonResult,
    ComparisonRow,
    JobSummary,
    ProofCard,
)


def build_comparison(
    *,
    job: JobSummary,
    cards: dict[str, ProofCard],
    candidate_ids: list[str],
) -> ComparisonResult:
    """Compare candidates for one job using identical criteria and weights."""
    criteria = tuple(job.skills) or tuple(
        s.skill_name for s in cards[candidate_ids[0]].skill_results
    )
    rows: list[ComparisonRow] = []
    for candidate_id in candidate_ids:
        card = cards[candidate_id]
        scores: dict[str, float | None] = {}
        for criterion in criteria:
            result = next(
                (s for s in card.skill_results if s.skill_name == criterion), None
            )
            if result is not None and result.status == "assessed":
                scores[criterion] = result.performance_score
            else:
                scores[criterion] = None
        unassessed = tuple(name for name, value in scores.items() if value is None)
        assessed = {name: value for name, value in scores.items() if value is not None}
        explanation = (
            f"Assessed against {len(assessed)} of {len(criteria)} criteria for "
            f"{job.title}."
        )
        if assessed:
            strongest = max(assessed, key=lambda name: assessed[name] or 0.0)
            explanation += (
                f" Strongest assessed evidence: {strongest} "
                f"({assessed[strongest]:.0f}/100)."
            )
        if unassessed:
            explanation += (
                " Not assessed: "
                + ", ".join(unassessed)
                + " — missing evidence is reported as unassessed, not as zero."
            )
        rows.append(
            ComparisonRow(
                candidate_id=candidate_id,
                reference_label=card.candidate_reference,
                scores=scores,
                unassessed=unassessed,
                evidence_coverage=card.evidence_coverage,
                score_status=card.score_status,
                explanation=explanation,
            )
        )

    warnings = [
        "Comparison is decision support for human reviewers — it is not an "
        "automatic hiring or rejection decision."
    ]
    coverages = [cards[candidate_id].evidence_coverage for candidate_id in candidate_ids]
    if coverages and max(coverages) - min(coverages) >= 20:
        warnings.append(
            f"Evidence coverage differs between candidates "
            f"({min(coverages):.0f}%-{max(coverages):.0f}%). Treat the comparison "
            "as incomplete and recommend further assessment before ranking."
        )
    limitations = (
        "Every candidate is compared against the same job criteria and rubric version.",
        "Skills without assessment evidence appear as 'not assessed', never as zero.",
        "College name, gender, age and location are excluded from ranking inputs.",
    )
    return ComparisonResult(
        job_id=job.job_id,
        job_title=job.title,
        criteria=criteria,
        rows=tuple(rows),
        rubric_version="1.0",
        warnings=tuple(warnings),
        limitations=limitations,
    )
