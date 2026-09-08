#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "bootstrap_commentary_semantic_bindings_v1"
AUTHORITY = "exact_live_identity_binding_for_claim_bearing_bootstrap_commentary"
DEFAULT_PATH = Path(__file__).resolve().parents[1] / "data" / "bootstrap-commentary-semantic-bindings.json"
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TOP_FIELDS = {"schema_version", "authority", "records"}
RECORD_FIELDS = {
    "repository",
    "pr",
    "role",
    "surface",
    "comment_id",
    "actor",
    "updated_at",
    "body_sha256",
    "pull_request_review_id",
    "in_reply_to_id",
    "original_commit_id",
}


class SemanticBindingError(RuntimeError):
    pass


def _nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise SemanticBindingError(f"{label} must be a non-empty string")
    return value


def _positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise SemanticBindingError(f"{label} must be a positive integer")
    return value


def _nullable_positive_int(value: Any, label: str) -> int | None:
    if value is None:
        return None
    return _positive_int(value, label)


def _body_sha256(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_bindings(path: Path = DEFAULT_PATH) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != TOP_FIELDS:
        raise SemanticBindingError(f"{path}: top-level shape differs")
    if raw["schema_version"] != SCHEMA_VERSION or raw["authority"] != AUTHORITY:
        raise SemanticBindingError(f"{path}: schema/authority differs")
    records = raw["records"]
    if not isinstance(records, list) or not records:
        raise SemanticBindingError(f"{path}: records must be a non-empty array")

    seen_keys: set[tuple[str, str, int]] = set()
    seen_roles: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(records, start=1):
        label = f"{path}: record {index}"
        if not isinstance(item, dict) or set(item) != RECORD_FIELDS:
            raise SemanticBindingError(f"{label}: record shape differs")
        repository = _nonempty(item["repository"], f"{label} repository")
        if repository.count("/") != 1:
            raise SemanticBindingError(f"{label}: repository must be owner/name")
        _positive_int(item["pr"], f"{label} pr")
        role = _nonempty(item["role"], f"{label} role")
        surface = item["surface"]
        if surface not in {"review_comment", "issue_comment"}:
            raise SemanticBindingError(f"{label}: unsupported surface {surface!r}")
        comment_id = _positive_int(item["comment_id"], f"{label} comment_id")
        _nonempty(item["actor"], f"{label} actor")
        _nonempty(item["updated_at"], f"{label} updated_at")
        digest = item["body_sha256"]
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise SemanticBindingError(f"{label}: body_sha256 must be lowercase SHA-256")
        review_id = _nullable_positive_int(item["pull_request_review_id"], f"{label} pull_request_review_id")
        parent_id = _nullable_positive_int(item["in_reply_to_id"], f"{label} in_reply_to_id")
        original_commit = item["original_commit_id"]
        if original_commit is not None and (
            not isinstance(original_commit, str) or not SHA40_RE.fullmatch(original_commit)
        ):
            raise SemanticBindingError(f"{label}: original_commit_id must be null or lowercase SHA")
        if surface == "issue_comment" and any(
            value is not None for value in (review_id, parent_id, original_commit)
        ):
            raise SemanticBindingError(f"{label}: issue comments cannot claim review-thread fields")

        key = (repository, surface, comment_id)
        if key in seen_keys:
            raise SemanticBindingError(f"{label}: duplicate comment binding {key}")
        if role in seen_roles:
            raise SemanticBindingError(f"{label}: duplicate role {role}")
        seen_keys.add(key)
        seen_roles.add(role)
        normalized.append(item)

    return normalized


def records_for(snapshot: dict[str, Any], path: Path = DEFAULT_PATH) -> list[dict[str, Any]]:
    repository = snapshot.get("repository")
    pr = snapshot.get("pr_number")
    return [
        item
        for item in load_bindings(path)
        if item["repository"] == repository and item["pr"] == pr
    ]


def validate_snapshot(snapshot: dict[str, Any], path: Path = DEFAULT_PATH) -> int:
    repository = snapshot.get("repository")
    pr = snapshot.get("pr_number")
    if not isinstance(repository, str) or not isinstance(pr, int) or isinstance(pr, bool):
        raise SemanticBindingError("snapshot repository/PR identity is unavailable")

    review_comments = {
        item.get("id"): item
        for item in snapshot.get("review_comments", [])
        if isinstance(item, dict) and isinstance(item.get("id"), int)
    }
    issue_comments = {
        item.get("id"): item
        for item in snapshot.get("issue_comments", [])
        if isinstance(item, dict) and isinstance(item.get("id"), int)
    }

    checked = 0
    for expected in records_for(snapshot, path):
        source = review_comments if expected["surface"] == "review_comment" else issue_comments
        live = source.get(expected["comment_id"])
        label = f"{expected['role']} {repository}#{pr} comment {expected['comment_id']}"
        if not isinstance(live, dict):
            raise SemanticBindingError(f"{label}: exact comment is absent")
        if ((live.get("user") or {}).get("login")) != expected["actor"]:
            raise SemanticBindingError(f"{label}: actor differs")
        if live.get("updated_at") != expected["updated_at"]:
            raise SemanticBindingError(f"{label}: updated_at differs")
        actual_digest = _body_sha256(live.get("body"))
        if actual_digest != expected["body_sha256"]:
            raise SemanticBindingError(
                f"{label}: body digest differs "
                f"expected={expected['body_sha256']} actual={actual_digest}"
            )

        if expected["surface"] == "review_comment":
            for field in ("pull_request_review_id", "in_reply_to_id", "original_commit_id"):
                expected_value = expected[field]
                if expected_value is not None and live.get(field) != expected_value:
                    raise SemanticBindingError(f"{label}: {field} differs")
        checked += 1
    return checked
