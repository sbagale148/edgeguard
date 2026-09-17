import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("EDGEGUARD_DATABASE_URL", f"sqlite:///{BASE_DIR / 'edgeguard.db'}")

# Default API key for local dev — override via EDGEGUARD_API_KEY env var
DEFAULT_API_KEY = os.getenv("EDGEGUARD_API_KEY", "edgeguard-dev-key-change-me")

# Rate limiting: max requests per window per client IP
RATE_LIMIT_REQUESTS = int(os.getenv("EDGEGUARD_RATE_LIMIT", "100"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("EDGEGUARD_RATE_WINDOW", "60"))

# Anomaly detection thresholds
ANOMALY_ZSCORE_THRESHOLD = float(os.getenv("EDGEGUARD_ZSCORE_THRESHOLD", "2.5"))
ANOMALY_MIN_EVENTS = int(os.getenv("EDGEGUARD_MIN_EVENTS", "10"))
