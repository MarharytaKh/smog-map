import math
from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import aqi
from .models import Reading, Sensor, Station


def distance_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def latest_values(db: Session, max_age_hours: int = 6):
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    last = (
        select(Reading.sensor_id, func.max(Reading.ts).label("ts"))
        .where(Reading.ts >= cutoff)
        .group_by(Reading.sensor_id)
        .subquery()
    )
    q = (
        select(Sensor.station_id, Sensor.param, Reading.value, Reading.ts)
        .join(last, last.c.sensor_id == Sensor.id)
        .join(Reading, (Reading.sensor_id == last.c.sensor_id) & (Reading.ts == last.c.ts))
    )
    out: dict[int, dict] = defaultdict(lambda: {"values": {}, "updated_at": None})
    for station_id, param, value, ts in db.execute(q):
        entry = out[station_id]
        entry["values"][param] = value
        if entry["updated_at"] is None or ts > entry["updated_at"]:
            entry["updated_at"] = ts
    return out


def station_dict(st: Station, latest: dict):
    data = latest.get(st.id, {"values": {}, "updated_at": None})
    values = {p: data["values"].get(p) for p in aqi.PARAMS}
    idx = aqi.overall(values)
    return {
        "id": st.id,
        "name": st.name,
        "city": st.city,
        "lat": st.lat,
        "lon": st.lon,
        "values": values,
        "index": idx,
        "index_label": aqi.label(idx),
        "updated_at": data["updated_at"],
    }


def all_stations(db: Session):
    latest = latest_values(db)
    stations = db.scalars(select(Station).order_by(Station.city, Station.name)).all()
    return [station_dict(s, latest) for s in stations]


def stations_near(db: Session, lat: float, lon: float, limit: int = 5, radius_km: float | None = None):
    rows = []
    for s in all_stations(db):
        d = distance_km(lat, lon, s["lat"], s["lon"])
        if radius_km is not None and d > radius_km:
            continue
        rows.append({**s, "distance_km": round(d, 2)})
    rows.sort(key=lambda r: r["distance_km"])
    return rows[:limit]


def history(db: Session, station_ids: list[int], param: str, days: int = 7):
    since = datetime.now() - timedelta(days=days)
    hour = func.strftime("%Y-%m-%d %H:00:00", Reading.ts)
    q = (
        select(hour.label("h"), func.avg(Reading.value))
        .join(Sensor, Sensor.id == Reading.sensor_id)
        .where(Sensor.station_id.in_(station_ids), Sensor.param == param, Reading.ts >= since)
        .group_by("h")
        .order_by("h")
    )
    return [{"ts": datetime.strptime(h, "%Y-%m-%d %H:%M:%S"), "value": round(v, 1)} for h, v in db.execute(q)]


def city_ranking(db: Session, param: str = "PM2.5", order: str = "worst", limit: int = 10):
    by_city = defaultdict(list)
    for s in all_stations(db):
        v = s["values"].get(param)
        if v is not None and s["city"]:
            by_city[s["city"]].append(v)
    rows = []
    for city, vals in by_city.items():
        avg = sum(vals) / len(vals)
        lvl = aqi.level(param, avg)
        rows.append({
            "city": city,
            "value": round(avg, 1),
            "index": lvl,
            "index_label": aqi.label(lvl),
            "stations": len(vals),
        })
    rows.sort(key=lambda r: r["value"], reverse=(order == "worst"))
    return rows[:limit]


def city_stations(db: Session, city: str):
    latest = latest_values(db)
    wanted = city.strip().casefold()
    stations = [s for s in db.scalars(select(Station)).all() if s.city.casefold() == wanted]
    return [station_dict(s, latest) for s in stations]


def cities(db: Session):
    return list(db.scalars(select(Station.city).distinct().order_by(Station.city)))
