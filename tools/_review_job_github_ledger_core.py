from __future__ import annotations

import base64
import hashlib
import json
import socket
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from tools import review_job_state


LEDGER_SCHEMA = "REVIEW_JOB_LEDGER_V1"
OUTCOME_SCHEMA = "REVIEW_JOB_OUTCOME_V1"
DEFAULT_LEDGER_BRANCH = "mimiseek-review-jobs-v1"
LEDGER_ROOT = "review-jobs/v1"
LEDGER_MARKER_PATH = f"{LEDGER_ROOT}/ledger.json"
MAX_HTTP_BYTES = 2_000_000

RESULT_OR_LATER_STATES = {
    "RESULT_PERSISTED",
    "RETURN_PENDING",
    "RETURN_UNKNOWN",
    "RETURN_DELIVERED",
    "DONE",
}


class ReviewJobLedgerError(RuntimeError):
    pass


class ReviewJobLedgerValidationError(ReviewJobLedgerError):
    pass


class ReviewJobLedgerConflictError(ReviewJobLedgerError):
    pass


class ReviewJobLedgerAmbiguousWrite(ReviewJobLedgerError):
    """A mutating GitHub request may or may not have taken effect."""


@dataclass(frozen=True)
class LedgerFile:
    text: str
    blob_sha: str


@dataclass(frozen=True)
class LedgerWrite:
    head_sha: str
    job: dict[str, Any]
    changed: bool


@dataclass(frozen=True)
class PublicationReconciliation:
    status: str
    head_sha: str
    job: dict[str, Any]

    def __post_init__(self) -> None:
        if self.status not in {"PERSISTED", "ABSENT_PROVEN"}:
            raise ValueError("invalid publication reconciliation status")


class ReviewJobLedgerBackend(Protocol):
    repository: str

    def read_ref(self, branch: str) -> str | None: ...

    def read_commit_tree(self, commit_sha: str) -> str: ...

    def read_text(self, path: str, ref: str) -> LedgerFile | None: ...

    def create_blob(self, text: str) -> str: ...

    def create_tree(
        self,
        *,
        base_tree_sha: str | None,
        entries: Mapping[str, str],
    ) -> str: ...

    def create_commit(
        self,
        *,
        message: str,
        tree_sha: str,
        parent_sha: str | None,
    ) -> str: ...

    def create_ref(self, branch: str, commit_sha: str) -> None: ...

    def update_ref(self, branch: str, commit_sha: str) -> None: ...


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ReviewJobLedgerValidationError(f"{label} must be non-empty text")
    return value


def _require_git_sha(value: Any, label: str) -> str:
    value = _require_text(value, label)
    if len(value) != 40 or any(ch not in "0123456789abcdef" for ch in value):
        raise ReviewJobLedgerValidationError(f"{label} must be a 40-hex Git object id")
    return value


def _job_dir(job_id: str) -> str:
    if not isinstance(job_id, str) or not job_id.startswith("rj_"):
        raise ReviewJobLedgerValidationError("invalid review job id")
    if len(job_id) != 35:
        raise ReviewJobLedgerValidationError("invalid review job id")
    suffix = job_id[3:]
    if any(ch not in "0123456789abcdef" for ch in suffix):
        raise ReviewJobLedgerValidationError("invalid review job id")
    return f"{LEDGER_ROOT}/jobs/{job_id}"


def _job_path(job_id: str) -> str:
    return f"{_job_dir(job_id)}/job.json"


def _result_path(job_id: str) -> str:
    return f"{_job_dir(job_id)}/review-result.json"


def _outcome_path(job_id: str) -> str:
    return f"{_job_dir(job_id)}/outcome.json"


def _blob_ref(repository: str, blob_sha: str) -> str:
    quoted_repo = "/".join(
        urllib.parse.quote(part, safe="") for part in repository.split("/", 1)
    )
    return f"https://api.github.com/repos/{quoted_repo}/git/blobs/{blob_sha}"


def _marker_text(repository: str) -> str:
    return _canonical(
        {
            "schema": LEDGER_SCHEMA,
            "repository": repository,
            "root": LEDGER_ROOT,
            "version": 1,
        }
    ) + "\n"


