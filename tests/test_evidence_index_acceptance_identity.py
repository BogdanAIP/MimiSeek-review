from __future__ import annotations

import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "docs" / "EVIDENCE_INDEX.md").read_text(encoding="utf-8")
ACCEPTED_HEAD = re.compile(r"^- accepted exact PR HEAD: `([0-9a-f]{40})`$", re.MULTILINE)
EXPECTED_HEAD = re.compile(r"`expected_head_sha=([0-9a-f]{40})`")


def expected_head_mismatches(text: str) -> list[tuple[str, str]]:
    mismatches: list[tuple[str, str]] = []
    accepted = list(ACCEPTED_HEAD.finditer(text))
    for expected in EXPECTED_HEAD.finditer(text):
        prior = [m for m in accepted if m.start() < expected.start()]
        if not prior:
            mismatches.append(("<missing accepted head>", expected.group(1)))
            continue
        accepted_sha = prior[-1].group(1)
        if expected.group(1) != accepted_sha:
            mismatches.append((accepted_sha, expected.group(1)))
    return mismatches


class EvidenceIndexAcceptanceIdentityTests(unittest.TestCase):
    def test_expected_head_sha_matches_nearest_accepted_exact_pr_head(self) -> None:
        self.assertEqual(expected_head_mismatches(INDEX), [])

    def test_merge_commit_substitution_is_rejected(self) -> None:
        good = "`expected_head_sha=90b533fd1f2de743dfe388fc1e9747658039f1e1`"
        bad = "`expected_head_sha=c673c11bd0490b3b8218a11173e30c90d5b783a0`"
        self.assertIn(good, INDEX)
        mutated = INDEX.replace(good, bad, 1)
        self.assertIn(
            (
                "90b533fd1f2de743dfe388fc1e9747658039f1e1",
                "c673c11bd0490b3b8218a11173e30c90d5b783a0",
            ),
            expected_head_mismatches(mutated),
        )


if __name__ == "__main__":
    unittest.main()
