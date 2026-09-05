#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import verify_bootstrap_commentary_reconciliation as base

SCHEMA_VERSION = "bootstrap_commentary_multi_review_progression_reconciliation_v1"
AUTHORITY = "governed_reconciliation_of_authenticated_source_commentary"
KIND = "supported_same_pr_multi_review_progression_evidence"
STATUS = "SUPPORTED_SAME_PR_MULTI_REVIEW_PROGRESSION_EVIDENCE"
CODEX_LOGIN = "chatgpt-codex-connector[bot]"

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
    "related_followup_finding_ids",
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
    "initial_fix_evidence",
    "followup_reviews",
    "reconciliation_status",
    "authority_limit",
}
RANGE_FIELDS = {
    "codex_review_id",
    "codex_review_comment_id",
    "owner_reply_comment_id",
    "response_head",
    "expected_compare_commit_count",
    "required_changed_files",
    "content_assertions",
}
FOLLOWUP_FIELDS = RANGE_FIELDS | {
    "finding_id",
    "relation",
    "reviewed_head",
    "source_row",
}
ASSERTION_FIELDS = {"path", "required_present", "required_absent"}

EXPECTED_ROOT = {
    "finding_id": "F057",
    "repository": "BogdanAIP/uv-studio",
    "pr": 71,
    "reviewed_head": "aafddd3b37476a65558d56755edd2ae440648b74",
    "source_row": 58,
    "source_confirmed": "CONFIRMED",
    "source_note": "Fixed by complete typed delegation matching and later stronger namespace reservation.",
    "codex_review_id": 5043917353,
    "codex_review_comment_id": 3874358356,
    "owner_reply_comment_id": 3874611686,
    "response_head": "9af22cdcbb60501dca968fd10f12dc1d40ee6482",
    "expected_compare_commit_count": 4,
}
EXPECTED_FOLLOWUPS = [
    {
        "finding_id": "F059",
        "relation": "DISTINCT_STRONGER_NAMESPACE_FINDING",
        "reviewed_head": "10643bd160c65b8d8df690266390725d5d0dd6eb",
        "source_row": 60,
        "codex_review_id": 5044266036,
        "codex_review_comment_id": 3874658738,
        "owner_reply_comment_id": 3874859175,
        "response_head": "7c8280721d96e7822d3c56e08e00ff6cb3868349",
        "expected_compare_commit_count": 2,
    },
    {
        "finding_id": "F061",
        "relation": "DISTINCT_FURTHER_NAMESPACE_FINDING",
        "reviewed_head": "7c8280721d96e7822d3c56e08e00ff6cb3868349",
        "source_row": 62,
        "codex_review_id": 5044434417,
        "codex_review_comment_id": 3874801219,
        "owner_reply_comment_id": 3875173639,
        "response_head": "1467bd3c97511f8349b574d00a6029e8e98b3fe7",
        "expected_compare_commit_count": 11,
    },
]


class MultiReviewProgressionError(RuntimeError):
    pass


