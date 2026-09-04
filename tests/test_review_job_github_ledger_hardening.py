import hashlib
import json
import unittest

from tools import review_job_github_ledger as ledger
from tools import review_job_state


BASE = "a" * 40
HEAD = "b" * 40


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
        launch_capability_ref="d" * 40,
        return_capability_ref="e" * 40,
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


class FakeStateBackend:
    repository = ledger.MIMISEEK_LEDGER_REPOSITORY

    def __init__(self):
        self.blobs = {}
        self.trees = {}
        self.commits = {}
        self.refs = {}
        self.next_update = None
        self.counter = 0

    def _sha(self, kind, value):
        return hashlib.sha1(f"{kind}:{value}".encode()).hexdigest()

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
        tree = dict(self.trees.get(base_tree_sha, {}))
        tree.update(entries)
        sha = self._sha("tree", json.dumps(tree, sort_keys=True))
        self.trees[sha] = tree
        return sha

    def create_commit(self, *, message, tree_sha, parent_sha):
        self.counter += 1
        sha = self._sha(
            "commit",
            json.dumps(
                {
                    "message": message,
                    "tree": tree_sha,
                    "parent": parent_sha,
                    "counter": self.counter,
                },
                sort_keys=True,
            ),
        )
        self.commits[sha] = {"tree": tree_sha, "parent": parent_sha}
        return sha

    def create_ref(self, branch, commit_sha):
        if branch in self.refs:
            raise ledger.ReviewJobLedgerConflictError("ref exists")
        self.refs[branch] = commit_sha

    def update_ref(self, branch, commit_sha):
        current = self.refs[branch]
        if self.commits[commit_sha]["parent"] != current:
            raise ledger.ReviewJobLedgerConflictError("non-fast-forward")
        mode = self.next_update
        self.next_update = None
        if mode == "ambiguous_applied":
            self.refs[branch] = commit_sha
            raise ledger.ReviewJobLedgerAmbiguousWrite("timeout after apply")
        if mode == "ambiguous_not_applied":
            raise ledger.ReviewJobLedgerAmbiguousWrite("timeout before apply")
        self.refs[branch] = commit_sha


class WrongRepositoryBackend:
    repository = "BogdanAIP/uv-studio"


class LedgerOwnershipTests(unittest.TestCase):
    def test_supported_ledger_rejects_consumer_repository_backend(self):
        with self.assertRaisesRegex(
            ledger.ReviewJobLedgerValidationError,
            "MimiSeek-owned repository",
        ):
            ledger.ReviewJobGitHubLedger(WrongRepositoryBackend())

    def test_supported_rest_backend_rejects_non_mimiseek_repository(self):
        with self.assertRaisesRegex(
            ledger.ReviewJobLedgerValidationError,
            "non-MimiSeek repository",
        ):
            ledger.GitHubRestLedgerBackend(
                "BogdanAIP/uv-studio",
                "token",
            )

    def test_supported_rest_backend_single_token_form_is_mimiseek_scoped(self):
        backend = ledger.GitHubRestLedgerBackend("token")
        self.assertEqual(backend.repository, ledger.MIMISEEK_LEDGER_REPOSITORY)


class LedgerOrdinaryWriteAmbiguityTests(unittest.TestCase):
    def test_ambiguous_applied_exact_state_is_reconciled_as_success(self):
        backend = FakeStateBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        job = make_job()
        book.persist_job(job)
        validated = review_job_state.validate_request(job, 0, live())

        backend.next_update = "ambiguous_applied"
        write = book.persist_job(validated)

        self.assertEqual(write.job, validated)
        self.assertEqual(book.load_job(job["job_id"]), validated)

    def test_ambiguous_not_applied_exact_state_can_be_retried_safely(self):
        backend = FakeStateBackend()
        book = ledger.ReviewJobGitHubLedger(backend)
        job = make_job()
        initial = book.persist_job(job)
        validated = review_job_state.validate_request(job, 0, live())

        backend.next_update = "ambiguous_not_applied"
        with self.assertRaises(ledger.ReviewJobLedgerAmbiguousWrite):
            book.persist_job(validated)

        self.assertEqual(backend.read_ref(book.branch), initial.head_sha)
        self.assertEqual(book.load_job(job["job_id"]), job)

        retried = book.persist_job(validated)
        self.assertEqual(retried.job, validated)
        self.assertEqual(book.load_job(job["job_id"]), validated)


if __name__ == "__main__":
    unittest.main()
