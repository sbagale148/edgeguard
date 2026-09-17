# EdgeGuard Security Documentation

Security features implemented in EdgeGuard and how they map to the threat model.

## Implemented Features

| Feature | Location | Description |
|---------|----------|-------------|
| API key auth | `backend/auth.py` | All endpoints require `X-API-Key` header |
| Rate limiting | `backend/rate_limit.py` | 100 requests/minute per client IP (configurable) |
| Input validation | `backend/schemas.py` | Pydantic models with length limits and enums |
| Safe error handling | `backend/app.py` | Generic 500 responses, no stack trace leakage |
| Batch size limits | `backend/schemas.py` | Max 100 events per batch ingest |
| Alert deduplication | `ml/detector.py` | Prevents duplicate alerts within 1-hour window |

## Threat Model

See [threat_model.md](threat_model.md) for the full analysis of assets, threats, mitigations, and known limitations.

## Configuration

Set these environment variables to customize security settings:

```bash
EDGEGUARD_API_KEY=your-secret-key        # Override default dev key
EDGEGUARD_RATE_LIMIT=100                  # Max requests per window
EDGEGUARD_RATE_WINDOW=60                  # Window in seconds
```

## Reflection

The hardest part was deciding how much security is "enough" for a learning project. I landed on implementing real patterns (auth, validation, rate limiting) without over-engineering things like JWT or distributed rate limiting that wouldn't add much learning value at this scale.

The API key in the frontend JavaScript is intentionally a known limitation — it makes the demo easy to run locally but would be the first thing I'd fix for any real deployment.
