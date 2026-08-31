import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from simulator.models import Customer, Payment, PaymentStatus, Gateway, Checkout, CheckoutStatus
from simulator.world import world
from simulator.clock import clock
from simulator.chaos import chaos_engine
from backend.agent.observation import observer
from backend.audit.ledger import audit_ledger

class TestAdversarialChaosEngine(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset()
        chaos_engine.disable()
        audit_ledger.reset()
        world.add_customer(Customer(id="c_1001", name="Alpha Textiles", segment="B2B_ENTERPRISE", created_at=0))
        world.add_payment(Payment(id="p_1001", customer_id="c_1001", amount=1500.0, status=PaymentStatus.INITIATED, created_at=0))
        world.add_checkout(Checkout(id="chk_1001", customer_id="c_1001", amount=500.0, status=CheckoutStatus.STARTED, created_at=0))

    def test_upi_degradation_modifies_world_and_audit(self):
        """Scenario 1: UPI Degradation reduces gateway health and logs audit."""
        res = chaos_engine.trigger("UPI_DEGRADATION", gateway_id="gw_razorpay")
        self.assertEqual(res["status"], "INJECTED")
        self.assertTrue(world.gateways["gw_razorpay"].health <= 0.2)
        trace = audit_ledger.get_trace()
        self.assertTrue(any(e.payload.get("scenario") == "UPI_DEGRADATION" for e in trace))

    def test_gateway_timeout_forces_unknown_state(self):
        """Scenario 2: Gateway Timeout forces INITIATED -> UNKNOWN."""
        res = chaos_engine.trigger("GATEWAY_TIMEOUT", payment_id="p_1001")
        self.assertEqual(world.payments["p_1001"].status, PaymentStatus.UNKNOWN)

    def test_webhook_delay_schedules_delayed_settlement(self):
        """Scenario 3: Webhook delay defers state arrival until future clock timestamp."""
        world.update_payment_status("p_1001", PaymentStatus.AUTHORIZING.value)
        res = chaos_engine.trigger("WEBHOOK_DELAY", payment_id="p_1001", delay_seconds=100)
        
        # State at t=0 must still be AUTHORIZING
        self.assertEqual(world.payments["p_1001"].status, PaymentStatus.AUTHORIZING)
        
        # Advance clock to trigger delayed webhook
        clock.advance(150)
        self.assertEqual(world.payments["p_1001"].status, PaymentStatus.AUTHORIZED)

    def test_gateway_recovery_restores_gateway_health(self):
        """Scenario 4: Gateway Recovery restores gateway health to 1.0."""
        chaos_engine.trigger("UPI_DEGRADATION", gateway_id="gw_razorpay")
        self.assertTrue(world.gateways["gw_razorpay"].health < 1.0)
        
        chaos_engine.trigger("GATEWAY_RECOVERY", gateway_id="gw_razorpay")
        self.assertEqual(world.gateways["gw_razorpay"].health, 1.0)

    def test_mass_checkout_abandonment_modifies_active_checkouts(self):
        """Scenario 5: Mass Checkout Abandonment transitions active checkouts to ABANDONED."""
        res = chaos_engine.trigger("MASS_CHECKOUT_ABANDONMENT")
        self.assertEqual(world.checkouts["chk_1001"].status, CheckoutStatus.ABANDONED)

    def test_customer_silence_scenario(self):
        """Scenario 6: Customer Silence increases silence duration."""
        initial_silence = world.customers["c_1001"].silence_duration
        chaos_engine.trigger("CUSTOMER_SILENCE", customer_id="c_1001", silence_duration=50000)
        self.assertEqual(world.customers["c_1001"].silence_duration, initial_silence + 50000)

    def test_payment_state_ambiguity_triggers_observation_replan(self):
        """Scenario 7: State ambiguity mutates world and forces observation error."""
        chaos_engine.trigger("PAYMENT_STATE_AMBIGUITY", payment_id="p_1001")
        self.assertEqual(world.payments["p_1001"].status, PaymentStatus.UNKNOWN)
        
        # Observer evaluates expected SETTLED vs observed UNKNOWN -> REPLAN
        res = observer.evaluate(expected_value=1500.0, observed_value=0.0, actual_status="UNKNOWN")
        self.assertTrue(res["requires_replan"])

if __name__ == '__main__':
    unittest.main()
