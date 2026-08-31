import unittest
from backend.evidence.economic_evidence import run_economic_lift_benchmark
from backend.evidence.models import EconomicLiftResult

class TestEconomicLift(unittest.TestCase):
    def test_paired_counterfactual_economic_lift(self):
        """Experiment 6 Contract: Economic lift is computed strictly from identical-seed counterfactual pairs."""
        lift_results, ablation_rows = run_economic_lift_benchmark(seeds=[101, 102], horizon_days=7)
        self.assertEqual(len(lift_results), 2)
        for r in lift_results:
            self.assertIsInstance(r, EconomicLiftResult)
            # Incremental formula verification: Treatment - Control
            self.assertEqual(r.paired_incremental_vs_rule_based, round(r.ultron_recovery - r.rule_based_recovery, 2))
            self.assertEqual(r.paired_incremental_vs_fixed_retry, round(r.ultron_recovery - r.fixed_retry_recovery, 2))

if __name__ == '__main__':
    unittest.main()
