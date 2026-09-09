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
DFA_RANGE_RE = re.compile(r"`?DFA-([0-9]{4})`?\s*\.\.\s*`?DFA-([0-9]{4})`?")
HEAD_RE = re.compile(r"\bHEAD\s*:?\s*`([0-9a-f]{40})`", re.IGNORECASE)
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


def dfa_refs(text: str) -> list[str]:
    def expand(match: re.Match[str]) -> str:
        start = int(match.group(1))
        end = int(match.group(2))
        if end < start or end - start > 999:
            raise AssertionError(f"invalid compact DFA range: DFA-{start:04d}..DFA-{end:04d}")
        return " ".join(f"DFA-{value:04d}" for value in range(start, end + 1))

    return DFA_RE.findall(DFA_RANGE_RE.sub(expand, text))


def head_refs(text: str) -> list[str]:
    return HEAD_RE.findall(text)


def chronology_blocks(text: str) -> list[list[dict[str, list[str]]]]:
    blocks: list[list[dict[str, list[str]]]] = []
    current_block: list[dict[str, list[str]]] | None = None
    current_event: list[str] | None = None

    def flush_event() -> None:
        nonlocal current_event
        if current_block is not None and current_event is not None:
            event_text = "\n".join(current_event)
            current_block.append(
                {
                    "dfa": dfa_refs(event_text),
                    "heads": head_refs(event_text),
                }
            )
        current_event = None

    def flush_block() -> None:
        nonlocal current_block
        flush_event()
        if current_block is not None:
            blocks.append(current_block)
        current_block = None

    for line in text.splitlines():
        stripped = line.strip()
        if CHRONOLOGY_HEADING_RE.fullmatch(stripped):
            flush_block()
            current_block = []
            continue
        if current_block is not None and stripped.startswith("#"):
            flush_block()
            continue
        if current_block is None:
            continue
        if NUMBERED_RE.match(stripped):
            flush_event()
            current_event = [stripped]
        elif current_event is not None:
            current_event.append(stripped)

    flush_block()
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


def assert_chronology_order(events: list[dict[str, list[str]]], records: dict[str, dict]) -> None:
    source_prs: set[int] = set()
    for event in events:
        for aid in event["dfa"]:
            if aid not in records:
                raise AssertionError(f"EVIDENCE_INDEX chronology references unknown adjudication {aid}")
            source_prs.add(records[aid]["pr"])

    if not source_prs:
        return

    seen_dfa: set[str] = set()
    last_by_pr: dict[int, tuple[str, str]] = {}

    for event_number, event in enumerate(events, 1):
        event_prs = {records[aid]["pr"] for aid in event["dfa"] if aid in records}

        for pr in sorted(source_prs):
            heads: list[tuple[str, str]] = []

            if event["heads"]:
                if len(source_prs) == 1 or event_prs == {pr}:
                    for head in event["heads"]:
                        heads.append((f"event-{event_number}-HEAD", head))
                elif not event_prs:
                    raise AssertionError(
                        f"chronology block has ambiguous explicit HEAD event {event_number} "
                        f"across source PRs {sorted(source_prs)}"
                    )

            for aid in event["dfa"]:
                if aid in seen_dfa:
                    continue
                row = records[aid]
                if row["pr"] == pr:
                    head = row["head_sha"]
                    if all(existing_head != head for _, existing_head in heads):
                        heads.append((aid, head))

            for label, head in heads:
                previous = last_by_pr.get(pr)
                if previous is not None:
                    previous_label, previous_head = previous
                    if not is_ancestor(pr, previous_head, head):
                        raise AssertionError(
                            f"chronology reverses source PR #{pr}: "
                            f"{previous_label}@{previous_head} is not an ancestor of {label}@{head}"
                        )
                last_by_pr[pr] = (label, head)

        seen_dfa.update(event["dfa"])


class EvidenceIndexDevelopmentChronologyTests(unittest.TestCase):
    def test_canonical_chronology_follows_source_git_order(self) -> None:
        records = ledger_by_id()
        blocks = chronology_blocks(git_text(INDEX))
        governed_blocks = [events for events in blocks if any(event["dfa"] for event in events)]
        self.assertTrue(governed_blocks, "expected at least one DFA reference in canonical chronology")
        for events in governed_blocks:
            assert_chronology_order(events, records)

    def test_compact_range_expands_every_adjudication(self) -> None:
        self.assertEqual(
            dfa_refs("`DFA-0014`..`DFA-0016`"),
            ["DFA-0014", "DFA-0015", "DFA-0016"],
        )

    def test_continuation_lines_are_part_of_numbered_event(self) -> None:
        blocks = chronology_blocks(
            "Review/remediation chronology:\n"
            "\n"
            "1. Review completed.\n"
            "   - finding: `DFA-0014`\n"
            "2. Later event `DFA-0012`.\n"
            "\n"
            "# next\n"
        )
        self.assertEqual(blocks[0][0]["dfa"], ["DFA-0014"])
        self.assertEqual(blocks[0][1]["dfa"], ["DFA-0012"])

    def test_repeated_summary_refs_do_not_create_new_events(self) -> None:
        records = ledger_by_id()
        assert_chronology_order(
            [
                {"dfa": ["DFA-0014"], "heads": []},
                {"dfa": ["DFA-0012", "DFA-0013"], "heads": []},
                {
                    "dfa": ["DFA-0015", "DFA-0016", "DFA-0014", "DFA-0015", "DFA-0016"],
                    "heads": [],
                },
            ],
            records,
        )

    def test_head_only_descendant_then_older_finding_is_rejected(self) -> None:
        records = ledger_by_id()
        descendant = records["DFA-0012"]["head_sha"]
        with self.assertRaisesRegex(AssertionError, "chronology reverses source PR #26"):
            assert_chronology_order(
                [
                    {"dfa": [], "heads": [descendant]},
                    {"dfa": ["DFA-0014"], "heads": []},
                ],
                records,
            )

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
            assert_chronology_order(
                [
                    {"dfa": ["DFA-0012"], "heads": []},
                    {"dfa": ["DFA-0014"], "heads": []},
                ],
                records,
            )


if __name__ == "__main__":
    unittest.main()
