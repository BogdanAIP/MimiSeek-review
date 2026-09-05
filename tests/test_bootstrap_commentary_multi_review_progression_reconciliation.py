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
    "bootstrap_commentary_multi_review_progression",
    TOOLS_ROOT / "verify_bootstrap_commentary_multi_review_progression_reconciliation.py",
)
progression = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = progression
SPEC.loader.exec_module(progression)

ROOT_HEAD = "aafddd3b37476a65558d56755edd2ae440648b74"
INITIAL_RESPONSE = "9af22cdcbb60501dca968fd10f12dc1d40ee6482"
F059_HEAD = "10643bd160c65b8d8df690266390725d5d0dd6eb"
F059_RESPONSE = "7c8280721d96e7822d3c56e08e00ff6cb3868349"
F061_HEAD = F059_RESPONSE
F061_RESPONSE = "1467bd3c97511f8349b574d00a6029e8e98b3fe7"
FINAL_HEAD = "9120fd768255775d938da5e827043db9691a8886"

ROOT_REVIEW = 5043917353
ROOT_COMMENT = 3874358356
ROOT_REPLY = 3874611686
F059_REVIEW = 5044266036
F059_COMMENT = 3874658738
F059_REPLY = 3874859175
F061_REVIEW = 5044434417
F061_COMMENT = 3874801219
F061_REPLY = 3875173639

CONTENT = {
    (INITIAL_RESPONSE, "uv_studio/agent/stage17_provenance.py"): """
_DELEGATION_REFERENCE_PATTERN = re.compile(
    r"^agent_delegate_(?:explore|plan|media|critic)_[0-9a-f]{32}$"
)
def _is_delegation_reference(value):
    return _DELEGATION_REFERENCE_PATTERN.fullmatch(value) is not None
""",
    (INITIAL_RESPONSE, "tests/test_agent_stage17_result_integrity.py"): """
def test_prefix_like_canonical_project_id_is_not_a_delegation_reference(self):
    project_id="agent_delegate_project"
""",
    (F059_RESPONSE, "uv_studio/agent/stage17_provenance.py"): """
def prepare(self, request: AgentSubagentRequest) -> AgentSubagentContext:
    if _is_delegation_reference(reference):
        raise AgentSubagentError("canonical identity collides with the reserved functional-subagent delegation namespace")
""",
    (F059_RESPONSE, "tests/test_agent_stage17_result_integrity.py"): """
def test_complete_delegation_namespace_is_reserved_from_canonical_project_ids(self):
    project_id="agent_delegate_media_00000000000000000000000000000000"
""",
    (F061_RESPONSE, "uv_studio/agent/stage17_provenance.py"): """
_RESERVED_ACTION_OUTPUT_FIELDS = {}
_RESERVED_SKILL_OUTPUT_FIELDS = {}
def _validate_reserved_proposal_outputs(proposals):
    raise AgentSubagentError("planned canonical output collides with the reserved functional-subagent delegation namespace")
_validate_reserved_proposal_outputs(base.proposals)
_validate_reserved_proposal_outputs(result.proposals)
""",
    (F061_RESPONSE, "tests/test_agent_stage17_result_integrity.py"): """
_RESERVED_TRACK_ID = "agent_delegate_media_00000000000000000000000000000000"
def test_planned_canonical_output_cannot_occupy_delegation_namespace(self):
    pass
""",
}


def finding(finding_id, head, source_row):
    groups = {"F057": "UV71-05", "F059": "UV71-07", "F061": "UV71-09"}
    claims = {
        "F057": "Prefix-only delegation detection misclassified valid canonical IDs beginning with agent_delegate_",
        "F059": "A valid canonical identity could exactly collide with the complete typed delegation-ID format",
        "F061": "A proposal could create a canonical output inside the reserved delegation namespace",
    }
    return {
        "finding_id": finding_id,
        "repository": "BogdanAIP/uv-studio",
        "pr": 71,
        "head_sha": head,
        "reviewer": "Codex Review",
        "severity": "P2",
        "confirmed": "CONFIRMED",
        "scored": False,
        "defect_group": groups[finding_id],
        "category": "Identity / namespace",
        "finding": claims[finding_id],
        "same_head_match": False,
        "other_reviewer": None,
        "source_url": "https://github.com/BogdanAIP/uv-studio/pull/71",
        "evidence_confidence": "High",
        "source_row": source_row,
    }


def findings_by_id():
    return {
        "F057": finding("F057", ROOT_HEAD, 58),
        "F059": finding("F059", F059_HEAD, 60),
        "F061": finding("F061", F061_HEAD, 62),
    }


