import unittest
from simulator.world import world
from simulator.models import Customer, Payment, Invoice, Checkout, PaymentStatus, InvoiceStatus, CheckoutStatus
from backend.interference.interference_graph import interference_graph

class TestInterferenceEngine(unittest.TestCase):
    def setUp(self):
        world.reset()

    def test_multi_opportunity_interference_score(self):
        cust_id = "c_int_1"
        world.add_customer(Customer(id=cust_id, name="Interference Corp", segment="SMB", created_at=0))
        
        # 1 issue -> interference_score = 0.0
        world.add_payment(Payment(id="p1", customer_id=cust_id, amount=1000.0, status=PaymentStatus.FAILED, created_at=0))
        exp1 = interference_graph.get_customer_exposure(cust_id)
        self.assertEqual(exp1["active_opportunities"], 1)
        self.assertEqual(exp1["interference_score"], 0.0)

        # 2 issues -> interference_score = 0.25
        world.add_invoice(Invoice(id="inv1", customer_id=cust_id, amount=2000.0, status=InvoiceStatus.OVERDUE, due_date=0))
        exp2 = interference_graph.get_customer_exposure(cust_id)
        self.assertEqual(exp2["active_opportunities"], 2)
        self.assertEqual(exp2["interference_score"], 0.25)
        self.assertEqual(exp2["total_exposure"], 3000.0)

        # 3 issues -> interference_score = 0.50
        world.add_checkout(Checkout(id="chk1", customer_id=cust_id, amount=3000.0, status=CheckoutStatus.ABANDONED, created_at=0))
        exp3 = interference_graph.get_customer_exposure(cust_id)
        self.assertEqual(exp3["active_opportunities"], 3)
        self.assertEqual(exp3["interference_score"], 0.50)
        self.assertEqual(exp3["total_exposure"], 6000.0)

if __name__ == "__main__":
    unittest.main()
