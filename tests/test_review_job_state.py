import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "review_job_state",
    ROOT / "tools" / "review_job_state.py",
)
review_job = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = review_job
SPEC.loader.exec_module(review_job)

BASE = "a" * 40
HEAD = "b" * 40
MOVED_HEAD = "c" * 40
LAUNCH_CAPABILITY = "d" * 40
RETURN_CAPABILITY = "e" * 40


def make_job():
    return review_job.create_job(
        repository_id=1352648898,
        repository="BogdanAIP/uv-studio",
        pr_number=89,
        base_sha=BASE,
        head_sha=HEAD,
        review_policy_ref=BASE,
        reviewer_profile="fresh-readonly-v1",
        reviewer_source="openai-chatgpt",
        review_context="temporary-chat-fresh",
        review_mode="read-only",
        request_ref=(
            "https://github.com/BogdanAIP/MimiSeek-review/"
            "issues/100#issuecomment-1000"
        ),
        executor_source="BogdanAIP/chat-agent-platform",
        launch_capability_ref=LAUNCH_CAPABILITY,
        return_capability_ref=RETURN_CAPABILITY,
    )


def live(*, head=HEAD, base=BASE, state="open", draft=False, merged=False):
    return {
        "repository_id": 1352648898,
        "repository": "BogdanAIP/uv-studio",
        "pr_number": 89,
        "base_sha": base,
        "head_sha": head,
        "state": state,
        "draft": draft,
        "merged": merged,
    }


def result_identity(job, *, validity="CURRENT", status="PASS", findings=0):
    return {
        "schema": "REVIEW_RESULT_V1",
        "job_id": job["job_id"],
        "repository": job["repository"],
        "pr_number": job["pr_number"],
        "base_sha": job["base_sha"],
        "head_sha": job["head_sha"],
        "review_policy_ref": job["review_policy_ref"],
        "reviewer_profile": job["reviewer_profile"],
        "reviewer_source": job["reviewer_source"],
        "review_context": job["review_context"],
        "review_mode": job["review_mode"],
        "validity": validity,
        "status": status,
        "reported_findings": findings,
    }


def advance_to_reviewing():
    job = make_job()
    job = review_job.validate_request(job, 0, live())
    job = review_job.claim_launch(job, 1, "launch-0001", live())
    job = review_job.mark_reviewing(
        job,
        2,
        "launch-0001",
        "private-external-execution-capability",
    )
    return job


def advance_to_result_validated(*, raw="raw terminal result", identity=None, live_state=None):
    job = advance_to_reviewing()
    identity = identity or result_identity(job)
    job = review_job.capture_result(job, 3, identity, raw)
    job = review_job.validate_captured_result(job, 4, live_state or live())
    return job


