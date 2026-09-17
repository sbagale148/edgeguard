# EdgeGuard Backend

FastAPI REST API for event ingestion, storage, and anomaly detection.

## Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
# From the backend/ directory
python app.py
```

API docs: http://127.0.0.1:8000/docs

## Seed test data

```bash
python seed.py          # Add ~330 demo events
python seed.py --clear  # Clear existing events first
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (no auth) |
| POST | `/api/v1/events` | Ingest a single event |
| POST | `/api/v1/events/batch` | Ingest up to 100 events |
| GET | `/api/v1/events` | List events (filterable) |
| GET | `/api/v1/stats/summary` | Dashboard summary stats |
| GET | `/api/v1/stats/trends` | Hourly event trends |
| GET | `/api/v1/alerts` | List alerts |
| POST | `/api/v1/alerts/analyze` | Run anomaly detection |
| POST | `/api/v1/alerts/{id}/resolve` | Mark alert resolved |

All endpoints except `/health` require the `X-API-Key` header.

## Example: ingest an event

```bash
curl -X POST http://127.0.0.1:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -H "X-API-Key: edgeguard-dev-key-change-me" \
  -d '{
    "event_type": "http_request",
    "source_ip": "10.0.1.10",
    "severity": "info",
    "message": "GET /api/users 200",
    "status_code": 200,
    "path": "/api/users"
  }'
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EDGEGUARD_API_KEY` | `edgeguard-dev-key-change-me` | API authentication key |
| `EDGEGUARD_DATABASE_URL` | `sqlite:///edgeguard.db` | Database connection string |
| `EDGEGUARD_RATE_LIMIT` | `100` | Max requests per rate window |
| `EDGEGUARD_RATE_WINDOW` | `60` | Rate limit window (seconds) |
