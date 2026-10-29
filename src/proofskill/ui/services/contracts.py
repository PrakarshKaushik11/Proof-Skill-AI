"""Typed service contracts consumed by the ProofSkill AI Streamlit UI.

This module is the only vocabulary the UI layer speaks. It mirrors the
structures documented in ``docs/API_CONTRACTS.md``:

* the UI never calls AI providers, scoring functions or SQL directly;
* every service call returns a :class:`ServiceResult` that is either a validated
  success or an explicit, user-safe :class:`ServiceError` — never a fake success;
* backend implementations may return these dataclasses directly, or plain
  dictionaries that are coerced by :func:`coerce_to` (malformed output becomes
  ``INVALID_PROVIDER_OUTPUT``).

Statuses, scores and verification labels here are the single source of truth for
the labels rendered by the UI.
"""

from __future__ import annotations

from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from typing import Any, Literal, Protocol, Union, get_args, get_origin, get_type_hints, runtime_checkable

ProviderMode = Literal["demo", "live", "mock"]

#: Verification labels used across the product. The UI maps these to readable
#: copy such as "Claimed from resume" or "Not assessed".
VerificationStatus = Literal[
    "candidate_claim",
    "assessed",
    "verified_evidence",
    "not_assessed",
    "unavailable",
]
EvidenceConfidence = Literal["low", "medium", "high", "not_assessed"]
SkillStatus = Literal["assessed", "not_assessed"]

# Error codes from docs/API_CONTRACTS.md section 2.
ERROR_CODES = (
    "INVALID_INPUT",
    "UNSUPPORTED_FILE",
    "EXTRACTION_FAILED",
    "NOT_FOUND",
    "CONSENT_REQUIRED",
    "PROVIDER_UNAVAILABLE",
    "INVALID_PROVIDER_OUTPUT",
    "INTEGRATION_UNAVAILABLE",
    "ASSESSMENT_INCOMPLETE",
)


class ContractError(ValueError):
    """Raised when a backend payload does not match the documented contract."""


@dataclass(frozen=True)
class ServiceError:
    """A safe, user-presentable service failure."""

    code: str
    message: str
    retryable: bool = False


@dataclass(frozen=True)
class ServiceResult:
    """Uniform wrapper for every UI-facing service call."""

    ok: bool
    data: Any = None
    error: ServiceError | None = None
    provider_mode: ProviderMode = "demo"
    warnings: tuple[str, ...] = ()

    @classmethod
    def success(
        cls,
        data: Any,
        provider_mode: ProviderMode = "demo",
        warnings: tuple[str, ...] | list[str] = (),
    ) -> ServiceResult:
        return cls(
            ok=True,
            data=data,
            provider_mode=provider_mode,
            warnings=tuple(warnings),
        )

    @classmethod
    def failure(
        cls,
        code: str,
        message: str,
        retryable: bool = False,
        provider_mode: ProviderMode = "demo",
        warnings: tuple[str, ...] | list[str] = (),
    ) -> ServiceResult:
        return cls(
            ok=False,
            error=ServiceError(code=code, message=message, retryable=retryable),
            provider_mode=provider_mode,
            warnings=tuple(warnings),
        )

    @classmethod
    def from_error(
        cls,
        error: ServiceError,
        provider_mode: ProviderMode = "demo",
    ) -> ServiceResult:
        return cls(ok=False, error=error, provider_mode=provider_mode)

    @property
    def message(self) -> str:
        """User-safe message for this result ("" when successful)."""
        if self.error is None:
            return ""
        return self.error.message


# --------------------------------------------------------------------------
# Evidence and resume structures
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class EvidenceRef:
    """A pointer back to the source that supports a claim or answer."""

    source_type: str  # resume | repository | answer | job_description | assessment
    skill_name: str
    source_id: str | None = None
    excerpt: str | None = None


@dataclass(frozen=True)
class SkillClaim:
    skill_name: str
    status: VerificationStatus = "candidate_claim"
    evidence: tuple[EvidenceRef, ...] = ()


@dataclass(frozen=True)
class ProjectClaim:
    name: str
    description: str = ""
    technologies: tuple[str, ...] = ()
    evidence_excerpt: str | None = None
    link: str | None = None


@dataclass(frozen=True)
class GithubLink:
    url: str
    link_type: Literal["profile", "repository"]
    account: str
    repo: str | None = None
    verification_status: VerificationStatus = "candidate_claim"