class ReviewJobIdentityTests(unittest.TestCase):
    def test_creation_is_deterministic_and_identity_bound(self):
        first = make_job()
        second = make_job()
        self.assertEqual(first, second)
        self.assertRegex(first["job_id"], r"^rj_[0-9a-f]{32}$")
        self.assertRegex(first["identity_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(first["state"], "REQUESTED")
        self.assertEqual(first["revision"], 0)

    def test_immutable_identity_mutation_fails_even_if_digest_is_recomputed(self):
        job = make_job()
        job["head_sha"] = MOVED_HEAD
        with self.assertRaises(review_job.ReviewJobIdentityError):
            review_job.validate_job(job)

        job["identity_sha256"] = review_job.derive_identity_sha256(job)
        with self.assertRaisesRegex(
            review_job.ReviewJobIdentityError,
            "job_id does not match",
        ):
            review_job.validate_job(job)

    def test_wrong_live_repository_or_pr_is_identity_error_not_stale(self):
        job = make_job()
        wrong = live()
        wrong["repository_id"] += 1
        with self.assertRaises(review_job.ReviewJobIdentityError):
            review_job.validate_request(job, 0, wrong)

    def test_new_head_is_explicit_stale_before_launch(self):
        job = review_job.validate_request(make_job(), 0, live(head=MOVED_HEAD))
        self.assertEqual(job["state"], "RESULT_VALIDATED")
        self.assertEqual(job["outcome"], "STALE")
        self.assertEqual(job["outcome_code"], "SOURCE_IDENTITY_NOT_CURRENT")
        self.assertIsNone(job["launch_claim_id"])
        self.assertIsNone(job["result_identity"])

    def test_closed_draft_or_merged_source_is_not_current(self):
        for kwargs in (
            {"state": "closed"},
            {"draft": True},
            {"merged": True, "state": "closed"},
        ):
            with self.subTest(kwargs=kwargs):
                job = review_job.validate_request(make_job(), 0, live(**kwargs))
                self.assertEqual(job["outcome"], "STALE")


class ReviewJobPrivacyAndSerializationTests(unittest.TestCase):
    def test_public_record_rejects_private_route_or_conversation_fields(self):
        for key, value in (
            ("return_route", "opaque-secret-route"),
            ("conversation_id", "chatgpt-conversation-secret"),
            ("cookie", "session-cookie"),
        ):
            with self.subTest(key=key):
                job = make_job()
                job[key] = value
                with self.assertRaises(review_job.ReviewJobValidationError):
                    review_job.validate_job(job)

    def test_public_locators_must_be_github_owned(self):
        job = make_job()
        job["request_ref"] = "https://chatgpt.com/c/private-conversation"
        job["identity_sha256"] = review_job.derive_identity_sha256(job)
        job["job_id"] = "rj_" + job["identity_sha256"][:32]
        with self.assertRaisesRegex(
            review_job.ReviewJobValidationError,
            "GitHub-owned durable locator",
        ):
            review_job.validate_job(job)

    def test_external_execution_is_persisted_only_as_digest(self):
        job = advance_to_reviewing()
        self.assertRegex(job["external_execution_sha256"], r"^[0-9a-f]{64}$")
        self.assertNotIn("private-external-execution-capability", json.dumps(job))

    def test_canonical_serialization_round_trips_and_rejects_duplicate_keys(self):
        job = make_job()
        serialized = review_job.serialize_job(job)
        self.assertEqual(review_job.deserialize_job(serialized), job)
        self.assertTrue(serialized.endswith("\n"))

        duplicate = serialized.rstrip()
        duplicate = duplicate[:-1] + ',"schema":"REVIEW_JOB_V1"}'
        with self.assertRaisesRegex(
            review_job.ReviewJobValidationError,
            "duplicate JSON key",
        ):
            review_job.deserialize_job(duplicate)

    def test_machine_schema_has_exact_public_property_set(self):
        schema = json.loads(
            (ROOT / "schemas" / "review-job-v1.schema.json").read_text(encoding="utf-8")
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["properties"]), review_job.PUBLIC_KEYS)
        self.assertEqual(set(schema["required"]), review_job.PUBLIC_KEYS)


class ReviewJobLaunchTests(unittest.TestCase):
    def test_same_launch_claim_is_idempotent_but_different_claim_conflicts(self):
        job = review_job.validate_request(make_job(), 0, live())
        claimed = review_job.claim_launch(job, 1, "launch-0001", live())
        repeated = review_job.claim_launch(
            claimed,
            claimed["revision"],
            "launch-0001",
            live(),
        )
        self.assertEqual(repeated, claimed)

        with self.assertRaises(review_job.ReviewJobConflictError):
            review_job.claim_launch(
                claimed,
                claimed["revision"],
                "launch-0002",
                live(),
            )

    def test_unknown_launch_blocks_blind_resend_until_reconciled(self):
        job = review_job.validate_request(make_job(), 0, live())
        job = review_job.claim_launch(job, 1, "launch-0001", live())
        job = review_job.mark_launch_unknown(job, 2, "launch-0001")

        with self.assertRaises(review_job.ReviewJobTransitionError):
            review_job.claim_launch(
                job,
                job["revision"],
                "launch-0001",
                live(),
            )

        job = review_job.resolve_launch_absent(
            job,
            job["revision"],
            "launch-0001",
        )
        job = review_job.claim_launch(
            job,
            job["revision"],
            "launch-0001",
            live(),
        )
        self.assertEqual(job["state"], "LAUNCH_CLAIMED")

    def test_unknown_launch_can_reconcile_to_exact_execution(self):
        job = review_job.validate_request(make_job(), 0, live())
        job = review_job.claim_launch(job, 1, "launch-0001", live())
        job = review_job.mark_launch_unknown(job, 2, "launch-0001")
        job = review_job.mark_reviewing(
            job,
            job["revision"],
            "launch-0001",
            "exact-execution-after-reconcile",
        )
        self.assertEqual(job["state"], "REVIEWING")

    def test_head_move_between_validation_and_launch_prevents_launch(self):
        job = review_job.validate_request(make_job(), 0, live())
        job = review_job.claim_launch(
            job,
            job["revision"],
            "launch-0001",
            live(head=MOVED_HEAD),
        )
        self.assertEqual(job["state"], "RESULT_VALIDATED")
        self.assertEqual(job["outcome"], "STALE")
        self.assertEqual(
            job["outcome_code"],
            "SOURCE_IDENTITY_MOVED_BEFORE_LAUNCH",
        )
        self.assertIsNone(job["launch_claim_id"])


class ReviewJobResultTests(unittest.TestCase):
    def test_current_pass_is_validated_as_pass(self):
        job = advance_to_result_validated()
        self.assertEqual(job["state"], "RESULT_VALIDATED")
        self.assertEqual(job["outcome"], "PASS")
        self.assertIsNone(job["outcome_code"])

    def test_current_findings_requires_positive_count(self):
        job = advance_to_reviewing()
        finding_result = result_identity(job, status="FINDINGS", findings=2)
        job = review_job.capture_result(job, 3, finding_result, "two findings")
        job = review_job.validate_captured_result(job, 4, live())
        self.assertEqual(job["outcome"], "FINDINGS")

        bad = result_identity(job, status="FINDINGS", findings=0)
        with self.assertRaises(review_job.ReviewJobValidationError):
            review_job.validate_result_identity(job, bad)

    def test_pass_with_nonzero_findings_is_rejected(self):
        job = advance_to_reviewing()
        bad = result_identity(job, status="PASS", findings=1)
        with self.assertRaises(review_job.ReviewJobValidationError):
            review_job.capture_result(job, 3, bad, "bad result")

    def test_wrong_job_head_policy_or_job_id_fails_closed(self):
        for field, value in (
            ("job_id", "rj_" + "f" * 32),
            ("head_sha", MOVED_HEAD),
            ("review_policy_ref", MOVED_HEAD),
        ):
            with self.subTest(field=field):
                job = advance_to_reviewing()
                identity = result_identity(job)
                identity[field] = value
                with self.assertRaises(review_job.ReviewJobIdentityError):
                    review_job.capture_result(job, 3, identity, "wrong identity")

    def test_repeated_identical_result_is_noop_conflicting_result_is_rejected(self):
        job = advance_to_reviewing()
        identity = result_identity(job)
        captured = review_job.capture_result(job, 3, identity, "same result")
        repeated = review_job.capture_result(
            captured,
            captured["revision"],
            identity,
            "same result",
        )
        self.assertEqual(repeated, captured)

        with self.assertRaises(review_job.ReviewJobConflictError):
            review_job.capture_result(
                captured,
                captured["revision"],
                identity,
                "different bytes",
            )

    def test_live_head_move_after_pass_forces_stale(self):
        job = advance_to_reviewing()
        identity = result_identity(job)
        job = review_job.capture_result(job, 3, identity, "pass on old head")
        job = review_job.validate_captured_result(job, 4, live(head=MOVED_HEAD))
        self.assertEqual(job["outcome"], "STALE")
        self.assertEqual(job["outcome_code"], "SOURCE_IDENTITY_MOVED_AFTER_RESULT")

    def test_reviewer_reported_stale_and_abstain_are_preserved(self):
        for validity, status, code in (
            ("STALE", "PASS", "REVIEWER_REPORTED_STALE"),
            ("ABSTAIN", "ABSTAIN", "REVIEWER_ABSTAIN"),
        ):
            with self.subTest(validity=validity):
                job = advance_to_reviewing()
                identity = result_identity(
                    job,
                    validity=validity,
                    status=status,
                    findings=0,
                )
                job = review_job.capture_result(job, 3, identity, validity)
                job = review_job.validate_captured_result(job, 4, live())
                self.assertEqual(job["outcome"], validity)
                self.assertEqual(job["outcome_code"], code)


class ReviewJobPublicationAndReturnTests(unittest.TestCase):
    def test_head_move_between_result_validation_and_publication_reclassifies_stale(self):
        job = advance_to_result_validated()
        job = review_job.claim_publication(
            job,
            job["revision"],
            "publish-0001",
            live(head=MOVED_HEAD),
        )
        self.assertEqual(job["state"], "PUBLICATION_CLAIMED")
        self.assertEqual(job["outcome"], "STALE")
        self.assertEqual(
            job["outcome_code"],
            "SOURCE_IDENTITY_MOVED_BEFORE_PUBLICATION",
        )

    def test_head_move_after_publication_before_return_reclassifies_stale(self):
        job = advance_to_result_validated()
        job = review_job.claim_publication(
            job,
            job["revision"],
            "publish-0001",
            live(),
        )
        job = review_job.record_publication(
            job,
            job["revision"],
            "publish-0001",
            "https://github.com/BogdanAIP/MimiSeek-review/issues/200#issuecomment-2000",
            job["result_sha256"],
        )
        job = review_job.claim_return_delivery(
            job,
            job["revision"],
            "return-0001",
            live(head=MOVED_HEAD),
        )
        self.assertEqual(job["state"], "RETURN_PENDING")
        self.assertEqual(job["outcome"], "STALE")
        self.assertEqual(
            job["outcome_code"],
            "SOURCE_IDENTITY_MOVED_BEFORE_RETURN",
        )

    def test_end_to_end_local_state_flow_reaches_done_once(self):
        job = advance_to_result_validated()
        job = review_job.claim_publication(job, 5, "publish-0001", live())
        job = review_job.record_publication(
            job,
            6,
            "publish-0001",
            "https://github.com/BogdanAIP/MimiSeek-review/issues/200#issuecomment-2000",
            job["result_sha256"],
        )
        job = review_job.claim_return_delivery(job, 7, "return-0001", live())
        job = review_job.record_return_delivered(
            job,
            8,
            "return-0001",
            "https://github.com/BogdanAIP/MimiSeek-review/issues/200#issuecomment-2001",
        )
        job = review_job.complete_job(job, 9)
        self.assertEqual(job["state"], "DONE")
        self.assertEqual(job["revision"], 10)

        repeated = review_job.complete_job(job, job["revision"])
        self.assertEqual(repeated, job)

    def test_ambiguous_publication_requires_reconciliation_before_retry(self):
        job = advance_to_result_validated()
        job = review_job.claim_publication(job, 5, "publish-0001", live())
        job = review_job.mark_publication_unknown(job, 6, "publish-0001")

        with self.assertRaises(review_job.ReviewJobTransitionError):
            review_job.claim_publication(
                job,
                job["revision"],
                "publish-0001",
                live(),
            )

        job = review_job.resolve_publication_absent(
            job,
            job["revision"],
            "publish-0001",
        )
        job = review_job.claim_publication(
            job,
            job["revision"],
            "publish-0001",
            live(),
        )
        self.assertEqual(job["state"], "PUBLICATION_CLAIMED")

    def test_ambiguous_publication_can_reconcile_to_exact_result(self):
        job = advance_to_result_validated()
        job = review_job.claim_publication(job, 5, "publish-0001", live())
        job = review_job.mark_publication_unknown(job, 6, "publish-0001")
        job = review_job.record_publication(
            job,
            job["revision"],
            "publish-0001",
            "https://github.com/BogdanAIP/MimiSeek-review/issues/200#issuecomment-2000",
            job["result_sha256"],
        )
        self.assertEqual(job["state"], "RESULT_PERSISTED")

    def test_wrong_published_digest_fails_closed(self):
        job = advance_to_result_validated()
        job = review_job.claim_publication(job, 5, "publish-0001", live())
        with self.assertRaises(review_job.ReviewJobConflictError):
            review_job.record_publication(
                job,
                6,
                "publish-0001",
                "https://github.com/BogdanAIP/MimiSeek-review/issues/200#issuecomment-2000",
                "f" * 64,
            )

    def test_ambiguous_return_requires_reconciliation_before_retry(self):
        job = advance_to_result_validated()
        job = review_job.claim_publication(job, 5, "publish-0001", live())
        job = review_job.record_publication(
            job,
            6,
            "publish-0001",
            "https://github.com/BogdanAIP/MimiSeek-review/issues/200#issuecomment-2000",
            job["result_sha256"],
        )
        job = review_job.claim_return_delivery(job, 7, "return-0001", live())
        job = review_job.mark_return_unknown(job, 8, "return-0001")

        with self.assertRaises(review_job.ReviewJobTransitionError):
            review_job.claim_return_delivery(
                job,
                job["revision"],
                "return-0001",
                live(),
            )

        job = review_job.resolve_return_absent(
            job,
            job["revision"],
            "return-0001",
        )
        job = review_job.claim_return_delivery(
            job,
            job["revision"],
            "return-0001",
            live(),
        )
        self.assertEqual(job["state"], "RETURN_PENDING")

    def test_failure_is_explicit_and_can_be_persisted_and_returned(self):
        job = review_job.set_failure_outcome(
            make_job(),
            0,
            "EXECUTOR_UNAVAILABLE",
        )
        self.assertEqual(job["outcome"], "FAILED")
        self.assertEqual(job["outcome_code"], "EXECUTOR_UNAVAILABLE")
        self.assertIsNone(job["result_sha256"])

        job = review_job.claim_publication(job, 1, "publish-failure", live())
        job = review_job.record_publication(
            job,
            2,
            "publish-failure",
            "https://github.com/BogdanAIP/MimiSeek-review/issues/300#issuecomment-3000",
        )
        job = review_job.claim_return_delivery(job, 3, "return-failure", live())
        self.assertEqual(job["state"], "RETURN_PENDING")


class ReviewJobConcurrencyTests(unittest.TestCase):
    def test_stale_revision_is_rejected_before_mutation(self):
        job = review_job.validate_request(make_job(), 0, live())
        with self.assertRaises(review_job.ReviewJobRevisionConflict):
            review_job.claim_launch(job, 0, "launch-0001", live())

    def test_same_current_revision_noop_does_not_increment_revision(self):
        job = review_job.validate_request(make_job(), 0, live())
        repeated = review_job.validate_request(job, job["revision"], live())
        self.assertEqual(repeated["revision"], job["revision"])
        self.assertEqual(repeated, job)


if __name__ == "__main__":
    unittest.main()
