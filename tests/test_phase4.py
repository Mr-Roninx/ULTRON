import sys
import os
import unittest
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.llm.functions import schema_generator
from backend.llm.context import context_manager
from backend.llm.prompts import prompts
from backend.llm.provider import MockProvider
from backend.agent.schemas import AgentIntent
from backend.agent.loop import AgentLoop
from backend.agent.state_machine import AgentPhase
from simulator.models import Customer, Payment, PaymentStatus
from simulator.world import world

class TestPhase4(unittest.TestCase):
    def setUp(self):
        world.reset()
        
    def test_schema_generator_filters_infeasible(self):
        feasible = ["WAIT", "RECONCILE"]
        schemas = schema_generator.get_tool_schemas(feasible)
        self.assertEqual(len(schemas), 2)
        names = [s["function"]["name"] for s in schemas]
        self.assertIn("WAIT", names)
        self.assertIn("RECONCILE", names)
        
    def test_context_manager_format_state(self):
        state = context_manager.format_state({"key": "val"}, ["WAIT"])
        parsed = json.loads(state)
        self.assertEqual(parsed["snapshot"]["key"], "val")
        self.assertEqual(parsed["feasible_actions"], ["WAIT"])
        
    def test_context_manager_build_prompt(self):
        messages = context_manager.build_prompt("system", "state", "memory")
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]["content"], "system")
        self.assertEqual(messages[1]["content"], "memory")
        self.assertIn("state", messages[2]["content"])
        
    def test_mock_provider_determinism(self):
        intent1 = AgentIntent(action_type="WAIT", reasoning="test", expected_yield=0, payload={})
        intent2 = AgentIntent(action_type="STOP", reasoning="test2", expected_yield=0, payload={})
        provider = MockProvider([intent1, intent2])
        
        res1 = provider.generate_intent([], [])
        self.assertEqual(res1.action_type, "WAIT")
        
        res2 = provider.generate_intent([], [])
        self.assertEqual(res2.action_type, "STOP")
        
        res3 = provider.generate_intent([], []) # fallback
        self.assertEqual(res3.action_type, "WAIT")
        
    def test_agent_loop_with_mock_provider(self):
        world.add_customer(Customer(id="c_1", name="Test", segment="B2B", created_at=0))
        world.add_payment(Payment(id="p_1", customer_id="c_1", amount=100, status=PaymentStatus.UNKNOWN, created_at=0))
        
        intent = AgentIntent(action_type="RECONCILE", reasoning="test", expected_yield=100.0, payload={"payment_id": "p_1"})
        provider = MockProvider([intent])
        
        loop = AgentLoop("c_1", "m_1", llm_provider=provider)
        
        # Run loop until complete
        while loop.fsm.current() not in [AgentPhase.COMPLETE, AgentPhase.ESCALATE]:
            loop.tick()
            
        self.assertEqual(loop.fsm.current(), AgentPhase.COMPLETE)
        self.assertEqual(loop.chosen_intent.action_type, "RECONCILE")
        
if __name__ == '__main__':
    unittest.main()
