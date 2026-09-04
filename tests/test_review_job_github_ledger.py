import hashlib
import json
import socket
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

from tools import review_job_github_ledger as ledger
from tools import review_job_state


BASE = "a" * 40
HEAD = "b" * 40
LAUNCH_CAPABILITY = "d" * 40
RETURN_CAPABILITY = "e" * 40
EXECUTION = "private-execution-a"
OTHER_EXECUTION = "private-execution-b"


def make_job():
    return review_job_state.create_job(
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


def live():
    return {
        "repository_id": 1352648898,
        "repository": "BogdanAIP/uv-studio",
        "pr_number": 89,
        "base_sha": BASE,
        "head_sha": HEAD,
        "state": "open",
        "draft": False,
        "merged": False,
    }


def raw_result(job, *, status="PASS", findings=0, report="No findings."):
    payload = {
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
        "status": status,
        "reported_findings": findings,
        "report": report,
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n"


class FakeLedgerBackend:
    repository = "BogdanAIP/MimiSeek-review"

    def __init__(self):
        self.blobs = {}
        self.trees = {}
        self.commits = {}
        self.refs = {}
        self.next_update = None
        self.commit_counter = 0

    def _sha(self, kind, value):
        return hashlib.sha1(f"{kind}:{value}".encode("utf-8")).hexdigest()

    def read_ref(self, branch):
        return self.refs.get(branch)

    def read_commit_tree(self, commit_sha):
        return self.commits[commit_sha]["tree"]

    def read_text(self, path, ref):
        commit_sha = self.refs.get(ref, ref)
        commit = self.commits.get(commit_sha)
        if commit is None:
            return None
        blob_sha = self.trees[commit["tree"]].get(path)
        if blob_sha is None:
            return None
        return ledger.LedgerFile(self.blobs[blob_sha], blob_sha)

    def create_blob(self, text):
        sha = self._sha("blob", text)
        self.blobs[sha] = text
        return sha

    def create_tree(self, *, base_tree_sha, entries):
        tree = {}
        if base_tree_sha is not None:
            tree.update(self.trees[base_tree_sha])
        tree.update(entries)
        serial = json.dumps(tree, sort_keys=True, separators=(",", ":"))
        sha = self._sha("tree", serial)
        self.trees[sha] = tree
        return sha

    def create_commit(self, *, message, tree_sha, parent_sha):
        self.commit_counter += 1
        serial = json.dumps(
            {
                "message": message,
                "tree": tree_sha,
                "parent": parent_sha,
                "nonce": self.commit_counter,
            },
            sort_keys=True,
        )
        sha = self._sha("commit", serial)
        self.commits[sha] = {
            "tree": tree_sha,
            "parent": parent_sha,
            "message": message,
        }
        return sha

    def create_ref(self, branch, commit_sha):
        if branch in self.refs:
            raise ledger.ReviewJobLedgerConflictError("ref exists")
        self.refs[branch] = commit_sha

    def update_ref(self, branch, commit_sha):
        mode = self.next_update
        self.next_update = None
        current = self.refs.get(branch)
        parent = self.commits[commit_sha]["parent"]
        if current != parent:
            raise ledger.ReviewJobLedgerConflictError("non-fast-forward")
        if mode == "ambiguous_applied":
            self.refs[branch] = commit_sha
            raise ledger.ReviewJobLedgerAmbiguousWrite("timeout after apply")
        if mode == "ambiguous_not_applied":
            raise ledger.ReviewJobLedgerAmbiguousWrite("timeout before apply")
        if mode == "definite_concurrent":
            tree = self.commits[current]["tree"]
            unrelated = self.create_commit(
                message="unrelated job",
                tree_sha=tree,
                parent_sha=current,
            )
            self.refs[branch] = unrelated
            raise ledger.ReviewJobLedgerConflictError("concurrent writer won")
        self.refs[branch] = commit_sha


def persist_to_publication_claim(book):
    job = make_job()
    book.persist_job(job)
    job = review_job_state.validate_request(job, job["revision"], live())
    book.persist_job(job)
    job = review_job_state.claim_launch(job, job["revision"], "launch-0001", live())
    book.persist_job(job)
    job = review_job_state.mark_reviewing(
        job, job["revision"], "launch-0001", EXECUTION
    )
    book.persist_job(job)
    raw = raw_result(job)
    job = review_job_state.capture_result(
        job, job["revision"], EXECUTION, raw
    )
    book.persist_job(job)
    job = review_job_state.validate_captured_result(job, job["revision"], live())
    book.persist_job(job)
    job = review_job_state.claim_publication(
        job, job["revision"], "publish-0001", live()
    )
    book.persist_job(job)
    return job, raw


class LedgerInitializationTests(unittest.TestCase):
    def test_initialization_is_isolated_and_idempotent(self):
        backend = FakeLedgerBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        first = book.ensure_initialized()
        second = book.ensure_initialized()
        self.assertEqual(first, second)
        marker = backend.read_text(ledger.LEDGER_MARKER_PATH, first)
        self.assertIsNotNone(marker)
        self.assertIn('"schema":"REVIEW_JOB_LEDGER_V1"', marker.text)
        self.assertEqual(
            set(backend.trees[backend.commits[first]["tree"]]),
            {ledger.LEDGER_MARKER_PATH},
        )

    def test_existing_wrong_branch_marker_fails_closed(self):
        backend = FakeLedgerBackend()
        marker_blob = backend.create_blob('{"schema":"OTHER"}\n')
        tree = backend.create_tree(
            base_tree_sha=None, entries={ledger.LEDGER_MARKER_PATH: marker_blob}
        )
        commit = backend.create_commit(message="wrong", tree_sha=tree, parent_sha=None)
        backend.create_ref(ledger.DEFAULT_LEDGER_BRANCH, commit)
        with self.assertRaises(ledger.ReviewJobLedgerValidationError):
            ledger.ReviewJobGitHubLedger(backend).ensure_initialized()


class LedgerStateTests(unittest.TestCase):
    def test_first_snapshot_must_be_revision_zero_and_transitions_are_exactly_one(self):
        backend = FakeLedgerBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        job = make_job()
        first = book.persist_job(job)
        self.assertTrue(first.changed)
        repeated = book.persist_job(job)
        self.assertFalse(repeated.changed)
        self.assertEqual(repeated.head_sha, first.head_sha)
        validated = review_job_state.validate_request(job, 0, live())
        written = book.persist_job(validated)
        self.assertEqual(written.job["revision"], 1)
        jumped = review_job_state.claim_launch(
            validated, validated["revision"], "launch-0001", live()
        )
        jumped = review_job_state.mark_launch_unknown(
            jumped, jumped["revision"], "launch-0001"
        )
        with self.assertRaisesRegex(ledger.ReviewJobLedgerConflictError, "exactly one"):
            book.persist_job(jumped)

    def test_same_revision_different_state_is_conflict(self):
        backend = FakeLedgerBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        job = make_job()
        book.persist_job(job)
        validated = review_job_state.validate_request(job, 0, live())
        book.persist_job(validated)
        launch_a = review_job_state.claim_launch(validated, 1, "launch-a", live())
        launch_b = review_job_state.claim_launch(validated, 1, "launch-b", live())
        book.persist_job(launch_a)
        with self.assertRaisesRegex(
            ledger.ReviewJobLedgerConflictError, "same ledger revision"
        ):
            book.persist_job(launch_b)

    def test_definite_global_branch_conflict_retries_without_overwrite(self):
        backend = FakeLedgerBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        job = make_job()
        book.persist_job(job)
        validated = review_job_state.validate_request(job, 0, live())
        backend.next_update = "definite_concurrent"
        written = book.persist_job(validated)
        self.assertEqual(written.job, validated)
        self.assertEqual(book.load_job(job["job_id"]), validated)


class LedgerPublicationTests(unittest.TestCase):
    def test_exact_result_and_result_persisted_state_commit_atomically(self):
        backend = FakeLedgerBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        job, raw = persist_to_publication_claim(book)
        written = book.publish_result(
            job,
            expected_revision=job["revision"],
            claim_id="publish-0001",
            raw_result_text=raw,
        )
        self.assertEqual(written.job["state"], "RESULT_PERSISTED")
        self.assertRegex(
            written.job["result_ref"],
            r"^https://api\.github\.com/repos/BogdanAIP/MimiSeek-review/git/blobs/[0-9a-f]{40}$",
        )
        result_file = backend.read_text(
            f"{ledger.LEDGER_ROOT}/jobs/{job['job_id']}/review-result.json",
            written.head_sha,
        )
        job_file = backend.read_text(
            f"{ledger.LEDGER_ROOT}/jobs/{job['job_id']}/job.json",
            written.head_sha,
        )
        self.assertEqual(result_file.text, raw)
        self.assertEqual(
            hashlib.sha256(result_file.text.encode("utf-8")).hexdigest(),
            job["result_sha256"],
        )
        self.assertEqual(job_file.text, review_job_state.serialize_job(written.job))

    def test_publication_rejects_non_exact_result_bytes(self):
        backend = FakeLedgerBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        job, raw = persist_to_publication_claim(book)
        changed = raw.replace("No findings.", "Different exact bytes.")
        with self.assertRaises(
            (ledger.ReviewJobLedgerConflictError, review_job_state.ReviewJobConflictError)
        ):
            book.publish_result(
                job,
                expected_revision=job["revision"],
                claim_id="publish-0001",
                raw_result_text=changed,
            )

    def test_publication_requires_claim_state_already_durable(self):
        backend = FakeLedgerBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        job = make_job()
        book.persist_job(job)
        job = review_job_state.validate_request(job, 0, live())
        book.persist_job(job)
        job = review_job_state.claim_launch(job, 1, "launch-0001", live())
        book.persist_job(job)
        job = review_job_state.mark_reviewing(job, 2, "launch-0001", EXECUTION)
        book.persist_job(job)
        raw = raw_result(job)
        job = review_job_state.capture_result(job, 3, EXECUTION, raw)
        book.persist_job(job)
        job = review_job_state.validate_captured_result(job, 4, live())
        book.persist_job(job)
        claimed_not_persisted = review_job_state.claim_publication(
            job, 5, "publish-0001", live()
        )
        with self.assertRaisesRegex(
            ledger.ReviewJobLedgerConflictError,
            "does not exactly match publication claim state",
        ):
            book.publish_result(
                claimed_not_persisted,
                expected_revision=claimed_not_persisted["revision"],
                claim_id="publish-0001",
                raw_result_text=raw,
            )

    def test_ambiguous_applied_write_reconciles_without_second_publication(self):
        backend = FakeLedgerBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        job, raw = persist_to_publication_claim(book)
        commits_before = backend.commit_counter
        backend.next_update = "ambiguous_applied"
        written = book.publish_result(
            job,
            expected_revision=job["revision"],
            claim_id="publish-0001",
            raw_result_text=raw,
        )
        self.assertEqual(written.job["state"], "RESULT_PERSISTED")
        self.assertEqual(book.load_job(job["job_id"]), written.job)
        self.assertEqual(backend.commit_counter, commits_before + 1)

    def test_ambiguous_not_applied_is_fenced_unknown_then_absence_is_proven(self):
        backend = FakeLedgerBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        job, raw = persist_to_publication_claim(book)
        backend.next_update = "ambiguous_not_applied"
        unknown_write = book.publish_result(
            job,
            expected_revision=job["revision"],
            claim_id="publish-0001",
            raw_result_text=raw,
        )
        unknown = unknown_write.job
        self.assertEqual(unknown["state"], "PUBLICATION_UNKNOWN")
        result_path = f"{ledger.LEDGER_ROOT}/jobs/{job['job_id']}/review-result.json"
        self.assertIsNone(backend.read_text(result_path, unknown_write.head_sha))
        with self.assertRaises(review_job_state.ReviewJobTransitionError):
            book.publish_result(
                unknown,
                expected_revision=unknown["revision"],
                claim_id="publish-0001",
                raw_result_text=raw,
            )
        reconciliation = book.reconcile_publication(
            unknown,
            expected_revision=unknown["revision"],
            claim_id="publish-0001",
            raw_result_text=raw,
        )
        self.assertEqual(reconciliation.status, "ABSENT_PROVEN")
        self.assertEqual(reconciliation.job["state"], "RESULT_VALIDATED")
        reclaimed = review_job_state.claim_publication(
            reconciliation.job,
            reconciliation.job["revision"],
            "publish-0001",
            live(),
        )
        book.persist_job(reclaimed)
        persisted = book.publish_result(
            reclaimed,
            expected_revision=reclaimed["revision"],
            claim_id="publish-0001",
            raw_result_text=raw,
        )
        self.assertEqual(persisted.job["state"], "RESULT_PERSISTED")

    def test_resultless_failure_publishes_bounded_outcome_artifact(self):
        backend = FakeLedgerBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        job = make_job()
        book.persist_job(job)
        failed = review_job_state.set_failure_outcome(
            job, job["revision"], "EXECUTOR_UNAVAILABLE"
        )
        book.persist_job(failed)
        claimed = review_job_state.claim_publication(
            failed, failed["revision"], "publish-failure", live()
        )
        book.persist_job(claimed)
        persisted = book.publish_result(
            claimed,
            expected_revision=claimed["revision"],
            claim_id="publish-failure",
            raw_result_text=None,
        )
        self.assertEqual(persisted.job["state"], "RESULT_PERSISTED")
        self.assertIsNone(persisted.job["result_sha256"])
        outcome_path = f"{ledger.LEDGER_ROOT}/jobs/{job['job_id']}/outcome.json"
        outcome = backend.read_text(outcome_path, persisted.head_sha)
        data = json.loads(outcome.text)
        self.assertEqual(data["schema"], "REVIEW_JOB_OUTCOME_V1")
        self.assertEqual(data["outcome"], "FAILED")
        self.assertEqual(data["outcome_code"], "EXECUTOR_UNAVAILABLE")
        self.assertEqual(data["publication_claim_id"], "publish-failure")
        self.assertNotIn("conversation_id", outcome.text)
        self.assertNotIn(EXECUTION, outcome.text)

    def test_outcome_schema_matches_bounded_resultless_artifact(self):
        schema = json.loads(
            Path("schemas/review-job-outcome-v1.schema.json").read_text(encoding="utf-8")
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            set(schema["required"]),
            {
                "schema",
                "job_id",
                "identity_sha256",
                "repository",
                "pr_number",
                "base_sha",
                "head_sha",
                "review_policy_ref",
                "revision",
                "publication_claim_id",
                "outcome",
                "outcome_code",
            },
        )


class RestBackendFailureClassificationTests(unittest.TestCase):
    def test_ref_update_timeout_is_ambiguous(self):
        backend = ledger.GitHubRestLedgerBackend(
            "BogdanAIP/MimiSeek-review", "secret-token"
        )
        with mock.patch(
            "urllib.request.urlopen", side_effect=socket.timeout("timeout")
        ):
            with self.assertRaises(ledger.ReviewJobLedgerAmbiguousWrite):
                backend.update_ref(ledger.DEFAULT_LEDGER_BRANCH, "f" * 40)

    def test_ref_update_422_is_definite_conflict(self):
        backend = ledger.GitHubRestLedgerBackend(
            "BogdanAIP/MimiSeek-review", "secret-token"
        )
        error = urllib.error.HTTPError(
            url="https://api.github.com/",
            code=422,
            msg="unprocessable",
            hdrs=None,
            fp=None,
        )
        with mock.patch("urllib.request.urlopen", side_effect=error):
            with self.assertRaises(ledger.ReviewJobLedgerConflictError):
                backend.update_ref(ledger.DEFAULT_LEDGER_BRANCH, "f" * 40)


if __name__ == "__main__":
    unittest.main()
