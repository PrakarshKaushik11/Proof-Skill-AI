"""Session-state schema and helpers for the ProofSkill AI Streamlit UI.

Session state holds **temporary UI workflow state only** — no business logic,
no scoring, no database access. Every key is prefixed ``psa_`` to avoid
colliding with widget state owned by other code.

Progress survives Streamlit reruns because each stage writes its result into
this schema, and restart explicitly clears it (with a confirmation step) rather
than losing data by accident.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

NOTICE_KINDS = ("info", "success", "warning", "error")

#: Keys reset by "Restart assessment". Everything else (e.g. consent flags for
#: the current session) is intentionally preserved.
RESETTABLE_KEYS: tuple[str, ...] = (
    "psa_resume_filename",
    "psa_resume_text",
    "psa_profile",
    "psa_job",
    "psa_route",
    "psa_route_locked",
    "psa_discovery_consent",
    "psa_discovery",
    "psa_discovery_failed",
    "psa_selected_repos",
    "psa_analysis_consent",
    "psa_scope",
    "psa_questions",
    "psa_question_index",
    "psa_evaluations",
    "psa_interview_done",
    "psa_tasks",
    "psa_task_index",
    "psa_task_evaluations",
    "psa_tasks_done",
    "psa_proof_card",
    "psa_candidate_id",
    "psa_candidate_reference",
)

DEFAULTS: dict[str, Any] = {
    "psa_stage": "home",
    "psa_furthest_stage": "home",
    "psa_notice": None,
    "psa_repo_selection": [],
    "psa_repo_confirm": False,
    "psa_restart_confirm": False,
    "psa_resume_filename": None,
    "psa_resume_text": None,
    "psa_profile": None,
    "psa_job": None,
    "psa_job_title": "",
    "psa_job_desc": "",
    "psa_route": None,
    "psa_route_locked": False,
    "psa_discovery_consent": None,
    "psa_discovery": None,
    "psa_discovery_failed": False,
    "psa_selected_repos": (),
    "psa_analysis_consent": None,
    "psa_scope": None,
    "psa_questions": (),
    "psa_question_budget": 8,
    "psa_question_index": 0,
    "psa_evaluations": {},
    "psa_interview_done": False,
    "psa_tasks": (),
    "psa_task_index": 0,
    "psa_task_evaluations": {},
    "psa_tasks_done": False,
    "psa_proof_card": None,
    "psa_candidate_id": "demo-candidate-self",
    "psa_candidate_reference": "CANDIDATE-SELF",
}


def init() -> None:
    """Apply defaults without overwriting anything already present."""
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)


def get(key: str, default: Any = None) -> Any:
    return st.session_state.get(key, default)


def set(key: str, value: Any) -> None:
    st.session_state[key] = value


def stage() -> str:
    return str(st.session_state.get("psa_stage", "home"))


def set_stage(key: str) -> None:
    """Navigate to a stage, clearing any notice that belonged to the old one."""
    if key != st.session_state.get("psa_stage"):
        st.session_state["psa_notice"] = None
        st.session_state["psa_restart_confirm"] = False
    st.session_state["psa_stage"] = key
    _track_progress(key)


def _track_progress(key: str) -> None:
    order = [
        "home",
        "onboarding",
        "resume",
        "profile",
        "job",
        "route",
        "github",
        "interview",
        "tasks",
        "proof_card",
    ]
    if key not in order:
        return
    current = order.index(key)
    furthest = order.index(st.session_state.get("psa_furthest_stage", "home"))
    if current > furthest:
        st.session_state["psa_furthest_stage"] = key


def set_notice(kind: str, text: str) -> None:
    """Record a message for the current stage (survives Streamlit reruns)."""
    if kind not in NOTICE_KINDS:
        kind = "info"
    st.session_state["psa_notice"] = {"kind": kind, "text": str(text), "stage": stage()}


def clear_notice() -> None:
    st.session_state["psa_notice"] = None


def current_notice() -> dict[str, Any] | None:
    """Notice belonging to the stage currently being rendered, if any."""
    notice = st.session_state.get("psa_notice")
    if isinstance(notice, dict) and notice.get("stage") == stage():
        return notice
    return None


def reset_assessment() -> None:
    """Clear assessment progress (explicit user action, never automatic)."""
    for key in RESETTABLE_KEYS:
        if key in DEFAULTS:
            st.session_state[key] = DEFAULTS[key]
        else:
            st.session_state.pop(key, None)
    st.session_state["psa_notice"] = None
    st.session_state["psa_furthest_stage"] = "home"
    st.session_state["psa_restart_confirm"] = False
    st.session_state["psa_repo_selection"] = []
    st.session_state["psa_repo_confirm"] = False
    st.session_state["psa_stage"] = "home"


def answered_questions() -> dict[str, Any]:
    return dict(st.session_state.get("psa_evaluations", {}))


def answered_task_responses() -> dict[str, Any]:
    return dict(st.session_state.get("psa_task_evaluations", {}))
