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
    "bootstrap_commentary_fix_evidence",
    TOOLS_ROOT / "verify_bootstrap_commentary_fix_evidence_reconciliation.py",
)
fixev = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = fixev
SPEC.loader.exec_module(fixev)

REVIEWED = "238870958fb88a291cdfa3e2345d8c5d84821534"
F053_FIX = "ce4a51f042e628df2f569532d42be17394e2ab4b"
F054_FIX = "aafddd3b37476a65558d56755edd2ae440648b74"
REVIEW_ID = 5043741722
F053_COMMENT = 3874197354
F054_COMMENT = 3874197368
F053_REPLY = 3874292248
F054_REPLY = 3874293460

F053_FILES = [
    "tests/test_agent_stage17_result_integrity.py",
    "uv_studio/agent/stage17_provenance.py",
]
F054_FILES = [
    "tests/test_agent_stage17_shared_executor_provenance.py",
    "uv_studio/agent/stage16_review_consistency.py",
]

CONTENT = {
    (F053_FIX, F053_FILES[0]): """
def test_persist_plan_revalidates_media_role_for_exactly_addressed_result(self):
    with self.assertRaisesRegex(AgentSubagentError, "media role cannot propose action 'production.create_scene'"):
        pass
    self.assertEqual(AgentPlanStore(self.store).list(self.project.project_id), ())
""",
    (F053_FIX, F053_FILES[1]): """
if not isinstance(result, AgentSubagentResult):
    raise AgentSubagentError("bad")
self._validate_role_output(
    self.catalog.get(result.request.role), tuple(result.proposals)
)
expected_delegation_id = _delegation_id(result)
""",
    (F054_FIX, F054_FILES[0]): """
def test_plain_stage16_executor_preserves_stage17_plan_provenance(self):
    self.assertIn(result.delegation_id, trace.canonical_references)
def test_plain_stage16_reopen_recovery_preserves_stage17_plan_provenance(self):
    self.assertIn(result.delegation_id, traces[0].canonical_references)
""",
    (F054_FIX, F054_FILES[1]): """
references = list(plan.canonical_references)
references.extend(extra_references)
correlation = (*plan.canonical_references,)
""",
}


def finding(fid):
    row = 54 if fid == "F053" else 55
    category = "Role boundary / persistence" if fid == "F053" else "Provenance / recovery"
    text = (
        "Persisting a role result did not revalidate proposals or recompute delegation identity"
        if fid == "F053"
        else "Shared Stage-16 task execution could drop Stage-17 delegation provenance"
    )
    return {
        "finding_id": fid,
        "repository": "BogdanAIP/uv-studio",
        "pr": 71,
        "head_sha": REVIEWED,
        "reviewer": "Codex Review",
        "severity": "P2",
        "confirmed": "CONFIRMED",
        "scored": False,
        "defect_group": "UV71-01" if fid == "F053" else "UV71-02",
        "category": category,
        "finding": text,
        "same_head_match": False,
        "other_reviewer": None,
        "source_url": "https://github.com/BogdanAIP/uv-studio/pull/71",
        "evidence_confidence": "High",
        "source_row": row,
    }