@dataclass(frozen=True)
class ExtractedProfile:
    """Structured claims extracted from a resume. Nothing here is verified."""

    skills: tuple[SkillClaim, ...] = ()
    projects: tuple[ProjectClaim, ...] = ()
    technologies: tuple[str, ...] = ()
    github_links: tuple[GithubLink, ...] = ()
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResumeExtraction:
    text: str
    content_type: str
    filename: str = ""
    warnings: tuple[str, ...] = ()


# --------------------------------------------------------------------------
# Job requirements
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class SkillRequirement:
    skill_name: str
    weight: float
    required: bool = True


@dataclass(frozen=True)
class JobRequirements:
    job_title: str
    requirements: tuple[SkillRequirement, ...] = ()
    job_id: str | None = None
    description: str = ""
    warnings: tuple[str, ...] = ()


# --------------------------------------------------------------------------
# Interview
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Question:
    id: str
    skill_name: str
    question_text: str
    question_type: str = "technical"
    difficulty: str = "beginner"
    weight: float = 1.0
    evidence: tuple[EvidenceRef, ...] = ()
    context: str | None = None
    #: Used only for evaluation. Never rendered to the candidate.
    expected_concepts: tuple[str, ...] = ()
    is_follow_up: bool = False
    source: str = "role_based"
    allow_skip: bool = True
    time_limit_seconds: int | None = None


@dataclass(frozen=True)
class AnswerEvaluation:
    """A validated 0-4 rubric evaluation returned by the evaluation service."""

    status: Literal["assessed", "not_assessed"] = "assessed"
    skill_name: str = ""
    score: int | None = None
    max_score: int = 4
    score_scale: str = "0-4"
    explanation: str = ""
    strengths: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    evidence_references: tuple[str, ...] = ()
    evidence_confidence: EvidenceConfidence = "medium"
    communication_score: float | None = None
    communication_note: str | None = None
    rubric_version: str = "1.0"
    provider_mode: ProviderMode = "demo"

    def __post_init__(self) -> None:
        if self.score is not None and not 0 <= self.score <= self.max_score:
            raise ContractError(
                f"score {self.score} is outside the 0-{self.max_score} rubric range"
            )
        if self.communication_score is not None and not 0 <= self.communication_score <= 4:
            raise ContractError(
                f"communication_score {self.communication_score} is outside 0-4"
            )


@dataclass(frozen=True)
class FollowUp:
    action: Literal["ask_follow_up", "assess_next_skill", "finish"] = "assess_next_skill"
    skill_name: str = ""
    reason: str = ""
    question: Question | None = None


# --------------------------------------------------------------------------
# GitHub consent, discovery and repository scope
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ConsentRecord:
    consent_id: str
    scope: str  # repository_discovery | repository_analysis
    granted: bool
    purpose: str = ""
    recorded_at: str = ""


@dataclass(frozen=True)
class DiscoveredRepository:
    full_name: str
    html_url: str
    description: str = ""
    language: str = ""
    visibility: str = "public"
    updated_at: str = ""


@dataclass(frozen=True)
class DiscoveryResult:
    account: str
    source_url: str = ""
    repositories: tuple[DiscoveredRepository, ...] = ()
    selection_required: bool = True
    consent_id: str | None = None
    limitations: tuple[str, ...] = ()
    provider_mode: ProviderMode = "demo"


@dataclass(frozen=True)
class RepositoryFinding:
    repository: str
    summary: str
    file_paths: tuple[str, ...] = ()
    language: str | None = None


@dataclass(frozen=True)
class RepositoryScope:
    """The confirmed, candidate-selected analysis scope."""

    consent_id: str
    repositories: tuple[DiscoveredRepository, ...] = ()
    findings: tuple[RepositoryFinding, ...] = ()
    file_count: int = 0
    limitations: tuple[str, ...] = ()
    provider_mode: ProviderMode = "demo"


# --------------------------------------------------------------------------
# Assessment tasks (project viva / code tasks / alternative path)
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class AssessmentTask:
    id: str
    task_type: str
    prompt: str
    skill_name: str
    difficulty: str = "intermediate"
    weight: float = 1.0
    evidence: tuple[EvidenceRef, ...] = ()
    file_refs: tuple[str, ...] = ()
    code_excerpt: str | None = None
    response_kind: Literal["text", "patch"] = "text"
    context: str | None = None
    expected_concepts: tuple[str, ...] = ()
    allow_skip: bool = True


