from __future__ import annotations

import copy
import hashlib
import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1] / "tools" / "verify_development_finding_authority.py"
spec = importlib.util.spec_from_file_location("authority", P)
a = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(a)


class AuthorityTests(unittest.TestCase):
    def review_record(self):
        body = "finding"
        record = {
            "adjudication_id": "DFA-1",
            "repository": a.REPO,
            "pr": 21,
            "head_sha": "a" * 40,
            "evidence_locator": "review_comment:1",
            "disposition": "CONFIRMED",
            "claim": "claim",
            "basis": "basis",
            "source_type": "REVIEW_COMMENT",
            "source_author_login": "bot",
            "source_updated_at": "2026-01-01T00:00:00Z",
            "source_body_sha256": hashlib.sha256(body.encode()).hexdigest(),
        }
        return record, body

    def process_record(self):
        body = "PROCESS_INCIDENT\nclass=workflow.noop_head_mutation\n" + "b" * 40
        record = {
            "source_comment_id": 9,
            "source_author_login": "BogdanAIP",
            "source_updated_at": "2026-01-01T00:00:00Z",
            "source_body_sha256": hashlib.sha256(body.encode()).hexdigest(),
            "pattern_id": "DFP-4",
            "failure_class": "workflow.noop_head_mutation",
            "occurrences": [
                {
                    "occurrence_id": "O1",
                    "head_sha": "b" * 40,
                    "relation": "REPEAT",
                    "prevention_failure_reason": "GUARD_TOO_NARROW",
                }
            ],
        }
        payload = {
            "id": 9,
            "issue_url": f"https://api.github.com/repos/{a.REPO}/issues/21",
            "user": {"login": "BogdanAIP"},
            "updated_at": record["source_updated_at"],
            "body": body,
        }
        return record, payload

    def test_ledger_claim_is_bound(self):
        record, _ = self.review_record()
        ledger = {
            "schema_version": "DEVELOPMENT_FINDING_ADJUDICATION_V1",
            **{k: record[k] for k in (
                "adjudication_id",
                "repository",
                "pr",
                "head_sha",
                "evidence_locator",
                "disposition",
                "claim",
                "basis",
            )},
        }
        ledger["claim"] = "negated"
        with self.assertRaises(a.E):
            a.bind_ledger([ledger], [record])

    def test_review_source_binds_body_head_pr_actor_and_update(self):
        record, body = self.review_record()
        payload = {
            "id": 1,
            "pull_request_url": f"https://api.github.com/repos/{a.REPO}/pulls/21",
            "original_commit_id": "a" * 40,
            "user": {"login": "bot"},
            "updated_at": record["source_updated_at"],
            "body": body,
        }
        a.source_review(record, lambda _: payload)
        for field, value in (
            ("original_commit_id", "b" * 40),
            ("updated_at", "2026-01-01T00:00:01Z"),
            ("body", "edited"),
        ):
            changed = dict(payload)
            changed[field] = value
            with self.assertRaises(a.E):
                a.source_review(record, lambda _, q=changed: q)

    def test_review_occurrence_requires_explicit_kind_and_confirmation(self):
        patterns = [{
            "pattern_id": "DFP-1",
            "failure_class": "x",
            "origin": {"source_kind": "REVIEW_FINDING"},
            "occurrences": [{
                "occurrence_id": "O1",
                "relation": "ORIGIN",
                "pr": 21,
                "head_sha": "a" * 40,
                "evidence_locator": "review_comment:1",
                "prevention_failure_reason": None,
            }],
        }]
        with self.assertRaises(a.E):
            a.occurrence_authority(patterns, {}, {}, {})
        kinds = {("DFP-1", "O1"): "REVIEW_FINDING"}
        with self.assertRaises(a.E):
            a.occurrence_authority(patterns, kinds, {}, {})
        adjudications = {(a.REPO, 21, "a" * 40, "review_comment:1"): {"disposition": "CONFIRMED"}}
        a.occurrence_authority(patterns, kinds, adjudications, {})

    def test_ambiguous_review_transport_is_rejected(self):
        patterns = [{
            "pattern_id": "DFP-1",
            "failure_class": "x",
            "origin": {"source_kind": "REVIEW_FINDING"},
            "occurrences": [{
                "occurrence_id": "O1",
                "relation": "ORIGIN",
                "pr": 21,
                "head_sha": "a" * 40,
                "evidence_locator": "issue_comment:9",
                "prevention_failure_reason": None,
            }],
        }]
        with self.assertRaises(a.E):
            a.occurrence_authority(
                patterns,
                {("DFP-1", "O1"): "REVIEW_FINDING"},
                {},
                {},
            )

    def test_process_source_binds_exact_body_and_update(self):
        record, payload = self.process_record()
        bound = a.bind_process_incidents([record], lambda _: payload)
        self.assertIn(("DFP-4", "O1"), bound)
        for field, value in (("updated_at", "2026-01-01T00:00:01Z"), ("body", "edited")):
            changed = dict(payload)
            changed[field] = value
            with self.assertRaises(a.E):
                a.bind_process_incidents([record], lambda _, q=changed: q)

    def test_process_occurrence_requires_claim_specific_binding(self):
        record, payload = self.process_record()
        bindings = a.bind_process_incidents([record], lambda _: payload)
        occurrence = {
            "occurrence_id": "O1",
            "relation": "REPEAT",
            "pr": 21,
            "head_sha": "b" * 40,
            "evidence_locator": "pr_comment:9",
            "prevention_failure_reason": "GUARD_TOO_NARROW",
        }
        patterns = [{
            "pattern_id": "DFP-4",
            "failure_class": "workflow.noop_head_mutation",
            "origin": {"source_kind": "PROCESS_INCIDENT"},
            "occurrences": [occurrence],
        }]
        kinds = {("DFP-4", "O1"): "PROCESS_INCIDENT"}
        a.occurrence_authority(patterns, kinds, {}, bindings)
        for field, value in (
            ("head_sha", "c" * 40),
            ("relation", "RELATED"),
            ("prevention_failure_reason", "NEW_VARIANT"),
            ("evidence_locator", "pr_comment:10"),
        ):
            changed = copy.deepcopy(patterns)
            changed[0]["occurrences"][0][field] = value
            with self.assertRaises(a.E):
                a.occurrence_authority(changed, kinds, {}, bindings)
        changed = copy.deepcopy(patterns)
        changed[0]["failure_class"] = "other.class"
        with self.assertRaises(a.E):
            a.occurrence_authority(changed, kinds, {}, bindings)

    def test_extra_process_manifest_binding_is_rejected(self):
        record, payload = self.process_record()
        bindings = a.bind_process_incidents([record], lambda _: payload)
        patterns = [{
            "pattern_id": "DFP-1",
            "failure_class": "x",
            "origin": {"source_kind": "REVIEW_FINDING"},
            "occurrences": [{
                "occurrence_id": "O1",
                "relation": "ORIGIN",
                "pr": 21,
                "head_sha": "a" * 40,
                "evidence_locator": "review_comment:1",
                "prevention_failure_reason": None,
            }],
        }]
        kinds = {("DFP-1", "O1"): "REVIEW_FINDING"}
        adjudications = {(a.REPO, 21, "a" * 40, "review_comment:1"): {"disposition": "CONFIRMED"}}
        with self.assertRaises(a.E):
            a.occurrence_authority(patterns, kinds, adjudications, bindings)


if __name__ == "__main__":
    unittest.main()