def entry(fid):
    expected = fixev.EXPECTED[fid]
    files = F053_FILES if fid == "F053" else F054_FILES
    assertions = []
    if fid == "F053":
        assertions = [
            {
                "path": F053_FILES[0],
                "required_present": [
                    "test_persist_plan_revalidates_media_role_for_exactly_addressed_result",
                    "media role cannot propose action 'production.create_scene'",
                    "self.assertEqual(AgentPlanStore(self.store).list(self.project.project_id), ())",
                ],
                "required_absent": [],
            },
            {
                "path": F053_FILES[1],
                "required_present": [
                    "if not isinstance(result, AgentSubagentResult):",
                    "self._validate_role_output(",
                    "expected_delegation_id = _delegation_id(result)",
                ],
                "required_absent": [],
            },
        ]
    else:
        assertions = [
            {
                "path": F054_FILES[0],
                "required_present": [
                    "test_plain_stage16_executor_preserves_stage17_plan_provenance",
                    "test_plain_stage16_reopen_recovery_preserves_stage17_plan_provenance",
                    "self.assertIn(result.delegation_id, trace.canonical_references)",
                    "self.assertIn(result.delegation_id, traces[0].canonical_references)",
                ],
                "required_absent": [],
            },
            {
                "path": F054_FILES[1],
                "required_present": [
                    "references = list(plan.canonical_references)",
                    "*plan.canonical_references,",
                ],
                "required_absent": [],
            },
        ]
    return {
        "finding_id": fid,
        "repository": expected["repository"],
        "pr": expected["pr"],
        "reviewed_head": expected["reviewed_head"],
        "source_sheet": "Findings",
        "source_row": expected["source_row"],
        "source_confirmed": expected["source_confirmed"],
        "source_note": expected["source_note"],
        "kind": fixev.KIND,
        "github_evidence": {
            "codex_review_id": expected["codex_review_id"],
            "codex_review_comment_id": expected["codex_review_comment_id"],
            "owner_reply_comment_id": expected["owner_reply_comment_id"],
        },
        "fix_evidence": {
            "fix_head": expected["fix_head"],
            "changed_files": files,
            "content_assertions": assertions,
        },
        "reconciliation_status": fixev.STATUS,
        "authority_limit": "Bounded material fix evidence only.",
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
            "head": {"sha": "9120fd768255775d938da5e827043db9691a8886"},
            "user": {"login": "BogdanAIP"},
        },
        "reviews": [
            {
                "id": REVIEW_ID,
                "commit_id": REVIEWED,
                "user": {"login": fixev.CODEX_LOGIN},
            }
        ],
        "review_comments": [
            {
                "id": F053_COMMENT,
                "pull_request_review_id": REVIEW_ID,
                "commit_id": REVIEWED,
                "original_commit_id": REVIEWED,
                "user": {"login": fixev.CODEX_LOGIN},
            },
            {
                "id": F054_COMMENT,
                "pull_request_review_id": REVIEW_ID,
                "commit_id": REVIEWED,
                "original_commit_id": REVIEWED,
                "user": {"login": fixev.CODEX_LOGIN},
            },
        ],
        "commits": [{"sha": F053_FIX}, {"sha": F054_FIX}],
    }


class FakeClient:
    def __init__(self):
        self.compare_status = "ahead"
        self.compare_merge_base = REVIEWED
        self.reply_parent_override = None
        self.reply_body_override = None
        self.commit_files_override = {}
        self.content_override = {}

    def get(self, path, params=None):
        prefix = "/repos/BogdanAIP/uv-studio"
        if path.startswith(f"{prefix}/compare/{REVIEWED}..."):
            return {
                "status": self.compare_status,
                "base_commit": {"sha": REVIEWED},
                "merge_base_commit": {"sha": self.compare_merge_base},
            }
        if path == f"{prefix}/pulls/comments/{F053_REPLY}":
            parent = self.reply_parent_override if self.reply_parent_override is not None else F053_COMMENT
            body = self.reply_body_override if self.reply_body_override is not None else f"Fixed in `{F053_FIX}`."
            return {
                "id": F053_REPLY,
                "in_reply_to_id": parent,
                "original_commit_id": REVIEWED,
                "pull_request_url": f"https://api.github.com/repos/BogdanAIP/uv-studio/pulls/71",
                "user": {"login": "BogdanAIP"},
                "body": body,
            }
        if path == f"{prefix}/pulls/comments/{F054_REPLY}":
            parent = self.reply_parent_override if self.reply_parent_override is not None else F054_COMMENT
            body = self.reply_body_override if self.reply_body_override is not None else f"Fixed in `{F054_FIX}`."
            return {
                "id": F054_REPLY,
                "in_reply_to_id": parent,
                "original_commit_id": REVIEWED,
                "pull_request_url": f"https://api.github.com/repos/BogdanAIP/uv-studio/pulls/71",
                "user": {"login": "BogdanAIP"},
                "body": body,
            }
        if path == f"{prefix}/commits/{F053_FIX}":
            files = self.commit_files_override.get(F053_FIX, F053_FILES)
            return {"sha": F053_FIX, "files": [{"filename": item} for item in files]}
        if path == f"{prefix}/commits/{F054_FIX}":
            files = self.commit_files_override.get(F054_FIX, F054_FILES)
            return {"sha": F054_FIX, "files": [{"filename": item} for item in files]}
        if path.startswith(f"{prefix}/contents/"):
            ref = params["ref"]
            file_path = path.split("/contents/", 1)[1]
            text = self.content_override.get((ref, file_path), CONTENT[(ref, file_path)])
            return {
                "type": "file",
                "encoding": "base64",
                "content": base64.b64encode(text.encode("utf-8")).decode("ascii"),
            }
        raise AssertionError(f"unexpected GET {path} params={params}")


