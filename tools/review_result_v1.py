from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from tools import review_job_state

RAW_RESULT_KEYS = {*review_job_state.RESULT_KEYS, "report"}


class ReviewResultParseError(review_job_state.ReviewJobValidationError):
    pass


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReviewResultParseError(f"duplicate REVIEW_RESULT_V1 JSON key: {key}")
        result[key] = value
    return result


def parse_review_result_v1(
    job: Mapping[str, Any], raw_result_text: str
) -> tuple[dict[str, Any], str, str]:
    """Parse one exact REVIEW_RESULT_V1 payload.

    The worker-facing payload is a single JSON object. Its structured identity,
    status and human-readable report are therefore derived from the same bytes
    that are later content-addressed. Callers must not construct result metadata
    separately from the captured worker bytes.
    """

    current = review_job_state.validate_job(job)
    if not isinstance(raw_result_text, str) or not raw_result_text:
        raise ReviewResultParseError("raw REVIEW_RESULT_V1 must be non-empty text")
    encoded = raw_result_text.encode("utf-8")
    if len(encoded) > review_job_state.MAX_RESULT_BYTES:
        raise ReviewResultParseError("raw REVIEW_RESULT_V1 exceeds size limit")

    try:
        payload = json.loads(raw_result_text, object_pairs_hook=_reject_duplicate_keys)
    except ReviewResultParseError:
        raise
    except json.JSONDecodeError as exc:
        raise ReviewResultParseError(
            f"invalid REVIEW_RESULT_V1 JSON: {exc.msg}"
        ) from exc

    if not isinstance(payload, Mapping):
        raise ReviewResultParseError("REVIEW_RESULT_V1 payload must be a JSON object")
    missing = RAW_RESULT_KEYS - set(payload)
    extra = set(payload) - RAW_RESULT_KEYS
    if missing or extra:
        raise ReviewResultParseError(
            "REVIEW_RESULT_V1 keys invalid: "
            f"missing={sorted(missing)} unexpected={sorted(extra)}"
        )

    report = payload["report"]
    if not isinstance(report, str) or not report.strip():
        raise ReviewResultParseError("REVIEW_RESULT_V1 report must be non-empty text")

    metadata = {key: payload[key] for key in review_job_state.RESULT_KEYS}
    metadata = review_job_state.validate_result_identity(current, metadata)
    digest = hashlib.sha256(encoded).hexdigest()
    return metadata, digest, report


def capture_review_result_v1(
    job: Mapping[str, Any], expected_revision: int, raw_result_text: str
) -> dict[str, Any]:
    """Safely capture result metadata only after deriving it from exact bytes."""

    metadata, expected_digest, _ = parse_review_result_v1(job, raw_result_text)
    captured = review_job_state.capture_result(
        job,
        expected_revision,
        metadata,
        raw_result_text,
    )
    if captured["result_sha256"] != expected_digest:
        raise ReviewJobInvariantError("captured result digest diverged from parsed bytes")
    return captured


class ReviewJobInvariantError(review_job_state.ReviewJobError):
    pass
