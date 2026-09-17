# EdgeGuard Frontend Dashboard

Vanilla JS dashboard for visualizing events, trends, and alerts. No build step required.

## Run

1. Start the backend API (see `backend/README.md`)
2. Seed data: `python backend/seed.py`
3. Open `index.html` in a browser, or serve it:

```bash
# Python
cd frontend
python -m http.server 8080
```

Then visit http://127.0.0.1:8080

## Features

- Summary stats (total events, alerts, hourly volume)
- 24-hour event trend chart (events, errors, auth failures)
- Active alerts with resolve action
- Top source IPs and event types
- Recent events table
- Manual "Run Analysis" to trigger anomaly detection
- Auto-refresh every 30 seconds

## Configuration

Edit `app.js` to change the API URL or key:

```javascript
const API_BASE = 'http://127.0.0.1:8000';
const API_KEY = 'edgeguard-dev-key-change-me';
```

Note: embedding the API key in frontend JS is fine for local demos but not for production. See `security/threat_model.md`.
