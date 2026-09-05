#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import verify_bootstrap_commentary_reconciliation as base

SCHEMA_VERSION = "bootstrap_commentary_authority_ci_reconciliation_v1"
AUTHORITY = "governed_reconciliation_of_authenticated_source_commentary"
CODEX_LOGIN = "chatgpt-codex-connector[bot]"
REPOSITORY = "BogdanAIP/uv-studio"
PR_NUMBER = 71
REVIEWED_HEAD = "aafddd3b37476a65558d56755edd2ae440648b74"
CODE_DOCS_HEAD = "9af22cdcbb60501dca968fd10f12dc1d40ee6482"
METADATA_HEAD = "10643bd160c65b8d8df690266390725d5d0dd6eb"
WORKFLOW_ID = 331109076
EXPECTED_JOBS = [
    "app-baseline (ubuntu-latest)",
    "app-baseline (windows-latest)",
    "bootstrap (ubuntu-latest, 3.11)",
    "bootstrap (windows-latest, 3.11)",
    "development-context",
]
EXPECTED = {
    "F055": {
        "source_row": 56,
        "source_note": "Current architecture authorities were synchronized to active review state.",
        "review_id": 5043917353,
        "comment_id": 3874358302,
        "reply_id": 3874609972,
        "kind": "supported_same_pr_authority_sync_evidence",
        "status": "SUPPORTED_SAME_PR_AUTHORITY_SYNC_EVIDENCE",
    },
    "F056": {
        "source_row": 57,
        "source_note": "Exact code-bearing and metadata-head CI evidence was rerun and recorded.",
        "review_id": 5043917353,
        "comment_id": 3874358316,
        "reply_id": 3874610894,
        "kind": "supported_exact_head_ci_refresh_evidence",
        "status": "SUPPORTED_EXACT_HEAD_CI_REFRESH_EVIDENCE",
    },
}
EXPECTED_BASELINE_COMMITS = [
    "981bc1a1c4e98d4cb9d98bc9a18ef319c459be57",
    "07d52d21d0dcd6a3e1c9ee4e2e36d34a1ed998be",
    "57518f8fd28744a0c3b3b3051c7093edeba53a06",
    CODE_DOCS_HEAD,
]
EXPECTED_BASELINE_FILES = [
    "docs/architecture/CURRENT_ARCHITECTURE.md",
    "docs/architecture/UV_STUDIO_V2_ARCHITECTURE_MAP.md",
    "tests/test_agent_stage17_result_integrity.py",
    "uv_studio/agent/stage17_provenance.py",
]


class AuthorityCiError(RuntimeError):
    pass


def exact(raw: Any, fields: set[str], label: str) -> dict[str, Any]:
    return base.require_exact_shape(raw, fields, label)


