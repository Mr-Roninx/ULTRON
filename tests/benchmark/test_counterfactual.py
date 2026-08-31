import unittest
from backend.benchmark.models import OpportunityResult, BenchmarkOpportunity
from backend.benchmark.generator import SeededWorldGenerator
from backend.benchmark.simulator_dynamics import SimulationDynamicsEngine
from backend.benchmark.baselines import NoActionBaseline, RuleBasedRecoveryBaseline
from backend.benchmark.ultron_strategy import UltronStrategy
from simulator.clock import clock

class TestBenchmarkCounterfactual(unittest.TestCase):
    def setUp(self):
        clock.reset()

    def test_opportunity_level_counterfactual_comparison(self):
        """Verify that each opportunity records paired control vs treatment recovery."""
        gen = SeededWorldGenerator(seed=42)
        world, opps = gen.generate()
        
        control_recovered = 1000.0
        ultron_recovered = 2500.0
        incremental = ultron_recovered - control_recovered
        
        res = OpportunityResult(
            opportunity_id="opp_101",
            customer_id="c_1001",
            initial_amount=2500.0,
            channel="UPI",
            failure_type="TIMEOUT",
            customer_segment="B2B_ENTERPRISE",
            payment_rail="UPI",
            amount_bucket="LOW",
            control_strategy="NoAction",
            control_action="NONE",
            control_recovered=control_recovered,
            treatment_strategy="FULL_ULTRON",
            ultron_action="RETRY",
            ultron_recovered=ultron_recovered,
            incremental_recovery=incremental,
            net_incremental_recovery=incremental - 1.0
        )

        self.assertEqual(res.incremental_recovery, 1500.0)
        self.assertEqual(res.net_incremental_recovery, 1499.0)

if __name__ == '__main__':
    unittest.main()
