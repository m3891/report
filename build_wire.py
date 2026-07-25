import re
import urllib.request
from bs4 import BeautifulSoup

URL = "https://t.me/s/S2undergroundWire"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

req = urllib.request.Request(URL, headers=HEADERS)

with urllib.request.urlopen(req, timeout=30) as r:
    html = r.read()

soup = BeautifulSoup(html, "html.parser")

# Find all visible Telegram messages
messages = soup.select("div.tgme_widget_message_wrap")

if not messages:
    raise Exception("No Telegram messages found.")

wire = None
title = None

for msg in messages:
    text_node = msg.select_one(".tgme_widget_message_text")

    if text_node is None:
        continue

    text = text_node.get_text("\n", strip=True)

    if "//The Wire//" not in text:
        continue

    m = re.search(
        r"The Wire\s*[-–]\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        text,
        re.IGNORECASE,
    )

    if m:
        title = f"The Wire - {m.group(1)}"
    else:
        title = "The Wire"

    start = text.find("//The Wire//")
    end = text.find("//END REPORT//")

    if start == -1:
        continue

    if end != -1:
        text = text[start:end + len("//END REPORT//")]
    else:
        text = text[start:]

    wire = text
    break

if wire is None:
    raise Exception("Latest Wire report not found.")

# Clean whitespace
wire = re.sub(r"\n{3,}", "\n\n", wire)
wire = wire.replace("\u00A0", " ")

with open("wire.txt", "w", encoding="utf-8") as f:
    f.write(title + "\n")
    f.write("=" * len(title) + "\n\n")
    f.write(wire)

print("wire.txt updated successfully.")
