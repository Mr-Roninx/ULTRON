import unittest
from backend.benchmark.generator import SeededWorldGenerator
from backend.benchmark.baselines import RuleBasedRecoveryBaseline
from backend.benchmark.simulator_dynamics import SimulationDynamicsEngine
from simulator.clock import clock

class TestBenchmarkReproducibility(unittest.TestCase):
    def test_identical_seed_produces_identical_world(self):
        """Seed 42 generated twice must have identical customer IDs, amounts, and statuses."""
        gen1 = SeededWorldGenerator(seed=42)
        world1, opps1 = gen1.generate()

        gen2 = SeededWorldGenerator(seed=42)
        world2, opps2 = gen2.generate()

        self.assertEqual(len(world1.customers), len(world2.customers))
        self.assertEqual(len(world1.payments), len(world2.payments))
        self.assertEqual(len(opps1), len(opps2))

        for opp1, opp2 in zip(opps1, opps2):
            self.assertEqual(opp1.opportunity_id, opp2.opportunity_id)
            self.assertEqual(opp1.initial_amount, opp2.initial_amount)
            self.assertEqual(opp1.failure_type, opp2.failure_type)

    def test_different_seeds_produce_different_distributions(self):
        """Seed 42 and Seed 99 must produce distinct customer names and initial exposures."""
        gen1 = SeededWorldGenerator(seed=42)
        world1, opps1 = gen1.generate()

        gen2 = SeededWorldGenerator(seed=99)
        world2, opps2 = gen2.generate()

        total1 = sum(o.initial_amount for o in opps1)
        total2 = sum(o.initial_amount for o in opps2)
        self.assertNotEqual(total1, total2)

    def test_strategy_execution_is_deterministic(self):
        """Running RuleBasedRecovery on the same seed twice must produce identical actions and costs."""
        gen1 = SeededWorldGenerator(seed=55)
        w1, opps1 = gen1.generate()
        dyn1 = SimulationDynamicsEngine(seed=55)
        strat1 = RuleBasedRecoveryBaseline()
        strat1.run(w1.snapshot(), opps1, dyn1, horizon_days=30)

        gen2 = SeededWorldGenerator(seed=55)
        w2, opps2 = gen2.generate()
        dyn2 = SimulationDynamicsEngine(seed=55)
        strat2 = RuleBasedRecoveryBaseline()
        strat2.run(w2.snapshot(), opps2, dyn2, horizon_days=30)

        self.assertEqual(strat1.actions_attempted, strat2.actions_attempted)
        self.assertEqual(strat1.intervention_cost, strat2.intervention_cost)
        self.assertEqual(strat1.opportunity_actions, strat2.opportunity_actions)

if __name__ == '__main__':
    unittest.main()
