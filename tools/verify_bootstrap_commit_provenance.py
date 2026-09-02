#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

TOOLS_ROOT = Path(__file__).resolve().parent
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from collect_github_evidence import GitHubClient, build_snapshot  # noqa: E402

SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
RECONCILIATION_SCHEMA = "bootstrap_provenance_reconciliation_v1"
REBASE_KIND = "reviewed_head_rebased_before_fix"

CASE_COLUMNS = [
    "case_id",
    "finding_id",
    "repository",
    "pr",
    "severity",
    "category",
    "known_defect",
    "buggy_base",
    "buggy_head",
    "fix_head",
    "verified_head",
    "historical_source_reviewer",
    "codex_target",
    "codex_basis",
    "our_target",
    "our_extra_confirmed",
    "our_false_positives",
    "buggy_rerun",
    "fixed_rerun",
    "regression_result",
    "disposition",
    "priority",
    "source_url",
    "notes",
    "source_row",
]

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

REBASE_ENTRY_FIELDS = {
    "case_ids",
    "repository",
    "pr",
    "kind",
    "source_buggy_base",
    "reviewed_buggy_head",
    "reviewed_buggy_parent",
    "rebased_fix_lineage_anchor",
    "fix_head",
    "verified_head",
    "source_conflict",
    "github_evidence",
}
REBASE_EVIDENCE_FIELDS = {
    "review_request_issue_comment_id",
    "codex_review_id",
    "codex_review_comment_ids",
}


class ProvenanceError(RuntimeError):
    pass


def require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA40_RE.fullmatch(value):
        raise ProvenanceError(f"{label} must be a 40-character lowercase SHA, got {value!r}")
    return value


def require_positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ProvenanceError(f"{label} must be a positive integer, got {value!r}")
    return value


def load_tuple_jsonl(path: Path, columns: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        raw = json.loads(line)
        if not isinstance(raw, list) or len(raw) != len(columns):
            raise ProvenanceError(
                f"{path}:{line_number}: expected {len(columns)} positional fields, got "
                f"{len(raw) if isinstance(raw, list) else type(raw).__name__}"
            )
        record = dict(zip(columns, raw, strict=True))
        record["_line_number"] = line_number
        records.append(record)
    return records


def index_unique(records: list[dict[str, Any]], key: str, label: str) -> dict[Any, dict[str, Any]]:
    indexed: dict[Any, dict[str, Any]] = {}
    for record in records:
        value = record[key]
        if value in indexed:
            raise ProvenanceError(f"duplicate {label} {value!r}")
        indexed[value] = record
    return indexed


def load_reconciliations(path: Path | None) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    if path is None:
        return {}, []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema_version") != RECONCILIATION_SCHEMA:
        raise ProvenanceError(f"{path}: unsupported reconciliation schema")
    entries = raw.get("entries")
    if not isinstance(entries, list):
        raise ProvenanceError(f"{path}: entries must be an array")

    by_case: dict[str, dict[str, Any]] = {}
    normalized: list[dict[str, Any]] = []
    for entry_index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict) or set(entry) != REBASE_ENTRY_FIELDS:
            raise ProvenanceError(f"{path}: entry {entry_index} has an unexpected shape")
        if entry.get("kind") != REBASE_KIND:
            raise ProvenanceError(f"{path}: entry {entry_index} has unsupported kind {entry.get('kind')!r}")
        repository = entry.get("repository")
        if not isinstance(repository, str) or repository.count("/") != 1:
            raise ProvenanceError(f"{path}: entry {entry_index} has invalid repository")
        require_positive_int(entry.get("pr"), f"{path}: entry {entry_index} pr")
        for field in (
            "source_buggy_base",
            "reviewed_buggy_head",
            "reviewed_buggy_parent",
            "rebased_fix_lineage_anchor",
            "fix_head",
            "verified_head",
        ):
            require_sha(entry.get(field), f"{path}: entry {entry_index} {field}")
        if entry["source_buggy_base"] == entry["reviewed_buggy_parent"]:
            raise ProvenanceError(f"{path}: entry {entry_index} does not describe a base conflict")
        if not isinstance(entry.get("source_conflict"), str) or not entry["source_conflict"].strip():
            raise ProvenanceError(f"{path}: entry {entry_index} source_conflict must be non-empty")

        case_ids = entry.get("case_ids")
        if not isinstance(case_ids, list) or not case_ids or any(
            not isinstance(case_id, str) or not case_id for case_id in case_ids
        ):
            raise ProvenanceError(f"{path}: entry {entry_index} case_ids must be a non-empty string array")
        if len(case_ids) != len(set(case_ids)):
            raise ProvenanceError(f"{path}: entry {entry_index} has duplicate case_ids")

        evidence = entry.get("github_evidence")
        if not isinstance(evidence, dict) or set(evidence) != REBASE_EVIDENCE_FIELDS:
            raise ProvenanceError(f"{path}: entry {entry_index} github_evidence has an unexpected shape")
        require_positive_int(
            evidence.get("review_request_issue_comment_id"),
            f"{path}: entry {entry_index} review_request_issue_comment_id",
        )
        require_positive_int(evidence.get("codex_review_id"), f"{path}: entry {entry_index} codex_review_id")
        comment_ids = evidence.get("codex_review_comment_ids")
        if not isinstance(comment_ids, list) or not comment_ids or any(
            not isinstance(comment_id, int) or isinstance(comment_id, bool) or comment_id < 1
            for comment_id in comment_ids
        ):
            raise ProvenanceError(f"{path}: entry {entry_index} codex_review_comment_ids is invalid")
        if len(comment_ids) != len(set(comment_ids)):
            raise ProvenanceError(f"{path}: entry {entry_index} has duplicate codex review comment ids")
        if len(comment_ids) != len(case_ids):
            raise ProvenanceError(
                f"{path}: entry {entry_index} must bind one original review comment per reconciled case"
            )

        for case_id in case_ids:
            if case_id in by_case:
                raise ProvenanceError(f"{path}: case {case_id} is reconciled more than once")
            by_case[case_id] = entry
        normalized.append(entry)
    return by_case, normalized


