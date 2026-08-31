import unittest
from backend.evidence.llm_evidence import measure_llm_candidate_influence
from backend.evidence.models import LLMCandidateInfluenceResult

class TestLLMCandidateInfluence(unittest.TestCase):
    def test_llm_candidate_influence_measurement(self):
        """Experiment 2 Contract: LLM candidates are evaluated and novelty is computed."""
        results = measure_llm_candidate_influence(["SCEN_1_TRANSIENT", "SCEN_2_LIQUIDITY"])
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertIsInstance(r, LLMCandidateInfluenceResult)
            self.assertGreaterEqual(r.candidate_novelty_rate, 0.0)
            self.assertLessEqual(r.candidate_novelty_rate, 1.0)
            self.assertIn(r.final_authority_action, r.deterministic_candidates)

if __name__ == '__main__':
    unittest.main()
