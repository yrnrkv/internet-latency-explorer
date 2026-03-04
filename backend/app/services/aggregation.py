"""Percentile and rolling-window aggregation helpers."""
import statistics
from typing import Sequence


def percentile(data: Sequence[float], p: float) -> float:
    """Return the p-th percentile (0–100) of data."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p / 100
    lo = int(k)
    hi = lo + 1
    frac = k - lo
    if hi >= len(sorted_data):
        return sorted_data[lo]
    return sorted_data[lo] * (1 - frac) + sorted_data[hi] * frac


def compute_stats(values: Sequence[float]) -> dict:
    if not values:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "avg": 0.0, "min": 0.0, "max": 0.0}
    return {
        "p50": percentile(values, 50),
        "p95": percentile(values, 95),
        "p99": percentile(values, 99),
        "avg": statistics.mean(values),
        "min": min(values),
        "max": max(values),
    }
