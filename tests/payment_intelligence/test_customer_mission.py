import unittest
from simulator.world import world
from simulator.models import Customer, Payment, Invoice, Checkout, PaymentStatus, InvoiceStatus, CheckoutStatus
from backend.mission.mission_builder import mission_builder, mission_registry
from backend.mission.mission_state import RevenueMissionState

class TestCustomerMission(unittest.TestCase):
    def setUp(self):
        world.reset()
        mission_registry.reset()

    def test_multi_opportunity_mission_creation(self):
        # Setup Ananya Textiles with 3 revenue opportunities
        cust_id = "c_ananya"
        world.add_customer(Customer(id=cust_id, name="Ananya Textiles", segment="B2B_ENTERPRISE", created_at=0))

        # 1. Failed Subscription Payment: ₹8,200
        world.add_payment(Payment(
            id="p_sub_8200", customer_id=cust_id, amount=8200.0,
            status=PaymentStatus.FAILED, created_at=100, metadata={"type": "subscription"}
        ))

        # 2. Overdue Invoice: ₹4,500
        world.add_invoice(Invoice(
            id="inv_4500", customer_id=cust_id, amount=4500.0,
            status=InvoiceStatus.OVERDUE, created_at=150, due_date=120
        ))

        # 3. Abandoned Checkout: ₹12,000
        world.add_checkout(Checkout(
            id="chk_12000", customer_id=cust_id, amount=12000.0,
            status=CheckoutStatus.ABANDONED, created_at=200
        ))

        # Build Revenue Mission
        mission = mission_builder.build_or_update_mission(cust_id)

        self.assertEqual(mission.customer_id, cust_id)
        self.assertEqual(mission.customer_name, "Ananya Textiles")
        self.assertEqual(len(mission.opportunities), 3)
        self.assertEqual(mission.total_exposure, 24700.0) # 8200 + 4500 + 12000
        self.assertEqual(mission.state, RevenueMissionState.DISCOVERED)

        # Transition state
        mission.transition_state(RevenueMissionState.INVESTIGATING, "Agent started investigation")
        self.assertEqual(mission.state, RevenueMissionState.INVESTIGATING)
        self.assertEqual(len(mission.telemetry_trail), 1)

if __name__ == "__main__":
    unittest.main()
