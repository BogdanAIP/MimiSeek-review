#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

API_VERSION = "2026-03-10"
SCHEMA_VERSION = "github_pr_evidence_snapshot_v1"
STATE_SCHEMA_VERSION = "github_evidence_collector_state_v1"
DEFAULT_OVERLAP_MINUTES = 180
DEFAULT_TIMEOUT_SECONDS = 30
USER_AGENT = "MimiSeek-Review-Collector/1"

ISO_Z_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def to_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_z(value: str) -> datetime:
    if not isinstance(value, str) or not ISO_Z_RE.fullmatch(value):
        raise ValueError(f"expected UTC timestamp YYYY-MM-DDTHH:MM:SSZ, got {value!r}")
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def stable_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_if_changed(path: Path, value: Any) -> bool:
    new_bytes = stable_json_bytes(value)
    if path.exists() and path.read_bytes() == new_bytes:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(new_bytes)
    return True


def split_repository(repository: str) -> tuple[str, str]:
    if not isinstance(repository, str) or repository.count("/") != 1:
        raise ValueError(f"invalid repository identity: {repository!r}")
    owner, name = repository.split("/", 1)
    if not owner or not name or any(ch.isspace() for ch in repository):
        raise ValueError(f"invalid repository identity: {repository!r}")
    return owner, name


@dataclass(frozen=True)
class Consumer:
    repository: str
    evidence_enabled: bool
    backfill_from: str

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Consumer":
        repository = raw["repository"]
        split_repository(repository)
        evidence = raw.get("evidence", {})
        enabled = bool(evidence.get("enabled", True))
        backfill_from = evidence.get("backfill_from", "1970-01-01T00:00:00Z")
        parse_z(backfill_from)
        return cls(repository=repository, evidence_enabled=enabled, backfill_from=backfill_from)


class GitHubApiError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: str | None, api_url: str = "https://api.github.com", timeout: int = DEFAULT_TIMEOUT_SECONDS):
        self.token = token or None
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

    def _request(self, url: str) -> tuple[Any, dict[str, str]]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": USER_AGENT,
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return payload, {k.lower(): v for k, v in response.headers.items()}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            remaining = exc.headers.get("x-ratelimit-remaining")
            reset = exc.headers.get("x-ratelimit-reset")
            raise GitHubApiError(
                f"GitHub GET failed: status={exc.code} url={url} "
                f"rate_remaining={remaining!r} rate_reset={reset!r} body={body[:500]!r}"
            ) from exc
        except urllib.error.URLError as exc:
            raise GitHubApiError(f"GitHub GET failed: url={url} reason={exc.reason!r}") from exc

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        if not path.startswith("/"):
            raise ValueError("GitHub API path must start with '/'")
        query = urllib.parse.urlencode(params or {}, doseq=True)
        url = f"{self.api_url}{path}"
        if query:
            url += "?" + query
        payload, _ = self._request(url)
        return payload

    def paged(self, path: str, params: dict[str, Any] | None = None) -> list[Any]:
        params = dict(params or {})
        params.setdefault("per_page", 100)
        page = 1
        result: list[Any] = []
        while True:
            params["page"] = page
            payload = self.get(path, params)
            if not isinstance(payload, list):
                raise GitHubApiError(f"expected paginated list from {path}, got {type(payload).__name__}")
            result.extend(payload)
            if len(payload) < int(params["per_page"]):
                return result
            page += 1

    def pulls_updated_since(self, repository: str, since: datetime) -> list[dict[str, Any]]:
        owner, name = split_repository(repository)
        page = 1
        result: list[dict[str, Any]] = []
        while True:
            payload = self.get(
                f"/repos/{owner}/{name}/pulls",
                {
                    "state": "all",
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": 100,
                    "page": page,
                },
            )
            if not isinstance(payload, list):
                raise GitHubApiError(f"expected pull request list for {repository}")
            if not payload:
                break
            stop = False
            for pr in payload:
                updated_at = parse_z(pr["updated_at"])
                if updated_at < since:
                    stop = True
                    break
                result.append(pr)
            if stop or len(payload) < 100:
                break
            page += 1
        return result


