import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.economics.engine import economic_engine
from backend.economics.relationship import RelationshipState

class TestAdversarialEconomicEngine(unittest.TestCase):
    def test_zero_recovery_leads_to_negative_nev(self):
        """When expected recovery is 0, any costly action must yield negative NEV."""
        context = {
            "expected_yield": 0.0,
            "risk_score": 0.1,
            "relationship_state": RelationshipState(
                customer_id="c_1",
                recent_contacts=2,
                recent_responses=1,
                successful_prior_recoveries=0,
                customer_value=50000.0,
                complaints=0,
                opt_out=False,
                silence_duration=0
            )
        }
        res = economic_engine.evaluate_action("RETRY", context)
        self.assertTrue(res["net_expected_value"] < 0)

    def test_extreme_relationship_cost_for_opted_out_customer(self):
        """Customer who opted out must produce infinite relationship cost, prohibiting contact."""
        rel = RelationshipState(
            customer_id="c_1",
            recent_contacts=0,
            recent_responses=0,
            successful_prior_recoveries=0,
            customer_value=10000.0,
            complaints=5,
            opt_out=True,
            silence_duration=0
        )
        cost = rel.relationship_cost_proxy()
        self.assertEqual(cost, float('inf'))

    def test_extreme_customer_complaints_inflate_relationship_cost(self):
        """Customer with 10 complaints has relationship cost exceeding $1000."""
        rel = RelationshipState(
            customer_id="c_1",
            recent_contacts=1,
            recent_responses=0,
            successful_prior_recoveries=0,
            customer_value=10000.0,
            complaints=10,
            opt_out=False,
            silence_duration=0
        )
        cost = rel.relationship_cost_proxy()
        self.assertTrue(cost >= 1000.0)

    def test_large_amounts_floating_point_determinism(self):
        """Evaluating massive enterprise exposure values ($100M) remains numerically stable."""
        context = {
            "expected_yield": 100000000.0, # $100M
            "risk_score": 0.05,
            "relationship_state": None
        }
        res1 = economic_engine.evaluate_action("RECONCILE", context)
        res2 = economic_engine.evaluate_action("RECONCILE", context)
        self.assertEqual(res1["net_expected_value"], res2["net_expected_value"])
        # NEV = 100,000,000 - 0.5 (action) - 0 (rel) - 5,000,000 (risk) = 94,999,999.5
        self.assertAlmostEqual(res1["net_expected_value"], 94999999.5, places=2)

if __name__ == '__main__':
    unittest.main()
