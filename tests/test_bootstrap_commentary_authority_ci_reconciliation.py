import base64
import importlib.util
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = REPO_ROOT / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))
SPEC = importlib.util.spec_from_file_location(
    "authority_ci",
    TOOLS_ROOT / "verify_bootstrap_commentary_authority_ci_reconciliation.py",
)
verifier = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = verifier
SPEC.loader.exec_module(verifier)

DOC_PATH = REPO_ROOT / "data" / "bootstrap-commentary-authority-ci-reconciliation.json"
MANIFEST_PATH = REPO_ROOT / "data" / "bootstrap-source.json"
FINDINGS_PATH = REPO_ROOT / "data" / "findings.jsonl"

F055_CODEX_BODY = """**<sub><sub>![P1 Badge](https://img.shields.io/badge/P1-orange?style=flat)</sub></sub>  Synchronize the authoritative architecture with the review state**

This changes the lifecycle authority to say Stage 17 is under review, but `docs/architecture/CURRENT_ARCHITECTURE.md:47,205` and `docs/architecture/UV_STUDIO_V2_ARCHITECTURE_MAP.md:24,60,231-233` still describe functional subagents as the next handoff from an idle Stage-16 repository. Agents following the required authority order can therefore treat this active slice as unstarted and initialize duplicate work; update the current architecture and its index classification to describe Stage 17 as an active review implementation rather than merged functionality.

AGENTS.md reference: [AGENTS.md:L85-L87](https://github.com/BogdanAIP/uv-studio/blob/aafddd3b37476a65558d56755edd2ae440648b74/AGENTS.md#L85-L87)

Useful? React with 👍 / 👎."""

F056_CODEX_BODY = """**<sub><sub>![P1 Badge](https://img.shields.io/badge/P1-orange?style=flat)</sub></sub>  Update the exact-head verification record**

The reviewed tree differs materially from the claimed final head `dc973c9`—including the result-integrity and shared-executor provenance fixes—so CI #3469 on that older head does not establish the required checks for this review head. Recording the older SHA as the “final draft implementation head” leaves the review state claiming evidence that does not cover the code being approved; rerun the declared checks on the latest head and record that exact SHA/result.

AGENTS.md reference: [AGENTS.md:L126-L133](https://github.com/BogdanAIP/uv-studio/blob/aafddd3b37476a65558d56755edd2ae440648b74/AGENTS.md#L126-L133)

Useful? React with 👍 / 👎."""

F055_REPLY_BODY = "Fixed in the code/docs baseline ending at `9af22cdcbb60501dca968fd10f12dc1d40ee6482`. `docs/architecture/CURRENT_ARCHITECTURE.md` and `docs/architecture/UV_STUDIO_V2_ARCHITECTURE_MAP.md` now classify Stage 17 / PR #71 as **active review**, explicitly not the next/unstarted handoff, and identify background Agent execution as the post-merge D-066 layer 4. `PROJECT_STATE.md` is synchronized on metadata head `10643bd160c65b8d8df690266390725d5d0dd6eb`. The code-bearing head passed all five PR CI jobs in #3488 (`33101350599`), and the final metadata head passed all five again in #3490 (`33102045907`)."
F056_REPLY_BODY = "Fixed in metadata head `10643bd160c65b8d8df690266390725d5d0dd6eb`. `PROJECT_STATE.md` now records the exact code-bearing review baseline `9af22cdcbb60501dca968fd10f12dc1d40ee6482` and exact PR CI #3488 (`33101350599`), which passed all five permanent jobs including both browser suites. The metadata head itself then passed all five permanent jobs again in PR CI #3490 (`33102045907`), so the review-state record is no longer relying on obsolete `dc973c9` evidence."


def document():
    return verifier.load_document(DOC_PATH, MANIFEST_PATH)


def snapshot():
    return {
        "repository": verifier.REPOSITORY,
        "pr_number": verifier.PR_NUMBER,
        "pull_request": {
            "number": verifier.PR_NUMBER,
            "state": "closed",
            "merged_at": "2026-08-27T19:37:20Z",
            "head": {"sha": "9120fd768255775d938da5e827043db9691a8886"},
            "user": {"login": "BogdanAIP"},
        },
        "reviews": [
            {
                "id": 5043917353,
                "commit_id": verifier.REVIEWED_HEAD,
                "user": {"login": verifier.CODEX_LOGIN},
            }
        ],
        "review_comments": [
            {
                "id": 3874358302,
                "pull_request_review_id": 5043917353,
                "commit_id": verifier.REVIEWED_HEAD,
                "original_commit_id": verifier.REVIEWED_HEAD,
                "updated_at": "2026-08-27T17:50:12Z",
                "body": F055_CODEX_BODY,
                "user": {"login": verifier.CODEX_LOGIN},
            },
            {
                "id": 3874358316,
                "pull_request_review_id": 5043917353,
                "commit_id": verifier.REVIEWED_HEAD,
                "original_commit_id": verifier.REVIEWED_HEAD,
                "updated_at": "2026-08-27T17:50:12Z",
                "body": F056_CODEX_BODY,
                "user": {"login": verifier.CODEX_LOGIN},
            },
        ],
        "commits": [
            {"sha": verifier.REVIEWED_HEAD},
            *[{"sha": sha} for sha in verifier.EXPECTED_BASELINE_COMMITS],
            {"sha": verifier.METADATA_HEAD},
        ],
    }


