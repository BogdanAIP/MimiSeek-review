from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load_columns(schema_name: str) -> list[str]:
    schema = json.loads((DATA / "schemas" / schema_name).read_text(encoding="utf-8"))
    return list(schema["x-columns"])


def load_jsonl(path: Path, columns: list[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        value = json.loads(line)
        if len(value) != len(columns):
            raise AssertionError(f"{path.name}:{line_number} column count mismatch")
        rows.append(dict(zip(columns, value, strict=True)))
    return rows


class BootstrapDataIntegrityTests(unittest.TestCase):
    def test_regression_cases_resolve_to_the_same_source_finding(self) -> None:
        finding_columns = load_columns("finding-v1.schema.json")
        regression_columns = load_columns("regression-case-v1.schema.json")
        findings = load_jsonl(DATA / "findings.jsonl", finding_columns)
        cases = load_jsonl(DATA / "regression-cases.jsonl", regression_columns)
        findings_by_id = {str(row["finding_id"]): row for row in findings}
        case_ids = [str(row["case_id"]) for row in cases]

        self.assertEqual(len(findings), len(findings_by_id), "finding ids must be unique")
        self.assertEqual(len(case_ids), len(set(case_ids)), "regression case ids must be unique")

        for case in cases:
            case_id = str(case["case_id"])
            finding_id = str(case["finding_id"])
            with self.subTest(case_id=case_id, finding_id=finding_id):
                self.assertIn(finding_id, findings_by_id)
                finding = findings_by_id[finding_id]
                self.assertEqual(case["repository"], finding["repository"])
                self.assertEqual(case["pr"], finding["pr"])
                self.assertEqual(case["severity"], finding["severity"])
                self.assertEqual(case["category"], finding["category"])
                self.assertEqual(case["known_defect"], finding["finding"])
                self.assertEqual(case["source_url"], finding["source_url"])
                self.assertEqual(case["historical_source_reviewer"], finding["reviewer"])
                self.assertEqual(case["buggy_head"], finding["head_sha"])
                self.assertEqual("CONFIRMED", finding["confirmed"])

                basis = case["codex_basis"]
                if isinstance(basis, str) and basis.startswith("Direct Codex finding "):
                    self.assertIn(
                        f"Direct Codex finding {finding_id} ",
                        basis,
                        "direct-finding prose must agree with the canonical finding id",
                    )

    def test_review_run_source_blanks_remain_unknown(self) -> None:
        columns = load_columns("review-run-v1.schema.json")
        runs = load_jsonl(DATA / "review-runs.jsonl", columns)
        runs_by_id = {str(row["run_id"]): row for row in runs}

        self.assertEqual(len(runs), len(runs_by_id), "review run ids must be unique")

        # These are the only Rejected candidates cells populated in the authenticated
        # bootstrap workbook. Explicit source zeroes for R009/R010 must remain zero;
        # all source blanks must remain null rather than being manufactured as zero.
        expected_recorded_rejected_candidates = {
            "R001": 3,
            "R002": 3,
            "R003": 5,
            "R004": 4,
            "R007": 9,
            "R009": 0,
            "R010": 0,
            "R022": 14,
        }
        observed_recorded_rejected_candidates = {
            str(row["run_id"]): row["rejected_candidates"]
            for row in runs
            if row["rejected_candidates"] is not None
        }
        self.assertEqual(
            expected_recorded_rejected_candidates,
            observed_recorded_rejected_candidates,
        )

        # R025 was not reconstructed in the source workbook, so no review-count
        # metric is known. R016 likewise has no reconstructed confirmed/rejected
        # disposition counts. Unknown source cells must stay null.
        for field in (
            "findings",
            "p1",
            "p2",
            "p3",
            "rejected_candidates",
            "confirmed_findings",
            "rejected_findings",
        ):
            self.assertIsNone(runs_by_id["R025"][field], field)
        self.assertIsNone(runs_by_id["R016"]["confirmed_findings"])
        self.assertIsNone(runs_by_id["R016"]["rejected_findings"])

    def test_bootstrap_report_dataset_digests_match_canonical_files(self) -> None:
        report = json.loads((DATA / "bootstrap-import-report.json").read_text(encoding="utf-8"))
        for filename, metadata in report["datasets"].items():
            with self.subTest(filename=filename):
                raw = (DATA / filename).read_bytes()
                self.assertEqual(len(raw), metadata["bytes"])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), metadata["sha256"])


if __name__ == "__main__":
    unittest.main()