def compact_user(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    return {"id": raw.get("id"), "login": raw.get("login"), "type": raw.get("type")}


def compact_pr(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "number": raw.get("number"),
        "state": raw.get("state"),
        "draft": raw.get("draft"),
        "locked": raw.get("locked"),
        "title": raw.get("title"),
        "body": raw.get("body"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "closed_at": raw.get("closed_at"),
        "merged_at": raw.get("merged_at"),
        "merge_commit_sha": raw.get("merge_commit_sha"),
        "base": {
            "ref": (raw.get("base") or {}).get("ref"),
            "sha": (raw.get("base") or {}).get("sha"),
            "repo": ((raw.get("base") or {}).get("repo") or {}).get("full_name"),
        },
        "head": {
            "ref": (raw.get("head") or {}).get("ref"),
            "sha": (raw.get("head") or {}).get("sha"),
            "repo": ((raw.get("head") or {}).get("repo") or {}).get("full_name"),
        },
        "user": compact_user(raw.get("user")),
        "html_url": raw.get("html_url"),
    }


def compact_issue_comment(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": raw.get("id"),
        "node_id": raw.get("node_id"),
        "user": compact_user(raw.get("user")),
        "body": raw.get("body"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "html_url": raw.get("html_url"),
        "author_association": raw.get("author_association"),
    }


def compact_review(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": raw.get("id"),
        "node_id": raw.get("node_id"),
        "user": compact_user(raw.get("user")),
        "body": raw.get("body"),
        "state": raw.get("state"),
        "commit_id": raw.get("commit_id"),
        "submitted_at": raw.get("submitted_at"),
        "html_url": raw.get("html_url"),
        "author_association": raw.get("author_association"),
    }


def compact_review_comment(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": raw.get("id"),
        "node_id": raw.get("node_id"),
        "pull_request_review_id": raw.get("pull_request_review_id"),
        "in_reply_to_id": raw.get("in_reply_to_id"),
        "user": compact_user(raw.get("user")),
        "body": raw.get("body"),
        "commit_id": raw.get("commit_id"),
        "original_commit_id": raw.get("original_commit_id"),
        "path": raw.get("path"),
        "line": raw.get("line"),
        "side": raw.get("side"),
        "start_line": raw.get("start_line"),
        "start_side": raw.get("start_side"),
        "original_line": raw.get("original_line"),
        "diff_hunk": raw.get("diff_hunk"),
        "created_at": raw.get("created_at"),
        "updated_at": raw.get("updated_at"),
        "html_url": raw.get("html_url"),
        "author_association": raw.get("author_association"),
    }


def compact_commit(raw: dict[str, Any]) -> dict[str, Any]:
    commit = raw.get("commit") or {}
    return {
        "sha": raw.get("sha"),
        "parents": [parent.get("sha") for parent in raw.get("parents", []) if isinstance(parent, dict)],
        "author_date": (commit.get("author") or {}).get("date"),
        "committer_date": (commit.get("committer") or {}).get("date"),
        "message": commit.get("message"),
        "html_url": raw.get("html_url"),
    }


def sort_by_id(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(items, key=lambda item: (item.get("id") is None, item.get("id") or 0))


def build_snapshot(client: GitHubClient, repository: str, pr_number: int) -> dict[str, Any]:
    owner, name = split_repository(repository)
    prefix = f"/repos/{owner}/{name}"
    pr = client.get(f"{prefix}/pulls/{pr_number}")
    issue_comments = client.paged(f"{prefix}/issues/{pr_number}/comments")
    reviews = client.paged(f"{prefix}/pulls/{pr_number}/reviews")
    review_comments = client.paged(f"{prefix}/pulls/{pr_number}/comments")
    commits = client.paged(f"{prefix}/pulls/{pr_number}/commits")
    declared_commit_count = pr.get("commits")
    if isinstance(declared_commit_count, int) and declared_commit_count > len(commits):
        raise GitHubApiError(
            f"pull request commit list is incomplete for {repository}#{pr_number}: "
            f"declared={declared_commit_count} collected={len(commits)}"
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "authority": {
            "role": "non_authoritative_source_snapshot",
            "rules": [
                "preserve source evidence without adjudicating truth",
                "absence is not a negative finding",
                "normalization and learning happen under separate governed stages",
            ],
        },
        "repository": repository,
        "pr_number": pr_number,
        "pull_request": compact_pr(pr),
        "issue_comments": sort_by_id(compact_issue_comment(item) for item in issue_comments),
        "reviews": sort_by_id(compact_review(item) for item in reviews),
        "review_comments": sort_by_id(compact_review_comment(item) for item in review_comments),
        "commits": sorted((compact_commit(item) for item in commits), key=lambda item: item.get("committer_date") or ""),
        "source": {"api_base": client.api_url, "pull_request_url": pr.get("html_url")},
    }


def repository_output_path(output_root: Path, repository: str, pr_number: int) -> Path:
    owner, name = split_repository(repository)
    return output_root / owner / name / "pulls" / f"{pr_number}.json"


def load_consumers(config_path: Path) -> list[Consumer]:
    raw = load_json(config_path, {})
    if raw.get("schema_version") not in (1, 2):
        raise ValueError("unsupported config/consumers.json schema_version")
    consumers_raw = raw.get("consumers")
    if not isinstance(consumers_raw, list):
        raise ValueError("config/consumers.json consumers must be a list")
    consumers = [Consumer.from_dict(item) for item in consumers_raw]
    repositories = [c.repository for c in consumers]
    if len(repositories) != len(set(repositories)):
        raise ValueError("duplicate consumer repository")
    return consumers


def load_state(path: Path) -> dict[str, Any]:
    default = {"schema_version": STATE_SCHEMA_VERSION, "repositories": {}}
    raw = load_json(path, default)
    if raw.get("schema_version") != STATE_SCHEMA_VERSION:
        raise ValueError("unsupported collector state schema")
    if not isinstance(raw.get("repositories"), dict):
        raise ValueError("collector state repositories must be an object")
    return raw


def calculate_since(consumer: Consumer, repo_state: dict[str, Any], overlap_minutes: int) -> datetime:
    floor = parse_z(consumer.backfill_from)
    watermark_raw = repo_state.get("watermark")
    if not watermark_raw:
        return floor
    watermark = parse_z(watermark_raw)
    return max(floor, watermark - timedelta(minutes=overlap_minutes))


def collect(
    client: GitHubClient,
    config_path: Path,
    output_root: Path,
    state_path: Path,
    overlap_minutes: int = DEFAULT_OVERLAP_MINUTES,
    scan_started_at: datetime | None = None,
) -> dict[str, Any]:
    if overlap_minutes < 0:
        raise ValueError("overlap_minutes must be >= 0")
    scan_started_at = scan_started_at or utc_now()
    consumers = load_consumers(config_path)
    state = load_state(state_path)
    changed_files = 0
    collected_prs = 0
    per_repository: dict[str, Any] = {}

    for consumer in consumers:
        if not consumer.evidence_enabled:
            continue
        repo_state = state["repositories"].setdefault(consumer.repository, {})
        since = calculate_since(consumer, repo_state, overlap_minutes)
        prs = client.pulls_updated_since(consumer.repository, since)

        repo_changed = 0
        for listed_pr in sorted(prs, key=lambda item: int(item["number"])):
            pr_number = int(listed_pr["number"])
            snapshot = build_snapshot(client, consumer.repository, pr_number)
            path = repository_output_path(output_root, consumer.repository, pr_number)
            if write_if_changed(path, snapshot):
                changed_files += 1
                repo_changed += 1
            collected_prs += 1

        repo_state["watermark"] = to_z(scan_started_at)
        repo_state["backfill_from"] = consumer.backfill_from
        repo_state["last_selected_pr_count"] = len(prs)
        per_repository[consumer.repository] = {
            "since": to_z(since),
            "selected_prs": len(prs),
            "changed_snapshots": repo_changed,
            "watermark_after": to_z(scan_started_at),
        }

    state["last_successful_scan_started_at"] = to_z(scan_started_at)
    state_changed = write_if_changed(state_path, state)
    if state_changed:
        changed_files += 1

    return {
        "scan_started_at": to_z(scan_started_at),
        "repositories": per_repository,
        "collected_prs": collected_prs,
        "changed_files": changed_files,
        "state_changed": state_changed,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect non-authoritative GitHub review evidence snapshots.")
    parser.add_argument("--config", default="config/consumers.json")
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--state-file", required=True)
    parser.add_argument("--overlap-minutes", type=int, default=DEFAULT_OVERLAP_MINUTES)
    parser.add_argument("--api-url", default=os.environ.get("GITHUB_API_URL", "https://api.github.com"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    token = os.environ.get("MIMISEEK_GITHUB_TOKEN") or None
    client = GitHubClient(token=token, api_url=args.api_url)
    result = collect(
        client=client,
        config_path=Path(args.config),
        output_root=Path(args.output_root),
        state_path=Path(args.state_file),
        overlap_minutes=args.overlap_minutes,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if not token:
        print(
            "warning: MIMISEEK_GITHUB_TOKEN is unset; only public evidence is expected to be readable "
            "and unauthenticated GitHub API rate limits apply",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
