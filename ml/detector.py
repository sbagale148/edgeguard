"""
EdgeGuard anomaly detection.

Uses statistical methods (Z-score) and Isolation Forest to flag suspicious
patterns in edge event data. Kept separate from the main API so the ML logic
can evolve independently.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy import func
from sqlalchemy.orm import Session

_backend = Path(__file__).resolve().parent.parent / "backend"
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from config import ANOMALY_MIN_EVENTS, ANOMALY_ZSCORE_THRESHOLD  # noqa: E402
from models import Alert, Event  # noqa: E402


def _zscore(values: list[float]) -> list[float]:
    if len(values) < 2:
        return [0.0] * len(values)
    arr = np.array(values, dtype=float)
    mean = arr.mean()
    std = arr.std()
    if std == 0:
        return [0.0] * len(values)
    return ((arr - mean) / std).tolist()


def _recent_unresolved_alert(db: Session, alert_type: str, source_ip: str | None) -> Alert | None:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
    query = (
        db.query(Alert)
        .filter(
            Alert.alert_type == alert_type,
            Alert.resolved.is_(False),
            Alert.created_at >= cutoff,
        )
    )
    if source_ip:
        query = query.filter(Alert.source_ip == source_ip)
    return query.first()


def _create_alert(
    db: Session,
    alert_type: str,
    severity: str,
    source_ip: str | None,
    score: float,
    reason: str,
    event_count: int = 1,
) -> Alert | None:
    if _recent_unresolved_alert(db, alert_type, source_ip):
        return None
    alert = Alert(
        alert_type=alert_type,
        severity=severity,
        source_ip=source_ip,
        score=round(score, 3),
        reason=reason,
        event_count=event_count,
    )
    db.add(alert)
    return alert


def detect_ip_rate_anomalies(db: Session, hours: int = 1) -> int:
    """Flag IPs with unusually high event volume using Z-scores."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    rows = (
        db.query(Event.source_ip, func.count(Event.id).label("count"))
        .filter(Event.timestamp >= cutoff)
        .group_by(Event.source_ip)
        .all()
    )
    if len(rows) < ANOMALY_MIN_EVENTS:
        return 0

    ips = [r.source_ip for r in rows]
    counts = [float(r.count) for r in rows]
    scores = _zscore(counts)
    created = 0

    for ip, count, z in zip(ips, counts, scores):
        if z >= ANOMALY_ZSCORE_THRESHOLD:
            alert = _create_alert(
                db,
                alert_type="high_volume_ip",
                severity="warning" if z < 4 else "critical",
                source_ip=ip,
                score=z,
                reason=f"IP {ip} generated {int(count)} events in the last {hours}h (z-score: {z:.2f})",
                event_count=int(count),
            )
            if alert:
                created += 1
    return created


def detect_auth_bruteforce(db: Session, hours: int = 1, threshold: int = 10) -> int:
    """Flag IPs with many failed auth attempts."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    rows = (
        db.query(Event.source_ip, func.count(Event.id).label("count"))
        .filter(
            Event.timestamp >= cutoff,
            Event.event_type == "auth_attempt",
            Event.severity.in_(("warning", "error", "critical")),
        )
        .group_by(Event.source_ip)
        .all()
    )
    created = 0
    for row in rows:
        if row.count >= threshold:
            alert = _create_alert(
                db,
                alert_type="auth_bruteforce",
                severity="critical" if row.count >= threshold * 2 else "warning",
                source_ip=row.source_ip,
                score=float(row.count) / threshold,
                reason=f"IP {row.source_ip} had {row.count} failed auth attempts in {hours}h",
                event_count=row.count,
            )
            if alert:
                created += 1
    return created


def detect_isolation_forest_anomalies(db: Session, hours: int = 24) -> int:
    """
    Use Isolation Forest on per-IP feature vectors:
    [total_events, error_count, auth_failures, unique_paths]
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    events = db.query(Event).filter(Event.timestamp >= cutoff).all()
    if len(events) < ANOMALY_MIN_EVENTS:
        return 0

    ip_features: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, set()])
    for event in events:
        feats = ip_features[event.source_ip]
        feats[0] += 1
        if event.severity in ("error", "critical"):
            feats[1] += 1
        if event.event_type == "auth_attempt" and event.severity != "info":
            feats[2] += 1
        if event.path:
            feats[3].add(event.path)

    ips = list(ip_features.keys())
    matrix = np.array(
        [[f[0], f[1], f[2], len(f[3])] for f in ip_features.values()],
        dtype=float,
    )

    if len(ips) < 5:
        return 0

    model = IsolationForest(contamination=0.1, random_state=42, n_estimators=100)
    predictions = model.fit_predict(matrix)
    scores = -model.score_samples(matrix)

    created = 0
    for ip, pred, score, feats in zip(ips, predictions, scores, ip_features.values()):
        if pred == -1:
            alert = _create_alert(
                db,
                alert_type="behavioral_anomaly",
                severity="warning",
                source_ip=ip,
                score=float(score),
                reason=(
                    f"IP {ip} shows unusual behavior pattern: "
                    f"{feats[0]} events, {feats[1]} errors, {feats[2]} auth failures"
                ),
                event_count=feats[0],
            )
            if alert:
                created += 1
    return created


def detect_error_spike(db: Session, hours: int = 24) -> int:
    """Detect sudden spikes in error-rate across all events."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    events = (
        db.query(Event)
        .filter(Event.timestamp >= cutoff)
        .order_by(Event.timestamp.asc())
        .all()
    )
    if len(events) < ANOMALY_MIN_EVENTS:
        return 0

    hourly: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for event in events:
        bucket = event.timestamp.replace(minute=0, second=0, microsecond=0).isoformat()
        hourly[bucket][0] += 1
        if event.severity in ("error", "critical"):
            hourly[bucket][1] += 1

    buckets = sorted(hourly.keys())
    error_rates = [hourly[b][1] / max(hourly[b][0], 1) for b in buckets]
    zscores = _zscore(error_rates)

    created = 0
    for bucket, rate, z in zip(buckets, error_rates, zscores):
        if z >= ANOMALY_ZSCORE_THRESHOLD and rate > 0.1:
            alert = _create_alert(
                db,
                alert_type="error_spike",
                severity="warning",
                source_ip=None,
                score=z,
                reason=f"Error rate spike at {bucket}: {rate:.0%} of events were errors (z={z:.2f})",
                event_count=hourly[bucket][0],
            )
            if alert:
                created += 1
    return created


def run_anomaly_detection(db: Session) -> tuple[int, int]:
    """Run all detectors and return (alerts_created, events_analyzed)."""
    events_analyzed = db.query(func.count(Event.id)).scalar() or 0

    created = 0
    created += detect_ip_rate_anomalies(db)
    created += detect_auth_bruteforce(db)
    created += detect_isolation_forest_anomalies(db)
    created += detect_error_spike(db)

    db.commit()
    return created, events_analyzed
