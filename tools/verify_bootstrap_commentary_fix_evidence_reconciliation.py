#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import verify_bootstrap_commentary_reconciliation as base

SCHEMA_VERSION = "bootstrap_commentary_fix_evidence_reconciliation_v1"
AUTHORITY = "governed_reconciliation_of_authenticated_source_commentary"
KIND = "supported_same_pr_material_fix_evidence"
STATUS = "SUPPORTED_SAME_PR_MATERIAL_FIX_EVIDENCE"
CODEX_LOGIN = "chatgpt-codex-connector[bot]"

TOP_FIELDS = {"schema_version", "authority", "source_artifact_sha256", "coverage", "entries", "rules"}
COVERAGE_FIELDS = {
    "kind", "source_sheet", "finding_ids", "complete_for_scope",
    "global_commentary_reconciliation_complete",
}
ENTRY_FIELDS = {
    "finding_id", "repository", "pr", "reviewed_head", "source_sheet", "source_row",
    "source_confirmed", "source_note", "kind", "github_evidence", "fix_evidence",
    "reconciliation_status", "authority_limit",
}
GITHUB_FIELDS = {"codex_review_id", "codex_review_comment_id", "owner_reply_comment_id"}
FIX_FIELDS = {"fix_head", "changed_files", "content_assertions"}
ASSERTION_FIELDS = {"path", "required_present", "required_absent"}

EXPECTED = {
    "F053": {
        "repository": "BogdanAIP/uv-studio",
        "pr": 71,
        "reviewed_head": "238870958fb88a291cdfa3e2345d8c5d84821534",
        "source_row": 54,
        "source_confirmed": "CONFIRMED",
        "source_note": "Fixed with persistence-time role/output/identity revalidation.",
        "codex_review_id": 5043741722,
        "codex_review_comment_id": 3874197354,
        "owner_reply_comment_id": 3874292248,
        "fix_head": "ce4a51f042e628df2f569532d42be17394e2ab4b",
    },
    "F054": {
        "repository": "BogdanAIP/uv-studio",
        "pr": 71,
        "reviewed_head": "238870958fb88a291cdfa3e2345d8c5d84821534",
        "source_row": 55,
        "source_confirmed": "CONFIRMED",
        "source_note": "Fixed for normal shared execution and committed-effect recovery.",
        "codex_review_id": 5043741722,
        "codex_review_comment_id": 3874197368,
        "owner_reply_comment_id": 3874293460,
        "fix_head": "aafddd3b37476a65558d56755edd2ae440648b74",
    },
}


class FixEvidenceError(RuntimeError):
    pass


