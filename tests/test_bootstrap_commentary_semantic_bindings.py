import copy
import importlib.util
import json
import sys
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
        self.records = semantic.load_bindings(BINDINGS)

    def test_registry_is_exact_complete_current_family(self):
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

    def test_all_claim_bearing_comment_ids_in_accepted_reconciliations_are_bound(self):
        expected = set()
        base_doc = json.loads((ROOT / "data/bootstrap-commentary-reconciliation.json").read_text(encoding="utf-8"))
        for entry in base_doc["entries"]:
            expected.add(entry["github_evidence"]["codex_review_comment_id"])

        rereview = json.loads((ROOT / "data/bootstrap-commentary-rereview-reconciliation.json").read_text(encoding="utf-8"))
        entry = rereview["entries"][0]
        expected.add(entry["github_evidence"]["codex_review_comment_id"])
        expected.update(
            entry["resolution_evidence"][key]
            for key in ("owner_reply_comment_id", "rereview_request_comment_id", "clean_codex_result_comment_id")
        )

        fix = json.loads((ROOT / "data/bootstrap-commentary-fix-evidence-reconciliation.json").read_text(encoding="utf-8"))
        for entry in fix["entries"]:
            expected.add(entry["github_evidence"]["codex_review_comment_id"])
            expected.add(entry["github_evidence"]["owner_reply_comment_id"])

        baseline = json.loads((ROOT / "data/bootstrap-commentary-fix-baseline-reconciliation.json").read_text(encoding="utf-8"))
        entry = baseline["entries"][0]
        expected.add(entry["github_evidence"]["codex_review_comment_id"])
        expected.add(entry["github_evidence"]["owner_reply_comment_id"])

        progression = json.loads((ROOT / "data/bootstrap-commentary-multi-review-progression-reconciliation.json").read_text(encoding="utf-8"))
        entry = progression["entries"][0]
        expected.add(entry["initial_fix_evidence"]["codex_review_comment_id"])
        expected.add(entry["initial_fix_evidence"]["owner_reply_comment_id"])
        for followup in entry["followup_reviews"]:
            expected.add(followup["codex_review_comment_id"])
            expected.add(followup["owner_reply_comment_id"])

        authority_ci = json.loads((ROOT / "data/bootstrap-commentary-authority-ci-reconciliation.json").read_text(encoding="utf-8"))
        for entry in authority_ci["entries"]:
            expected.add(entry["github_evidence"]["codex_review_comment_id"])
            expected.add(entry["github_evidence"]["owner_reply_comment_id"])

        self.assertEqual(expected, {item["comment_id"] for item in self.records})

    def test_exact_live_record_passes_and_unbound_pr_is_noop(self):
        import hashlib
        record = self.records[0]
        body = "fixture exact body"
        fixture_record = dict(record)
        fixture_record["body_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
        tmp = self._write_manifest([fixture_record])
        live = compact_live(fixture_record)
        live["body"] = body
        snapshot = {
            "repository": fixture_record["repository"],
            "pr_number": fixture_record["pr"],
            "review_comments": [live] if fixture_record["surface"] == "review_comment" else [],
            "issue_comments": [live] if fixture_record["surface"] == "issue_comment" else [],
        }
        self.assertEqual(semantic.validate_snapshot(snapshot, tmp), 1)
        self.assertEqual(
            semantic.validate_snapshot(
                {"repository": "example/unbound", "pr_number": 1, "review_comments": [], "issue_comments": []},
                tmp,
            ),
            0,
        )

    def test_edited_swapped_negating_and_updated_comment_fail_closed(self):
        import hashlib
        first, second = self.records[0], self.records[1]
        bodies = {
            first["role"]: "Fixed in abc. This is supported.",
            second["role"]: "Different exact finding body.",
        }
        fixture = []
        for record in (first, second):
            item = dict(record)
            item["body_sha256"] = hashlib.sha256(bodies[record["role"]].encode("utf-8")).hexdigest()
            fixture.append(item)
        tmp = self._write_manifest(fixture)
        snapshot = {
            "repository": first["repository"],
            "pr_number": first["pr"],
            "review_comments": [],
            "issue_comments": [],
        }
        for record in fixture:
            live = compact_live(record)
            live["body"] = bodies[record["role"]]
            snapshot["review_comments"].append(live)
        self.assertEqual(semantic.validate_snapshot(snapshot, tmp), 2)

        edited = copy.deepcopy(snapshot)
        edited["review_comments"][0]["body"] += " edited"
        with self.assertRaisesRegex(semantic.SemanticBindingError, "body digest differs"):
            semantic.validate_snapshot(edited, tmp)

        swapped = copy.deepcopy(snapshot)
        swapped["review_comments"][0]["body"] = bodies[second["role"]]
        with self.assertRaisesRegex(semantic.SemanticBindingError, "body digest differs"):
            semantic.validate_snapshot(swapped, tmp)

        negating = copy.deepcopy(snapshot)
        negating["review_comments"][0]["body"] = "Not fixed; abc remains vulnerable."
        with self.assertRaisesRegex(semantic.SemanticBindingError, "body digest differs"):
            semantic.validate_snapshot(negating, tmp)

        moved = copy.deepcopy(snapshot)
        moved["review_comments"][0]["updated_at"] = "2099-01-01T00:00:00Z"
        with self.assertRaisesRegex(semantic.SemanticBindingError, "updated_at differs"):
            semantic.validate_snapshot(moved, tmp)

    def test_wrong_thread_or_original_head_fail_closed(self):
        import hashlib
        record = next(item for item in self.records if item["role"] == "F053_FINDING")
        body = "exact finding"
        fixture = dict(record)
        fixture["body_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
        tmp = self._write_manifest([fixture])
        live = compact_live(fixture)
        live["body"] = body
        snapshot = {
            "repository": fixture["repository"],
            "pr_number": fixture["pr"],
            "review_comments": [live],
            "issue_comments": [],
        }
        live["pull_request_review_id"] += 1
        with self.assertRaisesRegex(semantic.SemanticBindingError, "pull_request_review_id differs"):
            semantic.validate_snapshot(snapshot, tmp)
        live["pull_request_review_id"] = fixture["pull_request_review_id"]
        live["original_commit_id"] = "0" * 40
        with self.assertRaisesRegex(semantic.SemanticBindingError, "original_commit_id differs"):
            semantic.validate_snapshot(snapshot, tmp)

    def _write_manifest(self, records):
        import tempfile
        if not hasattr(self, "_tmpdirs"):
            self._tmpdirs = []
        tmpdir = tempfile.TemporaryDirectory()
        self._tmpdirs.append(tmpdir)
        path = Path(tmpdir.name) / "bindings.json"
        path.write_text(
            json.dumps(
                {
                    "schema_version": semantic.SCHEMA_VERSION,
                    "authority": semantic.AUTHORITY,
                    "records": records,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return path

    def tearDown(self):
        for tmpdir in getattr(self, "_tmpdirs", []):
            tmpdir.cleanup()


if __name__ == "__main__":
    unittest.main()
