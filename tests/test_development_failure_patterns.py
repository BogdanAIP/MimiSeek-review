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


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def canonical_patterns() -> list[dict]:
    return guard.load_canonical_registry(ROOT)


def adjudications() -> dict:
    return guard.load_adjudications(ROOT)


def seed() -> dict:
    return copy.deepcopy(canonical_patterns()[0])


def fixture_process_pattern() -> dict:
    return {
        "schema_version": guard.SCHEMA_VERSION,
        "pattern_id": "DFP-9000",
        "status": "ACTIVE",
        "title": "fixture",
        "failure_class": "fixture.process_incident",
        "origin": {
            "source_kind": "PROCESS_INCIDENT",
            "repository": guard.REPOSITORY,
            "pr": 1,
            "head_sha": "1" * 40,
            "evidence_locator": "pr_comment:1",
        },
        "root_cause": "fixture cause",
        "failure_mechanism": "fixture mechanism",
        "violated_invariant": "fixture invariant",
        "trigger_conditions": ["fixture trigger"],
        "applicable_scope": ["fixture scope"],
        "non_applicable_scope": [],
        "repository_search": {
            "status": "COMPLETED",
            "searched_scope": ["*.py"],
            "discovered_instances": ["tracked.py"],
            "follow_up_refs": [],
            "notes": "fixture search",
        },
        "prevention": {
            "kind": "EXECUTABLE",
            "guard_refs": ["guard.py"],
            "regression_refs": ["regression.py"],
            "manual_only_reason": None,
        },
        "occurrences": [{
            "occurrence_id": "DFP-9000-O001",
            "relation": "ORIGIN",
            "pr": 1,
            "head_sha": "1" * 40,
            "evidence_locator": "pr_comment:1",
            "prevention_failure_reason": None,
        }],
    }


def fixture_adjudication() -> dict:
    return {
        "schema_version": guard.ADJUDICATION_SCHEMA_VERSION,
        "adjudication_id": "DFA-9000",
        "repository": guard.REPOSITORY,
        "pr": 1,
        "head_sha": "2" * 40,
        "evidence_locator": "review_comment:2",
        "disposition": "CONFIRMED",
        "claim": "fixture confirmed finding",
        "basis": "fixture adjudication basis",
    }


def write_fixture_repo(root: Path) -> None:
    git(root, "init", "-q")
    (root / "data/schemas").mkdir(parents=True)
    (root / "data").mkdir(exist_ok=True)
    for name in ("tracked.py", "guard.py", "regression.py"):
        (root / name).write_text(f"# {name}\n", encoding="utf-8")
    (root / guard.SCHEMA_PATH).write_text((ROOT / guard.SCHEMA_PATH).read_text(encoding="utf-8"), encoding="utf-8")
    (root / guard.ADJUDICATION_SCHEMA_PATH).write_text((ROOT / guard.ADJUDICATION_SCHEMA_PATH).read_text(encoding="utf-8"), encoding="utf-8")
    (root / guard.ADJUDICATIONS_PATH).write_text(json.dumps(fixture_adjudication(), separators=(",", ":")) + "\n", encoding="utf-8")
    (root / guard.REGISTRY_PATH).write_text(json.dumps(fixture_process_pattern(), separators=(",", ":")) + "\n", encoding="utf-8")
    git(root, "add", ".")
    subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture"], cwd=root, check=True)


