import base64
import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = REPO_ROOT / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))
SPEC = importlib.util.spec_from_file_location(
    "bootstrap_commentary_fix_baseline",
    TOOLS_ROOT / "verify_bootstrap_commentary_fix_baseline_reconciliation.py",
)
fixbase = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = fixbase
SPEC.loader.exec_module(fixbase)

REVIEWED = "aafddd3b37476a65558d56755edd2ae440648b74"
BASELINE = "9af22cdcbb60501dca968fd10f12dc1d40ee6482"
FINAL = "9120fd768255775d938da5e827043db9691a8886"
REVIEW_ID = 5043917353
COMMENT_ID = 3874358367
REPLY_ID = 3874612625
RANGE_COMMITS = [
    "981bc1a1c4e98d4cb9d98bc9a18ef319c459be57",
    "07d52d21d0dcd6a3e1c9ee4e2e36d34a1ed998be",
    "57518f8fd28744a0c3b3b3051c7093edeba53a06",
    BASELINE,
]
RANGE_FILES = [
    "docs/architecture/CURRENT_ARCHITECTURE.md",
    "docs/architecture/UV_STUDIO_V2_ARCHITECTURE_MAP.md",
    "tests/test_agent_stage17_result_integrity.py",
    "uv_studio/agent/stage17_provenance.py",
]

CONTENT = {
    "uv_studio/agent/stage17_provenance.py": """
if not isinstance(task_coordinator, AgentSubagentTaskCoordinator):
    raise AgentSubagentError("bad")
if (
    task_coordinator.harness is not harness
    or task_coordinator.project_store is not harness.project_store
    or getattr(task_coordinator.plans, "project_store", None) is not harness.project_store
    or getattr(task_coordinator.tasks, "project_store", None) is not harness.project_store
):
    raise AgentSubagentError("Stage 17 task_coordinator must share the exact AgentHarness and Project Store authority")
coordinator_planner = task_coordinator.planner
if getattr(coordinator_planner, "harness", None) is not harness:
    raise AgentSubagentError("Stage 17 task_coordinator planner must share the exact AgentHarness authority")
if requested_planner is not None and coordinator_planner is not requested_planner:
    raise AgentSubagentError("Stage 17 task_coordinator must share the exact AgentPlanner authority")
if requested_planner is None:
    kwargs["planner"] = coordinator_planner
""",
    "tests/test_agent_stage17_result_integrity.py": """
def test_injected_task_coordinator_must_share_exact_harness_authority(self):
    foreign_store = ProjectStore(Path(self.tmp.name) / "foreign-projects")
    foreign_store.create_project(project_id=self.project.project_id)
    with self.assertRaisesRegex(AgentSubagentError, "share the exact AgentHarness and Project Store authority"):
        pass

def test_same_harness_injected_task_coordinator_shares_exact_planner(self):
    self.assertIs(coordinator.planner, task_coordinator.planner)
""",
}


def finding():
    return {
        "finding_id": "F058",
        "repository": "BogdanAIP/uv-studio",
        "pr": 71,
        "head_sha": REVIEWED,
        "reviewer": "Codex Review",
        "severity": "P2",
        "confirmed": "CONFIRMED",
        "scored": False,
        "defect_group": "UV71-06",
        "category": "Authority / dependency injection",
        "finding": "Injected task coordinator from another harness/store could pass type checks and cross authority boundaries",
        "same_head_match": False,
        "other_reviewer": None,
        "source_url": "https://github.com/BogdanAIP/uv-studio/pull/71",
        "evidence_confidence": "High",
        "source_row": 59,
    }


