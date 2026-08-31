import unittest
import json
from backend.benchmark.models import StrategyMetrics
from backend.benchmark.metrics import MetricsCalculator

class TestResultIntegrity(unittest.TestCase):
    def test_strategy_metrics_json_serialization(self):
        """StrategyMetrics must serialize to JSON cleanly with exact numerical fidelity."""
        m = StrategyMetrics(
            strategy_name="FULL_ULTRON",
            seed=42,
            horizon_days=30,
            revenue_at_risk=450000.0,
            addressable_revenue=450000.0,
            natural_recovery=45000.0,
            gross_recovery=315000.0,
            incremental_recovery=270000.0,
            net_incremental_recovery=268500.0,
            recovery_rate=0.70,
            incremental_recovery_rate=0.60,
            actions_attempted=180,
            actions_successful=175,
            actions_blocked=5,
            escalations=12,
            customer_contacts=120,
            replans=15,
            avg_time_to_recovery_hours=18.5,
            intervention_cost=450.0,
            relationship_cost=800.0,
            risk_cost=250.0,
            total_cost=1500.0
        )

        data = m.model_dump()
        json_str = json.dumps(data)
        loaded = json.loads(json_str)

        self.assertEqual(loaded["strategy_name"], "FULL_ULTRON")
        self.assertEqual(loaded["gross_recovery"], 315000.0)
        self.assertEqual(loaded["net_incremental_recovery"], 268500.0)
        self.assertEqual(loaded["actions_attempted"], 180)

if __name__ == '__main__':
    unittest.main()
