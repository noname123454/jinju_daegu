"""Collect current Open-Meteo weather data for Jinju and Daegu into a CSV file."""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


API_URL = "https://api.open-meteo.com/v1/forecast"
TIMEZONE = "Asia/Seoul"
OUTPUT_PATH = Path("data/weather.csv")

LOCATIONS = (
    {"name": "진주시", "latitude": 35.1802, "longitude": 128.1086},
    {"name": "대구광역시", "latitude": 35.8714, "longitude": 128.6014},
)

CURRENT_VARIABLES = (
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "rain",
    "showers",
    "snowfall",
    "weather_code",
    "cloud_cover",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
)

FIELDNAMES = (
    "collected_at_utc",
    "weather_time_kst",
    "location",
    "latitude",
    "longitude",
    *CURRENT_VARIABLES,
)


def request_weather(location: dict[str, Any]) -> dict[str, Any]:
    """Return the API payload for one configured location."""
    query = urlencode(
        {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": ",".join(CURRENT_VARIABLES),
            "timezone": TIMEZONE,
            "wind_speed_unit": "kmh",
        }
    )
    with urlopen(f"{API_URL}?{query}", timeout=30) as response:
        return json.load(response)


def make_row(location: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """Convert one API response to the stable CSV schema."""
    current = payload["current"]
    missing_variables = [
        variable for variable in CURRENT_VARIABLES if current.get(variable) is None
    ]
    if missing_variables:
        raise ValueError(
            f"{location['name']} 응답에 값이 없는 항목: {', '.join(missing_variables)}"
        )
    row = {
        "collected_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "weather_time_kst": current["time"],
        "location": location["name"],
        "latitude": payload.get("latitude", location["latitude"]),
        "longitude": payload.get("longitude", location["longitude"]),
    }
    row.update({variable: current.get(variable) for variable in CURRENT_VARIABLES})
    return row


def existing_keys(path: Path) -> set[tuple[str, str]]:
    """Read keys used to prevent duplicate location/weather-time rows."""
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return {
            (row["location"], row["weather_time_kst"])
            for row in csv.DictReader(file)
        }


def append_new_rows(rows: list[dict[str, Any]]) -> int:
    """Append only records that are not already present in the CSV."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    known_keys = existing_keys(OUTPUT_PATH)
    new_rows = [
        row
        for row in rows
        if (row["location"], row["weather_time_kst"]) not in known_keys
    ]
    if not new_rows:
        return 0

    write_header = not OUTPUT_PATH.exists() or OUTPUT_PATH.stat().st_size == 0
    with OUTPUT_PATH.open("a", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerows(new_rows)
    return len(new_rows)


def main() -> int:
    try:
        rows = [make_row(location, request_weather(location)) for location in LOCATIONS]
    except (
        HTTPError,
        URLError,
        TimeoutError,
        KeyError,
        ValueError,
        json.JSONDecodeError,
    ) as error:
        print(f"날씨 수집에 실패했습니다: {error}", file=sys.stderr)
        return 1

    added = append_new_rows(rows)
    print(f"수집 완료: {added}건 추가, 파일: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
