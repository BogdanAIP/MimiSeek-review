#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import verify_bootstrap_commentary_reconciliation as base

SCHEMA_VERSION = "bootstrap_commentary_fix_baseline_reconciliation_v1"
AUTHORITY = "governed_reconciliation_of_authenticated_source_commentary"
KIND = "supported_same_pr_material_fix_baseline_evidence"
STATUS = "SUPPORTED_SAME_PR_MATERIAL_FIX_BASELINE_EVIDENCE"
CODEX_LOGIN = "chatgpt-codex-connector[bot]"

TOP_FIELDS = {"schema_version", "authority", "source_artifact_sha256", "coverage", "entries", "rules"}
COVERAGE_FIELDS = {
    "kind", "source_sheet", "finding_ids", "complete_for_scope",
    "global_commentary_reconciliation_complete",
}
ENTRY_FIELDS = {
    "finding_id", "repository", "pr", "reviewed_head", "source_sheet", "source_row",
    "source_confirmed", "source_note", "kind", "github_evidence", "baseline_evidence",
    "reconciliation_status", "authority_limit",
}
GITHUB_FIELDS = {"codex_review_id", "codex_review_comment_id", "owner_reply_comment_id"}
BASELINE_FIELDS = {"baseline_head", "reviewed_to_baseline_commits", "changed_files", "content_assertions"}
ASSERTION_FIELDS = {"path", "required_present", "required_absent"}

EXPECTED = {
    "finding_id": "F058",
    "repository": "BogdanAIP/uv-studio",
    "pr": 71,
    "reviewed_head": "aafddd3b37476a65558d56755edd2ae440648b74",
    "source_row": 59,
    "source_confirmed": "CONFIRMED",
    "source_note": "Fixed with exact harness/store/planner authority checks.",
    "codex_review_id": 5043917353,
    "codex_review_comment_id": 3874358367,
    "owner_reply_comment_id": 3874612625,
    "baseline_head": "9af22cdcbb60501dca968fd10f12dc1d40ee6482",
    "reviewed_to_baseline_commits": [
        "981bc1a1c4e98d4cb9d98bc9a18ef319c459be57",
        "07d52d21d0dcd6a3e1c9ee4e2e36d34a1ed998be",
        "57518f8fd28744a0c3b3b3051c7093edeba53a06",
        "9af22cdcbb60501dca968fd10f12dc1d40ee6482",
    ],
    "changed_files": [
        "docs/architecture/CURRENT_ARCHITECTURE.md",
        "docs/architecture/UV_STUDIO_V2_ARCHITECTURE_MAP.md",
        "tests/test_agent_stage17_result_integrity.py",
        "uv_studio/agent/stage17_provenance.py",
    ],
}


class FixBaselineError(RuntimeError):
    pass


