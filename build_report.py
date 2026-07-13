import urllib.request
import json
from datetime import datetime
from zoneinfo import ZoneInfo

LAT = 40.84
LON = -81.76
TZ = ZoneInfo("America/New_York")

HEADERS = {
    "User-Agent": "WayneCountyOffGridWeather/2.2"
}


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def hazard_summary(periods, alerts):

    if alerts["features"]:
        return alerts["features"][0]["properties"]["headline"]

    text = " ".join(p["detailedForecast"] for p in periods[:4]).lower()

    checks = [
        ("tornado", "Tornadoes possible."),
        ("severe thunderstorm", "Severe thunderstorms possible."),
        ("thunderstorm", "Thunderstorms possible."),
        ("heavy rain", "Heavy rainfall possible."),
        ("flash flood", "Flash flooding possible."),
        ("flood", "Flooding possible."),
        ("snow", "Snow expected."),
        ("ice", "Icy conditions possible."),
        ("freezing rain", "Freezing rain possible."),
        ("heat index", "Heat index will be high."),
        ("heat", "Hot weather expected."),
        ("wind advisory", "Strong winds expected."),
        ("gust", "Gusty winds expected."),
        ("fog", "Reduced visibility in fog."),
    ]

    for word, message in checks:
        if word in text:
            return message

    return "No significant hazards expected."


points = fetch(f"https://api.weather.gov/points/{LAT},{LON}")

forecast = fetch(points["properties"]["forecast"])
hourly = fetch(points["properties"]["forecastHourly"])
alerts = fetch(f"https://api.weather.gov/alerts/active?point={LAT},{LON}")

generated = datetime.now(TZ)

forecast_updated = datetime.fromisoformat(
    forecast["properties"]["updateTime"]
).astimezone(TZ)

current = hourly["properties"]["periods"][0]

report = []

report.append("=" * 58)
report.append("WAYNE COUNTY OFF-GRID WEATHER REPORT")
report.append("=" * 58)
report.append("")
report.append(
    f"Forecast Issued : {forecast_updated.strftime('%Y-%m-%d %I:%M %p %Z')}"
)
report.append(
    f"Report Generated: {generated.strftime('%Y-%m-%d %I:%M %p %Z')}"
)
report.append("")

# Summary
# Summary
periods = forecast["properties"]["periods"]
today = periods[0]

report.append("SUMMARY")
report.append("-------")

summary = today["detailedForecast"].split(".")[0].strip() + "."
report.append(summary)

if alerts["features"]:
    report.append("Active alerts in effect.")
else:
    report.append("No active alerts.")

report.append(f"Next hazard: {hazard_summary(periods, alerts)}")
report.append("")

# Current
report.append("CURRENT CONDITIONS")
report.append("------------------")
report.append(
    f"{current['temperature']}°{current['temperatureUnit']}  {current['shortForecast']}"
)

wind_dir = current["windDirection"].strip()

if current["windSpeed"].startswith("0"):
    report.append("Wind: Calm")
elif wind_dir:
    report.append(f"Wind: {wind_dir} {current['windSpeed']}")
else:
    report.append(f"Wind: {current['windSpeed']}")

report.append("")

# Alerts
report.append("ACTIVE ALERTS")
report.append("-------------")

if alerts["features"]:
    for alert in alerts["features"]:
        report.append(alert["properties"]["headline"])
else:
    report.append("None")

report.append("")

# Hazard
report.append("NEXT HAZARD")
report.append("-----------")
report.append(hazard_summary(forecast["properties"]["periods"], alerts))
report.append("")

# Forecast
report.append("FORECAST")
report.append("--------")

for p in forecast["properties"]["periods"][:4]:
    report.append("")
    report.append(p["name"])
    report.append("")
    report.append(p["detailedForecast"])

report.append("")
report.append("=" * 58)

with open("report.txt", "w") as f:
    f.write("\n".join(report))

print("Updated report.txt")
