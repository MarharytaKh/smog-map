from unittest.mock import patch

from app import sync
from app.models import Subscription


def test_stations(client, seeded):
    r = client.get("/stations")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3
    krk = next(s for s in data if s["city"] == "Kraków")
    assert krk["values"]["PM2.5"] == 80
    assert krk["index_label"] == "bad"


def test_near(client, seeded):
    r = client.get("/stations/near", params={"lat": 52.23, "lon": 21.01, "limit": 2})
    data = r.json()
    assert [s["id"] for s in data] == [1, 2]
    assert data[0]["distance_km"] < 1


def test_near_radius(client, seeded):
    r = client.get("/stations/near", params={"lat": 52.23, "lon": 21.01, "radius_km": 3})
    assert len(r.json()) == 1


def test_history(client, seeded):
    r = client.get("/stations/1/history", params={"days": 1})
    pts = r.json()
    assert 20 <= len(pts) <= 25
    assert all(20 <= p["value"] <= 24 for p in pts)


def test_station_404(client, seeded):
    assert client.get("/stations/999").status_code == 404


def test_ranking(client, seeded):
    worst = client.get("/cities/ranking").json()
    assert worst[0]["city"] == "Kraków"
    best = client.get("/cities/ranking", params={"order": "best"}).json()
    assert best[0]["city"] == "Warszawa"
    assert best[0]["stations"] == 2


def test_city_and_compare(client, seeded):
    r = client.get("/cities/warszawa")
    assert r.status_code == 200
    assert r.json()["city"] == "Warszawa"
    assert set(r.json()["history"]) == {"PM2.5", "PM10", "NO2"}

    r = client.get("/compare", params={"a": "Warszawa", "b": "Kraków"})
    body = r.json()
    assert body["a"]["history"]["PM2.5"][0]["value"] < body["b"]["history"]["PM2.5"][0]["value"]

    assert client.get("/cities/Atlantyda").status_code == 404


def test_bad_param(client, seeded):
    assert client.get("/cities/ranking", params={"param": "CO"}).status_code == 422


def test_subscribe_and_alert(client, seeded):
    r = client.post("/subscriptions", json={"email": "me@example.com", "lat": 50.06, "lon": 19.93, "threshold": 50})
    assert r.status_code == 201
    token = r.json()["token"]
    assert r.json()["nearest_stations"][0]["id"] == 3

    with patch("app.sync.send_alert") as send:
        assert sync.check_subscriptions() == 1
        assert sync.check_subscriptions() == 0
        send.assert_called_once()

    assert client.delete(f"/subscriptions/{token}").status_code == 204
    assert client.delete(f"/subscriptions/{token}").status_code == 404


def test_no_alert_when_clean(client, seeded):
    client.post("/subscriptions", json={"email": "a@b.pl", "lat": 52.29, "lon": 21.04, "radius_km": 2})
    with patch("app.sync.send_alert") as send:
        assert sync.check_subscriptions() == 0
        send.assert_not_called()


def test_bad_email(client, seeded):
    r = client.post("/subscriptions", json={"email": "nope", "lat": 52, "lon": 21})
    assert r.status_code == 422
