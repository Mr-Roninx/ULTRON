import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.models import Customer, Payment, Invoice, Checkout, PaymentStatus, InvoiceStatus, CheckoutStatus
from backend.economics.engine import economic_engine
from backend.economics.relationship import RelationshipState
from backend.episodes.engine import episode_engine
from financial.feasible_actions import feasible_action_engine
from backend.tools.execution import execution_tools
from simulator.world import world
from simulator.clock import clock
from financial.authority import AuthorityLevel
from simulator.event_bus import event_bus

class TestPhase2(unittest.TestCase):
    def setUp(self):
        world.reset()
        c = Customer(
            id="c_1", name="Test", segment="B2B_ENTERPRISE",
            created_at=0, ltv=10000, recent_contacts=1, complaints=0
        )
        world.add_customer(c)

    def test_nev_calculation_basic(self):
        # Expected = 100, Action = 10, Rel = 5, Risk (0.1*100 = 10) -> 100 - 10 - 5 - 10 = 75
        nev = economic_engine.calculate_nev(100.0, 10.0, 5.0, 10.0)
        self.assertEqual(nev, 75.0)

    def test_nev_negative_when_cost_exceeds_recovery(self):
        nev = economic_engine.calculate_nev(10.0, 50.0, 0.0, 0.0)
        self.assertLess(nev, 0.0)

    def test_nev_with_zero_recovery(self):
        nev = economic_engine.calculate_nev(0.0, 10.0, 5.0, 0.0)
        self.assertEqual(nev, -15.0)

    def test_relationship_cost_proxy_high_complaints(self):
        rs = RelationshipState(customer_id="c_1", recent_contacts=1, recent_responses=0,
                               successful_prior_recoveries=0, customer_value=1000,
                               complaints=2, opt_out=False, silence_duration=0)
        cost = rs.relationship_cost_proxy()
        # 1*5 + 2*100 + (1000*0.001)*1 = 5 + 200 + 1 = 206
        self.assertEqual(cost, 206.0)

    def test_relationship_cost_proxy_opt_out(self):
        rs = RelationshipState(customer_id="c_1", recent_contacts=0, recent_responses=0,
                               successful_prior_recoveries=0, customer_value=1000,
                               complaints=0, opt_out=True, silence_duration=0)
        self.assertEqual(rs.relationship_cost_proxy(), float('inf'))

    def test_revenue_episode_aggregates_all_channels(self):
        world.add_payment(Payment(id="p_1", customer_id="c_1", amount=100, status=PaymentStatus.FAILED, created_at=0))
        world.add_invoice(Invoice(id="i_1", customer_id="c_1", amount=200, status=InvoiceStatus.OVERDUE, due_date=0))
        world.add_checkout(Checkout(id="chk_1", customer_id="c_1", amount=300, status=CheckoutStatus.ABANDONED, created_at=0))
        
        episode = episode_engine.create_episode("c_1")
        self.assertEqual(episode.total_exposure, 600.0)
        self.assertEqual(len(episode.payments), 1)
        self.assertEqual(len(episode.invoices), 1)
        self.assertEqual(len(episode.checkouts), 1)

    def test_episode_with_no_exposure(self):
        episode = episode_engine.create_episode("c_1")
        self.assertEqual(episode.total_exposure, 0.0)

    def test_feasible_actions_excludes_unauthorized(self):
        context = {"snapshot": {"customer": {"segment": "B2B_ENTERPRISE"}}}
        # OBSERVE cannot do anything
        actions = feasible_action_engine.get_feasible_actions(context, max_risk=1.0, current_authority=AuthorityLevel.OBSERVE)
        self.assertEqual(len(actions), 0)

    def test_feasible_actions_excludes_risky(self):
        context = {"snapshot": {"customer": {"segment": "B2B_ENTERPRISE"}}}
        # max_risk 0.1 excludes APPLY_DISCOUNT (0.5), REFUND_PAYMENT (0.8), SEND_PAYMENT_LINK (0.2), REGISTER_PTP (0.2)
        # allowed: WAIT(0.0), RECONCILE(0.01), RETRY(0.10), SEND_MESSAGE(0.05), ESCALATE(0.0), STOP(0.0)
        actions = feasible_action_engine.get_feasible_actions(context, max_risk=0.1, current_authority=AuthorityLevel.AUTONOMOUS)
        self.assertNotIn("APPLY_DISCOUNT", actions)
        self.assertNotIn("REFUND_PAYMENT", actions)
        self.assertIn("RECONCILE", actions)

    def test_feasible_actions_excludes_policy_violations(self):
        # B2B policy violation for APPLY_DISCOUNT
        context = {"snapshot": {"customer": {"segment": "B2C_STANDARD"}}}
        actions = feasible_action_engine.get_feasible_actions(context, max_risk=1.0, current_authority=AuthorityLevel.AUTONOMOUS)
        self.assertNotIn("APPLY_DISCOUNT", actions)

    def test_feasible_actions_returns_empty_when_all_blocked(self):
        context = {"snapshot": {"customer": {"segment": "B2C_STANDARD"}}}
        # Very low risk + OBSERVE authority
        actions = feasible_action_engine.get_feasible_actions(context, max_risk=0.0, current_authority=AuthorityLevel.OBSERVE)
        self.assertEqual(len(actions), 0)

    def test_tool_contract_validate_authority(self):
        res = execution_tools.reconcile_payment("m_1", "c_1", "p_1", "OBSERVE")
        self.assertFalse(res.success)
        self.assertIn("Authority", res.message)

    def test_tool_contract_validate_state_and_structured_result(self):
        world.add_payment(Payment(id="p_1", customer_id="c_1", amount=100, status=PaymentStatus.UNKNOWN, created_at=0))
        res = execution_tools.reconcile_payment("m_1", "c_1", "p_1", "AUTONOMOUS")
        self.assertTrue(res.success)
        self.assertEqual(res.state_change, "RECONCILED")
        self.assertTrue(res.action_id.startswith("act_"))

    def test_tool_rejects_invalid_payment_id(self):
        res = execution_tools.reconcile_payment("m_1", "c_1", "invalid_p_1", "AUTONOMOUS")
        self.assertFalse(res.success)
        self.assertIn("Reconciliation failed", res.message)

    def test_tool_contract_emit_event(self):
        event_bus.reset()
        execution_tools.register_ptp("m_1", "c_1", 123456, "AUTONOMOUS")
        self.assertEqual(len(event_bus.events), 1)
        self.assertEqual(event_bus.events[0].event_type, "PTP_REGISTERED")

if __name__ == '__main__':
    unittest.main()
