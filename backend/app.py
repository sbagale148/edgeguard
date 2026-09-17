"""
EdgeGuard Backend API

REST API for ingesting edge events, running anomaly detection, and serving
dashboard data.
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure project root is on path for ml imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import init_db
from routes import alerts, events, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="EdgeGuard API",
    description="Edge security monitoring — event ingestion and anomaly detection",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred"},
    )


app.include_router(events.router)
app.include_router(stats.router)
app.include_router(alerts.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "edgeguard-api"}


def main():
    import uvicorn

    print("Starting EdgeGuard API on http://127.0.0.1:8000")
    print("Docs: http://127.0.0.1:8000/docs")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
