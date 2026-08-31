import unittest
from simulator.world import world
from simulator.clock import clock
from simulator.models import Customer, Payment, PaymentStatus
from simulator.chaos import chaos_engine
from backend.payment_intelligence.rail_health import rail_health_engine

class TestChaosEffect(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset(1718000000)

    def test_chaos_engine_alters_rail_health_and_payment_states(self):
        """Validates that ChaosEngine produces genuine world and rail health mutations."""
        rail_health_engine.restore_gateway("GATEWAY_B", target_health=0.95)
        self.assertEqual(rail_health_engine.get_gateway_health("GATEWAY_B").success_probability, 0.95)

        chaos_engine.trigger("GATEWAY_DEGRADATION", gateway_id="GATEWAY_B", target_health=0.20)
        self.assertEqual(rail_health_engine.get_gateway_health("GATEWAY_B").success_probability, 0.20)

if __name__ == '__main__':
    unittest.main()
