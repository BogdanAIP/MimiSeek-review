#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "bootstrap_commentary_semantic_bindings_v2"
AUTHORITY = "exact_live_identity_binding_for_claim_bearing_bootstrap_commentary"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "data" / "bootstrap-commentary-semantic-bindings.json"
AUTHORITY_CI_PATH = "data/bootstrap-commentary-authority-ci-reconciliation.json"
CODEX_LOGIN = "chatgpt-codex-connector[bot]"
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TOP_FIELDS = {"schema_version", "authority", "direct_records", "delegated_records"}
DIRECT_FIELDS = {
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
DELEGATED_FIELDS = {"role", "owner_path", "finding_id", "party"}
EXPECTED_DOCS = {
    "base": "data/bootstrap-commentary-reconciliation.json",
    "rereview": "data/bootstrap-commentary-rereview-reconciliation.json",
    "fix": "data/bootstrap-commentary-fix-evidence-reconciliation.json",
    "baseline": "data/bootstrap-commentary-fix-baseline-reconciliation.json",
    "progression": "data/bootstrap-commentary-multi-review-progression-reconciliation.json",
    "authority_ci": AUTHORITY_CI_PATH,
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


def _read_json(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SemanticBindingError(f"{path}: cannot load canonical JSON") from exc
    if not isinstance(raw, dict):
        raise SemanticBindingError(f"{path}: canonical JSON must be an object")
    return raw


def _normalize_direct(item: Any, label: str) -> dict[str, Any]:
    if not isinstance(item, dict) or set(item) != DIRECT_FIELDS:
        raise SemanticBindingError(f"{label}: direct record shape differs")
    repository = _nonempty(item["repository"], f"{label} repository")
    if repository.count("/") != 1:
        raise SemanticBindingError(f"{label}: repository must be owner/name")
    pr = _positive_int(item["pr"], f"{label} pr")
    role = _nonempty(item["role"], f"{label} role")
    surface = item["surface"]
    if surface not in {"review_comment", "issue_comment"}:
        raise SemanticBindingError(f"{label}: unsupported surface {surface!r}")
    comment_id = _positive_int(item["comment_id"], f"{label} comment_id")
    actor = _nonempty(item["actor"], f"{label} actor")
    updated_at = _nonempty(item["updated_at"], f"{label} updated_at")
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
    return {
        "repository": repository,
        "pr": pr,
        "role": role,
        "surface": surface,
        "comment_id": comment_id,
        "actor": actor,
        "actor_source": "literal",
        "updated_at": updated_at,
        "body_sha256": digest,
        "pull_request_review_id": review_id,
        "in_reply_to_id": parent_id,
        "original_commit_id": original_commit,
        "binding_owner": "direct_registry",
    }


def _normalize_delegated(item: Any, label: str) -> dict[str, str]:
    if not isinstance(item, dict) or set(item) != DELEGATED_FIELDS:
        raise SemanticBindingError(f"{label}: delegated record shape differs")
    role = _nonempty(item["role"], f"{label} role")
    owner_path = _nonempty(item["owner_path"], f"{label} owner_path")
    finding_id = _nonempty(item["finding_id"], f"{label} finding_id")
    party = item["party"]
    if owner_path != AUTHORITY_CI_PATH:
        raise SemanticBindingError(f"{label}: unsupported delegated owner {owner_path!r}")
    if finding_id not in {"F055", "F056"}:
        raise SemanticBindingError(f"{label}: unsupported delegated finding {finding_id!r}")
    if party not in {"finding", "owner_reply"}:
        raise SemanticBindingError(f"{label}: unsupported delegated party {party!r}")
    expected_role = f"{finding_id}_{'FINDING' if party == 'finding' else 'OWNER_REPLY'}"
    if role != expected_role:
        raise SemanticBindingError(f"{label}: delegated role differs from owner identity")
    return {
        "role": role,
        "owner_path": owner_path,
        "finding_id": finding_id,
        "party": party,
    }


def load_manifest(path: Path = DEFAULT_PATH) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SemanticBindingError(f"{path}: cannot load semantic-binding registry") from exc
    if not isinstance(raw, dict) or set(raw) != TOP_FIELDS:
        raise SemanticBindingError(f"{path}: top-level shape differs")
    if raw["schema_version"] != SCHEMA_VERSION or raw["authority"] != AUTHORITY:
        raise SemanticBindingError(f"{path}: schema/authority differs")
    direct = raw["direct_records"]
    delegated = raw["delegated_records"]
    if not isinstance(direct, list) or not direct:
        raise SemanticBindingError(f"{path}: direct_records must be a non-empty array")
    if not isinstance(delegated, list) or not delegated:
        raise SemanticBindingError(f"{path}: delegated_records must be a non-empty array")
    direct_records = [_normalize_direct(item, f"{path}: direct record {i}") for i, item in enumerate(direct, 1)]
    delegated_records = [_normalize_delegated(item, f"{path}: delegated record {i}") for i, item in enumerate(delegated, 1)]
    return {"direct_records": direct_records, "delegated_records": delegated_records}


def _authority_ci_entries(root: Path) -> dict[str, dict[str, Any]]:
    doc = _read_json(root, AUTHORITY_CI_PATH)
    entries = doc.get("entries")
    if not isinstance(entries, list):
        raise SemanticBindingError(f"{AUTHORITY_CI_PATH}: entries must be an array")
    result: dict[str, dict[str, Any]] = {}
    for item in entries:
        if not isinstance(item, dict):
            raise SemanticBindingError(f"{AUTHORITY_CI_PATH}: entry must be an object")
        fid = item.get("finding_id")
        if fid in result:
            raise SemanticBindingError(f"{AUTHORITY_CI_PATH}: duplicate finding {fid!r}")
        if isinstance(fid, str):
            result[fid] = item
    return result


def _delegated_effective(spec: dict[str, str], root: Path) -> dict[str, Any]:
    entry = _authority_ci_entries(root).get(spec["finding_id"])
    if not isinstance(entry, dict):
        raise SemanticBindingError(f"{spec['role']}: canonical delegated owner entry is absent")
    repository = _nonempty(entry.get("repository"), f"{spec['role']} owner repository")
    pr = _positive_int(entry.get("pr"), f"{spec['role']} owner pr")
    reviewed_head = entry.get("reviewed_head")
    if not isinstance(reviewed_head, str) or not SHA40_RE.fullmatch(reviewed_head):
        raise SemanticBindingError(f"{spec['role']}: owner reviewed_head is invalid")
    gh = entry.get("github_evidence")
    if not isinstance(gh, dict):
        raise SemanticBindingError(f"{spec['role']}: canonical delegated github_evidence is absent")
    if spec["party"] == "finding":
        comment_id = _positive_int(gh.get("codex_review_comment_id"), f"{spec['role']} comment_id")
        review_id = _positive_int(gh.get("codex_review_id"), f"{spec['role']} review_id")
        updated_at = _nonempty(gh.get("codex_review_comment_updated_at"), f"{spec['role']} updated_at")
        digest = gh.get("codex_review_comment_body_sha256")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise SemanticBindingError(f"{spec['role']}: canonical body digest is invalid")
        return {
            "repository": repository,
            "pr": pr,
            "role": spec["role"],
            "surface": "review_comment",
            "comment_id": comment_id,
            "actor": CODEX_LOGIN,
            "actor_source": "literal",
            "updated_at": updated_at,
            "body_sha256": digest,
            "pull_request_review_id": review_id,
            "in_reply_to_id": None,
            "original_commit_id": reviewed_head,
            "binding_owner": AUTHORITY_CI_PATH,
        }

    finding_id = _positive_int(gh.get("codex_review_comment_id"), f"{spec['role']} parent comment_id")
    comment_id = _positive_int(gh.get("owner_reply_comment_id"), f"{spec['role']} comment_id")
    updated_at = _nonempty(gh.get("owner_reply_updated_at"), f"{spec['role']} updated_at")
    digest = gh.get("owner_reply_body_sha256")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        raise SemanticBindingError(f"{spec['role']}: canonical owner-reply digest is invalid")
    return {
        "repository": repository,
        "pr": pr,
        "role": spec["role"],
        "surface": "review_comment",
        "comment_id": comment_id,
        "actor": None,
        "actor_source": "pr_owner",
        "updated_at": updated_at,
        "body_sha256": digest,
        "pull_request_review_id": None,
        "in_reply_to_id": finding_id,
        "original_commit_id": reviewed_head,
        "binding_owner": AUTHORITY_CI_PATH,
    }


def effective_bindings(path: Path = DEFAULT_PATH, root: Path = ROOT) -> list[dict[str, Any]]:
    manifest = load_manifest(path)
    records = list(manifest["direct_records"])
    records.extend(_delegated_effective(spec, root) for spec in manifest["delegated_records"])
    seen_keys: set[tuple[str, str, int, str, int]] = set()
    seen_roles: set[str] = set()
    for record in records:
        key = binding_key(record)
        if key in seen_keys:
            raise SemanticBindingError(f"duplicate effective semantic binding {key}")
        if record["role"] in seen_roles:
            raise SemanticBindingError(f"duplicate effective semantic-binding role {record['role']}")
        seen_keys.add(key)
        seen_roles.add(record["role"])
    return records


def binding_key(record: dict[str, Any]) -> tuple[str, str, int, str, int]:
    return (
        str(record["role"]),
        str(record["repository"]),
        int(record["pr"]),
        str(record["surface"]),
        int(record["comment_id"]),
    )


def expected_inventory(root: Path = ROOT) -> set[tuple[str, str, int, str, int]]:
    expected: set[tuple[str, str, int, str, int]] = set()

    def add(role: str, repository: Any, pr: Any, surface: str, comment_id: Any) -> None:
        repository = _nonempty(repository, f"{role} expected repository")
        pr = _positive_int(pr, f"{role} expected pr")
        comment_id = _positive_int(comment_id, f"{role} expected comment_id")
        key = (role, repository, pr, surface, comment_id)
        if key in expected:
            raise SemanticBindingError(f"duplicate expected semantic-binding inventory key {key}")
        expected.add(key)

    base = _read_json(root, EXPECTED_DOCS["base"])
    for entry in base.get("entries", []):
        fid = _nonempty(entry.get("finding_id"), "base finding_id")
        gh = entry.get("github_evidence") or {}
        add(f"{fid}_FINDING", entry.get("repository"), entry.get("pr"), "review_comment", gh.get("codex_review_comment_id"))

    rereview = _read_json(root, EXPECTED_DOCS["rereview"])
    for entry in rereview.get("entries", []):
        fid = _nonempty(entry.get("finding_id"), "rereview finding_id")
        gh = entry.get("github_evidence") or {}
        resolution = entry.get("resolution_evidence") or {}
        add(f"{fid}_FINDING", entry.get("repository"), entry.get("pr"), "review_comment", gh.get("codex_review_comment_id"))
        add(f"{fid}_OWNER_REPLY", entry.get("repository"), entry.get("pr"), "review_comment", resolution.get("owner_reply_comment_id"))
        add(f"{fid}_REREVIEW_REQUEST", entry.get("repository"), entry.get("pr"), "issue_comment", resolution.get("rereview_request_comment_id"))
        add(f"{fid}_CLEAN_RESULT", entry.get("repository"), entry.get("pr"), "issue_comment", resolution.get("clean_codex_result_comment_id"))

    fix = _read_json(root, EXPECTED_DOCS["fix"])
    for entry in fix.get("entries", []):
        fid = _nonempty(entry.get("finding_id"), "fix finding_id")
        gh = entry.get("github_evidence") or {}
        add(f"{fid}_FINDING", entry.get("repository"), entry.get("pr"), "review_comment", gh.get("codex_review_comment_id"))
        add(f"{fid}_OWNER_REPLY", entry.get("repository"), entry.get("pr"), "review_comment", gh.get("owner_reply_comment_id"))

    authority_ci = _read_json(root, EXPECTED_DOCS["authority_ci"])
    for entry in authority_ci.get("entries", []):
        fid = _nonempty(entry.get("finding_id"), "authority-ci finding_id")
        gh = entry.get("github_evidence") or {}
        add(f"{fid}_FINDING", entry.get("repository"), entry.get("pr"), "review_comment", gh.get("codex_review_comment_id"))
        add(f"{fid}_OWNER_REPLY", entry.get("repository"), entry.get("pr"), "review_comment", gh.get("owner_reply_comment_id"))

    baseline = _read_json(root, EXPECTED_DOCS["baseline"])
    for entry in baseline.get("entries", []):
        fid = _nonempty(entry.get("finding_id"), "baseline finding_id")
        gh = entry.get("github_evidence") or {}
        add(f"{fid}_FINDING", entry.get("repository"), entry.get("pr"), "review_comment", gh.get("codex_review_comment_id"))
        add(f"{fid}_OWNER_REPLY", entry.get("repository"), entry.get("pr"), "review_comment", gh.get("owner_reply_comment_id"))

    progression = _read_json(root, EXPECTED_DOCS["progression"])
    for entry in progression.get("entries", []):
        fid = _nonempty(entry.get("finding_id"), "progression finding_id")
        initial = entry.get("initial_fix_evidence") or {}
        add(f"{fid}_FINDING", entry.get("repository"), entry.get("pr"), "review_comment", initial.get("codex_review_comment_id"))
        add(f"{fid}_OWNER_REPLY", entry.get("repository"), entry.get("pr"), "review_comment", initial.get("owner_reply_comment_id"))
        for followup in entry.get("followup_reviews", []):
            ffid = _nonempty(followup.get("finding_id"), "follow-up finding_id")
            add(f"{ffid}_FINDING", entry.get("repository"), entry.get("pr"), "review_comment", followup.get("codex_review_comment_id"))
            add(f"{ffid}_OWNER_REPLY", entry.get("repository"), entry.get("pr"), "review_comment", followup.get("owner_reply_comment_id"))

    return expected


def validate_registry_coverage(path: Path = DEFAULT_PATH, root: Path = ROOT) -> list[dict[str, Any]]:
    records = effective_bindings(path, root)
    actual = {binding_key(record) for record in records}
    expected = expected_inventory(root)
    if actual != expected or len(records) != len(expected):
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise SemanticBindingError(
            f"semantic-binding family coverage differs; missing={missing} extra={extra}"
        )
    return records


def records_for(snapshot: dict[str, Any], path: Path = DEFAULT_PATH, root: Path = ROOT) -> list[dict[str, Any]]:
    repository = snapshot.get("repository")
    pr = snapshot.get("pr_number")
    return [
        item
        for item in validate_registry_coverage(path, root)
        if item["repository"] == repository and item["pr"] == pr
    ]


def _validate_records(snapshot: dict[str, Any], records: list[dict[str, Any]]) -> int:
    repository = snapshot.get("repository")
    pr = snapshot.get("pr_number")
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
    pr_owner = (((snapshot.get("pull_request") or {}).get("user") or {}).get("login"))

    checked = 0
    for expected in records:
        source = review_comments if expected["surface"] == "review_comment" else issue_comments
        live = source.get(expected["comment_id"])
        label = f"{expected['role']} {repository}#{pr} comment {expected['comment_id']}"
        if not isinstance(live, dict):
            raise SemanticBindingError(f"{label}: exact comment is absent")
        expected_actor = expected["actor"]
        if expected["actor_source"] == "pr_owner":
            if not isinstance(pr_owner, str) or not pr_owner:
                raise SemanticBindingError(f"{label}: PR-owner actor identity is unavailable")
            expected_actor = pr_owner
        if ((live.get("user") or {}).get("login")) != expected_actor:
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


def validate_snapshot(snapshot: dict[str, Any], path: Path = DEFAULT_PATH, root: Path = ROOT) -> int:
    repository = snapshot.get("repository")
    pr = snapshot.get("pr_number")
    if not isinstance(repository, str) or not repository or not isinstance(pr, int) or isinstance(pr, bool):
        raise SemanticBindingError("snapshot repository/PR identity is unavailable")
    selected = records_for(snapshot, path, root)
    if not selected:
        raise SemanticBindingError(
            f"snapshot {repository}#{pr}: no required semantic bindings are registered"
        )
    return _validate_records(snapshot, selected)
