import asyncio
import logging
from datetime import datetime

import httpx

from .aqi import PARAMS

BASE_URL = "https://api.gios.gov.pl/pjp-api/v1/rest"

log = logging.getLogger(__name__)


def parse_station(raw: dict) -> dict:
    return {
        "id": int(raw["Identyfikator stacji"]),
        "name": raw["Nazwa stacji"],
        "city": raw.get("Nazwa miasta") or "",
        "province": (raw.get("Województwo") or "").lower(),
        "lat": float(raw["WGS84 φ N"]),
        "lon": float(raw["WGS84 λ E"]),
    }


def parse_sensor(raw: dict) -> dict | None:
    code = raw.get("Wskaźnik - kod")
    if code not in PARAMS:
        return None
    return {
        "id": int(raw["Identyfikator stanowiska"]),
        "station_id": int(raw["Identyfikator stacji"]),
        "param": code,
    }


def parse_readings(raw: dict) -> list[tuple[datetime, float]]:
    out = []
    for row in raw.get("Lista danych pomiarowych", []):
        val = row.get("Wartość")
        if val is None:
            continue
        ts = datetime.strptime(row["Data"], "%Y-%m-%d %H:%M:%S")
        out.append((ts, float(val)))
    return out


class GiosClient:
    def __init__(self, client: httpx.AsyncClient | None = None, concurrency: int = 3):
        self.client = client or httpx.AsyncClient(base_url=BASE_URL, timeout=30)
        self.sem = asyncio.Semaphore(concurrency)

    async def _get(self, path: str, **params):
        async with self.sem:
            for attempt in range(4):
                try:
                    r = await self.client.get(path, params=params or None)
                except httpx.TransportError as e:
                    log.info("gios %s failed (%s), retry %s", path, type(e).__name__, attempt + 1)
                    await asyncio.sleep(3 * (attempt + 1))
                    continue
                if r.status_code in (429, 502, 503, 504):
                    await asyncio.sleep(5 * (attempt + 1))
                    continue
                if r.status_code >= 400:
                    log.debug("gios %s -> %s", path, r.status_code)
                    return {}
                return r.json()
        log.warning("gios %s gave up", path)
        return {}

    async def stations(self) -> list[dict]:
        rows = []
        page = 0
        while True:
            data = await self._get("/station/findAll", page=page, size=500)
            rows.extend(data.get("Lista stacji pomiarowych", []))
            page += 1
            if page >= int(data.get("totalPages") or 1):
                break
        return [parse_station(r) for r in rows]

    async def sensors(self, station_id: int) -> list[dict]:
        data = await self._get(f"/station/sensors/{station_id}")
        items = data.get("Lista stanowisk pomiarowych dla podanej stacji", [])
        parsed = [parse_sensor(s) for s in items]
        return [s for s in parsed if s]

    async def readings(self, sensor_id: int):
        data = await self._get(f"/data/getData/{sensor_id}")
        return parse_readings(data)

    async def close(self):
        await self.client.aclose()
