"""Binds real backend services when they exist, otherwise demo fallbacks.

Integration seam for the UI (Om) and the backend (Prakarsh):

* the backend exposes the operations named in
  :data:`proofskill.ui.services.contracts.OP_RETURN_TYPES` from a module
  importable as ``proofskill.services`` (auto-discovered), or from the module
  named by the ``PROOFSKILL_SERVICES_MODULE`` environment variable;
* a module may either expose those functions directly or provide a
  ``get_services()`` factory returning an object with them;
* whatever the backend returns is validated against the documented payload type.
  A malformed payload becomes ``INVALID_PROVIDER_OUTPUT`` — it is never shown as
  a successful result;
* anything not bound falls back to :class:`~proofskill.ui.services.demo.DemoServices`
  and is reported per operation by ``service_status()`` so the UI can label it.
"""

from __future__ import annotations

import importlib
import logging
import os
from functools import lru_cache
from typing import Any

from proofskill.ui.services.contracts import (
    OP_RETURN_TYPES,
    AssessmentServices,
    ConsentRecord,
    ContractError,
    DiscoveredRepository,
    ExtractedProfile,
    GithubLink,
    JobRequirements,
    ServiceError,
    ServiceResult,
    coerce_to,
)
from proofskill.ui.services.demo import DemoServices

logger = logging.getLogger(__name__)

MODULE_ENV_VAR = "PROOFSKILL_SERVICES_MODULE"
BACKEND_PACKAGE = "proofskill.services"
_OPERATIONS = tuple(OP_RETURN_TYPES)

_BINDING_NOTE: str | None = None


def get_binding_note() -> str | None:
    """Human-readable note about backend binding, shown on the home page."""
    return _BINDING_NOTE


@lru_cache(maxsize=8)
def _load_module(module_name: str) -> Any | None:
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        return None
    except Exception:  # noqa: BLE001 - a broken backend must not crash the UI
        logger.warning("Service module %s failed to import", module_name, exc_info=True)
        return None


def _safe_message(operation: str) -> str:
    return (
        f"The {operation.replace('_', ' ')} service is unavailable right now. "
        "Try again in a moment, or continue in demo mode."
    )


def _normalize(operation: str, raw: Any, provider_mode: str) -> ServiceResult:
    """Validate a backend response against the documented contract."""
    mode = provider_mode
    warnings: tuple[str, ...] = ()
    if isinstance(raw, ServiceResult):
        if not raw.ok:
            return raw
        mode = raw.provider_mode
        warnings = raw.warnings
        value = raw.data
    elif isinstance(raw, ServiceError):
        return ServiceResult.from_error(raw, provider_mode)  # type: ignore[arg-type]
    elif isinstance(raw, dict) and isinstance(raw.get("error"), dict):
        error = raw["error"]
        return ServiceResult.failure(
            str(error.get("code", "INVALID_PROVIDER_OUTPUT")),
            str(error.get("message", "The service reported an error.")),
            retryable=bool(error.get("retryable", False)),
            provider_mode=provider_mode,  # type: ignore[arg-type]
        )
    else:
        value = raw

    try:
        data = coerce_to(OP_RETURN_TYPES[operation], value, operation)
    except ContractError:
        logger.warning("Backend payload for %s failed contract validation", operation)
        return ServiceResult.failure(
            "INVALID_PROVIDER_OUTPUT",
            f"The {operation.replace('_', ' ')} service returned an unexpected "
            "response, so nothing was displayed. Try again, or continue in demo "
            "mode.",
            provider_mode=mode,  # type: ignore[arg-type]
        )
    return ServiceResult.success(data, provider_mode=mode, warnings=warnings)  # type: ignore[arg-type]