def entry():
    return {
        "finding_id": "F058",
        "repository": "BogdanAIP/uv-studio",
        "pr": 71,
        "reviewed_head": REVIEWED,
        "source_sheet": "Findings",
        "source_row": 59,
        "source_confirmed": "CONFIRMED",
        "source_note": "Fixed with exact harness/store/planner authority checks.",
        "kind": fixbase.KIND,
        "github_evidence": {
            "codex_review_id": REVIEW_ID,
            "codex_review_comment_id": COMMENT_ID,
            "owner_reply_comment_id": REPLY_ID,
        },
        "baseline_evidence": {
            "baseline_head": BASELINE,
            "reviewed_to_baseline_commits": list(RANGE_COMMITS),
            "changed_files": list(RANGE_FILES),
            "content_assertions": [
                {
                    "path": "uv_studio/agent/stage17_provenance.py",
                    "required_present": [
                        "if not isinstance(task_coordinator, AgentSubagentTaskCoordinator):",
                        "task_coordinator.harness is not harness",
                        "task_coordinator.project_store is not harness.project_store",
                        "getattr(task_coordinator.plans, \"project_store\", None)",
                        "getattr(task_coordinator.tasks, \"project_store\", None)",
                        "Stage 17 task_coordinator must share the exact AgentHarness and Project Store authority",
                        "coordinator_planner = task_coordinator.planner",
                        "getattr(coordinator_planner, \"harness\", None) is not harness",
                        "Stage 17 task_coordinator planner must share the exact AgentHarness authority",
                        "requested_planner is not None and coordinator_planner is not requested_planner",
                        "Stage 17 task_coordinator must share the exact AgentPlanner authority",
                        "kwargs[\"planner\"] = coordinator_planner",
                    ],
                    "required_absent": [],
                },
                {
                    "path": "tests/test_agent_stage17_result_integrity.py",
                    "required_present": [
                        "test_injected_task_coordinator_must_share_exact_harness_authority",
                        "foreign_store = ProjectStore",
                        "project_id=self.project.project_id",
                        "share the exact AgentHarness and Project Store authority",
                        "test_same_harness_injected_task_coordinator_shares_exact_planner",
                        "self.assertIs(coordinator.planner, task_coordinator.planner)",
                    ],
                    "required_absent": [],
                },
            ],
        },
        "reconciliation_status": fixbase.STATUS,
        "authority_limit": "Bounded baseline evidence only.",
    }


def snapshot():
    return {
        "repository": "BogdanAIP/uv-studio",
        "repository_id": 1329787546,
        "pr_number": 71,
        "pull_request": {
            "number": 71,
            "state": "closed",
            "merged_at": "2026-08-27T20:00:00Z",
            "head": {"sha": FINAL},
            "user": {"login": "BogdanAIP"},
        },
        "reviews": [
            {
                "id": REVIEW_ID,
                "commit_id": REVIEWED,
                "user": {"login": fixbase.CODEX_LOGIN},
            }
        ],
        "review_comments": [
            {
                "id": COMMENT_ID,
                "pull_request_review_id": REVIEW_ID,
                "commit_id": REVIEWED,
                "original_commit_id": REVIEWED,
                "user": {"login": fixbase.CODEX_LOGIN},
            }
        ],
        "commits": [{"sha": item} for item in (*RANGE_COMMITS, FINAL)],
    }


class FakeClient:
    def __init__(self):
        self.compare_status = "ahead"
        self.compare_base = REVIEWED
        self.compare_merge_base = REVIEWED
        self.compare_commits = list(RANGE_COMMITS)
        self.compare_files = list(RANGE_FILES)
        self.reply_parent = COMMENT_ID
        self.reply_original_commit = REVIEWED
        self.reply_body = f"Fixed in code-bearing head `{BASELINE}`."
        self.content = dict(CONTENT)

    def get(self, path, params=None):
        prefix = "/repos/BogdanAIP/uv-studio"
        if path == f"{prefix}/compare/{REVIEWED}...{BASELINE}":
            return {
                "status": self.compare_status,
                "base_commit": {"sha": self.compare_base},
                "merge_base_commit": {"sha": self.compare_merge_base},
                "commits": [{"sha": item} for item in self.compare_commits],
                "files": [{"filename": item} for item in self.compare_files],
            }
        if path == f"{prefix}/pulls/comments/{REPLY_ID}":
            return {
                "id": REPLY_ID,
                "in_reply_to_id": self.reply_parent,
                "original_commit_id": self.reply_original_commit,
                "pull_request_url": "https://api.github.com/repos/BogdanAIP/uv-studio/pulls/71",
                "user": {"login": "BogdanAIP"},
                "body": self.reply_body,
            }
        if path == f"{prefix}/commits/{BASELINE}":
            return {"sha": BASELINE, "files": [{"filename": "docs/architecture/CURRENT_ARCHITECTURE.md"}]}
        if path.startswith(f"{prefix}/contents/"):
            ref = params["ref"]
            self.assert_ref(ref)
            file_path = path.split("/contents/", 1)[1]
            text = self.content[file_path]
            return {
                "type": "file",
                "encoding": "base64",
                "content": base64.b64encode(text.encode("utf-8")).decode("ascii"),
            }
        raise AssertionError(f"unexpected GET {path} params={params}")

    @staticmethod
    def assert_ref(ref):
        if ref != BASELINE:
            raise AssertionError(f"unexpected content ref {ref}")


