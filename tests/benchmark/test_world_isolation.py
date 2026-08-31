import unittest
from simulator.models import Customer, Payment, PaymentStatus, Invoice, InvoiceStatus
from simulator.world import FinancialWorld, world
from simulator.clock import clock
from backend.benchmark.generator import SeededWorldGenerator

class TestBenchmarkWorldIsolation(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset()

    def test_immutable_snapshot_isolation(self):
        """Verify that branching from canonical snapshot creates genuinely isolated worlds."""
        generator = SeededWorldGenerator(seed=42)
        canonical, opps = generator.generate()

        control_branch = canonical.snapshot()
        treatment_branch = canonical.snapshot()

        # Mutate treatment branch failed payments
        failed_p_ids = [p.id for p in canonical.payments.values() if p.status == PaymentStatus.FAILED][:5]
        for p_id in failed_p_ids:
            treatment_branch.payments[p_id].status = PaymentStatus.SETTLED

        # Verify control branch and canonical are unaffected
        for p_id in failed_p_ids:
            self.assertEqual(control_branch.payments[p_id].status, PaymentStatus.FAILED)
            self.assertEqual(canonical.payments[p_id].status, PaymentStatus.FAILED)

    def test_cross_branch_customer_mutation_isolation(self):
        """Verify that customer relationship mutations do not bleed between control and treatment."""
        generator = SeededWorldGenerator(seed=101)
        canonical, _ = generator.generate()

        control_branch = canonical.snapshot()
        treatment_branch = canonical.snapshot()

        c_id = list(canonical.customers.keys())[0]
        treatment_branch.customers[c_id].recent_contacts += 5
        treatment_branch.customers[c_id].complaints += 2

        self.assertEqual(control_branch.customers[c_id].recent_contacts, canonical.customers[c_id].recent_contacts)
        self.assertEqual(control_branch.customers[c_id].complaints, canonical.customers[c_id].complaints)

    def test_restore_from_integrity(self):
        """Verify that world.restore_from() completely and safely restores state."""
        generator = SeededWorldGenerator(seed=77)
        canonical, _ = generator.generate()

        target_world = FinancialWorld()
        target_world.restore_from(canonical)

        self.assertEqual(len(target_world.customers), len(canonical.customers))
        self.assertEqual(len(target_world.payments), len(canonical.payments))

        # Mutating target_world must not mutate canonical
        target_world.customers.clear()
        self.assertGreater(len(canonical.customers), 0)

if __name__ == '__main__':
    unittest.main()
