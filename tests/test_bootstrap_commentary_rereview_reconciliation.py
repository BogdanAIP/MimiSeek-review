import base64
import copy
import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = REPO_ROOT / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))
SPEC = importlib.util.spec_from_file_location(
    "bootstrap_commentary_rereview",
    TOOLS_ROOT / "verify_bootstrap_commentary_rereview_reconciliation.py",
)
rereview = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = rereview
SPEC.loader.exec_module(rereview)

REVIEWED = "0dde5aab1725c076ff56e2d2c8662c842e57b8ae"
FIXED = "d6ea5bbd913d8a3ab27d7d1521d389e972602de2"
REVIEW_ID = 5053423808
FINDING_COMMENT = 3882602422
OWNER_REPLY = 3882673119
REREVIEW_REQUEST = 5455619813
CLEAN_RESULT = 5455644288
TEST_PATH = "tests/test_computer_use_architecture_contract.py"
FILES = [
    "project-context/COMPUTER_USE_ARCHITECTURE.md",
    "project-context/ROADMAP.md",
    TEST_PATH,
]

FIXED_TEST = '''
visual_section = architecture.split("### Fresh visual post-action verification", maxsplit=1)[1].split(
    "### Environmental content is untrusted data", maxsplit=1
)[0].casefold()
self.assertIn("this is **not** a screenshot-after-every-action requirement", visual_section)
self.assertIn("does **not** require a screenshot after every action", roadmap.casefold())
'''


def entry():
    return {
        "finding_id": "F052",
        "repository": "BogdanAIP/chat-agent-platform",
        "pr": 129,
        "reviewed_head": REVIEWED,
        "source_sheet": "Findings",
        "source_row": 53,
        "source_confirmed": "CONFIRMED",
        "source_note": "Fixed; final exact-head Codex re-review reported no remaining major issues.",
        "kind": rereview.KIND,
        "github_evidence": {
            "codex_review_id": REVIEW_ID,
            "codex_review_comment_id": FINDING_COMMENT,
        },
        "resolution_evidence": {
            "fixed_head": FIXED,
            "owner_reply_comment_id": OWNER_REPLY,
            "rereview_request_comment_id": REREVIEW_REQUEST,
            "clean_codex_result_comment_id": CLEAN_RESULT,
            "changed_files": FILES,
            "content_assertions": [
                {
                    "path": TEST_PATH,
                    "required_present": [
                        'visual_section = architecture.split("### Fresh visual post-action verification", maxsplit=1)[1].split(',
                        'self.assertIn("this is **not** a screenshot-after-every-action requirement", visual_section)',
                        'self.assertIn("does **not** require a screenshot after every action", roadmap.casefold())',
                    ],
                    "required_absent": [],
                }
            ],
        },
        "reconciliation_status": rereview.STATUS,
        "authority_limit": "Bounded review evidence only.",
    }


def finding():
    return {
        "finding_id": "F052",
        "repository": "BogdanAIP/chat-agent-platform",
        "pr": 129,
        "head_sha": REVIEWED,
        "reviewer": "Codex Review",
        "severity": "P2",
        "confirmed": "CONFIRMED",
        "scored": False,
        "defect_group": "CAP129-01",
        "category": "Contract / acceptance semantics",
        "finding": "Visual-verification test checked a screenshot keyword rather than the complete screenshot-after-every-action negation",
        "same_head_match": False,
        "other_reviewer": None,
        "source_url": "https://github.com/BogdanAIP/chat-agent-platform/pull/129",
        "evidence_confidence": "High",
        "source_row": 53,
    }


