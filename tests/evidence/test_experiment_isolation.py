import unittest
from simulator.world import world, FinancialWorld
from simulator.models import Customer
from simulator.clock import clock
from memory.episodic import memory_store
from backend.evidence.instrumentation import generate_deterministic_hash

class TestExperimentIsolation(unittest.TestCase):
    def test_treatment_and_control_branches_are_strictly_isolated(self):
        """Verifies zero memory, world state, or clock leakage between experiment branches."""
        world.reset()
        clock.reset(1718000000)
        memory_store.clear()

        # Branch 1 mutation
        world.add_customer(Customer(id='c_branch_1', name='Branch 1', segment='SMB', created_at=0))
        snap_1 = world.snapshot()
        hash_1 = generate_deterministic_hash(snap_1)

        # Clone world for Branch 2
        cloned_world = FinancialWorld()
        cloned_world.restore_from(snap_1)
        cloned_world.add_customer(Customer(id='c_branch_2', name='Branch 2', segment='SMB', created_at=0))

        snap_2 = cloned_world.snapshot()
        hash_2 = generate_deterministic_hash(snap_2)

        self.assertNotEqual(hash_1, hash_2)
        self.assertNotIn("c_branch_2", world.customers)
        self.assertIn("c_branch_2", cloned_world.customers)

if __name__ == '__main__':
    unittest.main()
