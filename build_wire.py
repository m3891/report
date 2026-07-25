import json
import re
import urllib.request

URL = "https://tg.me/api/telegram/messages/S2undergroundWire?limit=5"

HEADERS = {
    "User-Agent": "WinlinkWireFetcher/1.0"
}


def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


data = fetch_json(URL)

wire = None
title = None

for msg in data["messages"]:

    text = msg.get("message", "")

    if "//The Wire//" not in text:
        continue

    m = re.search(
        r"//The Wire//\s*\d+Z\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})//",
        text,
    )

    if m:
        title = f"The Wire - {m.group(1)}"
    else:
        title = "The Wire"

    end = text.find("//END REPORT//")

    if end != -1:
        text = text[: end + len("//END REPORT//")]

    wire = text
    break

if wire is None:
    raise Exception("No Wire report found.")

wire = wire.replace("\u00A0", " ")
wire = re.sub(r"\n{3,}", "\n\n", wire)

with open("wire.txt", "w", encoding="utf-8") as f:
    f.write(title + "\n")
    f.write("=" * len(title) + "\n\n")
    f.write(wire)

print("wire.txt updated successfully.")