def snapshot():
    return {
        "repository": "BogdanAIP/chat-agent-platform",
        "repository_id": 1326588757,
        "pr_number": 129,
        "pull_request": {
            "number": 129,
            "state": "closed",
            "merged_at": "2026-08-28T17:32:58Z",
            "head": {"sha": FIXED},
            "user": {"login": "BogdanAIP"},
        },
        "reviews": [
            {
                "id": REVIEW_ID,
                "commit_id": REVIEWED,
                "submitted_at": "2026-08-28T17:21:29Z",
                "user": {"login": rereview.CODEX_LOGIN},
            }
        ],
        "review_comments": [
            {
                "id": FINDING_COMMENT,
                "pull_request_review_id": REVIEW_ID,
                "commit_id": REVIEWED,
                "original_commit_id": REVIEWED,
                "created_at": "2026-08-28T17:21:29Z",
                "user": {"login": rereview.CODEX_LOGIN},
            }
        ],
        "issue_comments": [
            {
                "id": CLEAN_RESULT,
                "created_at": "2026-08-28T17:28:24Z",
                "user": {"login": rereview.CODEX_LOGIN},
            }
        ],
    }


class FakeClient:
    def __init__(self):
        self.owner_reply = {
            "id": OWNER_REPLY,
            "in_reply_to_id": FINDING_COMMENT,
            "pull_request_review_id": 5053503406,
            "commit_id": REVIEWED,
            "original_commit_id": REVIEWED,
            "created_at": "2026-08-28T17:32:01Z",
            "pull_request_url": "https://api.github.com/repos/BogdanAIP/chat-agent-platform/pulls/129",
            "user": {"login": "BogdanAIP"},
            "body": f"Fixed on exact head `{FIXED}`. Fresh Codex re-review reported no remaining major issues.",
        }
        self.request = {
            "id": REREVIEW_REQUEST,
            "created_at": "2026-08-28T17:25:53Z",
            "issue_url": "https://api.github.com/repos/BogdanAIP/chat-agent-platform/issues/129",
            "user": {"login": "BogdanAIP"},
            "body": f"@codex review\n\nRe-review exact head `{FIXED}` after addressing the prior P2.",
        }
        self.clean = {
            "id": CLEAN_RESULT,
            "created_at": "2026-08-28T17:28:24Z",
            "issue_url": "https://api.github.com/repos/BogdanAIP/chat-agent-platform/issues/129",
            "user": {"login": rereview.CODEX_LOGIN},
            "performed_via_github_app": {"slug": rereview.CODEX_APP_SLUG},
            "body": "Codex Review: Didn't find any major issues. Breezy!\n\n**Reviewed commit:** `d6ea5bbd91`",
        }
        self.fixed_text = FIXED_TEST
        self.fixed_compare_status = "ahead"
        self.fixed_compare_merge_base = REVIEWED
        self.default_compare_status = "ahead"
        self.default_compare_merge_base = FIXED

    def get(self, path, params=None):
        prefix = "/repos/BogdanAIP/chat-agent-platform"
        if path == f"{prefix}/compare/{REVIEWED}...{FIXED}":
            return {
                "status": self.fixed_compare_status,
                "base_commit": {"sha": REVIEWED},
                "merge_base_commit": {"sha": self.fixed_compare_merge_base},
                "head_commit": {"sha": FIXED},
            }
        if path == prefix:
            return {"default_branch": "main"}
        if path == f"{prefix}/compare/{FIXED}...main":
            return {
                "status": self.default_compare_status,
                "base_commit": {"sha": FIXED},
                "merge_base_commit": {"sha": self.default_compare_merge_base},
            }
        if path == f"{prefix}/pulls/comments/{OWNER_REPLY}":
            return self.owner_reply
        if path == f"{prefix}/issues/comments/{REREVIEW_REQUEST}":
            return self.request
        if path == f"{prefix}/issues/comments/{CLEAN_RESULT}":
            return self.clean
        if path == f"{prefix}/contents/{TEST_PATH}":
            return {
                "type": "file",
                "encoding": "base64",
                "content": base64.b64encode(self.fixed_text.encode("utf-8")).decode("ascii"),
            }
        raise AssertionError(f"unexpected GET {path} params={params}")

    def paged(self, path, params=None):
        if path == "/repos/BogdanAIP/chat-agent-platform/pulls/129/files":
            return [{"filename": name} for name in FILES]
        raise AssertionError(f"unexpected paged {path}")


