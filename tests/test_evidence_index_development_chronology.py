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


def chronology_dfa_blocks(text: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if CHRONOLOGY_HEADING_RE.fullmatch(stripped):
            if current is not None:
                blocks.append(current)
            current = []
            continue
        if current is not None and stripped.startswith("#"):
            blocks.append(current)
            current = None
            continue
        if current is not None and NUMBERED_RE.match(stripped):
            current.extend(DFA_RE.findall(stripped))
    if current is not None:
        blocks.append(current)
    return blocks


def commit_available(sha: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def ensure_source_history(pr: int, *shas: str) -> None:
    if all(commit_available(sha) for sha in shas):
        return

    shallow = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    if shallow == "true":
        result = subprocess.run(
            ["git", "fetch", "--quiet", "--no-tags", "--unshallow", "origin", "main"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            raise AssertionError(
                "cannot unshallow canonical main for chronology ancestry: "
                + result.stderr.decode(errors="replace")
            )

    if not all(commit_available(sha) for sha in shas):
        result = subprocess.run(
            [
                "git",
                "fetch",
                "--quiet",
                "--no-tags",
                "origin",
                f"+refs/pull/{pr}/head:refs/remotes/origin/mimiseek-chronology-pr-{pr}",
            ],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            raise AssertionError(
                f"cannot fetch exact source PR #{pr} history for chronology ancestry: "
                + result.stderr.decode(errors="replace")
            )

    missing = [sha for sha in shas if not commit_available(sha)]
    if missing:
        raise AssertionError(f"source PR #{pr} chronology commits are unavailable after exact history fetch: {missing}")


def is_ancestor(pr: int, older: str, newer: str) -> bool:
    ensure_source_history(pr, older, newer)
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
        f"git ancestry check failed for PR #{pr} {older} -> {newer}: "
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
            if not is_ancestor(pr, previous_head, head):
                raise AssertionError(
                    f"chronology reverses source PR #{pr}: {previous_aid}@{previous_head} "
                    f"is not an ancestor of {aid}@{head}"
                )
        last_by_pr[pr] = (aid, head)


class EvidenceIndexDevelopmentChronologyTests(unittest.TestCase):
    def test_canonical_dfa_chronology_follows_source_git_order(self) -> None:
        records = ledger_by_id()
        blocks = chronology_dfa_blocks(git_text(INDEX))
        dfa_blocks = [ids for ids in blocks if ids]
        self.assertTrue(dfa_blocks, "expected at least one DFA reference in canonical chronology")
        for ids in dfa_blocks:
            assert_dfa_order(ids, records)

    def test_reverse_ancestor_order_is_rejected(self) -> None:
        records = ledger_by_id()
        self.assertTrue(
            is_ancestor(
                26,
                records["DFA-0014"]["head_sha"],
                records["DFA-0012"]["head_sha"],
            )
        )
        with self.assertRaisesRegex(AssertionError, "chronology reverses source PR #26"):
            assert_dfa_order(["DFA-0012", "DFA-0014"], records)


if __name__ == "__main__":
    unittest.main()
