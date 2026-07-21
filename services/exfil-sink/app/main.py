"""
Meeseeks Exfil Sink - the "attacker's inbox".
=============================================
Captures data that rogue Meeseeks agents exfiltrate. Intentionally trivial and
open: no auth, CORS wide open. This is the attacker-controlled endpoint that a
compromised agent phones home to.
"""

import os
import time
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("exfil-sink")

app = FastAPI(title="Meeseeks Exfil Sink", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory capture store (a lab; nothing persists across restarts).
_CAPTURED: List[Dict[str, Any]] = []


class Capture(BaseModel):
    source: str = "unknown"
    payload: Any = None


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/collect")
async def collect(item: Capture):
    entry = {"source": item.source, "payload": item.payload, "ts": time.time()}
    _CAPTURED.append(entry)
    logger.info("captured exfil from %s", item.source)
    return {"ok": True, "count": len(_CAPTURED)}


@app.get("/collected")
async def collected():
    return {"items": list(_CAPTURED)}


@app.post("/reset")
async def reset():
    _CAPTURED.clear()
    return {"ok": True}


@app.get("/metrics")
async def metrics():
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
