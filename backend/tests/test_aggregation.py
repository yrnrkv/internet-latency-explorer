"""Tests for the aggregation service."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from app.services.aggregation import percentile, compute_stats


class TestPercentile(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(percentile([], 50), 0.0)

    def test_single(self):
        self.assertEqual(percentile([42.0], 50), 42.0)

    def test_median(self):
        self.assertAlmostEqual(percentile([1, 2, 3, 4, 5], 50), 3.0)

    def test_p95(self):
        data = list(range(1, 101))  # 1..100
        self.assertAlmostEqual(percentile(data, 95), 95.05, places=1)

    def test_p99(self):
        data = list(range(1, 101))
        result = percentile(data, 99)
        self.assertGreater(result, 98)
        self.assertLessEqual(result, 100)


class TestComputeStats(unittest.TestCase):
    def test_empty(self):
        stats = compute_stats([])
        self.assertEqual(stats["p50"], 0.0)

    def test_values(self):
        stats = compute_stats([10.0, 20.0, 30.0, 40.0, 50.0])
        self.assertAlmostEqual(stats["avg"], 30.0)
        self.assertEqual(stats["min"], 10.0)
        self.assertEqual(stats["max"], 50.0)


if __name__ == "__main__":
    unittest.main()
