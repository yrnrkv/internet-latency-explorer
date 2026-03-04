"""Unit tests for the probe agent."""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure probe module is importable from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config  # noqa: E402
import probe  # noqa: E402


class TestLoadTargets(unittest.TestCase):
    def test_loads_from_file(self):
        data = {"targets": [{"name": "T1", "host": "1.1.1.1", "port": 443,
                              "city": "A", "lat": 0.0, "lng": 0.0, "type": "service"}]}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            tmp_path = f.name

        original = config.TARGETS_FILE
        config.TARGETS_FILE = tmp_path
        try:
            targets = probe.load_targets()
            self.assertEqual(len(targets), 1)
            self.assertEqual(targets[0]["name"], "T1")
        finally:
            config.TARGETS_FILE = original
            os.unlink(tmp_path)


class TestTcpPing(unittest.TestCase):
    def test_returns_none_on_refused(self):
        # Port 1 is almost never open; expect None (connection refused/timeout)
        result = asyncio.run(probe.tcp_ping("127.0.0.1", 1, timeout=0.5))
        self.assertIsNone(result)

    def test_returns_float_on_success(self):
        import socket
        # Create a listening socket to simulate a connectable host
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]
        try:
            result = asyncio.run(probe.tcp_ping("127.0.0.1", port, timeout=2.0))
            self.assertIsNotNone(result)
            self.assertGreaterEqual(result, 0)
        finally:
            server.close()


class TestMeasureTarget(unittest.TestCase):
    def _make_session(self):
        session = MagicMock()
        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(return_value=MagicMock(status=200))
        ctx.__aexit__ = AsyncMock(return_value=False)
        session.get.return_value = ctx
        return session

    def test_packet_loss_all_fail(self):
        target = {"name": "T", "host": "192.0.2.1", "port": 443,
                  "city": "X", "lat": 0.0, "lng": 0.0, "type": "service"}
        # All TCP pings fail; http also fails
        with patch("probe.tcp_ping", new=AsyncMock(return_value=None)), \
             patch("probe.http_latency", new=AsyncMock(return_value=(None, None))):
            result = asyncio.run(probe.measure_target(self._make_session(), target))
        self.assertEqual(result["packet_loss"], 1.0)
        self.assertEqual(result["latency_ms"], 0.0)

    def test_packet_loss_all_succeed(self):
        target = {"name": "T", "host": "8.8.8.8", "port": 443,
                  "city": "X", "lat": 1.0, "lng": 2.0, "type": "service"}
        with patch("probe.tcp_ping", new=AsyncMock(return_value=10.0)), \
             patch("probe.http_latency", new=AsyncMock(return_value=(12.0, 200))):
            result = asyncio.run(probe.measure_target(self._make_session(), target))
        self.assertEqual(result["packet_loss"], 0.0)
        self.assertGreater(result["latency_ms"], 0)
        self.assertEqual(result["http_status"], 200)


class TestSendSamples(unittest.TestCase):
    def test_returns_true_on_200(self):
        session = MagicMock()
        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(return_value=MagicMock(status=200))
        ctx.__aexit__ = AsyncMock(return_value=False)
        session.post.return_value = ctx
        result = asyncio.run(probe.send_samples(session, [{"foo": "bar"}]))
        self.assertTrue(result)

    def test_returns_false_on_exception(self):
        session = MagicMock()
        session.post.side_effect = Exception("network error")
        result = asyncio.run(probe.send_samples(session, [{"foo": "bar"}]))
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
