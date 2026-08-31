import unittest
from backend.evidence.mechanism_evidence import run_payment_intelligence_ablation
from backend.evidence.models import PaymentIntelligenceAblationResult

class TestPaymentIntelligenceEffect(unittest.TestCase):
    def test_payment_intelligence_ablation_alters_decisions(self):
        """Experiment 3 Contract: Full Payment Intelligence produces diagnosis-specific actions."""
        results = run_payment_intelligence_ablation()
        self.assertGreaterEqual(len(results), 6)
        
        differed_count = sum(1 for r in results if r.decision_differed)
        self.assertGreater(differed_count, 0, "Payment Intelligence must alter decisions vs naive retry baseline.")

if __name__ == '__main__':
    unittest.main()
