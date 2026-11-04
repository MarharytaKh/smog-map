# smog map

Air quality map for Poland. Pulls hourly measurements from the public [GIOŚ API](https://powietrze.gios.gov.pl/pjp/content/api), keeps a 30 day history and shows it on a map, per city, and side by side. You can also subscribe to an email alert when PM2.5 near you goes above a limit.

![screenshot](docs/screenshot.png)

## Stack

- **backend** – Python, FastAPI, SQLAlchemy 2, SQLite, httpx
- **frontend** – Next.js 15 (App Router), React 19, TypeScript (strict), react-leaflet, Recharts
- API types for the frontend are generated from FastAPI's OpenAPI schema with `openapi-typescript`, so if a response model changes in Python the frontend stops compiling until it's fixed

## How it works

```
GIOŚ API ──(every hour)──> sync loop ──> SQLite ──> FastAPI ──> Next.js
                                │
                                └──> check subscriptions ──> email
```

- on startup (and every night at 3) the backend loads the station list and their sensors, only PM2.5, PM10 and NO₂
- every hour it fetches the last readings for every sensor and upserts them, readings older than 30 days are deleted
- the air quality index uses the GIOŚ thresholds, the station index is the worst of its pollutants
- after each sync subscriptions are checked, an alert is sent if any station within the radius is above the threshold, at most once per 6 hours
- pages are server rendered and revalidated every 10 minutes, the map is client only because Leaflet needs `window`

## Run it

backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

first sync takes a couple of minutes (around 800 requests to GIOŚ). docs at http://localhost:8000/docs

frontend:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

open http://localhost:3000

regenerate API types while the backend is running:

```bash
npm run gen:api
```

tests:

```bash
cd backend
pytest
```

## API

| method | path | |
|---|---|---|
| GET | `/stations` | all stations with latest values and index |
| GET | `/stations/near?lat=&lon=&limit=&radius_km=` | nearest stations |
| GET | `/stations/{id}` | one station |
| GET | `/stations/{id}/history?param=PM2.5&days=7` | hourly history |
| GET | `/cities` | city names |
| GET | `/cities/ranking?param=PM2.5&order=worst` | worst / cleanest cities right now |
| GET | `/cities/{name}?days=7` | stations + history for a city |
| GET | `/compare?a=&b=&param=` | two cities side by side |
| POST | `/subscriptions` | subscribe to alerts |
| DELETE | `/subscriptions/{token}` | unsubscribe |

## Emails

Without `SMTP_HOST` alerts are only written to the log. For real emails set the SMTP variables in `backend/.env` (works with any SMTP, e.g. a Gmail app password or Mailtrap for testing).

## Todo

- postgres instead of sqlite for deploy
- show a forecast
- docker compose
