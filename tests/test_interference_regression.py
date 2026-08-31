import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.world import world
from simulator.clock import clock
from simulator.models import Customer, Payment, Checkout, PaymentStatus, CheckoutStatus
from simulator.event_bus import event_bus
from intelligence.interference import interference_engine

class TestInterferenceRegression(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset()

    def test_interference_changes_dynamically_with_dataset(self):
        """Verify calculate_interference calculates dynamically and does not return a constant 0.19."""
        # Scenario 1: 100% correlation (Customer 1 gets failed payment then abandoned checkout 1 hour later)
        world.add_customer(Customer(id="c_1", name="Client 1", segment="B2B_ENTERPRISE", created_at=0))
        p1 = Payment(id="p_1", customer_id="c_1", amount=100.0, status=PaymentStatus.FAILED, created_at=0)
        world.add_payment(p1)
        
        clock.advance(3600) # 1 hr
        chk1 = Checkout(id="chk_1", customer_id="c_1", amount=50.0, status=CheckoutStatus.ABANDONED, created_at=clock.now())
        world.add_checkout(chk1)

        delta_1 = interference_engine.calculate_interference("PAYMENT_FAILED", "CHECKOUT_ABANDONED")
        # 1 customer with A, who also had B within window -> P(B|A) = 1.0. Zero without A -> P(B|~A) = 0. Delta = 1.0
        self.assertEqual(delta_1, 1.0)

        # Scenario 2: Add Customer 2 with Payment Failure but NO abandoned checkout
        world.add_customer(Customer(id="c_2", name="Client 2", segment="B2B_ENTERPRISE", created_at=0))
        p2 = Payment(id="p_2", customer_id="c_2", amount=200.0, status=PaymentStatus.FAILED, created_at=0)
        world.add_payment(p2)

        delta_2 = interference_engine.calculate_interference("PAYMENT_FAILED", "CHECKOUT_ABANDONED")
        # 2 customers with A, only 1 had B -> P(B|A) = 0.5. Delta = 0.5
        self.assertEqual(delta_2, 0.5)

        # Scenario 3: Add Customer 3 with Abandoned Checkout but NO Payment Failure
        world.add_customer(Customer(id="c_3", name="Client 3", segment="B2B_ENTERPRISE", created_at=0))
        chk3 = Checkout(id="chk_3", customer_id="c_3", amount=50.0, status=CheckoutStatus.ABANDONED, created_at=clock.now())
        world.add_checkout(chk3)

        delta_3 = interference_engine.calculate_interference("PAYMENT_FAILED", "CHECKOUT_ABANDONED")
        # P(B|A) = 1/2 = 0.5. P(B|~A) = 1/1 = 1.0. Delta = 0.5 - 1.0 = -0.5
        self.assertEqual(delta_3, -0.5)

if __name__ == '__main__':
    unittest.main()
