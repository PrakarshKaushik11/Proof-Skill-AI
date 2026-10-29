"""Service resolution for the Streamlit UI.

UI code calls :func:`get_services` and never talks to AI providers, scoring
routines or the database directly.
"""

from proofskill.ui.services.contracts import (
    OP_RETURN_TYPES,
    AssessmentServices,
    ServiceError,
    ServiceResult,
)
from proofskill.ui.services.provider import (
    MODULE_ENV_VAR,
    get_binding_note,
    get_services,
)

__all__ = [
    "MODULE_ENV_VAR",
    "OP_RETURN_TYPES",
    "AssessmentServices",
    "ServiceError",
    "ServiceResult",
    "get_binding_note",
    "get_services",
]