def exact_object(raw: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise FixEvidenceError(f"{label} must be an object")
    if set(raw) != fields:
        raise FixEvidenceError(
            f"{label} shape mismatch; missing={sorted(fields - set(raw))} unknown={sorted(set(raw) - fields)}"
        )
    return raw


def positive_int(value: Any, label: str) -> int:
    try:
        return base.require_positive_int(value, label)
    except Exception as exc:
        raise FixEvidenceError(str(exc)) from exc


def nonempty(value: Any, label: str) -> str:
    try:
        return base.require_nonempty_string(value, label)
    except Exception as exc:
        raise FixEvidenceError(str(exc)) from exc


def sha40(value: Any, label: str) -> str:
    try:
        return base.require_sha(value, label)
    except Exception as exc:
        raise FixEvidenceError(str(exc)) from exc


def strings(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    try:
        return base.require_string_array(value, label, allow_empty=allow_empty)
    except Exception as exc:
        raise FixEvidenceError(str(exc)) from exc


def load_document(path: Path, source_manifest_path: Path) -> dict[str, Any]:
    doc = exact_object(json.loads(path.read_text(encoding="utf-8")), TOP_FIELDS, str(path))
    if doc["schema_version"] != SCHEMA_VERSION or doc["authority"] != AUTHORITY:
        raise FixEvidenceError(f"{path}: unsupported schema/authority")
    manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    if doc["source_artifact_sha256"] != manifest.get("sha256"):
        raise FixEvidenceError(f"{path}: source artifact digest mismatch")

    coverage = exact_object(doc["coverage"], COVERAGE_FIELDS, f"{path}: coverage")
    if coverage["kind"] != "bounded_same_pr_material_fix_evidence_slice":
        raise FixEvidenceError(f"{path}: unsupported coverage kind")
    if coverage["source_sheet"] != "Findings":
        raise FixEvidenceError(f"{path}: coverage must be bound to Findings")
    ids = strings(coverage["finding_ids"], f"{path}: finding_ids")
    if ids != ["F053", "F054"]:
        raise FixEvidenceError(f"{path}: this bounded schema is exactly F053/F054")
    if coverage["complete_for_scope"] is not True:
        raise FixEvidenceError(f"{path}: complete_for_scope must be true")
    if coverage["global_commentary_reconciliation_complete"] is not False:
        raise FixEvidenceError(f"{path}: bounded slice cannot claim global completion")

    entries = doc["entries"]
    if not isinstance(entries, list) or len(entries) != 2:
        raise FixEvidenceError(f"{path}: entries must contain exactly F053/F054")
    seen_ids: set[str] = set()
    seen_rows: set[int] = set()
    for index, raw_entry in enumerate(entries, start=1):
        label = f"{path}: entry {index}"
        entry = exact_object(raw_entry, ENTRY_FIELDS, label)
        finding_id = nonempty(entry["finding_id"], f"{label} finding_id")
        expected = EXPECTED.get(finding_id)
        if expected is None:
            raise FixEvidenceError(f"{label}: unsupported finding {finding_id}")
        if entry["source_sheet"] != "Findings" or entry["kind"] != KIND or entry["reconciliation_status"] != STATUS:
            raise FixEvidenceError(f"{label}: unsupported source/kind/status")
        nonempty(entry["authority_limit"], f"{label} authority_limit")
        positive_int(entry["pr"], f"{label} pr")
        positive_int(entry["source_row"], f"{label} source_row")
        sha40(entry["reviewed_head"], f"{label} reviewed_head")
        nonempty(entry["source_confirmed"], f"{label} source_confirmed")
        nonempty(entry["source_note"], f"{label} source_note")

        for field in ("repository", "pr", "reviewed_head", "source_row", "source_confirmed", "source_note"):
            if entry[field] != expected[field]:
                raise FixEvidenceError(f"{label}: {field} differs from bounded F053/F054 contract")

        github = exact_object(entry["github_evidence"], GITHUB_FIELDS, f"{label} github_evidence")
        for field in GITHUB_FIELDS:
            positive_int(github[field], f"{label} {field}")
            if github[field] != expected[field]:
                raise FixEvidenceError(f"{label}: {field} differs from bounded contract")

        fix = exact_object(entry["fix_evidence"], FIX_FIELDS, f"{label} fix_evidence")
        sha40(fix["fix_head"], f"{label} fix_head")
        if fix["fix_head"] != expected["fix_head"]:
            raise FixEvidenceError(f"{label}: fix_head differs from bounded contract")
        changed_files = strings(fix["changed_files"], f"{label} changed_files")
        assertions = fix["content_assertions"]
        if not isinstance(assertions, list) or not assertions:
            raise FixEvidenceError(f"{label}: content_assertions must be non-empty")
        paths: set[str] = set()
        for assertion_index, raw_assertion in enumerate(assertions, start=1):
            assertion_label = f"{label} assertion {assertion_index}"
            assertion = exact_object(raw_assertion, ASSERTION_FIELDS, assertion_label)
            path_value = nonempty(assertion["path"], f"{assertion_label} path")
            if path_value in paths:
                raise FixEvidenceError(f"{label}: duplicate assertion path")
            paths.add(path_value)
            present = strings(assertion["required_present"], f"{assertion_label} required_present")
            absent = strings(assertion["required_absent"], f"{assertion_label} required_absent", allow_empty=True)
            if set(present) & set(absent):
                raise FixEvidenceError(f"{assertion_label}: contradictory tokens")
        if not paths.issubset(set(changed_files)):
            raise FixEvidenceError(f"{label}: assertions must target declared changed files")
        if finding_id in seen_ids or entry["source_row"] in seen_rows:
            raise FixEvidenceError(f"{label}: duplicate finding/source row")
        seen_ids.add(finding_id)
        seen_rows.add(entry["source_row"])

    if seen_ids != set(ids):
        raise FixEvidenceError(f"{path}: coverage and entries differ")
    strings(doc["rules"], f"{path}: rules")
    return doc


def validate_compare(raw: Any, reviewed_head: str, fix_head: str) -> None:
    if not isinstance(raw, dict):
        raise FixEvidenceError("reviewed-to-fix compare is unavailable")
    status = nonempty(raw.get("status"), "reviewed-to-fix compare status")
    base_sha = sha40(((raw.get("base_commit") or {}).get("sha")), "reviewed-to-fix base")
    merge_base = sha40(((raw.get("merge_base_commit") or {}).get("sha")), "reviewed-to-fix merge base")
    if status != "ahead" or base_sha != reviewed_head or merge_base != reviewed_head:
        raise FixEvidenceError(
            f"fix head {fix_head} is not an exact descendant of reviewed head; status={status} base={base_sha} merge_base={merge_base}"
        )


def validate_source(entry: dict[str, Any], finding: dict[str, Any], snapshot: dict[str, Any]) -> list[str]:
    errors = base.validate_normalized_source(entry, finding)
    finding_id = entry["finding_id"]

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(f"{finding_id}: {message}")

    check(snapshot.get("repository") == entry["repository"], "snapshot repository differs")
    check(snapshot.get("pr_number") == entry["pr"], "snapshot PR differs")
    pr = snapshot.get("pull_request") or {}
    check(pr.get("number") == entry["pr"], "live PR number differs")
    check(pr.get("state") == "closed", "source PR is not closed")
    check(pr.get("merged_at") is not None, "source PR is not merged")

    github = entry["github_evidence"]
    reviews = {item.get("id"): item for item in snapshot.get("reviews", []) if isinstance(item, dict)}
    comments = {item.get("id"): item for item in snapshot.get("review_comments", []) if isinstance(item, dict)}
    review = reviews.get(github["codex_review_id"])
    comment = comments.get(github["codex_review_comment_id"])
    check(review is not None, "exact original Codex review is absent")
    if review:
        check(review.get("commit_id") == entry["reviewed_head"], "original Codex review commit differs")
        check(((review.get("user") or {}).get("login")) == CODEX_LOGIN, "original review actor differs")
    check(comment is not None, "exact original Codex finding is absent")
    if comment:
        check(comment.get("pull_request_review_id") == github["codex_review_id"], "original finding review id differs")
        # GitHub may relocate an outdated inline comment onto the merged PR's later
        # head while preserving original_commit_id. Treat original_commit_id plus the
        # exact review submission as the immutable historical binding, but require
        # any current relocation to be either the original reviewed head or live final
        # PR head rather than an arbitrary commit.
        current_commit = comment.get("commit_id")
        live_final_head = ((pr.get("head") or {}).get("sha"))
        check(
            current_commit in {entry["reviewed_head"], live_final_head},
            "original finding commit differs",
        )
        check(comment.get("original_commit_id") == entry["reviewed_head"], "original finding original_commit differs")
        check(((comment.get("user") or {}).get("login")) == CODEX_LOGIN, "original finding actor differs")

    fix_head = entry["fix_evidence"]["fix_head"]
    commit_ids = {
        item.get("sha") for item in snapshot.get("commits", []) if isinstance(item, dict)
    }
    check(fix_head in commit_ids, "declared fix commit is not a commit of the exact source PR")
    return errors


def resolve_and_validate_live(client: base.GitHubClient, entry: dict[str, Any], snapshot: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    finding_id = entry["finding_id"]
    owner, name = base.split_repository(entry["repository"])
    prefix = f"/repos/{owner}/{name}"
    pr = snapshot.get("pull_request") or {}
    pr_owner = ((pr.get("user") or {}).get("login"))
    if not pr_owner:
        return [f"{finding_id}: PR owner identity is unavailable"]
    github = entry["github_evidence"]
    fix = entry["fix_evidence"]
    fix_head = fix["fix_head"]

    try:
        validate_compare(
            client.get(f"{prefix}/compare/{entry['reviewed_head']}...{fix_head}"),
            entry["reviewed_head"],
            fix_head,
        )

        owner_reply = client.get(f"{prefix}/pulls/comments/{github['owner_reply_comment_id']}")
        if not isinstance(owner_reply, dict) or owner_reply.get("id") != github["owner_reply_comment_id"]:
            raise FixEvidenceError("exact owner reply is unavailable")
        if owner_reply.get("in_reply_to_id") != github["codex_review_comment_id"]:
            errors.append(f"{finding_id}: owner reply does not target exact original finding")
        if ((owner_reply.get("user") or {}).get("login")) != pr_owner:
            errors.append(f"{finding_id}: owner reply actor differs from PR owner")
        if owner_reply.get("original_commit_id") != entry["reviewed_head"]:
            errors.append(f"{finding_id}: owner reply lost original finding-head binding")
        if not str(owner_reply.get("pull_request_url") or "").endswith(f"/pulls/{entry['pr']}"):
            errors.append(f"{finding_id}: owner reply is not bound to exact PR")
        if fix_head not in str(owner_reply.get("body") or ""):
            errors.append(f"{finding_id}: owner reply does not name full exact fix head")

        commit = client.get(f"{prefix}/commits/{fix_head}")
        if not isinstance(commit, dict) or commit.get("sha") != fix_head:
            raise FixEvidenceError("exact fix commit lookup failed")
        changed = sorted(
            item.get("filename") for item in commit.get("files", []) if isinstance(item, dict)
        )
        if changed != sorted(fix["changed_files"]):
            errors.append(f"{finding_id}: exact fix-commit changed-file inventory differs")

        for assertion in fix["content_assertions"]:
            text = base.fetch_text_file(client, entry["repository"], assertion["path"], fix_head)
            for token in assertion["required_present"]:
                if token not in text:
                    errors.append(f"{finding_id}: {assertion['path']} is missing required token {token!r}")
            for token in assertion["required_absent"]:
                if token in text:
                    errors.append(f"{finding_id}: {assertion['path']} contains forbidden token {token!r}")
    except Exception as exc:
        errors.append(f"{finding_id}: live same-PR fix-evidence verification failed: {exc}")
    return errors


def verify(findings_path: Path, reconciliation_path: Path, source_manifest_path: Path, client: base.GitHubClient) -> dict[str, Any]:
    findings = base.load_tuple_jsonl(findings_path, base.FINDING_COLUMNS)
    findings_by_id = base.index_unique(findings, "finding_id", "finding_id")
    doc = load_document(reconciliation_path, source_manifest_path)
    snapshots: dict[tuple[str, int], dict[str, Any]] = {}
    errors: list[str] = []
    summaries: list[dict[str, Any]] = []
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
        summaries.append({
            "finding_id": entry["finding_id"],
            "reconciliation_status": entry["reconciliation_status"],
            "status": "PASS" if not entry_errors else "FAIL",
        })
    return {
        "schema_version": "bootstrap_commentary_fix_evidence_reconciliation_check_v1",
        "authority": "derived_live_verification_not_source_truth",
        "source_artifact_sha256": doc["source_artifact_sha256"],
        "scope": doc["coverage"],
        "entries_checked": len(summaries),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "entries": summaries,
        "limitations": [
            "owner fixed prose is not accepted without exact thread, commit, inventory, ancestry, and immutable content evidence",
            "GitHub current commit_id relocation for historical inline comments is not treated as the immutable reviewed-head identity; original_commit_id plus the exact review submission is",
            "later reviewer silence is not used as proof that an old defect is fixed",
            "material same-PR fix evidence is not universal semantic correctness proof",
            "does not modify authenticated bootstrap-v1 source projections",
            "does not claim global source-commentary reconciliation is complete",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify bounded same-PR material fix evidence reconciliation.")
    parser.add_argument("--findings", type=Path, default=Path("data/findings.jsonl"))
    parser.add_argument("--reconciliation", type=Path, default=Path("data/bootstrap-commentary-fix-evidence-reconciliation.json"))
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
        print(f"bootstrap commentary fix-evidence reconciliation verification failed: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
