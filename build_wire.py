import urllib.request
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "WinlinkWireFetcher/1.0"
}

URL = "https://t.me/s/S2undergroundWire"

req = urllib.request.Request(URL, headers=HEADERS)

with urllib.request.urlopen(req, timeout=30) as r:
    html = r.read()

soup = BeautifulSoup(html, "html.parser")

text = soup.get_text("\n")

start = text.find("//The Wire//")

if start == -1:
    raise Exception("Latest Wire not found.")

text = text[start:]

end = text.find("//END REPORT//")

if end != -1:
    text = text[:end + len("//END REPORT//")]

with open("wire.txt", "w", encoding="utf-8") as f:
    f.write(text.strip())

print("wire.txt updated.")
