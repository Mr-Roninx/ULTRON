import unittest
from backend.benchmark.firewall import FutureInformationFirewall, FutureInformationLeakageError
from simulator.clock import clock

class TestFutureInformationFirewall(unittest.TestCase):
    def setUp(self):
        clock.reset(1000)

    def test_clean_context_passes_sanitization(self):
        clean_ctx = {
            "customer": {"id": "c_1", "segment": "B2B_ENTERPRISE"},
            "exposure": 5000.0,
            "recent_actions": ["SEND_MESSAGE"]
        }
        res = FutureInformationFirewall.sanitize_agent_context(clean_ctx)
        self.assertEqual(res, clean_ctx)

    def test_direct_control_outcome_leakage_blocked(self):
        leaked_ctx = {
            "customer": {"id": "c_1"},
            "control_outcome": 5000.0
        }
        with self.assertRaises(FutureInformationLeakageError):
            FutureInformationFirewall.sanitize_agent_context(leaked_ctx)

    def test_nested_incremental_recovery_leakage_blocked(self):
        leaked_ctx = {
            "customer": {"id": "c_1"},
            "history": {
                "evaluation": {
                    "nested": {
                        "incremental_recovery": 2400.0
                    }
                }
            }
        }
        with self.assertRaises(FutureInformationLeakageError):
            FutureInformationFirewall.sanitize_agent_context(leaked_ctx)

    def test_actual_recovery_field_blocked(self):
        leaked_ctx = {
            "customer": {"id": "c_1"},
            "actual_recovery": 1000.0
        }
        with self.assertRaises(FutureInformationLeakageError):
            FutureInformationFirewall.sanitize_agent_context(leaked_ctx)

    def test_temporal_future_peeking_blocked(self):
        clock.reset(5000)
        # Querying timestamp at t=5000 is allowed
        FutureInformationFirewall.verify_time_boundary(5000)
        
        # Querying timestamp at t=5001 is rejected
        with self.assertRaises(FutureInformationLeakageError):
            FutureInformationFirewall.verify_time_boundary(5001)

if __name__ == '__main__':
    unittest.main()
