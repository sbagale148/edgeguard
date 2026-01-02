# EdgeGuard Backend

The API that accepts events, stores them, and lets you query them. This is where most of the actual work happens.

## Current Status

Still just a placeholder. The real implementation starts in Milestone 2.

## What I'm Planning to Build

- API endpoints to accept events/logs (POST /api/events or something like that)
- Some way to store this data (database, probably SQLite to start)
- Basic auth so not just anyone can send data
- Input validation because people will send garbage
- Rate limiting to prevent abuse (ironic, given this is an abuse detection system)

## Tech Stack

Haven't decided yet, but probably Python with Flask or FastAPI. FastAPI seems cool and has built-in docs, but Flask is simpler. We'll see.

## API Ideas (Subject to Change)

```
POST   /api/events          # Send me events
GET    /api/events          # Get events (with filters probably)
GET    /api/events/:id      # One specific event
GET    /api/analytics       # Analysis results from ML stuff
POST   /api/auth/login      # Login endpoint
```

These will definitely change once I start building and realize what I actually need.

## Database

No idea yet. Will figure this out when I know what the data looks like.

