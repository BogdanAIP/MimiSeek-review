from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any, Mapping

SCHEMA = "REVIEW_JOB_V1"
RESULT_SCHEMA = "REVIEW_RESULT_V1"
MAX_RESULT_BYTES = 1_000_000

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
CODE = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")
JOB_ID = re.compile(r"^rj_[0-9a-f]{32}$")
GITHUB_REF = re.compile(r"^https://(?:github\.com|api\.github\.com)/")

IDENTITY_FIELDS = (
    "repository_id",
    "repository",
    "pr_number",
    "base_sha",
    "head_sha",
    "review_policy_ref",
    "reviewer_profile",
    "reviewer_source",
    "review_context",
    "review_mode",
    "request_ref",
    "executor_source",
    "launch_capability_ref",
    "return_capability_ref",
)

MUTABLE_FIELDS = (
    "state",
    "revision",
    "launch_claim_id",
    "external_execution_sha256",
    "result_identity",
    "result_sha256",
    "publication_claim_id",
    "result_ref",
    "return_delivery_id",
    "return_receipt_ref",
    "outcome",
    "outcome_code",
)

PUBLIC_KEYS = {"schema", "job_id", *IDENTITY_FIELDS, "identity_sha256", *MUTABLE_FIELDS}

RESULT_KEYS = {
    "schema",
    "job_id",
    "repository",
    "pr_number",
    "base_sha",
    "head_sha",
    "review_policy_ref",
    "reviewer_profile",
    "reviewer_source",
    "review_context",
    "review_mode",
    "validity",
    "status",
    "reported_findings",
}
RAW_RESULT_KEYS = {*RESULT_KEYS, "report"}

LIVE_KEYS = {
    "repository_id",
    "repository",
    "pr_number",
    "base_sha",
    "head_sha",
    "state",
    "draft",
    "merged",
}

STATES = {
    "REQUESTED",
    "VALIDATED",
    "LAUNCH_CLAIMED",
    "LAUNCH_UNKNOWN",
    "REVIEWING",
    "RESULT_RECEIVED",
    "RESULT_VALIDATED",
    "PUBLICATION_CLAIMED",
    "PUBLICATION_UNKNOWN",
    "RESULT_PERSISTED",
    "RETURN_PENDING",
    "RETURN_UNKNOWN",
    "RETURN_DELIVERED",
    "DONE",
}

OUTCOMES = {None, "PASS", "FINDINGS", "STALE", "ABSTAIN", "FAILED"}


class ReviewJobError(RuntimeError):
    pass


class ReviewJobValidationError(ReviewJobError):
    pass


class ReviewJobIdentityError(ReviewJobError):
    pass


class ReviewJobConflictError(ReviewJobError):
    pass


class ReviewJobTransitionError(ReviewJobError):
    pass


class ReviewJobRevisionConflict(ReviewJobError):
    pass


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    missing = expected - set(value)
    extra = set(value) - expected
    if missing or extra:
        raise ReviewJobValidationError(
            f"{label} keys invalid: missing={sorted(missing)} unexpected={sorted(extra)}"
        )


def _positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ReviewJobValidationError(f"{label} must be a positive integer")
    return value


def _nonnegative_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ReviewJobValidationError(f"{label} must be a non-negative integer")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ReviewJobValidationError(f"{label} must be a non-empty string")
    return value


def _match(value: Any, pattern: re.Pattern[str], label: str) -> str:
    value = _string(value, label)
    if not pattern.fullmatch(value):
        raise ReviewJobValidationError(f"{label} has invalid format")
    return value


def _github_ref(value: Any, label: str) -> str:
    value = _string(value, label)
    if not GITHUB_REF.match(value):
        raise ReviewJobValidationError(f"{label} must be a GitHub-owned durable locator")
    return value


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def derive_identity_sha256(fields: Mapping[str, Any]) -> str:
    return _digest_text(_canonical({name: fields[name] for name in IDENTITY_FIELDS}))


def derive_job_id(fields: Mapping[str, Any]) -> str:
    return "rj_" + derive_identity_sha256(fields)[:32]


