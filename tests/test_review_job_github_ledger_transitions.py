import unittest

from tools import review_job_github_ledger as ledger
from tools import review_job_state

from test_review_job_github_ledger_hardening import FakeStateBackend, make_job, live


class LedgerPersistedTransitionFenceTests(unittest.TestCase):
    def test_first_durable_snapshot_cannot_skip_requested(self):
        backend = FakeStateBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        forged = make_job()
        forged["state"] = "VALIDATED"
        review_job_state.validate_job(forged)

        with self.assertRaisesRegex(
            ledger.ReviewJobLedgerConflictError,
            "first durable snapshot",
        ):
            book.persist_job(forged)

    def test_next_revision_cannot_skip_validation_before_launch_claim(self):
        backend = FakeStateBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        job = make_job()
        book.persist_job(job)

        forged = dict(job)
        forged["revision"] = 1
        forged["state"] = "LAUNCH_CLAIMED"
        forged["launch_claim_id"] = "launch-forged"
        review_job_state.validate_job(forged)

        with self.assertRaisesRegex(
            ledger.ReviewJobLedgerConflictError,
            "state transition is not allowed",
        ):
            book.persist_job(forged)

    def test_next_revision_cannot_jump_from_reviewing_to_done(self):
        backend = FakeStateBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        job = make_job()
        book.persist_job(job)
        job = review_job_state.validate_request(job, 0, live())
        book.persist_job(job)
        job = review_job_state.claim_launch(job, 1, "launch-0001", live())
        book.persist_job(job)
        job = review_job_state.mark_reviewing(
            job,
            2,
            "launch-0001",
            "private-execution",
        )
        book.persist_job(job)

        forged = dict(job)
        forged["revision"] = job["revision"] + 1
        forged["state"] = "DONE"
        forged["result_identity"] = {
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
            "validity": "CURRENT",
            "status": "PASS",
            "reported_findings": 0,
        }
        forged["result_sha256"] = "f" * 64
        forged["outcome"] = "PASS"
        forged["publication_claim_id"] = "publish-forged"
        forged["result_ref"] = (
            "https://github.com/BogdanAIP/MimiSeek-review/"
            "issues/1#issuecomment-1"
        )
        forged["return_delivery_id"] = "return-forged"
        forged["return_receipt_ref"] = (
            "https://github.com/BogdanAIP/MimiSeek-review/"
            "issues/1#issuecomment-2"
        )
        review_job_state.validate_job(forged)

        with self.assertRaisesRegex(
            ledger.ReviewJobLedgerConflictError,
            "state transition is not allowed",
        ):
            book.persist_job(forged)

    def test_normal_state_machine_transition_remains_persistable(self):
        backend = FakeStateBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        job = make_job()
        book.persist_job(job)
        validated = review_job_state.validate_request(job, 0, live())
        write = book.persist_job(validated)
        self.assertEqual(write.job, validated)


if __name__ == "__main__":
    unittest.main()
