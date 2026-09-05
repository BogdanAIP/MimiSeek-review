from __future__ import annotations

import copy
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools import validate_development_failure_patterns as guard


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/development-failure-patterns.jsonl"


def load_patterns() -> list[dict]:
    return [
        json.loads(line)
        for line in REGISTRY.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_seed() -> dict:
    for item in load_patterns():
        if item["pattern_id"] == "DFP-0001":
            return item
    raise AssertionError("DFP-0001 seed is missing")


def git(*args: str, cwd: Path) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def commit_fixture(root: Path, message: str) -> None:
    git(
        "-c",
        "user.name=MimiSeek Test",
        "-c",
        "user.email=mimiseek-test@example.invalid",
        "commit",
        "-q",
        "-m",
        message,
        cwd=root,
    )


def make_git_fixture(root: Path) -> None:
    git("init", "-q", cwd=root)
    for name in ("tracked.py", "guard.py", "regression.py"):
        (root / name).write_text(f"# {name}\n", encoding="utf-8")
    git("add", "tracked.py", "guard.py", "regression.py", cwd=root)
    commit_fixture(root, "fixture")


def fixture_pattern() -> dict:
    pattern = copy.deepcopy(load_seed())
    pattern["repository_search"] = {
        "status": "COMPLETED",
        "searched_scope": ["*.py"],
        "discovered_instances": ["tracked.py"],
        "follow_up_refs": [],
        "notes": "Temporary Git fixture for path-authority regression tests.",
    }
    pattern["prevention"] = {
        "kind": "EXECUTABLE",
        "guard_refs": ["guard.py"],
        "regression_refs": ["regression.py"],
        "manual_only_reason": None,
    }
    return pattern


class DevelopmentFailurePatternTests(unittest.TestCase):
    def test_repository_registry_is_valid_and_seed_is_exact(self) -> None:
        guard.validate_schema_identity(ROOT)
        patterns = guard.load_registry(REGISTRY, ROOT)
        self.assertEqual(
            [item["pattern_id"] for item in patterns],
            ["DFP-0001", "DFP-0002", "DFP-0003", "DFP-0004"],
        )
        seed = patterns[0]
        self.assertEqual(seed["failure_class"], "evidence.semantic_binding_missing")
        self.assertEqual(seed["origin"]["pr"], 20)
        self.assertEqual(
            seed["origin"]["head_sha"],
            "a6a79485db9caac3cf68a6a9049a0a6ef9cd1c26",
        )
        self.assertEqual(seed["origin"]["evidence_locator"], "review_comment:3940860016")
        self.assertEqual(seed["repository_search"]["status"], "BOUNDED_FOLLOW_UP")
        self.assertEqual(
            seed["repository_search"]["follow_up_refs"],
            ["https://github.com/BogdanAIP/MimiSeek-review/issues/22"],
        )
        self.assertEqual(
            seed["repository_search"]["discovered_instances"],
            [
                "tools/verify_bootstrap_commentary_authority_ci_reconciliation.py",
                "tools/verify_bootstrap_commentary_fix_baseline_reconciliation.py",
                "tools/verify_bootstrap_commentary_fix_evidence_reconciliation.py",
            ],
        )
        self.assertEqual(seed["prevention"]["kind"], "EXECUTABLE")

        self.assertEqual(patterns[1]["failure_class"], "repository.reference_not_git_bound")
        self.assertEqual(patterns[1]["origin"]["evidence_locator"], "review_comment:3941887912")
        self.assertEqual(patterns[2]["failure_class"], "governance.duplicate_canonical_owner")
        self.assertEqual(patterns[2]["origin"]["evidence_locator"], "review_comment:3941887906")

        incident = patterns[3]
        self.assertEqual(incident["failure_class"], "workflow.noop_head_mutation")
        self.assertEqual(incident["origin"]["source_kind"], "PROCESS_INCIDENT")
        self.assertEqual(incident["origin"]["evidence_locator"], "pr_comment:5554652018")
        self.assertEqual(incident["prevention"]["kind"], "MANUAL_ONLY")
        self.assertEqual(len(incident["occurrences"]), 2)
        self.assertEqual(incident["occurrences"][1]["relation"], "REPEAT")
        self.assertEqual(
            incident["occurrences"][1]["prevention_failure_reason"],
            "NO_GUARD",
        )

    def test_executable_pattern_requires_guard_and_regression_refs(self) -> None:
        pattern = load_seed()
        pattern["prevention"]["guard_refs"] = []
        with self.assertRaisesRegex(
            guard.DevelopmentFailurePatternError,
            "requires guard_refs and regression_refs",
        ):
            guard.validate_pattern(pattern, ROOT, "pattern")

    def test_executable_pattern_rejects_missing_guard_file(self) -> None:
        pattern = load_seed()
        pattern["prevention"]["guard_refs"] = ["tools/does-not-exist.py"]
        with self.assertRaisesRegex(
            guard.DevelopmentFailurePatternError,
            "not a tracked regular file in exact HEAD",
        ):
            guard.validate_pattern(pattern, ROOT, "pattern")

    def test_manual_only_requires_explicit_reason_and_no_executable_refs(self) -> None:
        pattern = load_seed()
        pattern["prevention"] = {
            "kind": "MANUAL_ONLY",
            "guard_refs": [],
            "regression_refs": [],
            "manual_only_reason": "Cannot be automated without unavailable external authority.",
        }
        guard.validate_pattern(pattern, ROOT, "pattern")

        pattern["prevention"]["manual_only_reason"] = ""
        with self.assertRaisesRegex(
            guard.DevelopmentFailurePatternError,
            "manual_only_reason must be a non-empty string",
        ):
            guard.validate_pattern(pattern, ROOT, "pattern")

        pattern["prevention"] = {
            "kind": "MANUAL_ONLY",
            "guard_refs": [],
            "regression_refs": ["tests/test_development_failure_patterns.py"],
            "manual_only_reason": "Still claims an executable regression.",
        }
        with self.assertRaisesRegex(
            guard.DevelopmentFailurePatternError,
            "must not claim executable guard/regression refs",
        ):
            guard.validate_pattern(pattern, ROOT, "pattern")

    def test_completed_repository_search_cannot_hide_follow_up(self) -> None:
        pattern = load_seed()
        pattern["repository_search"]["status"] = "COMPLETED"
        with self.assertRaisesRegex(
            guard.DevelopmentFailurePatternError,
            "COMPLETED search must not retain follow_up_refs",
        ):
            guard.validate_pattern(pattern, ROOT, "pattern")

    def test_bounded_repository_search_requires_follow_up(self) -> None:
        pattern = load_seed()
        pattern["repository_search"]["follow_up_refs"] = []
        with self.assertRaisesRegex(
            guard.DevelopmentFailurePatternError,
            "BOUNDED_FOLLOW_UP requires at least one follow_up_ref",
        ):
            guard.validate_pattern(pattern, ROOT, "pattern")

    def test_repository_search_scope_must_match_tracked_regular_files(self) -> None:
        pattern = load_seed()
        pattern["repository_search"]["searched_scope"] = ["no/such/family/*.py"]
        with self.assertRaisesRegex(
            guard.DevelopmentFailurePatternError,
            "matches no tracked regular files in exact HEAD",
        ):
            guard.validate_pattern(pattern, ROOT, "pattern")

    def test_git_metadata_cannot_satisfy_prevention_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_git_fixture(root)
            pattern = fixture_pattern()
            pattern["prevention"]["guard_refs"] = [".git/config"]
            with self.assertRaisesRegex(
                guard.DevelopmentFailurePatternError,
                "must not reference .git metadata",
            ):
                guard.validate_pattern(pattern, root, "pattern")

    def test_untracked_file_cannot_satisfy_prevention_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_git_fixture(root)
            (root / "untracked.py").write_text("# untracked\n", encoding="utf-8")
            pattern = fixture_pattern()
            pattern["prevention"]["guard_refs"] = ["untracked.py"]
            with self.assertRaisesRegex(
                guard.DevelopmentFailurePatternError,
                "not a tracked regular file in exact HEAD",
            ):
                guard.validate_pattern(pattern, root, "pattern")

    def test_staged_but_uncommitted_file_cannot_satisfy_prevention_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_git_fixture(root)
            (root / "staged.py").write_text("# staged only\n", encoding="utf-8")
            git("add", "staged.py", cwd=root)
            pattern = fixture_pattern()
            pattern["prevention"]["guard_refs"] = ["staged.py"]
            with self.assertRaisesRegex(
                guard.DevelopmentFailurePatternError,
                "not a tracked regular file in exact HEAD",
            ):
                guard.validate_pattern(pattern, root, "pattern")

    def test_tracked_symlink_escape_cannot_satisfy_prevention_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root = Path(tmp)
            outside = Path(outside_tmp) / "outside.py"
            outside.write_text("# outside\n", encoding="utf-8")
            make_git_fixture(root)
            link = root / "escape.py"
            try:
                os.symlink(outside, link)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink unsupported: {exc}")
            git("add", "escape.py", cwd=root)
            commit_fixture(root, "tracked symlink")
            pattern = fixture_pattern()
            pattern["prevention"]["guard_refs"] = ["escape.py"]
            with self.assertRaisesRegex(
                guard.DevelopmentFailurePatternError,
                "not a tracked regular file in exact HEAD",
            ):
                guard.validate_pattern(pattern, root, "pattern")

    def test_checkout_only_paths_cannot_satisfy_repository_search_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root = Path(tmp)
            make_git_fixture(root)
            (root / "untracked.py").write_text("# untracked\n", encoding="utf-8")
            outside = Path(outside_tmp) / "outside.py"
            outside.write_text("# outside\n", encoding="utf-8")
            link = root / "escape.py"
            try:
                os.symlink(outside, link)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink unsupported: {exc}")
            git("add", "escape.py", cwd=root)
            commit_fixture(root, "tracked symlink")

            for scope, expected in (
                (".git/*", "must not reference .git metadata"),
                ("untracked*.py", "matches no tracked regular files in exact HEAD"),
                ("escape*.py", "matches no tracked regular files in exact HEAD"),
            ):
                with self.subTest(scope=scope):
                    pattern = fixture_pattern()
                    pattern["repository_search"]["searched_scope"] = [scope]
                    with self.assertRaisesRegex(
                        guard.DevelopmentFailurePatternError,
                        expected,
                    ):
                        guard.validate_pattern(pattern, root, "pattern")

    def test_repeat_requires_prevention_failure_reason(self) -> None:
        pattern = load_seed()
        pattern["occurrences"].append(
            {
                "occurrence_id": "DFP-0001-O002",
                "relation": "REPEAT",
                "pr": 99,
                "head_sha": "1" * 40,
                "evidence_locator": "review_comment:999",
                "prevention_failure_reason": None,
            }
        )
        with self.assertRaisesRegex(
            guard.DevelopmentFailurePatternError,
            "REPEAT requires a prevention_failure_reason",
        ):
            guard.validate_pattern(pattern, ROOT, "pattern")

        pattern["occurrences"][-1]["prevention_failure_reason"] = "GUARD_TOO_NARROW"
        guard.validate_pattern(pattern, ROOT, "pattern")

    def test_repeat_must_be_added_to_existing_failure_class_not_duplicate_pattern(self) -> None:
        seed = load_seed()
        second = copy.deepcopy(seed)
        second["pattern_id"] = "DFP-9999"
        second["origin"]["head_sha"] = "2" * 40
        second["occurrences"][0]["occurrence_id"] = "DFP-9999-O001"
        second["occurrences"][0]["head_sha"] = "2" * 40
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.jsonl"
            path.write_text(
                json.dumps(seed, separators=(",", ":"))
                + "\n"
                + json.dumps(second, separators=(",", ":"))
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                guard.DevelopmentFailurePatternError,
                "duplicate failure_class",
            ):
                guard.load_registry(path, ROOT)

    def test_origin_occurrence_must_exactly_match_pattern_origin(self) -> None:
        pattern = load_seed()
        pattern["occurrences"][0]["head_sha"] = "3" * 40
        with self.assertRaisesRegex(
            guard.DevelopmentFailurePatternError,
            "must exactly match the pattern origin",
        ):
            guard.validate_pattern(pattern, ROOT, "pattern")

    def test_registry_is_mimiseek_self_development_only(self) -> None:
        pattern = load_seed()
        pattern["origin"]["repository"] = "BogdanAIP/chat-agent-platform"
        with self.assertRaisesRegex(
            guard.DevelopmentFailurePatternError,
            "must remain scoped to BogdanAIP/MimiSeek-review",
        ):
            guard.validate_pattern(pattern, ROOT, "pattern")

    def test_active_summary_exposes_search_boundary_and_prevention(self) -> None:
        summary = guard.active_summary(load_seed())
        self.assertEqual(summary["pattern_id"], "DFP-0001")
        self.assertIn("trigger_conditions", summary)
        self.assertIn("applicable_scope", summary)
        self.assertEqual(summary["search_status"], "BOUNDED_FOLLOW_UP")
        self.assertEqual(
            summary["follow_up_refs"],
            ["https://github.com/BogdanAIP/MimiSeek-review/issues/22"],
        )
        self.assertIn("guard_refs", summary)
        self.assertNotIn("root_cause", summary)
        self.assertNotIn("occurrences", summary)

    def test_development_protocol_is_the_only_normative_repeat_prevention_owner(self) -> None:
        protocol = (ROOT / "docs/DEVELOPMENT_PROTOCOL.md").read_text(encoding="utf-8")
        reference = (ROOT / "docs/DEVELOPMENT_REPEAT_PREVENTION.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "Canonical owner for the MimiSeek cross-chat development process: this document.",
            protocol,
        )
        self.assertIn(
            "Status: explanatory reference only; non-authoritative.",
            reference,
        )
        for forbidden in (
            "## Required closure loop",
            "## Development-start retrieval",
            "## Review-time repeat check",
            "python tools/validate_development_failure_patterns.py --list-active",
        ):
            self.assertNotIn(forbidden, reference)


if __name__ == "__main__":
    unittest.main()
