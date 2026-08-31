import unittest
from backend.evidence.mechanism_evidence import run_chaos_replanning_experiment
from backend.evidence.models import ReplanningEvidenceResult

class TestReplanningEffect(unittest.TestCase):
    def test_chaos_triggers_plan_invalidation_and_replan(self):
        """Experiment 5 Contract: Gateway health drop during WAIT forces wake-up replan."""
        result = run_chaos_replanning_experiment(customer_id="c_test_replan_unit")
        self.assertIsInstance(result, ReplanningEvidenceResult)
        self.assertTrue(result.plan_invalidated)
        self.assertGreaterEqual(result.replan_count, 1)
        self.assertTrue(result.action_changed)

if __name__ == '__main__':
    unittest.main()
