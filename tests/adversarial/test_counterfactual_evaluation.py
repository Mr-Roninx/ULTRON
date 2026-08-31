import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from simulator.models import Customer, Payment, PaymentStatus
from simulator.world import world, FinancialWorld
from simulator.clock import clock
from backend.agent.schemas import AgentIntent
from evaluator.counterfactual import counterfactual_evaluator

class TestAdversarialCounterfactualEvaluation(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset()

    def test_snapshot_independence_between_control_and_treatment(self):
        """Verify modifying treatment world does not mutate control world."""
        world.add_customer(Customer(id="c_1001", name="Gamma Inc", segment="B2B_ENTERPRISE", created_at=0))
        world.add_payment(Payment(id="p_1001", customer_id="c_1001", amount=2000.0, status=PaymentStatus.UNKNOWN, created_at=0))

        # Snapshot creates independent world
        control_world = world.snapshot()
        treatment_world = world.snapshot()

        # Mutate treatment world
        treatment_world.update_payment_status("p_1001", PaymentStatus.RECONCILING.value)
        treatment_world.update_payment_status("p_1001", PaymentStatus.SETTLED.value)

        # Control world MUST remain in original UNKNOWN status
        self.assertEqual(control_world.payments["p_1001"].status, PaymentStatus.UNKNOWN)
        self.assertEqual(treatment_world.payments["p_1001"].status, PaymentStatus.SETTLED)

    def test_control_world_receives_no_agent_actions(self):
        """Verify control world is purely non-intervened baseline."""
        world.add_customer(Customer(id="c_1001", name="Gamma Inc", segment="B2B_ENTERPRISE", created_at=0))
        world.add_payment(Payment(id="p_1001", customer_id="c_1001", amount=2000.0, status=PaymentStatus.UNKNOWN, created_at=0))

        control = world.snapshot()
        self.assertEqual(len(control.recovery_actions), 0)
        self.assertEqual(len(control.communications), 0)

    def test_regret_evaluation_world_pointer_restoration(self):
        """Verify that counterfactual evaluation leaves global world untouched."""
        world.add_customer(Customer(id="c_1001", name="Gamma Inc", segment="B2B_ENTERPRISE", created_at=0))
        world.add_payment(Payment(id="p_1001", customer_id="c_1001", amount=2000.0, status=PaymentStatus.UNKNOWN, created_at=0))

        initial_payment_status = world.payments["p_1001"].status
        initial_recovery_count = len(world.recovery_actions)

        intent = AgentIntent(
            action_type="RECONCILE",
            reasoning="Reconciling test",
            expected_yield=2000.0,
            payload={"payment_id": "p_1001"}
        )

        regret_result = counterfactual_evaluator.calculate_regret(
            customer_id="c_1001",
            chosen_intent=intent,
            max_risk=1.0,
            authority="AUTONOMOUS"
        )

        # Global world must be exactly as it was before calculation
        self.assertEqual(world.payments["p_1001"].status, initial_payment_status)
        self.assertEqual(len(world.recovery_actions), initial_recovery_count)
        self.assertIn("regret", regret_result)
        self.assertTrue(regret_result["regret"] >= 0.0)

if __name__ == '__main__':
    unittest.main()
