import unittest
from backend.evidence.llm_evidence import verify_live_llm_path
from backend.evidence.models import LLMExecutionEvidence

class TestLLMLivePath(unittest.TestCase):
    def test_llm_path_executes_without_crashing_even_if_offline(self):
        """Experiment 1 Contract: verify_live_llm_path executes safely without crashing."""
        evidence = verify_live_llm_path("exp_test_live")
        self.assertIsInstance(evidence, LLMExecutionEvidence)
        self.assertTrue(evidence.success)
        self.assertTrue(evidence.schema_valid)
        self.assertGreater(evidence.latency_ms, 0.0)
        self.assertIn(evidence.fallback_used, [True, False])
        self.assertIsInstance(evidence.candidate_actions, list)

if __name__ == '__main__':
    unittest.main()
