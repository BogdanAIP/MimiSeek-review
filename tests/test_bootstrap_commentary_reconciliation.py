import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "bootstrap_commentary",
    REPO_ROOT / "tools" / "verify_bootstrap_commentary_reconciliation.py",
)
commentary = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = commentary
SPEC.loader.exec_module(commentary)

SOURCE_HEAD = "2849ef50fff1ec1b66cc86db3858cc8300d63742"
SOURCE_MERGE = "050e4b267c4dd58df4326b66240700ad12707f19"
FOLLOW_HEAD = "09c58c4bc286a639662cd77432a54c3f08438ad7"
FOLLOW_MERGE = "e8bda851e9d810d0e007826693540ec1d4c71053"
SOURCE_TREE = "1" * 40
FOLLOW_TREE = "2" * 40
REVIEW_ID = 5048123956
COMMENT_ID = 3878098608
TEST_PATH = "runtime/semantic-projection/tests/inventory-guard-acceptance.mjs"
LAUNCHER_PATH = "runtime/semantic-projection/bin/semantic-projection-launcher.mjs"
CONTROL_PATH = "runtime/semantic-projection/bin/semantic-control-plane-projection.mjs"


def finding_record():
    return {
        "finding_id": "F051",
        "repository": "BogdanAIP/chat-agent-platform",
        "pr": 121,
        "head_sha": SOURCE_HEAD,
        "reviewer": "Codex Review",
        "severity": "P2",
        "confirmed": "CONFIRMED",
        "scored": False,
        "defect_group": "CAP121-PM02",
        "category": "Acceptance / regression quality",
        "finding": "Browser output ownership regression inspected source text instead of exercising a real hostile caller directory",
        "same_head_match": False,
        "other_reviewer": None,
        "source_url": "https://github.com/BogdanAIP/chat-agent-platform/pull/121",
        "evidence_confidence": "High",
        "source_row": 52,
    }


def entry_record():
    return {
        "finding_id": "F051",
        "repository": "BogdanAIP/chat-agent-platform",
        "pr": 121,
        "reviewed_head": SOURCE_HEAD,
        "source_sheet": "Findings",
        "source_row": 52,
        "source_confirmed": "CONFIRMED",
        "source_note": "Materially addressed by PR #123.",
        "kind": commentary.SUPPORTED_ADDRESS_KIND,
        "github_evidence": {
            "codex_review_id": REVIEW_ID,
            "codex_review_comment_id": COMMENT_ID,
        },
        "follow_up": {
            "repository": "BogdanAIP/chat-agent-platform",
            "pr": 123,
            "base_sha": SOURCE_MERGE,
            "head_sha": FOLLOW_HEAD,
            "merge_commit_sha": FOLLOW_MERGE,
            "changed_files": [CONTROL_PATH, LAUNCHER_PATH, TEST_PATH],
            "content_assertions": [
                {
                    "path": TEST_PATH,
                    "required_present": [
                        "const callerRoot = fs.mkdtempSync",
                        "[launcherEntry, '--verify-runtime-output-ownership']",
                        "cwd: callerRoot",
                        "fs.existsSync(path.join(callerRoot, '.playwright-mcp'))",
                        "fs.existsSync(hostileOutput)",
                    ],
                    "required_absent": [],
                },
                {
                    "path": LAUNCHER_PATH,
                    "required_present": [
                        "PLAYWRIGHT_MCP_OUTPUT_DIR",
                        "--verify-runtime-output-ownership",
                    ],
                    "required_absent": ["CHAT_SEMANTIC_RUNTIME_ROOT"],
                },
            ],
        },
        "reconciliation_status": commentary.SUPPORTED_ADDRESS_STATUS,
        "authority_limit": "Structural follow-up evidence only.",
    }


