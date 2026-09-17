# EdgeGuard ML / Anomaly Detection

Statistical and ML-based anomaly detection for edge event data. Kept in a separate module so detection logic can evolve independently of the API.

## Detectors

| Detector | Method | What it catches |
|----------|--------|-----------------|
| `detect_ip_rate_anomalies` | Z-score on event counts | IPs generating unusually high traffic |
| `detect_auth_bruteforce` | Rule-based threshold | IPs with 10+ failed auth attempts/hour |
| `detect_isolation_forest_anomalies` | Isolation Forest | IPs with unusual behavior patterns |
| `detect_error_spike` | Z-score on hourly error rates | System-wide error rate spikes |

## Why these methods?

- **Z-score:** Simple, interpretable, good for volume spikes. Easy to explain in a report.
- **Isolation Forest:** Handles multi-dimensional patterns (events + errors + auth failures + path diversity) without needing labeled attack data.
- **Rule-based auth threshold:** Some attacks are obvious — brute force doesn't need ML.

I deliberately avoided deep learning. With ~300 demo events, a neural network would overfit instantly and be impossible to explain.

## Configuration

```bash
EDGEGUARD_ZSCORE_THRESHOLD=2.5   # Standard deviations for spike detection
EDGEGUARD_MIN_EVENTS=10          # Minimum events before running detectors
```

## Usage

Analysis runs via the API:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/alerts/analyze \
  -H "X-API-Key: edgeguard-dev-key-change-me"
```

Or click "Run Analysis" in the dashboard.

## Tradeoffs

**Pros:** Fast, no training data needed, results are explainable (every alert has a human-readable reason).

**Cons:** High false-positive rate on small datasets, Isolation Forest needs ~5+ unique IPs to run, thresholds are hand-tuned not learned.

## What I'd do differently

- Add a feedback mechanism (mark alert as false positive → adjust thresholds)
- Store feature vectors for offline evaluation
- Try streaming detection (EWMA) instead of batch hourly analysis