def exact_object(raw: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise MultiReviewProgressionError(f"{label} must be an object")
    if set(raw) != fields:
        raise MultiReviewProgressionError(
            f"{label} shape mismatch; missing={sorted(fields - set(raw))} "
            f"unknown={sorted(set(raw) - fields)}"
        )
    return raw


def positive_int(value: Any, label: str) -> int:
    try:
        return base.require_positive_int(value, label)
    except Exception as exc:
        raise MultiReviewProgressionError(str(exc)) from exc


def nonempty(value: Any, label: str) -> str:
    try:
        return base.require_nonempty_string(value, label)
    except Exception as exc:
        raise MultiReviewProgressionError(str(exc)) from exc


def sha40(value: Any, label: str) -> str:
    try:
        return base.require_sha(value, label)
    except Exception as exc:
        raise MultiReviewProgressionError(str(exc)) from exc


def strings(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    try:
        return base.require_string_array(value, label, allow_empty=allow_empty)
    except Exception as exc:
        raise MultiReviewProgressionError(str(exc)) from exc


def _validate_assertions(raw: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        raise MultiReviewProgressionError(f"{label} must be a non-empty array")
    result: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for index, item in enumerate(raw, start=1):
        assertion = exact_object(item, ASSERTION_FIELDS, f"{label}[{index}]")
        path = nonempty(assertion["path"], f"{label}[{index}].path")
        if path in seen_paths:
            raise MultiReviewProgressionError(f"{label}: duplicate assertion path {path!r}")
        seen_paths.add(path)
        present = strings(assertion["required_present"], f"{label}[{index}].required_present")
        absent = strings(
            assertion["required_absent"],
            f"{label}[{index}].required_absent",
            allow_empty=True,
        )
        if set(present) & set(absent):
            raise MultiReviewProgressionError(f"{label}[{index}]: contradictory tokens")
        result.append(assertion)
    return result


def _validate_range_shape(
    raw: Any,
    fields: set[str],
    label: str,
    expected: dict[str, Any],
) -> dict[str, Any]:
    item = exact_object(raw, fields, label)
    for key in (
        "codex_review_id",
        "codex_review_comment_id",
        "owner_reply_comment_id",
        "expected_compare_commit_count",
    ):
        positive_int(item[key], f"{label}.{key}")
        if item[key] != expected[key]:
            raise MultiReviewProgressionError(f"{label}: {key} differs from bounded contract")
    sha40(item["response_head"], f"{label}.response_head")
    if item["response_head"] != expected["response_head"]:
        raise MultiReviewProgressionError(f"{label}: response_head differs from bounded contract")
    required_files = strings(item["required_changed_files"], f"{label}.required_changed_files")
    if len(required_files) != len(set(required_files)):
        raise MultiReviewProgressionError(f"{label}: duplicate required changed file")
    assertions = _validate_assertions(item["content_assertions"], f"{label}.content_assertions")
    if not {assertion["path"] for assertion in assertions}.issubset(set(required_files)):
        raise MultiReviewProgressionError(
            f"{label}: every content assertion must target a required changed file"
        )
    return item


def load_document(path: Path, source_manifest_path: Path) -> dict[str, Any]:
    doc = exact_object(json.loads(path.read_text(encoding="utf-8")), TOP_FIELDS, str(path))
    if doc["schema_version"] != SCHEMA_VERSION or doc["authority"] != AUTHORITY:
        raise MultiReviewProgressionError(f"{path}: unsupported schema/authority")

    manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    if doc["source_artifact_sha256"] != manifest.get("sha256"):
        raise MultiReviewProgressionError(f"{path}: source artifact digest mismatch")

    coverage = exact_object(doc["coverage"], COVERAGE_FIELDS, f"{path}: coverage")
    if coverage["kind"] != "bounded_same_pr_multi_review_progression_slice":
        raise MultiReviewProgressionError(f"{path}: unsupported coverage kind")
    if coverage["source_sheet"] != "Findings":
        raise MultiReviewProgressionError(f"{path}: coverage must be bound to Findings")
    if strings(coverage["finding_ids"], f"{path}: finding_ids") != ["F057"]:
        raise MultiReviewProgressionError(f"{path}: bounded root scope must be exactly F057")
    if strings(
        coverage["related_followup_finding_ids"],
        f"{path}: related_followup_finding_ids",
    ) != ["F059", "F061"]:
        raise MultiReviewProgressionError(
            f"{path}: bounded follow-up scope must preserve distinct F059/F061 identities"
        )
    if coverage["complete_for_scope"] is not True:
        raise MultiReviewProgressionError(f"{path}: complete_for_scope must be true")
    if coverage["global_commentary_reconciliation_complete"] is not False:
        raise MultiReviewProgressionError(f"{path}: bounded slice cannot claim global completion")

    entries = doc["entries"]
    if not isinstance(entries, list) or len(entries) != 1:
        raise MultiReviewProgressionError(f"{path}: entries must contain exactly F057")
    entry = exact_object(entries[0], ENTRY_FIELDS, f"{path}: F057")
    if entry["source_sheet"] != "Findings" or entry["kind"] != KIND:
        raise MultiReviewProgressionError(f"{path}: unsupported F057 source/kind")
    if entry["reconciliation_status"] != STATUS:
        raise MultiReviewProgressionError(f"{path}: unsupported reconciliation status")
    nonempty(entry["authority_limit"], f"{path}: authority_limit")
    positive_int(entry["pr"], f"{path}: pr")
    positive_int(entry["source_row"], f"{path}: source_row")
    sha40(entry["reviewed_head"], f"{path}: reviewed_head")
    for field in (
        "finding_id",
        "repository",
        "pr",
        "reviewed_head",
        "source_row",
        "source_confirmed",
        "source_note",
    ):
        if entry[field] != EXPECTED_ROOT[field]:
            raise MultiReviewProgressionError(f"{path}: root {field} differs from bounded contract")

    _validate_range_shape(
        entry["initial_fix_evidence"],
        RANGE_FIELDS,
        f"{path}: initial_fix_evidence",
        EXPECTED_ROOT,
    )

    followups = entry["followup_reviews"]
    if not isinstance(followups, list) or len(followups) != 2:
        raise MultiReviewProgressionError(f"{path}: followup_reviews must contain exactly F059 and F061")
    for index, expected in enumerate(EXPECTED_FOLLOWUPS):
        label = f"{path}: followup_reviews[{index}]"
        item = _validate_range_shape(followups[index], FOLLOWUP_FIELDS, label, expected)
        for field in ("finding_id", "relation", "reviewed_head", "source_row"):
            if item[field] != expected[field]:
                raise MultiReviewProgressionError(f"{label}: {field} differs from bounded contract")
        sha40(item["reviewed_head"], f"{label}.reviewed_head")
        positive_int(item["source_row"], f"{label}.source_row")

    ids = [entry["finding_id"], *(item["finding_id"] for item in followups)]
    if len(ids) != len(set(ids)):
        raise MultiReviewProgressionError(f"{path}: progression must preserve distinct finding IDs")

    strings(doc["rules"], f"{path}: rules")
    return doc


def _validate_finding_record(
    finding: dict[str, Any] | None,
    *,
    finding_id: str,
    reviewed_head: str,
    source_row: int,
) -> list[str]:
    if finding is None:
        return [f"{finding_id}: normalized finding does not exist"]
    errors: list[str] = []
    expected = {
        "finding_id": finding_id,
        "repository": "BogdanAIP/uv-studio",
        "pr": 71,
        "head_sha": reviewed_head,
        "reviewer": "Codex Review",
        "severity": "P2",
        "confirmed": "CONFIRMED",
        "category": "Identity / namespace",
        "source_url": "https://github.com/BogdanAIP/uv-studio/pull/71",
        "source_row": source_row,
    }
    for field, value in expected.items():
        if finding.get(field) != value:
            errors.append(f"{finding_id}: normalized {field} differs")
    return errors


def _validate_review_binding(
    *,
    finding_id: str,
    reviewed_head: str,
    review_id: int,
    comment_id: int,
    reviews: dict[int, dict[str, Any]],
    comments: dict[int, dict[str, Any]],
    live_final_head: str | None,
) -> list[str]:
    errors: list[str] = []
    review = reviews.get(review_id)
    comment = comments.get(comment_id)
    if review is None:
        errors.append(f"{finding_id}: exact Codex review is absent")
    else:
        if review.get("commit_id") != reviewed_head:
            errors.append(f"{finding_id}: Codex review commit differs")
        if ((review.get("user") or {}).get("login")) != CODEX_LOGIN:
            errors.append(f"{finding_id}: Codex review actor differs")
    if comment is None:
        errors.append(f"{finding_id}: exact Codex finding comment is absent")
    else:
        if comment.get("pull_request_review_id") != review_id:
            errors.append(f"{finding_id}: finding review id differs")
        if comment.get("original_commit_id") != reviewed_head:
            errors.append(f"{finding_id}: finding original_commit differs")
        if comment.get("commit_id") not in {reviewed_head, live_final_head}:
            errors.append(f"{finding_id}: finding current commit is not reviewed/live-final head")
        if ((comment.get("user") or {}).get("login")) != CODEX_LOGIN:
            errors.append(f"{finding_id}: finding actor differs")
    return errors


def validate_source(
    entry: dict[str, Any],
    findings_by_id: dict[str, dict[str, Any]],
    snapshot: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    root = findings_by_id.get("F057")
    if root is None:
        errors.append("F057: normalized finding does not exist")
    else:
        errors.extend(base.validate_normalized_source(entry, root))
        errors.extend(
            _validate_finding_record(
                root,
                finding_id="F057",
                reviewed_head=entry["reviewed_head"],
                source_row=entry["source_row"],
            )
        )

    if snapshot.get("repository") != entry["repository"]:
        errors.append("F057: snapshot repository differs")
    if snapshot.get("pr_number") != entry["pr"]:
        errors.append("F057: snapshot PR differs")
    pr = snapshot.get("pull_request") or {}
    if pr.get("number") != entry["pr"]:
        errors.append("F057: live PR number differs")
    if pr.get("state") != "closed" or pr.get("merged_at") is None:
        errors.append("F057: source PR is not closed+merged")
    live_final_head = ((pr.get("head") or {}).get("sha"))

    reviews = {
        item.get("id"): item
        for item in snapshot.get("reviews", [])
        if isinstance(item, dict) and isinstance(item.get("id"), int)
    }
    comments = {
        item.get("id"): item
        for item in snapshot.get("review_comments", [])
        if isinstance(item, dict) and isinstance(item.get("id"), int)
    }
    commit_ids = {
        item.get("sha")
        for item in snapshot.get("commits", [])
        if isinstance(item, dict) and isinstance(item.get("sha"), str)
    }

    initial = entry["initial_fix_evidence"]
    errors.extend(
        _validate_review_binding(
            finding_id="F057",
            reviewed_head=entry["reviewed_head"],
            review_id=initial["codex_review_id"],
            comment_id=initial["codex_review_comment_id"],
            reviews=reviews,
            comments=comments,
            live_final_head=live_final_head,
        )
    )
    if initial["response_head"] not in commit_ids:
        errors.append("F057: initial response head is not a commit of source PR")

    for followup in entry["followup_reviews"]:
        finding_id = followup["finding_id"]
        errors.extend(
            _validate_finding_record(
                findings_by_id.get(finding_id),
                finding_id=finding_id,
                reviewed_head=followup["reviewed_head"],
                source_row=followup["source_row"],
            )
        )
        errors.extend(
            _validate_review_binding(
                finding_id=finding_id,
                reviewed_head=followup["reviewed_head"],
                review_id=followup["codex_review_id"],
                comment_id=followup["codex_review_comment_id"],
                reviews=reviews,
                comments=comments,
                live_final_head=live_final_head,
            )
        )
        if followup["response_head"] not in commit_ids:
            errors.append(f"{finding_id}: response head is not a commit of source PR")

    return errors


def _validate_compare(
    raw: Any,
    *,
    finding_id: str,
    reviewed_head: str,
    response_head: str,
    expected_commit_count: int,
    required_changed_files: list[str],
) -> list[str]:
    if not isinstance(raw, dict):
        return [f"{finding_id}: reviewed-to-response compare is unavailable"]
    errors: list[str] = []
    if raw.get("status") != "ahead":
        errors.append(f"{finding_id}: response head is not reported ahead of reviewed head")
    if ((raw.get("base_commit") or {}).get("sha")) != reviewed_head:
        errors.append(f"{finding_id}: compare base differs from reviewed head")
    if ((raw.get("merge_base_commit") or {}).get("sha")) != reviewed_head:
        errors.append(f"{finding_id}: compare merge base differs from reviewed head")

    commits = raw.get("commits")
    if not isinstance(commits, list):
        errors.append(f"{finding_id}: compare commit list is unavailable")
    else:
        shas = [item.get("sha") for item in commits if isinstance(item, dict)]
        if len(shas) != expected_commit_count:
            errors.append(f"{finding_id}: compare commit count differs")
        if not shas or shas[-1] != response_head:
            errors.append(f"{finding_id}: compare does not terminate at exact response head")

    files = raw.get("files")
    if not isinstance(files, list):
        errors.append(f"{finding_id}: compare file inventory is unavailable")
    else:
        filenames = {
            item.get("filename")
            for item in files
            if isinstance(item, dict) and isinstance(item.get("filename"), str)
        }
        missing = sorted(set(required_changed_files) - filenames)
        if missing:
            errors.append(f"{finding_id}: compare is missing required changed files {missing}")
    return errors


def _validate_live_stage(
    client: base.GitHubClient,
    *,
    repository: str,
    pr_number: int,
    pr_owner: str,
    finding_id: str,
    reviewed_head: str,
    stage: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    owner, name = base.split_repository(repository)
    prefix = f"/repos/{owner}/{name}"
    response_head = stage["response_head"]
    try:
        compare = client.get(f"{prefix}/compare/{reviewed_head}...{response_head}")
        errors.extend(
            _validate_compare(
                compare,
                finding_id=finding_id,
                reviewed_head=reviewed_head,
                response_head=response_head,
                expected_commit_count=stage["expected_compare_commit_count"],
                required_changed_files=stage["required_changed_files"],
            )
        )

        reply = client.get(f"{prefix}/pulls/comments/{stage['owner_reply_comment_id']}")
        if not isinstance(reply, dict) or reply.get("id") != stage["owner_reply_comment_id"]:
            errors.append(f"{finding_id}: exact owner reply is unavailable")
        else:
            if reply.get("in_reply_to_id") != stage["codex_review_comment_id"]:
                errors.append(f"{finding_id}: owner reply does not target exact finding")
            if ((reply.get("user") or {}).get("login")) != pr_owner:
                errors.append(f"{finding_id}: owner reply actor differs from PR owner")
            if not str(reply.get("pull_request_url") or "").endswith(f"/pulls/{pr_number}"):
                errors.append(f"{finding_id}: owner reply is not bound to exact PR")
            if response_head not in str(reply.get("body") or ""):
                errors.append(f"{finding_id}: owner reply does not name full exact response head")

        commit = client.get(f"{prefix}/commits/{response_head}")
        if not isinstance(commit, dict) or commit.get("sha") != response_head:
            errors.append(f"{finding_id}: exact response commit lookup failed")

        for assertion in stage["content_assertions"]:
            text = base.fetch_text_file(client, repository, assertion["path"], response_head)
            for token in assertion["required_present"]:
                if token not in text:
                    errors.append(
                        f"{finding_id}: {assertion['path']} is missing required token {token!r}"
                    )
            for token in assertion["required_absent"]:
                if token in text:
                    errors.append(
                        f"{finding_id}: {assertion['path']} contains forbidden token {token!r}"
                    )
    except Exception as exc:
        errors.append(f"{finding_id}: live progression verification failed: {exc}")
    return errors


def resolve_and_validate_live(
    client: base.GitHubClient,
    entry: dict[str, Any],
    snapshot: dict[str, Any],
) -> list[str]:
    pr = snapshot.get("pull_request") or {}
    pr_owner = ((pr.get("user") or {}).get("login"))
    if not isinstance(pr_owner, str) or not pr_owner:
        return ["F057: PR owner identity is unavailable"]

    errors = _validate_live_stage(
        client,
        repository=entry["repository"],
        pr_number=entry["pr"],
        pr_owner=pr_owner,
        finding_id="F057",
        reviewed_head=entry["reviewed_head"],
        stage=entry["initial_fix_evidence"],
    )
    for followup in entry["followup_reviews"]:
        errors.extend(
            _validate_live_stage(
                client,
                repository=entry["repository"],
                pr_number=entry["pr"],
                pr_owner=pr_owner,
                finding_id=followup["finding_id"],
                reviewed_head=followup["reviewed_head"],
                stage=followup,
            )
        )
    return errors


def verify(
    findings_path: Path,
    reconciliation_path: Path,
    source_manifest_path: Path,
    client: base.GitHubClient,
) -> dict[str, Any]:
    findings = base.load_tuple_jsonl(findings_path, base.FINDING_COLUMNS)
    findings_by_id = base.index_unique(findings, "finding_id", "finding_id")
    doc = load_document(reconciliation_path, source_manifest_path)
    entry = doc["entries"][0]
    snapshot = base.build_snapshot(client, entry["repository"], entry["pr"])

    errors = validate_source(entry, findings_by_id, snapshot)
    errors.extend(resolve_and_validate_live(client, entry, snapshot))
    return {
        "schema_version": "bootstrap_commentary_multi_review_progression_reconciliation_check_v1",
        "authority": "derived_live_verification_not_source_truth",
        "source_artifact_sha256": doc["source_artifact_sha256"],
        "scope": doc["coverage"],
        "entries_checked": 1,
        "related_findings_checked": 2,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "entries": [
            {
                "finding_id": "F057",
                "related_followup_finding_ids": ["F059", "F061"],
                "reconciliation_status": STATUS,
                "status": "PASS" if not errors else "FAIL",
            }
        ],
        "limitations": [
            "F057, F059, and F061 remain distinct findings bound to distinct reviewed heads",
            "later stronger namespace findings do not retroactively collapse the earlier F057 finding identity",
            "owner replies, ancestry, tests, CI, and later reviewer silence are not universal semantic correctness proof",
            "relation labels are bootstrap evidence descriptors and do not instantiate future FINDING_V1 lifecycle semantics",
            "does not modify authenticated bootstrap-v1 source projections",
            "does not claim global source-commentary reconciliation is complete",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify bounded same-PR multi-review progression evidence reconciliation."
    )
    parser.add_argument("--findings", type=Path, default=Path("data/findings.jsonl"))
    parser.add_argument(
        "--reconciliation",
        type=Path,
        default=Path("data/bootstrap-commentary-multi-review-progression-reconciliation.json"),
    )
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
        print(f"bootstrap commentary multi-review progression verification failed: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