def _outcome_text(job: Mapping[str, Any]) -> str:
    current = review_job_state.validate_job(job)
    if current["result_identity"] is not None or current["result_sha256"] is not None:
        raise ReviewJobLedgerValidationError(
            "outcome artifact is only for jobs without captured reviewer result bytes"
        )
    if current["outcome"] not in {"STALE", "FAILED"}:
        raise ReviewJobLedgerValidationError(
            "result-less publication requires STALE or FAILED outcome"
        )
    return _canonical(
        {
            "schema": OUTCOME_SCHEMA,
            "job_id": current["job_id"],
            "identity_sha256": current["identity_sha256"],
            "repository": current["repository"],
            "pr_number": current["pr_number"],
            "base_sha": current["base_sha"],
            "head_sha": current["head_sha"],
            "review_policy_ref": current["review_policy_ref"],
            "revision": current["revision"],
            "publication_claim_id": current["publication_claim_id"],
            "outcome": current["outcome"],
            "outcome_code": current["outcome_code"],
        }
    ) + "\n"


class ReviewJobGitHubLedger:
    """Durable MimiSeek-owned review-job ledger over an isolated GitHub branch.

    Every visible state mutation is a non-force branch update whose parent is the
    branch head observed immediately before the write. GitHub's fast-forward rule
    therefore provides the branch-level CAS fence. Exact reviewer result bytes are
    stored as a Git blob referenced by the same tree commit as the RESULT_PERSISTED
    job snapshot. The public REVIEW_JOB_V1 stores only the immutable blob API URL.
    """

    def __init__(
        self,
        backend: ReviewJobLedgerBackend,
        *,
        branch: str = DEFAULT_LEDGER_BRANCH,
    ) -> None:
        self.backend = backend
        self.repository = _require_text(backend.repository, "repository")
        self.branch = _require_text(branch, "ledger branch")

    def ensure_initialized(self) -> str:
        head = self.backend.read_ref(self.branch)
        if head is not None:
            self._validate_marker(head)
            return head

        marker_blob = self.backend.create_blob(_marker_text(self.repository))
        root_tree = self.backend.create_tree(
            base_tree_sha=None,
            entries={LEDGER_MARKER_PATH: marker_blob},
        )
        root_commit = self.backend.create_commit(
            message="review-job ledger v1: initialize",
            tree_sha=root_tree,
            parent_sha=None,
        )
        try:
            self.backend.create_ref(self.branch, root_commit)
        except ReviewJobLedgerConflictError:
            head = self.backend.read_ref(self.branch)
            if head is None:
                raise
            self._validate_marker(head)
            return head
        except ReviewJobLedgerAmbiguousWrite:
            head = self.backend.read_ref(self.branch)
            if head is None:
                raise
            self._validate_marker(head)
            return head
        self._validate_marker(root_commit)
        return root_commit

    def _validate_marker(self, ref: str) -> None:
        marker = self.backend.read_text(LEDGER_MARKER_PATH, ref)
        if marker is None or marker.text != _marker_text(self.repository):
            raise ReviewJobLedgerValidationError(
                "ledger branch marker is missing or belongs to another ledger"
            )

    def load_job(self, job_id: str, *, ref: str | None = None) -> dict[str, Any] | None:
        head = ref or self.ensure_initialized()
        file = self.backend.read_text(_job_path(job_id), head)
        if file is None:
            return None
        try:
            job = review_job_state.deserialize_job(file.text)
        except review_job_state.ReviewJobError as exc:
            raise ReviewJobLedgerValidationError(
                "persisted ledger job is not a valid REVIEW_JOB_V1"
            ) from exc
        if job["job_id"] != job_id:
            raise ReviewJobLedgerValidationError("ledger path/job_id mismatch")
        return job

    def persist_job(
        self,
        value: Mapping[str, Any],
        *,
        max_definite_conflict_retries: int = 2,
    ) -> LedgerWrite:
        desired = review_job_state.validate_job(value)
        desired_text = review_job_state.serialize_job(desired)

        for attempt in range(max_definite_conflict_retries + 1):
            head = self.ensure_initialized()
            existing_file = self.backend.read_text(_job_path(desired["job_id"]), head)
            existing = None
            if existing_file is not None:
                try:
                    existing = review_job_state.deserialize_job(existing_file.text)
                except review_job_state.ReviewJobError as exc:
                    raise ReviewJobLedgerValidationError(
                        "persisted ledger job is invalid"
                    ) from exc
                self._check_identity(existing, desired)
                if existing_file.text == desired_text:
                    return LedgerWrite(head, existing, False)
                if desired["revision"] == existing["revision"]:
                    raise ReviewJobLedgerConflictError(
                        "same ledger revision has different content"
                    )
                if desired["revision"] != existing["revision"] + 1:
                    raise ReviewJobLedgerConflictError(
                        "ledger job revision must advance exactly one step"
                    )
            elif desired["revision"] != 0:
                raise ReviewJobLedgerConflictError(
                    "first persisted job snapshot must be revision 0"
                )

            desired_blob = self.backend.create_blob(desired_text)
            try:
                new_head = self._commit_entries(
                    parent=head,
                    message=(
                        f"review-job {desired['job_id']}: "
                        f"persist revision {desired['revision']}"
                    ),
                    entries={_job_path(desired["job_id"]): desired_blob},
                )
                return LedgerWrite(new_head, desired, True)
            except ReviewJobLedgerConflictError:
                if attempt >= max_definite_conflict_retries:
                    raise
                continue
            except ReviewJobLedgerAmbiguousWrite:
                observed_head = self.backend.read_ref(self.branch)
                if observed_head is not None:
                    observed_file = self.backend.read_text(
                        _job_path(desired["job_id"]), observed_head
                    )
                    if observed_file is not None and observed_file.text == desired_text:
                        return LedgerWrite(observed_head, desired, True)
                raise

        raise AssertionError("unreachable")

    def publish_result(
        self,
        value: Mapping[str, Any],
        *,
        expected_revision: int,
        claim_id: str,
        raw_result_text: str | None,
    ) -> LedgerWrite:
        current = review_job_state.validate_job(value)
        if current["state"] != "PUBLICATION_CLAIMED":
            raise review_job_state.ReviewJobTransitionError(
                "publication side effect requires PUBLICATION_CLAIMED"
            )
        if current["revision"] != expected_revision:
            raise review_job_state.ReviewJobRevisionConflict(
                f"expected revision {expected_revision}, found {current['revision']}"
            )
        head = self.ensure_initialized()
        self._require_exact_persisted_job(head, current)

        artifact_text, artifact_path, observed_digest = self._publication_artifact(
            current, raw_result_text
        )
        artifact_blob = self.backend.create_blob(artifact_text)
        result_ref = _blob_ref(self.repository, artifact_blob)
        persisted = review_job_state.record_publication(
            current,
            expected_revision,
            claim_id,
            result_ref,
            observed_digest,
        )
        job_blob = self.backend.create_blob(review_job_state.serialize_job(persisted))
        entries = {
            artifact_path: artifact_blob,
            _job_path(current["job_id"]): job_blob,
        }

        try:
            new_head = self._commit_entries(
                parent=head,
                message=f"review-job {current['job_id']}: persist result",
                entries=entries,
            )
            return LedgerWrite(new_head, persisted, True)
        except ReviewJobLedgerConflictError:
            return self._reconcile_after_definite_publication_conflict(
                current=current,
                persisted=persisted,
                artifact_path=artifact_path,
                artifact_blob=artifact_blob,
            )
        except ReviewJobLedgerAmbiguousWrite:
            return self._fence_ambiguous_publication(
                current=current,
                persisted=persisted,
                artifact_path=artifact_path,
                artifact_blob=artifact_blob,
                claim_id=claim_id,
            )

    def reconcile_publication(
        self,
        value: Mapping[str, Any],
        *,
        expected_revision: int,
        claim_id: str,
        raw_result_text: str | None,
    ) -> PublicationReconciliation:
        current = review_job_state.validate_job(value)
        if current["state"] != "PUBLICATION_UNKNOWN":
            raise review_job_state.ReviewJobTransitionError(
                "publication reconciliation requires PUBLICATION_UNKNOWN"
            )
        if current["revision"] != expected_revision:
            raise review_job_state.ReviewJobRevisionConflict(
                f"expected revision {expected_revision}, found {current['revision']}"
            )
        head = self.ensure_initialized()
        stored = self.load_job(current["job_id"], ref=head)
        if stored is None:
            raise ReviewJobLedgerConflictError(
                "ledger job disappeared during reconciliation"
            )
        self._check_identity(stored, current)

        artifact_text, artifact_path, observed_digest = self._publication_artifact(
            current, raw_result_text
        )
        artifact_blob = self.backend.create_blob(artifact_text)
        expected_ref = _blob_ref(self.repository, artifact_blob)

        if stored["state"] in RESULT_OR_LATER_STATES:
            if stored["publication_claim_id"] != claim_id:
                raise ReviewJobLedgerConflictError("publication claim changed")
            if stored["result_ref"] != expected_ref:
                raise ReviewJobLedgerConflictError(
                    "persisted result locator conflicts with expected exact artifact"
                )
            self._verify_artifact(head, artifact_path, artifact_blob, artifact_text)
            if (
                current["result_sha256"] is not None
                and observed_digest != current["result_sha256"]
            ):
                raise ReviewJobLedgerConflictError("review result digest changed")
            return PublicationReconciliation("PERSISTED", head, stored)

        if stored != current:
            raise ReviewJobLedgerConflictError(
                "ledger state diverged from PUBLICATION_UNKNOWN reconciliation state"
            )
        if self.backend.read_text(artifact_path, head) is not None:
            raise ReviewJobLedgerConflictError(
                "publication artifact exists without matching persisted job state"
            )

        resolved = review_job_state.resolve_publication_absent(
            current, expected_revision, claim_id
        )
        write = self.persist_job(resolved)
        return PublicationReconciliation("ABSENT_PROVEN", write.head_sha, write.job)

    def _publication_artifact(
        self,
        current: Mapping[str, Any],
        raw_result_text: str | None,
    ) -> tuple[str, str, str | None]:
        if current["result_sha256"] is not None:
            if raw_result_text is None:
                raise ReviewJobLedgerValidationError(
                    "exact REVIEW_RESULT_V1 bytes are required for publication"
                )
            metadata, digest, _ = review_job_state.parse_result_payload(
                current, raw_result_text
            )
            if metadata != current["result_identity"]:
                raise ReviewJobLedgerConflictError(
                    "raw result metadata differs from captured result identity"
                )
            if digest != current["result_sha256"]:
                raise ReviewJobLedgerConflictError(
                    "raw result bytes differ from captured result digest"
                )
            return raw_result_text, _result_path(current["job_id"]), digest

        if raw_result_text is not None:
            raise ReviewJobLedgerValidationError(
                "raw reviewer result must be omitted for result-less outcome"
            )
        return _outcome_text(current), _outcome_path(current["job_id"]), None

    def _fence_ambiguous_publication(
        self,
        *,
        current: Mapping[str, Any],
        persisted: Mapping[str, Any],
        artifact_path: str,
        artifact_blob: str,
        claim_id: str,
    ) -> LedgerWrite:
        observed_head = self.backend.read_ref(self.branch)
        if observed_head is not None:
            observed = self.load_job(current["job_id"], ref=observed_head)
            if observed is not None and observed["state"] in RESULT_OR_LATER_STATES:
                if (
                    observed["publication_claim_id"] == claim_id
                    and observed["result_ref"] == persisted["result_ref"]
                ):
                    artifact = self.backend.read_text(artifact_path, observed_head)
                    if artifact is not None and artifact.blob_sha == artifact_blob:
                        return LedgerWrite(observed_head, observed, True)

        unknown = review_job_state.mark_publication_unknown(
            current, current["revision"], claim_id
        )
        try:
            write = self.persist_job(unknown)
        except ReviewJobLedgerAmbiguousWrite:
            final_head = self.backend.read_ref(self.branch)
            if final_head is not None:
                final = self.load_job(current["job_id"], ref=final_head)
                if final == unknown:
                    return LedgerWrite(final_head, unknown, True)
                if final is not None and final["state"] in RESULT_OR_LATER_STATES:
                    if (
                        final["publication_claim_id"] == claim_id
                        and final["result_ref"] == persisted["result_ref"]
                    ):
                        artifact = self.backend.read_text(artifact_path, final_head)
                        if artifact is not None and artifact.blob_sha == artifact_blob:
                            return LedgerWrite(final_head, final, True)
            raise
        except ReviewJobLedgerConflictError:
            final_head = self.ensure_initialized()
            final = self.load_job(current["job_id"], ref=final_head)
            if final == unknown:
                return LedgerWrite(final_head, unknown, True)
            if final is not None and final["state"] in RESULT_OR_LATER_STATES:
                if (
                    final["publication_claim_id"] == claim_id
                    and final["result_ref"] == persisted["result_ref"]
                ):
                    artifact = self.backend.read_text(artifact_path, final_head)
                    if artifact is not None and artifact.blob_sha == artifact_blob:
                        return LedgerWrite(final_head, final, True)
            raise
        return write

    def _reconcile_after_definite_publication_conflict(
        self,
        *,
        current: Mapping[str, Any],
        persisted: Mapping[str, Any],
        artifact_path: str,
        artifact_blob: str,
    ) -> LedgerWrite:
        head = self.ensure_initialized()
        observed = self.load_job(current["job_id"], ref=head)
        if observed is None:
            raise ReviewJobLedgerConflictError(
                "ledger job missing after publication conflict"
            )
        if (
            observed["state"] in RESULT_OR_LATER_STATES
            and observed["publication_claim_id"] == current["publication_claim_id"]
            and observed["result_ref"] == persisted["result_ref"]
        ):
            artifact = self.backend.read_text(artifact_path, head)
            if artifact is not None and artifact.blob_sha == artifact_blob:
                return LedgerWrite(head, observed, False)
        raise ReviewJobLedgerConflictError(
            "concurrent ledger publication does not match the exact requested result"
        )

    def _require_exact_persisted_job(
        self, head: str, current: Mapping[str, Any]
    ) -> None:
        file = self.backend.read_text(_job_path(current["job_id"]), head)
        if file is None:
            raise ReviewJobLedgerConflictError(
                "publication claim must be durable before publication side effect"
            )
        if file.text != review_job_state.serialize_job(current):
            raise ReviewJobLedgerConflictError(
                "ledger job does not exactly match publication claim state"
            )

    def _verify_artifact(
        self, ref: str, path: str, blob_sha: str, expected_text: str
    ) -> None:
        artifact = self.backend.read_text(path, ref)
        if (
            artifact is None
            or artifact.blob_sha != blob_sha
            or artifact.text != expected_text
        ):
            raise ReviewJobLedgerConflictError(
                "durable publication artifact does not match exact expected content"
            )

    def _check_identity(
        self, existing: Mapping[str, Any], desired: Mapping[str, Any]
    ) -> None:
        if existing["job_id"] != desired["job_id"]:
            raise ReviewJobLedgerConflictError("review job id changed")
        if existing["identity_sha256"] != desired["identity_sha256"]:
            raise ReviewJobLedgerConflictError("immutable review job identity changed")

    def _commit_entries(
        self,
        *,
        parent: str,
        message: str,
        entries: Mapping[str, str],
    ) -> str:
        tree_sha = self.backend.read_commit_tree(parent)
        new_tree = self.backend.create_tree(
            base_tree_sha=tree_sha,
            entries=entries,
        )
        commit = self.backend.create_commit(
            message=message,
            tree_sha=new_tree,
            parent_sha=parent,
        )
        self.backend.update_ref(self.branch, commit)
        return commit


