import unittest
from backend.benchmark.models import AblationConfig
from backend.benchmark.ultron_strategy import UltronStrategy
from backend.benchmark.generator import SeededWorldGenerator
from backend.benchmark.simulator_dynamics import SimulationDynamicsEngine
from memory.episodic import memory_store, EpisodeRecord
from simulator.clock import clock

class TestBenchmarkAblations(unittest.TestCase):
    def setUp(self):
        clock.reset()
        memory_store.memories = []

    def test_full_ultron_vs_ablations_instantiation(self):
        """All ablation variants must instantiate cleanly with distinct configs."""
        configs = [
            AblationConfig(name="FULL_ULTRON"),
            AblationConfig(name="ULTRON_NO_INTERFERENCE", disable_interference=True),
            AblationConfig(name="ULTRON_NO_MEMORY", disable_memory=True),
            AblationConfig(name="ULTRON_NO_REPLANNING", disable_replanning=True),
            AblationConfig(name="ULTRON_NO_DECAY", disable_decay=True),
            AblationConfig(name="ULTRON_NO_RELATIONSHIP_COST", disable_relationship_cost=True)
        ]
        
        for cfg in configs:
            strat = UltronStrategy(ablation=cfg)
            self.assertEqual(strat.name, cfg.name)

    def test_ablation_no_relationship_cost_zeros_rel_cost(self):
        """ULTRON_NO_RELATIONSHIP_COST must report 0.0 relationship cost."""
        generator = SeededWorldGenerator(seed=42)
        canonical, opps = generator.generate(start_time=1718000000)
        dynamics = SimulationDynamicsEngine(seed=42)
    
        clock.reset(1718000000)
        
        strat = UltronStrategy(ablation=AblationConfig(name="ULTRON_NO_RELATIONSHIP_COST", disable_relationship_cost=True))
        branch = canonical.snapshot()
        strat.run(branch, opps[:5], dynamics, horizon_days=30)

        self.assertEqual(strat.relationship_cost, 0.0)

    def test_ablation_no_memory_resets_memories(self):
        """ULTRON_NO_MEMORY must clear episodic memories upon execution."""
        memory_store.store(EpisodeRecord(
            customer_id="c_1", failure_type="TIMEOUT", action_taken="RETRY",
            result="SUCCESS", recovery_amount=100.0, timestamp=0
        ))
        self.assertEqual(len(memory_store.memories), 1)

        generator = SeededWorldGenerator(seed=42)
        canonical, opps = generator.generate(start_time=1718000000)
        dynamics = SimulationDynamicsEngine(seed=42)

        clock.reset(1718000000)
        strat = UltronStrategy(ablation=AblationConfig(name="ULTRON_NO_MEMORY", disable_memory=True))
        branch = canonical.snapshot()
        strat.run(branch, opps[:2], dynamics, horizon_days=30)

        # Memories must only contain newly executed episodes (old memory cleared)
        self.assertEqual(len(memory_store.memories), 2)
        for m in memory_store.memories:
            self.assertNotEqual(m.customer_id, "c_1")

if __name__ == '__main__':
    unittest.main()
