import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = REPO_ROOT / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

SPEC = importlib.util.spec_from_file_location(
    "authority_ci_relocation",
    TOOLS_ROOT / "verify_bootstrap_commentary_authority_ci_reconciliation.py",
)
verifier = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = verifier
SPEC.loader.exec_module(verifier)

DOC_PATH = REPO_ROOT / "data" / "bootstrap-commentary-authority-ci-reconciliation.json"
MANIFEST_PATH = REPO_ROOT / "data" / "bootstrap-source.json"
FINDINGS_PATH = REPO_ROOT / "data" / "findings.jsonl"
FINAL_HEAD = "9120fd768255775d938da5e827043db9691a8886"
F056_CODEX_BODY = """**<sub><sub>![P1 Badge](https://img.shields.io/badge/P1-orange?style=flat)</sub></sub>  Update the exact-head verification record**

The reviewed tree differs materially from the claimed final head `dc973c9`—including the result-integrity and shared-executor provenance fixes—so CI #3469 on that older head does not establish the required checks for this review head. Recording the older SHA as the “final draft implementation head” leaves the review state claiming evidence that does not cover the code being approved; rerun the declared checks on the latest head and record that exact SHA/result.

AGENTS.md reference: [AGENTS.md:L126-L133](https://github.com/BogdanAIP/uv-studio/blob/aafddd3b37476a65558d56755edd2ae440648b74/AGENTS.md#L126-L133)

Useful? React with 👍 / 👎."""


def f056_entry():
    doc = verifier.load_document(DOC_PATH, MANIFEST_PATH)
    return next(entry for entry in doc["entries"] if entry["finding_id"] == "F056")


def f056_finding():
    findings = verifier.base.load_tuple_jsonl(FINDINGS_PATH, verifier.base.FINDING_COLUMNS)
    return verifier.base.index_unique(findings, "finding_id", "finding_id")["F056"]


def source_snapshot(current_commit):
    return {
        "repository": verifier.REPOSITORY,
        "pr_number": verifier.PR_NUMBER,
        "pull_request": {
            "number": verifier.PR_NUMBER,
            "state": "closed",
            "merged_at": "2026-08-27T19:37:20Z",
            "head": {"sha": FINAL_HEAD},
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
                "id": 3874358316,
                "pull_request_review_id": 5043917353,
                "commit_id": current_commit,
                "original_commit_id": verifier.REVIEWED_HEAD,
                "updated_at": "2026-08-27T17:50:12Z",
                "body": F056_CODEX_BODY,
                "user": {"login": verifier.CODEX_LOGIN},
            }
        ],
        "commits": [
            {"sha": verifier.REVIEWED_HEAD},
            *[{"sha": sha} for sha in verifier.EXPECTED_BASELINE_COMMITS],
            {"sha": verifier.METADATA_HEAD},
            {"sha": FINAL_HEAD},
        ],
    }


class HistoricalRelocationBoundaryTests(unittest.TestCase):
    def test_current_commit_relocation_to_source_pr_member_is_not_historical_identity(self):
        errors = verifier._validate_historical_binding(
            f056_entry(),
            f056_finding(),
            source_snapshot(verifier.CODE_DOCS_HEAD),
        )
        self.assertEqual(errors, [])

    def test_current_commit_relocation_outside_source_pr_fails_closed(self):
        arbitrary = "0" * 40
        snap = source_snapshot(verifier.CODE_DOCS_HEAD)
        snap["review_comments"][0]["commit_id"] = arbitrary
        errors = verifier._validate_historical_binding(
            f056_entry(),
            f056_finding(),
            snap,
        )
        self.assertTrue(
            any("finding relocated commit is not a member of the exact source PR" in error for error in errors),
            errors,
        )

    def test_original_commit_id_still_owns_reviewed_head_binding(self):
        snap = source_snapshot(verifier.CODE_DOCS_HEAD)
        snap["review_comments"][0]["original_commit_id"] = verifier.CODE_DOCS_HEAD
        errors = verifier._validate_historical_binding(
            f056_entry(),
            f056_finding(),
            snap,
        )
        self.assertTrue(any("finding original_commit_id differs" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
