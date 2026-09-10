from __future__ import annotations

import inspect
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = "docs/EVIDENCE_INDEX.md"
LEDGER = "data/development-finding-adjudications.jsonl"

DFA_RE = re.compile(r"DFA-[0-9]{4}", re.IGNORECASE)
DFA_RANGE_RE = re.compile(r"`?DFA-([0-9]{4})`?\s*\.\.\s*`?DFA-([0-9]{4})`?", re.IGNORECASE)
HEAD_RE = re.compile(r"\bHEAD\s*:?\s*`([0-9a-f]{40})`", re.IGNORECASE)
TOKEN_RE = re.compile(
    r"(?P<range>`?DFA-(?P<start>[0-9]{4})`?\s*\.\.\s*`?DFA-(?P<end>[0-9]{4})`?)"
    r"|(?P<dfa>DFA-[0-9]{4})"
    r"|(?P<head>\bHEAD\s*:?\s*`(?P<sha>[0-9a-f]{40})`)",
    re.IGNORECASE,
)
CHRONOLOGY_HEADING_RE = re.compile(
    r"^(?:"
    r"#{1,6}[ \t]+(?:PR[ \t]+#[1-9][0-9]*[ \t]+)?review/remediation chronology:?(?:[ \t]+#+)?"
    r"|(?:PR[ \t]+#[1-9][0-9]*[ \t]+)?review/remediation chronology:?"
    r")[ \t]*$",
    re.IGNORECASE,
)
NUMBERED_RE = re.compile(r"^[0-9]{1,9}[.)][ \t]{1,4}(?=\S)")
PR_CONTEXT_RE = re.compile(
    r"^(?:"
    r"#{1,6}[ \t]+.*?\bPR[ \t]+#(?P<heading>[1-9][0-9]*)\b.*"
    r"|(?:[-*][ \t]+)?PR[ \t]+#(?P<body>[1-9][0-9]*)[ \t]+—.*"
    r")$",
    re.IGNORECASE,
)
ACCEPTED_HEAD_RE = re.compile(
    r"^-[ \t]+accepted exact PR HEAD:[ \t]*`(?P<head>[0-9a-f]{40})`[ \t]*$",
    re.IGNORECASE,
)
FENCE_OPEN_RE = re.compile(r"^(?P<indent> {0,3})(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
_SOURCE_PR_HEADS: dict[int, str] = {}


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


def visible_markdown_lines(text: str) -> list[str]:
    visible: list[str] = []
    fence_char: str | None = None
    fence_len = 0
    in_html_comment = False

    for raw_line in text.splitlines():
        if fence_char is not None:
            candidate = raw_line.lstrip(" ")
            indent = len(raw_line) - len(candidate)
            if indent <= 3 and re.fullmatch(
                rf"{re.escape(fence_char)}{{{fence_len},}}[ \t]*",
                candidate,
            ):
                fence_char = None
                fence_len = 0
            continue

        line = raw_line
        rendered: list[str] = []
        cursor = 0
        while cursor < len(line):
            if in_html_comment:
                end = line.find("-->", cursor)
                if end < 0:
                    cursor = len(line)
                    break
                in_html_comment = False
                cursor = end + 3
                continue

            start = line.find("<!--", cursor)
            if start < 0:
                rendered.append(line[cursor:])
                cursor = len(line)
                break
            rendered.append(line[cursor:start])
            in_html_comment = True
            cursor = start + 4

        line = "".join(rendered)
        if not line and in_html_comment:
            continue

        match = FENCE_OPEN_RE.fullmatch(line)
        if match is not None:
            fence = match.group("fence")
            info = match.group("info")
            if fence[0] == "`" and "`" in info:
                visible.append(line)
                continue
            fence_char = fence[0]
            fence_len = len(fence)
            continue

        visible.append(line)

    return visible


def top_level_indented_code(line: str) -> bool:
    return line.startswith("\t") or line.startswith("    ")


def accepted_pr_heads(text: str) -> dict[int, str]:
    heads: dict[int, str] = {}
    current_pr: int | None = None
    for line in visible_markdown_lines(text):
        if top_level_indented_code(line):
            continue
        stripped = line.strip()
        context = PR_CONTEXT_RE.fullmatch(stripped)
        if context is not None:
            current_pr = int(context.group("heading") or context.group("body"))
            continue
        accepted = ACCEPTED_HEAD_RE.fullmatch(stripped)
        if accepted is None:
            continue
        if current_pr is None:
            raise AssertionError("accepted exact PR HEAD lacks an unambiguous PR context")
        head = accepted.group("head").lower()
        previous = heads.get(current_pr)
        if previous is not None and previous != head:
            raise AssertionError(f"conflicting accepted exact heads for PR #{current_pr}")
        heads[current_pr] = head
    return heads


def accepted_source_head(pr: int) -> str:
    heads = accepted_pr_heads(git_text(INDEX))
    head = heads.get(pr)
    if head is None:
        raise AssertionError(f"canonical EVIDENCE_INDEX lacks accepted exact PR HEAD for PR #{pr}")
    return head


def ordered_refs(text: str) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for match in TOKEN_RE.finditer(text):
        if match.group("range") is not None:
            start = int(match.group("start"))
            end = int(match.group("end"))
            if end < start or end - start > 999:
                raise AssertionError(f"invalid compact DFA range: DFA-{start:04d}..DFA-{end:04d}")
            refs.extend(("DFA", f"DFA-{value:04d}") for value in range(start, end + 1))
        elif match.group("dfa") is not None:
            refs.append(("DFA", match.group("dfa").upper()))
        else:
            refs.append(("HEAD", match.group("sha").lower()))
    return refs


def dfa_refs(text: str) -> list[str]:
    return [value for kind, value in ordered_refs(text) if kind == "DFA"]


def chronology_blocks(text: str) -> list[list[list[tuple[str, str]]]]:
    blocks: list[list[list[tuple[str, str]]]] = []
    current_block: list[list[tuple[str, str]]] | None = None
    current_event: list[str] | None = None

    def flush_event() -> None:
        nonlocal current_event
        if current_block is not None and current_event is not None:
            current_block.append(ordered_refs("\n".join(current_event)))
        current_event = None

    def flush_block() -> None:
        nonlocal current_block
        flush_event()
        if current_block is not None:
            blocks.append(current_block)
        current_block = None

    for line in visible_markdown_lines(text):
        indented_code = top_level_indented_code(line)
        stripped = line.strip()
        if not indented_code and CHRONOLOGY_HEADING_RE.fullmatch(stripped):
            flush_block()
            current_block = []
            continue
        if current_block is not None and not indented_code and stripped.startswith("#"):
            flush_block()
            continue
        if current_block is None:
            continue
        if not indented_code and NUMBERED_RE.match(stripped):
            flush_event()
            current_event = [stripped]
        elif current_event is not None:
            if not stripped or line[:1].isspace():
                current_event.append(stripped)
            else:
                flush_block()

    flush_block()
    return blocks


def commit_available(sha: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def _git_is_ancestor(older: str, newer: str) -> bool:
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


def ensure_source_history(pr: int, *shas: str) -> None:
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

    if pr not in _SOURCE_PR_HEADS:
        source_head = accepted_source_head(pr)
        result = subprocess.run(
            ["git", "fetch", "--quiet", "--no-tags", "origin", source_head],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            raise AssertionError(
                f"cannot fetch immutable accepted source PR #{pr} head {source_head}: "
                + result.stderr.decode(errors="replace")
            )
        if not commit_available(source_head):
            raise AssertionError(
                f"immutable accepted source PR #{pr} head {source_head} is unavailable after exact fetch"
            )
        _SOURCE_PR_HEADS[pr] = source_head

    missing = [sha for sha in shas if not commit_available(sha)]
    if missing:
        raise AssertionError(
            f"source PR #{pr} chronology commits are unavailable after accepted-head history fetch: {missing}"
        )


def source_pr_contains(pr: int, sha: str) -> bool:
    ensure_source_history(pr, sha)
    return _git_is_ancestor(sha, _SOURCE_PR_HEADS[pr])


def is_ancestor(pr: int, older: str, newer: str) -> bool:
    ensure_source_history(pr, older, newer)
    return _git_is_ancestor(older, newer)


def assert_chronology_order(events: list[list[tuple[str, str]]], records: dict[str, dict]) -> None:
    source_prs: set[int] = set()
    for event in events:
        for kind, value in event:
            if kind != "DFA":
                continue
            if value not in records:
                raise AssertionError(f"EVIDENCE_INDEX chronology references unknown adjudication {value}")
            source_prs.add(records[value]["pr"])

    if not source_prs:
        return

    seen_dfa: set[str] = set()
    last_by_pr: dict[int, tuple[str, str]] = {}

    for event_number, event in enumerate(events, 1):
        event_prs = {
            records[value]["pr"]
            for kind, value in event
            if kind == "DFA" and value in records
        }

        for kind, value in event:
            if kind == "DFA":
                if value in seen_dfa:
                    continue
                row = records[value]
                pr = row["pr"]
                label = value
                head = row["head_sha"]
                seen_dfa.add(value)
            else:
                if len(source_prs) == 1:
                    pr = next(iter(source_prs))
                elif len(event_prs) == 1:
                    pr = next(iter(event_prs))
                else:
                    raise AssertionError(
                        f"chronology block has ambiguous explicit HEAD event {event_number} "
                        f"across source PRs {sorted(source_prs)}"
                    )
                label = f"event-{event_number}-HEAD"
                head = value
                if not source_pr_contains(pr, head):
                    raise AssertionError(
                        f"explicit HEAD {head} is not reachable from accepted source PR #{pr} head "
                        f"{_SOURCE_PR_HEADS[pr]}"
                    )

            previous = last_by_pr.get(pr)
            if previous is not None:
                previous_label, previous_head = previous
                if not is_ancestor(pr, previous_head, head):
                    raise AssertionError(
                        f"chronology reverses source PR #{pr}: "
                        f"{previous_label}@{previous_head} is not an ancestor of {label}@{head}"
                    )
            last_by_pr[pr] = (label, head)


class EvidenceIndexDevelopmentChronologyTests(unittest.TestCase):
    def test_canonical_chronology_follows_source_git_order(self) -> None:
        records = ledger_by_id()
        blocks = chronology_blocks(git_text(INDEX))
        governed = [
            events
            for events in blocks
            if any(kind == "DFA" for event in events for kind, _ in event)
        ]
        self.assertTrue(governed, "expected at least one DFA reference in canonical chronology")
        for events in governed:
            assert_chronology_order(events, records)

    def test_compact_range_expands_every_adjudication(self) -> None:
        self.assertEqual(
            dfa_refs("`DFA-0014`..`DFA-0016`"),
            ["DFA-0014", "DFA-0015", "DFA-0016"],
        )

    def test_prefixed_chronology_heading_is_governed(self) -> None:
        records = ledger_by_id()
        blocks = chronology_blocks(
            "#### PR #26 review/remediation chronology\n\n"
            "1. Later finding `DFA-0012`.\n"
            "2. Older finding `DFA-0014`.\n"
        )
        self.assertEqual(len(blocks), 1)
        with self.assertRaisesRegex(AssertionError, "chronology reverses source PR #26"):
            assert_chronology_order(blocks[0], records)

    def test_parenthesis_ordered_markers_are_governed(self) -> None:
        records = ledger_by_id()
        blocks = chronology_blocks(
            "#### PR #26 review/remediation chronology\n\n"
            "1) Later finding `DFA-0012`.\n"
            "2) Older finding `DFA-0014`.\n"
        )
        self.assertEqual(len(blocks), 1)
        with self.assertRaisesRegex(AssertionError, "chronology reverses source PR #26"):
            assert_chronology_order(blocks[0], records)

    def test_closing_hash_atx_heading_is_governed(self) -> None:
        records = ledger_by_id()
        blocks = chronology_blocks(
            "#### PR #26 review/remediation chronology ####\n\n"
            "1. Later finding `DFA-0012`.\n"
            "2. Older finding `DFA-0014`.\n"
        )
        self.assertEqual(len(blocks), 1)
        with self.assertRaisesRegex(AssertionError, "chronology reverses source PR #26"):
            assert_chronology_order(blocks[0], records)

    def test_fenced_chronology_examples_are_ignored(self) -> None:
        cases = (
            ("```markdown", "```"),
            ("  ~~~~text", "  ~~~~"),
        )
        for opening, closing in cases:
            with self.subTest(opening=opening):
                text = (
                    f"{opening}\n"
                    "Review/remediation chronology:\n"
                    "1. Example `DFA-9999`.\n"
                    f"{closing}\n"
                )
                self.assertEqual(chronology_blocks(text), [])

    def test_fenced_accepted_heads_are_ignored(self) -> None:
        accepted = "8cb7d24ce18042227ebf6e9b4acbdcdb6b947922"
        fake = "f" * 40
        cases = (
            ("```markdown", "```"),
            ("  ~~~~text", "  ~~~~"),
        )
        for opening, closing in cases:
            with self.subTest(opening=opening):
                text = (
                    f"{opening}\n"
                    "PR #26 — `example only`\n"
                    f"- accepted exact PR HEAD: `{fake}`\n"
                    f"{closing}\n"
                    "PR #26 — `Stage 1: harden bootstrap commentary semantic bindings`\n"
                    f"- accepted exact PR HEAD: `{accepted}`\n"
                )
                self.assertEqual(accepted_pr_heads(text), {26: accepted})

    def test_html_commented_chronology_examples_are_ignored(self) -> None:
        text = (
            "<!--\n"
            "Review/remediation chronology:\n"
            "1. Example `DFA-9999`.\n"
            "-->\n"
        )
        self.assertEqual(chronology_blocks(text), [])

    def test_html_commented_accepted_heads_are_ignored(self) -> None:
        accepted = "8cb7d24ce18042227ebf6e9b4acbdcdb6b947922"
        fake = "f" * 40
        text = (
            "<!--\n"
            "PR #26 — `example only`\n"
            f"- accepted exact PR HEAD: `{fake}`\n"
            "-->\n"
            "PR #26 — `Stage 1: harden bootstrap commentary semantic bindings`\n"
            f"- accepted exact PR HEAD: `{accepted}`\n"
        )
        self.assertEqual(accepted_pr_heads(text), {26: accepted})

    def test_top_level_indented_code_examples_are_ignored(self) -> None:
        text = (
            "    Review/remediation chronology:\n"
            "    1. Example `DFA-9999`.\n"
        )
        self.assertEqual(chronology_blocks(text), [])

    def test_top_level_indented_accepted_heads_are_ignored(self) -> None:
        accepted = "8cb7d24ce18042227ebf6e9b4acbdcdb6b947922"
        fake = "f" * 40
        text = (
            "    PR #26 — `example only`\n"
            f"    - accepted exact PR HEAD: `{fake}`\n"
            "PR #26 — `Stage 1: harden bootstrap commentary semantic bindings`\n"
            f"- accepted exact PR HEAD: `{accepted}`\n"
        )
        self.assertEqual(accepted_pr_heads(text), {26: accepted})

    def test_acceptance_context_with_title_is_parsed(self) -> None:
        text = (
            "PR #26 — `Stage 1: harden bootstrap commentary semantic bindings`\n"
            "\nAcceptance identity:\n\n"
            "- accepted exact PR HEAD: `8cb7d24ce18042227ebf6e9b4acbdcdb6b947922`\n"
        )
        self.assertEqual(
            accepted_pr_heads(text),
            {26: "8cb7d24ce18042227ebf6e9b4acbdcdb6b947922"},
        )

    def test_source_pr_membership_uses_immutable_accepted_head(self) -> None:
        self.assertEqual(
            accepted_source_head(26),
            "8cb7d24ce18042227ebf6e9b4acbdcdb6b947922",
        )
        self.assertNotIn("refs/pull/", inspect.getsource(ensure_source_history))

    def test_continuation_lines_are_part_of_numbered_event(self) -> None:
        blocks = chronology_blocks(
            "Review/remediation chronology:\n\n"
            "1. Review completed.\n"
            "   - finding: `DFA-0014`\n"
            "2. Later event `DFA-0012`.\n\n"
            "# next\n"
        )
        self.assertEqual(blocks[0][0], [("DFA", "DFA-0014")])
        self.assertEqual(blocks[0][1], [("DFA", "DFA-0012")])

    def test_four_space_continuation_is_part_of_numbered_event(self) -> None:
        blocks = chronology_blocks(
            "Review/remediation chronology:\n\n"
            "1. Review completed.\n"
            "    - finding: `DFA-0014`\n"
            "2. Later event `DFA-0012`.\n\n"
            "# next\n"
        )
        self.assertEqual(blocks[0][0], [("DFA", "DFA-0014")])
        self.assertEqual(blocks[0][1], [("DFA", "DFA-0012")])

    def test_top_level_prose_ends_numbered_chronology(self) -> None:
        records = ledger_by_id()
        older = records["DFA-0014"]["head_sha"]
        blocks = chronology_blocks(
            "Review/remediation chronology:\n\n"
            "1. Review completed `DFA-0012`.\n\n"
            f"Trailing note about older exact HEAD `{older}` must not belong to the list.\n\n"
            "# next\n"
        )
        self.assertEqual(blocks, [[[("DFA", "DFA-0012")]]])

    def test_repeated_summary_refs_do_not_create_new_events(self) -> None:
        records = ledger_by_id()
        assert_chronology_order(
            [
                [("DFA", "DFA-0014")],
                [("DFA", "DFA-0012"), ("DFA", "DFA-0013")],
                [
                    ("DFA", "DFA-0015"),
                    ("DFA", "DFA-0016"),
                    ("DFA", "DFA-0014"),
                    ("DFA", "DFA-0015"),
                    ("DFA", "DFA-0016"),
                ],
            ],
            records,
        )

    def test_head_only_descendant_then_older_finding_is_rejected(self) -> None:
        records = ledger_by_id()
        descendant = records["DFA-0012"]["head_sha"]
        with self.assertRaisesRegex(AssertionError, "chronology reverses source PR #26"):
            assert_chronology_order(
                [
                    [("HEAD", descendant)],
                    [("DFA", "DFA-0014")],
                ],
                records,
            )

    def test_explicit_head_outside_source_pr_is_rejected(self) -> None:
        records = ledger_by_id()
        older = records["DFA-0014"]["head_sha"]
        foreign_descendant = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout.strip()
        ensure_source_history(26, older, foreign_descendant)
        self.assertTrue(_git_is_ancestor(older, foreign_descendant))
        with self.assertRaisesRegex(AssertionError, "not reachable from accepted source PR #26 head"):
            assert_chronology_order(
                [
                    [("DFA", "DFA-0014")],
                    [("HEAD", foreign_descendant)],
                ],
                records,
            )

    def test_interleaved_dfa_then_later_head_preserves_text_order(self) -> None:
        records = ledger_by_id()
        newer = records["DFA-0012"]["head_sha"]
        event = ordered_refs(f"`DFA-0014` was fixed and final HEAD `{newer}` passed")
        self.assertEqual(event[0], ("DFA", "DFA-0014"))
        self.assertEqual(event[1], ("HEAD", newer))
        assert_chronology_order([event], records)

    def test_interleaved_later_head_then_older_dfa_is_rejected(self) -> None:
        records = ledger_by_id()
        newer = records["DFA-0012"]["head_sha"]
        event = ordered_refs(f"Exact HEAD `{newer}` passed before `DFA-0014` was recorded")
        with self.assertRaisesRegex(AssertionError, "chronology reverses source PR #26"):
            assert_chronology_order([event], records)

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
                    [("DFA", "DFA-0012")],
                    [("DFA", "DFA-0014")],
                ],
                records,
            )


if __name__ == "__main__":
    unittest.main()