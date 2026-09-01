#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API_VERSION = "2026-03-10"
SCHEMA_VERSION = "github_pr_reactions_snapshot_v1"
DEFAULT_TIMEOUT_SECONDS = 30
USER_AGENT = "MimiSeek-Review-Reaction-Collector/1"


def stable_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


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


class GitHubApiError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: str | None, api_url: str = "https://api.github.com", timeout: int = DEFAULT_TIMEOUT_SECONDS):
        self.token = token or None
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        if not path.startswith("/"):
            raise ValueError("GitHub API path must start with '/'")
        query = urllib.parse.urlencode(params or {}, doseq=True)
        url = f"{self.api_url}{path}"
        if query:
            url += "?" + query
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
                return json.loads(response.read().decode("utf-8"))
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

    def issue_reactions(self, repository: str, pr_number: int) -> list[dict[str, Any]]:
        owner, name = split_repository(repository)
        result: list[dict[str, Any]] = []
        page = 1
        while True:
            payload = self.get(
                f"/repos/{owner}/{name}/issues/{pr_number}/reactions",
                {"per_page": 100, "page": page},
            )
            if not isinstance(payload, list):
                raise GitHubApiError(f"expected reaction list for {repository}#{pr_number}")
            result.extend(payload)
            if len(payload) < 100:
                return result
            page += 1


def compact_user(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    return {"id": raw.get("id"), "login": raw.get("login"), "type": raw.get("type")}


def compact_reaction(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": raw.get("id"),
        "node_id": raw.get("node_id"),
        "content": raw.get("content"),
        "created_at": raw.get("created_at"),
        "user": compact_user(raw.get("user")),
    }


def reaction_output_path(pr_snapshot_path: Path, pr_number: int) -> Path:
    if pr_snapshot_path.parent.name != "pulls":
        raise ValueError(f"unexpected PR snapshot path: {pr_snapshot_path}")
    return pr_snapshot_path.parent.parent / "pull-reactions" / f"{pr_number}.json"


def collect_reactions(client: GitHubClient, output_root: Path) -> dict[str, int]:
    changed_files = 0
    scanned_prs = 0
    for pr_snapshot_path in sorted(output_root.glob("*/*/pulls/*.json")):
        raw = json.loads(pr_snapshot_path.read_text(encoding="utf-8"))
        repository = raw.get("repository")
        pr_number = raw.get("pr_number")
        split_repository(repository)
        if not isinstance(pr_number, int) or pr_number <= 0:
            raise ValueError(f"invalid pr_number in {pr_snapshot_path}: {pr_number!r}")

        reactions = client.issue_reactions(repository, pr_number)
        snapshot = {
            "schema_version": SCHEMA_VERSION,
            "authority": {
                "role": "non_authoritative_source_snapshot",
                "rules": [
                    "preserve pull-request reactions without inferring review truth",
                    "a +1 reaction may be evidence of a clean automated review only when later normalization proves reviewer identity and timing",
                    "absence of a reaction is not evidence of a finding or miss",
                ],
            },
            "repository": repository,
            "pr_number": pr_number,
            "reactions": sorted((compact_reaction(item) for item in reactions), key=lambda item: (item.get("id") is None, item.get("id") or 0)),
            "source": {"api_base": client.api_url, "kind": "issue_reactions_for_pull_request"},
        }
        if write_if_changed(reaction_output_path(pr_snapshot_path, pr_number), snapshot):
            changed_files += 1
        scanned_prs += 1

    return {"changed_files": changed_files, "scanned_prs": scanned_prs}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect non-authoritative GitHub pull-request reactions for existing MimiSeek PR snapshots.")
    parser.add_argument("--output-root", default="evidence/github")
    parser.add_argument("--api-url", default="https://api.github.com")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    token = os.environ.get("MIMISEEK_GITHUB_TOKEN") or None
    client = GitHubClient(token=token, api_url=args.api_url)
    result = collect_reactions(client, Path(args.output_root))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if not token:
        print(
            "warning: MIMISEEK_GITHUB_TOKEN is unset; only public reactions are expected to be readable "
            "and unauthenticated GitHub API rate limits apply",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
