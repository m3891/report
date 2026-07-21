import urllib.request
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo

LAT = 40.84
LON = -81.76
TZ = ZoneInfo("America/New_York")

HEADERS = {
    "User-Agent": "WinlinkCustomReport/3.0"
}


def fetch_hamqsl():
    req = urllib.request.Request(
        "https://www.hamqsl.com/solarxml.php",
        headers=HEADERS
    )

    with urllib.request.urlopen(req, timeout=20) as r:
        root = ET.fromstring(r.read())

    solar = root.find("solardata")

    conditions = {}

    calc = solar.find("calculatedconditions")

    if calc is not None:
        for band in calc.findall("band"):
            name = band.attrib["name"]
            when = band.attrib["time"]

            if name not in conditions:
                conditions[name] = {}

            conditions[name][when] = band.text.strip()

    return {
        "sfi": solar.findtext("solarflux", "N/A").strip(),
        "kp": solar.findtext("kindex", "N/A").strip(),
        "bands": conditions,
    }


def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def hazard_summary(periods, alerts):

    if alerts["features"]:
        return "See ALERTS."

    text = " ".join(p["detailedForecast"] for p in periods[:4])
    lower = text.lower()

    m = re.search(r"Heat index values? as high as (\d+)", text, re.IGNORECASE)
    if m:
        return f"Heat index up to {m.group(1)}F."

    m = re.search(r"gusts? as high as (\d+)\s*mph", text, re.IGNORECASE)
    if m:
        return f"Wind gusts up to {m.group(1)} mph."

    m = re.search(r"between ([0-9.]+) and ([0-9.]+) inches", text, re.IGNORECASE)
    if m:
        return f"Heavy rain {m.group(1)}-{m.group(2)} inches."

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

points = fetch_json(f"https://api.weather.gov/points/{LAT},{LON}")

forecast = fetch_json(points["properties"]["forecast"])
hourly = fetch_json(points["properties"]["forecastHourly"])
alerts = fetch_json(f"https://api.weather.gov/alerts/active?point={LAT},{LON}")

# NOAA Sunrise/Sunset
sun = fetch_json(
    f"https://api.sunrise-sunset.org/json?lat={LAT}&lng={LON}&formatted=0"
)

try:
    solar = fetch_hamqsl()
except Exception:
    solar = {
        "sfi": "N/A",
        "kp": "N/A",
        "bands": {
            "80m-40m": {"day": "N/A", "night": "N/A"},
            "30m-20m": {"day": "N/A", "night": "N/A"},
            "17m-15m": {"day": "N/A", "night": "N/A"},
            "12m-10m": {"day": "N/A", "night": "N/A"},
        },
    }

generated = datetime.now(TZ)

current = hourly["properties"]["periods"][0]
periods = forecast["properties"]["periods"]
today = periods[0]

# --------------------------------------------------------
# Sunrise / Sunset
# --------------------------------------------------------

sunrise = (
    datetime.fromisoformat(sun["results"]["sunrise"])
    .astimezone(TZ)
    .strftime("%I:%M %p")
    .lstrip("0")
)

sunset = (
    datetime.fromisoformat(sun["results"]["sunset"])
    .astimezone(TZ)
    .strftime("%I:%M %p")
    .lstrip("0")
)

# --------------------------------------------------------
# Today's Forecast
# --------------------------------------------------------

forecast_line = today["shortForecast"]

if today["isDaytime"]:
    forecast_line += f". High {today['temperature']}F."
else:
    forecast_line += f". Low {today['temperature']}F."

wind_dir = today["windDirection"].strip()
wind_speed = today["windSpeed"].strip()

if wind_speed.startswith("0"):
    forecast_line += " Wind calm."
elif wind_dir:
    forecast_line += f" Wind {wind_dir} {wind_speed}."
else:
    forecast_line += f" Wind {wind_speed}."

# --------------------------------------------------------
# Report
# --------------------------------------------------------

report = []

report.append("WINLINK CUSTOM REPORT")
report.append("---------------------")
report.append(f"Updated : {generated.strftime('%b %d %I:%M %p %Z')}")
report.append(f"Sunrise: {sunrise}   Sunset: {sunset}")
report.append("")

report.append("WAYNE CO. WEATHER")
report.append("------------------")

report.append(
    f"CURRENT : {current['temperature']}F, "
    f"{current['shortForecast']}"
)

if alerts["features"]:
    alert = alerts["features"][0]["properties"]

    expires = (
        datetime.fromisoformat(alert["expires"])
        .astimezone(TZ)
        .strftime("%I:%M %p")
        .lstrip("0")
    )

    report.append(
        f"ALERTS  : {alert['event']} until {expires}"
    )
else:
    report.append("ALERTS  : None")

report.append(f"HAZARDS : {hazard_summary(periods, alerts)}")
report.append(f"FORECAST: {forecast_line}")

report.append("")

report.append("HF CONDITIONS")
report.append("-------------")

report.append(f"SFI     : {solar['sfi']}")
report.append(f"K-INDEX : {solar['kp']}")

bands = solar["bands"]

report.append(
    f"80/40   : Day {bands['80m-40m']['day']} | Night {bands['80m-40m']['night']}"
)

report.append(
    f"30/20   : Day {bands['30m-20m']['day']} | Night {bands['30m-20m']['night']}"
)

report.append(
    f"17/15   : Day {bands['17m-15m']['day']} | Night {bands['17m-15m']['night']}"
)

report.append(
    f"12/10   : Day {bands['12m-10m']['day']} | Night {bands['12m-10m']['night']}"
)

with open("report.txt", "w") as f:
    f.write("\n".join(report))

print("report.txt updated successfully.")