def fingerprint_external_reference(value: str) -> str:
    value = _string(value, "external reference")
    if len(value.encode("utf-8")) > 4096:
        raise ReviewJobValidationError("external reference is too large")
    return _digest_text(value)


def _validate_identity(record: Mapping[str, Any]) -> None:
    _positive_int(record["repository_id"], "repository_id")
    _match(record["repository"], REPOSITORY, "repository")
    _positive_int(record["pr_number"], "pr_number")
    for name in (
        "base_sha",
        "head_sha",
        "review_policy_ref",
        "launch_capability_ref",
        "return_capability_ref",
    ):
        _match(record[name], SHA40, name)
    for name in ("reviewer_profile", "reviewer_source", "review_context", "review_mode"):
        _match(record[name], TOKEN, name)
    _github_ref(record["request_ref"], "request_ref")
    _match(record["executor_source"], REPOSITORY, "executor_source")


def validate_result_identity(job: Mapping[str, Any], value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ReviewJobValidationError("result_identity must be an object")
    _exact_keys(value, RESULT_KEYS, "result_identity")
    result = dict(value)
    if result["schema"] != RESULT_SCHEMA:
        raise ReviewJobValidationError("result_identity schema must be REVIEW_RESULT_V1")
    if result["job_id"] != job["job_id"]:
        raise ReviewJobIdentityError("result job_id does not match review job")
    for name in (
        "repository",
        "pr_number",
        "base_sha",
        "head_sha",
        "review_policy_ref",
        "reviewer_profile",
        "reviewer_source",
        "review_context",
        "review_mode",
    ):
        if result[name] != job[name]:
            raise ReviewJobIdentityError(f"result {name} does not match review job")
    findings = _nonnegative_int(result["reported_findings"], "reported_findings")
    validity = result["validity"]
    status = result["status"]
    if validity not in {"CURRENT", "STALE", "ABSTAIN"}:
        raise ReviewJobValidationError("invalid result validity")
    if status not in {"PASS", "FINDINGS", "ABSTAIN"}:
        raise ReviewJobValidationError("invalid result status")
    if status == "PASS" and findings != 0:
        raise ReviewJobValidationError("PASS result must report zero findings")
    if status == "FINDINGS" and findings < 1:
        raise ReviewJobValidationError("FINDINGS result must report at least one finding")
    if status == "ABSTAIN" and findings != 0:
        raise ReviewJobValidationError("ABSTAIN result must report zero findings")
    if validity == "CURRENT" and status == "ABSTAIN":
        raise ReviewJobValidationError("CURRENT result cannot have ABSTAIN status")
    if validity == "ABSTAIN" and status != "ABSTAIN":
        raise ReviewJobValidationError("ABSTAIN validity requires ABSTAIN status")
    return result


def parse_result_payload(
    job: Mapping[str, Any], raw_result_text: str
) -> tuple[dict[str, Any], str, str]:
    """Derive reviewer metadata, digest, and report from one exact payload."""

    current = validate_job(job)
    raw_result_text = _string(raw_result_text, "raw_result_text")
    encoded = raw_result_text.encode("utf-8")
    if len(encoded) > MAX_RESULT_BYTES:
        raise ReviewJobValidationError("raw result exceeds size limit")
    try:
        payload = json.loads(raw_result_text, object_pairs_hook=_reject_duplicate_keys)
    except ReviewJobValidationError:
        raise
    except json.JSONDecodeError as exc:
        raise ReviewJobValidationError(f"invalid REVIEW_RESULT_V1 JSON: {exc.msg}") from exc
    if not isinstance(payload, Mapping):
        raise ReviewJobValidationError("REVIEW_RESULT_V1 payload must be a JSON object")
    _exact_keys(payload, RAW_RESULT_KEYS, "REVIEW_RESULT_V1")
    report = payload["report"]
    if not isinstance(report, str) or not report.strip():
        raise ReviewJobValidationError("REVIEW_RESULT_V1 report must be non-empty text")
    metadata = {key: payload[key] for key in RESULT_KEYS}
    metadata = validate_result_identity(current, metadata)
    return metadata, hashlib.sha256(encoded).hexdigest(), report


def _validate_live(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ReviewJobValidationError("live identity must be an object")
    _exact_keys(value, LIVE_KEYS, "live identity")
    live = dict(value)
    _positive_int(live["repository_id"], "live repository_id")
    _match(live["repository"], REPOSITORY, "live repository")
    _positive_int(live["pr_number"], "live pr_number")
    _match(live["base_sha"], SHA40, "live base_sha")
    _match(live["head_sha"], SHA40, "live head_sha")
    if live["state"] not in {"open", "closed"}:
        raise ReviewJobValidationError("live state must be open or closed")
    if not isinstance(live["draft"], bool) or not isinstance(live["merged"], bool):
        raise ReviewJobValidationError("live draft/merged must be booleans")
    return live


def _same_object(job: Mapping[str, Any], live: Mapping[str, Any]) -> None:
    for name in ("repository_id", "repository", "pr_number"):
        if job[name] != live[name]:
            raise ReviewJobIdentityError(f"live {name} does not match review job")


def is_live_identity_current(job: Mapping[str, Any], live: Mapping[str, Any]) -> bool:
    live = _validate_live(live)
    _same_object(job, live)
    return (
        live["base_sha"] == job["base_sha"]
        and live["head_sha"] == job["head_sha"]
        and live["state"] == "open"
        and not live["draft"]
        and not live["merged"]
    )


def create_job(**identity: Any) -> dict[str, Any]:
    if set(identity) != set(IDENTITY_FIELDS):
        raise ReviewJobValidationError("create_job requires the exact REVIEW_JOB_V1 identity fields")
    _validate_identity(identity)
    identity_sha256 = derive_identity_sha256(identity)
    record = {
        "schema": SCHEMA,
        "job_id": "rj_" + identity_sha256[:32],
        **identity,
        "identity_sha256": identity_sha256,
        "state": "REQUESTED",
        "revision": 0,
        "launch_claim_id": None,
        "external_execution_sha256": None,
        "result_identity": None,
        "result_sha256": None,
        "publication_claim_id": None,
        "result_ref": None,
        "return_delivery_id": None,
        "return_receipt_ref": None,
        "outcome": None,
        "outcome_code": None,
    }
    return validate_job(record)


def validate_job(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ReviewJobValidationError("review job must be an object")
    _exact_keys(value, PUBLIC_KEYS, "review job")
    job = copy.deepcopy(dict(value))
    if job["schema"] != SCHEMA:
        raise ReviewJobValidationError("schema must be REVIEW_JOB_V1")
    _validate_identity(job)
    identity_sha = derive_identity_sha256(job)
    if job["identity_sha256"] != identity_sha:
        raise ReviewJobIdentityError("identity_sha256 does not match immutable job identity")
    if job["job_id"] != "rj_" + identity_sha[:32]:
        raise ReviewJobIdentityError("job_id does not match immutable job identity")
    _match(job["job_id"], JOB_ID, "job_id")
    _nonnegative_int(job["revision"], "revision")
    if job["state"] not in STATES:
        raise ReviewJobValidationError("unknown review-job state")
    if job["outcome"] not in OUTCOMES:
        raise ReviewJobValidationError("unknown review-job outcome")

    for name in ("launch_claim_id", "publication_claim_id", "return_delivery_id"):
        if job[name] is not None:
            _match(job[name], TOKEN, name)
    for name in ("external_execution_sha256", "result_sha256"):
        if job[name] is not None:
            _match(job[name], SHA256, name)
    for name in ("result_ref", "return_receipt_ref"):
        if job[name] is not None:
            _github_ref(job[name], name)
    if job["outcome_code"] is not None:
        _match(job["outcome_code"], CODE, "outcome_code")
    if job["result_identity"] is not None:
        job["result_identity"] = validate_result_identity(job, job["result_identity"])

    if (job["result_identity"] is None) != (job["result_sha256"] is None):
        raise ReviewJobValidationError("reviewer result identity and digest must be present together")
    if job["result_identity"] is not None:
        if job["launch_claim_id"] is None or job["external_execution_sha256"] is None:
            raise ReviewJobValidationError(
                "captured reviewer result requires launch and external execution provenance"
            )

    state = job["state"]
    before_result = {"REQUESTED", "VALIDATED", "LAUNCH_CLAIMED", "LAUNCH_UNKNOWN", "REVIEWING"}
    if state in before_result:
        if any(
            job[name] is not None
            for name in (
                "result_identity",
                "result_sha256",
                "publication_claim_id",
                "result_ref",
                "return_delivery_id",
                "return_receipt_ref",
                "outcome",
                "outcome_code",
            )
        ):
            raise ReviewJobValidationError(f"{state} contains premature result/publication/return state")
    if state == "RESULT_RECEIVED":
        if job["result_identity"] is None or job["result_sha256"] is None:
            raise ReviewJobValidationError("RESULT_RECEIVED requires captured result identity and digest")
        if any(
            job[name] is not None
            for name in (
                "publication_claim_id",
                "result_ref",
                "return_delivery_id",
                "return_receipt_ref",
                "outcome",
                "outcome_code",
            )
        ):
            raise ReviewJobValidationError("RESULT_RECEIVED contains premature classified/publication state")

    post_result = {
        "RESULT_VALIDATED",
        "PUBLICATION_CLAIMED",
        "PUBLICATION_UNKNOWN",
        "RESULT_PERSISTED",
        "RETURN_PENDING",
        "RETURN_UNKNOWN",
        "RETURN_DELIVERED",
        "DONE",
    }
    if state in post_result and job["outcome"] is None:
        raise ReviewJobValidationError(f"{state} requires an explicit outcome")
    if job["outcome"] in {"STALE", "ABSTAIN", "FAILED"} and job["outcome_code"] is None:
        raise ReviewJobValidationError(f"{job['outcome']} outcome requires outcome_code")
    if job["outcome"] in {None, "PASS", "FINDINGS"} and job["outcome_code"] is not None:
        raise ReviewJobValidationError("outcome_code is reserved for STALE, ABSTAIN, or FAILED")

    if state in {"LAUNCH_CLAIMED", "LAUNCH_UNKNOWN", "REVIEWING", "RESULT_RECEIVED"} and job["launch_claim_id"] is None:
        raise ReviewJobValidationError(f"{state} requires launch_claim_id")
    if state in {"REVIEWING", "RESULT_RECEIVED"} and job["external_execution_sha256"] is None:
        raise ReviewJobValidationError(f"{state} requires external_execution_sha256")

    if state in post_result and job["outcome"] not in {"FAILED", "STALE"}:
        if job["result_identity"] is None or job["result_sha256"] is None:
            raise ReviewJobValidationError(f"{state} requires captured result identity and digest")
    if job["outcome"] == "STALE" and (
        (job["result_identity"] is None) != (job["result_sha256"] is None)
    ):
        raise ReviewJobValidationError("STALE outcome must have both result identity/digest or neither")

    if state in {
        "PUBLICATION_CLAIMED",
        "PUBLICATION_UNKNOWN",
        "RESULT_PERSISTED",
        "RETURN_PENDING",
        "RETURN_UNKNOWN",
        "RETURN_DELIVERED",
        "DONE",
    }:
        if job["publication_claim_id"] is None:
            raise ReviewJobValidationError(f"{state} requires publication_claim_id")
    if state in {"RESULT_VALIDATED", "PUBLICATION_CLAIMED", "PUBLICATION_UNKNOWN"} and job["result_ref"] is not None:
        raise ReviewJobValidationError(f"{state} cannot contain result_ref before publication is proven")
    if state in {"RESULT_PERSISTED", "RETURN_PENDING", "RETURN_UNKNOWN", "RETURN_DELIVERED", "DONE"}:
        if job["result_ref"] is None:
            raise ReviewJobValidationError(f"{state} requires result_ref")
    if state in {"RETURN_PENDING", "RETURN_UNKNOWN", "RETURN_DELIVERED", "DONE"}:
        if job["return_delivery_id"] is None:
            raise ReviewJobValidationError(f"{state} requires return_delivery_id")
    if state in {"RETURN_DELIVERED", "DONE"}:
        if job["return_receipt_ref"] is None:
            raise ReviewJobValidationError(f"{state} requires return_receipt_ref")
    elif job["return_receipt_ref"] is not None:
        raise ReviewJobValidationError(f"{state} cannot contain a return receipt before delivery is proven")
    return job


def serialize_job(value: Mapping[str, Any]) -> str:
    return _canonical(validate_job(value)) + "\n"


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReviewJobValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def deserialize_job(text: str) -> dict[str, Any]:
    if not isinstance(text, str) or not text:
        raise ReviewJobValidationError("serialized review job must be non-empty text")
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except ReviewJobValidationError:
        raise
    except json.JSONDecodeError as exc:
        raise ReviewJobValidationError(f"invalid review-job JSON: {exc.msg}") from exc
    return validate_job(value)


def _mutate(value: Mapping[str, Any], expected_revision: int, fn) -> dict[str, Any]:
    current = validate_job(value)
    if current["revision"] != expected_revision:
        raise ReviewJobRevisionConflict(
            f"expected revision {expected_revision}, found {current['revision']}"
        )
    draft = copy.deepcopy(current)
    if not fn(draft):
        return current
    draft["revision"] += 1
    return validate_job(draft)


def _state(job: Mapping[str, Any], allowed: set[str], action: str) -> None:
    if job["state"] not in allowed:
        raise ReviewJobTransitionError(f"{action} not allowed from state {job['state']}")


def _same_id(existing: str | None, requested: str, label: str) -> None:
    if existing is not None and existing != requested:
        raise ReviewJobConflictError(f"{label} already bound to a different id")


def _stale(draft: dict[str, Any], code: str) -> None:
    draft["outcome"] = "STALE"
    draft["outcome_code"] = code
    draft["state"] = "RESULT_VALIDATED"


def validate_request(
    value: Mapping[str, Any], expected_revision: int, live: Mapping[str, Any]
) -> dict[str, Any]:
    live = _validate_live(live)

    def apply(job: dict[str, Any]) -> bool:
        _state(job, {"REQUESTED", "VALIDATED", "RESULT_VALIDATED"}, "validate_request")
        _same_object(job, live)
        current = is_live_identity_current(job, live)
        if job["state"] == "RESULT_VALIDATED":
            if job["outcome"] == "STALE" and not current:
                return False
            raise ReviewJobTransitionError("validate_request cannot replace an existing outcome")
        if not current:
            _stale(job, "SOURCE_IDENTITY_NOT_CURRENT")
            return True
        if job["state"] == "VALIDATED":
            return False
        job["state"] = "VALIDATED"
        return True

    return _mutate(value, expected_revision, apply)


def claim_launch(
    value: Mapping[str, Any],
    expected_revision: int,
    claim_id: str,
    live: Mapping[str, Any],
) -> dict[str, Any]:
    claim_id = _match(claim_id, TOKEN, "launch_claim_id")
    live = _validate_live(live)

    def apply(job: dict[str, Any]) -> bool:
        _state(job, {"VALIDATED", "LAUNCH_CLAIMED"}, "claim_launch")
        _same_id(job["launch_claim_id"], claim_id, "launch")
        if job["state"] == "LAUNCH_CLAIMED":
            return False
        _same_object(job, live)
        if not is_live_identity_current(job, live):
            _stale(job, "SOURCE_IDENTITY_MOVED_BEFORE_LAUNCH")
            return True
        job["launch_claim_id"] = claim_id
        job["state"] = "LAUNCH_CLAIMED"
        return True

    return _mutate(value, expected_revision, apply)


def mark_launch_unknown(
    value: Mapping[str, Any], expected_revision: int, claim_id: str
) -> dict[str, Any]:
    claim_id = _match(claim_id, TOKEN, "launch_claim_id")

    def apply(job: dict[str, Any]) -> bool:
        _state(job, {"LAUNCH_CLAIMED", "LAUNCH_UNKNOWN"}, "mark_launch_unknown")
        if job["launch_claim_id"] != claim_id:
            raise ReviewJobConflictError("launch claim id mismatch")
        if job["state"] == "LAUNCH_UNKNOWN":
            return False
        job["state"] = "LAUNCH_UNKNOWN"
        return True

    return _mutate(value, expected_revision, apply)


def mark_reviewing(
    value: Mapping[str, Any],
    expected_revision: int,
    claim_id: str,
    external_execution_ref: str,
) -> dict[str, Any]:
    claim_id = _match(claim_id, TOKEN, "launch_claim_id")
    execution_sha = fingerprint_external_reference(external_execution_ref)

    def apply(job: dict[str, Any]) -> bool:
        _state(job, {"LAUNCH_CLAIMED", "LAUNCH_UNKNOWN", "REVIEWING"}, "mark_reviewing")
        if job["launch_claim_id"] != claim_id:
            raise ReviewJobConflictError("launch claim id mismatch")
        if job["external_execution_sha256"] not in {None, execution_sha}:
            raise ReviewJobConflictError("external execution correlation conflicts")
        if job["state"] == "REVIEWING":
            return False
        job["external_execution_sha256"] = execution_sha
        job["state"] = "REVIEWING"
        return True

    return _mutate(value, expected_revision, apply)


def resolve_launch_absent(
    value: Mapping[str, Any], expected_revision: int, claim_id: str
) -> dict[str, Any]:
    claim_id = _match(claim_id, TOKEN, "launch_claim_id")

    def apply(job: dict[str, Any]) -> bool:
        _state(job, {"LAUNCH_UNKNOWN"}, "resolve_launch_absent")
        if job["launch_claim_id"] != claim_id or job["external_execution_sha256"] is not None:
            raise ReviewJobConflictError("launch cannot be proven absent")
        job["state"] = "VALIDATED"
        return True

    return _mutate(value, expected_revision, apply)


def capture_result(
    value: Mapping[str, Any],
    expected_revision: int,
    raw_result_text: str,
) -> dict[str, Any]:
    current = validate_job(value)
    result, digest, _ = parse_result_payload(current, raw_result_text)

    def apply(job: dict[str, Any]) -> bool:
        _state(job, {"REVIEWING", "RESULT_RECEIVED"}, "capture_result")
        if job["result_identity"] is not None:
            if job["result_identity"] != result or job["result_sha256"] != digest:
                raise ReviewJobConflictError("conflicting repeated result for immutable review job")
            return False
        job["result_identity"] = result
        job["result_sha256"] = digest
        job["state"] = "RESULT_RECEIVED"
        return True

    return _mutate(current, expected_revision, apply)


def validate_captured_result(
    value: Mapping[str, Any], expected_revision: int, live: Mapping[str, Any]
) -> dict[str, Any]:
    live = _validate_live(live)

    def apply(job: dict[str, Any]) -> bool:
        _state(job, {"RESULT_RECEIVED", "RESULT_VALIDATED"}, "validate_captured_result")
        if job["state"] == "RESULT_VALIDATED":
            return False
        _same_object(job, live)
        result = job["result_identity"]
        if result["validity"] == "ABSTAIN":
            job["outcome"], job["outcome_code"] = "ABSTAIN", "REVIEWER_ABSTAIN"
        elif result["validity"] == "STALE":
            job["outcome"], job["outcome_code"] = "STALE", "REVIEWER_REPORTED_STALE"
        elif not is_live_identity_current(job, live):
            job["outcome"], job["outcome_code"] = (
                "STALE",
                "SOURCE_IDENTITY_MOVED_AFTER_RESULT",
            )
        else:
            job["outcome"] = result["status"]
        job["state"] = "RESULT_VALIDATED"
        return True

    return _mutate(value, expected_revision, apply)


def set_failure_outcome(
    value: Mapping[str, Any], expected_revision: int, code: str
) -> dict[str, Any]:
    code = _match(code, CODE, "failure_code")

    def apply(job: dict[str, Any]) -> bool:
        if job["state"] in {
            "PUBLICATION_CLAIMED",
            "PUBLICATION_UNKNOWN",
            "RESULT_PERSISTED",
            "RETURN_PENDING",
            "RETURN_UNKNOWN",
            "RETURN_DELIVERED",
            "DONE",
        }:
            raise ReviewJobTransitionError("cannot replace a publication-bound outcome")
        if job["state"] == "RESULT_VALIDATED":
            if job["outcome"] == "FAILED" and job["outcome_code"] == code:
                return False
            raise ReviewJobConflictError("job already has a different validated outcome")
        job["outcome"], job["outcome_code"], job["state"] = (
            "FAILED",
            code,
            "RESULT_VALIDATED",
        )
        return True

    return _mutate(value, expected_revision, apply)


def claim_publication(
    value: Mapping[str, Any],
    expected_revision: int,
    claim_id: str,
    live: Mapping[str, Any],
) -> dict[str, Any]:
    claim_id = _match(claim_id, TOKEN, "publication_claim_id")
    live = _validate_live(live)

    def apply(job: dict[str, Any]) -> bool:
        _state(job, {"RESULT_VALIDATED", "PUBLICATION_CLAIMED"}, "claim_publication")
        _same_id(job["publication_claim_id"], claim_id, "publication")
        if job["state"] == "PUBLICATION_CLAIMED":
            return False
        _same_object(job, live)
        if job["outcome"] in {"PASS", "FINDINGS"} and not is_live_identity_current(job, live):
            job["outcome"], job["outcome_code"] = (
                "STALE",
                "SOURCE_IDENTITY_MOVED_BEFORE_PUBLICATION",
            )
        job["publication_claim_id"], job["state"] = claim_id, "PUBLICATION_CLAIMED"
        return True

    return _mutate(value, expected_revision, apply)


def mark_publication_unknown(
    value: Mapping[str, Any], expected_revision: int, claim_id: str
) -> dict[str, Any]:
    claim_id = _match(claim_id, TOKEN, "publication_claim_id")

    def apply(job: dict[str, Any]) -> bool:
        _state(job, {"PUBLICATION_CLAIMED", "PUBLICATION_UNKNOWN"}, "mark_publication_unknown")
        if job["publication_claim_id"] != claim_id:
            raise ReviewJobConflictError("publication claim id mismatch")
        if job["state"] == "PUBLICATION_UNKNOWN":
            return False
        job["state"] = "PUBLICATION_UNKNOWN"
        return True

    return _mutate(value, expected_revision, apply)


def record_publication(
    value: Mapping[str, Any],
    expected_revision: int,
    claim_id: str,
    result_ref: str,
    observed_result_sha256: str | None = None,
) -> dict[str, Any]:
    claim_id = _match(claim_id, TOKEN, "publication_claim_id")
    result_ref = _github_ref(result_ref, "result_ref")
    if observed_result_sha256 is not None:
        observed_result_sha256 = _match(
            observed_result_sha256, SHA256, "observed_result_sha256"
        )

    def apply(job: dict[str, Any]) -> bool:
        _state(
            job,
            {"PUBLICATION_CLAIMED", "PUBLICATION_UNKNOWN", "RESULT_PERSISTED"},
            "record_publication",
        )
        if job["publication_claim_id"] != claim_id:
            raise ReviewJobConflictError("publication claim id mismatch")
        if job["result_sha256"] is not None:
            if observed_result_sha256 != job["result_sha256"]:
                raise ReviewJobConflictError(
                    "published result digest does not match captured result"
                )
        elif observed_result_sha256 is not None:
            raise ReviewJobValidationError(
                "digest must be omitted when no reviewer result was captured"
            )
        if job["state"] == "RESULT_PERSISTED":
            if job["result_ref"] != result_ref:
                raise ReviewJobConflictError("result already persisted at a different locator")
            return False
        job["result_ref"], job["state"] = result_ref, "RESULT_PERSISTED"
        return True

    return _mutate(value, expected_revision, apply)


def resolve_publication_absent(
    value: Mapping[str, Any], expected_revision: int, claim_id: str
) -> dict[str, Any]:
    claim_id = _match(claim_id, TOKEN, "publication_claim_id")

    def apply(job: dict[str, Any]) -> bool:
        _state(job, {"PUBLICATION_UNKNOWN"}, "resolve_publication_absent")
        if job["publication_claim_id"] != claim_id or job["result_ref"] is not None:
            raise ReviewJobConflictError("publication cannot be proven absent")
        job["state"] = "RESULT_VALIDATED"
        return True

    return _mutate(value, expected_revision, apply)


def claim_return_delivery(
    value: Mapping[str, Any],
    expected_revision: int,
    delivery_id: str,
    live: Mapping[str, Any],
) -> dict[str, Any]:
    delivery_id = _match(delivery_id, TOKEN, "return_delivery_id")
    live = _validate_live(live)

    def apply(job: dict[str, Any]) -> bool:
        _state(job, {"RESULT_PERSISTED", "RETURN_PENDING"}, "claim_return_delivery")
        _same_id(job["return_delivery_id"], delivery_id, "return delivery")
        if job["state"] == "RETURN_PENDING":
            return False
        _same_object(job, live)
        if job["outcome"] in {"PASS", "FINDINGS"} and not is_live_identity_current(job, live):
            job["outcome"], job["outcome_code"] = (
                "STALE",
                "SOURCE_IDENTITY_MOVED_BEFORE_RETURN",
            )
        job["return_delivery_id"], job["state"] = delivery_id, "RETURN_PENDING"
        return True

    return _mutate(value, expected_revision, apply)


def mark_return_unknown(
    value: Mapping[str, Any], expected_revision: int, delivery_id: str
) -> dict[str, Any]:
    delivery_id = _match(delivery_id, TOKEN, "return_delivery_id")

    def apply(job: dict[str, Any]) -> bool:
        _state(job, {"RETURN_PENDING", "RETURN_UNKNOWN"}, "mark_return_unknown")
        if job["return_delivery_id"] != delivery_id:
            raise ReviewJobConflictError("return delivery id mismatch")
        if job["state"] == "RETURN_UNKNOWN":
            return False
        job["state"] = "RETURN_UNKNOWN"
        return True

    return _mutate(value, expected_revision, apply)


def record_return_delivered(
    value: Mapping[str, Any],
    expected_revision: int,
    delivery_id: str,
    receipt_ref: str,
) -> dict[str, Any]:
    delivery_id = _match(delivery_id, TOKEN, "return_delivery_id")
    receipt_ref = _github_ref(receipt_ref, "receipt_ref")

    def apply(job: dict[str, Any]) -> bool:
        _state(
            job,
            {"RETURN_PENDING", "RETURN_UNKNOWN", "RETURN_DELIVERED"},
            "record_return_delivered",
        )
        if job["return_delivery_id"] != delivery_id:
            raise ReviewJobConflictError("return delivery id mismatch")
        if job["state"] == "RETURN_DELIVERED":
            if job["return_receipt_ref"] != receipt_ref:
                raise ReviewJobConflictError("return already delivered with a different receipt")
            return False
        job["return_receipt_ref"], job["state"] = receipt_ref, "RETURN_DELIVERED"
        return True

    return _mutate(value, expected_revision, apply)


def resolve_return_absent(
    value: Mapping[str, Any], expected_revision: int, delivery_id: str
) -> dict[str, Any]:
    delivery_id = _match(delivery_id, TOKEN, "return_delivery_id")

    def apply(job: dict[str, Any]) -> bool:
        _state(job, {"RETURN_UNKNOWN"}, "resolve_return_absent")
        if job["return_delivery_id"] != delivery_id or job["return_receipt_ref"] is not None:
            raise ReviewJobConflictError("return delivery cannot be proven absent")
        job["state"] = "RESULT_PERSISTED"
        return True

    return _mutate(value, expected_revision, apply)


def complete_job(value: Mapping[str, Any], expected_revision: int) -> dict[str, Any]:
    def apply(job: dict[str, Any]) -> bool:
        _state(job, {"RETURN_DELIVERED", "DONE"}, "complete_job")
        if job["state"] == "DONE":
            return False
        job["state"] = "DONE"
        return True

    return _mutate(value, expected_revision, apply)
