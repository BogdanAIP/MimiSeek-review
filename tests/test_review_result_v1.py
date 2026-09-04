import hashlib
import json
import unittest
from pathlib import Path

from tools import review_job_state, review_result_v1

ROOT = Path(__file__).resolve().parents[1]
BASE = "a" * 40
HEAD = "b" * 40
LAUNCH_CAPABILITY = "d" * 40
RETURN_CAPABILITY = "e" * 40


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
        request_ref="https://github.com/BogdanAIP/MimiSeek-review/issues/100#issuecomment-1000",
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


def reviewing_job():
    job = make_job()
    job = review_job_state.validate_request(job, 0, live())
    job = review_job_state.claim_launch(job, 1, "launch-0001", live())
    return review_job_state.mark_reviewing(job, 2, "launch-0001", "private-execution-ref")


def payload(job, **overrides):
    value = {
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
        "report": "No actionable defect remains.",
    }
    value.update(overrides)
    return value


def raw(job, **overrides):
    return json.dumps(payload(job, **overrides), sort_keys=True, ensure_ascii=False) + "\n"


class ReviewResultV1Tests(unittest.TestCase):
    def test_valid_payload_derives_metadata_digest_and_report_from_same_bytes(self):
        job = reviewing_job()
        text = raw(job)
        metadata, digest, report = review_result_v1.parse_review_result_v1(job, text)
        self.assertEqual(metadata["status"], "PASS")
        self.assertEqual(metadata["head_sha"], HEAD)
        self.assertEqual(report, "No actionable defect remains.")
        self.assertEqual(digest, hashlib.sha256(text.encode("utf-8")).hexdigest())
        self.assertNotIn("report", metadata)

    def test_safe_capture_uses_parsed_metadata_and_exact_raw_digest(self):
        job = reviewing_job()
        text = raw(job, status="FINDINGS", reported_findings=2, report="Two findings.")
        captured = review_result_v1.capture_review_result_v1(job, 3, text)
        self.assertEqual(captured["result_identity"]["status"], "FINDINGS")
        self.assertEqual(captured["result_identity"]["reported_findings"], 2)
        self.assertEqual(captured["result_sha256"], hashlib.sha256(text.encode("utf-8")).hexdigest())
        self.assertNotIn("Two findings.", json.dumps(captured))

    def test_malformed_truncated_or_non_object_payload_fails_closed(self):
        job = reviewing_job()
        for text in ('{"schema":', '[]', '"REVIEW_RESULT_V1"'):
            with self.subTest(text=text):
                with self.assertRaises(review_job_state.ReviewJobValidationError):
                    review_result_v1.parse_review_result_v1(job, text)

    def test_duplicate_key_fails_closed(self):
        job = reviewing_job()
        text = raw(job).rstrip()
        text = text[:-1] + ',"status":"FINDINGS"}'
        with self.assertRaisesRegex(review_result_v1.ReviewResultParseError, "duplicate"):
            review_result_v1.parse_review_result_v1(job, text)

    def test_missing_extra_or_empty_report_fails_closed(self):
        job = reviewing_job()
        missing = payload(job)
        del missing["report"]
        extra = payload(job)
        extra["conversation_id"] = "private"
        empty = payload(job, report="   ")
        for value in (missing, extra, empty):
            with self.subTest(value=value):
                with self.assertRaises(review_job_state.ReviewJobValidationError):
                    review_result_v1.parse_review_result_v1(job, json.dumps(value))

    def test_wrong_job_head_policy_or_reviewer_binding_fails_from_raw_bytes(self):
        job = reviewing_job()
        cases = {
            "job_id": "rj_" + "f" * 32,
            "head_sha": "c" * 40,
            "review_policy_ref": "c" * 40,
            "reviewer_profile": "other-profile",
        }
        for field, value in cases.items():
            with self.subTest(field=field):
                with self.assertRaises(review_job_state.ReviewJobIdentityError):
                    review_result_v1.parse_review_result_v1(job, raw(job, **{field: value}))

    def test_status_count_invariants_are_enforced_on_raw_payload(self):
        job = reviewing_job()
        for overrides in (
            {"status": "PASS", "reported_findings": 1},
            {"status": "FINDINGS", "reported_findings": 0},
            {"validity": "ABSTAIN", "status": "PASS"},
            {"validity": "CURRENT", "status": "ABSTAIN"},
        ):
            with self.subTest(overrides=overrides):
                with self.assertRaises(review_job_state.ReviewJobValidationError):
                    review_result_v1.parse_review_result_v1(job, raw(job, **overrides))

    def test_worker_payload_schema_matches_parser_property_set(self):
        schema = json.loads((ROOT / "schemas" / "review-result-v1.schema.json").read_text(encoding="utf-8"))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["properties"]), review_result_v1.RAW_RESULT_KEYS)
        self.assertEqual(set(schema["required"]), review_result_v1.RAW_RESULT_KEYS)


if __name__ == "__main__":
    unittest.main()
