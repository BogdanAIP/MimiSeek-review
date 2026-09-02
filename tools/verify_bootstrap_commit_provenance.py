#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

TOOLS_ROOT = Path(__file__).resolve().parent
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from collect_github_evidence import GitHubClient, build_snapshot  # noqa: E402

SHA40_RE = re.compile(r"^[0-9a-f]{40}$")

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


class ProvenanceError(RuntimeError):
    pass


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


def commit_graph(snapshot: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    graph: dict[str, tuple[str, ...]] = {}
    for commit in snapshot.get("commits", []):
        if not isinstance(commit, dict):
            raise ProvenanceError("snapshot commit entry is not an object")
        sha = commit.get("sha")
        parents = commit.get("parents")
        if not isinstance(sha, str) or not SHA40_RE.fullmatch(sha):
            raise ProvenanceError(f"snapshot contains invalid commit SHA {sha!r}")
        if not isinstance(parents, list) or any(
            not isinstance(parent, str) or not SHA40_RE.fullmatch(parent) for parent in parents
        ):
            raise ProvenanceError(f"snapshot contains invalid parents for commit {sha}")
        normalized = tuple(parents)
        if sha in graph and graph[sha] != normalized:
            raise ProvenanceError(f"snapshot contains conflicting duplicate commit {sha}")
        graph[sha] = normalized
    return graph


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


def validate_case(
    case: dict[str, Any],
    finding: dict[str, Any],
    snapshot: dict[str, Any],
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
    head = pull_request.get("head") or {}
    check(pull_request.get("number") == pr_number, "live PR identity number differs")
    check(base.get("repo") == repository, "live PR base repository differs")
    check(base.get("repo_id") == snapshot.get("repository_id"), "repository numeric identity differs")
    check(
        base.get("repo_node_id") == snapshot.get("repository_node_id"),
        "repository node identity differs",
    )
    check((snapshot.get("source") or {}).get("pull_request_url") == expected_url, "snapshot source URL differs")

    try:
        graph = commit_graph(snapshot)
    except ProvenanceError as exc:
        errors.append(f"{case_id}: {exc}")
        return errors

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

    live_head = head.get("sha")
    if isinstance(live_head, str) and live_head in graph and case["verified_head"] in graph:
        check(
            is_ancestor(case["verified_head"], live_head, graph),
            f"VERIFIED HEAD {case['verified_head']} is not in the ancestry of live PR HEAD {live_head}",
        )

    return errors


def reconcile(
    cases_path: Path,
    findings_path: Path,
    client: GitHubClient,
    snapshot_builder: Callable[[GitHubClient, str, int], dict[str, Any]] = build_snapshot,
) -> dict[str, Any]:
    cases = load_tuple_jsonl(cases_path, CASE_COLUMNS)
    findings = load_tuple_jsonl(findings_path, FINDING_COLUMNS)
    findings_by_id = index_unique(findings, "finding_id", "finding_id")
    index_unique(cases, "case_id", "case_id")

    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        finding = findings_by_id.get(case["finding_id"])
        if finding is None:
            raise ProvenanceError(f"{case['case_id']}: unknown finding_id {case['finding_id']}")
        grouped[(case["repository"], case["pr"])].append(case)

    all_errors: list[str] = []
    pr_summaries: list[dict[str, Any]] = []
    for repository, pr_number in sorted(grouped):
        snapshot = snapshot_builder(client, repository, pr_number)
        graph = commit_graph(snapshot)
        live_pr = snapshot.get("pull_request") or {}
        case_errors: list[str] = []
        for case in sorted(grouped[(repository, pr_number)], key=lambda item: item["case_id"]):
            case_errors.extend(validate_case(case, findings_by_id[case["finding_id"]], snapshot))
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
                "status": "PASS" if not case_errors else "FAIL",
            }
        )

    result = {
        "schema_version": "bootstrap_commit_provenance_check_v1",
        "authority": "derived_live_verification_not_source_truth",
        "scope": "structural BUGGY/FIXED/VERIFIED commit identity and ancestry only",
        "cases_checked": len(cases),
        "prs_checked": len(grouped),
        "repositories": sorted({case["repository"] for case in cases}),
        "status": "PASS" if not all_errors else "FAIL",
        "errors": all_errors,
        "pull_requests": pr_summaries,
        "limitations": [
            "does not infer semantic fix correctness from commit ancestry",
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
    parser.add_argument("--api-url", default=os.environ.get("GITHUB_API_URL", "https://api.github.com"))
    parser.add_argument("--token-env", default="MIMISEEK_GITHUB_TOKEN")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    token = os.environ.get(args.token_env)
    client = GitHubClient(token=token, api_url=args.api_url)
    try:
        result = reconcile(args.cases, args.findings, client)
    except Exception as exc:
        print(f"bootstrap commit provenance verification failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    if result["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
