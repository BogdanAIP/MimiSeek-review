import base64
import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = REPO_ROOT / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

WRAPPER_SPEC = importlib.util.spec_from_file_location(
    "bootstrap_commentary_multi_review_progression_integrated",
    TOOLS_ROOT / "verify_bootstrap_commentary_multi_review_progression_reconciliation.py",
)
progression = importlib.util.module_from_spec(WRAPPER_SPEC)
sys.modules[WRAPPER_SPEC.name] = progression
WRAPPER_SPEC.loader.exec_module(progression)

STAGE_SPEC = importlib.util.spec_from_file_location(
    "bootstrap_commentary_multi_review_progression_stage",
    TOOLS_ROOT / "verify_bootstrap_commentary_multi_review_progression_stage_evidence.py",
)
stage = importlib.util.module_from_spec(STAGE_SPEC)
sys.modules[STAGE_SPEC.name] = stage
STAGE_SPEC.loader.exec_module(stage)

ROOT_HEAD = "aafddd3b37476a65558d56755edd2ae440648b74"
INITIAL_RESPONSE = "9af22cdcbb60501dca968fd10f12dc1d40ee6482"
F059_HEAD = "10643bd160c65b8d8df690266390725d5d0dd6eb"
F059_RESPONSE = "7c8280721d96e7822d3c56e08e00ff6cb3868349"
F061_HEAD = F059_RESPONSE
F061_RESPONSE = "1467bd3c97511f8349b574d00a6029e8e98b3fe7"
FINAL_HEAD = "9120fd768255775d938da5e827043db9691a8886"

REVIEW_TIMES = {
    "F057": "2026-08-27T17:50:12Z",
    "F059": "2026-08-27T18:21:53Z",
    "F061": "2026-08-27T18:39:01Z",
}
RESPONSE_TIMES = {
    INITIAL_RESPONSE: "2026-08-27T18:00:52Z",
    F059_RESPONSE: "2026-08-27T18:34:43Z",
    F061_RESPONSE: "2026-08-27T19:23:30Z",
}
REPLY_TIMES = {
    3874611686: "2026-08-27T18:15:50Z",
    3874859175: "2026-08-27T18:47:15Z",
    3875173639: "2026-08-27T19:30:10Z",
}


def entry():
    doc = progression.load_document(
        REPO_ROOT / "data" / "bootstrap-commentary-multi-review-progression-reconciliation.json",
        REPO_ROOT / "data" / "bootstrap-source.json",
    )
    return doc["entries"][0]


def stages(item):
    return [
        ("F057", item["reviewed_head"], item["initial_fix_evidence"]),
        *[
            (followup["finding_id"], followup["reviewed_head"], followup)
            for followup in item["followup_reviews"]
        ],
    ]


def snapshot(item):
    reviews = []
    comments = []
    for finding_id, reviewed_head, evidence in stages(item):
        when = REVIEW_TIMES[finding_id]
        reviews.append(
            {
                "id": evidence["codex_review_id"],
                "commit_id": reviewed_head,
                "submitted_at": when,
                "user": {"login": progression.CODEX_LOGIN},
            }
        )
        comments.append(
            {
                "id": evidence["codex_review_comment_id"],
                "pull_request_review_id": evidence["codex_review_id"],
                "commit_id": reviewed_head,
                "original_commit_id": reviewed_head,
                "created_at": when,
                "user": {"login": progression.CODEX_LOGIN},
            }
        )
    return {
        "repository": "BogdanAIP/uv-studio",
        "pr_number": 71,
        "pull_request": {
            "number": 71,
            "state": "closed",
            "merged_at": "2026-08-27T19:37:20Z",
            "head": {"sha": FINAL_HEAD},
            "user": {"login": "BogdanAIP"},
        },
        "reviews": reviews,
        "review_comments": comments,
        "commits": [
            {"sha": ROOT_HEAD},
            {"sha": INITIAL_RESPONSE},
            {"sha": F059_HEAD},
            {"sha": F059_RESPONSE},
            {"sha": F061_RESPONSE},
            {"sha": FINAL_HEAD},
        ],
    }


