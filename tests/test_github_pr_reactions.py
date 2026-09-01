from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "collect_github_pr_reactions.py"
SPEC = importlib.util.spec_from_file_location("collect_github_pr_reactions", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
collector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(collector)


class FakeClient:
    api_url = "https://api.github.test"

    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    def issue_reactions(self, repository: str, pr_number: int):
        self.calls.append((repository, pr_number))
        return [
            {
                "id": 20,
                "node_id": "reaction-20",
                "content": "+1",
                "created_at": "2026-09-01T10:00:00Z",
                "user": {"id": 9, "login": "review-bot", "type": "Bot", "ignored": "x"},
                "ignored": "x",
            },
            {
                "id": 10,
                "node_id": "reaction-10",
                "content": "eyes",
                "created_at": "2026-09-01T09:00:00Z",
                "user": {"id": 8, "login": "owner", "type": "User"},
            },
        ]


class PullRequestReactionCollectorTests(unittest.TestCase):
    def test_collects_reactions_for_existing_pr_snapshots_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "evidence" / "github"
            pr_path = root / "BogdanAIP" / "uv-studio" / "pulls" / "89.json"
            pr_path.parent.mkdir(parents=True)
            pr_path.write_text(
                json.dumps(
                    {
                        "schema_version": "github_pr_evidence_snapshot_v1",
                        "repository": "BogdanAIP/uv-studio",
                        "pr_number": 89,
                    }
                ),
                encoding="utf-8",
            )
            client = FakeClient()

            first = collector.collect_reactions(client, root)
            self.assertEqual(first, {"changed_files": 1, "scanned_prs": 1})
            self.assertEqual(client.calls, [("BogdanAIP/uv-studio", 89)])

            out = root / "BogdanAIP" / "uv-studio" / "pull-reactions" / "89.json"
            snapshot = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(snapshot["schema_version"], "github_pr_reactions_snapshot_v1")
            self.assertEqual(snapshot["authority"]["role"], "non_authoritative_source_snapshot")
            self.assertEqual([item["id"] for item in snapshot["reactions"]], [10, 20])
            self.assertEqual(snapshot["reactions"][1]["content"], "+1")
            self.assertEqual(snapshot["reactions"][1]["user"], {"id": 9, "login": "review-bot", "type": "Bot"})
            self.assertEqual(snapshot["source"]["kind"], "issue_reactions_for_pull_request")

            second = collector.collect_reactions(client, root)
            self.assertEqual(second, {"changed_files": 0, "scanned_prs": 1})

    def test_rejects_malformed_pr_snapshot_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "evidence" / "github"
            pr_path = root / "BogdanAIP" / "uv-studio" / "pulls" / "bad.json"
            pr_path.parent.mkdir(parents=True)
            pr_path.write_text(
                json.dumps({"repository": "BogdanAIP/uv-studio", "pr_number": 0}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "invalid pr_number"):
                collector.collect_reactions(FakeClient(), root)

    def test_reaction_output_path_is_separate_from_pr_snapshot(self) -> None:
        source = Path("evidence/github/BogdanAIP/chat-agent-platform/pulls/141.json")
        self.assertEqual(
            collector.reaction_output_path(source, 141),
            Path("evidence/github/BogdanAIP/chat-agent-platform/pull-reactions/141.json"),
        )


if __name__ == "__main__":
    unittest.main()
