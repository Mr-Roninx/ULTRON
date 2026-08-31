import unittest
from backend.payment_intelligence.schemas import FailureClass, FailureSeverity
from backend.payment_intelligence.failure_taxonomy import failure_taxonomy, DETERMINISTIC_TAXONOMY
from backend.payment_intelligence.failure_normalizer import failure_normalizer
from backend.payment_intelligence.schemas import PaymentFailureRaw

class TestFailureTaxonomy(unittest.TestCase):
    def test_insufficient_funds_taxonomy(self):
        rule = failure_taxonomy.get_rule("INSUFFICIENT_FUNDS")
        self.assertEqual(rule.failure_class, FailureClass.LIQUIDITY)
        self.assertEqual(rule.severity, FailureSeverity.MEDIUM)
        self.assertTrue(rule.retry_eligible)
        self.assertFalse(rule.customer_action_required)
        self.assertIn("RETRY", rule.typical_recovery_actions)
        self.assertIn("ESCALATE", rule.prohibited_actions)

    def test_expired_card_taxonomy(self):
        rule = failure_taxonomy.get_rule("EXPIRED_CARD")
        self.assertEqual(rule.failure_class, FailureClass.CREDENTIAL)
        self.assertFalse(rule.retry_eligible)
        self.assertTrue(rule.customer_action_required)
        self.assertIn("RETRY", rule.prohibited_actions)
        self.assertIn("SEND_PAYMENT_LINK", rule.typical_recovery_actions)

    def test_multi_gateway_normalization(self):
        # Stripe
        stripe_norm = failure_normalizer.normalize(PaymentFailureRaw(
            gateway_id="stripe", raw_code="insufficient_funds", amount=8400.0
        ))
        self.assertEqual(stripe_norm.failure_class, FailureClass.LIQUIDITY)
        self.assertEqual(stripe_norm.failure_reason, "INSUFFICIENT_FUNDS")

        # Razorpay
        rzp_norm = failure_normalizer.normalize(PaymentFailureRaw(
            gateway_id="razorpay", raw_code="GATEWAY_ERROR", amount=5000.0
        ))
        self.assertEqual(rzp_norm.failure_class, FailureClass.GATEWAY)
        self.assertEqual(rzp_norm.failure_reason, "GATEWAY_DOWN")

        # Gateway A (ISO 8583 Code 51)
        gwa_norm = failure_normalizer.normalize(PaymentFailureRaw(
            gateway_id="gateway_a", raw_code="51", amount=8400.0
        ))
        self.assertEqual(gwa_norm.failure_class, FailureClass.LIQUIDITY)
        self.assertEqual(gwa_norm.failure_reason, "INSUFFICIENT_FUNDS")

        # Adyen
        adyen_norm = failure_normalizer.normalize(PaymentFailureRaw(
            gateway_id="adyen", raw_code="ExpiredCard", amount=1200.0
        ))
        self.assertEqual(adyen_norm.failure_class, FailureClass.CREDENTIAL)
        self.assertEqual(adyen_norm.failure_reason, "EXPIRED_CARD")
        self.assertFalse(adyen_norm.retry_eligible)

if __name__ == "__main__":
    unittest.main()
