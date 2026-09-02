import importlib.util
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("collector", REPO_ROOT / "tools" / "collect_github_evidence.py")
collector = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = collector
SPEC.loader.exec_module(collector)


def repo(full_name="BogdanAIP/example", repo_id=101, node_id="R_example"):
    return {"full_name": full_name, "id": repo_id, "node_id": node_id}


def pr(number=7, updated_at="2026-09-01T12:00:00Z"):
    return {
        "id": 7007,
        "node_id": "PR_7007",
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
        "base": {"ref": "main", "sha": "a"*40, "repo": repo()},
        "head": {"ref": "feature", "sha": "b"*40, "repo": repo()},
        "user": {"id": 1, "login": "BogdanAIP", "type": "User"},
        "html_url": "https://github.com/BogdanAIP/example/pull/7",
        "commits": 1,
    }


def commit(sha="b"*40):
    return {
        "sha": sha,
        "parents": [{"sha": "a"*40}],
        "commit": {
            "author": {"date": "2026-09-01T11:00:00Z"},
            "committer": {"date": "2026-09-01T11:00:00Z"},
            "message": "change",
        },
        "html_url": "https://example/commit",
    }


class FakeClient:
    api_url = "https://api.github.test"

    def __init__(self):
        self.listed = [pr()]
        self.calls = []
        self.pull_reads = 0

    def pulls_to_refresh(self, repository, since):
        self.calls.append(("list", repository, collector.to_z(since)))
        return list(self.listed)

    def get(self, path, params=None):
        self.calls.append(("get", path))
        if path.endswith("/pulls/7"):
            self.pull_reads += 1
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
            return [commit()]
        raise AssertionError(path)


class MovingPrClient(FakeClient):
    def __init__(self, final_pr):
        super().__init__()
        self.final_pr = final_pr

    def get(self, path, params=None):
        self.calls.append(("get", path))
        if path.endswith("/pulls/7"):
            self.pull_reads += 1
            return pr() if self.pull_reads == 1 else deepcopy(self.final_pr)
        raise AssertionError(path)


class RulesClient:
    api_url = "https://api.github.test"

    def __init__(self, effective_rules=None, current_user_can_bypass="never"):
        self.ruleset_id = 77
        self.effective_rules = effective_rules if effective_rules is not None else [
            {"type": rule_type, "ruleset_id": self.ruleset_id}
            for rule_type in collector.REQUIRED_CANONICAL_RULE_TYPES
        ]
        self.current_user_can_bypass = current_user_can_bypass

    def get(self, path, params=None):
        if path == "/repos/BogdanAIP/example":
            return {"default_branch": "main"}
        if path == f"/repos/BogdanAIP/example/rulesets/{self.ruleset_id}":
            return {
                "id": self.ruleset_id,
                "name": "mimiseek-canonical-main",
                "target": "branch",
                "enforcement": "active",
                "conditions": {
                    "ref_name": {
                        "include": ["~DEFAULT_BRANCH"],
                        "exclude": ["refs/heads/m*"],
                    }
                },
                "current_user_can_bypass": self.current_user_can_bypass,
            }
        if path == "/repos/BogdanAIP/example/branches/main":
            return {"name": "main", "protected": True}
        raise AssertionError(path)

    def paged(self, path, params=None):
        if path == "/repos/BogdanAIP/example/rulesets":
            return [{
                "id": self.ruleset_id,
                "name": "mimiseek-canonical-main",
                "target": "branch",
                "source_type": "Repository",
                "source": "BogdanAIP/example",
                "enforcement": "active",
            }]
        if path == "/repos/BogdanAIP/example/rules/branches/main":
            return list(self.effective_rules)
        raise AssertionError(path)


