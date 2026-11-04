import os
import tempfile
from datetime import datetime, timedelta

import pytest

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["SYNC_ENABLED"] = "0"

from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.main import app
from app.models import Reading, Sensor, Station


@pytest.fixture()
def db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as s:
        yield s


@pytest.fixture()
def seeded(db):
    db.add_all([
        Station(id=1, name="Warszawa, ul. Marszałkowska", city="Warszawa", lat=52.2251, lon=21.0103),
        Station(id=2, name="Warszawa, ul. Kondratowicza", city="Warszawa", lat=52.2909, lon=21.0425),
        Station(id=3, name="Kraków, al. Krasińskiego", city="Kraków", lat=50.0577, lon=19.9265),
    ])
    db.add_all([
        Sensor(id=11, station_id=1, param="PM2.5"),
        Sensor(id=12, station_id=1, param="PM10"),
        Sensor(id=21, station_id=2, param="PM2.5"),
        Sensor(id=31, station_id=3, param="PM2.5"),
    ])
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    for h in range(48):
        ts = now - timedelta(hours=h)
        db.add(Reading(sensor_id=11, ts=ts, value=20 + h % 5))
        db.add(Reading(sensor_id=12, ts=ts, value=40))
        db.add(Reading(sensor_id=21, ts=ts, value=10))
        db.add(Reading(sensor_id=31, ts=ts, value=80))
    db.commit()
    return db


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
