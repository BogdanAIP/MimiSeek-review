#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Any

TOOLS_ROOT = Path(__file__).resolve().parent
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from collect_github_evidence import GitHubClient, build_snapshot, split_repository  # noqa: E402

SCHEMA_VERSION = "bootstrap_commentary_reconciliation_v1"
AUTHORITY = "governed_reconciliation_of_authenticated_source_commentary"
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CODEX_LOGIN = "chatgpt-codex-connector[bot]"

FINDING_COLUMNS = [
    "finding_id",
    "repository",
    "pr",
    "head_sha",
    "reviewer",
    "severity",
    "confirmed",
    "scored",
    "defect_group",
    "category",
    "finding",
    "same_head_match",
    "other_reviewer",
    "source_url",
    "evidence_confidence",
    "source_row",
]

TOP_FIELDS = {
    "schema_version",
    "authority",
    "source_artifact_sha256",
    "coverage",
    "entries",
    "rules",
}
COVERAGE_FIELDS = {
    "kind",
    "source_sheet",
    "finding_ids",
    "complete_for_scope",
    "global_commentary_reconciliation_complete",
}
ENTRY_FIELDS = {
    "finding_id",
    "repository",
    "pr",
    "reviewed_head",
    "source_sheet",
    "source_row",
    "source_confirmed",
    "source_note",
    "kind",
    "github_evidence",
    "follow_up",
    "reconciliation_status",
    "authority_limit",
}
GITHUB_EVIDENCE_FIELDS = {"codex_review_id", "codex_review_comment_id"}
FOLLOW_UP_FIELDS = {
    "repository",
    "pr",
    "base_sha",
    "head_sha",
    "merge_commit_sha",
    "changed_files",
    "content_assertions",
}
CONTENT_ASSERTION_FIELDS = {"path", "required_present", "required_absent"}

PRESERVE_UNKNOWN_KIND = "preserve_source_unknown"
SUPPORTED_ADDRESS_KIND = "supported_material_address"
PRESERVED_UNKNOWN_STATUS = "PRESERVED_UNKNOWN"
SUPPORTED_ADDRESS_STATUS = "SUPPORTED_MATERIAL_ADDRESS_EVIDENCE"


class CommentaryProvenanceError(RuntimeError):
    pass


