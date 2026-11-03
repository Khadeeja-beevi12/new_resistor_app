import base64
import hashlib
import hmac
import json
import logging
import math
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import resistor_logic as R

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Set TOKEN_SECRET in the environment for production (same value on every server).
SECRET = os.environ.get("TOKEN_SECRET", "change-me-in-production").encode()

log = logging.getLogger("resistor")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Resistor AI Detective", docs_url="/docs")
app.add_middleware(GZipMiddleware, minimum_size=500)


# ---------- stateless signed token: any server can verify, no sessions ----------
def sign(bands):
    payload = base64.urlsafe_b64encode(json.dumps(bands).encode()).decode()
    sig = hmac.new(SECRET, payload.encode(), hashlib.sha256).hexdigest()[:24]
    return f"{payload}.{sig}"


def verify(token: str):
    try:
        payload, sig = token.rsplit(".", 1)
        good = hmac.new(SECRET, payload.encode(), hashlib.sha256).hexdigest()[:24]
        if not hmac.compare_digest(sig, good):
            raise ValueError("bad signature")
        bands = json.loads(base64.urlsafe_b64decode(payload))
        if len(bands) != 4:
            raise ValueError("bad bands")
        return bands
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid challenge token")


# ---------- request models ----------
class CheckReq(BaseModel):
    token: str = Field(max_length=600)
    answer: str = Field(default="", max_length=40)


class DecodeReq(BaseModel):
    b1: str
    b2: str
    mult: str
    tol: str


class LogReq(BaseModel):
    student_id: str | None = Field(default=None, max_length=64)
    score: int = Field(ge=0, le=100000)
    attempts: int = Field(ge=0, le=100000)


# ---------- API ----------
@app.get("/api/challenge")
def challenge():
    bands = list(R.pick())
    return {"bands": bands, "token": sign(bands)}


@app.post("/api/check")
def check(req: CheckReq):
    bands = verify(req.token)
    correct, tol = R.calculate(bands)
    student = R.normalize(req.answer)
    if student is None or not math.isfinite(student) or student <= 0:
        return {"status": "invalid"}
    ok = math.isclose(student, correct, rel_tol=1e-9, abs_tol=1e-9)
    return {
        "status": "correct" if ok else "wrong",
        "value": R.fmt(correct) if ok else None,
        "tolerance": tol if ok else None,
    }


@app.post("/api/hint")
def hint(req: CheckReq):
    b = verify(req.token)
    return {
        "band1": [b[0], R.DIGITS[b[0]]],
        "band2": [b[1], R.DIGITS[b[1]]],
        "multiplier": [b[2], R.MULTIPLIERS[b[2]]],
        "tolerance": [b[3], R.TOLERANCES[b[3]]],
    }


@app.post("/api/decode")
def decode(r: DecodeReq):
    try:
        val, tol = R.calculate((r.b1, r.b2, r.mult, r.tol))
    except KeyError:
        raise HTTPException(status_code=400, detail="Unknown colour")
    return {
        "digits": [R.DIGITS[r.b1], R.DIGITS[r.b2]],
        "multiplier": R.MULTIPLIERS[r.mult],
        "value": R.fmt(val),
        "tolerance": tol,
    }


@app.post("/api/log")
def log_result(r: LogReq):
    # Cheap structured log line. Ship stdout to your log pipeline (CloudWatch, ELK, etc.)
    # and aggregate there, or replace with a Redis/queue push for batch DB writes.
    log.info("result student=%s score=%d attempts=%d", r.student_id, r.score, r.attempts)
    return {"ok": True}


@app.get("/health")
def health():
    return {"ok": True}


# ---------- frontend ----------
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html", headers={"Cache-Control": "public, max-age=300"})
