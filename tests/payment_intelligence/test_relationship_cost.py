import unittest
from backend.economics.relationship import RelationshipState

class TestRelationshipCost(unittest.TestCase):
    def test_relationship_cost_fatigue_and_sensitivity(self):
        # 1. Low fatigue SMB
        rel_smb = RelationshipState(
            customer_id="c_smb",
            customer_segment="SMB",
            recent_contacts=0,
            silence_duration=86400 * 5
        )
        cost_smb = rel_smb.calculate_relationship_cost("SEND_MESSAGE")
        self.assertEqual(cost_smb, 4.0) # 4 * 1.0 * 1.0 * 1.0

        # 2. Enterprise with 2 recent contacts and short silence duration
        rel_ent = RelationshipState(
            customer_id="c_ent",
            customer_segment="B2B_ENTERPRISE",
            recent_contacts=2,
            silence_duration=1800 # 30 mins ago
        )
        cost_ent = rel_ent.calculate_relationship_cost("SEND_MESSAGE")
        # Base 4 * (1 + 2^1.5 * 0.5 = 2.414) * 2.2 * 2.5 = 53.11
        self.assertGreater(cost_ent, 40.0)

        # 3. Opted-out customer
        rel_optout = RelationshipState(
            customer_id="c_opt",
            opt_out=True
        )
        self.assertEqual(rel_optout.calculate_relationship_cost("SEND_MESSAGE"), float('inf'))

if __name__ == "__main__":
    unittest.main()
