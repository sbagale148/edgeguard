# EdgeGuard Threat Model

A learning-project threat model documenting what EdgeGuard protects, what could go wrong, and what we're explicitly not protecting.

## Assets

| Asset | Description | Sensitivity |
|-------|-------------|-------------|
| Event data | Logs, HTTP requests, auth attempts ingested via API | Medium — may contain IPs, paths, user agents |
| Alert data | Anomaly detection results and scores | Medium — reveals detection logic |
| API key | Shared secret for ingestion and queries | High — grants full API access |
| SQLite database | Local storage of events and alerts | Medium |

## Trust Boundaries

```
[External clients] --HTTPS/API--> [EdgeGuard API] --> [SQLite DB]
                                        |
                                   [ML Detector]
                                        |
                              [Dashboard (browser)]
```

- External clients send events via authenticated API
- Dashboard reads from the same API (browser-side API key — dev only)
- ML runs server-side on stored events

## Threats & Mitigations

### T1: Unauthorized API access
- **Threat:** Attacker sends fake events or reads sensitive data without credentials
- **Mitigation:** API key required on all endpoints (`X-API-Key` header)
- **Limitation:** Single shared key, no per-client keys or rotation in v1

### T2: API abuse / DoS
- **Threat:** Attacker floods ingestion endpoint to exhaust resources
- **Mitigation:** Per-IP rate limiting (100 req/min default), batch size capped at 100 events
- **Limitation:** In-memory rate limiter resets on restart; no distributed rate limiting

### T3: Malicious input / injection
- **Threat:** Oversized payloads, malformed data, or injection via event fields
- **Mitigation:** Pydantic validation (field length limits, enum types, IP format checks), SQLAlchemy ORM (parameterized queries)
- **Limitation:** No deep IP format validation; metadata field accepted but not stored (stripped)

### T4: Information disclosure via errors
- **Threat:** Stack traces or internal paths leaked in error responses
- **Mitigation:** Generic 500 handler returns `"An internal error occurred"`; validation errors are structured but don't expose internals
- **Limitation:** 404/401 messages are minimal but predictable

### T5: Data tampering
- **Threat:** Attacker modifies stored events or alerts
- **Mitigation:** No public update/delete endpoints for events; alerts can only be marked resolved
- **Limitation:** No audit log of who resolved alerts

### T6: False negatives in detection
- **Threat:** Real attacks go undetected
- **Mitigation:** Multiple detection methods (Z-score, Isolation Forest, rule-based auth threshold)
- **Limitation:** Tuned for demo data; not validated against real attack traffic

### T7: False positives
- **Threat:** Legitimate traffic flagged as attacks
- **Mitigation:** Deduplication window (1h) prevents alert spam; configurable Z-score threshold
- **Limitation:** No feedback loop to improve models

## Out of Scope (Known Limitations)

- TLS/HTTPS termination (assumed handled by reverse proxy in production)
- Multi-tenant isolation
- Key rotation and OAuth/JWT auth
- Persistent rate-limit state across restarts
- Real-time streaming (batch/hourly analysis only)
- GDPR/privacy compliance for stored IPs
- Protection against compromised API key (no IP allowlisting)

## Security Assumptions

1. API key is kept secret and not committed to version control
2. Database file is on a trusted local filesystem
3. Dashboard is used in development/demo — API key in frontend JS is acceptable for learning, not production
4. Attackers cannot directly access the SQLite file or server filesystem

## What I'd Add for Production

- Per-client API keys with scopes (ingest vs read-only)
- HTTPS everywhere, HSTS
- Redis-backed rate limiting
- Structured audit logging
- Secrets management (env vars / vault, not hardcoded defaults)
- Remove API key from frontend; use session-based auth or a backend-for-frontend proxy
