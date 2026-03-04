"""Tests for latency service helpers."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from app.services.aggregation import percentile, compute_stats


class TestLatencyAggregation(unittest.TestCase):
    def test_p50_sorted(self):
        data = [5.0, 10.0, 15.0, 20.0, 25.0]
        self.assertAlmostEqual(percentile(data, 50), 15.0)

    def test_p95_large(self):
        import random
        random.seed(42)
        data = [random.uniform(10, 100) for _ in range(1000)]
        p95 = percentile(data, 95)
        sorted_data = sorted(data)
        # Should be in the top 5%
        self.assertGreater(p95, sorted_data[900])

    def test_compute_stats_consistency(self):
        data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        stats = compute_stats(data)
        self.assertLessEqual(stats["p50"], stats["p95"])
        self.assertLessEqual(stats["p95"], stats["p99"])
        self.assertEqual(stats["min"], 1.0)
        self.assertEqual(stats["max"], 10.0)


if __name__ == "__main__":
    unittest.main()
