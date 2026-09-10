from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools" / "verify_development_finding_authority.py"
C = ROOT / "tests" / "test_evidence_index_development_chronology.py"
INDEX = "docs/EVIDENCE_INDEX.md"
FENCE_AUTHORITY_RE = re.compile(r"`{3,}|~{3,}")
spec = importlib.util.spec_from_file_location("authority_supplements", P)
a = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(a)
cspec = importlib.util.spec_from_file_location("evidence_index_chronology", C)
c = importlib.util.module_from_spec(cspec)
assert cspec.loader is not None
cspec.loader.exec_module(c)


def exact_head_text(path: str) -> str:
    return subprocess.run(
        ["git", "show", f"HEAD:{path}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout


def assert_no_raw_html_authority(text: str) -> None:
    if "<" in text:
        raise AssertionError(
            "literal raw-HTML opener syntax is forbidden on canonical EVIDENCE_INDEX authority surface; "
            "use escaped text such as &lt;...&gt; instead"
        )


def assert_no_fenced_authority(text: str) -> None:
    if FENCE_AUTHORITY_RE.search(text) is not None:
        raise AssertionError(
            "fenced blocks are forbidden on canonical EVIDENCE_INDEX authority surface; "
            "move examples to a non-authoritative document"
        )


def assert_canonical_authority_profile(text: str) -> None:
    assert_no_raw_html_authority(text)
    assert_no_fenced_authority(text)


class FindingSupplementTests(unittest.TestCase):
    def test_finding_records_reads_every_configured_supplement(self) -> None:
        original_specs = a.SUPPLEMENTS
        original_finding = a.finding_manifest
        original_supplement = a.supplement_manifest
        try:
            a.SUPPLEMENTS = (("one",), ("two",))
            a.finding_manifest = lambda get: [{"adjudication_id": "base"}]
            a.supplement_manifest = lambda get, spec: [{"adjudication_id": spec[0]}]
            rows = a.finding_records(lambda _: {})
            self.assertEqual(
                [row["adjudication_id"] for row in rows],
                ["base", "one", "two"],
            )
        finally:
            a.SUPPLEMENTS = original_specs
            a.finding_manifest = original_finding
            a.supplement_manifest = original_supplement

    def test_current_pr26_finding_supplement_is_configured(self) -> None:
        ids = [spec[0] for spec in a.SUPPLEMENTS]
        self.assertIn(5588130388, ids)

    def test_current_pr27_finding_supplement_is_configured(self) -> None:
        ids = [spec[0] for spec in a.SUPPLEMENTS]
        self.assertIn(5597570658, ids)
        self.assertIn(5619597338, ids)

    def test_process_issue_records_reads_every_configured_supplement(self) -> None:
        original_specs = a.PROCESS_SUPPLEMENTS
        original_supplement = a.process_issue_supplement_manifest
        try:
            a.PROCESS_SUPPLEMENTS = (("one",), ("two",))
            a.process_issue_supplement_manifest = lambda get, spec: [{"source": spec[0]}]
            rows = a.process_issue_records(lambda _: {})
            self.assertEqual([row["source"] for row in rows], ["one", "two"])
        finally:
            a.PROCESS_SUPPLEMENTS = original_specs
            a.process_issue_supplement_manifest = original_supplement


class EvidenceIndexAuthoritySurfaceTests(unittest.TestCase):
    def test_canonical_evidence_index_matches_strict_authority_profile(self) -> None:
        assert_canonical_authority_profile(exact_head_text(INDEX))

    def test_html_comment_with_fence_fails_closed_before_chronology_parsing(self) -> None:
        text = (
            "<!--\n"
            "```\n"
            "-->\n"
            "Review/remediation chronology:\n"
            "1. Later `DFA-0012`.\n"
            "2. Older `DFA-0014`.\n"
        )
        with self.assertRaisesRegex(AssertionError, "raw-HTML opener syntax is forbidden"):
            assert_canonical_authority_profile(text)

    def test_raw_html_block_fails_closed_before_chronology_parsing(self) -> None:
        text = (
            "<pre>\n"
            "Review/remediation chronology:\n"
            "1. Example `DFA-9999`.\n"
            "</pre>\n"
        )
        with self.assertRaisesRegex(AssertionError, "raw-HTML opener syntax is forbidden"):
            assert_canonical_authority_profile(text)

    def test_partial_multiline_raw_html_openers_fail_closed(self) -> None:
        for opener in ("<div\nclass=\"example\">", "<pre\nclass=\"example\">"):
            with self.subTest(opener=opener):
                text = (
                    f"{opener}\n"
                    "Review/remediation chronology:\n"
                    "1. Example `DFA-9999`.\n\n"
                    "PR #26 — example\n"
                    "- accepted exact PR HEAD: `ffffffffffffffffffffffffffffffffffffffff`\n"
                )
                with self.assertRaisesRegex(AssertionError, "raw-HTML opener syntax is forbidden"):
                    assert_canonical_authority_profile(text)

    def test_parent_nested_parent_fences_fail_closed(self) -> None:
        for fence in ("```", "~~~~"):
            with self.subTest(fence=fence):
                text = (
                    "Review/remediation chronology:\n"
                    "1. Real event `DFA-0014`.\n"
                    "   - nested note\n"
                    f"    {fence}text\n"
                    "    fake `DFA-9999` and HEAD: `ffffffffffffffffffffffffffffffffffffffff`\n"
                    f"    {fence}\n"
                    "2. Later real event `DFA-0012`.\n"
                )
                with self.assertRaisesRegex(AssertionError, "fenced blocks are forbidden"):
                    assert_canonical_authority_profile(text)

    def test_fence_after_list_marker_is_still_forbidden(self) -> None:
        for fence in ("```", "~~~"):
            with self.subTest(fence=fence):
                with self.assertRaisesRegex(AssertionError, "fenced blocks are forbidden"):
                    assert_canonical_authority_profile(f"1. {fence}text\nexample\n{fence}\n")

    def test_zero_to_three_space_atx_chronology_is_rendered_authority(self) -> None:
        for count in range(4):
            with self.subTest(spaces=count):
                prefix = " " * count
                blocks = c.chronology_blocks(
                    f"{prefix}#### PR #26 review/remediation chronology\n"
                    "1. Later `DFA-0012`.\n"
                    "2. Older `DFA-0014`.\n"
                )
                self.assertEqual(
                    blocks,
                    [[[("DFA", "DFA-0012")], [("DFA", "DFA-0014")]]],
                )

    def test_zero_to_three_space_accepted_head_authority_is_parsed(self) -> None:
        accepted = "8cb7d24ce18042227ebf6e9b4acbdcdb6b947922"
        for count in range(4):
            with self.subTest(spaces=count):
                prefix = " " * count
                text = (
                    f"{prefix}#### PR #26 — accepted evidence\n"
                    f"{prefix}- accepted exact PR HEAD: `{accepted}`\n"
                )
                self.assertEqual(c.accepted_pr_heads(text), {26: accepted})

    def test_escaped_html_text_remains_permitted(self) -> None:
        assert_canonical_authority_profile("Use &lt;pre&gt; or &lt;!-- --&gt; for literal examples.\n")


if __name__ == "__main__":
    unittest.main()
