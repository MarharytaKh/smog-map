from app import aqi


def test_levels_pm25():
    assert aqi.level("PM2.5", 5) == 0
    assert aqi.level("PM2.5", 13) == 0
    assert aqi.level("PM2.5", 13.1) == 1
    assert aqi.level("PM2.5", 60) == 3
    assert aqi.level("PM2.5", 500) == 5


def test_level_unknown():
    assert aqi.level("SO2", 10) is None
    assert aqi.level("PM10", None) is None


def test_overall_takes_worst():
    assert aqi.overall({"PM2.5": 10, "PM10": 90, "NO2": None}) == 3
    assert aqi.overall({"PM2.5": None}) is None
    assert aqi.label(3) == "sufficient"
