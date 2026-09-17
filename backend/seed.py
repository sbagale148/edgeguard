"""
Generate realistic test event data for EdgeGuard development and demos.
"""

import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_backend = Path(__file__).resolve().parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from database import SessionLocal, init_db
from models import Event

NORMAL_IPS = ["10.0.1.10", "10.0.1.11", "10.0.1.12", "192.168.0.50", "172.16.0.5"]
ATTACKER_IP = "203.0.113.99"
PATHS = ["/api/users", "/api/login", "/api/data", "/health", "/static/app.js"]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X) Safari/17.0",
    "EdgeGuard-HealthCheck/1.0",
    "python-requests/2.31.0",
]


def _rand_time(hours_back: int = 48) -> datetime:
    now = datetime.now(timezone.utc)
    offset = random.randint(0, hours_back * 3600)
    return now - timedelta(seconds=offset)


def generate_normal_events(count: int = 200) -> list[Event]:
    events = []
    for _ in range(count):
        event_type = random.choices(
            ["http_request", "auth_attempt", "log_entry"],
            weights=[0.6, 0.2, 0.2],
        )[0]
        severity = random.choices(["info", "warning", "error"], weights=[0.85, 0.1, 0.05])[0]
        status = random.choice([200, 200, 200, 301, 404, 500]) if event_type == "http_request" else None

        if event_type == "auth_attempt":
            severity = random.choices(["info", "warning"], weights=[0.9, 0.1])[0]
            message = "Authentication successful" if severity == "info" else "Authentication failed"
        elif event_type == "http_request":
            message = f"HTTP {status} {random.choice(PATHS)}"
        else:
            message = random.choice([
                "Cache warmed successfully",
                "Background job completed",
                "Config reloaded",
            ])

        events.append(
            Event(
                event_type=event_type,
                source_ip=random.choice(NORMAL_IPS),
                timestamp=_rand_time(),
                severity=severity,
                message=message,
                status_code=status,
                user_agent=random.choice(USER_AGENTS),
                path=random.choice(PATHS),
            )
        )
    return events


def generate_attack_events(count: int = 80) -> list[Event]:
    """Simulate brute-force auth and high-volume scanning from one IP."""
    events = []
    for _ in range(count):
        is_auth = random.random() < 0.7
        events.append(
            Event(
                event_type="auth_attempt" if is_auth else "http_request",
                source_ip=ATTACKER_IP,
                timestamp=_rand_time(hours_back=2),
                severity="error" if is_auth else random.choice(["warning", "error"]),
                message="Authentication failed: invalid credentials" if is_auth else f"HTTP 403 {random.choice(PATHS)}",
                status_code=None if is_auth else random.choice([403, 404, 429]),
                user_agent="curl/7.68.0",
                path="/api/login" if is_auth else random.choice(PATHS),
            )
        )
    return events


def seed(clear: bool = False) -> None:
    init_db()
    db = SessionLocal()
    try:
        if clear:
            db.query(Event).delete()
            db.commit()
            print("Cleared existing events.")

        events = generate_normal_events(250) + generate_attack_events(80)
        db.add_all(events)
        db.commit()
        print(f"Seeded {len(events)} events ({len(NORMAL_IPS)} normal IPs + 1 attacker IP).")
    finally:
        db.close()


if __name__ == "__main__":
    clear_flag = "--clear" in sys.argv
    seed(clear=clear_flag)