class FakeClient:
    def __init__(self, item):
        self.item = item
        self.cross_status = "ahead"
        self.cross_merge_base = INITIAL_RESPONSE
        self.response_time_override = {}
        self.reply_time_override = {}
        self.content = {}
        for _, _, evidence in stages(item):
            response_head = evidence["response_head"]
            for assertion in evidence["content_assertions"]:
                self.content[(response_head, assertion["path"])] = "\n".join(
                    assertion["required_present"]
                )

    def _stage_by_pair(self, reviewed, response):
        for finding_id, stage_reviewed, evidence in stages(self.item):
            if reviewed == stage_reviewed and response == evidence["response_head"]:
                return finding_id, evidence
        return None

    def get(self, path, params=None):
        prefix = "/repos/BogdanAIP/uv-studio"

        if path == f"{prefix}/compare/{INITIAL_RESPONSE}...{F059_HEAD}":
            return {
                "status": self.cross_status,
                "ahead_by": 1,
                "behind_by": 0,
                "base_commit": {"sha": INITIAL_RESPONSE},
                "merge_base_commit": {"sha": self.cross_merge_base},
                "commits": [{"sha": F059_HEAD}],
                "files": [{"filename": "project-context/PROJECT_STATE.md"}],
            }

        for finding_id, reviewed_head, evidence in stages(self.item):
            response_head = evidence["response_head"]
            if path == f"{prefix}/compare/{reviewed_head}...{response_head}":
                count = evidence["expected_compare_commit_count"]
                shas = [f"{index:040x}" for index in range(1, count)] + [response_head]
                return {
                    "status": "ahead",
                    "ahead_by": count,
                    "behind_by": 0,
                    "base_commit": {"sha": reviewed_head},
                    "merge_base_commit": {"sha": reviewed_head},
                    "commits": [{"sha": sha} for sha in shas],
                    "files": [
                        {"filename": filename}
                        for filename in evidence["required_changed_files"]
                    ],
                }
            if path == f"{prefix}/pulls/comments/{evidence['owner_reply_comment_id']}":
                return {
                    "id": evidence["owner_reply_comment_id"],
                    "in_reply_to_id": evidence["codex_review_comment_id"],
                    "pull_request_url": "https://api.github.com/repos/BogdanAIP/uv-studio/pulls/71",
                    "user": {"login": "BogdanAIP"},
                    "body": f"Fixed in exact response head `{response_head}`.",
                    "created_at": self.reply_time_override.get(
                        evidence["owner_reply_comment_id"],
                        REPLY_TIMES[evidence["owner_reply_comment_id"]],
                    ),
                }
            if path == f"{prefix}/commits/{response_head}":
                return {
                    "sha": response_head,
                    "commit": {
                        "committer": {
                            "date": self.response_time_override.get(
                                response_head,
                                RESPONSE_TIMES[response_head],
                            )
                        }
                    },
                }

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


class BootstrapCommentaryMultiReviewProgressionOrderingTests(unittest.TestCase):
    def test_actual_bounded_cross_stage_progression_passes(self):
        item = entry()
        client = FakeClient(item)
        snap = snapshot(item)

        self.assertEqual(stage.resolve_and_validate_live(client, item, snap), [])
        self.assertEqual(progression._validate_cross_stage_progression(client, item, snap), [])

        # Historical reality: F059's response commit existed before F061 review,
        # while the human owner reply documenting F059 was posted afterwards.
        self.assertGreater(
            progression.parse_z(REPLY_TIMES[3874859175]),
            progression.parse_z(REVIEW_TIMES["F061"]),
        )

    def test_individual_hops_pass_but_disconnected_cross_stage_fails(self):
        item = entry()
        client = FakeClient(item)
        snap = snapshot(item)
        self.assertEqual(stage.resolve_and_validate_live(client, item, snap), [])

        client.cross_status = "diverged"
        client.cross_merge_base = "0" * 40
        errors = progression._validate_cross_stage_progression(client, item, snap)
        self.assertTrue(
            any("F057->F059: next reviewed head is not reported ahead" in error for error in errors)
        )
        self.assertTrue(
            any("F057->F059: prior response head is not the cross-stage merge base" in error for error in errors)
        )

    def test_individual_hops_pass_but_reordered_pr_sequence_fails(self):
        item = entry()
        client = FakeClient(item)
        snap = snapshot(item)
        self.assertEqual(stage.resolve_and_validate_live(client, item, snap), [])

        snap["commits"][1], snap["commits"][2] = snap["commits"][2], snap["commits"][1]
        errors = progression._validate_cross_stage_progression(client, item, snap)
        self.assertTrue(any("source PR commit sequence reorders" in error for error in errors))

    def test_individual_hops_pass_but_cross_stage_time_reversal_fails(self):
        item = entry()
        client = FakeClient(item)
        snap = snapshot(item)
        self.assertEqual(stage.resolve_and_validate_live(client, item, snap), [])

        snap["reviews"][1]["submitted_at"] = "2026-08-27T17:59:00Z"
        snap["review_comments"][1]["created_at"] = "2026-08-27T17:59:00Z"
        errors = progression._validate_cross_stage_progression(client, item, snap)
        self.assertTrue(any("next Codex review predates prior exact response commit" in error for error in errors))
        self.assertTrue(any("next finding comment predates prior exact response commit" in error for error in errors))

    def test_owner_reply_must_not_predate_its_named_response_commit(self):
        item = entry()
        client = FakeClient(item)
        snap = snapshot(item)
        client.reply_time_override[3874859175] = "2026-08-27T18:30:00Z"

        errors = progression._validate_cross_stage_progression(client, item, snap)
        self.assertTrue(any("F059: owner reply predates the exact response commit" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
