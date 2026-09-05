#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from collect_github_evidence import parse_z
import verify_bootstrap_commentary_multi_review_progression_stage_evidence as stage
from verify_bootstrap_commentary_multi_review_progression_stage_evidence import *  # noqa: F401,F403


def _timestamp(value: Any, label: str, errors: list[str]):
    try:
        if not isinstance(value, str):
            raise ValueError(f"expected UTC timestamp, got {value!r}")
        return parse_z(value)
    except Exception as exc:
        errors.append(f"{label}: timestamp is unavailable or invalid: {exc}")
        return None


def _cross_stage_compare(
    client: stage.base.GitHubClient,
    *,
    prefix: str,
    prior_finding_id: str,
    prior_response_head: str,
    next_finding_id: str,
    next_reviewed_head: str,
) -> list[str]:
    if prior_response_head == next_reviewed_head:
        return []

    errors: list[str] = []
    label = f"{prior_finding_id}->{next_finding_id}"
    try:
        raw = client.get(f"{prefix}/compare/{prior_response_head}...{next_reviewed_head}")
    except Exception as exc:
        return [f"{label}: cross-stage ancestry compare failed: {exc}"]
    if not isinstance(raw, dict):
        return [f"{label}: cross-stage ancestry compare is unavailable"]
    if raw.get("status") != "ahead":
        errors.append(f"{label}: next reviewed head is not reported ahead of prior response head")
    if ((raw.get("base_commit") or {}).get("sha")) != prior_response_head:
        errors.append(f"{label}: cross-stage compare base differs from prior response head")
    if ((raw.get("merge_base_commit") or {}).get("sha")) != prior_response_head:
        errors.append(f"{label}: prior response head is not the cross-stage merge base")
    ahead_by = raw.get("ahead_by")
    if not isinstance(ahead_by, int) or isinstance(ahead_by, bool) or ahead_by < 1:
        errors.append(f"{label}: cross-stage compare ahead_by is unavailable or invalid")
    behind_by = raw.get("behind_by")
    if behind_by != 0:
        errors.append(f"{label}: cross-stage compare reports history behind prior response")
    commits = raw.get("commits")
    if not isinstance(commits, list) or not commits:
        errors.append(f"{label}: cross-stage compare commit list is unavailable")
    else:
        shas = [item.get("sha") for item in commits if isinstance(item, dict)]
        if not shas or shas[-1] != next_reviewed_head:
            errors.append(f"{label}: cross-stage compare does not terminate at next reviewed head")
    return errors


