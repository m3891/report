import urllib.request
import json
from datetime import datetime
from zoneinfo import ZoneInfo

# -------------------------------------------------
# Wayne County, OH (Orrville)
# -------------------------------------------------
LAT = 40.84
LON = -81.76
TZ = ZoneInfo("America/New_York")

HEADERS = {
    "User-Agent": "WinlinkWeatherReport/1.0 (GitHub Pages)"
}


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read())


# Get NWS endpoints
points = fetch(f"https://api.weather.gov/points/{LAT},{LON}")

forecast_url = points["properties"]["forecast"]
forecast_hourly_url = points["properties"]["forecastHourly"]

forecast = fetch(forecast_url)
hourly = fetch(forecast_hourly_url)

periods = forecast["properties"]["periods"]
current = hourly["properties"]["periods"][0]

generated = datetime.now(TZ)

forecast_updated = datetime.fromisoformat(
    forecast["properties"]["updateTime"]
).astimezone(TZ)

report = []

report.append("=" * 58)
report.append("WAYNE COUNTY OFF-GRID WEATHER REPORT")
report.append("=" * 58)
report.append("")
report.append(f"Forecast Issued : {forecast_updated.strftime('%Y-%m-%d %I:%M %p %Z')}")
report.append(f"Report Generated: {generated.strftime('%Y-%m-%d %I:%M %p %Z')}")
report.append("")

report.append("CURRENT CONDITIONS")
report.append("------------------")
report.append(
    f"{current['temperature']}°{current['temperatureUnit']}  "
    f"{current['shortForecast']}"
)
report.append(f"Wind: {current['windDirection']} {current['windSpeed']}")
report.append("")

report.append("FORECAST")
report.append("--------")

for p in periods[:4]:
    report.append("")
    report.append(p["name"])
    report.append(p["detailedForecast"])

report.append("")
report.append("ALERTS")
report.append("------")
report.append("(Coming in Version 2)")
report.append("")

report.append("METAR")
report.append("-----")
report.append("(Coming in Version 2)")
report.append("")

report.append("SPC OUTLOOK")
report.append("-----------")
report.append("(Coming in Version 2)")
report.append("")

report.append("=" * 58)

with open("report.txt", "w") as f:
    f.write("\n".join(report))

print("report.txt updated successfully.")
