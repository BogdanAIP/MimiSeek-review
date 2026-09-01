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
    def test_regression_cases_resolve_to_the_same_semantic_finding(self) -> None:
        finding_columns = load_columns("finding-v1.schema.json")
        regression_columns = load_columns("regression-case-v1.schema.json")
        findings = load_jsonl(DATA / "findings.jsonl", finding_columns)
        cases = load_jsonl(DATA / "regression-cases.jsonl", regression_columns)
        findings_by_id = {str(row["finding_id"]): row for row in findings}

        self.assertEqual(len(findings), len(findings_by_id), "finding ids must be unique")

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
                self.assertEqual("CONFIRMED", finding["confirmed"])

                basis = case["codex_basis"]
                if isinstance(basis, str) and basis.startswith("Direct Codex finding "):
                    self.assertIn(
                        f"Direct Codex finding {finding_id} ",
                        basis,
                        "direct-finding prose must agree with the canonical finding id",
                    )

    def test_bootstrap_report_dataset_digests_match_canonical_files(self) -> None:
        report = json.loads((DATA / "bootstrap-import-report.json").read_text(encoding="utf-8"))
        for filename, metadata in report["datasets"].items():
            with self.subTest(filename=filename):
                raw = (DATA / filename).read_bytes()
                self.assertEqual(len(raw), metadata["bytes"])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), metadata["sha256"])


if __name__ == "__main__":
    unittest.main()