def strings(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    return base.require_string_array(value, label, allow_empty=allow_empty)


def load_document(path: Path, source_manifest_path: Path) -> dict[str, Any]:
    doc = exact(
        json.loads(path.read_text(encoding="utf-8")),
        {"schema_version", "authority", "source_artifact_sha256", "coverage", "entries", "rules"},
        str(path),
    )
    if doc["schema_version"] != SCHEMA_VERSION or doc["authority"] != AUTHORITY:
        raise AuthorityCiError(f"{path}: unsupported schema/authority")
    manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    if doc["source_artifact_sha256"] != manifest.get("sha256"):
        raise AuthorityCiError(f"{path}: source artifact digest mismatch")
    coverage = exact(
        doc["coverage"],
        {"kind", "source_sheet", "finding_ids", "complete_for_scope", "global_commentary_reconciliation_complete"},
        f"{path}: coverage",
    )
    if coverage != {
        "kind": "bounded_same_pr_authority_and_exact_head_ci_slice",
        "source_sheet": "Findings",
        "finding_ids": ["F055", "F056"],
        "complete_for_scope": True,
        "global_commentary_reconciliation_complete": False,
    }:
        raise AuthorityCiError(f"{path}: bounded coverage contract differs")
    entries = doc["entries"]
    if not isinstance(entries, list) or [item.get("finding_id") if isinstance(item, dict) else None for item in entries] != ["F055", "F056"]:
        raise AuthorityCiError(f"{path}: entries must be exactly F055 then F056")
    for entry in entries:
        fid = entry["finding_id"]
        expected = EXPECTED[fid]
        common = {
            "finding_id", "repository", "pr", "reviewed_head", "source_sheet", "source_row",
            "source_confirmed", "source_note", "kind", "github_evidence", "reconciliation_status", "authority_limit",
        }
        evidence_field = "authority_sync_evidence" if fid == "F055" else "exact_head_ci_evidence"
        entry = exact(entry, common | {evidence_field}, f"{path}: {fid}")
        if entry["repository"] != REPOSITORY or entry["pr"] != PR_NUMBER or entry["reviewed_head"] != REVIEWED_HEAD:
            raise AuthorityCiError(f"{path}: {fid} source identity differs")
        if entry["source_sheet"] != "Findings" or entry["source_row"] != expected["source_row"]:
            raise AuthorityCiError(f"{path}: {fid} source row differs")
        if entry["source_confirmed"] != "CONFIRMED" or entry["source_note"] != expected["source_note"]:
            raise AuthorityCiError(f"{path}: {fid} source disposition/note differs")
        if entry["kind"] != expected["kind"] or entry["reconciliation_status"] != expected["status"]:
            raise AuthorityCiError(f"{path}: {fid} kind/status differs")
        base.require_nonempty_string(entry["authority_limit"], f"{path}: {fid} authority_limit")
        gh = exact(entry["github_evidence"], {"codex_review_id", "codex_review_comment_id", "owner_reply_comment_id"}, f"{path}: {fid} github")
        if gh != {"codex_review_id": expected["review_id"], "codex_review_comment_id": expected["comment_id"], "owner_reply_comment_id": expected["reply_id"]}:
            raise AuthorityCiError(f"{path}: {fid} GitHub identities differ")
        if fid == "F055":
            ev = exact(entry[evidence_field], {
                "code_docs_head", "metadata_head", "reviewed_to_code_docs_commits",
                "reviewed_to_code_docs_changed_files", "code_docs_content_assertions", "metadata_content_assertions",
            }, f"{path}: F055 evidence")
            if ev["code_docs_head"] != CODE_DOCS_HEAD or ev["metadata_head"] != METADATA_HEAD:
                raise AuthorityCiError(f"{path}: F055 evidence heads differ")
            if ev["reviewed_to_code_docs_commits"] != EXPECTED_BASELINE_COMMITS or ev["reviewed_to_code_docs_changed_files"] != EXPECTED_BASELINE_FILES:
                raise AuthorityCiError(f"{path}: F055 exact range contract differs")
            _validate_assertions(ev["code_docs_content_assertions"], "F055 code/docs")
            _validate_assertions(ev["metadata_content_assertions"], "F055 metadata")
        else:
            ev = exact(entry[evidence_field], {
                "code_head", "metadata_head", "code_to_metadata_commits", "code_to_metadata_changed_files",
                "workflow_id", "expected_jobs", "runs", "metadata_content_assertions",
            }, f"{path}: F056 evidence")
            if ev["code_head"] != CODE_DOCS_HEAD or ev["metadata_head"] != METADATA_HEAD:
                raise AuthorityCiError(f"{path}: F056 evidence heads differ")
            if ev["code_to_metadata_commits"] != [METADATA_HEAD] or ev["code_to_metadata_changed_files"] != ["project-context/PROJECT_STATE.md"]:
                raise AuthorityCiError(f"{path}: F056 metadata range differs")
            if ev["workflow_id"] != WORKFLOW_ID or ev["expected_jobs"] != EXPECTED_JOBS:
                raise AuthorityCiError(f"{path}: F056 workflow/job contract differs")
            expected_runs = [
                {"role": "code_head", "run_id": 33101350599, "run_number": 3488, "head_sha": CODE_DOCS_HEAD},
                {"role": "metadata_head", "run_id": 33102045907, "run_number": 3490, "head_sha": METADATA_HEAD},
            ]
            if ev["runs"] != expected_runs:
                raise AuthorityCiError(f"{path}: F056 exact run contract differs")
            _validate_assertions(ev["metadata_content_assertions"], "F056 metadata")
    strings(doc["rules"], f"{path}: rules")
    return doc


def _validate_assertions(raw: Any, label: str) -> None:
    if not isinstance(raw, list) or not raw:
        raise AuthorityCiError(f"{label}: assertions must be non-empty")
    seen: set[str] = set()
    for index, item in enumerate(raw, start=1):
        assertion = exact(item, {"path", "required_present", "required_absent"}, f"{label} assertion {index}")
        path = base.require_nonempty_string(assertion["path"], f"{label} path")
        if path in seen:
            raise AuthorityCiError(f"{label}: duplicate assertion path {path}")
        seen.add(path)
        present = strings(assertion["required_present"], f"{label} present")
        absent = strings(assertion["required_absent"], f"{label} absent", allow_empty=True)
        if set(present) & set(absent):
            raise AuthorityCiError(f"{label}: contradictory tokens")


def _validate_historical_binding(entry: dict[str, Any], finding: dict[str, Any], snapshot: dict[str, Any]) -> list[str]:
    errors = base.validate_normalized_source(entry, finding)
    fid = entry["finding_id"]
    pr = snapshot.get("pull_request") or {}
    if snapshot.get("repository") != REPOSITORY or snapshot.get("pr_number") != PR_NUMBER:
        errors.append(f"{fid}: snapshot source identity differs")
    if pr.get("state") != "closed" or pr.get("merged_at") is None:
        errors.append(f"{fid}: exact source PR is not merged/closed")
    gh = entry["github_evidence"]
    reviews = {x.get("id"): x for x in snapshot.get("reviews", []) if isinstance(x, dict)}
    comments = {x.get("id"): x for x in snapshot.get("review_comments", []) if isinstance(x, dict)}
    review = reviews.get(gh["codex_review_id"])
    comment = comments.get(gh["codex_review_comment_id"])
    if not isinstance(review, dict) or review.get("commit_id") != REVIEWED_HEAD or ((review.get("user") or {}).get("login")) != CODEX_LOGIN:
        errors.append(f"{fid}: exact original Codex review binding differs")
    if not isinstance(comment, dict):
        errors.append(f"{fid}: exact original finding is absent")
    else:
        live_final_head = ((pr.get("head") or {}).get("sha"))
        if comment.get("pull_request_review_id") != gh["codex_review_id"]:
            errors.append(f"{fid}: finding review id differs")
        if comment.get("original_commit_id") != REVIEWED_HEAD:
            errors.append(f"{fid}: finding original_commit_id differs")
        if comment.get("commit_id") not in {REVIEWED_HEAD, live_final_head}:
            errors.append(f"{fid}: finding relocated commit is not bounded")
        if ((comment.get("user") or {}).get("login")) != CODEX_LOGIN:
            errors.append(f"{fid}: finding actor differs")
    commits = {x.get("sha") for x in snapshot.get("commits", []) if isinstance(x, dict)}
    for sha in (REVIEWED_HEAD, CODE_DOCS_HEAD, METADATA_HEAD):
        if sha not in commits:
            errors.append(f"{fid}: required source PR commit {sha} is absent")
    return errors


def _validate_owner_reply(client: base.GitHubClient, entry: dict[str, Any], snapshot: dict[str, Any], required_tokens: list[str]) -> list[str]:
    fid = entry["finding_id"]
    errors: list[str] = []
    gh = entry["github_evidence"]
    owner, name = base.split_repository(REPOSITORY)
    prefix = f"/repos/{owner}/{name}"
    try:
        reply = client.get(f"{prefix}/pulls/comments/{gh['owner_reply_comment_id']}")
    except Exception as exc:
        return [f"{fid}: owner reply lookup failed: {exc}"]
    pr_owner = ((((snapshot.get("pull_request") or {}).get("user")) or {}).get("login"))
    if not isinstance(reply, dict) or reply.get("id") != gh["owner_reply_comment_id"]:
        return [f"{fid}: exact owner reply is unavailable"]
    if reply.get("in_reply_to_id") != gh["codex_review_comment_id"]:
        errors.append(f"{fid}: owner reply targets another finding")
    if ((reply.get("user") or {}).get("login")) != pr_owner:
        errors.append(f"{fid}: owner reply actor differs from PR owner")
    if reply.get("original_commit_id") != REVIEWED_HEAD:
        errors.append(f"{fid}: owner reply lost original reviewed-head binding")
    if not str(reply.get("pull_request_url") or "").endswith(f"/pulls/{PR_NUMBER}"):
        errors.append(f"{fid}: owner reply is not bound to source PR")
    body = str(reply.get("body") or "")
    for token in required_tokens:
        if token not in body:
            errors.append(f"{fid}: owner reply does not name required evidence {token!r}")
    return errors


def _validate_compare(raw: Any, base_sha: str, head_sha: str, commits: list[str], files: list[str], label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(raw, dict):
        return [f"{label}: compare unavailable"]
    if raw.get("status") != "ahead" or raw.get("behind_by") != 0:
        errors.append(f"{label}: compare status/behind differs")
    if ((raw.get("base_commit") or {}).get("sha")) != base_sha or ((raw.get("merge_base_commit") or {}).get("sha")) != base_sha:
        errors.append(f"{label}: base/merge-base differs")
    actual_commits = [x.get("sha") for x in raw.get("commits", []) if isinstance(x, dict)] if isinstance(raw.get("commits"), list) else []
    if actual_commits != commits or not actual_commits or actual_commits[-1] != head_sha:
        errors.append(f"{label}: exact commit sequence differs")
    actual_files = sorted(x.get("filename") for x in raw.get("files", []) if isinstance(x, dict) and isinstance(x.get("filename"), str)) if isinstance(raw.get("files"), list) else []
    if actual_files != sorted(files):
        errors.append(f"{label}: changed-file inventory differs")
    return errors


def _validate_assertion_content(client: base.GitHubClient, assertions: list[dict[str, Any]], ref: str, label: str) -> list[str]:
    errors: list[str] = []
    for assertion in assertions:
        try:
            text = base.fetch_text_file(client, REPOSITORY, assertion["path"], ref)
        except Exception as exc:
            errors.append(f"{label}: cannot read {assertion['path']} at {ref}: {exc}")
            continue
        for token in assertion["required_present"]:
            if token not in text:
                errors.append(f"{label}: {assertion['path']} missing {token!r}")
        for token in assertion["required_absent"]:
            if token in text:
                errors.append(f"{label}: {assertion['path']} contains forbidden {token!r}")
    return errors


def _validate_actions_run(public_client: base.GitHubClient, run_spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    run_id = run_spec["run_id"]
    try:
        run = public_client.get(f"/repos/BogdanAIP/uv-studio/actions/runs/{run_id}")
        jobs_payload = public_client.get(f"/repos/BogdanAIP/uv-studio/actions/runs/{run_id}/jobs", {"per_page": 100})
    except Exception as exc:
        return [f"F056: historical Actions run {run_id} lookup failed: {exc}"]
    if not isinstance(run, dict):
        return [f"F056: historical Actions run {run_id} is malformed"]
    expected = {
        "id": run_id,
        "workflow_id": WORKFLOW_ID,
        "run_number": run_spec["run_number"],
        "event": "pull_request",
        "head_sha": run_spec["head_sha"],
        "status": "completed",
        "conclusion": "success",
    }
    for field, value in expected.items():
        if run.get(field) != value:
            errors.append(f"F056: run {run_id} {field} differs: expected={value!r} actual={run.get(field)!r}")
    if ((run.get("repository") or {}).get("full_name")) != REPOSITORY:
        errors.append(f"F056: run {run_id} repository identity differs")
    if run.get("head_branch") != "stage-17/agent-functional-subagents":
        errors.append(f"F056: run {run_id} head branch differs")
    if not isinstance(jobs_payload, dict) or not isinstance(jobs_payload.get("jobs"), list):
        return errors + [f"F056: run {run_id} job list is unavailable"]
    jobs = jobs_payload["jobs"]
    if jobs_payload.get("total_count") != len(jobs):
        errors.append(f"F056: run {run_id} job list is truncated or count differs")
    names = [x.get("name") for x in jobs if isinstance(x, dict)]
    if sorted(names) != sorted(EXPECTED_JOBS) or len(names) != len(set(names)):
        errors.append(f"F056: run {run_id} exact five-job set differs")
    for job in jobs:
        if not isinstance(job, dict) or job.get("name") not in EXPECTED_JOBS:
            continue
        if job.get("status") != "completed" or job.get("conclusion") != "success" or job.get("run_id") != run_id:
            errors.append(f"F056: run {run_id} job {job.get('name')!r} is not exact completed success")
    return errors


def verify(findings_path: Path, reconciliation_path: Path, source_manifest_path: Path, source_client: base.GitHubClient, public_client: base.GitHubClient) -> dict[str, Any]:
    findings = base.load_tuple_jsonl(findings_path, base.FINDING_COLUMNS)
    findings_by_id = base.index_unique(findings, "finding_id", "finding_id")
    doc = load_document(reconciliation_path, source_manifest_path)
    snapshot = base.build_snapshot(source_client, REPOSITORY, PR_NUMBER)
    errors: list[str] = []
    summaries: list[dict[str, Any]] = []
    entries = {entry["finding_id"]: entry for entry in doc["entries"]}

    for fid in ("F055", "F056"):
        entry = entries[fid]
        finding = findings_by_id.get(fid)
        entry_errors = [f"{fid}: normalized finding does not exist"] if finding is None else _validate_historical_binding(entry, finding, snapshot)
        if fid == "F055":
            ev = entry["authority_sync_evidence"]
            entry_errors.extend(_validate_owner_reply(source_client, entry, snapshot, [CODE_DOCS_HEAD, METADATA_HEAD, "33101350599", "33102045907"]))
            try:
                owner, name = base.split_repository(REPOSITORY)
                prefix = f"/repos/{owner}/{name}"
                entry_errors.extend(_validate_compare(source_client.get(f"{prefix}/compare/{REVIEWED_HEAD}...{CODE_DOCS_HEAD}"), REVIEWED_HEAD, CODE_DOCS_HEAD, EXPECTED_BASELINE_COMMITS, EXPECTED_BASELINE_FILES, "F055 reviewed->code/docs"))
                entry_errors.extend(_validate_compare(source_client.get(f"{prefix}/compare/{CODE_DOCS_HEAD}...{METADATA_HEAD}"), CODE_DOCS_HEAD, METADATA_HEAD, [METADATA_HEAD], ["project-context/PROJECT_STATE.md"], "F055 code/docs->metadata"))
            except Exception as exc:
                entry_errors.append(f"F055: exact range lookup failed: {exc}")
            entry_errors.extend(_validate_assertion_content(source_client, ev["code_docs_content_assertions"], CODE_DOCS_HEAD, "F055 code/docs"))
            entry_errors.extend(_validate_assertion_content(source_client, ev["metadata_content_assertions"], METADATA_HEAD, "F055 metadata"))
        else:
            ev = entry["exact_head_ci_evidence"]
            entry_errors.extend(_validate_owner_reply(source_client, entry, snapshot, [CODE_DOCS_HEAD, METADATA_HEAD, "33101350599", "33102045907"]))
            try:
                owner, name = base.split_repository(REPOSITORY)
                prefix = f"/repos/{owner}/{name}"
                entry_errors.extend(_validate_compare(source_client.get(f"{prefix}/compare/{CODE_DOCS_HEAD}...{METADATA_HEAD}"), CODE_DOCS_HEAD, METADATA_HEAD, [METADATA_HEAD], ["project-context/PROJECT_STATE.md"], "F056 code->metadata"))
            except Exception as exc:
                entry_errors.append(f"F056: metadata range lookup failed: {exc}")
            entry_errors.extend(_validate_assertion_content(source_client, ev["metadata_content_assertions"], METADATA_HEAD, "F056 metadata"))
            for run_spec in ev["runs"]:
                entry_errors.extend(_validate_actions_run(public_client, run_spec))
        errors.extend(entry_errors)
        summaries.append({"finding_id": fid, "reconciliation_status": entry["reconciliation_status"], "status": "PASS" if not entry_errors else "FAIL"})

    return {
        "schema_version": "bootstrap_commentary_authority_ci_reconciliation_check_v1",
        "authority": "derived_live_verification_not_source_truth",
        "source_artifact_sha256": doc["source_artifact_sha256"],
        "scope": doc["coverage"],
        "entries_checked": 2,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "entries": summaries,
        "limitations": [
            "F055 and F056 remain distinct findings bound to one historical reviewed head",
            "historical current-architecture synchronization is bounded evidence about that source PR, not current product authority today",
            "historical Actions CI success is execution evidence, not universal semantic correctness proof",
            "historical Actions are read through a separate unauthenticated public GitHub client; the CAP/UV source App permissions remain unchanged and read-only",
            "owner prose, ancestry, CI, and later reviewer silence are not accepted as semantic correctness authority",
            "does not modify authenticated bootstrap-v1 source projections or create learning/baseline/stable state",
            "does not claim global source-commentary reconciliation or Stage 1 completion",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify bounded F055/F056 authority and exact-head CI reconciliation.")
    parser.add_argument("--findings", type=Path, default=Path("data/findings.jsonl"))
    parser.add_argument("--reconciliation", type=Path, default=Path("data/bootstrap-commentary-authority-ci-reconciliation.json"))
    parser.add_argument("--source-manifest", type=Path, default=Path("data/bootstrap-source.json"))
    parser.add_argument("--api-url", default=os.environ.get("GITHUB_API_URL", "https://api.github.com"))
    parser.add_argument("--token-env", default="MIMISEEK_GITHUB_TOKEN")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_client = base.GitHubClient(token=os.environ.get(args.token_env), api_url=args.api_url)
    public_client = base.GitHubClient(token=None, api_url=args.api_url)
    try:
        result = verify(args.findings, args.reconciliation, args.source_manifest, source_client, public_client)
    except Exception as exc:
        print(f"bootstrap commentary authority/CI reconciliation verification failed: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