# --------------------------------------------------------------------------
# Proof Card
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class SkillResult:
    skill_name: str
    performance_score: float | None
    evidence_coverage: float
    evidence_confidence: EvidenceConfidence
    status: SkillStatus
    evidence: tuple[EvidenceRef, ...] = ()
    explanation: str | None = None
    question_count: int = 0

    def __post_init__(self) -> None:
        if self.performance_score is not None and not 0 <= self.performance_score <= 100:
            raise ContractError(
                f"performance_score {self.performance_score} is outside 0-100"
            )
        if not 0 <= self.evidence_coverage <= 100:
            raise ContractError(f"evidence_coverage {self.evidence_coverage} is outside 0-100")


@dataclass(frozen=True)
class CommunicationAssessment:
    status: SkillStatus = "not_assessed"
    score: float | None = None
    scale: str = "0-100"
    explanation: str | None = None


@dataclass(frozen=True)
class ProofCard:
    candidate_id: str
    candidate_reference: str
    job_id: str | None
    job_title: str
    assessment_route: str
    performance_score: float | None
    score_status: Literal["complete", "provisional", "not_assessed"]
    skill_results: tuple[SkillResult, ...] = ()
    communication: CommunicationAssessment = field(default_factory=CommunicationAssessment)
    evidence_coverage: float = 0.0
    score_scale: str = "0-100"
    strengths: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    unassessed_skills: tuple[str, ...] = ()
    claims_not_assessed: tuple[str, ...] = ()
    recommended_follow_ups: tuple[str, ...] = ()
    evidence: tuple[EvidenceRef, ...] = ()
    rubric_version: str = "1.0"
    provider_mode: ProviderMode = "demo"
    provenance: dict[str, Any] = field(default_factory=dict)
    generated_at: str = ""
    is_demo: bool = True


# --------------------------------------------------------------------------
# Recruiter structures
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class JobSummary:
    job_id: str
    title: str
    skills: tuple[str, ...] = ()
    description: str = ""


@dataclass(frozen=True)
class CandidateSummary:
    candidate_id: str
    reference_label: str
    job_id: str
    job_title: str
    status: str = "completed"
    proof_card: ProofCard | None = None
    provider_mode: ProviderMode = "demo"


@dataclass(frozen=True)
class ComparisonRow:
    candidate_id: str
    reference_label: str
    scores: dict[str, float | None]
    unassessed: tuple[str, ...] = ()
    evidence_coverage: float = 0.0
    score_status: str = "provisional"
    explanation: str = ""


@dataclass(frozen=True)
class ComparisonResult:
    job_id: str
    job_title: str
    criteria: tuple[str, ...]
    rows: tuple[ComparisonRow, ...] = ()
    rubric_version: str = "1.0"
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


# --------------------------------------------------------------------------
# The service protocol implemented by the backend and by demo fallbacks
# --------------------------------------------------------------------------


@runtime_checkable
class AssessmentServices(Protocol):
    """Stable interface between the Streamlit UI and the application services."""

    @property
    def mode(self) -> ProviderMode:
        """Overall execution mode shown in the UI (``demo`` or ``live``)."""

    def service_status(self) -> dict[str, str]:
        """Per-operation source, e.g. ``{"extract_resume_text": "backend"}``."""

    def extract_resume_text(
        self, filename: str, content_type: str, data: bytes, max_size_mb: float
    ) -> ServiceResult: ...

    def extract_candidate_evidence(self, text: str) -> ServiceResult: ...

    def parse_job_requirements(self, job_title: str, job_description: str) -> ServiceResult: ...

    def generate_questions(
        self,
        profile: ExtractedProfile,
        job: JobRequirements,
        max_questions: int,
        route: str,
    ) -> ServiceResult: ...

    def evaluate_answer(self, question: Question, answer: str) -> ServiceResult: ...

    def select_follow_up(
        self,
        question: Question,
        evaluation: AnswerEvaluation,
        assessed_skills: list[str],
        budget: int,
    ) -> ServiceResult: ...

    def record_repository_consent(
        self, links: list[GithubLink], granted: bool, scope: str
    ) -> ServiceResult: ...

    def discover_repositories(self, link: GithubLink, consent: ConsentRecord) -> ServiceResult: ...

    def confirm_repository_scope(
        self, consent: ConsentRecord, repositories: list[DiscoveredRepository]
    ) -> ServiceResult: ...

    def generate_project_tasks(
        self, scope: RepositoryScope, job: JobRequirements
    ) -> ServiceResult: ...

    def create_alternative_assessment(
        self, profile: ExtractedProfile, job: JobRequirements
    ) -> ServiceResult: ...

    def generate_proof_card(
        self,
        job: JobRequirements,
        profile: ExtractedProfile,
        route: str,
        answer_evaluations: list[AnswerEvaluation],
        task_evaluations: list[AnswerEvaluation],
        scope: RepositoryScope | None,
        candidate_id: str,
        candidate_reference: str,
    ) -> ServiceResult: ...

    def list_jobs(self) -> ServiceResult: ...

    def list_candidates(self, job_id: str) -> ServiceResult: ...

    def compare_candidates(self, job_id: str, candidate_ids: list[str]) -> ServiceResult: ...


