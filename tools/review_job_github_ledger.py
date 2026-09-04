from __future__ import annotations

from tools import _review_job_github_ledger_core as _core


MIMISEEK_LEDGER_REPOSITORY = "BogdanAIP/MimiSeek-review"

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


class ReviewJobGitHubLedger(_core.ReviewJobGitHubLedger):
    """Supported MimiSeek-owned durable review-job ledger boundary.

    The accepted Track R contract keeps authoritative coordination writes inside
    MimiSeek. A backend naming any consumer/source repository is rejected before
    the adapter can initialize or mutate a ledger branch.
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
        super().__init__(backend, branch=branch)


class GitHubRestLedgerBackend(_core.GitHubRestLedgerBackend):
    """GitHub REST backend permanently scoped to MimiSeek-owned publication.

    The two-argument compatibility form is accepted only when its repository is
    the exact MimiSeek repository; callers cannot use this supported backend to
    redirect ledger writes into a consumer/source repository.
    """

    def __init__(
        self,
        repository_or_token: str,
        token: str | None = None,
        *,
        api_base: str = "https://api.github.com",
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
            api_base=api_base,
            timeout=timeout,
        )