def source_snapshot():
    return {
        "repository": "BogdanAIP/chat-agent-platform",
        "repository_id": 1326588757,
        "pr_number": 121,
        "pull_request": {
            "number": 121,
            # Scoped GitHub App installation tokens redact this field on these
            # historical PR reads; verification must not depend on it.
            "merge_commit_sha": None,
            "head": {"sha": SOURCE_HEAD},
        },
        "reviews": [
            {
                "id": REVIEW_ID,
                "commit_id": SOURCE_HEAD,
                "user": {"login": commentary.CODEX_LOGIN},
            }
        ],
        "review_comments": [
            {
                "id": COMMENT_ID,
                "pull_request_review_id": REVIEW_ID,
                "commit_id": SOURCE_HEAD,
                "original_commit_id": SOURCE_HEAD,
                "user": {"login": commentary.CODEX_LOGIN},
            }
        ],
    }


def resolved_follow_up():
    test_text = """
const callerRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'caller-'));
const verification = spawnSync(
  process.execPath,
  [launcherEntry, '--verify-runtime-output-ownership'],
  { cwd: callerRoot }
);
assert.equal(fs.existsSync(path.join(callerRoot, '.playwright-mcp')), false);
assert.equal(fs.existsSync(hostileOutput), false);
"""
    launcher_text = """
env.PLAYWRIGHT_MCP_OUTPUT_DIR = paths.playwrightOutputDirectory;
if (process.argv.includes('--verify-runtime-output-ownership')) {
  console.log('verify');
}
"""
    return {
        "pr": {
            "number": 123,
            "state": "closed",
            "merged_at": "2026-08-28T05:25:11Z",
            "merge_commit_sha": None,
            "base": {
                "sha": SOURCE_MERGE,
                "repo": {
                    "full_name": "BogdanAIP/chat-agent-platform",
                    "id": 1326588757,
                },
            },
            "head": {"sha": FOLLOW_HEAD},
        },
        "changed_files": sorted([CONTROL_PATH, LAUNCHER_PATH, TEST_PATH]),
        "contents": {
            TEST_PATH: test_text,
            LAUNCHER_PATH: launcher_text,
        },
        "source_head_commit": {
            "sha": SOURCE_HEAD,
            "tree": SOURCE_TREE,
            "parents": ("0" * 40,),
        },
        "source_merge_commit": {
            "sha": SOURCE_MERGE,
            "tree": SOURCE_TREE,
            "parents": ("0" * 40,),
        },
        "source_merge_associated_prs": {121},
        "follow_head_commit": {
            "sha": FOLLOW_HEAD,
            "tree": FOLLOW_TREE,
            "parents": (SOURCE_MERGE,),
        },
        "follow_merge_commit": {
            "sha": FOLLOW_MERGE,
            "tree": FOLLOW_TREE,
            "parents": (SOURCE_MERGE,),
        },
        "follow_merge_associated_prs": {123},
        "expected_source_pr_number": 121,
    }


