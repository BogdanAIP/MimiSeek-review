from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools" / "verify_development_finding_authority.py"
INDEX = "docs/EVIDENCE_INDEX.md"
RAW_HTML_AUTHORITY_RE = re.compile(r"<!--|-->|<\s*[!?]|<\s*/?\s*[A-Za-z][^>\n]*>")
spec = importlib.util.spec_from_file_location("authority_supplements", P)
a = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(a)


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
    match = RAW_HTML_AUTHORITY_RE.search(text)
    if match is not None:
        raise AssertionError(
            "raw HTML/comment syntax is forbidden on canonical EVIDENCE_INDEX authority surface; "
            "use escaped text such as &lt;...&gt; instead"
        )


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
    def test_canonical_evidence_index_rejects_raw_html_authority_syntax(self) -> None:
        assert_no_raw_html_authority(exact_head_text(INDEX))

    def test_html_comment_with_fence_fails_closed_before_chronology_parsing(self) -> None:
        text = (
            "<!--\n"
            "```\n"
            "-->\n"
            "Review/remediation chronology:\n"
            "1. Later `DFA-0012`.\n"
            "2. Older `DFA-0014`.\n"
        )
        with self.assertRaisesRegex(AssertionError, "raw HTML/comment syntax is forbidden"):
            assert_no_raw_html_authority(text)

    def test_raw_html_block_fails_closed_before_chronology_parsing(self) -> None:
        text = (
            "<pre>\n"
            "Review/remediation chronology:\n"
            "1. Example `DFA-9999`.\n"
            "</pre>\n"
        )
        with self.assertRaisesRegex(AssertionError, "raw HTML/comment syntax is forbidden"):
            assert_no_raw_html_authority(text)

    def test_escaped_html_text_remains_permitted(self) -> None:
        assert_no_raw_html_authority("Use &lt;pre&gt; or &lt;!-- --&gt; for literal examples.\n")


if __name__ == "__main__":
    unittest.main()
