import unittest
from backend.evidence.mechanism_evidence import run_memory_influence_experiment
from backend.evidence.models import MemoryInfluenceResult

class TestMemoryEffect(unittest.TestCase):
    def test_memory_influences_subsequent_encounter_strategy(self):
        """Experiment 4 Contract: Prior prediction error informs Episode 2 action selection."""
        result = run_memory_influence_experiment(customer_id="c_test_mem_unit")
        self.assertIsInstance(result, MemoryInfluenceResult)
        self.assertTrue(result.memory_retrieved)
        self.assertTrue(result.memory_influenced)
        self.assertNotEqual(result.episode_2_memory_on_action, result.episode_2_memory_off_action)

if __name__ == '__main__':
    unittest.main()
