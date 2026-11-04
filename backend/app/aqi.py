LEVELS = ["very good", "good", "moderate", "sufficient", "bad", "very bad"]

THRESHOLDS = {
    "PM2.5": [13, 35, 55, 75, 110],
    "PM10": [20, 50, 80, 110, 150],
    "NO2": [40, 90, 120, 230, 400],
}

PARAMS = list(THRESHOLDS.keys())


def level(param: str, value: float | None) -> int | None:
    if value is None:
        return None
    limits = THRESHOLDS.get(param)
    if not limits:
        return None
    for i, lim in enumerate(limits):
        if value <= lim:
            return i
    return len(limits)


def overall(values: dict[str, float | None]) -> int | None:
    found = [level(p, v) for p, v in values.items()]
    found = [x for x in found if x is not None]
    if not found:
        return None
    return max(found)


def label(idx):
    if idx is None:
        return None
    return LEVELS[idx]
