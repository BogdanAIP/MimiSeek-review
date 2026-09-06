from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1] / "tools" / "verify_development_finding_authority.py"
spec = importlib.util.spec_from_file_location("authority_supplements", P)
a = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(a)


class FindingSupplementTests(unittest.TestCase):
    def test_finding_records_reads_every_configured_supplement(self) -> None:
        original_specs = a.SUPPLEMENTS
        original_finding = a.finding_manifest
        original_supplement = a.supplement_manifest
        try:
            a.SUPPLEMENTS = (("one",), ("two",))
            a.finding_manifest = lambda get: [{"adjudication_id": "base"}]
            a.supplement_manifest = lambda get, spec: [{"adjudication_id": spec[0]}]
            rows = a.finding_records(lambda _: {})
            self.assertEqual(
                [row["adjudication_id"] for row in rows],
                ["base", "one", "two"],
            )
        finally:
            a.SUPPLEMENTS = original_specs
            a.finding_manifest = original_finding
            a.supplement_manifest = original_supplement


if __name__ == "__main__":
    unittest.main()