def exact_object(raw: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise FixBaselineError(f"{label} must be an object")
    if set(raw) != fields:
        raise FixBaselineError(
            f"{label} shape mismatch; missing={sorted(fields - set(raw))} unknown={sorted(set(raw) - fields)}"
        )
    return raw


def positive_int(value: Any, label: str) -> int:
    try:
        return base.require_positive_int(value, label)
    except Exception as exc:
        raise FixBaselineError(str(exc)) from exc


def nonempty(value: Any, label: str) -> str:
    try:
        return base.require_nonempty_string(value, label)
    except Exception as exc:
        raise FixBaselineError(str(exc)) from exc


def sha40(value: Any, label: str) -> str:
    try:
        return base.require_sha(value, label)
    except Exception as exc:
        raise FixBaselineError(str(exc)) from exc


def strings(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    try:
        return base.require_string_array(value, label, allow_empty=allow_empty)
    except Exception as exc:
        raise FixBaselineError(str(exc)) from exc


def load_document(path: Path, source_manifest_path: Path) -> dict[str, Any]:
    doc = exact_object(json.loads(path.read_text(encoding="utf-8")), TOP_FIELDS, str(path))
    if doc["schema_version"] != SCHEMA_VERSION or doc["authority"] != AUTHORITY:
        raise FixBaselineError(f"{path}: unsupported schema/authority")
    manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    if doc["source_artifact_sha256"] != manifest.get("sha256"):
        raise FixBaselineError(f"{path}: source artifact digest mismatch")

    coverage = exact_object(doc["coverage"], COVERAGE_FIELDS, f"{path}: coverage")
    if coverage["kind"] != "bounded_same_pr_material_fix_baseline_slice":
        raise FixBaselineError(f"{path}: unsupported coverage kind")
    if coverage["source_sheet"] != "Findings":
        raise FixBaselineError(f"{path}: coverage must be bound to Findings")
    ids = strings(coverage["finding_ids"], f"{path}: finding_ids")
    if ids != ["F058"]:
        raise FixBaselineError(f"{path}: this bounded schema is exactly F058")
    if coverage["complete_for_scope"] is not True:
        raise FixBaselineError(f"{path}: complete_for_scope must be true")
    if coverage["global_commentary_reconciliation_complete"] is not False:
        raise FixBaselineError(f"{path}: bounded slice cannot claim global completion")

    entries = doc["entries"]
    if not isinstance(entries, list) or len(entries) != 1:
        raise FixBaselineError(f"{path}: entries must contain exactly F058")
    entry = exact_object(entries[0], ENTRY_FIELDS, f"{path}: F058")
    if entry["finding_id"] != "F058":
        raise FixBaselineError(f"{path}: unsupported finding")
    if entry["source_sheet"] != "Findings" or entry["kind"] != KIND or entry["reconciliation_status"] != STATUS:
        raise FixBaselineError(f"{path}: unsupported source/kind/status")
    nonempty(entry["authority_limit"], f"{path}: authority_limit")
    positive_int(entry["pr"], f"{path}: pr")
    positive_int(entry["source_row"], f"{path}: source_row")
    sha40(entry["reviewed_head"], f"{path}: reviewed_head")
    nonempty(entry["source_confirmed"], f"{path}: source_confirmed")
    nonempty(entry["source_note"], f"{path}: source_note")
    for field in ("repository", "pr", "reviewed_head", "source_row", "source_confirmed", "source_note"):
        if entry[field] != EXPECTED[field]:
            raise FixBaselineError(f"{path}: {field} differs from bounded F058 contract")

    github = exact_object(entry["github_evidence"], GITHUB_FIELDS, f"{path}: github_evidence")
    for field in GITHUB_FIELDS:
        positive_int(github[field], f"{path}: {field}")
        if github[field] != EXPECTED[field]:
            raise FixBaselineError(f"{path}: {field} differs from bounded F058 contract")

    baseline = exact_object(entry["baseline_evidence"], BASELINE_FIELDS, f"{path}: baseline_evidence")
    sha40(baseline["baseline_head"], f"{path}: baseline_head")
    if baseline["baseline_head"] != EXPECTED["baseline_head"]:
        raise FixBaselineError(f"{path}: baseline_head differs from bounded F058 contract")
    commits = strings(baseline["reviewed_to_baseline_commits"], f"{path}: reviewed_to_baseline_commits")
    for index, sha in enumerate(commits, start=1):
        sha40(sha, f"{path}: reviewed_to_baseline_commits[{index}]")
    if commits != EXPECTED["reviewed_to_baseline_commits"]:
        raise FixBaselineError(f"{path}: reviewed-to-baseline commit sequence differs from bounded F058 contract")
    changed_files = strings(baseline["changed_files"], f"{path}: changed_files")
    if changed_files != EXPECTED["changed_files"]:
        raise FixBaselineError(f"{path}: range changed-file inventory differs from bounded F058 contract")
    assertions = baseline["content_assertions"]
    if not isinstance(assertions, list) or not assertions:
        raise FixBaselineError(f"{path}: content_assertions must be non-empty")
    seen_paths: set[str] = set()
    for index, raw_assertion in enumerate(assertions, start=1):
        label = f"{path}: assertion {index}"
        assertion = exact_object(raw_assertion, ASSERTION_FIELDS, label)
        assertion_path = nonempty(assertion["path"], f"{label}: path")
        if assertion_path in seen_paths:
            raise FixBaselineError(f"{path}: duplicate assertion path")
        seen_paths.add(assertion_path)
        present = strings(assertion["required_present"], f"{label}: required_present")
        absent = strings(assertion["required_absent"], f"{label}: required_absent", allow_empty=True)
        if set(present) & set(absent):
            raise FixBaselineError(f"{label}: contradictory tokens")
    if not seen_paths.issubset(set(changed_files)):
        raise FixBaselineError(f"{path}: assertions must target files in the exact reviewed-to-baseline range")
    strings(doc["rules"], f"{path}: rules")
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
        live_final_head = ((pr.get("head") or {}).get("sha"))
        check(comment.get("commit_id") in {entry["reviewed_head"], live_final_head}, "original finding current commit differs")
        check(comment.get("original_commit_id") == entry["reviewed_head"], "original finding original_commit differs")
        check(((comment.get("user") or {}).get("login")) == CODEX_LOGIN, "original finding actor differs")

    baseline_head = entry["baseline_evidence"]["baseline_head"]
    commit_ids = {item.get("sha") for item in snapshot.get("commits", []) if isinstance(item, dict)}
    check(baseline_head in commit_ids, "declared baseline head is not a commit of the exact source PR")
    return errors


def validate_range_compare(raw: Any, entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    reviewed_head = entry["reviewed_head"]
    baseline = entry["baseline_evidence"]
    baseline_head = baseline["baseline_head"]
    if not isinstance(raw, dict):
        return ["reviewed-to-baseline compare is unavailable"]
    try:
        status = nonempty(raw.get("status"), "reviewed-to-baseline compare status")
        base_sha = sha40(((raw.get("base_commit") or {}).get("sha")), "reviewed-to-baseline base")
        merge_base = sha40(((raw.get("merge_base_commit") or {}).get("sha")), "reviewed-to-baseline merge base")
    except Exception as exc:
        return [str(exc)]
    if status != "ahead" or base_sha != reviewed_head or merge_base != reviewed_head:
        errors.append(
            f"baseline head {baseline_head} is not an exact descendant of reviewed head; status={status} base={base_sha} merge_base={merge_base}"
        )
    commits = raw.get("commits")
    if not isinstance(commits, list):
        errors.append("reviewed-to-baseline compare commits are unavailable")
    else:
        actual_commits: list[str] = []
        for index, item in enumerate(commits, start=1):
            if not isinstance(item, dict):
                errors.append(f"reviewed-to-baseline compare commit {index} is malformed")
                continue
            try:
                actual_commits.append(sha40(item.get("sha"), f"reviewed-to-baseline commit {index}"))
            except Exception as exc:
                errors.append(str(exc))
        if actual_commits != baseline["reviewed_to_baseline_commits"]:
            errors.append("exact reviewed-to-baseline commit sequence differs")
        if actual_commits and actual_commits[-1] != baseline_head:
            errors.append("reviewed-to-baseline compare does not terminate at exact declared baseline head")
    files = raw.get("files")
    if not isinstance(files, list):
        errors.append("reviewed-to-baseline compare file inventory is unavailable")
    else:
        actual_files: list[str] = []
        for index, item in enumerate(files, start=1):
            if not isinstance(item, dict):
                errors.append(f"reviewed-to-baseline compare file {index} is malformed")
                continue
            filename = item.get("filename")
            if not isinstance(filename, str) or not filename:
                errors.append(f"reviewed-to-baseline compare file {index} has no filename")
                continue
            actual_files.append(filename)
        if sorted(actual_files) != sorted(baseline["changed_files"]):
            errors.append("exact reviewed-to-baseline range changed-file inventory differs")
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
    baseline = entry["baseline_evidence"]
    baseline_head = baseline["baseline_head"]

    try:
        compare = client.get(f"{prefix}/compare/{entry['reviewed_head']}...{baseline_head}")
        for error in validate_range_compare(compare, entry):
            errors.append(f"{finding_id}: {error}")

        owner_reply = client.get(f"{prefix}/pulls/comments/{github['owner_reply_comment_id']}")
        if not isinstance(owner_reply, dict) or owner_reply.get("id") != github["owner_reply_comment_id"]:
            raise FixBaselineError("exact owner reply is unavailable")
        if owner_reply.get("in_reply_to_id") != github["codex_review_comment_id"]:
            errors.append(f"{finding_id}: owner reply does not target exact original finding")
        if ((owner_reply.get("user") or {}).get("login")) != pr_owner:
            errors.append(f"{finding_id}: owner reply actor differs from PR owner")
        if owner_reply.get("original_commit_id") != entry["reviewed_head"]:
            errors.append(f"{finding_id}: owner reply lost original finding-head binding")
        if not str(owner_reply.get("pull_request_url") or "").endswith(f"/pulls/{entry['pr']}"):
            errors.append(f"{finding_id}: owner reply is not bound to exact PR")
        if baseline_head not in str(owner_reply.get("body") or ""):
            errors.append(f"{finding_id}: owner reply does not name full exact baseline head")

        commit = client.get(f"{prefix}/commits/{baseline_head}")
        if not isinstance(commit, dict) or commit.get("sha") != baseline_head:
            raise FixBaselineError("exact baseline commit lookup failed")

        for assertion in baseline["content_assertions"]:
            text = base.fetch_text_file(client, entry["repository"], assertion["path"], baseline_head)
            for token in assertion["required_present"]:
                if token not in text:
                    errors.append(f"{finding_id}: {assertion['path']} is missing required token {token!r}")
            for token in assertion["required_absent"]:
                if token in text:
                    errors.append(f"{finding_id}: {assertion['path']} contains forbidden token {token!r}")
    except Exception as exc:
        errors.append(f"{finding_id}: live same-PR fix-baseline verification failed: {exc}")
    return errors


def verify(findings_path: Path, reconciliation_path: Path, source_manifest_path: Path, client: base.GitHubClient) -> dict[str, Any]:
    findings = base.load_tuple_jsonl(findings_path, base.FINDING_COLUMNS)
    findings_by_id = base.index_unique(findings, "finding_id", "finding_id")
    doc = load_document(reconciliation_path, source_manifest_path)
    entry = doc["entries"][0]
    finding = findings_by_id.get(entry["finding_id"])
    errors: list[str] = []
    if finding is None:
        errors.append("F058: normalized finding does not exist")
    else:
        snapshot = base.build_snapshot(client, entry["repository"], entry["pr"])
        errors.extend(validate_source(entry, finding, snapshot))
        errors.extend(resolve_and_validate_live(client, entry, snapshot))
    return {
        "schema_version": "bootstrap_commentary_fix_baseline_reconciliation_check_v1",
        "authority": "derived_live_verification_not_source_truth",
        "source_artifact_sha256": doc["source_artifact_sha256"],
        "scope": doc["coverage"],
        "entries_checked": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "entries": [{
            "finding_id": "F058",
            "reconciliation_status": STATUS,
            "status": "PASS" if not errors else "FAIL",
        }],
        "limitations": [
            "the named baseline spans multiple commits and is not misrepresented as one exact fix commit",
            "owner fixed prose is not accepted without exact thread, baseline, ordered range, range inventory, ancestry, and immutable baseline content evidence",
            "later reviewer silence and CI success are not used as semantic correctness proof",
            "material same-PR fix-baseline evidence is not universal semantic correctness proof",
            "does not modify authenticated bootstrap-v1 source projections",
            "does not claim global source-commentary reconciliation is complete",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify bounded same-PR material fix-baseline evidence reconciliation.")
    parser.add_argument("--findings", type=Path, default=Path("data/findings.jsonl"))
    parser.add_argument("--reconciliation", type=Path, default=Path("data/bootstrap-commentary-fix-baseline-reconciliation.json"))
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
        print(f"bootstrap commentary fix-baseline reconciliation verification failed: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