class BootstrapCommentaryReconciliationTests(unittest.TestCase):
    def test_repository_data_loads_as_bounded_not_global_slice(self):
        doc = commentary.load_reconciliation(
            REPO_ROOT / "data" / "bootstrap-commentary-reconciliation.json",
            REPO_ROOT / "data" / "bootstrap-source.json",
        )
        self.assertEqual(doc["coverage"]["finding_ids"], ["F050", "F051"])
        self.assertTrue(doc["coverage"]["complete_for_scope"])
        self.assertFalse(doc["coverage"]["global_commentary_reconciliation_complete"])
        unknown = next(entry for entry in doc["entries"] if entry["finding_id"] == "F050")
        self.assertEqual(unknown["reconciliation_status"], commentary.PRESERVED_UNKNOWN_STATUS)
        self.assertIsNone(unknown["follow_up"])

    def test_supported_material_address_evidence_passes_with_redacted_pr_merge_sha(self):
        entry = entry_record()
        self.assertEqual(commentary.validate_normalized_source(entry, finding_record()), [])
        self.assertEqual(
            commentary.validate_original_github_evidence(entry, source_snapshot()), []
        )
        self.assertEqual(
            commentary.validate_follow_up_live(
                entry, source_snapshot(), resolved_follow_up()
            ),
            [],
        )

    def test_original_codex_comment_must_match_reviewed_head(self):
        snapshot = source_snapshot()
        snapshot["review_comments"][0]["original_commit_id"] = FOLLOW_HEAD
        errors = commentary.validate_original_github_evidence(entry_record(), snapshot)
        self.assertTrue(any("original_commit_id differs" in error for error in errors))

    def test_source_merge_commit_must_match_exact_reviewed_head_tree(self):
        resolved = resolved_follow_up()
        resolved["source_merge_commit"]["tree"] = "3" * 40
        errors = commentary.validate_follow_up_live(
            entry_record(), source_snapshot(), resolved
        )
        self.assertTrue(any("source merged commit tree differs" in error for error in errors))

    def test_source_merge_commit_must_be_associated_with_source_pr(self):
        resolved = resolved_follow_up()
        resolved["source_merge_associated_prs"] = {120}
        errors = commentary.validate_follow_up_live(
            entry_record(), source_snapshot(), resolved
        )
        self.assertTrue(any("exact source PR" in error for error in errors))

    def test_follow_up_merge_commit_must_be_directly_based_on_source_merge(self):
        resolved = resolved_follow_up()
        resolved["follow_merge_commit"]["parents"] = ("4" * 40,)
        errors = commentary.validate_follow_up_live(
            entry_record(), source_snapshot(), resolved
        )
        self.assertTrue(any("not directly based" in error for error in errors))

    def test_follow_up_merge_commit_tree_must_match_exact_head(self):
        resolved = resolved_follow_up()
        resolved["follow_merge_commit"]["tree"] = "5" * 40
        errors = commentary.validate_follow_up_live(
            entry_record(), source_snapshot(), resolved
        )
        self.assertTrue(any("merged commit tree differs" in error for error in errors))

    def test_follow_up_merge_commit_must_be_associated_with_follow_up_pr(self):
        resolved = resolved_follow_up()
        resolved["follow_merge_associated_prs"] = {122}
        errors = commentary.validate_follow_up_live(
            entry_record(), source_snapshot(), resolved
        )
        self.assertTrue(any("exact follow-up PR" in error for error in errors))

    def test_fake_caller_regression_evidence_cannot_be_omitted(self):
        resolved = resolved_follow_up()
        resolved["contents"][TEST_PATH] = resolved["contents"][TEST_PATH].replace(
            "cwd: callerRoot", "cwd: process.cwd()"
        )
        errors = commentary.validate_follow_up_live(
            entry_record(), source_snapshot(), resolved
        )
        self.assertTrue(any("cwd: callerRoot" in error for error in errors))

    def test_caller_selectable_runtime_override_is_forbidden(self):
        resolved = resolved_follow_up()
        resolved["contents"][LAUNCHER_PATH] += "\nconst old = 'CHAT_SEMANTIC_RUNTIME_ROOT';\n"
        errors = commentary.validate_follow_up_live(
            entry_record(), source_snapshot(), resolved
        )
        self.assertTrue(any("forbidden evidence token" in error for error in errors))

    def test_follow_up_changed_file_inventory_is_exact(self):
        resolved = resolved_follow_up()
        resolved["changed_files"] = sorted(resolved["changed_files"] + ["unexpected.txt"])
        errors = commentary.validate_follow_up_live(
            entry_record(), source_snapshot(), resolved
        )
        self.assertTrue(any("changed-file inventory differs" in error for error in errors))

    def test_source_row_and_confirmed_state_are_bound_to_normalized_finding(self):
        finding = finding_record()
        finding["source_row"] = 999
        finding["confirmed"] = "UNKNOWN"
        errors = commentary.validate_normalized_source(entry_record(), finding)
        self.assertTrue(any("source row differs" in error for error in errors))
        self.assertTrue(any("confirmed state differs" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
