from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from auth import verify_api_key
from database import get_db
from models import Event
from rate_limit import check_rate_limit
from schemas import EventBatchCreate, EventCreate, EventResponse

router = APIRouter(prefix="/api/v1/events", tags=["events"])


def _to_event(data: EventCreate) -> Event:
    return Event(
        event_type=data.event_type.value,
        source_ip=data.source_ip,
        timestamp=data.timestamp or datetime.now(timezone.utc),
        severity=data.severity.value,
        message=data.message,
        status_code=data.status_code,
        user_agent=data.user_agent,
        path=data.path,
    )


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event: EventCreate,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    check_rate_limit(request)
    db_event = _to_event(event)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@router.post("/batch", response_model=list[EventResponse], status_code=status.HTTP_201_CREATED)
def create_events_batch(
    batch: EventBatchCreate,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    check_rate_limit(request)
    db_events = [_to_event(e) for e in batch.events]
    db.add_all(db_events)
    db.commit()
    for e in db_events:
        db.refresh(e)
    return db_events


@router.get("", response_model=list[EventResponse])
def list_events(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    event_type: str | None = None,
    source_ip: str | None = None,
    severity: str | None = None,
):
    check_rate_limit(request)
    query = db.query(Event).order_by(Event.timestamp.desc())
    if event_type:
        query = query.filter(Event.event_type == event_type)
    if source_ip:
        query = query.filter(Event.source_ip == source_ip)
    if severity:
        query = query.filter(Event.severity == severity)
    return query.offset(offset).limit(limit).all()


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    check_rate_limit(request)
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event
