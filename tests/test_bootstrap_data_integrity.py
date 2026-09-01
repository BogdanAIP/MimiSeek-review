from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# Fixed Stage-1 bootstrap-v1 prefix anchor. These digests were derived from the
# authenticated version-1 workbook plus the independently adjudicated UV #70
# finding-link repair. Later operational records may be appended after these
# bootstrap prefixes, but changing an anchored prefix requires an explicit new
# reconciliation/version rather than silently editing the derived import report.
BOOTSTRAP_V1_PREFIX_ANCHOR = {
    "review-runs.jsonl": {
        "records": 92,
        "bytes": 25018,
        "sha256": "f841cac53f6fbd676b7128e4ecfc7684599eabfcc4409439654506a88d77e143",
    },
    "findings.jsonl": {
        "records": 139,
        "bytes": 45323,
        "sha256": "58d1756caf2c83cd92479577bb2e9e2fe22c884f49f8d08dc680747b32f10bcc",
    },
    "regression-cases.jsonl": {
        "records": 84,
        "bytes": 51522,
        "sha256": "7065aab04e1a83c344607e8047b399c35f12e6aff600c4bca168600b0c925bbf",
    },
}

DATASET_SCHEMAS = {
    "review-runs.jsonl": "review-run-v1.schema.json",
    "findings.jsonl": "finding-v1.schema.json",
    "regression-cases.jsonl": "regression-case-v1.schema.json",
}


def load_schema(schema_name: str) -> dict[str, object]:
    return json.loads((DATA / "schemas" / schema_name).read_text(encoding="utf-8"))


def load_columns(schema_name: str) -> list[str]:
    return list(load_schema(schema_name)["x-columns"])


def load_jsonl(path: Path, columns: list[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        value = json.loads(line)
        if len(value) != len(columns):
            raise AssertionError(f"{path.name}:{line_number} column count mismatch")
        rows.append(dict(zip(columns, value, strict=True)))
    return rows


def json_type_matches(value: object, expected_type: str) -> bool:
    if expected_type == "null":
        return value is None
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "object":
        return isinstance(value, dict)
    raise AssertionError(f"unsupported JSON Schema type in bootstrap validator: {expected_type}")


class BootstrapDataIntegrityTests(unittest.TestCase):
    def assert_schema_value(self, value: object, rule: dict[str, object], label: str) -> None:
        expected = rule.get("type")
        if expected is not None:
            expected_types = [expected] if isinstance(expected, str) else list(expected)
            self.assertTrue(
                any(json_type_matches(value, expected_type) for expected_type in expected_types),
                f"{label}: {value!r} does not match type {expected_types}",
            )

        enum = rule.get("enum")
        if enum is not None:
            self.assertIn(value, enum, f"{label}: {value!r} not in enum {enum!r}")

        pattern = rule.get("pattern")
        if pattern is not None and value is not None:
            self.assertIsInstance(value, str, f"{label}: pattern requires a string")
            self.assertIsNotNone(
                re.fullmatch(str(pattern), value),
                f"{label}: {value!r} does not match {pattern!r}",
            )

    def test_canonical_jsonl_rows_match_declared_schemas(self) -> None:
        for filename, schema_name in DATASET_SCHEMAS.items():
            schema = load_schema(schema_name)
            raw_rows = (DATA / filename).read_text(encoding="utf-8").splitlines()
            prefix_items = list(schema["prefixItems"])
            minimum = int(schema["minItems"])
            maximum = int(schema["maxItems"])

            for line_number, line in enumerate(raw_rows, start=1):
                with self.subTest(filename=filename, line_number=line_number):
                    row = json.loads(line)
                    self.assertIsInstance(row, list)
                    self.assertGreaterEqual(len(row), minimum)
                    self.assertLessEqual(len(row), maximum)
                    self.assertEqual(len(row), len(prefix_items))
                    for index, (value, rule) in enumerate(zip(row, prefix_items, strict=True)):
                        self.assert_schema_value(value, rule, f"{filename}:{line_number}[{index}]")

    def test_bootstrap_v1_prefix_matches_fixed_reconciliation_anchor(self) -> None:
        for filename, expected in BOOTSTRAP_V1_PREFIX_ANCHOR.items():
            with self.subTest(filename=filename):
                lines = (DATA / filename).read_bytes().splitlines(keepends=True)
                self.assertGreaterEqual(len(lines), expected["records"])
                anchored = b"".join(lines[: expected["records"]])
                self.assertEqual(len(anchored), expected["bytes"])
                self.assertEqual(hashlib.sha256(anchored).hexdigest(), expected["sha256"])

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
        self.assertEqual(expected_recorded_rejected_candidates, observed_recorded_rejected_candidates)

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
