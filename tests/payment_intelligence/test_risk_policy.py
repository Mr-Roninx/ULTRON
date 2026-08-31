import unittest
from financial.risk import risk_engine, RiskViolationError, ConfidenceTier

class TestRiskPolicy(unittest.TestCase):
    def test_risk_tiers_and_validation(self):
        # 1. Low risk action (RETRY)
        retry_risk = risk_engine.calculate_action_risk("RETRY")
        self.assertEqual(risk_engine.determine_confidence_tier(retry_risk), ConfidenceTier.HIGH_CONFIDENCE)
        self.assertTrue(risk_engine.validate("RETRY", max_risk=0.50))

        # 2. Medium risk action (APPLY_DISCOUNT standard)
        discount_risk = risk_engine.calculate_action_risk("APPLY_DISCOUNT", payload={"amount": 1000.0})
        self.assertEqual(risk_engine.determine_confidence_tier(discount_risk), ConfidenceTier.LOW_CONFIDENCE)
        
        # 3. High risk action exceeding max_risk raises RiskViolationError (fail-closed)
        with self.assertRaises(RiskViolationError):
            risk_engine.validate("REFUND_PAYMENT", max_risk=0.10)

if __name__ == "__main__":
    unittest.main()
