import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from auth import verify_api_key
from database import get_db
from models import Alert
from rate_limit import check_rate_limit
from schemas import AlertResponse, AnalyzeResponse

# Allow importing ml module from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from ml.detector import run_anomaly_detection  # noqa: E402

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
def list_alerts(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
    limit: int = Query(50, ge=1, le=200),
    unresolved_only: bool = False,
):
    check_rate_limit(request)
    query = db.query(Alert).order_by(Alert.created_at.desc())
    if unresolved_only:
        query = query.filter(Alert.resolved.is_(False))
    return query.limit(limit).all()


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    check_rate_limit(request)
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    alert.resolved = True
    db.commit()
    db.refresh(alert)
    return alert


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_events(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    check_rate_limit(request)
    alerts_created, events_analyzed = run_anomaly_detection(db)
    return AnalyzeResponse(
        alerts_created=alerts_created,
        events_analyzed=events_analyzed,
        message=f"Analysis complete. Created {alerts_created} new alert(s).",
    )
