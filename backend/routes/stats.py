from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth import verify_api_key
from database import get_db
from models import Alert, Event
from rate_limit import check_rate_limit
from schemas import SummaryStats, TrendPoint

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


@router.get("/summary", response_model=SummaryStats)
def get_summary(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    check_rate_limit(request)
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)

    total_events = db.query(func.count(Event.id)).scalar() or 0
    total_alerts = db.query(func.count(Alert.id)).scalar() or 0
    unresolved = db.query(func.count(Alert.id)).filter(Alert.resolved.is_(False)).scalar() or 0
    events_last_hour = (
        db.query(func.count(Event.id)).filter(Event.timestamp >= one_hour_ago).scalar() or 0
    )

    top_types = (
        db.query(Event.event_type, func.count(Event.id).label("count"))
        .group_by(Event.event_type)
        .order_by(func.count(Event.id).desc())
        .limit(5)
        .all()
    )

    top_ips = (
        db.query(Event.source_ip, func.count(Event.id).label("count"))
        .group_by(Event.source_ip)
        .order_by(func.count(Event.id).desc())
        .limit(5)
        .all()
    )

    return SummaryStats(
        total_events=total_events,
        total_alerts=total_alerts,
        unresolved_alerts=unresolved,
        events_last_hour=events_last_hour,
        top_event_types=[{"type": t, "count": c} for t, c in top_types],
        top_source_ips=[{"ip": ip, "count": c} for ip, c in top_ips],
    )


@router.get("/trends", response_model=list[TrendPoint])
def get_trends(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
    hours: int = Query(24, ge=1, le=168),
):
    check_rate_limit(request)
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=hours)

    events = (
        db.query(Event)
        .filter(Event.timestamp >= start)
        .order_by(Event.timestamp.asc())
        .all()
    )

    buckets: dict[str, dict[str, int]] = {}
    for event in events:
        bucket = event.timestamp.replace(minute=0, second=0, microsecond=0).isoformat()
        if bucket not in buckets:
            buckets[bucket] = {"count": 0, "errors": 0, "auth_failures": 0}
        buckets[bucket]["count"] += 1
        if event.severity in ("error", "critical"):
            buckets[bucket]["errors"] += 1
        if event.event_type == "auth_attempt" and event.severity in ("warning", "error", "critical"):
            buckets[bucket]["auth_failures"] += 1

    return [
        TrendPoint(bucket=b, count=v["count"], errors=v["errors"], auth_failures=v["auth_failures"])
        for b, v in sorted(buckets.items())
    ]
