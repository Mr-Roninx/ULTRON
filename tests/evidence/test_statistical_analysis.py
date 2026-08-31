import unittest
from backend.evidence.statistical_analysis import calculate_paired_statistics
from backend.evidence.models import MechanismVerdict

class TestStatisticalAnalysis(unittest.TestCase):
    def test_positive_confidence_interval_yields_supported(self):
        """Positive paired differences with CI bounded strictly above 0 yield SUPPORTED."""
        diffs = [100.0, 150.0, 120.0, 80.0, 200.0, 95.0, 110.0, 140.0]
        stats = calculate_paired_statistics(diffs)
        self.assertEqual(stats.verdict, MechanismVerdict.SUPPORTED)
        self.assertGreater(stats.ci_95_lower, 0.0)

    def test_zero_crossing_confidence_interval_yields_inconclusive(self):
        """Zero-crossing confidence interval honestly yields INCONCLUSIVE."""
        diffs = [-50.0, 10.0, -20.0, 30.0, -10.0, 40.0]
        stats = calculate_paired_statistics(diffs)
        self.assertEqual(stats.verdict, MechanismVerdict.INCONCLUSIVE)
        self.assertLessEqual(stats.ci_95_lower, 0.0)
        self.assertGreaterEqual(stats.ci_95_upper, 0.0)

if __name__ == '__main__':
    unittest.main()