class SourceClient:
    api_url = "https://api.github.test"

    def __init__(self, doc):
        self.doc = doc
        self.reply_target_override = {}
        self.reply_body_override = {}
        self.reply_updated_at_override = {}
        self.content_override = {}
        self.compare_status_override = {}
        self.contents = {}
        for entry in doc["entries"]:
            if entry["finding_id"] == "F055":
                for assertion in entry["authority_sync_evidence"]["code_docs_content_assertions"]:
                    self.contents[(verifier.CODE_DOCS_HEAD, assertion["path"])] = "\n".join(assertion["required_present"])
                for assertion in entry["authority_sync_evidence"]["metadata_content_assertions"]:
                    self.contents[(verifier.METADATA_HEAD, assertion["path"])] = "\n".join(assertion["required_present"])
            else:
                for assertion in entry["exact_head_ci_evidence"]["metadata_content_assertions"]:
                    existing = self.contents.get((verifier.METADATA_HEAD, assertion["path"]), "")
                    self.contents[(verifier.METADATA_HEAD, assertion["path"])] = existing + "\n" + "\n".join(assertion["required_present"])

    def get(self, path, params=None):
        prefix = "/repos/BogdanAIP/uv-studio"
        if path == f"{prefix}/pulls/comments/3874609972":
            return self._reply(
                3874609972,
                3874358302,
                F055_REPLY_BODY,
                "2026-08-27T18:15:36Z",
            )
        if path == f"{prefix}/pulls/comments/3874610894":
            return self._reply(
                3874610894,
                3874358316,
                F056_REPLY_BODY,
                "2026-08-27T18:15:43Z",
            )
        if path == f"{prefix}/compare/{verifier.REVIEWED_HEAD}...{verifier.CODE_DOCS_HEAD}":
            return {
                "status": self.compare_status_override.get("baseline", "ahead"),
                "behind_by": 0,
                "base_commit": {"sha": verifier.REVIEWED_HEAD},
                "merge_base_commit": {"sha": verifier.REVIEWED_HEAD},
                "commits": [{"sha": sha} for sha in verifier.EXPECTED_BASELINE_COMMITS],
                "files": [{"filename": name} for name in verifier.EXPECTED_BASELINE_FILES],
            }
        if path == f"{prefix}/compare/{verifier.CODE_DOCS_HEAD}...{verifier.METADATA_HEAD}":
            return {
                "status": self.compare_status_override.get("metadata", "ahead"),
                "behind_by": 0,
                "base_commit": {"sha": verifier.CODE_DOCS_HEAD},
                "merge_base_commit": {"sha": verifier.CODE_DOCS_HEAD},
                "commits": [{"sha": verifier.METADATA_HEAD}],
                "files": [{"filename": "project-context/PROJECT_STATE.md"}],
            }
        if path.startswith(f"{prefix}/contents/"):
            file_path = path.split("/contents/", 1)[1]
            ref = (params or {}).get("ref")
            text = self.content_override.get((ref, file_path), self.contents[(ref, file_path)])
            return {
                "type": "file",
                "encoding": "base64",
                "content": base64.b64encode(text.encode()).decode(),
            }
        raise AssertionError(f"unexpected source GET {path} params={params}")

    def _reply(self, reply_id, expected_target, expected_body, expected_updated_at):
        return {
            "id": reply_id,
            "in_reply_to_id": self.reply_target_override.get(reply_id, expected_target),
            "original_commit_id": verifier.REVIEWED_HEAD,
            "pull_request_url": "https://api.github.test/repos/BogdanAIP/uv-studio/pulls/71",
            "user": {"login": "BogdanAIP"},
            "updated_at": self.reply_updated_at_override.get(reply_id, expected_updated_at),
            "body": self.reply_body_override.get(reply_id, expected_body),
        }


class PublicClient:
    api_url = "https://api.github.test"

    def __init__(self):
        self.run_head_override = {}
        self.job_conclusion_override = {}
        self.drop_job = {}
        self.calls = []

    def get(self, path, params=None):
        self.calls.append((path, deepcopy(params)))
        for run_id, run_number, head in (
            (33101350599, 3488, verifier.CODE_DOCS_HEAD),
            (33102045907, 3490, verifier.METADATA_HEAD),
        ):
            if path == f"/repos/BogdanAIP/uv-studio/actions/runs/{run_id}":
                return {
                    "id": run_id,
                    "workflow_id": verifier.WORKFLOW_ID,
                    "run_number": run_number,
                    "event": "pull_request",
                    "head_sha": self.run_head_override.get(run_id, head),
                    "head_branch": "stage-17/agent-functional-subagents",
                    "status": "completed",
                    "conclusion": "success",
                    "repository": {"full_name": verifier.REPOSITORY},
                }
            if path == f"/repos/BogdanAIP/uv-studio/actions/runs/{run_id}/jobs":
                names = [name for name in verifier.EXPECTED_JOBS if name != self.drop_job.get(run_id)]
                jobs = [
                    {
                        "name": name,
                        "run_id": run_id,
                        "status": "completed",
                        "conclusion": self.job_conclusion_override.get((run_id, name), "success"),
                    }
                    for name in names
                ]
                return {"total_count": len(jobs), "jobs": jobs}
        raise AssertionError(f"unexpected public GET {path} params={params}")


