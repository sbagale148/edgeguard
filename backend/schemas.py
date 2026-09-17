from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class EventType(str, Enum):
    HTTP_REQUEST = "http_request"
    AUTH_ATTEMPT = "auth_attempt"
    LOG_ENTRY = "log_entry"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventCreate(BaseModel):
    event_type: EventType
    source_ip: str = Field(..., min_length=7, max_length=45)
    timestamp: datetime | None = None
    severity: Severity = Severity.INFO
    message: str = Field(..., min_length=1, max_length=2000)
    status_code: int | None = Field(None, ge=100, le=599)
    user_agent: str | None = Field(None, max_length=512)
    path: str | None = Field(None, max_length=512)
    metadata: dict[str, Any] | None = None

    @field_validator("source_ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("source_ip cannot be empty")
        return v

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        return v.strip()


class EventBatchCreate(BaseModel):
    events: list[EventCreate] = Field(..., min_length=1, max_length=100)


class EventResponse(BaseModel):
    id: int
    event_type: str
    source_ip: str
    timestamp: datetime
    severity: str
    message: str
    status_code: int | None
    user_agent: str | None
    path: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    source_ip: str | None
    score: float
    reason: str
    event_count: int
    created_at: datetime
    resolved: bool

    model_config = {"from_attributes": True}


class SummaryStats(BaseModel):
    total_events: int
    total_alerts: int
    unresolved_alerts: int
    events_last_hour: int
    top_event_types: list[dict[str, Any]]
    top_source_ips: list[dict[str, Any]]


class TrendPoint(BaseModel):
    bucket: str
    count: int
    errors: int
    auth_failures: int


class AnalyzeResponse(BaseModel):
    alerts_created: int
    events_analyzed: int
    message: str
