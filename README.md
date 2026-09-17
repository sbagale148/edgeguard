# EdgeGuard

A semester learning project that simulates how edge infrastructure teams detect abuse and anomalies. EdgeGuard ingests logs and events, runs statistical/ML anomaly detection, and visualizes results through a web dashboard.

**Disclaimer:** This is a learning project, not production-ready security software.

## Architecture

```
┌─────────────┐     REST API      ┌──────────────┐     ┌──────────┐
│  Dashboard  │ ◄──────────────► │  FastAPI     │ ◄──► │  SQLite  │
│  (vanilla)  │   X-API-Key      │  Backend     │      │  DB      │
└─────────────┘                   └──────┬───────┘      └──────────┘
                                         │
                                  ┌──────▼───────┐
                                  │  ML Detector │
                                  │  Z-score +   │
                                  │  Isolation   │
                                  │  Forest      │
                                  └──────────────┘
```

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
python seed.py               # Load demo data
python app.py                # Start API on :8000
```

### 2. Dashboard

```bash
cd frontend
python -m http.server 8080
```

Open http://127.0.0.1:8080 — click **Run Analysis** to detect the simulated attacker IP.

### 3. API Docs

Interactive docs at http://127.0.0.1:8000/docs

## Project Structure

```
edgeguard/
├── backend/       FastAPI server, SQLite storage, auth, rate limiting
├── frontend/      Dashboard (HTML/CSS/JS + Chart.js)
├── ml/            Anomaly detection (Z-score, Isolation Forest, rules)
├── security/      Threat model and security documentation
└── docs/          Development log
```

## Milestones

| # | Milestone | Status |
|---|-----------|--------|
| 1 | Project foundation | Done |
| 2 | Core backend & data flow | Done |
| 3 | Security & threat modeling | Done |
| 4 | ML anomaly detection | Done |
| 5 | Frontend dashboard | Done |
| 6 | Documentation & polish | Done |

## What It Detects

The seed data includes normal traffic from 5 IPs plus a simulated attacker (`203.0.113.99`) doing brute-force auth and high-volume scanning. Running analysis should flag:

- High-volume IP (Z-score)
- Auth brute-force (rule-based)
- Behavioral anomaly (Isolation Forest)

## What I'd Do Differently

- **Auth:** Per-client API keys with scopes instead of one shared key
- **Frontend:** Backend-for-frontend proxy so the API key isn't in JavaScript
- **ML:** Add a feedback loop for false positives; evaluate on real log data
- **Storage:** PostgreSQL for concurrent writes; time-series partitioning for events
- **Deployment:** Docker Compose with proper HTTPS via reverse proxy

## Documentation

- [Backend setup](backend/README.md)
- [Frontend dashboard](frontend/README.md)
- [ML detection](ml/README.md)
- [Security & threat model](security/threat_model.md)
- [Development log](docs/dev_log.md)
