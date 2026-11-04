from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StationOut(BaseModel):
    id: int
    name: str
    city: str
    lat: float
    lon: float
    values: dict[str, float | None]
    index: int | None
    index_label: str | None
    updated_at: datetime | None


class NearStation(StationOut):
    distance_km: float


class Point(BaseModel):
    ts: datetime
    value: float


class CityRank(BaseModel):
    city: str
    value: float
    index: int | None
    index_label: str | None
    stations: int


class CityDetail(BaseModel):
    city: str
    stations: list[StationOut]
    history: dict[str, list[Point]]


class Compare(BaseModel):
    param: str
    a: CityDetail
    b: CityDetail


class SubscriptionIn(BaseModel):
    email: str
    lat: float = Field(ge=49, le=55.1)
    lon: float = Field(ge=14, le=24.2)
    radius_km: float = Field(default=5, gt=0, le=50)
    threshold: float = Field(default=35, gt=0, le=500)

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str):
        v = v.strip()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("invalid email")
        return v


class SubscriptionOut(BaseModel):
    token: str
    email: str
    lat: float
    lon: float
    radius_km: float
    threshold: float
    nearest_stations: list[NearStation] = []
