#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import verify_bootstrap_commentary_reconciliation as base

SCHEMA_VERSION = "bootstrap_commentary_rereview_reconciliation_v1"
AUTHORITY = "governed_reconciliation_of_authenticated_source_commentary"
KIND = "supported_fixed_clean_rereview"
STATUS = "SUPPORTED_FIXED_AND_CLEAN_REREVIEW_EVIDENCE"
CODEX_LOGIN = "chatgpt-codex-connector[bot]"
CODEX_APP_SLUG = "chatgpt-codex-connector"

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
    "resolution_evidence",
    "reconciliation_status",
    "authority_limit",
}
GITHUB_EVIDENCE_FIELDS = {"codex_review_id", "codex_review_comment_id"}
RESOLUTION_FIELDS = {
    "fixed_head",
    "owner_reply_comment_id",
    "rereview_request_comment_id",
    "clean_codex_result_comment_id",
    "changed_files",
    "content_assertions",
}
ASSERTION_FIELDS = {"path", "required_present", "required_absent"}
REVIEWED_COMMIT_RE = re.compile(r"Reviewed commit:\*\*?\s*`([0-9a-f]{7,40})`", re.IGNORECASE)


class RereviewReconciliationError(RuntimeError):
    pass


def exact_object(raw: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise RereviewReconciliationError(f"{label} must be an object")
    if set(raw) != fields:
        raise RereviewReconciliationError(
            f"{label} shape mismatch; missing={sorted(fields - set(raw))} "
            f"unknown={sorted(set(raw) - fields)}"
        )
    return raw


def positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise RereviewReconciliationError(f"{label} must be a positive integer")
    return value


def nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RereviewReconciliationError(f"{label} must be a non-empty string")
    return value


def sha40(value: Any, label: str) -> str:
    try:
        return base.require_sha(value, label)
    except Exception as exc:
        raise RereviewReconciliationError(str(exc)) from exc


def string_array(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    try:
        return base.require_string_array(value, label, allow_empty=allow_empty)
    except Exception as exc:
        raise RereviewReconciliationError(str(exc)) from exc


def timestamp(value: Any, label: str) -> datetime:
    text = nonempty(value, label)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RereviewReconciliationError(f"{label} is not an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise RereviewReconciliationError(f"{label} must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def load_document(path: Path, source_manifest_path: Path) -> dict[str, Any]:
    doc = exact_object(json.loads(path.read_text(encoding="utf-8")), TOP_FIELDS, str(path))
    if doc["schema_version"] != SCHEMA_VERSION:
        raise RereviewReconciliationError(f"{path}: unsupported schema")
    if doc["authority"] != AUTHORITY:
        raise RereviewReconciliationError(f"{path}: unexpected authority")

    manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    if doc["source_artifact_sha256"] != manifest.get("sha256"):
        raise RereviewReconciliationError(f"{path}: source artifact digest mismatch")

    coverage = exact_object(doc["coverage"], COVERAGE_FIELDS, f"{path}: coverage")
    if coverage["kind"] != "bounded_material_commentary_rereview_slice":
        raise RereviewReconciliationError(f"{path}: unsupported coverage kind")
    if coverage["source_sheet"] != "Findings":
        raise RereviewReconciliationError(f"{path}: source_sheet must be Findings")
    ids = string_array(coverage["finding_ids"], f"{path}: finding_ids")
    if coverage["complete_for_scope"] is not True:
        raise RereviewReconciliationError(f"{path}: complete_for_scope must be true")
    if coverage["global_commentary_reconciliation_complete"] is not False:
        raise RereviewReconciliationError(f"{path}: bounded slice cannot claim global completion")

    entries = doc["entries"]
    if not isinstance(entries, list) or not entries:
        raise RereviewReconciliationError(f"{path}: entries must be a non-empty array")
    seen_ids: set[str] = set()
    seen_rows: set[int] = set()
    for index, raw_entry in enumerate(entries, start=1):
        label = f"{path}: entry {index}"
        entry = exact_object(raw_entry, ENTRY_FIELDS, label)
        finding_id = nonempty(entry["finding_id"], f"{label} finding_id")
        nonempty(entry["repository"], f"{label} repository")
        positive_int(entry["pr"], f"{label} pr")
        sha40(entry["reviewed_head"], f"{label} reviewed_head")
        if entry["source_sheet"] != "Findings":
            raise RereviewReconciliationError(f"{label}: source_sheet must be Findings")
        row = positive_int(entry["source_row"], f"{label} source_row")
        nonempty(entry["source_confirmed"], f"{label} source_confirmed")
        nonempty(entry["source_note"], f"{label} source_note")
        if entry["kind"] != KIND or entry["reconciliation_status"] != STATUS:
            raise RereviewReconciliationError(f"{label}: unsupported kind/status")
        nonempty(entry["authority_limit"], f"{label} authority_limit")

        evidence = exact_object(entry["github_evidence"], GITHUB_EVIDENCE_FIELDS, f"{label} github_evidence")
        positive_int(evidence["codex_review_id"], f"{label} codex_review_id")
        positive_int(evidence["codex_review_comment_id"], f"{label} codex_review_comment_id")

        resolution = exact_object(entry["resolution_evidence"], RESOLUTION_FIELDS, f"{label} resolution_evidence")
        sha40(resolution["fixed_head"], f"{label} fixed_head")
        positive_int(resolution["owner_reply_comment_id"], f"{label} owner_reply_comment_id")
        positive_int(resolution["rereview_request_comment_id"], f"{label} rereview_request_comment_id")
        positive_int(resolution["clean_codex_result_comment_id"], f"{label} clean_codex_result_comment_id")
        changed_files = string_array(resolution["changed_files"], f"{label} changed_files")
        assertions = resolution["content_assertions"]
        if not isinstance(assertions, list) or not assertions:
            raise RereviewReconciliationError(f"{label}: content_assertions must be non-empty")
        paths: set[str] = set()
        for assertion_index, raw_assertion in enumerate(assertions, start=1):
            assertion_label = f"{label} assertion {assertion_index}"
            assertion = exact_object(raw_assertion, ASSERTION_FIELDS, assertion_label)
            path_value = nonempty(assertion["path"], f"{assertion_label} path")
            if path_value in paths:
                raise RereviewReconciliationError(f"{label}: duplicate assertion path {path_value}")
            paths.add(path_value)
            present = string_array(assertion["required_present"], f"{assertion_label} required_present")
            absent = string_array(assertion["required_absent"], f"{assertion_label} required_absent", allow_empty=True)
            if set(present) & set(absent):
                raise RereviewReconciliationError(f"{assertion_label}: contradictory tokens")
        if not paths.issubset(set(changed_files)):
            raise RereviewReconciliationError(f"{label}: assertions must target changed files")

        if finding_id in seen_ids or row in seen_rows:
            raise RereviewReconciliationError(f"{label}: duplicate finding or source row")
        seen_ids.add(finding_id)
        seen_rows.add(row)

    if set(ids) != seen_ids:
        raise RereviewReconciliationError(f"{path}: coverage identities do not match entries")
    string_array(doc["rules"], f"{path}: rules")
    return doc


def validate_source(entry: dict[str, Any], finding: dict[str, Any], snapshot: dict[str, Any]) -> list[str]:
    errors = base.validate_normalized_source(entry, finding)
    finding_id = entry["finding_id"]

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(f"{finding_id}: {message}")

    check(snapshot.get("repository") == entry["repository"], "snapshot repository differs")
    check(snapshot.get("pr_number") == entry["pr"], "snapshot PR differs")
    pr = snapshot.get("pull_request") or {}
    resolution = entry["resolution_evidence"]
    check(pr.get("number") == entry["pr"], "live PR number differs")
    check(pr.get("state") == "closed", "source PR is not closed")
    check(pr.get("merged_at") is not None, "source PR is not merged")
    check(((pr.get("head") or {}).get("sha")) == resolution["fixed_head"], "live final PR HEAD differs from fixed head")

    evidence = entry["github_evidence"]
    reviews = {item.get("id"): item for item in snapshot.get("reviews", []) if isinstance(item, dict)}
    comments = {item.get("id"): item for item in snapshot.get("review_comments", []) if isinstance(item, dict)}
    review = reviews.get(evidence["codex_review_id"])
    comment = comments.get(evidence["codex_review_comment_id"])
    check(review is not None, "exact original Codex review is absent")
    if review is not None:
        check(review.get("commit_id") == entry["reviewed_head"], "original Codex review commit differs")
        check(((review.get("user") or {}).get("login")) == CODEX_LOGIN, "original review actor differs")
    check(comment is not None, "exact original Codex finding is absent")
    if comment is not None:
        check(comment.get("pull_request_review_id") == evidence["codex_review_id"], "original finding review id differs")
        check(comment.get("commit_id") == entry["reviewed_head"], "original finding commit differs")
        check(comment.get("original_commit_id") == entry["reviewed_head"], "original finding original_commit differs")
        check(((comment.get("user") or {}).get("login")) == CODEX_LOGIN, "original finding actor differs")
    return errors


def validate_reviewed_to_fixed_compare(raw: Any, reviewed_head: str, fixed_head: str) -> None:
    if not isinstance(raw, dict):
        raise RereviewReconciliationError("reviewed-to-fixed compare is unavailable")
    status = nonempty(raw.get("status"), "reviewed-to-fixed compare status")
    base_sha = sha40(((raw.get("base_commit") or {}).get("sha")), "reviewed-to-fixed base")
    merge_base = sha40(((raw.get("merge_base_commit") or {}).get("sha")), "reviewed-to-fixed merge base")
    head_sha = sha40(((raw.get("head_commit") or {}).get("sha")), "reviewed-to-fixed head")
    if base_sha != reviewed_head or merge_base != reviewed_head or head_sha != fixed_head or status != "ahead":
        raise RereviewReconciliationError(
            f"fixed head is not an exact descendant of reviewed head; status={status} base={base_sha} merge_base={merge_base} head={head_sha}"
        )


def parse_clean_reviewed_prefix(body: str, fixed_head: str) -> None:
    if "Didn't find any major issues" not in body:
        raise RereviewReconciliationError("clean Codex result does not report no remaining major issues")
    match = REVIEWED_COMMIT_RE.search(body)
    if match is None:
        raise RereviewReconciliationError("clean Codex result has no Reviewed commit identity")
    prefix = match.group(1)
    if not fixed_head.startswith(prefix):
        raise RereviewReconciliationError(
            f"clean Codex result reviewed commit {prefix} does not match fixed head {fixed_head}"
        )


def resolve_and_validate_live(client: base.GitHubClient, entry: dict[str, Any], snapshot: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    finding_id = entry["finding_id"]
    repository = entry["repository"]
    owner, name = base.split_repository(repository)
    prefix = f"/repos/{owner}/{name}"
    pr = snapshot.get("pull_request") or {}
    pr_owner = ((pr.get("user") or {}).get("login"))
    if not pr_owner:
        errors.append(f"{finding_id}: PR owner identity is unavailable")
        return errors

    resolution = entry["resolution_evidence"]
    fixed_head = resolution["fixed_head"]
    evidence = entry["github_evidence"]

    try:
        compare = client.get(f"{prefix}/compare/{entry['reviewed_head']}...{fixed_head}")
        validate_reviewed_to_fixed_compare(compare, entry["reviewed_head"], fixed_head)
        base.fetch_default_branch_ancestry(client, prefix, fixed_head, "fixed rereview head")

        files = client.paged(f"{prefix}/pulls/{entry['pr']}/files")
        changed = sorted(item.get("filename") for item in files if isinstance(item, dict))
        if changed != sorted(resolution["changed_files"]):
            errors.append(f"{finding_id}: final changed-file inventory differs")

        for assertion in resolution["content_assertions"]:
            text = base.fetch_text_file(client, repository, assertion["path"], fixed_head)
            for token in assertion["required_present"]:
                if token not in text:
                    errors.append(f"{finding_id}: {assertion['path']} is missing required token {token!r}")
            for token in assertion["required_absent"]:
                if token in text:
                    errors.append(f"{finding_id}: {assertion['path']} contains forbidden token {token!r}")

        owner_reply = client.get(f"{prefix}/pulls/comments/{resolution['owner_reply_comment_id']}")
        if not isinstance(owner_reply, dict) or owner_reply.get("id") != resolution["owner_reply_comment_id"]:
            raise RereviewReconciliationError("exact owner reply is unavailable")
        if owner_reply.get("in_reply_to_id") != evidence["codex_review_comment_id"]:
            errors.append(f"{finding_id}: owner reply does not target original Codex finding")
        if ((owner_reply.get("user") or {}).get("login")) != pr_owner:
            errors.append(f"{finding_id}: owner reply actor differs from PR owner")
        if owner_reply.get("commit_id") != entry["reviewed_head"] or owner_reply.get("original_commit_id") != entry["reviewed_head"]:
            errors.append(f"{finding_id}: owner reply lost historical finding-head binding")
        if fixed_head not in str(owner_reply.get("body") or ""):
            errors.append(f"{finding_id}: owner reply does not name exact fixed head")
        if not str(owner_reply.get("pull_request_url") or "").endswith(f"/pulls/{entry['pr']}"):
            errors.append(f"{finding_id}: owner reply is not bound to exact PR")

        rereview_request = client.get(f"{prefix}/issues/comments/{resolution['rereview_request_comment_id']}")
        clean_result = client.get(f"{prefix}/issues/comments/{resolution['clean_codex_result_comment_id']}")
        if not isinstance(rereview_request, dict) or rereview_request.get("id") != resolution["rereview_request_comment_id"]:
            raise RereviewReconciliationError("exact re-review request is unavailable")
        if not isinstance(clean_result, dict) or clean_result.get("id") != resolution["clean_codex_result_comment_id"]:
            raise RereviewReconciliationError("exact clean Codex result is unavailable")

        if ((rereview_request.get("user") or {}).get("login")) != pr_owner:
            errors.append(f"{finding_id}: re-review request actor differs from PR owner")
        request_body = str(rereview_request.get("body") or "")
        if "@codex review" not in request_body or fixed_head not in request_body:
            errors.append(f"{finding_id}: re-review request does not bind exact fixed head")
        if not str(rereview_request.get("issue_url") or "").endswith(f"/issues/{entry['pr']}"):
            errors.append(f"{finding_id}: re-review request is not bound to exact PR")

        if ((clean_result.get("user") or {}).get("login")) != CODEX_LOGIN:
            errors.append(f"{finding_id}: clean result actor is not Codex bot")
        if ((clean_result.get("performed_via_github_app") or {}).get("slug")) != CODEX_APP_SLUG:
            errors.append(f"{finding_id}: clean result is not attributed to expected Codex GitHub App")
        if not str(clean_result.get("issue_url") or "").endswith(f"/issues/{entry['pr']}"):
            errors.append(f"{finding_id}: clean result is not bound to exact PR")
        try:
            parse_clean_reviewed_prefix(str(clean_result.get("body") or ""), fixed_head)
        except RereviewReconciliationError as exc:
            errors.append(f"{finding_id}: {exc}")

        request_time = timestamp(rereview_request.get("created_at"), "re-review request created_at")
        clean_time = timestamp(clean_result.get("created_at"), "clean result created_at")
        owner_reply_time = timestamp(owner_reply.get("created_at"), "owner reply created_at")
        merged_time = timestamp(pr.get("merged_at"), "PR merged_at")
        if not request_time < clean_time < owner_reply_time < merged_time:
            errors.append(f"{finding_id}: re-review evidence chronology is inconsistent")

        # "final exact-head Codex re-review" means no later Codex-authored review
        # submission, inline finding, or issue comment exists before merge.
        latest_codex_time = clean_time
        for item in snapshot.get("reviews", []):
            if isinstance(item, dict) and ((item.get("user") or {}).get("login")) == CODEX_LOGIN:
                candidate = item.get("submitted_at")
                if candidate and timestamp(candidate, "Codex review submitted_at") > latest_codex_time:
                    errors.append(f"{finding_id}: later Codex review exists after declared clean result")
        for item in snapshot.get("review_comments", []):
            if isinstance(item, dict) and ((item.get("user") or {}).get("login")) == CODEX_LOGIN:
                candidate = item.get("created_at")
                if candidate and timestamp(candidate, "Codex review comment created_at") > latest_codex_time:
                    errors.append(f"{finding_id}: later Codex inline finding exists after declared clean result")
        for item in snapshot.get("issue_comments", []):
            if isinstance(item, dict) and item.get("id") != resolution["clean_codex_result_comment_id"] and ((item.get("user") or {}).get("login")) == CODEX_LOGIN:
                candidate = item.get("created_at")
                if candidate and timestamp(candidate, "Codex issue comment created_at") > latest_codex_time:
                    errors.append(f"{finding_id}: later Codex issue comment exists after declared clean result")

    except Exception as exc:
        errors.append(f"{finding_id}: live rereview verification failed: {exc}")
    return errors


def verify(findings_path: Path, reconciliation_path: Path, source_manifest_path: Path, client: base.GitHubClient) -> dict[str, Any]:
    findings = base.load_tuple_jsonl(findings_path, base.FINDING_COLUMNS)
    findings_by_id = base.index_unique(findings, "finding_id", "finding_id")
    doc = load_document(reconciliation_path, source_manifest_path)
    snapshots: dict[tuple[str, int], dict[str, Any]] = {}
    errors: list[str] = []
    entries: list[dict[str, Any]] = []

    for entry in doc["entries"]:
        finding = findings_by_id.get(entry["finding_id"])
        if finding is None:
            errors.append(f"{entry['finding_id']}: normalized finding does not exist")
            continue
        key = (entry["repository"], entry["pr"])
        if key not in snapshots:
            snapshots[key] = base.build_snapshot(client, *key)
        snapshot = snapshots[key]
        entry_errors = validate_source(entry, finding, snapshot)
        entry_errors.extend(resolve_and_validate_live(client, entry, snapshot))
        errors.extend(entry_errors)
        entries.append({
            "finding_id": entry["finding_id"],
            "reconciliation_status": entry["reconciliation_status"],
            "status": "PASS" if not entry_errors else "FAIL",
        })

    return {
        "schema_version": "bootstrap_commentary_rereview_reconciliation_check_v1",
        "authority": "derived_live_verification_not_source_truth",
        "source_artifact_sha256": doc["source_artifact_sha256"],
        "scope": doc["coverage"],
        "entries_checked": len(entries),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "entries": entries,
        "limitations": [
            "a clean exact-head Codex re-review is evidence about that bounded review run, not universal proof of semantic correctness",
            "owner fixed prose is not accepted without independent fixed-head content and identity evidence",
            "does not modify authenticated bootstrap-v1 source projections",
            "does not claim global source-commentary reconciliation is complete",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify bounded clean-rereview source-commentary reconciliation.")
    parser.add_argument("--findings", type=Path, default=Path("data/findings.jsonl"))
    parser.add_argument("--reconciliation", type=Path, default=Path("data/bootstrap-commentary-rereview-reconciliation.json"))
    parser.add_argument("--source-manifest", type=Path, default=Path("data/bootstrap-source.json"))
    parser.add_argument("--api-url", default=os.environ.get("GITHUB_API_URL", "https://api.github.com"))
    parser.add_argument("--token-env", default="MIMISEEK_GITHUB_TOKEN")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    client = base.GitHubClient(token=os.environ.get(args.token_env), api_url=args.api_url)
    try:
        result = verify(args.findings, args.reconciliation, args.source_manifest, client)
    except Exception as exc:
        print(f"bootstrap commentary rereview reconciliation verification failed: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
