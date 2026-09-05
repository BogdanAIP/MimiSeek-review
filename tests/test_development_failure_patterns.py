from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools import validate_development_failure_patterns as guard


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/development-failure-patterns.jsonl"


def load_seed() -> dict:
    lines = [line for line in REGISTRY.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 1
    return json.loads(lines[0])


class DevelopmentFailurePatternTests(unittest.TestCase):
    def test_repository_registry_is_valid_and_seed_is_exact(self) -> None:
        guard.validate_schema_identity(ROOT)
        patterns = guard.load_registry(REGISTRY, ROOT)
        self.assertEqual([item["pattern_id"] for item in patterns], ["DFP-0001"])
        seed = patterns[0]
        self.assertEqual(seed["failure_class"], "evidence.semantic_binding_missing")
        self.assertEqual(seed["origin"]["pr"], 20)
        self.assertEqual(
            seed["origin"]["head_sha"],
            "a6a79485db9caac3cf68a6a9049a0a6ef9cd1c26",
        )
        self.assertEqual(seed["origin"]["evidence_locator"], "review_comment:3940860016")
        self.assertEqual(seed["prevention"]["kind"], "EXECUTABLE")
        self.assertIn(
            "tools/verify_bootstrap_commentary_authority_ci_reconciliation.py",
            seed["prevention"]["guard_refs"],
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
            "does not resolve to a repository file",
        ):
            guard.validate_pattern(pattern, ROOT, "pattern")

    def test_manual_only_requires_explicit_reason_and_no_guard_claim(self) -> None:
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

    def test_completed_repository_search_cannot_hide_follow_up(self) -> None:
        pattern = load_seed()
        pattern["repository_search"]["follow_up_refs"] = ["https://github.com/BogdanAIP/MimiSeek-review/issues/1"]
        with self.assertRaisesRegex(
            guard.DevelopmentFailurePatternError,
            "COMPLETED search must not retain follow_up_refs",
        ):
            guard.validate_pattern(pattern, ROOT, "pattern")

    def test_bounded_repository_search_requires_follow_up(self) -> None:
        pattern = load_seed()
        pattern["repository_search"]["status"] = "BOUNDED_FOLLOW_UP"
        with self.assertRaisesRegex(
            guard.DevelopmentFailurePatternError,
            "BOUNDED_FOLLOW_UP requires at least one follow_up_ref",
        ):
            guard.validate_pattern(pattern, ROOT, "pattern")

    def test_repository_search_scope_must_match_real_files(self) -> None:
        pattern = load_seed()
        pattern["repository_search"]["searched_scope"] = ["no/such/family/*.py"]
        with self.assertRaisesRegex(
            guard.DevelopmentFailurePatternError,
            "matches no repository files",
        ):
            guard.validate_pattern(pattern, ROOT, "pattern")

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
        second["pattern_id"] = "DFP-0002"
        second["origin"]["head_sha"] = "2" * 40
        second["occurrences"][0]["occurrence_id"] = "DFP-0002-O001"
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

    def test_active_summary_exposes_prevention_without_private_reasoning(self) -> None:
        summary = guard.active_summary(load_seed())
        self.assertEqual(summary["pattern_id"], "DFP-0001")
        self.assertIn("trigger_conditions", summary)
        self.assertIn("applicable_scope", summary)
        self.assertIn("guard_refs", summary)
        self.assertNotIn("root_cause", summary)
        self.assertNotIn("occurrences", summary)


if __name__ == "__main__":
    unittest.main()
