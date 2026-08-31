import unittest
from backend.payment_intelligence.schemas import RailHealthStatus, RailType
from backend.payment_intelligence.rail_health import rail_health_engine

class TestGatewayHealth(unittest.TestCase):
    def setUp(self):
        rail_health_engine.reset()

    def test_default_healthy_state(self):
        health = rail_health_engine.get_gateway_health("GATEWAY_A")
        self.assertEqual(health.status, RailHealthStatus.HEALTHY)
        self.assertGreaterEqual(health.success_probability, 0.90)

    def test_degrade_and_restore_gateway(self):
        # Degrade to 20%
        degraded = rail_health_engine.degrade_gateway("GATEWAY_B", target_health=0.20)
        self.assertEqual(degraded.status, RailHealthStatus.DEGRADED)
        self.assertEqual(degraded.success_probability, 0.20)
        self.assertLess(degraded.recovery_trend, 0.0)

        # Best gateway should no longer be GATEWAY_B
        best_gw = rail_health_engine.get_best_gateway("CARD")
        self.assertNotEqual(best_gw, "GATEWAY_B")

        # Restore
        restored = rail_health_engine.restore_gateway("GATEWAY_B", target_health=0.95)
        self.assertEqual(restored.status, RailHealthStatus.HEALTHY)
        self.assertEqual(restored.success_probability, 0.95)
        self.assertGreater(restored.recovery_trend, 0.0)

if __name__ == "__main__":
    unittest.main()
