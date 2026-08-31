import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.llm.provider import LLMProvider, MockProvider, HuggingFaceProvider, LocalQwenProvider, LLMRouter
from backend.agent.schemas import AgentIntent
from backend.audit.ledger import audit_ledger

class FailingProvider(LLMProvider):
    def __init__(self, error_type=RuntimeError, msg="Mock Provider Failure"):
        self.error_type = error_type
        self.msg = msg
        
    def health(self) -> bool:
        return False
        
    def generate_intent(self, messages, schemas) -> AgentIntent:
        raise self.error_type(self.msg)

class SuccessProvider(LLMProvider):
    def __init__(self, intent: AgentIntent):
        self.intent = intent
        
    def health(self) -> bool:
        return True
        
    def generate_intent(self, messages, schemas) -> AgentIntent:
        return self.intent

class TestAdversarialLLMFailover(unittest.TestCase):
    def setUp(self):
        audit_ledger.reset()

    def test_primary_hf_success_uses_primary(self):
        """When primary succeeds, result is returned and no failover event is logged."""
        expected_intent = AgentIntent(action_type="RECONCILE", reasoning="HF Success", expected_yield=100.0, payload={})
        router = LLMRouter(
            primary=SuccessProvider(expected_intent),
            fallback=FailingProvider(),
            active_provider_name="AUTO"
        )
        res = router.generate_intent([], [])
        self.assertEqual(res.action_type, "RECONCILE")
        
        trace = audit_ledger.get_trace()
        self.assertTrue(any(e.event_type == "LLM_INFERENCE_SUCCESS" for e in trace))
        self.assertFalse(any(e.event_type == "LLM_FAILOVER_TRIGGERED" for e in trace))

    def test_hf_failure_fails_over_to_local_qwen(self):
        """When HF encounters an error, router logs LLM_FAILOVER_TRIGGERED and successfully falls back to Local Qwen."""
        fallback_intent = AgentIntent(action_type="SEND_MESSAGE", reasoning="Local Qwen fallback", expected_yield=50.0, payload={})
        router = LLMRouter(
            primary=FailingProvider(error_type=TimeoutError, msg="HF Cloud Timeout (10s)"),
            fallback=SuccessProvider(fallback_intent),
            active_provider_name="AUTO"
        )
        res = router.generate_intent([], [])
        self.assertEqual(res.action_type, "SEND_MESSAGE")

        trace = audit_ledger.get_trace()
        self.assertTrue(any(e.event_type == "LLM_FAILOVER_TRIGGERED" for e in trace))
        self.assertTrue(any(e.event_type == "LLM_INFERENCE_SUCCESS" for e in trace))

    def test_both_providers_fail_yields_safe_failure_without_crashing(self):
        """When both HF and Local Qwen fail, router safely falls back to WAIT action and logs LLM_FALLBACK_FAILED."""
        router = LLMRouter(
            primary=FailingProvider(error_type=ConnectionError, msg="HF Offline"),
            fallback=FailingProvider(error_type=TimeoutError, msg="Local Qwen Unreachable"),
            active_provider_name="AUTO"
        )
        res = router.generate_intent([], [])
        self.assertEqual(res.action_type, "WAIT")
        self.assertIn("Safe failure", res.reasoning)

        trace = audit_ledger.get_trace()
        self.assertTrue(any(e.event_type == "LLM_FAILOVER_TRIGGERED" for e in trace))
        self.assertTrue(any(e.event_type == "LLM_FALLBACK_FAILED" for e in trace))

if __name__ == '__main__':
    unittest.main()