class BootstrapCommentaryFixEvidenceTests(unittest.TestCase):
    def test_repository_slice_is_exactly_f053_f054_and_not_global(self):
        doc = fixev.load_document(
            REPO_ROOT / "data" / "bootstrap-commentary-fix-evidence-reconciliation.json",
            REPO_ROOT / "data" / "bootstrap-source.json",
        )
        self.assertEqual(doc["coverage"]["finding_ids"], ["F053", "F054"])
        self.assertTrue(doc["coverage"]["complete_for_scope"])
        self.assertFalse(doc["coverage"]["global_commentary_reconciliation_complete"])

    def test_f053_source_and_live_chain_pass(self):
        item = entry("F053")
        self.assertEqual(fixev.validate_source(item, finding("F053"), snapshot()), [])
        self.assertEqual(fixev.resolve_and_validate_live(FakeClient(), item, snapshot()), [])

    def test_f054_source_and_live_chain_pass(self):
        item = entry("F054")
        self.assertEqual(fixev.validate_source(item, finding("F054"), snapshot()), [])
        self.assertEqual(fixev.resolve_and_validate_live(FakeClient(), item, snapshot()), [])

    def test_owner_reply_must_target_exact_original_finding(self):
        client = FakeClient()
        client.reply_parent_override = 1
        errors = fixev.resolve_and_validate_live(client, entry("F053"), snapshot())
        self.assertTrue(any("does not target exact original finding" in error for error in errors))

    def test_owner_reply_must_name_full_exact_fix_head(self):
        client = FakeClient()
        client.reply_body_override = "Fixed in another commit."
        errors = fixev.resolve_and_validate_live(client, entry("F053"), snapshot())
        self.assertTrue(any("does not name full exact fix head" in error for error in errors))

    def test_fix_head_must_descend_from_reviewed_head(self):
        client = FakeClient()
        client.compare_status = "diverged"
        client.compare_merge_base = "0" * 40
        errors = fixev.resolve_and_validate_live(client, entry("F054"), snapshot())
        self.assertTrue(any("not an exact descendant" in error for error in errors))

    def test_fix_commit_must_be_in_source_pr_snapshot(self):
        snap = snapshot()
        snap["commits"] = [{"sha": F054_FIX}]
        errors = fixev.validate_source(entry("F053"), finding("F053"), snap)
        self.assertTrue(any("not a commit of the exact source PR" in error for error in errors))

    def test_exact_fix_commit_changed_files_are_required(self):
        client = FakeClient()
        client.commit_files_override[F053_FIX] = [F053_FILES[0]]
        errors = fixev.resolve_and_validate_live(client, entry("F053"), snapshot())
        self.assertTrue(any("changed-file inventory differs" in error for error in errors))

    def test_required_material_fix_content_cannot_be_missing(self):
        client = FakeClient()
        client.content_override[(F054_FIX, F054_FILES[1])] = "references = list(extra_references)"
        errors = fixev.resolve_and_validate_live(client, entry("F054"), snapshot())
        self.assertTrue(any("missing required token" in error for error in errors))

    def test_original_finding_identity_is_exact(self):
        snap = snapshot()
        snap["review_comments"][0]["commit_id"] = F053_FIX
        errors = fixev.validate_source(entry("F053"), finding("F053"), snap)
        self.assertTrue(any("original finding commit differs" in error for error in errors))

    def test_bounded_contract_rejects_wrong_source_note(self):
        item = entry("F053")
        item["source_note"] = "Fixed."
        doc = {
            "schema_version": fixev.SCHEMA_VERSION,
            "authority": fixev.AUTHORITY,
            "source_artifact_sha256": "6fe79a73a7f10e528a7323adce1fafcc1951955394a0dbece31a5eec73d6391a",
            "coverage": {
                "kind": "bounded_same_pr_material_fix_evidence_slice",
                "source_sheet": "Findings",
                "finding_ids": ["F053", "F054"],
                "complete_for_scope": True,
                "global_commentary_reconciliation_complete": False,
            },
            "entries": [item, entry("F054")],
            "rules": ["bounded"],
        }
        import json, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.json"
            path.write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaisesRegex(fixev.FixEvidenceError, "source_note differs"):
                fixev.load_document(path, REPO_ROOT / "data" / "bootstrap-source.json")


if __name__ == "__main__":
    unittest.main()