class DevelopmentFailurePatternTests(unittest.TestCase):
    def test_registry_exact_seed_current_patterns_and_adjudications(self) -> None:
        guard.validate_schema_identity(ROOT)
        patterns = canonical_patterns()
        self.assertEqual([p["pattern_id"] for p in patterns], [f"DFP-{i:04d}" for i in range(1, 7)])
        self.assertEqual(patterns[0]["repository_search"]["follow_up_refs"], ["https://github.com/BogdanAIP/MimiSeek-review/issues/22"])
        self.assertEqual(patterns[2]["occurrences"][1]["relation"], "RELATED")
        self.assertEqual(patterns[5]["occurrences"][1]["relation"], "REPEAT")
        self.assertEqual(patterns[5]["occurrences"][1]["prevention_failure_reason"], "GUARD_TOO_NARROW")
        records = guard.load_adjudications(ROOT)
        self.assertEqual(len(records), 8)
        for pattern in patterns:
            for occurrence in pattern["occurrences"]:
                if occurrence["evidence_locator"].startswith("review_comment:"):
                    key = (guard.REPOSITORY, occurrence["pr"], occurrence["head_sha"], occurrence["evidence_locator"])
                    self.assertEqual(records[key]["disposition"], "CONFIRMED")

    def test_review_finding_and_review_comment_occurrences_require_confirmed_adjudication(self) -> None:
        p = seed(); records = adjudications(); tracked = guard.tracked_regular_files(ROOT)
        guard.validate_pattern(p, ROOT, "p", tracked=tracked, adjudications=records)
        p = seed(); p["origin"]["evidence_locator"] = "review_comment:999999"
        p["occurrences"][0]["evidence_locator"] = "review_comment:999999"
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "not backed by a CONFIRMED exact-HEAD adjudication"):
            guard.validate_pattern(p, ROOT, "p", tracked=tracked, adjudications=records)
        p = seed(); p["occurrences"].append({
            "occurrence_id": "DFP-0001-O999", "relation": "RELATED", "pr": 21,
            "head_sha": "3" * 40, "evidence_locator": "review_comment:999998", "prevention_failure_reason": None,
        })
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "review-comment occurrence is not backed"):
            guard.validate_pattern(p, ROOT, "p", tracked=tracked, adjudications=records)
        q = fixture_process_pattern()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); write_fixture_repo(root)
            guard.validate_pattern(q, root, "q", tracked=guard.tracked_regular_files(root), adjudications={})

    def test_executable_and_manual_prevention_contracts(self) -> None:
        records=adjudications(); tracked=guard.tracked_regular_files(ROOT)
        p = seed(); p["prevention"]["guard_refs"] = []
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "requires guard_refs"):
            guard.validate_pattern(p, ROOT, "p", tracked=tracked, adjudications=records)
        p = seed(); p["prevention"] = {"kind":"MANUAL_ONLY","guard_refs":[],"regression_refs":[],"manual_only_reason":"external tool boundary"}
        guard.validate_pattern(p, ROOT, "p", tracked=tracked, adjudications=records)
        p["prevention"]["regression_refs"] = ["tests/test_development_failure_patterns.py"]
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "must not claim executable"):
            guard.validate_pattern(p, ROOT, "p", tracked=tracked, adjudications=records)

    def test_bounded_follow_up_syntax_and_live_resolution(self) -> None:
        records=adjudications(); tracked=guard.tracked_regular_files(ROOT)
        for ref in ("done later", "https://github.com/other/repo/issues/22", "https://github.com/BogdanAIP/MimiSeek-review/issues/0", "https://github.com/BogdanAIP/MimiSeek-review/issues/22?x=1"):
            with self.subTest(ref=ref):
                p=seed(); p["repository_search"]["follow_up_refs"]=[ref]
                with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "exact MimiSeek issue URL or tracked regular file"):
                    guard.validate_pattern(p, ROOT, "p", tracked=tracked, adjudications=records)
        seen=[]
        p=seed()
        guard.validate_pattern(p, ROOT, "p", tracked=tracked, adjudications=records, issue_resolver=lambda n: seen.append(n))
        self.assertEqual(seen, [22])
        def missing(n: int) -> None:
            raise guard.DevelopmentFailurePatternError(f"missing issue {n}")
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "missing issue 22"):
            guard.validate_pattern(p, ROOT, "p", tracked=tracked, adjudications=records, issue_resolver=missing)

    def test_tracked_file_can_be_bounded_follow_up(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); write_fixture_repo(root); p=fixture_process_pattern()
            p["repository_search"]["status"]="BOUNDED_FOLLOW_UP"; p["repository_search"]["follow_up_refs"]=["tracked.py"]
            guard.validate_pattern(p, root, "p", tracked=guard.tracked_regular_files(root), adjudications={})

    def test_completed_bounded_unknown_and_retirement_consistency(self) -> None:
        records=adjudications(); tracked=guard.tracked_regular_files(ROOT)
        p=seed(); p["repository_search"]["status"]="COMPLETED"
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "COMPLETED search must not retain follow_up_refs"):
            guard.validate_pattern(p, ROOT, "p", tracked=tracked, adjudications=records)
        p=seed(); p["occurrences"].append({"occurrence_id":"DFP-0001-O999","relation":"REPEAT","pr":21,"head_sha":"5be33a8d09534e412bc08ae752beba86f788cf57","evidence_locator":"review_comment:3942225446","prevention_failure_reason":"UNKNOWN_PENDING_ANALYSIS"})
        p["repository_search"]={**p["repository_search"],"status":"COMPLETED","follow_up_refs":[]}
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "UNKNOWN_PENDING_ANALYSIS requires BOUNDED_FOLLOW_UP"):
            guard.validate_pattern(p, ROOT, "p", tracked=tracked, adjudications=records)
        p["repository_search"]={**p["repository_search"],"status":"BOUNDED_FOLLOW_UP","follow_up_refs":["https://github.com/BogdanAIP/MimiSeek-review/issues/22"]}
        guard.validate_pattern(p, ROOT, "p", tracked=tracked, adjudications=records)
        self.assertEqual(guard.active_summary(p)["pending_repeat_analysis"], ["DFP-0001-O999"])
        p["status"]="RETIRED"
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError, "RETIRED pattern cannot hide unresolved"):
            guard.validate_pattern(p, ROOT, "p", tracked=tracked, adjudications=records)
        p=seed(); p["repository_search"]={**p["repository_search"],"status":"COMPLETED","follow_up_refs":[]}; p["status"]="RETIRED"
        guard.validate_pattern(p, ROOT, "p", tracked=tracked, adjudications=records)

    def test_schema_represents_pending_repeat_closure(self) -> None:
        schema=json.loads(guard.git_head_text(ROOT, guard.SCHEMA_PATH))
        self.assertTrue(guard._schema_has_pending_rule(schema))
        matching=[]
        for rule in schema["allOf"]:
            contains=rule.get("if",{}).get("properties",{}).get("occurrences",{}).get("contains",{})
            props=contains.get("properties",{}) if isinstance(contains,dict) else {}
            if props.get("prevention_failure_reason",{}).get("const")=="UNKNOWN_PENDING_ANALYSIS":
                matching.append(rule)
        self.assertEqual(len(matching),1)
        self.assertEqual(matching[0]["then"]["properties"]["repository_search"]["properties"]["status"]["const"], "BOUNDED_FOLLOW_UP")

    def test_canonical_registry_and_schema_bytes_ignore_dirty_or_staged_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); write_fixture_repo(root)
            head=guard.git_head(root)
            guard.validate_schema_identity(root)
            self.assertEqual(len(guard.load_canonical_registry(root)),1)
            (root/guard.REGISTRY_PATH).write_text("not-json\n", encoding="utf-8")
            (root/guard.SCHEMA_PATH).write_text("{}\n", encoding="utf-8")
            git(root,"add",guard.REGISTRY_PATH,guard.SCHEMA_PATH)
            self.assertEqual(guard.git_head(root), head)
            guard.validate_schema_identity(root)
            self.assertEqual(len(guard.load_canonical_registry(root)),1)

    def test_cli_rejects_external_registry_override_and_expected_head_mismatch(self) -> None:
        parser=guard.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["--registry", "/tmp/outside.jsonl"])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); write_fixture_repo(root)
            self.assertEqual(guard.main(["--root",str(root),"--expected-head",guard.git_head(root)]),0)
            self.assertEqual(guard.main(["--root",str(root),"--expected-head","0"*40]),1)

    def test_exact_head_git_authority_blocks_checkout_only_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root=Path(tmp); write_fixture_repo(root)
            (root/"untracked.py").write_text("# no\n",encoding="utf-8"); git(root,"add","untracked.py")
            p=fixture_process_pattern(); p["prevention"]["guard_refs"]=["untracked.py"]
            with self.assertRaisesRegex(guard.DevelopmentFailurePatternError,"not a tracked regular file in exact HEAD"):
                guard.validate_pattern(p,root,"p",tracked=guard.tracked_regular_files(root),adjudications={})
            git(root,"reset","-q")
            link=root/"escape.py"; outside=Path(outside_tmp)/"outside.py"; outside.write_text("x",encoding="utf-8")
            try: os.symlink(outside,link)
            except (OSError,NotImplementedError) as exc: self.skipTest(str(exc))
            git(root,"add","escape.py"); subprocess.run(["git","-c","user.name=Test","-c","user.email=test@example.invalid", "commit","-qm","symlink"],cwd=root,check=True)
            p=fixture_process_pattern(); p["prevention"]["guard_refs"]=["escape.py"]
            with self.assertRaisesRegex(guard.DevelopmentFailurePatternError,"not a tracked regular file in exact HEAD"):
                guard.validate_pattern(p,root,"p",tracked=guard.tracked_regular_files(root),adjudications={})

    def test_git_metadata_unmatched_scope_repeat_and_duplicate_class_fail_closed(self) -> None:
        records=adjudications(); tracked=guard.tracked_regular_files(ROOT)
        p=seed(); p["prevention"]["guard_refs"]=[".git/config"]
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError,"must not reference .git"):
            guard.validate_pattern(p,ROOT,"p",tracked=tracked,adjudications=records)
        p=seed(); p["repository_search"]["searched_scope"]=["no/such/*.py"]
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError,"matches no tracked regular files"):
            guard.validate_pattern(p,ROOT,"p",tracked=tracked,adjudications=records)
        p=seed(); p["occurrences"].append({"occurrence_id":"DFP-0001-O999","relation":"REPEAT","pr":21,"head_sha":"5be33a8d09534e412bc08ae752beba86f788cf57","evidence_locator":"review_comment:3942225446","prevention_failure_reason":None})
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError,"requires a prevention_failure_reason"):
            guard.validate_pattern(p,ROOT,"p",tracked=tracked,adjudications=records)
        p=seed(); q=copy.deepcopy(p); q["pattern_id"]="DFP-9999"
        for i, occurrence in enumerate(q["occurrences"], 1):
            occurrence["occurrence_id"] = f"DFP-9999-O{i:03d}"
        text=json.dumps(p)+"\n"+json.dumps(q)+"\n"
        with self.assertRaisesRegex(guard.DevelopmentFailurePatternError,"duplicate failure_class"):
            guard.load_registry_text(text,ROOT,"fixture",adjudications=records)

    def test_active_summary_is_bounded_not_answer_key(self) -> None:
        summary=guard.active_summary(seed())
        self.assertEqual(summary["search_status"],"BOUNDED_FOLLOW_UP")
        self.assertIn("pending_repeat_analysis",summary)
        self.assertNotIn("root_cause",summary); self.assertNotIn("occurrences",summary)

    def test_development_protocol_is_only_normative_owner(self) -> None:
        protocol=(ROOT/"docs/DEVELOPMENT_PROTOCOL.md").read_text(encoding="utf-8")
        reference=(ROOT/"docs/DEVELOPMENT_REPEAT_PREVENTION.md").read_text(encoding="utf-8")
        self.assertIn("Canonical owner for the MimiSeek cross-chat development process: this document.",protocol)
        self.assertIn("A failure pattern may be `RETIRED` only after",protocol)
        self.assertIn("Status: explanatory reference only; non-authoritative.",reference)
        for forbidden in ("## Required closure loop","## Development-start retrieval","## Review-time repeat check","## Current pattern inventory","## Why `DFP-0001` is not marked complete","DFP-0001"):
            self.assertNotIn(forbidden,reference)


if __name__ == "__main__":
    unittest.main()
