"""UI-facing configuration read from environment variables.

Kept separate from pages so limits are not hard-coded in presentation code.
Business configuration belongs to the backend services; this module only
exposes limits and labels the UI needs to explain itself to users.
"""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

_DEFAULT_MAX_RESUME_MB = 10.0
_DEFAULT_QUESTION_COUNT = 8


@lru_cache(maxsize=1)
def load_environment() -> None:
    """Load ``.env`` if present. Missing file is not an error."""
    load_dotenv()


def demo_mode() -> bool:
    """True when the application should run without external credentials."""
    load_environment()
    raw = os.environ.get("DEMO_MODE", "true").strip().lower()
    if raw in {"0", "false", "no", "off"}:
        return False
    if raw in {"1", "true", "yes", "on"}:
        return True
    # Unrecognised value: fall back to whether an AI credential exists.
    return not os.environ.get("AI_API_KEY", "").strip()


def max_resume_size_mb() -> float:
    load_environment()
    raw = os.environ.get("MAX_RESUME_SIZE_MB", str(_DEFAULT_MAX_RESUME_MB)).strip()
    try:
        value = float(raw)
    except ValueError:
        return _DEFAULT_MAX_RESUME_MB
    return value if value > 0 else _DEFAULT_MAX_RESUME_MB


def allowed_resume_extensions() -> tuple[str, ...]:
    load_environment()
    raw = os.environ.get("RESUME_ALLOWED_EXTENSIONS", "pdf,docx,txt")
    exts = tuple(
        part.strip().lower().lstrip(".")
        for part in raw.split(",")
        if part.strip().lstrip(".")
    )
    return exts or ("pdf", "docx", "txt")


def default_interview_questions() -> int:
    load_environment()
    raw = os.environ.get("DEFAULT_INTERVIEW_QUESTIONS", str(_DEFAULT_QUESTION_COUNT)).strip()
    try:
        value = int(raw)
    except ValueError:
        return _DEFAULT_QUESTION_COUNT
    return max(1, min(value, 50))


def resume_text_min_length() -> int:
    load_environment()
    raw = os.environ.get("RESUME_TEXT_MIN_LENGTH", "20").strip()
    try:
        value = int(raw)
    except ValueError:
        return 20
    return max(0, value)