class CollectorTests(unittest.TestCase):
    def test_snapshot_preserves_evidence_and_immutable_identities(self):
        snap = collector.build_snapshot(FakeClient(), "BogdanAIP/example", 7)
        self.assertEqual(snap["authority"]["role"], "non_authoritative_source_snapshot")
        self.assertEqual(snap["repository"], "BogdanAIP/example")
        self.assertEqual(snap["repository_id"], 101)
        self.assertEqual(snap["repository_node_id"], "R_example")
        self.assertEqual(snap["pull_request"]["id"], 7007)
        self.assertEqual(snap["pull_request"]["node_id"], "PR_7007")
        self.assertEqual(snap["pull_request"]["base"]["repo_id"], 101)
        self.assertEqual(snap["pull_request"]["head"]["repo_id"], 101)
        self.assertEqual(snap["reviews"][0]["commit_id"], "b"*40)
        self.assertEqual(snap["review_comments"][0]["body"], "P1 concrete defect")
        self.assertEqual(snap["review_comments"][0]["reactions"]["+1"], 2)
        self.assertIn("CONFIRMED", snap["issue_comments"][0]["body"])
        self.assertEqual(snap["issue_reactions"][0]["content"], "+1")
        self.assertNotIn("disposition", snap["review_comments"][0])

    def test_snapshot_fails_if_commit_added_during_collection(self):
        final = pr(updated_at="2026-09-01T12:01:00Z")
        final["head"]["sha"] = "c"*40
        final["commits"] = 2
        with self.assertRaisesRegex(collector.GitHubApiError, "moved during evidence snapshot"):
            collector.build_snapshot(MovingPrClient(final), "BogdanAIP/example", 7)

    def test_snapshot_fails_on_equal_count_force_push(self):
        final = pr(updated_at="2026-09-01T12:01:00Z")
        final["head"]["sha"] = "c"*40
        final["commits"] = 1
        with self.assertRaisesRegex(collector.GitHubApiError, "moved during evidence snapshot"):
            collector.build_snapshot(MovingPrClient(final), "BogdanAIP/example", 7)

    def test_snapshot_fails_if_repository_identity_moves(self):
        final = pr(updated_at="2026-09-01T12:01:00Z")
        final["base"]["repo"] = repo(repo_id=999, node_id="R_replacement")
        with self.assertRaisesRegex(collector.GitHubApiError, "moved during evidence snapshot"):
            collector.build_snapshot(MovingPrClient(final), "BogdanAIP/example", 7)

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

    def test_failed_snapshot_does_not_advance_watermark(self):
        final = pr(updated_at="2026-09-01T12:01:00Z")
        final["head"]["sha"] = "c"*40
        client = MovingPrClient(final)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "consumers.json"
            config.write_text(json.dumps({
                "schema_version": 2,
                "consumers": [{
                    "repository": "BogdanAIP/example",
                    "evidence": {"enabled": True, "backfill_from": "2026-09-01T00:00:00Z"},
                }],
            }), encoding="utf-8")
            state = root / "state.json"
            with self.assertRaises(collector.GitHubApiError):
                collector.collect(
                    client,
                    config,
                    root / "evidence",
                    state,
                    scan_started_at=datetime(2026, 9, 1, 13, 0, tzinfo=timezone.utc),
                )
            self.assertFalse(state.exists())

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

    def test_config_enabled_is_strict_json_boolean(self):
        for invalid in ("false", 0, 1, None, [], {}):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, "evidence.enabled must be a JSON boolean"):
                    collector.Consumer.from_dict({
                        "repository": "BogdanAIP/example",
                        "evidence": {"enabled": invalid},
                    })
        self.assertTrue(collector.Consumer.from_dict({"repository": "BogdanAIP/example"}).evidence_enabled)
        self.assertFalse(collector.Consumer.from_dict({
            "repository": "BogdanAIP/example",
            "evidence": {"enabled": False},
        }).evidence_enabled)

    def test_snapshot_schema_requires_immutable_github_ids(self):
        schema = json.loads(
            (REPO_ROOT / "data" / "schemas" / "github-pr-evidence-snapshot-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn("repository_id", schema["required"])
        self.assertIn("repository_node_id", schema["required"])
        pull_schema = schema["properties"]["pull_request"]
        self.assertIn("id", pull_schema["required"])
        self.assertIn("node_id", pull_schema["required"])
        for side in ("base", "head"):
            self.assertIn("repo_id", pull_schema["properties"][side]["required"])
            self.assertIn("repo_node_id", pull_schema["properties"][side]["required"])

    def test_canonical_boundary_uses_effective_rules_for_default_branch(self):
        result = collector.verify_canonical_ref_boundary(RulesClient(), "BogdanAIP/example")
        self.assertEqual(result["ruleset_id"], 77)
        self.assertEqual(result["current_user_can_bypass"], "never")
        self.assertEqual(
            set(result["effective_required_rule_types"]),
            collector.REQUIRED_CANONICAL_RULE_TYPES,
        )

    def test_canonical_boundary_rejects_pattern_exclusion_even_if_branch_is_protected(self):
        # The ruleset detail deliberately contains include=~DEFAULT_BRANCH plus
        # exclude=refs/heads/m*. A literal-string implementation would miss that
        # main is excluded. The effective-rules endpoint contains only a weaker
        # ruleset's rules, while branches/main still reports protected=true.
        effective = [
            {"type": rule_type, "ruleset_id": 88}
            for rule_type in collector.REQUIRED_CANONICAL_RULE_TYPES
        ]
        with self.assertRaisesRegex(collector.GitHubApiError, "does not effectively apply"):
            collector.verify_canonical_ref_boundary(
                RulesClient(effective_rules=effective),
                "BogdanAIP/example",
            )

    def test_canonical_boundary_rejects_unknown_bypass_capability(self):
        with self.assertRaisesRegex(collector.GitHubApiError, "not provably 'never'"):
            collector.verify_canonical_ref_boundary(
                RulesClient(current_user_can_bypass=None),
                "BogdanAIP/example",
            )


if __name__ == "__main__":
    unittest.main()
