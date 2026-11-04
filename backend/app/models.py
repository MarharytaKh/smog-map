from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Station(Base):
    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    city: Mapped[str] = mapped_column(String(100), index=True)
    province: Mapped[str] = mapped_column(String(60), default="")
    lat: Mapped[float]
    lon: Mapped[float]

    sensors: Mapped[list["Sensor"]] = relationship(back_populates="station", cascade="all, delete-orphan")


class Sensor(Base):
    __tablename__ = "sensors"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"), index=True)
    param: Mapped[str] = mapped_column(String(10))

    station: Mapped[Station] = relationship(back_populates="sensors")


class Reading(Base):
    __tablename__ = "readings"
    __table_args__ = (UniqueConstraint("sensor_id", "ts"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensors.id"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime, index=True)
    value: Mapped[float]


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200))
    lat: Mapped[float]
    lon: Mapped[float]
    radius_km: Mapped[float] = mapped_column(default=5)
    threshold: Mapped[float] = mapped_column(default=35)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    last_notified: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