def entry():
    doc = progression.load_document(
        REPO_ROOT / "data" / "bootstrap-commentary-multi-review-progression-reconciliation.json",
        REPO_ROOT / "data" / "bootstrap-source.json",
    )
    return doc["entries"][0]


def snapshot():
    return {
        "repository": "BogdanAIP/uv-studio",
        "repository_id": 1329787546,
        "pr_number": 71,
        "pull_request": {
            "number": 71,
            "state": "closed",
            "merged_at": "2026-08-27T19:37:20Z",
            "head": {"sha": FINAL_HEAD},
            "user": {"login": "BogdanAIP"},
        },
        "reviews": [
            {"id": ROOT_REVIEW, "commit_id": ROOT_HEAD, "user": {"login": progression.CODEX_LOGIN}},
            {"id": F059_REVIEW, "commit_id": F059_HEAD, "user": {"login": progression.CODEX_LOGIN}},
            {"id": F061_REVIEW, "commit_id": F061_HEAD, "user": {"login": progression.CODEX_LOGIN}},
        ],
        "review_comments": [
            {
                "id": ROOT_COMMENT,
                "pull_request_review_id": ROOT_REVIEW,
                "commit_id": ROOT_HEAD,
                "original_commit_id": ROOT_HEAD,
                "user": {"login": progression.CODEX_LOGIN},
            },
            {
                "id": F059_COMMENT,
                "pull_request_review_id": F059_REVIEW,
                "commit_id": F059_HEAD,
                "original_commit_id": F059_HEAD,
                "user": {"login": progression.CODEX_LOGIN},
            },
            {
                "id": F061_COMMENT,
                "pull_request_review_id": F061_REVIEW,
                "commit_id": F061_HEAD,
                "original_commit_id": F061_HEAD,
                "user": {"login": progression.CODEX_LOGIN},
            },
        ],
        "commits": [
            {"sha": INITIAL_RESPONSE},
            {"sha": F059_HEAD},
            {"sha": F059_RESPONSE},
            {"sha": F061_RESPONSE},
            {"sha": FINAL_HEAD},
        ],
    }


class FakeClient:
    def __init__(self):
        self.reply_parent_override = {}
        self.reply_body_override = {}
        self.compare_status_override = {}
        self.compare_count_override = {}
        self.compare_last_override = {}
        self.compare_files_override = {}
        self.content = dict(CONTENT)

    @staticmethod
    def _stages():
        return {
            (ROOT_HEAD, INITIAL_RESPONSE): (ROOT_COMMENT, ROOT_REPLY, 4),
            (F059_HEAD, F059_RESPONSE): (F059_COMMENT, F059_REPLY, 2),
            (F061_HEAD, F061_RESPONSE): (F061_COMMENT, F061_REPLY, 11),
        }

    def get(self, path, params=None):
        prefix = "/repos/BogdanAIP/uv-studio"
        for (reviewed, response), (comment_id, reply_id, count) in self._stages().items():
            if path == f"{prefix}/compare/{reviewed}...{response}":
                actual_count = self.compare_count_override.get(response, count)
                shas = [f"{index:040x}" for index in range(1, actual_count)] + [
                    self.compare_last_override.get(response, response)
                ]
                required = [
                    "tests/test_agent_stage17_result_integrity.py",
                    "uv_studio/agent/stage17_provenance.py",
                ]
                files = self.compare_files_override.get(response, required)
                return {
                    "status": self.compare_status_override.get(response, "ahead"),
                    "base_commit": {"sha": reviewed},
                    "merge_base_commit": {"sha": reviewed},
                    "commits": [{"sha": item} for item in shas],
                    "files": [{"filename": item} for item in files],
                }
            if path == f"{prefix}/pulls/comments/{reply_id}":
                return {
                    "id": reply_id,
                    "in_reply_to_id": self.reply_parent_override.get(reply_id, comment_id),
                    "pull_request_url": "https://api.github.com/repos/BogdanAIP/uv-studio/pulls/71",
                    "user": {"login": "BogdanAIP"},
                    "body": self.reply_body_override.get(reply_id, f"Fixed in code-bearing head `{response}`."),
                }
            if path == f"{prefix}/commits/{response}":
                return {"sha": response}
        if path.startswith(f"{prefix}/contents/"):
            ref = params["ref"]
            file_path = path.split("/contents/", 1)[1]
            text = self.content[(ref, file_path)]
            return {
                "type": "file",
                "encoding": "base64",
                "content": base64.b64encode(text.encode("utf-8")).decode("ascii"),
            }
        raise AssertionError(f"unexpected GET {path} params={params}")


