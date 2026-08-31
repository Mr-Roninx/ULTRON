import unittest
from simulator.world import world
from simulator.clock import clock
from simulator.models import Customer, Payment, PaymentStatus
from backend.tools.investigation import investigation_tools

class TestFutureInformationFirewall(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset(1000)

    def test_future_payments_hidden_from_investigation_tools(self):
        """Payments with created_at in the future must not be returned to the agent."""
        world.add_customer(Customer(id="c_future", name="Future Customer", segment="SMB", created_at=500))
        
        # Payment 1 at T=800 (observable)
        world.add_payment(Payment(id="p_past", customer_id="c_future", amount=1000.0, status=PaymentStatus.FAILED, created_at=800))
        
        # Payment 2 at T=1500 (future, not yet happened at clock=1000)
        world.add_payment(Payment(id="p_future", customer_id="c_future", amount=9999.0, status=PaymentStatus.FAILED, created_at=1500))

        history = investigation_tools.get_payment_history("c_future")
        payment_ids = [p["id"] for p in history]

        self.assertIn("p_past", payment_ids)
        self.assertNotIn("p_future", payment_ids)

if __name__ == "__main__":
    unittest.main()
