import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "bootstrap_provenance", REPO_ROOT / "tools" / "verify_bootstrap_commit_provenance.py"
)
provenance = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = provenance
SPEC.loader.exec_module(provenance)

BASE = "a" * 40
BUGGY = "b" * 40
FIX = "c" * 40
VERIFIED = "d" * 40
LIVE = "e" * 40
OLD_BASE = "f" * 40
REBASED_ANCHOR = "1" * 40


def case_record():
    return {
        "case_id": "RC-EXAMPLE-01",
        "finding_id": "F001",
        "repository": "BogdanAIP/example",
        "pr": 7,
        "severity": "P1",
        "category": "Recovery",
        "known_defect": "Durable state can be stranded",
        "buggy_base": BASE,
        "buggy_head": BUGGY,
        "fix_head": FIX,
        "verified_head": VERIFIED,
        "historical_source_reviewer": "Codex Review",
        "source_url": "https://github.com/BogdanAIP/example/pull/7",
    }


def finding_record():
    return {
        "finding_id": "F001",
        "repository": "BogdanAIP/example",
        "pr": 7,
        "head_sha": BUGGY,
        "reviewer": "Codex Review",
        "severity": "P1",
        "confirmed": "CONFIRMED",
        "category": "Recovery",
        "finding": "Durable state can be stranded",
        "source_url": "https://github.com/BogdanAIP/example/pull/7",
    }


def snapshot(commits=None):
    commits = commits or [
        {"sha": BUGGY, "parents": [BASE]},
        {"sha": FIX, "parents": [BUGGY]},
        {"sha": VERIFIED, "parents": [FIX]},
        {"sha": LIVE, "parents": [VERIFIED]},
    ]
    return {
        "authority": {"role": "non_authoritative_source_snapshot"},
        "repository": "BogdanAIP/example",
        "repository_id": 101,
        "repository_node_id": "R_example",
        "pr_number": 7,
        "pull_request": {
            "id": 7007,
            "node_id": "PR_7007",
            "number": 7,
            "user": {"id": 1, "login": "BogdanAIP", "type": "User"},
            "base": {
                "repo": "BogdanAIP/example",
                "repo_id": 101,
                "repo_node_id": "R_example",
            },
            "head": {"sha": LIVE},
        },
        "source": {"pull_request_url": "https://github.com/BogdanAIP/example/pull/7"},
        "issue_comments": [],
        "reviews": [],
        "review_comments": [],
        "commits": commits,
    }


def rebased_snapshot():
    result = snapshot(
        [
            {"sha": REBASED_ANCHOR, "parents": [BASE]},
            {"sha": FIX, "parents": [REBASED_ANCHOR]},
            {"sha": VERIFIED, "parents": [FIX]},
            {"sha": LIVE, "parents": [VERIFIED]},
        ]
    )
    result["issue_comments"] = [
        {
            "id": 10,
            "user": {"id": 1, "login": "BogdanAIP", "type": "User"},
            "body": f"@codex review exact head {BUGGY}",
        }
    ]
    result["reviews"] = [
        {
            "id": 20,
            "user": {"id": 2, "login": "chatgpt-codex-connector[bot]", "type": "Bot"},
            "commit_id": BUGGY,
        }
    ]
    result["review_comments"] = [
        {
            "id": 30,
            "pull_request_review_id": 20,
            "in_reply_to_id": None,
            "user": {"id": 2, "login": "chatgpt-codex-connector[bot]", "type": "Bot"},
            "commit_id": BUGGY,
            "original_commit_id": BUGGY,
            "body": "P1 concrete defect",
        },
        {
            "id": 31,
            "pull_request_review_id": 21,
            "in_reply_to_id": 30,
            "user": {"id": 1, "login": "BogdanAIP", "type": "User"},
            "commit_id": REBASED_ANCHOR,
            "original_commit_id": BUGGY,
            "body": "Fixed on the rebased head.",
        },
    ]
    return result


def rebase_reconciliation():
    return {
        "case_ids": ["RC-EXAMPLE-01"],
        "repository": "BogdanAIP/example",
        "pr": 7,
        "kind": provenance.REBASE_KIND,
        "source_buggy_base": BASE,
        "reviewed_buggy_head": BUGGY,
        "reviewed_buggy_parent": OLD_BASE,
        "rebased_fix_lineage_anchor": REBASED_ANCHOR,
        "fix_head": FIX,
        "verified_head": VERIFIED,
        "source_conflict": "Source base belongs to later rebased lineage.",
        "github_evidence": {
            "review_request_issue_comment_id": 10,
            "codex_review_id": 20,
            "codex_review_comment_ids": [30],
        },
    }


