# Resistor AI Detective: API Handover

FastAPI service. Stateless (no database, no sessions). Safe to run as many copies as needed.

**Base URL:** `https://<your-domain>` standalone, or `https://<your-domain>/resistor` when mounted inside the company app.
**Interactive docs:** `<base>/docs`  **OpenAPI spec:** `<base>/openapi.json`

## Environment

| Variable | Required | Notes |
|---|---|---|
| `TOKEN_SECRET` | Yes (production) | Long random string. Must be identical on every server/container, otherwise a challenge issued by one server fails on another. |

Run: `gunicorn main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000`

## Endpoints

### GET `/api/challenge`
Returns a random resistor and a signed token. The token carries the answer, so no server-side state is needed.
```json
{ "bands": ["Brown","Black","Red","Gold"], "token": "<payload>.<signature>" }
```

### POST `/api/check`
```json
{ "token": "<token from /api/challenge>", "answer": "1k" }
```
Accepted answer formats: `1000`, `1k`, `1 kΩ`, `4.7kΩ`, `220 ohm`.
Responses:
```json
{ "status": "correct", "value": "1 kΩ", "tolerance": "±5%" }
{ "status": "wrong",   "value": null,   "tolerance": null }
{ "status": "invalid" }
```
Errors: `400` invalid or tampered token, `422` bad request body.

### POST `/api/hint`
Body: same as `/api/check` (`answer` may be `""`).
```json
{ "band1": ["Brown",1], "band2": ["Black",0], "multiplier": ["Red",100], "tolerance": ["Gold","±5%"] }
```

### POST `/api/decode`
For the physical-kit decoder.
```json
{ "b1": "Yellow", "b2": "Violet", "mult": "Red", "tol": "Gold" }
```
Response:
```json
{ "digits": [4,7], "multiplier": 100, "value": "4.7 kΩ", "tolerance": "±5%" }
```
Error: `400` unknown colour.

### POST `/api/log`
Optional analytics. Currently writes a structured log line only.
```json
{ "student_id": "S12345", "score": 7, "attempts": 12 }
```
Response: `{ "ok": true }`. To persist results, replace the `log.info` line in `main.py` with a Redis/queue push or a DB insert.

### GET `/health`
`{ "ok": true }`. Use for load-balancer health checks.

## Quick test (curl)
```bash
curl <base>/api/challenge
curl -X POST <base>/api/check -H "Content-Type: application/json" \
     -d '{"token":"<paste token>","answer":"1k"}'
```

## Integration notes
- **Mount inside the company app:** `company_app.mount("/resistor", resistor_app)` (see `company_app_example.py`). If the company project also has a `main.py`, rename this one (e.g. `resistor_main.py`) to avoid an import clash.
- **Login / SSO:** add the company auth dependency to the mounted app or in front of `/resistor`. Send the student ID to `/api/log`.
- **Scale:** put `/resistor/static/` and `/` behind a CDN. Add per-IP rate limiting at the gateway (generous limits: schools share one IP).
- **Frontend:** `static/index.html` is a single self-contained file. It builds API URLs from its own path, so it works at `/` or `/resistor/`.
- **Load test:** `locust -f locustfile.py --host <base>` before printing QR codes.