class BootstrapCommentaryRereviewTests(unittest.TestCase):
    def test_repository_slice_is_exactly_f052_and_not_global(self):
        doc = rereview.load_document(
            REPO_ROOT / "data" / "bootstrap-commentary-rereview-reconciliation.json",
            REPO_ROOT / "data" / "bootstrap-source.json",
        )
        self.assertEqual(doc["coverage"]["finding_ids"], ["F052"])
        self.assertTrue(doc["coverage"]["complete_for_scope"])
        self.assertFalse(doc["coverage"]["global_commentary_reconciliation_complete"])

    def test_source_and_live_clean_rereview_chain_pass(self):
        item = entry()
        self.assertEqual(rereview.validate_source(item, finding(), snapshot()), [])
        self.assertEqual(rereview.resolve_and_validate_live(FakeClient(), item, snapshot()), [])

    def test_clean_result_must_bind_reviewed_commit_prefix_to_fixed_head(self):
        client = FakeClient()
        client.clean["body"] = "Codex Review: Didn't find any major issues.\n\n**Reviewed commit:** `09c58c4bc2`"
        errors = rereview.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("does not match fixed head" in error for error in errors))

    def test_owner_reply_must_target_exact_original_finding(self):
        client = FakeClient()
        client.owner_reply["in_reply_to_id"] = 3882602423
        errors = rereview.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("does not target original Codex finding" in error for error in errors))

    def test_rereview_request_must_name_full_fixed_head(self):
        client = FakeClient()
        client.request["body"] = "@codex review\nwrong head"
        errors = rereview.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("does not bind exact fixed head" in error for error in errors))

    def test_clean_result_must_be_expected_codex_app(self):
        client = FakeClient()
        client.clean["performed_via_github_app"] = {"slug": "other-app"}
        errors = rereview.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("expected Codex GitHub App" in error for error in errors))

    def test_fixed_head_must_descend_from_reviewed_head(self):
        client = FakeClient()
        client.fixed_compare_status = "diverged"
        client.fixed_compare_merge_base = "0" * 40
        errors = rereview.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("not an exact descendant" in error for error in errors))

    def test_fixed_head_must_remain_on_canonical_default_branch_ancestry(self):
        client = FakeClient()
        client.default_compare_status = "diverged"
        client.default_compare_merge_base = REVIEWED
        errors = rereview.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("not on canonical default-branch ancestry" in error for error in errors))

    def test_full_negated_contract_content_is_required(self):
        client = FakeClient()
        client.fixed_text = client.fixed_text.replace(
            "this is **not** a screenshot-after-every-action requirement",
            "screenshot-after-every-action requirement",
        )
        errors = rereview.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("missing required token" in error for error in errors))

    def test_later_codex_finding_invalidates_final_clean_claim(self):
        snap = snapshot()
        snap["review_comments"].append(
            {
                "id": 999,
                "created_at": "2026-08-28T17:29:00Z",
                "user": {"login": rereview.CODEX_LOGIN},
            }
        )
        errors = rereview.resolve_and_validate_live(FakeClient(), entry(), snap)
        self.assertTrue(any("later Codex inline finding" in error for error in errors))

    def test_chronology_must_be_request_then_clean_then_owner_reply_then_merge(self):
        client = FakeClient()
        client.clean["created_at"] = "2026-08-28T17:33:00Z"
        errors = rereview.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("chronology is inconsistent" in error for error in errors))

    def test_original_finding_identity_is_exact(self):
        snap = snapshot()
        snap["review_comments"][0]["commit_id"] = FIXED
        errors = rereview.validate_source(entry(), finding(), snap)
        self.assertTrue(any("original finding commit differs" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
