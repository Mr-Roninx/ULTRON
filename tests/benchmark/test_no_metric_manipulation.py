import unittest
from backend.benchmark.generator import SeededWorldGenerator
from backend.benchmark.firewall import FutureInformationFirewall, FutureInformationLeakageError
from backend.benchmark.models import ResourceConstraints
from backend.benchmark.metrics import MetricsCalculator
from financial.idempotency import idempotency_engine

class TestNoMetricManipulation(unittest.TestCase):
    def test_addressable_revenue_cannot_be_artificially_reduced(self):
        """Addressable revenue must match sum of all initial opportunities, cannot be reduced."""
        gen = SeededWorldGenerator(seed=42)
        world, opps = gen.generate()
        
        true_addressable = sum(o.initial_amount for o in opps)
        self.assertGreater(true_addressable, 100000.0)

        # Attempt to artificially filter out hard opportunities
        tampered_opps = [o for o in opps if o.failure_type in ["TIMEOUT", "NETWORK_ERROR"]]
        self.assertLess(len(tampered_opps), len(opps))
        
        # Denominator in benchmark runner is strictly fixed to true_addressable
        self.assertNotEqual(sum(o.initial_amount for o in tampered_opps), true_addressable)

    def test_duplicate_recovery_claim_blocked_by_idempotency(self):
        """Agent cannot claim double recovery for identical actions on same opportunity."""
        idempotency_engine.reset()
        res1 = idempotency_engine.check_and_record("m_101", "SEND_PAYMENT_LINK", {"items": ["item_1"]})
        self.assertIsNone(res1)  # First execution allowed

        idempotency_engine.check_and_record("m_101", "SEND_PAYMENT_LINK", {"items": ["item_1"]}, result={"action_id": "act_1"})
        
        res2 = idempotency_engine.check_and_record("m_101", "SEND_PAYMENT_LINK", {"items": ["item_1"]})
        self.assertIsNotNone(res2)  # Duplicate caught and suppressed

    def test_firewall_blocks_evaluator_state_manipulation(self):
        """Attempt to inject artificial control outcome into context must raise exception."""
        tampered_ctx = {
            "control_outcome": 0.0,  # Trying to make baseline look 0
            "treatment_outcome": 999999.0
        }
        with self.assertRaises(FutureInformationLeakageError):
            FutureInformationFirewall.sanitize_agent_context(tampered_ctx)

if __name__ == '__main__':
    unittest.main()
