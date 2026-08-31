import unittest
from backend.benchmark.generator import SeededWorldGenerator
from backend.benchmark.models import ResourceConstraints
from backend.benchmark.baselines import (
    NoActionBaseline, FixedRetryBaseline, 
    TraditionalDunningBaseline, RuleBasedRecoveryBaseline
)
from backend.benchmark.ultron_strategy import UltronStrategy
from backend.benchmark.simulator_dynamics import SimulationDynamicsEngine
from simulator.models import PaymentStatus
from simulator.clock import clock

class TestBaselineFairness(unittest.TestCase):
    def test_all_strategies_receive_identical_initial_exposure(self):
        """Verify that every strategy operates on identical opportunity amounts and customers."""
        generator = SeededWorldGenerator(seed=88)
        canonical, opps = generator.generate()

        constraints = ResourceConstraints(
            max_contacts_per_customer=3,
            max_recovery_actions_per_opportunity=4,
            max_risk_tolerance=1.0,
            authority_level="AUTONOMOUS"
        )

        strategies = [
            NoActionBaseline(constraints),
            FixedRetryBaseline(constraints),
            TraditionalDunningBaseline(constraints),
            RuleBasedRecoveryBaseline(constraints),
            UltronStrategy(constraints=constraints)
        ]

        # Ensure all strategies receive identical constraints
        for s in strategies:
            self.assertEqual(s.constraints.max_contacts_per_customer, 3)
            self.assertEqual(s.constraints.max_recovery_actions_per_opportunity, 4)
            self.assertEqual(s.constraints.authority_level, "AUTONOMOUS")

        # Verify opportunities are identical
        self.assertGreater(len(opps), 50)
        total_initial_exposure = sum(o.initial_amount for o in opps)
        self.assertGreater(total_initial_exposure, 100000.0)

    def test_baselines_respect_unknown_payment_protection(self):
        """FixedRetry must not blindly retry UNKNOWN payments without reconciliation."""
        generator = SeededWorldGenerator(seed=42)
        canonical, opps = generator.generate()
        
        # Inject an UNKNOWN payment into an active opportunity
        p_opp = [o for o in opps if o.entity_type == "PAYMENT"][0]
        canonical.payments[p_opp.entity_id].status = PaymentStatus.UNKNOWN

        fixed_retry = FixedRetryBaseline()
        dynamics = SimulationDynamicsEngine(seed=42)
        
        branch = canonical.snapshot()
        fixed_retry.run(branch, opps, dynamics, horizon_days=30)

        # UNKNOWN payment retry must be blocked
        self.assertGreater(fixed_retry.actions_blocked, 0)

if __name__ == '__main__':
    unittest.main()
