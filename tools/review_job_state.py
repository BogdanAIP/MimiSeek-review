from __future__ import annotations

from typing import Any, Mapping

from tools import _review_job_state_core as _core
from tools._review_job_state_core import *  # noqa: F401,F403


def capture_result(
    value: Mapping[str, Any],
    expected_revision: int,
    observed_execution_ref: str,
    raw_result_text: str,
) -> dict[str, Any]:
    """Capture one result only when it is correlated to the bound execution.

    ``observed_execution_ref`` is transport/private correlation evidence from the
    same result delivery. Only its SHA-256 fingerprint is compared; the raw
    capability/reference is never persisted in the public REVIEW_JOB_V1 record.
    """

    if not isinstance(observed_execution_ref, str):
        raise TypeError("observed_execution_ref must be a string")
    current = validate_job(value)
    observed_execution_sha256 = fingerprint_external_reference(observed_execution_ref)
    if current["external_execution_sha256"] is None:
        raise ReviewJobValidationError(
            "result capture requires a previously correlated external execution"
        )
    if current["external_execution_sha256"] != observed_execution_sha256:
        raise ReviewJobConflictError(
            "result external execution correlation does not match review job"
        )
    return _core.capture_result(
        current,
        expected_revision,
        raw_result_text,
    )


def set_failure_outcome(
    value: Mapping[str, Any], expected_revision: int, code: str
) -> dict[str, Any]:
    """Set a generic failure only before any launch attempt is unresolved/active.

    Once launch has been claimed, become ambiguous, or resolved to a concrete
    execution, failure must be represented by a separately evidenced execution
    reconciliation path. Generic failure cannot bypass the launch fence.
    """

    current = validate_job(value)
    if current["state"] not in {"REQUESTED", "VALIDATED", "RESULT_VALIDATED"}:
        raise ReviewJobTransitionError(
            "generic failure cannot bypass launch/execution reconciliation"
        )
    return _core.set_failure_outcome(current, expected_revision, code)
