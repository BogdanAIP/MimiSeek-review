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


def rows() -> list[dict]:
    return [json.loads(line) for line in REGISTRY.read_text(encoding="utf-8").splitlines() if line.strip()]


def seed() -> dict:
    return copy.deepcopy(rows()[0])


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def fixture_repo(root: Path) -> None:
    git(root, "init", "-q")
    for name in ("tracked.py", "guard.py", "regression.py"):
        (root / name).write_text(f"# {name}\n", encoding="utf-8")
    git(root, "add", ".")
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture"],
        cwd=root, check=True,
    )


def fixture_pattern() -> dict:
    p = seed()
    p["repository_search"] = {
        "status": "COMPLETED",
        "searched_scope": ["*.py"],
        "discovered_instances": ["tracked.py"],
        "follow_up_refs": [],
        "notes": "fixture",
    }
    p["prevention"] = {
        "kind": "EXECUTABLE",
        "guard_refs": ["guard.py"],
        "regression_refs": ["regression.py"],
        "manual_only_reason": None,
    }
    return p


class DevelopmentFailurePatternTests(unittest.TestCase):
    def test_registry_exact_seed_and_current_patterns(self) -> None:
        guard.validate_schema_identity(ROOT)
        patterns = guard.load_registry(REGISTRY, ROOT)
        self.assertEqual([p["pattern_id"] for p in patterns], [f"DFP-{i:04d}" for i in range(1, 7)])
        self.assertEqual(patterns[0]["repository_search"]["follow_up_refs"], ["https://github.com/BogdanAIP/MimiSeek-review/issues/22"])
        self.assertEqual(patterns[1]["origin"]["evidence_locator"], "review_comment:3941887912")
        self.assertEqual(patterns[2]["origin"]["evidence_locator"], "review_comment:3941887906")
        self.assertEqual(patterns[3]["failure_class"], "workflow.noop_head_mutation")
        self.assertEqual(patterns[3]["occurrences"][1]["prevention_failure_reason"], "NO_GUARD")
        self.assertEqual(patterns[4]["origin"]["evidence_locator"], "review_comment:3942020916")
        self.assertEqual(patterns[5]["origin"]["evidence_locator"], "review_comment:3942020917")

    def test_executable_and_manual_prevention_contracts(self) -> None:
        p = seed(); p["prevention"]["guard_refs"] = []
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "requires guard_refs"):
            guard.validate_pattern(p, ROOT, "p")
        p = seed(); p["prevention"] = {"kind":"MANUAL_ONLY","guard_refs":[],"regression_refs":[],"manual_only_reason":"external tool boundary"}
        guard.validate_pattern(p, ROOT, "p")
        p["prevention"]["regression_refs"] = ["tests/test_development_failure_patterns.py"]
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "must not claim executable"):
            guard.validate_pattern(p, ROOT, "p")

    def test_bounded_follow_up_requires_durable_supported_locator(self) -> None:
        for ref in ("done later", "https://github.com/other/repo/issues/22", "https://github.com/BogdanAIP/MimiSeek-review/issues/0", "https://github.com/BogdanAIP/MimiSeek-review/issues/22?x=1"):
            with self.subTest(ref=ref):
                p = seed(); p["repository_search"]["follow_up_refs"] = [ref]
                with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "exact MimiSeek issue URL or tracked regular file"):
                    guard.validate_pattern(p, ROOT, "p")

    def test_tracked_file_can_be_bounded_follow_up(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); fixture_repo(root); p = fixture_pattern()
            p["repository_search"]["status"] = "BOUNDED_FOLLOW_UP"
            p["repository_search"]["follow_up_refs"] = ["tracked.py"]
            guard.validate_pattern(p, root, "p")

    def test_completed_and_bounded_search_state_consistency(self) -> None:
        p = seed(); p["repository_search"]["status"] = "COMPLETED"
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "COMPLETED search must not retain follow_up_refs"):
            guard.validate_pattern(p, ROOT, "p")
        p = seed(); p["repository_search"]["follow_up_refs"] = []
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "requires at least one follow_up_ref"):
            guard.validate_pattern(p, ROOT, "p")

    def test_unknown_pending_repeat_stays_bounded_and_visible(self) -> None:
        p = seed()
        p["occurrences"].append({"occurrence_id":"DFP-0001-O002","relation":"REPEAT","pr":99,"head_sha":"4"*40,"evidence_locator":"review_comment:1001","prevention_failure_reason":"UNKNOWN_PENDING_ANALYSIS"})
        p["repository_search"] = {**p["repository_search"], "status":"COMPLETED", "follow_up_refs":[]}
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "UNKNOWN_PENDING_ANALYSIS requires BOUNDED_FOLLOW_UP"):
            guard.validate_pattern(p, ROOT, "p")
        p["repository_search"] = {**p["repository_search"], "status":"BOUNDED_FOLLOW_UP", "follow_up_refs":["https://github.com/BogdanAIP/MimiSeek-review/issues/22"]}
        guard.validate_pattern(p, ROOT, "p")
        self.assertEqual(guard.active_summary(p)["pending_repeat_analysis"], ["DFP-0001-O002"])
        p["occurrences"][-1]["prevention_failure_reason"] = "GUARD_TOO_NARROW"
        p["repository_search"] = {**p["repository_search"], "status":"COMPLETED", "follow_up_refs":[]}
        guard.validate_pattern(p, ROOT, "p")
        self.assertEqual(guard.active_summary(p)["pending_repeat_analysis"], [])

    def test_exact_head_git_authority_blocks_checkout_only_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root = Path(tmp); fixture_repo(root)
            (root / "untracked.py").write_text("# no\n", encoding="utf-8")
            git(root, "add", "untracked.py")
            p = fixture_pattern(); p["prevention"]["guard_refs"] = ["untracked.py"]
            with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "not a tracked regular file in exact HEAD"):
                guard.validate_pattern(p, root, "p")
            link = root / "escape.py"; outside = Path(outside_tmp) / "outside.py"; outside.write_text("x", encoding="utf-8")
            try:
                os.symlink(outside, link)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(str(exc))
            git(root, "reset", "-q"); git(root, "add", "escape.py")
            subprocess.run(["git","-c","user.name=Test","-c","user.email=test@example.invalid","commit","-qm","symlink"], cwd=root, check=True)
            p = fixture_pattern(); p["prevention"]["guard_refs"] = ["escape.py"]
            with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "not a tracked regular file in exact HEAD"):
                guard.validate_pattern(p, root, "p")

    def test_git_metadata_and_unmatched_search_scope_fail_closed(self) -> None:
        p = seed(); p["prevention"]["guard_refs"] = [".git/config"]
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "must not reference .git"):
            guard.validate_pattern(p, ROOT, "p")
        p = seed(); p["repository_search"]["searched_scope"] = ["no/such/*.py"]
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "matches no tracked regular files"):
            guard.validate_pattern(p, ROOT, "p")

    def test_repeat_requires_reason_and_duplicate_class_is_rejected(self) -> None:
        p = seed(); p["occurrences"].append({"occurrence_id":"DFP-0001-O002","relation":"REPEAT","pr":99,"head_sha":"1"*40,"evidence_locator":"review_comment:999","prevention_failure_reason":None})
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "requires a prevention_failure_reason"):
            guard.validate_pattern(p, ROOT, "p")
        p = seed(); q = copy.deepcopy(p); q["pattern_id"] = "DFP-9999"; q["origin"]["head_sha"] = "2"*40; q["occurrences"][0]["occurrence_id"]="DFP-9999-O001"; q["occurrences"][0]["head_sha"]="2"*40
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"registry.jsonl"; path.write_text(json.dumps(p)+"\n"+json.dumps(q)+"\n", encoding="utf-8")
            with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "duplicate failure_class"):
                guard.load_registry(path, ROOT)

    def test_origin_and_repository_scope_are_exact(self) -> None:
        p = seed(); p["occurrences"][0]["head_sha"] = "3"*40
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "must exactly match"):
            guard.validate_pattern(p, ROOT, "p")
        p = seed(); p["origin"]["repository"] = "BogdanAIP/chat-agent-platform"
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "must remain scoped"):
            guard.validate_pattern(p, ROOT, "p")

    def test_active_summary_is_bounded_not_answer_key(self) -> None:
        summary = guard.active_summary(seed())
        self.assertEqual(summary["search_status"], "BOUNDED_FOLLOW_UP")
        self.assertIn("pending_repeat_analysis", summary)
        self.assertNotIn("root_cause", summary)
        self.assertNotIn("occurrences", summary)

    def test_development_protocol_is_only_normative_owner(self) -> None:
        protocol = (ROOT/"docs/DEVELOPMENT_PROTOCOL.md").read_text(encoding="utf-8")
        reference = (ROOT/"docs/DEVELOPMENT_REPEAT_PREVENTION.md").read_text(encoding="utf-8")
        self.assertIn("Canonical owner for the MimiSeek cross-chat development process: this document.", protocol)
        self.assertIn("Status: explanatory reference only; non-authoritative.", reference)
        for forbidden in ("## Required closure loop", "## Development-start retrieval", "## Review-time repeat check", "python tools/validate_development_failure_patterns.py --list-active"):
            self.assertNotIn(forbidden, reference)


if __name__ == "__main__":
    unittest.main()