#: Maps every protocol operation to the payload type a successful result must
#: carry. Used to validate/coerce backend responses (see ``provider.py``).
OP_RETURN_TYPES: dict[str, Any] = {
    "extract_resume_text": ResumeExtraction,
    "extract_candidate_evidence": ExtractedProfile,
    "parse_job_requirements": JobRequirements,
    "generate_questions": tuple[Question, ...],
    "evaluate_answer": AnswerEvaluation,
    "select_follow_up": FollowUp,
    "record_repository_consent": ConsentRecord,
    "discover_repositories": DiscoveryResult,
    "confirm_repository_scope": RepositoryScope,
    "generate_project_tasks": tuple[AssessmentTask, ...],
    "create_alternative_assessment": tuple[AssessmentTask, ...],
    "generate_proof_card": ProofCard,
    "list_jobs": tuple[JobSummary, ...],
    "list_candidates": tuple[CandidateSummary, ...],
    "compare_candidates": ComparisonResult,
}


def _coerce_value(value: Any, annotation: Any, path: str) -> Any:
    """Coerce a raw backend value into ``annotation`` or raise :class:`ContractError`."""
    if annotation is Any:
        return value

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union:
        non_none = [a for a in args if a is not type(None)]
        if value is None:
            if type(None) in args:
                return None
            raise ContractError(f"{path}: null is not allowed")
        if len(non_none) == 1:
            return _coerce_value(value, non_none[0], path)
        for candidate in non_none:
            try:
                return _coerce_value(value, candidate, path)
            except ContractError:
                continue
        raise ContractError(f"{path}: value does not match any allowed type")

    if origin in (tuple, list):
        if not isinstance(value, (list, tuple)):
            raise ContractError(f"{path}: expected a list, got {type(value).__name__}")
        item_type = args[0] if args else Any
        items = tuple(_coerce_value(v, item_type, f"{path}[{i}]") for i, v in enumerate(value))
        return items if origin is tuple else list(items)

    if origin is Literal:
        if value not in args:
            raise ContractError(f"{path}: {value!r} is not one of {args}")
        return value

    if isinstance(annotation, type) and is_dataclass(annotation):
        if isinstance(value, annotation):
            return value
        if not isinstance(value, dict):
            raise ContractError(f"{path}: expected an object, got {type(value).__name__}")
        return dataclass_from_dict(annotation, value, path=path)

    if annotation is float:
        if isinstance(value, bool) or not isinstance(value, (int, float, str)):
            raise ContractError(f"{path}: expected a number, got {type(value).__name__}")
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise ContractError(f"{path}: {value!r} is not a number") from exc

    if annotation is int:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ContractError(f"{path}: expected an integer, got {type(value).__name__}")
        return int(value)

    if annotation is bool:
        if not isinstance(value, bool):
            raise ContractError(f"{path}: expected a boolean, got {type(value).__name__}")
        return value

    if annotation is str:
        if not isinstance(value, str):
            raise ContractError(f"{path}: expected a string, got {type(value).__name__}")
        return value

    return value


def dataclass_from_dict(cls: type, data: dict[str, Any], path: str = "") -> Any:
    """Build ``cls`` from a dictionary, validating every documented field."""
    if not isinstance(data, dict):
        raise ContractError(f"{path or cls.__name__}: expected an object")
    hints = get_type_hints(cls)
    known = {f.name: f for f in fields(cls)}
    kwargs: dict[str, Any] = {}
    root = path or cls.__name__
    for name, hint in hints.items():
        if name not in known:
            continue
        if name in data:
            kwargs[name] = _coerce_value(data[name], hint, f"{root}.{name}")
        elif known[name].default is not MISSING or known[name].default_factory is not MISSING:
            continue
        else:
            raise ContractError(f"{root}: missing required field {name!r}")
    return cls(**kwargs)


def coerce_to(expected: Any, value: Any, operation: str) -> Any:
    """Validate/coerce a backend success payload into its documented type."""
    if isinstance(expected, type) and is_dataclass(expected) and isinstance(value, dict):
        return dataclass_from_dict(expected, value, path=operation)
    coerced = _coerce_value(value, expected, operation)
    if expected in (tuple, list) or get_origin(expected) in (tuple, list):
        return tuple(coerced) if get_origin(expected) is tuple else coerced
    return coerced
