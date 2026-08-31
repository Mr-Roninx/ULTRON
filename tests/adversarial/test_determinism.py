import sys
import os
import unittest
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from simulator.world import world
from simulator.clock import clock
from simulator.seed import seed_ananya_textiles

class TestAdversarialSimulationDeterminism(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset()

    def test_seed_ananya_textiles_reproducibility(self):
        """Seeding the world produces strictly identical entities every time."""
        # Run 1
        world.reset()
        seed_ananya_textiles()
        c1_name = world.customers["c_1001"].name
        p1_amount = world.payments["pay_failed_1"].amount
        inv1_amount = world.invoices["inv_991"].amount

        # Run 2
        world.reset()
        seed_ananya_textiles()
        self.assertEqual(world.customers["c_1001"].name, c1_name)
        self.assertEqual(world.payments["pay_failed_1"].amount, p1_amount)
        self.assertEqual(world.invoices["inv_991"].amount, inv1_amount)

    def test_clock_queue_priority_determinism(self):
        """Clock scheduled priority queue execution order is strictly deterministic."""
        execution_log = []
        clock.schedule(10, lambda: execution_log.append("event_10_a"))
        clock.schedule(5, lambda: execution_log.append("event_5"))
        clock.schedule(10, lambda: execution_log.append("event_10_b"))
        clock.schedule(2, lambda: execution_log.append("event_2"))

        clock.advance(15)
        self.assertEqual(execution_log[0], "event_2")
        self.assertEqual(execution_log[1], "event_5")
        self.assertIn("event_10_a", execution_log[2:])
        self.assertIn("event_10_b", execution_log[2:])

if __name__ == '__main__':
    unittest.main()
