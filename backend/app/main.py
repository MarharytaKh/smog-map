import asyncio
import logging
import os
import secrets
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import queries, sync
from .aqi import PARAMS, THRESHOLDS
from .db import Base, engine, get_db
from .models import Station, Subscription
from .schemas import (
    CityDetail,
    CityRank,
    Compare,
    NearStation,
    Point,
    StationOut,
    SubscriptionIn,
    SubscriptionOut,
)

logging.basicConfig(level=logging.INFO)

Param = Literal["PM2.5", "PM10", "NO2"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    task = None
    if os.getenv("SYNC_ENABLED", "1") == "1":
        task = asyncio.create_task(sync.loop(int(os.getenv("SYNC_INTERVAL", "3600"))))
    yield
    if task:
        task.cancel()


app = FastAPI(title="Smog Map API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/meta")
def meta():
    return {"params": PARAMS, "thresholds": THRESHOLDS}


@app.get("/stations", response_model=list[StationOut])
def list_stations(db: Session = Depends(get_db)):
    return queries.all_stations(db)


@app.get("/stations/near", response_model=list[NearStation])
def near(
    lat: float,
    lon: float,
    limit: int = Query(5, ge=1, le=50),
    radius_km: float | None = Query(None, gt=0),
    db: Session = Depends(get_db),
):
    return queries.stations_near(db, lat, lon, limit, radius_km)


@app.get("/stations/{station_id}", response_model=StationOut)
def get_station(station_id: int, db: Session = Depends(get_db)):
    st = db.get(Station, station_id)
    if not st:
        raise HTTPException(404, "station not found")
    return queries.station_dict(st, queries.latest_values(db))


@app.get("/stations/{station_id}/history", response_model=list[Point])
def station_history(
    station_id: int,
    param: Param = "PM2.5",
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
):
    if not db.get(Station, station_id):
        raise HTTPException(404, "station not found")
    return queries.history(db, [station_id], param, days)


@app.get("/cities", response_model=list[str])
def list_cities(db: Session = Depends(get_db)):
    return queries.cities(db)


@app.get("/cities/ranking", response_model=list[CityRank])
def ranking(
    param: Param = "PM2.5",
    order: Literal["worst", "best"] = "worst",
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return queries.city_ranking(db, param, order, limit)


def _city(db, name: str, days: int, params: list[str]) -> CityDetail:
    stations = queries.city_stations(db, name)
    if not stations:
        raise HTTPException(404, f"no stations in {name}")
    ids = [s["id"] for s in stations]
    return CityDetail(
        city=stations[0]["city"],
        stations=stations,
        history={p: queries.history(db, ids, p, days) for p in params},
    )


@app.get("/cities/{name}", response_model=CityDetail)
def city(name: str, days: int = Query(7, ge=1, le=30), db: Session = Depends(get_db)):
    return _city(db, name, days, PARAMS)


@app.get("/compare", response_model=Compare)
def compare(
    a: str,
    b: str,
    param: Param = "PM2.5",
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
):
    return Compare(param=param, a=_city(db, a, days, [param]), b=_city(db, b, days, [param]))


@app.post("/subscriptions", response_model=SubscriptionOut, status_code=201)
def subscribe(body: SubscriptionIn, db: Session = Depends(get_db)):
    sub = Subscription(**body.model_dump(), token=secrets.token_urlsafe(24))
    db.add(sub)
    db.commit()
    near = queries.stations_near(db, sub.lat, sub.lon, 3, sub.radius_km)
    return {**body.model_dump(), "token": sub.token, "nearest_stations": near}


@app.delete("/subscriptions/{token}", status_code=204)
def unsubscribe(token: str, db: Session = Depends(get_db)):
    sub = db.scalar(select(Subscription).where(Subscription.token == token))
    if not sub:
        raise HTTPException(404, "subscription not found")
    db.delete(sub)
    db.commit()