def _validate_cross_stage_progression(
    client: stage.base.GitHubClient,
    entry: dict[str, Any],
    snapshot: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    owner, name = stage.base.split_repository(entry["repository"])
    prefix = f"/repos/{owner}/{name}"

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

    commit_sequence: list[str] = []
    seen_commits: set[str] = set()
    for index, item in enumerate(snapshot.get("commits", []), start=1):
        sha = item.get("sha") if isinstance(item, dict) else None
        if not isinstance(sha, str):
            errors.append(f"progression: source PR commit {index} has no exact SHA")
            continue
        if sha in seen_commits:
            errors.append(f"progression: source PR commit sequence contains duplicate {sha}")
            continue
        seen_commits.add(sha)
        commit_sequence.append(sha)
    commit_position = {sha: index for index, sha in enumerate(commit_sequence)}

    stages = [
        {
            "finding_id": "F057",
            "reviewed_head": entry["reviewed_head"],
            "evidence": entry["initial_fix_evidence"],
        },
        *[
            {
                "finding_id": item["finding_id"],
                "reviewed_head": item["reviewed_head"],
                "evidence": item,
            }
            for item in entry["followup_reviews"]
        ],
    ]

    stage_times: dict[str, dict[str, Any]] = {}
    for item in stages:
        finding_id = item["finding_id"]
        reviewed_head = item["reviewed_head"]
        evidence = item["evidence"]
        response_head = evidence["response_head"]

        for role, sha in (("reviewed head", reviewed_head), ("response head", response_head)):
            if sha not in commit_position:
                errors.append(f"{finding_id}: {role} is absent from exact source PR commit sequence")

        review = reviews.get(evidence["codex_review_id"])
        comment = comments.get(evidence["codex_review_comment_id"])
        review_at = _timestamp(
            review.get("submitted_at") if isinstance(review, dict) else None,
            f"{finding_id}: exact Codex review submitted_at",
            errors,
        )
        comment_at = _timestamp(
            comment.get("created_at") if isinstance(comment, dict) else None,
            f"{finding_id}: exact finding comment created_at",
            errors,
        )

        reply: Any = None
        response_commit: Any = None
        try:
            reply = client.get(f"{prefix}/pulls/comments/{evidence['owner_reply_comment_id']}")
        except Exception as exc:
            errors.append(f"{finding_id}: exact owner reply chronology lookup failed: {exc}")
        try:
            response_commit = client.get(f"{prefix}/commits/{response_head}")
        except Exception as exc:
            errors.append(f"{finding_id}: exact response commit chronology lookup failed: {exc}")

        reply_at = _timestamp(
            reply.get("created_at") if isinstance(reply, dict) else None,
            f"{finding_id}: exact owner reply created_at",
            errors,
        )
        response_commit_at = _timestamp(
            ((((response_commit or {}).get("commit") or {}).get("committer") or {}).get("date"))
            if isinstance(response_commit, dict)
            else None,
            f"{finding_id}: exact response commit committer date",
            errors,
        )

        for source_label, source_time in (
            ("Codex review", review_at),
            ("finding comment", comment_at),
        ):
            if source_time is not None and response_commit_at is not None and response_commit_at < source_time:
                errors.append(f"{finding_id}: response commit predates its {source_label}")
            if source_time is not None and reply_at is not None and reply_at < source_time:
                errors.append(f"{finding_id}: owner reply predates its {source_label}")
        if response_commit_at is not None and reply_at is not None and reply_at < response_commit_at:
            errors.append(f"{finding_id}: owner reply predates the exact response commit it names")

        stage_times[finding_id] = {
            "response_commit_at": response_commit_at,
            "review_at": review_at,
            "comment_at": comment_at,
        }

    for prior, next_stage in zip(stages, stages[1:]):
        prior_finding_id = prior["finding_id"]
        next_finding_id = next_stage["finding_id"]
        prior_response_head = prior["evidence"]["response_head"]
        next_reviewed_head = next_stage["reviewed_head"]
        label = f"{prior_finding_id}->{next_finding_id}"

        prior_position = commit_position.get(prior_response_head)
        next_position = commit_position.get(next_reviewed_head)
        if prior_position is not None and next_position is not None:
            if prior_response_head == next_reviewed_head:
                if prior_position != next_position:
                    errors.append(f"{label}: identical cross-stage head has inconsistent PR position")
            elif prior_position >= next_position:
                errors.append(f"{label}: source PR commit sequence reorders prior response after next review head")

        errors.extend(
            _cross_stage_compare(
                client,
                prefix=prefix,
                prior_finding_id=prior_finding_id,
                prior_response_head=prior_response_head,
                next_finding_id=next_finding_id,
                next_reviewed_head=next_reviewed_head,
            )
        )

        prior_response_at = stage_times.get(prior_finding_id, {}).get("response_commit_at")
        next_review_at = stage_times.get(next_finding_id, {}).get("review_at")
        next_comment_at = stage_times.get(next_finding_id, {}).get("comment_at")
        if prior_response_at is not None and next_review_at is not None and next_review_at < prior_response_at:
            errors.append(f"{label}: next Codex review predates prior exact response commit")
        if prior_response_at is not None and next_comment_at is not None and next_comment_at < prior_response_at:
            errors.append(f"{label}: next finding comment predates prior exact response commit")

    return errors


def verify(
    findings_path: Path,
    reconciliation_path: Path,
    source_manifest_path: Path,
    client: stage.base.GitHubClient,
) -> dict[str, Any]:
    findings = stage.base.load_tuple_jsonl(findings_path, stage.base.FINDING_COLUMNS)
    findings_by_id = stage.base.index_unique(findings, "finding_id", "finding_id")
    doc = stage.load_document(reconciliation_path, source_manifest_path)
    entry = doc["entries"][0]
    snapshot = stage.base.build_snapshot(client, entry["repository"], entry["pr"])

    errors = stage.validate_source(entry, findings_by_id, snapshot)
    errors.extend(stage.resolve_and_validate_live(client, entry, snapshot))
    errors.extend(_validate_cross_stage_progression(client, entry, snapshot))
    return {
        "schema_version": "bootstrap_commentary_multi_review_progression_reconciliation_check_v1",
        "authority": "derived_live_verification_not_source_truth",
        "source_artifact_sha256": doc["source_artifact_sha256"],
        "scope": doc["coverage"],
        "entries_checked": 1,
        "related_findings_checked": 2,
        "cross_stage_links_checked": 2,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "entries": [
            {
                "finding_id": "F057",
                "related_followup_finding_ids": ["F059", "F061"],
                "reconciliation_status": stage.STATUS,
                "status": "PASS" if not errors else "FAIL",
            }
        ],
        "limitations": [
            "F057, F059, and F061 remain distinct findings bound to distinct reviewed heads",
            "cross-stage progression requires prior response-head ancestry/PR ordering into the next reviewed head and response-commit chronology before the next review",
            "each owner reply must postdate its own finding and exact response commit; owner reply posting time is not used as the cross-stage ordering authority because a reply may document an already-existing response after a subsequent review began",
            "later stronger namespace findings do not retroactively collapse the earlier F057 finding identity",
            "owner replies, ancestry, tests, CI, and later reviewer silence are not universal semantic correctness proof",
            "relation labels are bootstrap evidence descriptors and do not instantiate future FINDING_V1 lifecycle semantics",
            "does not modify authenticated bootstrap-v1 source projections",
            "does not claim global source-commentary reconciliation is complete",
        ],
    }


def main() -> int:
    args = stage.parse_args()
    client = stage.base.GitHubClient(token=os.environ.get(args.token_env), api_url=args.api_url)
    try:
        result = verify(args.findings, args.reconciliation, args.source_manifest, client)
    except Exception as exc:
        print(f"bootstrap commentary multi-review progression verification failed: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
