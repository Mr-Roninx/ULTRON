import unittest
from backend.evidence.anti_gaming import audit_repository_for_gaming

class TestEvidenceIntegrity(unittest.TestCase):
    def test_repository_anti_gaming_audit_passes(self):
        """Validates that no production logic contains hardcoded overrides or benchmark manipulation."""
        audit_res = audit_repository_for_gaming()
        self.assertFalse(audit_res["gaming_detected"], f"Gaming detected in repository: {audit_res['flagged_entries']}")
        self.assertGreater(audit_res["total_files_scanned"], 20)

if __name__ == '__main__':
    unittest.main()
