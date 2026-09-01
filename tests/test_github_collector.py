import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("collector", REPO_ROOT / "tools" / "collect_github_evidence.py")
collector = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = collector
SPEC.loader.exec_module(collector)


def pr(number=7, updated_at="2026-09-01T12:00:00Z"):
    return {
        "number": number,
        "state": "open",
        "draft": False,
        "locked": False,
        "title": "Example",
        "body": "body",
        "created_at": "2026-09-01T10:00:00Z",
        "updated_at": updated_at,
        "closed_at": None,
        "merged_at": None,
        "merge_commit_sha": None,
        "base": {"ref": "main", "sha": "a"*40, "repo": {"full_name": "BogdanAIP/example"}},
        "head": {"ref": "feature", "sha": "b"*40, "repo": {"full_name": "BogdanAIP/example"}},
        "user": {"id": 1, "login": "BogdanAIP", "type": "User"},
        "html_url": "https://github.com/BogdanAIP/example/pull/7",
        "commits": 1,
    }


class FakeClient:
    api_url = "https://api.github.test"

    def __init__(self):
        self.listed = [pr()]
        self.calls = []

    def pulls_updated_since(self, repository, since):
        self.calls.append(("list", repository, collector.to_z(since)))
        return list(self.listed)

    def get(self, path, params=None):
        self.calls.append(("get", path))
        if path.endswith("/pulls/7"):
            return pr()
        raise AssertionError(path)

    def paged(self, path, params=None):
        self.calls.append(("paged", path))
        if path.endswith("/issues/7/comments"):
            return [{
                "id": 20, "node_id": "IC_20",
                "user": {"id": 1, "login": "BogdanAIP", "type": "User"},
                "body": "CONFIRMED and fixed on head " + "c"*40,
                "reactions": {"+1": 1, "-1": 0, "total_count": 1},
                "created_at": "2026-09-01T12:10:00Z",
                "updated_at": "2026-09-01T12:10:00Z",
                "html_url": "https://example/comment/20",
                "author_association": "OWNER",
            }]
        if path.endswith("/issues/7/reactions"):
            return [{
                "id": 25, "node_id": "REACTION_25",
                "user": {"id": 2, "login": "chatgpt-codex-connector[bot]", "type": "Bot"},
                "content": "+1",
                "created_at": "2026-09-01T12:06:00Z",
            }]
        if path.endswith("/pulls/7/reviews"):
            return [{
                "id": 30, "node_id": "R_30",
                "user": {"id": 2, "login": "chatgpt-codex-connector[bot]", "type": "Bot"},
                "body": "Codex review", "state": "COMMENTED",
                "commit_id": "b"*40, "submitted_at": "2026-09-01T12:05:00Z",
                "html_url": "https://example/review/30", "author_association": "NONE",
            }]
        if path.endswith("/pulls/7/comments"):
            return [{
                "id": 40, "node_id": "RC_40", "pull_request_review_id": 30, "in_reply_to_id": None,
                "user": {"id": 2, "login": "chatgpt-codex-connector[bot]", "type": "Bot"},
                "body": "P1 concrete defect",
                "reactions": {"+1": 2, "-1": 0, "total_count": 2},
                "commit_id": "b"*40, "original_commit_id": "b"*40,
                "path": "x.py", "line": 10, "side": "RIGHT", "start_line": None, "start_side": None,
                "original_line": 10, "diff_hunk": "@@",
                "created_at": "2026-09-01T12:05:00Z", "updated_at": "2026-09-01T12:05:00Z",
                "html_url": "https://example/review-comment/40", "author_association": "NONE",
            }]
        if path.endswith("/pulls/7/commits"):
            return [{
                "sha": "b"*40, "parents": [{"sha": "a"*40}],
                "commit": {
                    "author": {"date": "2026-09-01T11:00:00Z"},
                    "committer": {"date": "2026-09-01T11:00:00Z"},
                    "message": "change",
                },
                "html_url": "https://example/commit",
            }]
        raise AssertionError(path)


class CollectorTests(unittest.TestCase):
    def test_snapshot_preserves_evidence_without_adjudicating(self):
        snap = collector.build_snapshot(FakeClient(), "BogdanAIP/example", 7)
        self.assertEqual(snap["authority"]["role"], "non_authoritative_source_snapshot")
        self.assertEqual(snap["reviews"][0]["commit_id"], "b"*40)
        self.assertEqual(snap["review_comments"][0]["body"], "P1 concrete defect")
        self.assertEqual(snap["review_comments"][0]["reactions"]["+1"], 2)
        self.assertIn("CONFIRMED", snap["issue_comments"][0]["body"])
        self.assertEqual(snap["issue_reactions"][0]["content"], "+1")
        self.assertNotIn("disposition", snap["review_comments"][0])

    def test_collect_is_byte_idempotent_for_unchanged_source(self):
        client = FakeClient()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "consumers.json"
            config.write_text(json.dumps({
                "schema_version": 2,
                "consumers": [{
                    "repository": "BogdanAIP/example",
                    "distribution": "pull_request",
                    "evidence": {"enabled": True, "backfill_from": "2026-09-01T00:00:00Z"},
                }],
            }), encoding="utf-8")
            output = root / "evidence"
            state = root / "state.json"
            scan = datetime(2026, 9, 1, 13, 0, tzinfo=timezone.utc)

            first = collector.collect(client, config, output, state, scan_started_at=scan)
            snapshot_path = output / "BogdanAIP" / "example" / "pulls" / "7.json"
            first_bytes = snapshot_path.read_bytes()
            state_bytes = state.read_bytes()

            second = collector.collect(client, config, output, state, scan_started_at=scan)
            self.assertEqual(snapshot_path.read_bytes(), first_bytes)
            self.assertEqual(state.read_bytes(), state_bytes)
            self.assertEqual(first["changed_files"], 2)
            self.assertEqual(second["changed_files"], 0)

    def test_watermark_uses_scan_start_and_overlap(self):
        consumer = collector.Consumer("BogdanAIP/example", True, "2026-09-01T00:00:00Z")
        since = collector.calculate_since(
            consumer,
            {"watermark": "2026-09-01T10:00:00Z"},
            overlap_minutes=180,
        )
        self.assertEqual(collector.to_z(since), "2026-09-01T07:00:00Z")

    def test_config_rejects_duplicate_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "consumers.json"
            path.write_text(json.dumps({
                "schema_version": 2,
                "consumers": [
                    {"repository": "BogdanAIP/example"},
                    {"repository": "BogdanAIP/example"},
                ],
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                collector.load_consumers(path)


if __name__ == "__main__":
    unittest.main()
