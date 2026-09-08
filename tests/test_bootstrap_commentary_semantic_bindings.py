import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location(
    "semantic_binding",
    TOOLS / "verify_bootstrap_commentary_semantic_binding.py",
)
semantic = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = semantic
SPEC.loader.exec_module(semantic)

BINDINGS = ROOT / "data" / "bootstrap-commentary-semantic-bindings.json"


def compact_live(record):
    item = {
        "id": record["comment_id"],
        "user": {"login": record["actor"]},
        "body": "__BODY_FILLED_BY_TEST__",
        "updated_at": record["updated_at"],
    }
    if record["surface"] == "review_comment":
        item["pull_request_review_id"] = record["pull_request_review_id"]
        item["in_reply_to_id"] = record["in_reply_to_id"]
        item["original_commit_id"] = record["original_commit_id"]
    return item


class BootstrapCommentarySemanticBindingTests(unittest.TestCase):
    def setUp(self):
        self.manifest = semantic.load_manifest(BINDINGS)
        self.records = semantic.validate_registry_coverage(BINDINGS, ROOT)

    def test_registry_is_exact_complete_current_family(self):
        self.assertEqual(len(self.manifest["direct_records"]), 18)
        self.assertEqual(len(self.manifest["delegated_records"]), 4)
        self.assertEqual(len(self.records), 22)
        self.assertEqual(
            {item["role"] for item in self.records},
            {
                "F050_FINDING", "F051_FINDING",
                "F052_FINDING", "F052_OWNER_REPLY", "F052_REREVIEW_REQUEST", "F052_CLEAN_RESULT",
                "F053_FINDING", "F053_OWNER_REPLY", "F054_FINDING", "F054_OWNER_REPLY",
                "F055_FINDING", "F055_OWNER_REPLY", "F056_FINDING", "F056_OWNER_REPLY",
                "F057_FINDING", "F057_OWNER_REPLY", "F058_FINDING", "F058_OWNER_REPLY",
                "F059_FINDING", "F059_OWNER_REPLY", "F061_FINDING", "F061_OWNER_REPLY",
            },
        )
        self.assertEqual(
            {semantic.binding_key(item) for item in self.records},
            semantic.expected_inventory(ROOT),
        )

    def test_f055_f056_mutable_facts_have_one_canonical_owner(self):
        raw = json.loads(BINDINGS.read_text(encoding="utf-8"))
        delegated = raw["delegated_records"]
        self.assertEqual(
            {item["role"] for item in delegated},
            {"F055_FINDING", "F055_OWNER_REPLY", "F056_FINDING", "F056_OWNER_REPLY"},
        )
        for item in delegated:
            self.assertEqual(
                set(item),
                {"role", "owner_path", "finding_id", "party"},
            )
            self.assertEqual(
                item["owner_path"],
                "data/bootstrap-commentary-authority-ci-reconciliation.json",
            )
            for forbidden in (
                "repository", "pr", "surface", "comment_id", "actor",
                "updated_at", "body_sha256", "pull_request_review_id",
                "in_reply_to_id", "original_commit_id",
            ):
                self.assertNotIn(forbidden, item)

        delegated_effective = {
            item["role"]: item
            for item in self.records
            if item["role"] in {d["role"] for d in delegated}
        }
        for item in delegated_effective.values():
            self.assertEqual(
                item["binding_owner"],
                "data/bootstrap-commentary-authority-ci-reconciliation.json",
            )

    def test_repository_pr_surface_role_or_comment_drift_fails_family_coverage(self):
        raw = json.loads(BINDINGS.read_text(encoding="utf-8"))
        mutations = {
            "repository": "example/wrong",
            "pr": 999,
            "surface": "issue_comment",
            "role": "F050_WRONG",
            "comment_id": 999999,
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                changed = copy.deepcopy(raw)
                changed["direct_records"][0][field] = value
                path = self._write_manifest(changed)
                with self.assertRaisesRegex(
                    semantic.SemanticBindingError,
                    "family coverage differs",
                ):
                    semantic.validate_registry_coverage(path, ROOT)

    def test_unbound_repository_pr_fails_closed_instead_of_zero_success(self):
        with self.assertRaisesRegex(
            semantic.SemanticBindingError,
            "no required semantic bindings are registered",
        ):
            semantic.validate_snapshot(
                {
                    "repository": "example/unbound",
                    "pr_number": 1,
                    "review_comments": [],
                    "issue_comments": [],
                },
                BINDINGS,
                ROOT,
            )

    def test_exact_live_record_and_adversarial_body_timestamp_fail_closed(self):
        record = copy.deepcopy(self.manifest["direct_records"][0])
        body = "fixture exact body"
        record["body_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
        live = compact_live(record)
        live["body"] = body
        snapshot = {
            "repository": record["repository"],
            "pr_number": record["pr"],
            "review_comments": [live],
            "issue_comments": [],
            "pull_request": {"user": {"login": "BogdanAIP"}},
        }
        self.assertEqual(semantic._validate_records(snapshot, [record]), 1)

        for changed_body in (
            body + " edited",
            "Different exact finding body.",
            "Not fixed; the prior claim is negated.",
        ):
            changed = copy.deepcopy(snapshot)
            changed["review_comments"][0]["body"] = changed_body
            with self.assertRaisesRegex(semantic.SemanticBindingError, "body digest differs"):
                semantic._validate_records(changed, [record])

        moved = copy.deepcopy(snapshot)
        moved["review_comments"][0]["updated_at"] = "2099-01-01T00:00:00Z"
        with self.assertRaisesRegex(semantic.SemanticBindingError, "updated_at differs"):
            semantic._validate_records(moved, [record])

    def test_wrong_thread_or_original_head_fail_closed(self):
        record = copy.deepcopy(
            next(item for item in self.manifest["direct_records"] if item["role"] == "F053_FINDING")
        )
        body = "exact finding"
        record["body_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
        live = compact_live(record)
        live["body"] = body
        snapshot = {
            "repository": record["repository"],
            "pr_number": record["pr"],
            "review_comments": [live],
            "issue_comments": [],
            "pull_request": {"user": {"login": "BogdanAIP"}},
        }
        live["pull_request_review_id"] += 1
        with self.assertRaisesRegex(semantic.SemanticBindingError, "pull_request_review_id differs"):
            semantic._validate_records(snapshot, [record])
        live["pull_request_review_id"] = record["pull_request_review_id"]
        live["original_commit_id"] = "0" * 40
        with self.assertRaisesRegex(semantic.SemanticBindingError, "original_commit_id differs"):
            semantic._validate_records(snapshot, [record])

    def test_delegated_owner_reply_uses_exact_live_pr_owner_actor(self):
        record = next(item for item in self.records if item["role"] == "F055_OWNER_REPLY")
        body = "fixture owner reply"
        fixture = copy.deepcopy(record)
        fixture["body_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
        live = {
            "id": fixture["comment_id"],
            "user": {"login": "BogdanAIP"},
            "body": body,
            "updated_at": fixture["updated_at"],
            "pull_request_review_id": fixture["pull_request_review_id"],
            "in_reply_to_id": fixture["in_reply_to_id"],
            "original_commit_id": fixture["original_commit_id"],
        }
        snapshot = {
            "repository": fixture["repository"],
            "pr_number": fixture["pr"],
            "review_comments": [live],
            "issue_comments": [],
            "pull_request": {"user": {"login": "BogdanAIP"}},
        }
        self.assertEqual(semantic._validate_records(snapshot, [fixture]), 1)
        changed = copy.deepcopy(snapshot)
        changed["review_comments"][0]["user"]["login"] = "someone-else"
        with self.assertRaisesRegex(semantic.SemanticBindingError, "actor differs"):
            semantic._validate_records(changed, [fixture])

    def _write_manifest(self, raw):
        if not hasattr(self, "_tmpdirs"):
            self._tmpdirs = []
        tmpdir = tempfile.TemporaryDirectory()
        self._tmpdirs.append(tmpdir)
        path = Path(tmpdir.name) / "bindings.json"
        path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
        return path

    def tearDown(self):
        for tmpdir in getattr(self, "_tmpdirs", []):
            tmpdir.cleanup()


if __name__ == "__main__":
    unittest.main()
