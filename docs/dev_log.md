# EdgeGuard Development Log

---

## Week 1-2: Setting Up the Foundation

**Goal:** Get the project structure in place before writing actual code.

Set up folders for frontend, backend, ml, security, docs. Created placeholder files and initial README.

**Decisions:** Separate folders per component. Deferred tech stack until Milestone 2.

---

## Week 3-4: Core Backend & Data Flow

**Goal:** Make it actually work end-to-end.

**Tech stack chosen:**
- **Backend:** Python + FastAPI (async, auto OpenAPI docs, Pydantic validation built in)
- **Database:** SQLite via SQLAlchemy (zero config, good enough for a semester project)
- **Frontend:** Vanilla JS (no build step, keeps focus on the system not the tooling)

**What I built:**
- Event model with types: `http_request`, `auth_attempt`, `log_entry`
- REST endpoints for single/batch ingestion, listing, stats, alerts
- API key auth via `X-API-Key` header
- Seed script that generates 250 normal events + 80 attack events from a simulated attacker IP

**Design choice:** Events store the fields that matter for detection (IP, type, severity, path, status code) rather than a generic JSON blob. Makes queries and ML features straightforward.

---

## Week 5-6: Security Features & Threat Modeling

**Goal:** Actually think about security, not just bolt it on at the end.

**Implemented:**
- Pydantic validation with field length limits and enum types
- Per-IP rate limiting (in-memory, 100 req/min)
- Generic error handler (no stack traces in responses)
- Batch size cap (100 events)
- Full threat model in `security/threat_model.md`

**What was hard:** Deciding the right amount of security for a learning project. I wanted real patterns (auth, validation, rate limiting) without building OAuth or distributed systems I wouldn't learn much from.

**Known gap:** API key is in the frontend JS for demo convenience. Documented as an explicit limitation in the threat model.

---

## Week 7-9: ML / Anomaly Detection

**Goal:** Use ML where it helps, skip it where it doesn't.

**Detectors implemented:**
1. **Z-score on IP event volume** — catches the obvious high-volume scanner
2. **Auth brute-force rule** — 10+ failed auths in an hour, no ML needed
3. **Isolation Forest** — multi-feature behavioral anomalies (events, errors, auth failures, path diversity)
4. **Error rate spike** — Z-score on hourly error rates across the system

**Why not deep learning:** ~300 demo events. A neural net would memorize, not generalize, and I couldn't explain why it flagged something.

**Tradeoff I'm ok with:** Hand-tuned thresholds mean more false positives on small datasets, but every alert has a human-readable reason. Explainability > accuracy for this project.

---

## Week 10-11: Frontend Dashboard

**Goal:** Make the system visible.

Built a dark-themed dashboard with:
- Summary stat cards
- 24h trend chart (Chart.js)
- Active alerts with resolve action
- Top IPs and event types
- Recent events table
- Manual "Run Analysis" button + 30s auto-refresh

**Decision:** Vanilla JS over React. The dashboard is read-heavy with simple interactions — a framework would add complexity without teaching me anything new about the system itself.

---

## Week 12-13: Polish & Reflection

**Goal:** Make it portfolio-ready.

- Updated all READMEs with setup instructions and architecture
- Wrote "what I'd do differently" section
- Cleaned up import paths between backend and ml modules
- Verified end-to-end: seed → analyze → dashboard

### What I learned

1. **Start with the data model.** Once I knew what an "event" looked like, everything else (API, ML features, dashboard) fell into place.
2. **Security is a set of decisions, not a feature.** The threat model forced me to articulate what I'm *not* protecting, which was more valuable than adding another middleware.
3. **ML should be the last thing you add, not the first.** Rule-based detection (auth brute-force) catches obvious attacks. ML adds value for subtle behavioral patterns, but only with enough data.
4. **Document as you go.** This dev log was way more useful than I expected. I forgot half my reasoning within a week.

### Open questions for future me

- How would this scale to 1M events/day? (Partitioning, streaming detection, separate read replicas)
- Could I fine-tune thresholds automatically from resolved/false-positive alerts?
- What does this look like with real Cloudflare-style log formats?