class BackendServices:
    """Adapts backend operations to the UI protocol, falling back per operation."""

    def __init__(self, target: Any, fallback: DemoServices) -> None:
        self._target = target
        self._fallback = fallback

    @property
    def mode(self) -> str:
        return "live" if any(self._bound()) else "demo"

    def _bound(self) -> list[str]:
        return [op for op in _OPERATIONS if callable(getattr(self._target, op, None))]

    def service_status(self) -> dict[str, str]:
        bound = set(self._bound())
        status = {op: ("backend" if op in bound else "demo") for op in _OPERATIONS}
        note = get_binding_note()
        if note:
            status["backend"] = note
        return status

    def _invoke(self, operation: str, **kwargs: Any) -> ServiceResult:
        func = getattr(self._target, operation, None)
        if not callable(func):
            return getattr(self._fallback, operation)(**kwargs)
        try:
            raw = func(**kwargs)
        except Exception:  # noqa: BLE001 - surface as a safe, explicit error
            logger.warning("Backend service %s raised", operation, exc_info=True)
            return ServiceResult.failure(
                "INTEGRATION_UNAVAILABLE",
                _safe_message(operation),
                retryable=True,
                provider_mode="live",
            )
        return _normalize(operation, raw, "live")

    # -- protocol implementation -----------------------------------------
    def extract_resume_text(
        self, filename: str, content_type: str, data: bytes, max_size_mb: float
    ) -> ServiceResult:
        return self._invoke(
            "extract_resume_text",
            filename=filename,
            content_type=content_type,
            data=data,
            max_size_mb=max_size_mb,
        )

    def extract_candidate_evidence(self, text: str) -> ServiceResult:
        return self._invoke("extract_candidate_evidence", text=text)

    def parse_job_requirements(self, job_title: str, job_description: str) -> ServiceResult:
        return self._invoke(
            "parse_job_requirements", job_title=job_title, job_description=job_description
        )

    def generate_questions(
        self,
        profile: ExtractedProfile,
        job: JobRequirements,
        max_questions: int,
        route: str,
    ) -> ServiceResult:
        return self._invoke(
            "generate_questions",
            profile=profile,
            job=job,
            max_questions=max_questions,
            route=route,
        )

    def evaluate_answer(self, question: Any, answer: str) -> ServiceResult:
        return self._invoke("evaluate_answer", question=question, answer=answer)

    def select_follow_up(
        self,
        question: Any,
        evaluation: Any,
        assessed_skills: list[str],
        budget: int,
    ) -> ServiceResult:
        return self._invoke(
            "select_follow_up",
            question=question,
            evaluation=evaluation,
            assessed_skills=assessed_skills,
            budget=budget,
        )

    def record_repository_consent(
        self, links: list[GithubLink], granted: bool, scope: str
    ) -> ServiceResult:
        return self._invoke(
            "record_repository_consent", links=links, granted=granted, scope=scope
        )

    def discover_repositories(self, link: GithubLink, consent: ConsentRecord) -> ServiceResult:
        return self._invoke("discover_repositories", link=link, consent=consent)

    def confirm_repository_scope(
        self, consent: ConsentRecord, repositories: list[DiscoveredRepository]
    ) -> ServiceResult:
        return self._invoke(
            "confirm_repository_scope", consent=consent, repositories=repositories
        )

    def generate_project_tasks(
        self, scope: Any, job: JobRequirements
    ) -> ServiceResult:
        return self._invoke("generate_project_tasks", scope=scope, job=job)

    def create_alternative_assessment(
        self, profile: ExtractedProfile, job: JobRequirements
    ) -> ServiceResult:
        return self._invoke("create_alternative_assessment", profile=profile, job=job)

    def generate_proof_card(
        self,
        job: JobRequirements,
        profile: ExtractedProfile,
        route: str,
        answer_evaluations: list[Any],
        task_evaluations: list[Any],
        scope: Any,
        candidate_id: str,
        candidate_reference: str,
    ) -> ServiceResult:
        return self._invoke(
            "generate_proof_card",
            job=job,
            profile=profile,
            route=route,
            answer_evaluations=answer_evaluations,
            task_evaluations=task_evaluations,
            scope=scope,
            candidate_id=candidate_id,
            candidate_reference=candidate_reference,
        )

    def list_jobs(self) -> ServiceResult:
        return self._invoke("list_jobs")

    def list_candidates(self, job_id: str) -> ServiceResult:
        return self._invoke("list_candidates", job_id=job_id)

    def compare_candidates(self, job_id: str, candidate_ids: list[str]) -> ServiceResult:
        return self._invoke("compare_candidates", job_id=job_id, candidate_ids=candidate_ids)


def get_services() -> AssessmentServices:
    """Resolve the service implementation for this process.

    Resolution order:

    1. the module named by ``PROOFSKILL_SERVICES_MODULE`` (explicit override);
    2. the documented ``proofskill.services`` package;
    3. clearly labelled demo services.
    """
    global _BINDING_NOTE
    explicit = os.environ.get(MODULE_ENV_VAR, "").strip()
    candidates = ([explicit] if explicit else []) + [BACKEND_PACKAGE]
    note: str | None = None
    for name in candidates:
        module = _load_module(name)
        if module is None:
            if name == explicit and explicit:
                note = (
                    f"The configured service module '{name}' could not be imported, "
                    "so demo services are in use."
                )
            continue
        target = module
        factory = getattr(module, "get_services", None)
        if callable(factory):
            try:
                target = factory() or module
            except Exception:  # noqa: BLE001
                logger.warning("get_services() from %s raised", name, exc_info=True)
                target = module
        bound = [op for op in _OPERATIONS if callable(getattr(target, op, None))]
        if not bound:
            note = (
                f"Module '{name}' exposes no supported service operations "
                f"({len(bound)}/{len(_OPERATIONS)}), so demo services are in use."
            )
            continue
        _BINDING_NOTE = None
        return BackendServices(target, DemoServices())
    _BINDING_NOTE = note
    return DemoServices(binding_note=note)