def case_row():
    return [
        "RC-EXAMPLE-01",
        "F001",
        "BogdanAIP/example",
        7,
        "P1",
        "Recovery",
        "Durable state can be stranded",
        BASE,
        BUGGY,
        FIX,
        VERIFIED,
        "Codex Review",
        "HIT",
        "Direct finding",
        "NOT RUN",
        0,
        0,
        "NOT RUN",
        "NOT RUN",
        "NOT RUN",
        "PENDING",
        "HIGH",
        "https://github.com/BogdanAIP/example/pull/7",
        "source note",
        2,
    ]


def finding_row():
    return [
        "F001",
        "BogdanAIP/example",
        7,
        BUGGY,
        "Codex Review",
        "P1",
        "CONFIRMED",
        False,
        "EXAMPLE-01",
        "Recovery",
        "Durable state can be stranded",
        False,
        None,
        "https://github.com/BogdanAIP/example/pull/7",
        "High",
        2,
    ]


class BootstrapCommitProvenanceTests(unittest.TestCase):
    def test_valid_linear_provenance_passes(self):
        self.assertEqual(provenance.validate_case(case_record(), finding_record(), snapshot()), [])

    def test_missing_fix_head_fails_closed(self):
        commits = [
            {"sha": BUGGY, "parents": [BASE]},
            {"sha": VERIFIED, "parents": [BUGGY]},
            {"sha": LIVE, "parents": [VERIFIED]},
        ]
        errors = provenance.validate_case(case_record(), finding_record(), snapshot(commits))
        self.assertTrue(any("fix_head" in error and "absent" in error for error in errors))

    def test_non_descendant_fix_head_fails_closed(self):
        commits = [
            {"sha": BUGGY, "parents": [BASE]},
            {"sha": FIX, "parents": [BASE]},
            {"sha": VERIFIED, "parents": [FIX]},
            {"sha": LIVE, "parents": [VERIFIED]},
        ]
        errors = provenance.validate_case(case_record(), finding_record(), snapshot(commits))
        self.assertTrue(any("not descended from BUGGY HEAD" in error for error in errors))

    def test_finding_identity_must_match_case(self):
        finding = finding_record()
        finding["head_sha"] = FIX
        finding["finding"] = "different defect"
        errors = provenance.validate_case(case_record(), finding, snapshot())
        self.assertTrue(any("finding HEAD is not BUGGY HEAD" in error for error in errors))
        self.assertTrue(any("finding text differs" in error for error in errors))

    def test_explicit_rebase_reconciliation_preserves_detached_reviewed_head(self):
        errors = provenance.validate_case(
            case_record(),
            finding_record(),
            rebased_snapshot(),
            rebase_reconciliation(),
            {"sha": BUGGY, "parents": (OLD_BASE,)},
        )
        self.assertEqual(errors, [])

    def test_rebase_reconciliation_requires_pr_bound_codex_comment(self):
        snap = rebased_snapshot()
        snap["review_comments"][0]["commit_id"] = FIX
        errors = provenance.validate_case(
            case_record(),
            finding_record(),
            snap,
            rebase_reconciliation(),
            {"sha": BUGGY, "parents": (OLD_BASE,)},
        )
        self.assertTrue(any("commit_id differs from BUGGY HEAD" in error for error in errors))

    def test_rebase_reconciliation_requires_exact_historical_parent(self):
        errors = provenance.validate_case(
            case_record(),
            finding_record(),
            rebased_snapshot(),
            rebase_reconciliation(),
            {"sha": BUGGY, "parents": (BASE,)},
        )
        self.assertTrue(any("reviewed BUGGY HEAD parent differs" in error for error in errors))

    def test_reconcile_fetches_one_snapshot_per_pr(self):
        calls = []

        def builder(client, repository, pr_number):
            calls.append((repository, pr_number))
            return snapshot()

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            cases_path = root / "cases.jsonl"
            findings_path = root / "findings.jsonl"
            cases_path.write_text(json.dumps(case_row()) + "\n", encoding="utf-8")
            findings_path.write_text(json.dumps(finding_row()) + "\n", encoding="utf-8")
            result = provenance.reconcile(cases_path, findings_path, object(), snapshot_builder=builder)

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["cases_checked"], 1)
        self.assertEqual(result["prs_checked"], 1)
        self.assertEqual(calls, [("BogdanAIP/example", 7)])
        self.assertEqual(result["provenance_modes"], {"linear_pr_history": 1})
        self.assertTrue(
            any("does not infer semantic fix correctness" in item for item in result["limitations"])
        )


if __name__ == "__main__":
    unittest.main()
