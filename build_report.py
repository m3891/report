import urllib.request
import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo

LAT = 40.84
LON = -81.76
TZ = ZoneInfo("America/New_York")

HEADERS = {
    "User-Agent": "WinlinkCustomReport/2.4"
}


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def hazard_summary(periods, alerts):
    """Return the highest-priority hazard in a concise format."""

    # Active alerts always override everything else
    if alerts["features"]:
        return alerts["features"][0]["properties"]["headline"]

    text = " ".join(p["detailedForecast"] for p in periods[:4])
    lower = text.lower()

    # Heat Index
    m = re.search(r"Heat index values? as high as (\d+)", text, re.IGNORECASE)
    if m:
        return f"Heat index up to {m.group(1)}°F."

    # Wind gusts
    m = re.search(r"gusts? as high as (\d+)\s*mph", text, re.IGNORECASE)
    if m:
        return f"Wind gusts up to {m.group(1)} mph."

    # Rainfall amounts
    m = re.search(
        r"between ([0-9.]+) and ([0-9.]+) inches",
        text,
        re.IGNORECASE,
    )
    if m:
        return f"Heavy rain {m.group(1)}-{m.group(2)} inches."

    # General hazards
    if "severe thunderstorm" in lower:
        return "Severe thunderstorms possible."

    if "thunderstorm" in lower:
        return "Thunderstorms possible."

    if "flash flood" in lower:
        return "Flash flooding possible."

    if "flood" in lower:
        return "Flooding possible."

    if "freezing rain" in lower:
        return "Freezing rain possible."

    if "snow" in lower:
        return "Snow expected."

    if "fog" in lower:
        return "Fog possible."

    return "None"


# --------------------------------------------------------
# Download Weather
# --------------------------------------------------------

points = fetch(f"https://api.weather.gov/points/{LAT},{LON}")

forecast = fetch(points["properties"]["forecast"])
hourly = fetch(points["properties"]["forecastHourly"])
alerts = fetch(f"https://api.weather.gov/alerts/active?point={LAT},{LON}")

generated = datetime.now(TZ)

current = hourly["properties"]["periods"][0]
periods = forecast["properties"]["periods"]
today = periods[0]

# --------------------------------------------------------
# Build Today's Forecast
# --------------------------------------------------------

forecast_line = today["shortForecast"]

if today["isDaytime"]:
    forecast_line += f". High {today['temperature']}°F."
else:
    forecast_line += f". Low {today['temperature']}°F."

wind_dir = today["windDirection"].strip()
wind_speed = today["windSpeed"].strip()

if wind_speed.startswith("0"):
    forecast_line += " Wind calm."
elif wind_dir:
    forecast_line += f" Wind {wind_dir} {wind_speed}."
else:
    forecast_line += f" Wind {wind_speed}."

# --------------------------------------------------------
# Build Report
# --------------------------------------------------------

report = []

report.append("WINLINK CUSTOM REPORT")
report.append("---------------------")
report.append("")
report.append(
    f"Updated: {generated.strftime('%b %d %I:%M %p %Z')}"
)
report.append("")

report.append(
    f"CURRENT : {current['temperature']}°{current['temperatureUnit']}, "
    f"{current['shortForecast']}"
)

if alerts["features"]:
    report.append("ALERTS  : Active")
else:
    report.append("ALERTS  : None")

report.append(f"HAZARDS : {hazard_summary(periods, alerts)}")

report.append(f"FORECAST: {forecast_line}")

with open("report.txt", "w") as f:
    f.write("\n".join(report))

print("report.txt updated successfully.")
