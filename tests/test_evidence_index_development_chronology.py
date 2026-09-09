from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = "docs/EVIDENCE_INDEX.md"
LEDGER = "data/development-finding-adjudications.jsonl"
DFA_RE = re.compile(r"DFA-[0-9]{4}")
CHRONOLOGY_HEADING_RE = re.compile(r"^#{0,6}\s*Review/remediation chronology:?\s*$")
NUMBERED_RE = re.compile(r"^[0-9]+\.\s")


def git_text(path: str) -> str:
    return subprocess.run(
        ["git", "show", f"HEAD:{path}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout


def ledger_by_id() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for line in git_text(LEDGER).splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        aid = row["adjudication_id"]
        if aid in out:
            raise AssertionError(f"duplicate adjudication id: {aid}")
        out[aid] = row
    return out


def chronology_dfa_ids(text: str) -> list[str]:
    ids: list[str] = []
    in_chronology = False
    for line in text.splitlines():
        stripped = line.strip()
        if CHRONOLOGY_HEADING_RE.fullmatch(stripped):
            in_chronology = True
            continue
        if in_chronology and stripped.startswith("#"):
            in_chronology = False
        if in_chronology and NUMBERED_RE.match(stripped):
            ids.extend(DFA_RE.findall(stripped))
    return ids


def is_ancestor(older: str, newer: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", older, newer],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise AssertionError(
        f"git ancestry check failed for {older} -> {newer}: "
        + result.stderr.decode(errors="replace")
    )


def assert_dfa_order(ids: list[str], records: dict[str, dict]) -> None:
    last_by_pr: dict[int, tuple[str, str]] = {}
    for aid in ids:
        if aid not in records:
            raise AssertionError(f"EVIDENCE_INDEX chronology references unknown adjudication {aid}")
        row = records[aid]
        pr = row["pr"]
        head = row["head_sha"]
        previous = last_by_pr.get(pr)
        if previous is not None:
            previous_aid, previous_head = previous
            if not is_ancestor(previous_head, head):
                raise AssertionError(
                    f"chronology reverses source PR #{pr}: {previous_aid}@{previous_head} "
                    f"is not an ancestor of {aid}@{head}"
                )
        last_by_pr[pr] = (aid, head)


class EvidenceIndexDevelopmentChronologyTests(unittest.TestCase):
    def test_canonical_dfa_chronology_follows_source_git_order(self) -> None:
        records = ledger_by_id()
        ids = chronology_dfa_ids(git_text(INDEX))
        self.assertTrue(ids, "expected at least one DFA reference in canonical chronology")
        assert_dfa_order(ids, records)

    def test_reverse_ancestor_order_is_rejected(self) -> None:
        records = ledger_by_id()
        self.assertTrue(is_ancestor(records["DFA-0014"]["head_sha"], records["DFA-0012"]["head_sha"]))
        with self.assertRaisesRegex(AssertionError, "chronology reverses source PR #26"):
            assert_dfa_order(["DFA-0012", "DFA-0014"], records)


if __name__ == "__main__":
    unittest.main()
