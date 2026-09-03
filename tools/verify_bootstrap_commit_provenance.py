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
CASE_COLUMNS = "case_id finding_id repository pr severity category known_defect buggy_base buggy_head fix_head verified_head historical_source_reviewer codex_target codex_basis our_target our_extra_confirmed our_false_positives buggy_rerun fixed_rerun regression_result disposition priority source_url notes source_row".split()
FINDING_COLUMNS = "finding_id repository pr head_sha reviewer severity confirmed scored defect_group category finding same_head_match other_reviewer source_url evidence_confidence source_row".split()
REBASE_ENTRY_FIELDS = {
    "case_ids", "repository", "pr", "kind", "source_buggy_base", "reviewed_buggy_head",
    "reviewed_buggy_parent", "rebased_fix_lineage_anchor", "fix_head", "verified_head",
    "source_conflict", "github_evidence",
}
REBASE_EVIDENCE_FIELDS = {
    "review_request_issue_comment_id", "codex_review_id", "codex_review_comment_ids",
    "owner_reply_comment_ids",
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


def require_id_list(value: Any, label: str) -> list[int]:
    if not isinstance(value, list) or not value or any(
        not isinstance(item, int) or isinstance(item, bool) or item < 1 for item in value
    ):
        raise ProvenanceError(f"{label} is invalid")
    if len(value) != len(set(value)):
        raise ProvenanceError(f"{label} contains duplicates")
    return value


def load_tuple_jsonl(path: Path, columns: list[str]) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        raw = json.loads(line)
        if not isinstance(raw, list) or len(raw) != len(columns):
            got = len(raw) if isinstance(raw, list) else type(raw).__name__
            raise ProvenanceError(f"{path}:{line_number}: expected {len(columns)} positional fields, got {got}")
        record = dict(zip(columns, raw, strict=True))
        record["_line_number"] = line_number
        records.append(record)
    return records


def index_unique(records: list[dict[str, Any]], key: str, label: str) -> dict[Any, dict[str, Any]]:
    result = {}
    for record in records:
        value = record[key]
        if value in result:
            raise ProvenanceError(f"duplicate {label} {value!r}")
        result[value] = record
    return result


def load_reconciliations(path: Path | None) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    if path is None:
        return {}, []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema_version") != RECONCILIATION_SCHEMA:
        raise ProvenanceError(f"{path}: unsupported reconciliation schema")
    entries = raw.get("entries")
    if not isinstance(entries, list):
        raise ProvenanceError(f"{path}: entries must be an array")
    by_case, normalized = {}, []
    for index, entry in enumerate(entries, 1):
        prefix = f"{path}: entry {index}"
        if not isinstance(entry, dict) or set(entry) != REBASE_ENTRY_FIELDS:
            raise ProvenanceError(f"{prefix} has an unexpected shape")
        if entry.get("kind") != REBASE_KIND:
            raise ProvenanceError(f"{prefix} has unsupported kind {entry.get('kind')!r}")
        if not isinstance(entry.get("repository"), str) or entry["repository"].count("/") != 1:
            raise ProvenanceError(f"{prefix} has invalid repository")
        require_positive_int(entry.get("pr"), f"{prefix} pr")
        for field in ("source_buggy_base", "reviewed_buggy_head", "reviewed_buggy_parent", "rebased_fix_lineage_anchor", "fix_head", "verified_head"):
            require_sha(entry.get(field), f"{prefix} {field}")
        if entry["source_buggy_base"] == entry["reviewed_buggy_parent"]:
            raise ProvenanceError(f"{prefix} does not describe a base conflict")
        if not isinstance(entry.get("source_conflict"), str) or not entry["source_conflict"].strip():
            raise ProvenanceError(f"{prefix} source_conflict must be non-empty")
        case_ids = entry.get("case_ids")
        if not isinstance(case_ids, list) or not case_ids or any(not isinstance(x, str) or not x for x in case_ids):
            raise ProvenanceError(f"{prefix} case_ids must be a non-empty string array")
        if len(case_ids) != len(set(case_ids)):
            raise ProvenanceError(f"{prefix} has duplicate case_ids")
        evidence = entry.get("github_evidence")
        if not isinstance(evidence, dict) or set(evidence) != REBASE_EVIDENCE_FIELDS:
            raise ProvenanceError(f"{prefix} github_evidence has an unexpected shape")
        require_positive_int(evidence.get("review_request_issue_comment_id"), f"{prefix} review_request_issue_comment_id")
        require_positive_int(evidence.get("codex_review_id"), f"{prefix} codex_review_id")
        originals = require_id_list(evidence.get("codex_review_comment_ids"), f"{prefix} codex_review_comment_ids")
        replies = require_id_list(evidence.get("owner_reply_comment_ids"), f"{prefix} owner_reply_comment_ids")
        if len(originals) != len(case_ids):
            raise ProvenanceError(f"{prefix} must bind one original review comment per reconciled case")
        if len(replies) != len(originals):
            raise ProvenanceError(f"{prefix} must bind one exact owner reply per original review comment")
        if set(originals) & set(replies):
            raise ProvenanceError(f"{prefix} owner replies overlap original comments")
        for case_id in case_ids:
            if case_id in by_case:
                raise ProvenanceError(f"{path}: case {case_id} is reconciled more than once")
            by_case[case_id] = entry
        normalized.append(entry)
    return by_case, normalized


def commit_graph(snapshot: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    graph = {}
    for commit in snapshot.get("commits", []):
        if not isinstance(commit, dict):
            raise ProvenanceError("snapshot commit entry is not an object")
        sha = require_sha(commit.get("sha"), "snapshot commit SHA")
        parents = commit.get("parents")
        if not isinstance(parents, list) or any(not isinstance(p, str) or not SHA40_RE.fullmatch(p) for p in parents):
            raise ProvenanceError(f"snapshot contains invalid parents for commit {sha}")
        parents = tuple(parents)
        if sha in graph and graph[sha] != parents:
            raise ProvenanceError(f"snapshot contains conflicting duplicate commit {sha}")
        graph[sha] = parents
    return graph


def live_commit(client: GitHubClient, repository: str, sha: str) -> dict[str, Any]:
    owner, name = repository.split("/", 1)
    raw = client.get(f"/repos/{owner}/{name}/commits/{sha}")
    if not isinstance(raw, dict) or raw.get("sha") != sha or not isinstance(raw.get("parents"), list):
        raise ProvenanceError(f"live commit lookup did not return exact valid {repository}@{sha}")
    parents = []
    for parent in raw["parents"]:
        if not isinstance(parent, dict):
            raise ProvenanceError(f"live commit {repository}@{sha} has malformed parent")
        parents.append(require_sha(parent.get("sha"), f"live commit {sha} parent"))
    return {"sha": sha, "parents": tuple(parents), "html_url": raw.get("html_url")}


def is_ancestor(ancestor: str, descendant: str, graph: dict[str, tuple[str, ...]]) -> bool:
    if ancestor == descendant:
        return True
    stack, seen = [descendant], set()
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        for parent in graph.get(current, ()):
            if parent == ancestor:
                return True
            if parent in graph and parent not in seen:
                stack.append(parent)
    return False


def validate_common(case: dict[str, Any], finding: dict[str, Any], snapshot: dict[str, Any]) -> list[str]:
    errors, case_id = [], case["case_id"]
    def check(ok: bool, message: str) -> None:
        if not ok:
            errors.append(f"{case_id}: {message}")
    repository, pr = case["repository"], case["pr"]
    url = f"https://github.com/{repository}/pull/{pr}"
    for key, message in (
        (finding["finding_id"] == case["finding_id"], "finding identity does not resolve"),
        (finding["repository"] == repository, "finding repository differs from regression case"),
        (finding["pr"] == pr, "finding PR differs from regression case"),
        (finding["head_sha"] == case["buggy_head"], "finding HEAD is not BUGGY HEAD"),
        (finding["severity"] == case["severity"], "finding severity differs from regression case"),
        (finding["category"] == case["category"], "finding category differs from regression case"),
        (finding["finding"] == case["known_defect"], "finding text differs from known defect"),
        (finding["reviewer"] == case["historical_source_reviewer"], "source reviewer differs"),
        (finding["confirmed"] == "CONFIRMED", "regression target finding is not CONFIRMED"),
        (case["source_url"] == url, "case source URL is not the exact PR URL"),
        (finding["source_url"] == url, "finding source URL is not the exact PR URL"),
        (((snapshot.get("authority") or {}).get("role") == "non_authoritative_source_snapshot"), "live GitHub source snapshot has unexpected authority role"),
        (snapshot.get("repository") == repository, "snapshot repository differs from case"),
        (snapshot.get("pr_number") == pr, "snapshot PR number differs from case"),
        (((snapshot.get("source") or {}).get("pull_request_url") == url), "snapshot source URL differs"),
    ):
        check(key, message)
    live_pr, base = snapshot.get("pull_request") or {}, (snapshot.get("pull_request") or {}).get("base") or {}
    check(live_pr.get("number") == pr, "live PR identity number differs")
    check(base.get("repo") == repository, "live PR base repository differs")
    check(base.get("repo_id") == snapshot.get("repository_id"), "repository numeric identity differs")
    check(base.get("repo_node_id") == snapshot.get("repository_node_id"), "repository node identity differs")
    return errors


def validate_linear(case: dict[str, Any], graph: dict[str, tuple[str, ...]], live_head: Any) -> list[str]:
    errors, case_id = [], case["case_id"]
    def check(ok: bool, message: str) -> None:
        if not ok:
            errors.append(f"{case_id}: {message}")
    for field in ("buggy_head", "fix_head", "verified_head"):
        check(case[field] in graph, f"{field} {case[field]} is absent from the live PR commit history")
    if case["buggy_head"] in graph:
        check(is_ancestor(case["buggy_base"], case["buggy_head"], graph), f"BUGGY BASE {case['buggy_base']} is not an ancestor of BUGGY HEAD {case['buggy_head']}")
    if case["buggy_head"] in graph and case["fix_head"] in graph:
        check(is_ancestor(case["buggy_head"], case["fix_head"], graph), f"FIX HEAD {case['fix_head']} is not descended from BUGGY HEAD {case['buggy_head']}")
    if case["fix_head"] in graph and case["verified_head"] in graph:
        check(is_ancestor(case["fix_head"], case["verified_head"], graph), f"VERIFIED HEAD {case['verified_head']} is not descended from FIX HEAD {case['fix_head']}")
    if isinstance(live_head, str) and live_head in graph and case["verified_head"] in graph:
        check(is_ancestor(case["verified_head"], live_head, graph), f"VERIFIED HEAD {case['verified_head']} is not in the ancestry of live PR HEAD {live_head}")
    return errors


def validate_rebased(case: dict[str, Any], snapshot: dict[str, Any], graph: dict[str, tuple[str, ...]], entry: dict[str, Any], historical: dict[str, Any]) -> list[str]:
    errors, case_id = [], case["case_id"]
    def check(ok: bool, message: str) -> None:
        if not ok:
            errors.append(f"{case_id}: {message}")
    for field, expected in {
        "repository": case["repository"], "pr": case["pr"], "source_buggy_base": case["buggy_base"],
        "reviewed_buggy_head": case["buggy_head"], "fix_head": case["fix_head"], "verified_head": case["verified_head"],
    }.items():
        check(entry.get(field) == expected, f"reconciliation {field} does not match authenticated source")
    reviewed, parent = entry["reviewed_buggy_head"], entry["reviewed_buggy_parent"]
    anchor, source_base = entry["rebased_fix_lineage_anchor"], entry["source_buggy_base"]
    fix, verified = entry["fix_head"], entry["verified_head"]
    check(historical.get("sha") == reviewed, "historical commit lookup returned a different SHA")
    check(historical.get("parents") == (parent,), f"reviewed BUGGY HEAD parent differs from reconciled parent {parent}")
    check(reviewed not in graph, "rebased exception is no longer detached from final PR history")
    for sha, label in ((anchor, "rebased fix lineage anchor"), (fix, "FIX HEAD"), (verified, "VERIFIED HEAD")):
        check(sha in graph, f"{label} {sha} is absent from final PR history")
    if anchor in graph:
        check(is_ancestor(source_base, anchor, graph), "source BUGGY BASE is not the base ancestry of the declared rebased fix lineage")
    if anchor in graph and fix in graph:
        check(is_ancestor(anchor, fix, graph), "FIX HEAD is not descended from rebased lineage anchor")
    if fix in graph and verified in graph:
        check(is_ancestor(fix, verified, graph), "VERIFIED HEAD is not descended from FIX HEAD")
    live_head = ((snapshot.get("pull_request") or {}).get("head") or {}).get("sha")
    if isinstance(live_head, str) and live_head in graph and verified in graph:
        check(is_ancestor(verified, live_head, graph), "VERIFIED HEAD is not in live PR HEAD ancestry")

    evidence = entry["github_evidence"]
    issue_comments = {x.get("id"): x for x in snapshot.get("issue_comments", []) if isinstance(x, dict)}
    reviews = {x.get("id"): x for x in snapshot.get("reviews", []) if isinstance(x, dict)}
    comments = {x.get("id"): x for x in snapshot.get("review_comments", []) if isinstance(x, dict)}
    request = issue_comments.get(evidence["review_request_issue_comment_id"])
    check(request is not None, "exact-head review request issue comment is absent")
    if request:
        check(reviewed in (request.get("body") or ""), "review request does not bind the historical BUGGY HEAD")
    codex_review = reviews.get(evidence["codex_review_id"])
    check(codex_review is not None, "Codex review submission is absent")
    if codex_review:
        check(codex_review.get("commit_id") == reviewed, "Codex review submission is not bound to BUGGY HEAD")
        check(((codex_review.get("user") or {}).get("login") == "chatgpt-codex-connector[bot]"), "review submission actor is not the expected Codex bot")

    owner = ((snapshot.get("pull_request") or {}).get("user") or {}).get("id")
    owner_review_ids, rebase_text = set(), False
    for original_id, reply_id in zip(evidence["codex_review_comment_ids"], evidence["owner_reply_comment_ids"], strict=True):
        original = comments.get(original_id)
        check(original is not None, f"original Codex review comment {original_id} is absent")
        if original:
            check(original.get("pull_request_review_id") == evidence["codex_review_id"], f"comment {original_id} review id differs")
            check(original.get("commit_id") == reviewed, f"comment {original_id} commit_id differs from BUGGY HEAD")
            check(original.get("original_commit_id") == reviewed, f"comment {original_id} original_commit_id differs from BUGGY HEAD")
            check(((original.get("user") or {}).get("login") == "chatgpt-codex-connector[bot]"), f"comment {original_id} actor is not the expected Codex bot")
        reply = comments.get(reply_id)
        check(reply is not None, f"exact owner reply {reply_id} is absent")
        if not reply:
            continue
        check(reply.get("in_reply_to_id") == original_id, f"owner reply {reply_id} is not bound to Codex comment {original_id}")
        check(((reply.get("user") or {}).get("id")) == owner, f"reply {reply_id} actor is not the PR owner")
        check(reply.get("commit_id") == reviewed, f"owner reply {reply_id} thread commit_id differs from BUGGY HEAD")
        check(reply.get("original_commit_id") == reviewed, f"owner reply {reply_id} original_commit_id differs from BUGGY HEAD")
        review_id = reply.get("pull_request_review_id")
        if isinstance(review_id, int) and not isinstance(review_id, bool) and review_id > 0:
            owner_review_ids.add(review_id)
            owner_review = reviews.get(review_id)
            check(owner_review is not None, f"owner reply {reply_id} review submission {review_id} is absent")
            if owner_review:
                check(((owner_review.get("user") or {}).get("id")) == owner, f"owner review {review_id} actor differs from the PR owner")
                check(owner_review.get("commit_id") == anchor, f"owner review {review_id} is not bound to rebased lineage anchor {anchor}")
        else:
            check(False, f"owner reply {reply_id} has no valid review submission identity")
        rebase_text = rebase_text or "rebas" in (reply.get("body") or "").casefold()
    check(len(owner_review_ids) == len(evidence["owner_reply_comment_ids"]), "owner replies do not resolve to distinct review submissions")
    check(rebase_text, "exact owner replies do not explicitly preserve the rebase transition")
    return errors


def validate_case(case: dict[str, Any], finding: dict[str, Any], snapshot: dict[str, Any], reconciliation: dict[str, Any] | None = None, historical_commit: dict[str, Any] | None = None) -> list[str]:
    errors = validate_common(case, finding, snapshot)
    try:
        graph = commit_graph(snapshot)
    except ProvenanceError as exc:
        return errors + [f"{case['case_id']}: {exc}"]
    if reconciliation is None:
        return errors + validate_linear(case, graph, ((snapshot.get("pull_request") or {}).get("head") or {}).get("sha"))
    if reconciliation.get("kind") != REBASE_KIND:
        return errors + [f"{case['case_id']}: unsupported reconciliation kind"]
    if historical_commit is None:
        return errors + [f"{case['case_id']}: reconciled historical commit was not loaded"]
    return errors + validate_rebased(case, snapshot, graph, reconciliation, historical_commit)


def reconcile(cases_path: Path, findings_path: Path, client: GitHubClient, snapshot_builder: Callable[[GitHubClient, str, int], dict[str, Any]] = build_snapshot, reconciliation_path: Path | None = None) -> dict[str, Any]:
    cases = load_tuple_jsonl(cases_path, CASE_COLUMNS)
    findings = load_tuple_jsonl(findings_path, FINDING_COLUMNS)
    findings_by_id = index_unique(findings, "finding_id", "finding_id")
    cases_by_id = index_unique(cases, "case_id", "case_id")
    by_case, entries = load_reconciliations(reconciliation_path)
    unknown = sorted(set(by_case) - set(cases_by_id))
    if unknown:
        raise ProvenanceError(f"reconciliation references unknown cases: {unknown}")
    grouped = defaultdict(list)
    for case in cases:
        if case["finding_id"] not in findings_by_id:
            raise ProvenanceError(f"{case['case_id']}: unknown finding_id {case['finding_id']}")
        grouped[(case["repository"], case["pr"])].append(case)
    historical = {}
    for entry in entries:
        key = (entry["repository"], entry["reviewed_buggy_head"])
        historical.setdefault(key, live_commit(client, *key))

    all_errors, summaries, modes = [], [], Counter()
    for repository, pr in sorted(grouped):
        snap = snapshot_builder(client, repository, pr)
        graph, live_pr, pr_errors, pr_modes = commit_graph(snap), snap.get("pull_request") or {}, [], Counter()
        for case in sorted(grouped[(repository, pr)], key=lambda x: x["case_id"]):
            entry = by_case.get(case["case_id"])
            mode = entry["kind"] if entry else "linear_pr_history"
            modes[mode] += 1; pr_modes[mode] += 1
            hist = historical[(entry["repository"], entry["reviewed_buggy_head"])] if entry else None
            pr_errors.extend(validate_case(case, findings_by_id[case["finding_id"]], snap, entry, hist))
        all_errors.extend(pr_errors)
        summaries.append({
            "repository": repository, "repository_id": snap.get("repository_id"), "pr": pr,
            "pr_id": live_pr.get("id"), "pr_node_id": live_pr.get("node_id"),
            "live_head": (live_pr.get("head") or {}).get("sha"), "commit_count": len(graph),
            "case_count": len(grouped[(repository, pr)]), "provenance_modes": dict(sorted(pr_modes.items())),
            "status": "PASS" if not pr_errors else "FAIL",
        })
    return {
        "schema_version": "bootstrap_commit_provenance_check_v1",
        "authority": "derived_live_verification_not_source_truth",
        "scope": "structural BUGGY/FIXED/VERIFIED commit identity, PR binding, ancestry and explicit rebase reconciliation only",
        "cases_checked": len(cases), "prs_checked": len(grouped),
        "repositories": sorted({c["repository"] for c in cases}), "provenance_modes": dict(sorted(modes.items())),
        "reconciliation_entries_checked": len(entries), "status": "PASS" if not all_errors else "FAIL",
        "errors": all_errors, "pull_requests": summaries,
        "limitations": [
            "does not infer semantic fix correctness from commit ancestry or thread replies",
            "does not alter authenticated bootstrap-v1 source projections when source lineage claims conflict",
            "does not promote authenticated workbook commentary into adjudicated truth",
            "does not replace later source-commentary/disposition provenance reconciliation",
        ],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Verify bootstrap BUGGY/FIXED/VERIFIED commit provenance against live GitHub PR history.")
    p.add_argument("--cases", type=Path, default=Path("data/regression-cases.jsonl"))
    p.add_argument("--findings", type=Path, default=Path("data/findings.jsonl"))
    p.add_argument("--reconciliation", type=Path, default=Path("data/bootstrap-provenance-reconciliation.json"))
    p.add_argument("--api-url", default=os.environ.get("GITHUB_API_URL", "https://api.github.com"))
    p.add_argument("--token-env", default="MIMISEEK_GITHUB_TOKEN")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    client = GitHubClient(token=os.environ.get(args.token_env), api_url=args.api_url)
    try:
        result = reconcile(args.cases, args.findings, client, reconciliation_path=args.reconciliation)
    except Exception as exc:
        print(f"bootstrap commit provenance verification failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
