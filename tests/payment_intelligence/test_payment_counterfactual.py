import unittest
from evaluator.counterfactual import counterfactual_evaluator
from simulator.world import world
from simulator.models import Customer, Payment, PaymentStatus
from backend.agent.schemas import AgentIntent

class TestPaymentCounterfactual(unittest.TestCase):
    def setUp(self):
        world.reset()
        world.add_customer(Customer(id="c_cf_1", name="CF Corp", segment="SMB", created_at=0))
        world.add_payment(Payment(id="p_cf_1", customer_id="c_cf_1", amount=10000.0, status=PaymentStatus.FAILED, created_at=0))

    def test_counterfactual_regret_evaluation(self):
        intent = AgentIntent(
            action_type="RETRY",
            preferred_action="RETRY",
            candidate_actions=["RETRY", "SEND_PAYMENT_LINK", "WAIT"],
            reasoning="Testing counterfactual calculation",
            expected_yield=7000.0,
            payload={"payment_id": "p_cf_1"}
        )
        
        regret = counterfactual_evaluator.calculate_regret(
            customer_id="c_cf_1",
            chosen_intent=intent,
            max_risk=1.0,
            authority="AUTONOMOUS"
        )

        self.assertIn("chosen_action", regret)
        self.assertEqual(regret["chosen_action"], "RETRY")
        self.assertIn("regret", regret)
        self.assertGreaterEqual(regret["regret"], 0.0)

if __name__ == "__main__":
    unittest.main()
