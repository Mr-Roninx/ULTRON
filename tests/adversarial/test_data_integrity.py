import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from simulator.world import world
from simulator.clock import clock
from simulator.seed import seed_ananya_textiles
from simulator.event_bus import event_bus

class TestAdversarialDataIntegrity(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset()
        seed_ananya_textiles()

    def test_no_negative_amounts_in_seeded_world(self):
        """Verify all payments, invoices, and checkouts have non-negative monetary amounts."""
        for p_id, p in world.payments.items():
            self.assertTrue(p.amount >= 0, f"Negative payment amount in payment {p_id}: {p.amount}")
            
        for inv_id, inv in world.invoices.items():
            self.assertTrue(inv.amount >= 0, f"Negative invoice amount in invoice {inv_id}: {inv.amount}")
            
        for chk_id, chk in world.checkouts.items():
            self.assertTrue(chk.amount >= 0, f"Negative checkout amount in checkout {chk_id}: {chk.amount}")

    def test_no_orphan_customer_references(self):
        """Verify that every payment, invoice, and checkout points to an existing customer."""
        customer_ids = set(world.customers.keys())
        
        for p_id, p in world.payments.items():
            self.assertIn(p.customer_id, customer_ids, f"Payment {p_id} has orphan customer_id {p.customer_id}")
            
        for inv_id, inv in world.invoices.items():
            self.assertIn(inv.customer_id, customer_ids, f"Invoice {inv_id} has orphan customer_id {inv.customer_id}")

    def test_unique_event_ids(self):
        """Verify all published domain events have strictly unique IDs."""
        events = event_bus.get_history()
        event_ids = [e.event_id for e in events]
        self.assertEqual(len(event_ids), len(set(event_ids)), "Duplicate domain event IDs detected!")

    def test_no_negative_timestamps(self):
        """Verify all entity creation and event timestamps are >= 0."""
        for c in world.customers.values():
            self.assertTrue(c.created_at >= 0)
        for p in world.payments.values():
            self.assertTrue(p.created_at >= 0)
        for e in event_bus.get_history():
            self.assertTrue(e.timestamp >= 0)

if __name__ == '__main__':
    unittest.main()