def require_exact_shape(raw: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise CommentaryProvenanceError(f"{label} must be an object")
    if set(raw) != fields:
        missing = sorted(fields - set(raw))
        unknown = sorted(set(raw) - fields)
        raise CommentaryProvenanceError(
            f"{label} shape mismatch; missing={missing} unknown={unknown}"
        )
    return raw


def require_positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise CommentaryProvenanceError(f"{label} must be a positive integer, got {value!r}")
    return value


def require_nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CommentaryProvenanceError(f"{label} must be a non-empty string")
    return value


def require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA40_RE.fullmatch(value):
        raise CommentaryProvenanceError(f"{label} must be a lowercase 40-character SHA")
    return value


def require_string_array(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise CommentaryProvenanceError(f"{label} must be a string array")
    if not allow_empty and not value:
        raise CommentaryProvenanceError(f"{label} must not be empty")
    if len(value) != len(set(value)):
        raise CommentaryProvenanceError(f"{label} contains duplicates")
    return value


def load_tuple_jsonl(path: Path, columns: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        raw = json.loads(line)
        if not isinstance(raw, list) or len(raw) != len(columns):
            raise CommentaryProvenanceError(
                f"{path}:{line_number}: expected {len(columns)} positional fields"
            )
        record = dict(zip(columns, raw, strict=True))
        record["_line_number"] = line_number
        records.append(record)
    return records


def index_unique(records: list[dict[str, Any]], key: str, label: str) -> dict[Any, dict[str, Any]]:
    result: dict[Any, dict[str, Any]] = {}
    for record in records:
        value = record[key]
        if value in result:
            raise CommentaryProvenanceError(f"duplicate {label} {value!r}")
        result[value] = record
    return result


def validate_content_assertion(raw: Any, label: str) -> dict[str, Any]:
    assertion = require_exact_shape(raw, CONTENT_ASSERTION_FIELDS, label)
    require_nonempty_string(assertion["path"], f"{label} path")
    require_string_array(assertion["required_present"], f"{label} required_present")
    require_string_array(
        assertion["required_absent"], f"{label} required_absent", allow_empty=True
    )
    overlap = set(assertion["required_present"]) & set(assertion["required_absent"])
    if overlap:
        raise CommentaryProvenanceError(f"{label} has contradictory tokens: {sorted(overlap)}")
    return assertion


def validate_follow_up(raw: Any, label: str) -> dict[str, Any]:
    follow_up = require_exact_shape(raw, FOLLOW_UP_FIELDS, label)
    repository = require_nonempty_string(follow_up["repository"], f"{label} repository")
    split_repository(repository)
    require_positive_int(follow_up["pr"], f"{label} pr")
    for field in ("base_sha", "head_sha", "merge_commit_sha"):
        require_sha(follow_up[field], f"{label} {field}")
    require_string_array(follow_up["changed_files"], f"{label} changed_files")
    assertions = follow_up["content_assertions"]
    if not isinstance(assertions, list) or not assertions:
        raise CommentaryProvenanceError(f"{label} content_assertions must be a non-empty array")
    seen_paths: set[str] = set()
    for index, assertion in enumerate(assertions, start=1):
        normalized = validate_content_assertion(assertion, f"{label} assertion {index}")
        path = normalized["path"]
        if path in seen_paths:
            raise CommentaryProvenanceError(f"{label} has duplicate assertion path {path!r}")
        seen_paths.add(path)
    if not seen_paths.issubset(set(follow_up["changed_files"])):
        raise CommentaryProvenanceError(
            f"{label} assertions must target files in the declared changed-file inventory"
        )
    return follow_up


def load_reconciliation(path: Path, source_manifest_path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    doc = require_exact_shape(raw, TOP_FIELDS, str(path))
    if doc["schema_version"] != SCHEMA_VERSION:
        raise CommentaryProvenanceError(f"{path}: unsupported reconciliation schema")
    if doc["authority"] != AUTHORITY:
        raise CommentaryProvenanceError(f"{path}: unexpected authority")
    if not isinstance(doc["source_artifact_sha256"], str) or not SHA256_RE.fullmatch(
        doc["source_artifact_sha256"]
    ):
        raise CommentaryProvenanceError(f"{path}: source_artifact_sha256 is invalid")

    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    manifest_sha = source_manifest.get("sha256") if isinstance(source_manifest, dict) else None
    if doc["source_artifact_sha256"] != manifest_sha:
        raise CommentaryProvenanceError(
            f"{path}: source artifact digest does not match {source_manifest_path}"
        )

    coverage = require_exact_shape(doc["coverage"], COVERAGE_FIELDS, f"{path}: coverage")
    if coverage["kind"] != "bounded_material_commentary_slice":
        raise CommentaryProvenanceError(f"{path}: unsupported coverage kind")
    if coverage["source_sheet"] != "Findings":
        raise CommentaryProvenanceError(f"{path}: this slice must be bound to Findings")
    finding_ids = require_string_array(
        coverage["finding_ids"], f"{path}: coverage finding_ids"
    )
    if type(coverage["complete_for_scope"]) is not bool:
        raise CommentaryProvenanceError(f"{path}: complete_for_scope must be boolean")
    if type(coverage["global_commentary_reconciliation_complete"]) is not bool:
        raise CommentaryProvenanceError(
            f"{path}: global_commentary_reconciliation_complete must be boolean"
        )
    if coverage["global_commentary_reconciliation_complete"]:
        raise CommentaryProvenanceError(
            f"{path}: bounded slice cannot claim global commentary completion"
        )

    entries = doc["entries"]
    if not isinstance(entries, list) or not entries:
        raise CommentaryProvenanceError(f"{path}: entries must be a non-empty array")

    seen_ids: set[str] = set()
    seen_rows: set[tuple[str, int]] = set()
    for index, raw_entry in enumerate(entries, start=1):
        label = f"{path}: entry {index}"
        entry = require_exact_shape(raw_entry, ENTRY_FIELDS, label)
        finding_id = require_nonempty_string(entry["finding_id"], f"{label} finding_id")
        repository = require_nonempty_string(entry["repository"], f"{label} repository")
        split_repository(repository)
        require_positive_int(entry["pr"], f"{label} pr")
        require_sha(entry["reviewed_head"], f"{label} reviewed_head")
        if entry["source_sheet"] != "Findings":
            raise CommentaryProvenanceError(f"{label} source_sheet must be Findings")
        source_row = require_positive_int(entry["source_row"], f"{label} source_row")
        require_nonempty_string(entry["source_confirmed"], f"{label} source_confirmed")
        require_nonempty_string(entry["source_note"], f"{label} source_note")
        require_nonempty_string(entry["authority_limit"], f"{label} authority_limit")

        evidence = require_exact_shape(
            entry["github_evidence"], GITHUB_EVIDENCE_FIELDS, f"{label} github_evidence"
        )
        require_positive_int(evidence["codex_review_id"], f"{label} codex_review_id")
        require_positive_int(
            evidence["codex_review_comment_id"], f"{label} codex_review_comment_id"
        )

        kind = entry["kind"]
        if kind == PRESERVE_UNKNOWN_KIND:
            if entry["source_confirmed"] != "UNKNOWN":
                raise CommentaryProvenanceError(
                    f"{label}: preserve_source_unknown requires source_confirmed=UNKNOWN"
                )
            if entry["follow_up"] is not None:
                raise CommentaryProvenanceError(
                    f"{label}: preserve_source_unknown must not assert follow-up evidence"
                )
            if entry["reconciliation_status"] != PRESERVED_UNKNOWN_STATUS:
                raise CommentaryProvenanceError(f"{label}: wrong preserved-unknown status")
        elif kind == SUPPORTED_ADDRESS_KIND:
            if entry["follow_up"] is None:
                raise CommentaryProvenanceError(
                    f"{label}: supported material address requires follow-up evidence"
                )
            validate_follow_up(entry["follow_up"], f"{label} follow_up")
            if entry["reconciliation_status"] != SUPPORTED_ADDRESS_STATUS:
                raise CommentaryProvenanceError(f"{label}: wrong supported-address status")
        else:
            raise CommentaryProvenanceError(f"{label}: unsupported kind {kind!r}")

        if finding_id in seen_ids:
            raise CommentaryProvenanceError(f"{path}: duplicate finding reconciliation {finding_id}")
        row_key = (entry["source_sheet"], source_row)
        if row_key in seen_rows:
            raise CommentaryProvenanceError(f"{path}: duplicate source row {row_key}")
        seen_ids.add(finding_id)
        seen_rows.add(row_key)

    if set(finding_ids) != seen_ids:
        raise CommentaryProvenanceError(
            f"{path}: coverage finding_ids do not exactly match entry identities"
        )
    if not coverage["complete_for_scope"]:
        raise CommentaryProvenanceError(
            f"{path}: bounded slice must declare complete_for_scope=true for its listed identities"
        )
    require_string_array(doc["rules"], f"{path}: rules")
    return doc


def validate_normalized_source(entry: dict[str, Any], finding: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    finding_id = entry["finding_id"]

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(f"{finding_id}: {message}")

    check(finding["repository"] == entry["repository"], "repository differs from normalized finding")
    check(finding["pr"] == entry["pr"], "PR differs from normalized finding")
    check(finding["head_sha"] == entry["reviewed_head"], "reviewed HEAD differs from normalized finding")
    check(finding["confirmed"] == entry["source_confirmed"], "confirmed state differs from normalized finding")
    check(finding["source_row"] == entry["source_row"], "source row differs from normalized finding")
    check(
        finding["source_url"] == f"https://github.com/{entry['repository']}/pull/{entry['pr']}",
        "source URL differs from exact PR URL",
    )
    return errors


def validate_original_github_evidence(
    entry: dict[str, Any], snapshot: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    finding_id = entry["finding_id"]

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(f"{finding_id}: {message}")

    check(snapshot.get("repository") == entry["repository"], "snapshot repository differs")
    check(snapshot.get("pr_number") == entry["pr"], "snapshot PR differs")
    pr = snapshot.get("pull_request") or {}
    check(pr.get("number") == entry["pr"], "live PR number differs")
    check(((pr.get("head") or {}).get("sha")) == entry["reviewed_head"], "live/final PR HEAD differs")

    evidence = entry["github_evidence"]
    reviews = {
        item.get("id"): item for item in snapshot.get("reviews", []) if isinstance(item, dict)
    }
    comments = {
        item.get("id"): item
        for item in snapshot.get("review_comments", [])
        if isinstance(item, dict)
    }

    review = reviews.get(evidence["codex_review_id"])
    check(review is not None, "exact Codex review is absent")
    if review is not None:
        check(review.get("commit_id") == entry["reviewed_head"], "Codex review is not bound to reviewed HEAD")
        check(
            ((review.get("user") or {}).get("login")) == CODEX_LOGIN,
            "review actor is not the expected Codex bot",
        )

    comment = comments.get(evidence["codex_review_comment_id"])
    check(comment is not None, "exact Codex review comment is absent")
    if comment is not None:
        check(
            comment.get("pull_request_review_id") == evidence["codex_review_id"],
            "Codex comment is not bound to the expected review",
        )
        check(comment.get("commit_id") == entry["reviewed_head"], "Codex comment commit_id differs")
        check(
            comment.get("original_commit_id") == entry["reviewed_head"],
            "Codex comment original_commit_id differs",
        )
        check(
            ((comment.get("user") or {}).get("login")) == CODEX_LOGIN,
            "Codex comment actor differs",
        )
    return errors


def fetch_text_file(client: GitHubClient, repository: str, path: str, ref: str) -> str:
    owner, name = split_repository(repository)
    encoded_path = urllib.parse.quote(path, safe="/")
    payload = client.get(
        f"/repos/{owner}/{name}/contents/{encoded_path}",
        {"ref": ref},
    )
    if not isinstance(payload, dict) or payload.get("type") != "file":
        raise CommentaryProvenanceError(
            f"follow-up content lookup did not return file {repository}:{path}@{ref}"
        )
    if payload.get("encoding") != "base64" or not isinstance(payload.get("content"), str):
        raise CommentaryProvenanceError(
            f"follow-up content lookup returned unsupported encoding for {path}"
        )
    try:
        return base64.b64decode(payload["content"], validate=False).decode("utf-8")
    except Exception as exc:
        raise CommentaryProvenanceError(
            f"follow-up content for {path} is not valid UTF-8 base64"
        ) from exc


def fetch_commit_identity(client: GitHubClient, prefix: str, sha: str) -> dict[str, Any]:
    raw = client.get(f"{prefix}/commits/{sha}")
    if not isinstance(raw, dict) or raw.get("sha") != sha:
        raise CommentaryProvenanceError(f"live commit lookup did not return exact {sha}")
    tree = ((raw.get("commit") or {}).get("tree") or {}).get("sha")
    require_sha(tree, f"commit {sha} tree")
    parents_raw = raw.get("parents")
    if not isinstance(parents_raw, list):
        raise CommentaryProvenanceError(f"commit {sha} parents are malformed")
    parents: list[str] = []
    for parent in parents_raw:
        if not isinstance(parent, dict):
            raise CommentaryProvenanceError(f"commit {sha} parent is malformed")
        parents.append(require_sha(parent.get("sha"), f"commit {sha} parent"))
    return {"sha": sha, "tree": tree, "parents": tuple(parents)}


def fetch_associated_pr_numbers(client: GitHubClient, prefix: str, sha: str) -> set[int]:
    raw = client.get(f"{prefix}/commits/{sha}/pulls")
    if not isinstance(raw, list):
        raise CommentaryProvenanceError(f"commit-to-PR association lookup failed for {sha}")
    numbers: set[int] = set()
    for item in raw:
        if not isinstance(item, dict):
            raise CommentaryProvenanceError(f"commit-to-PR association for {sha} is malformed")
        number = require_positive_int(item.get("number"), f"associated PR number for {sha}")
        numbers.add(number)
    return numbers


def resolve_follow_up(
    client: GitHubClient,
    follow_up: dict[str, Any],
    source_pr_number: int,
    source_head_sha: str,
) -> dict[str, Any]:
    repository = follow_up["repository"]
    owner, name = split_repository(repository)
    pr_number = follow_up["pr"]
    prefix = f"/repos/{owner}/{name}"
    pr = client.get(f"{prefix}/pulls/{pr_number}")
    if not isinstance(pr, dict):
        raise CommentaryProvenanceError(f"follow-up PR {repository}#{pr_number} is unavailable")
    files = client.paged(f"{prefix}/pulls/{pr_number}/files")
    contents = {
        assertion["path"]: fetch_text_file(
            client, repository, assertion["path"], follow_up["head_sha"]
        )
        for assertion in follow_up["content_assertions"]
    }
    return {
        "pr": pr,
        "changed_files": sorted(
            item.get("filename") for item in files if isinstance(item, dict)
        ),
        "contents": contents,
        "source_head_commit": fetch_commit_identity(client, prefix, source_head_sha),
        "source_merge_commit": fetch_commit_identity(client, prefix, follow_up["base_sha"]),
        "source_merge_associated_prs": fetch_associated_pr_numbers(
            client, prefix, follow_up["base_sha"]
        ),
        "follow_head_commit": fetch_commit_identity(client, prefix, follow_up["head_sha"]),
        "follow_merge_commit": fetch_commit_identity(
            client, prefix, follow_up["merge_commit_sha"]
        ),
        "follow_merge_associated_prs": fetch_associated_pr_numbers(
            client, prefix, follow_up["merge_commit_sha"]
        ),
        "expected_source_pr_number": source_pr_number,
    }


def validate_follow_up_live(
    entry: dict[str, Any],
    source_snapshot: dict[str, Any],
    resolved: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    finding_id = entry["finding_id"]
    follow_up = entry["follow_up"]

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(f"{finding_id}: {message}")

    if follow_up is None:
        return errors

    pr = resolved.get("pr") or {}
    check(pr.get("number") == follow_up["pr"], "follow-up PR number differs")
    check(pr.get("state") == "closed", "follow-up PR is not closed")
    check(pr.get("merged_at") is not None, "follow-up PR is not merged")
    check(((pr.get("base") or {}).get("sha")) == follow_up["base_sha"], "follow-up BASE differs")
    check(((pr.get("head") or {}).get("sha")) == follow_up["head_sha"], "follow-up HEAD differs")

    base_repo = (pr.get("base") or {}).get("repo") or {}
    check(
        base_repo.get("full_name") == follow_up["repository"],
        "follow-up base repository differs",
    )
    check(
        base_repo.get("id") == source_snapshot.get("repository_id"),
        "follow-up repository numeric identity differs from source PR repository",
    )

    source_head_commit = resolved.get("source_head_commit") or {}
    source_merge_commit = resolved.get("source_merge_commit") or {}
    follow_head_commit = resolved.get("follow_head_commit") or {}
    follow_merge_commit = resolved.get("follow_merge_commit") or {}

    check(
        source_head_commit.get("sha") == entry["reviewed_head"],
        "source reviewed HEAD commit identity differs",
    )
    check(
        source_merge_commit.get("sha") == follow_up["base_sha"],
        "source merged commit identity differs from follow-up BASE",
    )
    check(
        source_merge_commit.get("tree") == source_head_commit.get("tree"),
        "source merged commit tree differs from exact reviewed source HEAD tree",
    )
    check(
        entry["pr"] in (resolved.get("source_merge_associated_prs") or set()),
        "source merged commit is not associated with the exact source PR",
    )

    check(
        follow_head_commit.get("sha") == follow_up["head_sha"],
        "follow-up HEAD commit identity differs",
    )
    check(
        follow_merge_commit.get("sha") == follow_up["merge_commit_sha"],
        "follow-up merged commit identity differs",
    )
    check(
        follow_merge_commit.get("parents") == (follow_up["base_sha"],),
        "follow-up merged commit is not directly based on the declared source merge/base",
    )
    check(
        follow_merge_commit.get("tree") == follow_head_commit.get("tree"),
        "follow-up merged commit tree differs from exact follow-up HEAD tree",
    )
    check(
        follow_up["pr"] in (resolved.get("follow_merge_associated_prs") or set()),
        "follow-up merged commit is not associated with the exact follow-up PR",
    )

    changed_files = resolved.get("changed_files")
    check(
        changed_files == sorted(follow_up["changed_files"]),
        "follow-up changed-file inventory differs",
    )

    contents = resolved.get("contents") or {}
    for assertion in follow_up["content_assertions"]:
        path = assertion["path"]
        text = contents.get(path)
        check(isinstance(text, str), f"follow-up content is missing for {path}")
        if not isinstance(text, str):
            continue
        for token in assertion["required_present"]:
            check(token in text, f"{path} is missing required evidence token {token!r}")
        for token in assertion["required_absent"]:
            check(token not in text, f"{path} contains forbidden evidence token {token!r}")
    return errors


def verify(
    findings_path: Path,
    reconciliation_path: Path,
    source_manifest_path: Path,
    client: GitHubClient,
) -> dict[str, Any]:
    findings = load_tuple_jsonl(findings_path, FINDING_COLUMNS)
    findings_by_id = index_unique(findings, "finding_id", "finding_id")
    doc = load_reconciliation(reconciliation_path, source_manifest_path)

    snapshots: dict[tuple[str, int], dict[str, Any]] = {}
    errors: list[str] = []
    entries_summary: list[dict[str, Any]] = []

    for entry in doc["entries"]:
        finding = findings_by_id.get(entry["finding_id"])
        if finding is None:
            errors.append(f"{entry['finding_id']}: normalized finding does not exist")
            continue

        key = (entry["repository"], entry["pr"])
        if key not in snapshots:
            snapshots[key] = build_snapshot(client, *key)
        source_snapshot = snapshots[key]

        entry_errors = validate_normalized_source(entry, finding)
        entry_errors.extend(validate_original_github_evidence(entry, source_snapshot))

        if entry["kind"] == SUPPORTED_ADDRESS_KIND:
            resolved = resolve_follow_up(
                client,
                entry["follow_up"],
                entry["pr"],
                entry["reviewed_head"],
            )
            entry_errors.extend(validate_follow_up_live(entry, source_snapshot, resolved))

        errors.extend(entry_errors)
        entries_summary.append(
            {
                "finding_id": entry["finding_id"],
                "kind": entry["kind"],
                "reconciliation_status": entry["reconciliation_status"],
                "status": "PASS" if not entry_errors else "FAIL",
            }
        )

    return {
        "schema_version": "bootstrap_commentary_reconciliation_check_v1",
        "authority": "derived_live_verification_not_source_truth",
        "source_artifact_sha256": doc["source_artifact_sha256"],
        "scope": doc["coverage"],
        "entries_checked": len(entries_summary),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "entries": entries_summary,
        "limitations": [
            "does not infer semantic fix correctness from owner prose, merge status, ancestry, or passing tests",
            "does not infer absence of later evidence for PRESERVED_UNKNOWN entries",
            "does not modify authenticated bootstrap-v1 source projections",
            "does not claim global source-commentary reconciliation is complete",
            "does not rely on pull.merge_commit_sha because the scoped source GitHub App redacts that field; merged-commit identity is instead checked through immutable Git objects and commit-to-PR association",
        ],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify bounded bootstrap source-commentary reconciliation against live GitHub evidence."
    )
    parser.add_argument("--findings", type=Path, default=Path("data/findings.jsonl"))
    parser.add_argument(
        "--reconciliation",
        type=Path,
        default=Path("data/bootstrap-commentary-reconciliation.json"),
    )
    parser.add_argument(
        "--source-manifest",
        type=Path,
        default=Path("data/bootstrap-source.json"),
    )
    parser.add_argument("--api-url", default=os.environ.get("GITHUB_API_URL", "https://api.github.com"))
    parser.add_argument("--token-env", default="MIMISEEK_GITHUB_TOKEN")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    client = GitHubClient(
        token=os.environ.get(args.token_env),
        api_url=args.api_url,
    )
    try:
        result = verify(
            args.findings,
            args.reconciliation,
            args.source_manifest,
            client,
        )
    except Exception as exc:
        print(f"bootstrap commentary reconciliation verification failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
