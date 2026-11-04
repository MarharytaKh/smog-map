import asyncio

import httpx

from app.gios import BASE_URL, GiosClient

STATIONS = {
    "Lista stacji pomiarowych": [
        {
            "Identyfikator stacji": 552,
            "Kod stacji": "MzWarKondrat",
            "Nazwa stacji": "Warszawa, ul. Kondratowicza",
            "WGS84 φ N": "52.290864",
            "WGS84 λ E": "21.042458",
            "Nazwa miasta": "Warszawa",
            "Województwo": "MAZOWIECKIE",
        }
    ],
    "totalPages": 1,
}

SENSORS = {
    "Lista stanowisk pomiarowych dla podanej stacji": [
        {"Identyfikator stanowiska": 3759, "Identyfikator stacji": 552, "Wskaźnik - kod": "NO"},
        {"Identyfikator stanowiska": 3762, "Identyfikator stacji": 552, "Wskaźnik - kod": "PM2.5"},
        {"Identyfikator stanowiska": 3763, "Identyfikator stacji": 552, "Wskaźnik - kod": "PM10"},
    ]
}

DATA = {
    "Lista danych pomiarowych": [
        {"Kod stanowiska": "x", "Data": "2026-11-04 15:00:00", "Wartość": None},
        {"Kod stanowiska": "x", "Data": "2026-11-04 14:00:00", "Wartość": 31.4},
        {"Kod stanowiska": "x", "Data": "2026-11-04 13:00:00", "Wartość": 28},
    ]
}


def handler(request: httpx.Request):
    path = request.url.path
    if path.endswith("/station/findAll"):
        return httpx.Response(200, json=STATIONS)
    if "/station/sensors/" in path:
        return httpx.Response(200, json=SENSORS)
    if "/data/getData/" in path:
        return httpx.Response(200, json=DATA)
    return httpx.Response(404)


def make_client():
    return GiosClient(httpx.AsyncClient(base_url=BASE_URL, transport=httpx.MockTransport(handler)))


def test_parse_everything():
    async def run():
        c = make_client()
        stations = await c.stations()
        sensors = await c.sensors(552)
        readings = await c.readings(3762)
        await c.close()
        return stations, sensors, readings

    stations, sensors, readings = asyncio.run(run())

    assert stations[0]["city"] == "Warszawa"
    assert stations[0]["lat"] == 52.290864
    assert [s["param"] for s in sensors] == ["PM2.5", "PM10"]
    assert len(readings) == 2
    assert readings[0][1] == 31.4


def test_404_is_empty():
    async def run():
        c = make_client()
        r = await c._get("/nope")
        await c.close()
        return r

    assert asyncio.run(run()) == {}
