from __future__ import annotations

from typing import Any, Mapping

from tools import review_job_state

RAW_RESULT_KEYS = review_job_state.RAW_RESULT_KEYS


class ReviewResultParseError(review_job_state.ReviewJobValidationError):
    pass


class ReviewJobInvariantError(review_job_state.ReviewJobError):
    pass


def parse_review_result_v1(
    job: Mapping[str, Any], raw_result_text: str
) -> tuple[dict[str, Any], str, str]:
    """Parse one exact REVIEW_RESULT_V1 payload through the state boundary."""

    try:
        return review_job_state.parse_result_payload(job, raw_result_text)
    except review_job_state.ReviewJobIdentityError:
        raise
    except review_job_state.ReviewJobValidationError as exc:
        raise ReviewResultParseError(str(exc)) from exc


def capture_review_result_v1(
    job: Mapping[str, Any],
    expected_revision: int,
    observed_execution_ref: str,
    raw_result_text: str,
) -> dict[str, Any]:
    """Capture exact result bytes only for the same observed execution."""

    metadata, expected_digest, _ = parse_review_result_v1(job, raw_result_text)
    captured = review_job_state.capture_result(
        job,
        expected_revision,
        observed_execution_ref,
        raw_result_text,
    )
    if captured["result_identity"] != metadata:
        raise ReviewJobInvariantError("captured result metadata diverged from parsed bytes")
    if captured["result_sha256"] != expected_digest:
        raise ReviewJobInvariantError("captured result digest diverged from parsed bytes")
    return captured
