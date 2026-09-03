import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "bootstrap_commentary_result_ancestry",
    REPO_ROOT / "tools" / "verify_bootstrap_commentary_reconciliation.py",
)
commentary = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = commentary
SPEC.loader.exec_module(commentary)

SOURCE_MERGE = "050e4b267c4dd58df4326b66240700ad12707f19"
FOLLOW_HEAD = "09c58c4bc286a639662cd77432a54c3f08438ad7"
FOLLOW_MERGE = "e8bda851e9d810d0e007826693540ec1d4c71053"
FOLLOW_TREE = "9744231f9a332ff0e7d217f129e7722a8739f462"


class BootstrapCommentaryResultAncestryTests(unittest.TestCase):
    def test_canonical_result_commit_is_accepted_on_default_branch_ancestry(self):
        result = commentary.validate_default_branch_ancestry(
            {
                "status": "ahead",
                "base_commit": {"sha": FOLLOW_MERGE},
                "merge_base_commit": {"sha": FOLLOW_MERGE},
            },
            FOLLOW_MERGE,
            "follow-up resulting commit",
        )
        self.assertEqual(result["base_sha"], FOLLOW_MERGE)
        self.assertEqual(result["merge_base_sha"], FOLLOW_MERGE)

    def test_follow_head_cannot_substitute_for_result_commit(self):
        # This models the exact bypass from fresh review. The PR HEAD can satisfy
        # the older result predicates: same sole parent, same tree, same PR
        # association. Canonical default-branch ancestry is the independent
        # discriminator that must still reject it.
        alleged_result = {
            "sha": FOLLOW_HEAD,
            "parents": (SOURCE_MERGE,),
            "tree": FOLLOW_TREE,
            "associated_prs": {123},
        }
        self.assertEqual(alleged_result["parents"], (SOURCE_MERGE,))
        self.assertEqual(alleged_result["tree"], FOLLOW_TREE)
        self.assertIn(123, alleged_result["associated_prs"])

        with self.assertRaisesRegex(
            commentary.CommentaryProvenanceError,
            "not on canonical default-branch ancestry",
        ):
            commentary.validate_default_branch_ancestry(
                {
                    "status": "diverged",
                    "base_commit": {"sha": FOLLOW_HEAD},
                    "merge_base_commit": {"sha": SOURCE_MERGE},
                },
                FOLLOW_HEAD,
                "follow-up resulting commit",
            )

    def test_compare_must_be_bound_to_declared_result_sha(self):
        with self.assertRaisesRegex(
            commentary.CommentaryProvenanceError,
            "does not match declared commit",
        ):
            commentary.validate_default_branch_ancestry(
                {
                    "status": "ahead",
                    "base_commit": {"sha": FOLLOW_HEAD},
                    "merge_base_commit": {"sha": FOLLOW_MERGE},
                },
                FOLLOW_MERGE,
                "follow-up resulting commit",
            )


if __name__ == "__main__":
    unittest.main()
