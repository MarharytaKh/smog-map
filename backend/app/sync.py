import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.dialects.sqlite import insert

from .db import SessionLocal
from .gios import GiosClient
from .models import Reading, Sensor, Station, Subscription
from .notify import send_alert
from .queries import stations_near

log = logging.getLogger(__name__)

ALERT_COOLDOWN = timedelta(hours=6)
KEEP_DAYS = 30


async def sync_stations(client: GiosClient):
    stations = await client.stations()
    if not stations:
        log.warning("got 0 stations, skipping")
        return 0
    sensor_lists = await asyncio.gather(*[client.sensors(s["id"]) for s in stations])

    with SessionLocal() as db:
        for s in stations:
            db.merge(Station(**s))
        for sensors in sensor_lists:
            for sn in sensors:
                db.merge(Sensor(**sn))
        db.commit()
    print("stations synced", len(stations))
    return len(stations)


async def sync_readings(client: GiosClient):
    with SessionLocal() as db:
        sensor_ids = list(db.scalars(select(Sensor.id)))

    results = await asyncio.gather(*[client.readings(sid) for sid in sensor_ids])

    rows = []
    for sid, readings in zip(sensor_ids, results):
        rows.extend({"sensor_id": sid, "ts": ts, "value": v} for ts, v in readings)

    with SessionLocal() as db:
        for i in range(0, len(rows), 500):
            chunk = rows[i:i + 500]
            stmt = insert(Reading).values(chunk)
            stmt = stmt.on_conflict_do_update(
                index_elements=["sensor_id", "ts"], set_={"value": stmt.excluded.value}
            )
            db.execute(stmt)
        db.execute(delete(Reading).where(Reading.ts < datetime.now() - timedelta(days=KEEP_DAYS)))
        db.commit()
    return len(rows)


def check_subscriptions():
    sent = 0
    now = datetime.utcnow()
    with SessionLocal() as db:
        subs = db.scalars(select(Subscription)).all()
        for sub in subs:
            if sub.last_notified and now - sub.last_notified < ALERT_COOLDOWN:
                continue
            near = stations_near(db, sub.lat, sub.lon, limit=10, radius_km=sub.radius_km)
            worst = None
            for st in near:
                v = st["values"].get("PM2.5")
                if v is not None and (worst is None or v > worst[0]):
                    worst = (v, st["name"])
            if worst and worst[0] > sub.threshold:
                send_alert(sub.email, worst[0], worst[1], sub.token)
                sub.last_notified = now
                sent += 1
        db.commit()
    return sent


async def run_once(client: GiosClient | None = None):
    own = client is None
    client = client or GiosClient()
    try:
        with SessionLocal() as db:
            empty = db.scalar(select(Station.id).limit(1)) is None
        if empty or datetime.now().hour == 3:
            await sync_stations(client)
        n = await sync_readings(client)
        alerts = check_subscriptions()
        log.info("sync done: %s readings, %s alerts", n, alerts)
    finally:
        if own:
            await client.close()


async def loop(interval: int = 3600):
    while True:
        try:
            await run_once()
        except Exception:
            log.exception("sync failed")
        await asyncio.sleep(interval)
