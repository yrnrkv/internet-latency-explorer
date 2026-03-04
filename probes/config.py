import os

PROBE_ID = os.environ.get("PROBE_ID", "probe-local")
PROBE_CITY = os.environ.get("PROBE_CITY", "Local")
PROBE_LAT = float(os.environ.get("PROBE_LAT", "0.0"))
PROBE_LNG = float(os.environ.get("PROBE_LNG", "0.0"))
API_URL = os.environ.get("API_URL", "http://localhost:8000")
API_KEY = os.environ.get("API_KEY", "dev-api-key")
INTERVAL_SECONDS = int(os.environ.get("INTERVAL_SECONDS", "10"))
SAMPLES_PER_TARGET = int(os.environ.get("SAMPLES_PER_TARGET", "3"))
TARGETS_FILE = os.environ.get("TARGETS_FILE", "targets.json")
