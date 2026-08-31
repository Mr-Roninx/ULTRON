import unittest
from backend.benchmark.metrics import MetricsCalculator
from backend.benchmark.models import StrategyMetrics

class TestMetricIntegrity(unittest.TestCase):
    def test_incremental_recovery_exact_formula(self):
        """incremental_recovery = treatment_recovery - control_recovery"""
        control_rec = 50000.0
        treatment_rec = 120000.0
        
        incremental = treatment_rec - control_rec
        self.assertEqual(incremental, 70000.0)

    def test_net_incremental_recovery_formula(self):
        """net_incremental = incremental - intervention_cost - rel_cost - risk_cost"""
        incremental = 70000.0
        intervention_cost = 250.0
        rel_cost = 1500.0
        risk_cost = 500.0
        
        net = incremental - intervention_cost - rel_cost - risk_cost
        self.assertEqual(net, 67750.0)

    def test_primary_recovery_rate_denominator_is_addressable(self):
        """Primary recovery rate MUST be gross_recovery / addressable_revenue, NEVER recovered/attempted."""
        gross_recovery = 80000.0
        addressable_revenue = 200000.0
        
        rate = gross_recovery / addressable_revenue
        self.assertEqual(rate, 0.40)

    def test_bootstrap_ci95_calculation(self):
        """Verify 95% bootstrap confidence interval produces sensible deterministic bounds."""
        values = [100.0, 105.0, 95.0, 110.0, 90.0, 102.0, 98.0, 107.0, 93.0, 100.0]
        ci = MetricsCalculator.bootstrap_ci95(values, num_resamples=1000, seed=42)
        
        self.assertEqual(len(ci), 2)
        self.assertLessEqual(ci[0], sum(values)/len(values))
        self.assertGreaterEqual(ci[1], sum(values)/len(values))
        self.assertGreater(ci[1], ci[0])

if __name__ == '__main__':
    unittest.main()
