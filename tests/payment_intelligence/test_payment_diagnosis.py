import unittest
from backend.payment_intelligence.schemas import FailureClass, RailHealthStatus
from backend.payment_intelligence.payment_diagnosis import payment_diagnosis_engine
from backend.payment_intelligence.rail_health import rail_health_engine

class TestPaymentDiagnosis(unittest.TestCase):
    def setUp(self):
        rail_health_engine.reset()

    def test_transient_issuer_failure_diagnosis(self):
        payment = {
            "id": "p_100",
            "customer_id": "c_ananya",
            "amount": 8200.0,
            "failure_code": "91", # ISO 8583 Issuer Unavailable
            "gateway_id": "gateway_a",
            "rail": "CARD",
            "attempt_count": 1
        }
        customer = {
            "id": "c_ananya",
            "name": "Ananya Textiles",
            "segment": "B2B_ENTERPRISE",
            "risk_band": "LOW"
        }

        diagnosis = payment_diagnosis_engine.diagnose(
            payment=payment,
            customer=customer,
            gateway_id="gateway_a",
            raw_failure_code="91"
        )

        self.assertEqual(diagnosis.primary_reason, "ISSUER_UNAVAILABLE")
        self.assertEqual(diagnosis.failure_class, FailureClass.INFRASTRUCTURE)
        self.assertTrue(diagnosis.retry_eligible)
        self.assertFalse(diagnosis.customer_action_required)
        self.assertIn("RETRY", diagnosis.suggested_actions)
        self.assertIn("ESCALATE", diagnosis.prohibited_actions)
        self.assertGreaterEqual(diagnosis.recoverability, 0.70)

    def test_diagnosis_when_gateway_is_down(self):
        # Degrade gateway to DOWN
        rail_health_engine.update_gateway_health("GATEWAY_A", success_probability=0.10, status=RailHealthStatus.DOWN)

        payment = {
            "id": "p_101",
            "customer_id": "c_ananya",
            "amount": 8200.0,
            "failure_code": "96",
            "gateway_id": "GATEWAY_A",
            "rail": "CARD"
        }

        diagnosis = payment_diagnosis_engine.diagnose(
            payment=payment,
            gateway_id="GATEWAY_A",
            raw_failure_code="96"
        )

        # RETRY should be prohibited and SWITCH_PERMITTED_RAIL should be suggested
        self.assertIn("RETRY", diagnosis.prohibited_actions)
        self.assertIn("SWITCH_PERMITTED_RAIL", diagnosis.suggested_actions)
        self.assertFalse(diagnosis.retry_eligible)

if __name__ == "__main__":
    unittest.main()
