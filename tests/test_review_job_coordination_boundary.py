from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_accept_narrow_decision_is_explicit_and_partial() -> None:
    adr = _read("docs/decisions/0013-narrow-independent-review-job-coordination.md")
    assert "Decision: **ACCEPT_NARROW**" in adr
    assert "partially supersedes ADR 0006" in adr
    assert "consumers own their development/review/fix/merge workflow" in adr
    assert "review-job `PASS`" in adr
    assert "neither consumer merge authority nor MimiSeek reviewer-candidate promotion/distribution authority" in adr


def test_canonical_owners_preserve_consumer_authority() -> None:
    product = _read("docs/PRODUCT.md")
    architecture = _read("docs/ARCHITECTURE.md")
    integration = _read("docs/INTEGRATION_CONTRACT.md")
    protocol = _read("docs/DEVELOPMENT_PROTOCOL.md")
    skill = _read(".agents/skills/mimiseek-run/SKILL.md")

    assert "does **not** own the normal development/fix/merge loop" in product
    assert "Consumer repositories own review readiness" in architecture
    assert "finding adjudication" in integration
    assert "consumer project authority and consequences remain outside MimiSeek" in protocol
    assert "merge a consumer PR because a reviewer returned `PASS`" in skill


def test_transport_boundary_stays_generic_and_private() -> None:
    architecture = _read("docs/ARCHITECTURE.md")
    integration = _read("docs/INTEGRATION_CONTRACT.md")
    adr = _read("docs/decisions/0013-narrow-independent-review-job-coordination.md")

    for text in (architecture, integration, adr):
        assert "project-specific routing tables" in text
        assert "GitHub PR semantics" in text

    assert "must not expose a raw browser tab ID" in architecture
    assert "must never contain a raw browser tab identifier" in integration
    assert "source GitHub App remains read-only" in integration


def test_track_r_is_authorized_but_runtime_is_still_pending() -> None:
    roadmap = _read("docs/ROADMAP.md")
    current = _read("docs/CURRENT_STATE.md")
    skill = _read(".agents/skills/mimiseek-run/SKILL.md")

    assert "Track R — Independent review-job coordination — AUTHORIZED, IMPLEMENTATION PENDING" in roadmap
    assert "Review-job coordination architecture: `ACCEPT_NARROW` selected by ADR 0013; MimiSeek runtime implementation remains pending" in current
    assert "do not pretend separately governed CAP/session capabilities are already accepted" in skill
    assert "no live external launch/wake integration until exact accepted generic CAP/session capabilities are independently resolved" in current


def test_review_job_and_reviewer_evolution_authorities_remain_separate() -> None:
    product = _read("docs/PRODUCT.md")
    roadmap = _read("docs/ROADMAP.md")
    integration = _read("docs/INTEGRATION_CONTRACT.md")

    assert "A review-job `PASS` is neither consumer merge authority nor MimiSeek reviewer-promotion authority" in product
    assert "does not make any reviewer-evolution stage complete" in roadmap
    assert "A job `PASS` cannot advance `mimiseek_stable` or `consumer_installed`" in integration
