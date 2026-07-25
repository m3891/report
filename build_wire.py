import urllib.request
import xml.etree.ElementTree as ET
import re

HEADERS = {
    "User-Agent": "WinlinkWireFetcher/1.0"
}

RSS_URL = (
    "https://publish.obsidian.md/"
    "s2underground/"
    "rss.xml"
)


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


# --------------------------------------------------------
# Read RSS feed
# --------------------------------------------------------

rss = ET.fromstring(fetch(RSS_URL))

channel = rss.find("channel")

wire_url = None

for item in channel.findall("item"):
    title = item.findtext("title", "")

    if title.startswith("The Wire"):
        wire_url = item.findtext("link")
        break

if wire_url is None:
    raise Exception("No Wire report found in RSS feed.")

print(f"Latest report: {wire_url}")

# --------------------------------------------------------
# Download report
# --------------------------------------------------------

html = fetch(wire_url).decode("utf-8")

# Remove HTML tags
text = re.sub(r"<[^>]+>", "", html)

# Compress blank lines
text = re.sub(r"\n\s*\n+", "\n\n", text)

# Trim report
start = text.find("The Wire")

if start != -1:
    text = text[start:]

end = text.find("//END REPORT//")

if end != -1:
    text = text[:end + len("//END REPORT//")]

with open("wire.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated wire.txt")