class BootstrapCommentaryMultiReviewProgressionTests(unittest.TestCase):
    def test_repository_slice_preserves_distinct_f057_f059_f061(self):
        doc = progression.load_document(
            REPO_ROOT / "data" / "bootstrap-commentary-multi-review-progression-reconciliation.json",
            REPO_ROOT / "data" / "bootstrap-source.json",
        )
        self.assertEqual(doc["coverage"]["finding_ids"], ["F057"])
        self.assertEqual(doc["coverage"]["related_followup_finding_ids"], ["F059", "F061"])
        self.assertFalse(doc["coverage"]["global_commentary_reconciliation_complete"])
        self.assertEqual(
            [item["finding_id"] for item in doc["entries"][0]["followup_reviews"]],
            ["F059", "F061"],
        )

    def test_source_and_live_progression_pass(self):
        item = entry()
        snap = snapshot()
        self.assertEqual(progression.validate_source(item, findings_by_id(), snap), [])
        self.assertEqual(progression.resolve_and_validate_live(FakeClient(), item, snap), [])

    def test_related_finding_head_must_remain_exact(self):
        records = findings_by_id()
        records["F059"]["head_sha"] = "0" * 40
        errors = progression.validate_source(entry(), records, snapshot())
        self.assertTrue(any("F059: normalized head_sha differs" in error for error in errors))

    def test_inline_comment_original_commit_must_match_reviewed_head(self):
        snap = snapshot()
        snap["review_comments"][1]["original_commit_id"] = "1" * 40
        errors = progression.validate_source(entry(), findings_by_id(), snap)
        self.assertTrue(any("F059: finding original_commit differs" in error for error in errors))

    def test_owner_reply_must_target_exact_corresponding_finding(self):
        client = FakeClient()
        client.reply_parent_override[F059_REPLY] = ROOT_COMMENT
        errors = progression.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("F059: owner reply does not target exact finding" in error for error in errors))

    def test_owner_reply_must_name_full_exact_response_head(self):
        client = FakeClient()
        client.reply_body_override[F061_REPLY] = "Fixed in final code/docs head."
        errors = progression.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("F061: owner reply does not name full exact response head" in error for error in errors))

    def test_each_response_must_descend_from_its_own_reviewed_head(self):
        client = FakeClient()
        client.compare_status_override[F059_RESPONSE] = "diverged"
        errors = progression.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("F059: response head is not reported ahead" in error for error in errors))

    def test_compare_must_terminate_at_exact_response_head(self):
        client = FakeClient()
        client.compare_last_override[F061_RESPONSE] = "2" * 40
        errors = progression.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("F061: compare does not terminate" in error for error in errors))

    def test_expected_compare_commit_count_is_bounded(self):
        client = FakeClient()
        client.compare_count_override[INITIAL_RESPONSE] = 3
        errors = progression.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("F057: compare commit count differs" in error for error in errors))

    def test_required_changed_file_cannot_disappear(self):
        client = FakeClient()
        client.compare_files_override[F061_RESPONSE] = ["uv_studio/agent/stage17_provenance.py"]
        errors = progression.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("F061: compare is missing required changed files" in error for error in errors))

    def test_required_response_content_cannot_disappear(self):
        client = FakeClient()
        client.content[(F061_RESPONSE, "uv_studio/agent/stage17_provenance.py")] = "pass"
        errors = progression.resolve_and_validate_live(client, entry(), snapshot())
        self.assertTrue(any("F061:" in error and "missing required token" in error for error in errors))

    def test_contract_rejects_collapsed_followup_identity(self):
        import json
        import tempfile

        source = REPO_ROOT / "data" / "bootstrap-commentary-multi-review-progression-reconciliation.json"
        doc = json.loads(source.read_text(encoding="utf-8"))
        doc["entries"][0]["followup_reviews"][1]["finding_id"] = "F059"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.json"
            path.write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaises(progression.MultiReviewProgressionError):
                progression.load_document(path, REPO_ROOT / "data" / "bootstrap-source.json")

    def test_contract_rejects_wrong_root_source_note(self):
        import json
        import tempfile

        source = REPO_ROOT / "data" / "bootstrap-commentary-multi-review-progression-reconciliation.json"
        doc = json.loads(source.read_text(encoding="utf-8"))
        doc["entries"][0]["source_note"] = "Fixed."
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.json"
            path.write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaisesRegex(progression.MultiReviewProgressionError, "source_note differs"):
                progression.load_document(path, REPO_ROOT / "data" / "bootstrap-source.json")


if __name__ == "__main__":
    unittest.main()