class GitHubRestLedgerBackend:
    """Standard-library GitHub REST backend for the ledger adapter.

    The caller supplies a MimiSeek-owned token. No token is serialized into the
    review-job record or ledger branch.
    """

    def __init__(
        self,
        repository: str,
        token: str,
        *,
        api_base: str = "https://api.github.com",
        timeout: float = 30.0,
    ) -> None:
        self.repository = _require_text(repository, "repository")
        self.token = _require_text(token, "GitHub token")
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout

    def _url(self, suffix: str) -> str:
        owner, name = self.repository.split("/", 1)
        return (
            f"{self.api_base}/repos/"
            f"{urllib.parse.quote(owner, safe='')}/"
            f"{urllib.parse.quote(name, safe='')}{suffix}"
        )

    def _request(
        self,
        method: str,
        suffix: str,
        *,
        body: Mapping[str, Any] | None = None,
        not_found_none: bool = False,
        mutation: bool = False,
    ) -> Any:
        data = None
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "mimiseek-review-job-ledger-v1",
        }
        if body is not None:
            data = json.dumps(body, separators=(",", ":")).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            self._url(suffix),
            data=data,
            method=method,
            headers=headers,
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read(MAX_HTTP_BYTES + 1)
                if len(raw) > MAX_HTTP_BYTES:
                    raise ReviewJobLedgerValidationError(
                        "GitHub API response exceeded size limit"
                    )
                if not raw:
                    return None
                return json.loads(raw.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if not_found_none and exc.code == 404:
                return None
            if exc.code in {409, 422}:
                raise ReviewJobLedgerConflictError(
                    f"GitHub rejected CAS/write with HTTP {exc.code}"
                ) from exc
            raise ReviewJobLedgerError(
                f"GitHub API HTTP error {exc.code}"
            ) from exc
        except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
            if mutation:
                raise ReviewJobLedgerAmbiguousWrite(
                    "mutating GitHub request ended ambiguously"
                ) from exc
            raise ReviewJobLedgerError("GitHub API request failed") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ReviewJobLedgerValidationError(
                "GitHub API returned invalid JSON"
            ) from exc

    def read_ref(self, branch: str) -> str | None:
        quoted = urllib.parse.quote(branch, safe="")
        payload = self._request(
            "GET",
            f"/git/ref/heads/{quoted}",
            not_found_none=True,
        )
        if payload is None:
            return None
        return _require_git_sha(payload.get("object", {}).get("sha"), "ref sha")

    def read_commit_tree(self, commit_sha: str) -> str:
        payload = self._request("GET", f"/git/commits/{commit_sha}")
        return _require_git_sha(payload.get("tree", {}).get("sha"), "commit tree sha")

    def read_text(self, path: str, ref: str) -> LedgerFile | None:
        quoted_path = urllib.parse.quote(path, safe="/")
        quoted_ref = urllib.parse.quote(ref, safe="")
        payload = self._request(
            "GET",
            f"/contents/{quoted_path}?ref={quoted_ref}",
            not_found_none=True,
        )
        if payload is None:
            return None
        if payload.get("type") != "file" or payload.get("encoding") != "base64":
            raise ReviewJobLedgerValidationError(
                "ledger path is not a base64 GitHub file"
            )
        try:
            raw = base64.b64decode(payload["content"], validate=False)
            text = raw.decode("utf-8")
        except (KeyError, ValueError, UnicodeDecodeError) as exc:
            raise ReviewJobLedgerValidationError(
                "ledger file content is invalid"
            ) from exc
        return LedgerFile(
            text=text,
            blob_sha=_require_git_sha(payload.get("sha"), "blob sha"),
        )

    def create_blob(self, text: str) -> str:
        payload = self._request(
            "POST",
            "/git/blobs",
            body={"content": text, "encoding": "utf-8"},
            mutation=False,
        )
        return _require_git_sha(payload.get("sha"), "created blob sha")

    def create_tree(
        self,
        *,
        base_tree_sha: str | None,
        entries: Mapping[str, str],
    ) -> str:
        body: dict[str, Any] = {
            "tree": [
                {"path": path, "mode": "100644", "type": "blob", "sha": sha}
                for path, sha in sorted(entries.items())
            ]
        }
        if base_tree_sha is not None:
            body["base_tree"] = base_tree_sha
        payload = self._request("POST", "/git/trees", body=body, mutation=False)
        return _require_git_sha(payload.get("sha"), "created tree sha")

    def create_commit(
        self,
        *,
        message: str,
        tree_sha: str,
        parent_sha: str | None,
    ) -> str:
        body: dict[str, Any] = {
            "message": message,
            "tree": tree_sha,
            "parents": [],
        }
        if parent_sha is not None:
            body["parents"] = [parent_sha]
        payload = self._request(
            "POST",
            "/git/commits",
            body=body,
            mutation=False,
        )
        return _require_git_sha(payload.get("sha"), "created commit sha")

    def create_ref(self, branch: str, commit_sha: str) -> None:
        self._request(
            "POST",
            "/git/refs",
            body={"ref": f"refs/heads/{branch}", "sha": commit_sha},
            mutation=True,
        )

    def update_ref(self, branch: str, commit_sha: str) -> None:
        quoted = urllib.parse.quote(branch, safe="")
        self._request(
            "PATCH",
            f"/git/refs/heads/{quoted}",
            body={"sha": commit_sha, "force": False},
            mutation=True,
        )