class AuthorityCiTests(unittest.TestCase):
    def run_verify(self, source=None, public=None, snapshot_value=None):
        doc = document()
        source = source or SourceClient(doc)
        public = public or PublicClient()
        with patch.object(verifier.base, "build_snapshot", return_value=snapshot_value or snapshot()):
            return verifier.verify(FINDINGS_PATH, DOC_PATH, MANIFEST_PATH, source, public)

    def test_full_bounded_fixture_passes(self):
        result = self.run_verify()
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertEqual([x["finding_id"] for x in result["entries"]], ["F055", "F056"])

    def test_source_note_is_exact_and_fails_closed(self):
        raw = json.loads(DOC_PATH.read_text(encoding="utf-8"))
        raw["entries"][0]["source_note"] += " changed"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.json"
            path.write_text(json.dumps(raw), encoding="utf-8")
            with self.assertRaisesRegex(Exception, "source disposition/note differs"):
                verifier.load_document(path, MANIFEST_PATH)

    def test_edited_codex_finding_body_fails_with_correct_ids(self):
        snap = snapshot()
        snap["review_comments"][0]["body"] = F055_CODEX_BODY + "\nEdited semantic claim."
        result = self.run_verify(snapshot_value=snap)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("F055: finding body digest differs" in error for error in result["errors"]), result["errors"])

    def test_codex_finding_updated_at_is_part_of_identity(self):
        snap = snapshot()
        snap["review_comments"][1]["updated_at"] = "2026-08-27T17:51:12Z"
        result = self.run_verify(snapshot_value=snap)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("F056: finding updated_at differs" in error for error in result["errors"]), result["errors"])

    def test_owner_reply_must_target_exact_finding(self):
        source = SourceClient(document())
        source.reply_target_override[3874609972] = 3874358316
        result = self.run_verify(source=source)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("F055: owner reply targets another finding" in error for error in result["errors"]))

    def test_negating_owner_reply_with_all_evidence_ids_fails(self):
        source = SourceClient(document())
        source.reply_body_override[3874609972] = (
            "Not fixed; do not accept this reconciliation. "
            f"{verifier.CODE_DOCS_HEAD} {verifier.METADATA_HEAD} 33101350599 33102045907"
        )
        result = self.run_verify(source=source)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("F055: owner reply body digest differs" in error for error in result["errors"]), result["errors"])

    def test_semantically_swapped_owner_reply_fails(self):
        source = SourceClient(document())
        source.reply_body_override[3874609972] = F056_REPLY_BODY
        result = self.run_verify(source=source)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("F055: owner reply body digest differs" in error for error in result["errors"]), result["errors"])

    def test_owner_reply_updated_at_is_part_of_identity(self):
        source = SourceClient(document())
        source.reply_updated_at_override[3874610894] = "2026-08-27T18:16:43Z"
        result = self.run_verify(source=source)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("F056: owner reply updated_at differs" in error for error in result["errors"]), result["errors"])

    def test_authority_sync_requires_new_active_review_content(self):
        source = SourceClient(document())
        source.content_override[(verifier.CODE_DOCS_HEAD, "docs/architecture/CURRENT_ARCHITECTURE.md")] = "functional Subagents [next D-066 layer 3]"
        result = self.run_verify(source=source)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("F055 code/docs" in error and "missing" in error for error in result["errors"]))

    def test_metadata_range_must_be_exact_descendant(self):
        source = SourceClient(document())
        source.compare_status_override["metadata"] = "diverged"
        result = self.run_verify(source=source)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("compare status/behind differs" in error for error in result["errors"]))

    def test_ci_run_must_be_bound_to_exact_head(self):
        public = PublicClient()
        public.run_head_override[33102045907] = "0" * 40
        result = self.run_verify(public=public)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("run 33102045907 head_sha differs" in error for error in result["errors"]))

    def test_ci_requires_exact_five_successful_jobs(self):
        public = PublicClient()
        public.drop_job[33101350599] = "development-context"
        result = self.run_verify(public=public)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("exact five-job set differs" in error for error in result["errors"]))

        public = PublicClient()
        public.job_conclusion_override[(33102045907, "app-baseline (windows-latest)")] = "failure"
        result = self.run_verify(public=public)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("is not exact completed success" in error for error in result["errors"]))

    def test_workflow_does_not_widen_source_app_permissions(self):
        workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("permission-contents: read", workflow)
        self.assertIn("permission-issues: read", workflow)
        self.assertIn("permission-pull-requests: read", workflow)
        self.assertNotIn("permission-actions:", workflow)
        self.assertNotIn("actions: write", workflow)


if __name__ == "__main__":
    unittest.main()
