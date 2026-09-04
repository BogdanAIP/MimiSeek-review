from __future__ import annotations

from typing import Any, Mapping

from tools import _review_job_github_ledger_core as _core
from tools import review_job_state


MIMISEEK_LEDGER_REPOSITORY = "BogdanAIP/MimiSeek-review"
CANONICAL_GITHUB_API_BASE = "https://api.github.com"

LEDGER_SCHEMA = _core.LEDGER_SCHEMA
OUTCOME_SCHEMA = _core.OUTCOME_SCHEMA
DEFAULT_LEDGER_BRANCH = _core.DEFAULT_LEDGER_BRANCH
LEDGER_ROOT = _core.LEDGER_ROOT
LEDGER_MARKER_PATH = _core.LEDGER_MARKER_PATH
MAX_HTTP_BYTES = _core.MAX_HTTP_BYTES
RESULT_OR_LATER_STATES = _core.RESULT_OR_LATER_STATES

ReviewJobLedgerError = _core.ReviewJobLedgerError
ReviewJobLedgerValidationError = _core.ReviewJobLedgerValidationError
ReviewJobLedgerConflictError = _core.ReviewJobLedgerConflictError
ReviewJobLedgerAmbiguousWrite = _core.ReviewJobLedgerAmbiguousWrite
LedgerFile = _core.LedgerFile
LedgerWrite = _core.LedgerWrite
PublicationReconciliation = _core.PublicationReconciliation
ReviewJobLedgerBackend = _core.ReviewJobLedgerBackend

_ALLOWED_PERSISTED_STATE_TRANSITIONS = {
    ("REQUESTED", "VALIDATED"),
    ("REQUESTED", "RESULT_VALIDATED"),
    ("VALIDATED", "LAUNCH_CLAIMED"),
    ("VALIDATED", "RESULT_VALIDATED"),
    ("LAUNCH_CLAIMED", "LAUNCH_UNKNOWN"),
    ("LAUNCH_CLAIMED", "REVIEWING"),
    ("LAUNCH_UNKNOWN", "VALIDATED"),
    ("LAUNCH_UNKNOWN", "REVIEWING"),
    ("REVIEWING", "RESULT_RECEIVED"),
    ("RESULT_RECEIVED", "RESULT_VALIDATED"),
    ("RESULT_VALIDATED", "PUBLICATION_CLAIMED"),
    ("PUBLICATION_CLAIMED", "PUBLICATION_UNKNOWN"),
    ("PUBLICATION_CLAIMED", "RESULT_PERSISTED"),
    ("PUBLICATION_UNKNOWN", "RESULT_VALIDATED"),
    ("PUBLICATION_UNKNOWN", "RESULT_PERSISTED"),
    ("RESULT_PERSISTED", "RETURN_PENDING"),
    ("RETURN_PENDING", "RETURN_UNKNOWN"),
    ("RETURN_PENDING", "RETURN_DELIVERED"),
    ("RETURN_UNKNOWN", "RETURN_PENDING"),
    ("RETURN_UNKNOWN", "RETURN_DELIVERED"),
    ("RETURN_DELIVERED", "DONE"),
}


class ReviewJobGitHubLedger(_core.ReviewJobGitHubLedger):
    """Supported MimiSeek-owned durable review-job ledger boundary.

    The facade adds invariants on top of the internal Git mechanics:
    authoritative writes are restricted to the MimiSeek repository and the
    canonical public GitHub API authority, and durable history cannot skip
    state-machine lifecycle states merely by presenting a separately valid
    future snapshot with the next revision number.
    """

    def __init__(
        self,
        backend: ReviewJobLedgerBackend,
        *,
        branch: str = DEFAULT_LEDGER_BRANCH,
    ) -> None:
        if backend.repository != MIMISEEK_LEDGER_REPOSITORY:
            raise ReviewJobLedgerValidationError(
                "review-job ledger backend must target the MimiSeek-owned repository"
            )
        backend_api_base = getattr(backend, "api_base", CANONICAL_GITHUB_API_BASE)
        if backend_api_base != CANONICAL_GITHUB_API_BASE:
            raise ReviewJobLedgerValidationError(
                "review-job ledger backend must use the canonical GitHub API authority"
            )
        super().__init__(backend, branch=branch)

    def persist_job(
        self,
        value: Mapping[str, Any],
        *,
        max_definite_conflict_retries: int = 2,
    ) -> LedgerWrite:
        desired = review_job_state.validate_job(value)
        head = self.ensure_initialized()
        existing = self.load_job(desired["job_id"], ref=head)

        if existing is None:
            if desired["revision"] != 0 or desired["state"] != "REQUESTED":
                raise ReviewJobLedgerConflictError(
                    "first durable snapshot must be REQUESTED at revision 0"
                )
        elif existing == desired:
            return LedgerWrite(head, existing, False)
        elif desired["revision"] == existing["revision"] + 1:
            transition = (existing["state"], desired["state"])
            if transition not in _ALLOWED_PERSISTED_STATE_TRANSITIONS:
                raise ReviewJobLedgerConflictError(
                    "durable review-job state transition is not allowed"
                )

        return super().persist_job(
            desired,
            max_definite_conflict_retries=max_definite_conflict_retries,
        )


class GitHubRestLedgerBackend(_core.GitHubRestLedgerBackend):
    """GitHub REST backend permanently scoped to canonical MimiSeek publication.

    The two-argument compatibility form is accepted only when its repository is
    the exact MimiSeek repository. The supported constructor intentionally does
    not expose the private core's ``api_base`` injection point: production
    credentials and writes always target ``https://api.github.com`` so the
    canonical result locator and the actual storage authority cannot diverge.
    """

    def __init__(
        self,
        repository_or_token: str,
        token: str | None = None,
        *,
        timeout: float = 30.0,
    ) -> None:
        if token is None:
            token = repository_or_token
        elif repository_or_token != MIMISEEK_LEDGER_REPOSITORY:
            raise ReviewJobLedgerValidationError(
                "GitHub ledger backend cannot target a non-MimiSeek repository"
            )
        super().__init__(
            MIMISEEK_LEDGER_REPOSITORY,
            token,
            api_base=CANONICAL_GITHUB_API_BASE,
            timeout=timeout,
        )