class BootstrapCommentaryFixBaselineTests(unittest.TestCase):
    def test_repository_slice_is_exactly_f058_and_not_global(self):
        doc = fixbase.load_document(
            REPO_ROOT / "data" / "bootstrap-commentary-fix-baseline-reconciliation.json",
            REPO_ROOT / "data" / "bootstrap-source.json",
        )
        self.assertEqual(doc["coverage"]["finding_ids"], ["F058"])
        self.assertTrue(doc["coverage"]["complete_for_scope"])
        self.assertFalse(doc["coverage"]["global_commentary_reconciliation_complete"])

    def test_f058_source_and_live_chain_pass(self):
        item = entry()
        snap = snapshot()
        self.assertEqual(fixbase.validate_source(item, finding(), snap), [])
        self.assertEqual(fixbase.resolve_and_validate_live(FakeClient(), item, snap), [])

    def test_owner_reply_must_target_exact_original_finding(self):
        client = FakeClient()
        client.reply_parent = 1
        errors = fixbase.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("does not target exact original finding" in error for error in errors))

    def test_owner_reply_must_name_full_exact_baseline_head(self):
        client = FakeClient()
        client.reply_body = "Fixed in a later baseline."
        errors = fixbase.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("does not name full exact baseline head" in error for error in errors))

    def test_owner_reply_must_preserve_original_reviewed_head_binding(self):
        client = FakeClient()
        client.reply_original_commit = "0" * 40
        errors = fixbase.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("lost original finding-head binding" in error for error in errors))

    def test_baseline_must_descend_exactly_from_reviewed_head(self):
        client = FakeClient()
        client.compare_status = "diverged"
        client.compare_merge_base = "0" * 40
        errors = fixbase.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("not an exact descendant" in error for error in errors))

    def test_exact_ordered_range_commits_are_required(self):
        client = FakeClient()
        client.compare_commits[0], client.compare_commits[1] = client.compare_commits[1], client.compare_commits[0]
        errors = fixbase.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("commit sequence differs" in error for error in errors))

    def test_range_must_terminate_at_exact_declared_baseline(self):
        client = FakeClient()
        client.compare_commits[-1] = "1" * 40
        errors = fixbase.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("does not terminate" in error for error in errors))

    def test_exact_range_changed_file_inventory_is_required(self):
        client = FakeClient()
        client.compare_files = client.compare_files[:-1]
        errors = fixbase.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("range changed-file inventory differs" in error for error in errors))

    def test_baseline_head_must_be_in_source_pr_snapshot(self):
        snap = snapshot()
        snap["commits"] = [{"sha": REVIEWED}, {"sha": FINAL}]
        errors = fixbase.validate_source(entry(), finding(), snap)
        self.assertTrue(any("baseline head is not a commit" in error for error in errors))

    def test_original_finding_identity_is_exact(self):
        snap = snapshot()
        snap["review_comments"][0]["original_commit_id"] = "2" * 40
        errors = fixbase.validate_source(entry(), finding(), snap)
        self.assertTrue(any("original finding original_commit differs" in error for error in errors))

    def test_current_inline_comment_can_only_be_reviewed_or_live_final_head(self):
        snap = snapshot()
        snap["review_comments"][0]["commit_id"] = "3" * 40
        errors = fixbase.validate_source(entry(), finding(), snap)
        self.assertTrue(any("original finding current commit differs" in error for error in errors))

    def test_required_baseline_content_cannot_be_missing(self):
        client = FakeClient()
        client.content["uv_studio/agent/stage17_provenance.py"] = "if task_coordinator: pass"
        errors = fixbase.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("missing required token" in error for error in errors))

    def test_bounded_contract_rejects_wrong_source_note(self):
        import json
        import tempfile

        original_path = REPO_ROOT / "data" / "bootstrap-commentary-fix-baseline-reconciliation.json"
        doc = json.loads(original_path.read_text(encoding="utf-8"))
        doc["entries"][0]["source_note"] = "Fixed."
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.json"
            path.write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaisesRegex(fixbase.FixBaselineError, "source_note differs"):
                fixbase.load_document(path, REPO_ROOT / "data" / "bootstrap-source.json")

    def test_bounded_contract_rejects_range_sequence_substitution(self):
        import json
        import tempfile

        original_path = REPO_ROOT / "data" / "bootstrap-commentary-fix-baseline-reconciliation.json"
        doc = json.loads(original_path.read_text(encoding="utf-8"))
        doc["entries"][0]["baseline_evidence"]["reviewed_to_baseline_commits"][0] = "4" * 40
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.json"
            path.write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaisesRegex(fixbase.FixBaselineError, "commit sequence differs"):
                fixbase.load_document(path, REPO_ROOT / "data" / "bootstrap-source.json")


if __name__ == "__main__":
    unittest.main()
