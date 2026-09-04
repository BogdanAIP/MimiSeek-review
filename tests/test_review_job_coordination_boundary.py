import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class ReviewJobCoordinationBoundaryTests(unittest.TestCase):
    def test_accept_narrow_decision_is_explicit_and_partial(self) -> None:
        adr = _read("docs/decisions/0013-narrow-independent-review-job-coordination.md")
        self.assertIn("Decision: **ACCEPT_NARROW**", adr)
        self.assertIn("partially supersedes ADR 0006", adr)
        self.assertIn("consumers own their development/review/fix/merge workflow", adr)
        self.assertIn("review-job `PASS`", adr)
        self.assertIn(
            "neither consumer merge authority nor MimiSeek reviewer-candidate promotion/distribution authority",
            adr,
        )

    def test_canonical_owners_preserve_consumer_authority(self) -> None:
        product = _read("docs/PRODUCT.md")
        architecture = _read("docs/ARCHITECTURE.md")
        integration = _read("docs/INTEGRATION_CONTRACT.md")
        protocol = _read("docs/DEVELOPMENT_PROTOCOL.md")
        skill = _read(".agents/skills/mimiseek-run/SKILL.md")

        self.assertIn("does **not** own the normal development/fix/merge loop", product)
        self.assertIn("Consumer repositories own review readiness", architecture)
        self.assertIn("finding adjudication", integration)
        self.assertIn("consumer project authority and consequences remain outside MimiSeek", protocol)
        self.assertIn("merge a consumer PR because a reviewer returned `PASS`", skill)

    def test_transport_boundary_stays_generic_and_private(self) -> None:
        architecture = _read("docs/ARCHITECTURE.md")
        integration = _read("docs/INTEGRATION_CONTRACT.md")
        adr = _read("docs/decisions/0013-narrow-independent-review-job-coordination.md")

        self.assertIn("project-specific routing tables", architecture)
        self.assertIn(
            "must not require UV Studio, MimiSeek Review, chat-agent-platform, GitHub PR",
            architecture,
        )
        self.assertIn(
            "transport must not need CAP/UV/MimiSeek project semantics, GitHub PR semantics",
            integration,
        )
        self.assertIn("GitHub PR semantics", adr)
        self.assertIn("project-specific routing tables", adr)

        self.assertIn("must not expose a raw browser tab ID", architecture)
        self.assertIn("must never contain a raw browser tab identifier", integration)
        self.assertIn("source GitHub App remains read-only", integration)

    def test_track_r_local_foundation_is_real_but_overall_runtime_is_pending(self) -> None:
        roadmap = _read("docs/ROADMAP.md")
        current = _read("docs/CURRENT_STATE.md")
        skill = _read(".agents/skills/mimiseek-run/SKILL.md")

        self.assertIn(
            "Track R — Independent review-job coordination — AUTHORIZED, IMPLEMENTATION PENDING",
            roadmap,
        )
        self.assertIn(
            "Review-job local foundation: `REVIEW_JOB_V1` public schema/state-machine/validation implemented; durable GitHub ledger/publication adapter and external CAP/session integration remain pending",
            current,
        )
        self.assertIn(
            "do not pretend external CAP/session prerequisites are already accepted",
            skill,
        )
        self.assertIn(
            "live external launch/wake remains blocked until separately accepted/verified generic external session capabilities are resolved",
            current,
        )

    def test_review_job_and_reviewer_evolution_authorities_remain_separate(self) -> None:
        product = _read("docs/PRODUCT.md")
        roadmap = _read("docs/ROADMAP.md")
        integration = _read("docs/INTEGRATION_CONTRACT.md")

        self.assertIn(
            "A review-job `PASS` is neither consumer merge authority nor MimiSeek reviewer-promotion authority",
            product,
        )
        self.assertIn("does not make any reviewer-evolution stage complete", roadmap)
        self.assertIn(
            "A job `PASS` cannot advance `mimiseek_stable` or `consumer_installed`",
            integration,
        )


if __name__ == "__main__":
    unittest.main()
