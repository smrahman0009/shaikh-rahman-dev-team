import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from team import Ledger, TeamError


class MetricsTests(unittest.TestCase):
    def test_outcomes_are_unknown_until_measured_and_duplicate_feedback_is_not_double_acceptance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "business_requirement.md").write_text("A scoped requirement", encoding="utf-8")
            ledger = Ledger(root)
            ledger.init(root / "business_requirement.md")
            self.assertIsNone(ledger.status()["metrics"]["acceptance_rate"])
            ledger.apply({"action": "task", "actor": "cto", "id": "t", "purpose": "Test", "approach": "Inspect", "owner_role": "dev", "critic_role": "reviewer", "profile": "software", "stage": "implementation", "acceptance": ["Works"], "files": ["out.txt"]})
            feedback = {"action": "feedback", "actor": "ceo", "task": "t", "accepted": False, "repeat_mistake": True, "human_minutes": 5, "source": "CEO measured review"}
            ledger.apply(feedback)
            ledger.apply(feedback | {"accepted": True, "repeat_mistake": False, "human_minutes": 2})
            metrics = ledger.status()["metrics"]
            self.assertEqual(metrics["acceptance_rate"], 1)
            self.assertEqual(metrics["reviewed_task_outcomes"], 1)
            self.assertEqual(metrics["human_review_minutes"], 7)
            self.assertEqual(metrics["repeat_mistakes_reported"], 1)
            self.assertIsNone(metrics["cost_per_accepted_task"])
            with self.assertRaises(TeamError):
                ledger.apply(feedback | {"human_minutes": float("nan")})


if __name__ == "__main__":
    unittest.main()
