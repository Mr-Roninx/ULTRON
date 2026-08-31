import sys
import os
import unittest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from simulator.world import world

class TestPhase6(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        world.reset()

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_simulator_seed(self):
        response = self.client.post("/simulator/seed")
        self.assertEqual(response.status_code, 200)
        self.assertIn("c_1001", world.customers)

    def test_simulator_clock_advance(self):
        self.client.post("/simulator/seed")
        response = self.client.post("/simulator/clock/advance?seconds=100")
        self.assertEqual(response.status_code, 200)
        
    def test_simulator_get_world(self):
        self.client.post("/simulator/seed")
        response = self.client.get("/simulator/world")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("customers", data)
        self.assertIn("payments", data)

    def test_agent_start_mission(self):
        req = {
            "customer_id": "c_1001",
            "target_recovery": 1000.0,
            "max_risk": 0.5,
            "authority": "AUTONOMOUS"
        }
        response = self.client.post("/agent/mission/start", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("mission_id", response.json())

    def test_evaluator_memories(self):
        self.client.post("/simulator/seed")
        # Empty memories initially
        response = self.client.get("/evaluator/memories/c_1001")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

if __name__ == '__main__':
    unittest.main()