def commit_graph(snapshot: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    graph: dict[str, tuple[str, ...]] = {}
    for commit in snapshot.get("commits", []):
        if not isinstance(commit, dict):
            raise ProvenanceError("snapshot commit entry is not an object")
        sha = require_sha(commit.get("sha"), "snapshot commit SHA")
        parents = commit.get("parents")
        if not isinstance(parents, list) or any(
            not isinstance(parent, str) or not SHA40_RE.fullmatch(parent) for parent in parents
        ):
            raise ProvenanceError(f"snapshot contains invalid parents for commit {sha}")
        normalized = tuple(parents)
        if sha in graph and graph[sha] != normalized:
            raise ProvenanceError(f"snapshot contains conflicting duplicate commit {sha}")
        graph[sha] = normalized
    return graph


def live_commit(client: GitHubClient, repository: str, sha: str) -> dict[str, Any]:
    owner, name = repository.split("/", 1)
    raw = client.get(f"/repos/{owner}/{name}/commits/{sha}")
    if not isinstance(raw, dict) or raw.get("sha") != sha:
        raise ProvenanceError(f"live commit lookup did not return exact {repository}@{sha}")
    parents = raw.get("parents")
    if not isinstance(parents, list):
        raise ProvenanceError(f"live commit {repository}@{sha} has invalid parents")
    parent_shas: list[str] = []
    for parent in parents:
        if not isinstance(parent, dict):
            raise ProvenanceError(f"live commit {repository}@{sha} has malformed parent")
        parent_shas.append(require_sha(parent.get("sha"), f"live commit {sha} parent"))
    return {"sha": sha, "parents": tuple(parent_shas), "html_url": raw.get("html_url")}


def is_ancestor(ancestor: str, descendant: str, graph: dict[str, tuple[str, ...]]) -> bool:
    if ancestor == descendant:
        return True
    stack = [descendant]
    seen: set[str] = set()
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        for parent in graph.get(current, ()):  # external base parents are intentionally leaves
            if parent == ancestor:
                return True
            if parent in graph and parent not in seen:
                stack.append(parent)
    return False


def expected_pr_url(repository: str, pr_number: int) -> str:
    return f"https://github.com/{repository}/pull/{pr_number}"


def validate_common_case_identity(
    case: dict[str, Any], finding: dict[str, Any], snapshot: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    case_id = case["case_id"]
    repository = case["repository"]
    pr_number = case["pr"]
    expected_url = expected_pr_url(repository, pr_number)

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(f"{case_id}: {message}")

    check(finding["finding_id"] == case["finding_id"], "finding identity does not resolve")
    check(finding["repository"] == repository, "finding repository differs from regression case")
    check(finding["pr"] == pr_number, "finding PR differs from regression case")
    check(finding["head_sha"] == case["buggy_head"], "finding HEAD is not BUGGY HEAD")
    check(finding["severity"] == case["severity"], "finding severity differs from regression case")
    check(finding["category"] == case["category"], "finding category differs from regression case")
    check(finding["finding"] == case["known_defect"], "finding text differs from known defect")
    check(finding["reviewer"] == case["historical_source_reviewer"], "source reviewer differs")
    check(finding["confirmed"] == "CONFIRMED", "regression target finding is not CONFIRMED")
    check(case["source_url"] == expected_url, "case source URL is not the exact PR URL")
    check(finding["source_url"] == expected_url, "finding source URL is not the exact PR URL")

    authority = snapshot.get("authority") or {}
    check(
        authority.get("role") == "non_authoritative_source_snapshot",
        "live GitHub source snapshot has unexpected authority role",
    )
    check(snapshot.get("repository") == repository, "snapshot repository differs from case")
    check(snapshot.get("pr_number") == pr_number, "snapshot PR number differs from case")

    pull_request = snapshot.get("pull_request") or {}
    base = pull_request.get("base") or {}
    check(pull_request.get("number") == pr_number, "live PR identity number differs")
    check(base.get("repo") == repository, "live PR base repository differs")
    check(base.get("repo_id") == snapshot.get("repository_id"), "repository numeric identity differs")
    check(
        base.get("repo_node_id") == snapshot.get("repository_node_id"),
        "repository node identity differs",
    )
    check((snapshot.get("source") or {}).get("pull_request_url") == expected_url, "snapshot source URL differs")
    return errors


def validate_linear_case(case: dict[str, Any], graph: dict[str, tuple[str, ...]], live_head: Any) -> list[str]:
    errors: list[str] = []
    case_id = case["case_id"]

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(f"{case_id}: {message}")

    for field in ("buggy_head", "fix_head", "verified_head"):
        sha = case[field]
        check(sha in graph, f"{field} {sha} is absent from the live PR commit history")

    if case["buggy_head"] in graph:
        check(
            is_ancestor(case["buggy_base"], case["buggy_head"], graph),
            f"BUGGY BASE {case['buggy_base']} is not an ancestor of BUGGY HEAD {case['buggy_head']}",
        )
    if case["buggy_head"] in graph and case["fix_head"] in graph:
        check(
            is_ancestor(case["buggy_head"], case["fix_head"], graph),
            f"FIX HEAD {case['fix_head']} is not descended from BUGGY HEAD {case['buggy_head']}",
        )
    if case["fix_head"] in graph and case["verified_head"] in graph:
        check(
            is_ancestor(case["fix_head"], case["verified_head"], graph),
            f"VERIFIED HEAD {case['verified_head']} is not descended from FIX HEAD {case['fix_head']}",
        )
    if isinstance(live_head, str) and live_head in graph and case["verified_head"] in graph:
        check(
            is_ancestor(case["verified_head"], live_head, graph),
            f"VERIFIED HEAD {case['verified_head']} is not in the ancestry of live PR HEAD {live_head}",
        )
    return errors


def validate_rebased_case(
    case: dict[str, Any],
    snapshot: dict[str, Any],
    graph: dict[str, tuple[str, ...]],
    reconciliation: dict[str, Any],
    historical_commit: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    case_id = case["case_id"]

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(f"{case_id}: {message}")

    expected_source = {
        "repository": case["repository"],
        "pr": case["pr"],
        "source_buggy_base": case["buggy_base"],
        "reviewed_buggy_head": case["buggy_head"],
        "fix_head": case["fix_head"],
        "verified_head": case["verified_head"],
    }
    for field, expected in expected_source.items():
        check(reconciliation.get(field) == expected, f"reconciliation {field} does not match authenticated source")

    reviewed_head = reconciliation["reviewed_buggy_head"]
    reviewed_parent = reconciliation["reviewed_buggy_parent"]
    rebased_anchor = reconciliation["rebased_fix_lineage_anchor"]
    source_base = reconciliation["source_buggy_base"]
    fix_head = reconciliation["fix_head"]
    verified_head = reconciliation["verified_head"]

    check(historical_commit.get("sha") == reviewed_head, "historical commit lookup returned a different SHA")
    check(
        historical_commit.get("parents") == (reviewed_parent,),
        f"reviewed BUGGY HEAD parent differs from reconciled parent {reviewed_parent}",
    )
    check(reviewed_head not in graph, "rebased exception is no longer detached from final PR history")
    check(rebased_anchor in graph, f"rebased fix lineage anchor {rebased_anchor} is absent from final PR history")
    check(fix_head in graph, f"FIX HEAD {fix_head} is absent from final PR history")
    check(verified_head in graph, f"VERIFIED HEAD {verified_head} is absent from final PR history")
    if rebased_anchor in graph:
        check(
            is_ancestor(source_base, rebased_anchor, graph),
            "source BUGGY BASE is not the base ancestry of the declared rebased fix lineage",
        )
    if rebased_anchor in graph and fix_head in graph:
        check(is_ancestor(rebased_anchor, fix_head, graph), "FIX HEAD is not descended from rebased lineage anchor")
    if fix_head in graph and verified_head in graph:
        check(is_ancestor(fix_head, verified_head, graph), "VERIFIED HEAD is not descended from FIX HEAD")

    live_head = ((snapshot.get("pull_request") or {}).get("head") or {}).get("sha")
    if isinstance(live_head, str) and live_head in graph and verified_head in graph:
        check(is_ancestor(verified_head, live_head, graph), "VERIFIED HEAD is not in live PR HEAD ancestry")

    evidence = reconciliation["github_evidence"]
    issue_comments = {
        item.get("id"): item for item in snapshot.get("issue_comments", []) if isinstance(item, dict)
    }
    reviews = {item.get("id"): item for item in snapshot.get("reviews", []) if isinstance(item, dict)}
    review_comments = {
        item.get("id"): item for item in snapshot.get("review_comments", []) if isinstance(item, dict)
    }

    request = issue_comments.get(evidence["review_request_issue_comment_id"])
    check(request is not None, "exact-head review request issue comment is absent")
    if request is not None:
        check(reviewed_head in (request.get("body") or ""), "review request does not bind the historical BUGGY HEAD")

    review = reviews.get(evidence["codex_review_id"])
    check(review is not None, "Codex review submission is absent")
    if review is not None:
        check(review.get("commit_id") == reviewed_head, "Codex review submission is not bound to BUGGY HEAD")
        check(
            ((review.get("user") or {}).get("login") == "chatgpt-codex-connector[bot]"),
            "review submission actor is not the expected Codex bot",
        )

    expected_comment_ids = set(evidence["codex_review_comment_ids"])
    original_comments: list[dict[str, Any]] = []
    for comment_id in expected_comment_ids:
        comment = review_comments.get(comment_id)
        check(comment is not None, f"original Codex review comment {comment_id} is absent")
        if comment is None:
            continue
        original_comments.append(comment)
        check(comment.get("pull_request_review_id") == evidence["codex_review_id"], f"comment {comment_id} review id differs")
        check(comment.get("commit_id") == reviewed_head, f"comment {comment_id} commit_id differs from BUGGY HEAD")
        check(
            comment.get("original_commit_id") == reviewed_head,
            f"comment {comment_id} original_commit_id differs from BUGGY HEAD",
        )
        check(
            ((comment.get("user") or {}).get("login") == "chatgpt-codex-connector[bot]"),
            f"comment {comment_id} actor is not the expected Codex bot",
        )

    owner = ((snapshot.get("pull_request") or {}).get("user") or {}).get("id")
    replied_to: set[int] = set()
    rebased_reply_present = False
    for comment in review_comments.values():
        parent = comment.get("in_reply_to_id")
        if parent not in expected_comment_ids:
            continue
        if ((comment.get("user") or {}).get("id")) != owner:
            continue
        replied_to.add(parent)
        body = comment.get("body") or ""
        if "rebas" in body.casefold():
            rebased_reply_present = True
    check(replied_to == expected_comment_ids, "not every original Codex finding has an owner reply in its PR thread")
    check(rebased_reply_present, "PR threads do not explicitly preserve the rebase transition")
    return errors


def validate_case(
    case: dict[str, Any],
    finding: dict[str, Any],
    snapshot: dict[str, Any],
    reconciliation: dict[str, Any] | None = None,
    historical_commit: dict[str, Any] | None = None,
) -> list[str]:
    errors = validate_common_case_identity(case, finding, snapshot)
    try:
        graph = commit_graph(snapshot)
    except ProvenanceError as exc:
        return errors + [f"{case['case_id']}: {exc}"]

    if reconciliation is None:
        live_head = ((snapshot.get("pull_request") or {}).get("head") or {}).get("sha")
        return errors + validate_linear_case(case, graph, live_head)
    if reconciliation.get("kind") != REBASE_KIND:
        return errors + [f"{case['case_id']}: unsupported reconciliation kind"]
    if historical_commit is None:
        return errors + [f"{case['case_id']}: reconciled historical commit was not loaded"]
    return errors + validate_rebased_case(case, snapshot, graph, reconciliation, historical_commit)


def reconcile(
    cases_path: Path,
    findings_path: Path,
    client: GitHubClient,
    snapshot_builder: Callable[[GitHubClient, str, int], dict[str, Any]] = build_snapshot,
    reconciliation_path: Path | None = None,
) -> dict[str, Any]:
    cases = load_tuple_jsonl(cases_path, CASE_COLUMNS)
    findings = load_tuple_jsonl(findings_path, FINDING_COLUMNS)
    findings_by_id = index_unique(findings, "finding_id", "finding_id")
    cases_by_id = index_unique(cases, "case_id", "case_id")
    reconciliations_by_case, reconciliation_entries = load_reconciliations(reconciliation_path)

    unknown_reconciled_cases = sorted(set(reconciliations_by_case) - set(cases_by_id))
    if unknown_reconciled_cases:
        raise ProvenanceError(f"reconciliation references unknown cases: {unknown_reconciled_cases}")

    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        finding = findings_by_id.get(case["finding_id"])
        if finding is None:
            raise ProvenanceError(f"{case['case_id']}: unknown finding_id {case['finding_id']}")
        grouped[(case["repository"], case["pr"])].append(case)

    historical_commit_cache: dict[tuple[str, str], dict[str, Any]] = {}
    for entry in reconciliation_entries:
        key = (entry["repository"], entry["reviewed_buggy_head"])
        if key not in historical_commit_cache:
            historical_commit_cache[key] = live_commit(client, *key)

    all_errors: list[str] = []
    pr_summaries: list[dict[str, Any]] = []
    mode_counts: Counter[str] = Counter()
    for repository, pr_number in sorted(grouped):
        snapshot = snapshot_builder(client, repository, pr_number)
        graph = commit_graph(snapshot)
        live_pr = snapshot.get("pull_request") or {}
        case_errors: list[str] = []
        pr_modes: Counter[str] = Counter()
        for case in sorted(grouped[(repository, pr_number)], key=lambda item: item["case_id"]):
            entry = reconciliations_by_case.get(case["case_id"])
            mode = entry["kind"] if entry else "linear_pr_history"
            mode_counts[mode] += 1
            pr_modes[mode] += 1
            historical = None
            if entry:
                historical = historical_commit_cache[(entry["repository"], entry["reviewed_buggy_head"])]
            case_errors.extend(
                validate_case(case, findings_by_id[case["finding_id"]], snapshot, entry, historical)
            )
        all_errors.extend(case_errors)
        pr_summaries.append(
            {
                "repository": repository,
                "repository_id": snapshot.get("repository_id"),
                "pr": pr_number,
                "pr_id": live_pr.get("id"),
                "pr_node_id": live_pr.get("node_id"),
                "live_head": (live_pr.get("head") or {}).get("sha"),
                "commit_count": len(graph),
                "case_count": len(grouped[(repository, pr_number)]),
                "provenance_modes": dict(sorted(pr_modes.items())),
                "status": "PASS" if not case_errors else "FAIL",
            }
        )

    result = {
        "schema_version": "bootstrap_commit_provenance_check_v1",
        "authority": "derived_live_verification_not_source_truth",
        "scope": "structural BUGGY/FIXED/VERIFIED commit identity, PR binding, ancestry and explicit rebase reconciliation only",
        "cases_checked": len(cases),
        "prs_checked": len(grouped),
        "repositories": sorted({case["repository"] for case in cases}),
        "provenance_modes": dict(sorted(mode_counts.items())),
        "reconciliation_entries_checked": len(reconciliation_entries),
        "status": "PASS" if not all_errors else "FAIL",
        "errors": all_errors,
        "pull_requests": pr_summaries,
        "limitations": [
            "does not infer semantic fix correctness from commit ancestry or thread replies",
            "does not alter authenticated bootstrap-v1 source projections when source lineage claims conflict",
            "does not promote authenticated workbook commentary into adjudicated truth",
            "does not replace later source-commentary/disposition provenance reconciliation",
        ],
    }
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify bootstrap BUGGY/FIXED/VERIFIED commit provenance against live GitHub PR history."
    )
    parser.add_argument("--cases", type=Path, default=Path("data/regression-cases.jsonl"))
    parser.add_argument("--findings", type=Path, default=Path("data/findings.jsonl"))
    parser.add_argument(
        "--reconciliation",
        type=Path,
        default=Path("data/bootstrap-provenance-reconciliation.json"),
    )
    parser.add_argument("--api-url", default=os.environ.get("GITHUB_API_URL", "https://api.github.com"))
    parser.add_argument("--token-env", default="MIMISEEK_GITHUB_TOKEN")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    token = os.environ.get(args.token_env)
    client = GitHubClient(token=token, api_url=args.api_url)
    try:
        result = reconcile(
            args.cases,
            args.findings,
            client,
            reconciliation_path=args.reconciliation,
        )
    except Exception as exc:
        print(f"bootstrap commit provenance verification failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    if result["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
