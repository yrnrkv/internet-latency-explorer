"""Tests for ingestion models and auth middleware."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from datetime import datetime, timezone

from fastapi import HTTPException

from app.middleware.auth import verify_api_key
from app.models import IngestRequest, LatencySample


def _make_sample(**kwargs):
    defaults = dict(
        probe_id="p1",
        probe_city="NYC",
        probe_lat=40.7,
        probe_lng=-74.0,
        target_name="Google DNS",
        target_host="8.8.8.8",
        target_city="Mountain View",
        target_lat=37.4,
        target_lng=-122.1,
        target_type="service",
        latency_ms=20.0,
        jitter_ms=1.0,
        packet_loss=0.0,
        http_status=200,
        timestamp=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return LatencySample(**defaults)


class TestLatencySampleModel(unittest.TestCase):
    def test_valid(self):
        s = _make_sample()
        self.assertEqual(s.probe_id, "p1")

    def test_negative_latency_rejected(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            _make_sample(latency_ms=-1.0)

    def test_packet_loss_out_of_range(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            _make_sample(packet_loss=1.5)


class TestVerifyApiKey(unittest.TestCase):
    def test_valid_key(self):
        # Should not raise
        verify_api_key("dev-api-key")

    def test_invalid_key(self):
        with self.assertRaises(HTTPException) as ctx:
            verify_api_key("wrong-key")
        self.assertEqual(ctx.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
