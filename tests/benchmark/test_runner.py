import unittest
import os
from backend.benchmark.runner import BenchmarkRunner

class TestBenchmarkRunner(unittest.TestCase):
    def setUp(self):
        self.runner = BenchmarkRunner(output_dir="results")

    def test_run_single_experiment_completes_and_returns_all_metrics(self):
        """Verify single experiment runs across all 10 strategies (baselines + ablations)."""
        res = self.runner.run_single_experiment(seed=42, horizon_days=7)
        
        self.assertIn("metrics", res)
        metrics = res["metrics"]
        
        # Verify all 4 baselines + ULTRON + 5 ablations exist
        expected_strats = [
            "NoAction", "FixedRetry", "TraditionalDunning", "RuleBasedRecovery",
            "FULL_ULTRON", "ULTRON_NO_INTERFERENCE", "ULTRON_NO_MEMORY",
            "ULTRON_NO_REPLANNING", "ULTRON_NO_DECAY", "ULTRON_NO_RELATIONSHIP_COST"
        ]
        for s in expected_strats:
            self.assertIn(s, metrics)
            self.assertGreaterEqual(metrics[s].gross_recovery, 0.0)

    def test_benchmark_suite_writes_json_artifact(self):
        """Verify benchmark suite produces results/benchmark_results.json."""
        suite_res = self.runner.run_benchmark_suite(seeds=[42], horizons=[7], include_chaos=False)
        self.assertTrue(os.path.exists("results/benchmark_results.json"))
        self.assertIn("aggregated_metrics", suite_res)

if __name__ == '__main__':
    unittest.main()
