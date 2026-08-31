import sys
import os
import unittest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.main import app
from simulator.world import world

class TestAdversarialAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        world.reset()

    def test_nonexistent_mission_stepping_returns_404(self):
        """Stepping an unknown mission ID returns HTTP 404 cleanly."""
        res = self.client.post("/agent/mission/m_nonexistent_999/step")
        self.assertEqual(res.status_code, 404)
        self.assertIn("not found", res.json()["detail"].lower())

    def test_nonexistent_mission_context_returns_404(self):
        """Querying context of unknown mission returns HTTP 404."""
        res = self.client.get("/agent/mission/m_nonexistent_999/context")
        self.assertEqual(res.status_code, 404)

    def test_clock_advance_with_negative_seconds_returns_400(self):
        """Advancing clock by negative time is rejected with HTTP 400."""
        res = self.client.post("/simulator/clock/advance?seconds=-50")
        self.assertEqual(res.status_code, 400)

    def test_malformed_json_to_start_mission_returns_422(self):
        """Sending malformed schema returns HTTP 422 Unprocessable Entity."""
        res = self.client.post("/agent/mission/start", json={"bad_field": 123})
        self.assertEqual(res.status_code, 422)

    def test_evaluator_replay_empty_memories_returns_empty_list(self):
        """Running replay on a customer with no memories returns empty result without crashing."""
        res = self.client.post("/evaluator/replay/c_empty_999")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["results"], [])

if __name__ == '__main__':
    unittest.main()
