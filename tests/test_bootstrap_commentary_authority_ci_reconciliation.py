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
                "user": {"login": verifier.CODEX_LOGIN},
            },
            {
                "id": 3874358316,
                "pull_request_review_id": 5043917353,
                "commit_id": verifier.REVIEWED_HEAD,
                "original_commit_id": verifier.REVIEWED_HEAD,
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
            return self._reply(3874609972, 3874358302, [verifier.CODE_DOCS_HEAD, verifier.METADATA_HEAD, "33101350599", "33102045907"])
        if path == f"{prefix}/pulls/comments/3874610894":
            return self._reply(3874610894, 3874358316, [verifier.CODE_DOCS_HEAD, verifier.METADATA_HEAD, "33101350599", "33102045907"])
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

    def _reply(self, reply_id, expected_target, tokens):
        return {
            "id": reply_id,
            "in_reply_to_id": self.reply_target_override.get(reply_id, expected_target),
            "original_commit_id": verifier.REVIEWED_HEAD,
            "pull_request_url": "https://api.github.test/repos/BogdanAIP/uv-studio/pulls/71",
            "user": {"login": "BogdanAIP"},
            "body": " ".join(tokens),
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
    def run_verify(self, source=None, public=None):
        doc = document()
        source = source or SourceClient(doc)
        public = public or PublicClient()
        with patch.object(verifier.base, "build_snapshot", return_value=snapshot()):
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

    def test_owner_reply_must_target_exact_finding(self):
        source = SourceClient(document())
        source.reply_target_override[3874609972] = 3874358316
        result = self.run_verify(source=source)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("F055: owner reply targets another finding" in error for error in result["errors"]))

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
