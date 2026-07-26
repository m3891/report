import urllib.request
import urllib.error
import re
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "WireFetcher/1.0"
}

MONTHS = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError:
        return None
    except Exception:
        return None


today = datetime.utcnow().date()

html = None
found_url = None

for i in range(10):

    d = today - timedelta(days=i)

    month_name = MONTHS[d.month - 1]
    month_folder = f"{month_name}+{d.year}"

    page = (
        f"The+Wire+-+{month_name}+"
        f"{d.day}%2C+{d.year}"
    )

    url = (
        "https://publish.obsidian.md/"
        "s2underground/"
        "S2+Underground+PUBLISH/"
        "02+Wire+Reports/"
        f"{month_folder}/"
        f"{page}"
    )

    print(f"Trying {url}")

    html = fetch(url)

    if html:
        found_url = url
        break


if html is None:
    raise RuntimeError("Unable to locate a Wire report from the last 10 days.")


# ----------------------------------------------------
# Strip HTML
# ----------------------------------------------------

text = re.sub(r"<script.*?</script>", "", html, flags=re.S)
text = re.sub(r"<style.*?</style>", "", text, flags=re.S)
text = re.sub(r"<[^>]+>", "\n", text)

text = (
    text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
)

lines = [x.strip() for x in text.splitlines()]
lines = [x for x in lines if x]

text = "\n".join(lines)

# ----------------------------------------------------
# Extract report
# ----------------------------------------------------

start = text.find("//The Wire//")
end = text.find("//END REPORT//")

if start == -1 or end == -1:
    raise RuntimeError("Found page but could not locate report markers.")

report = text[start:end + len("//END REPORT//")]

# remove excessive blank lines
report = re.sub(r"\n{3,}", "\n\n", report)

with open("wire.txt", "w", encoding="utf-8") as f:
    f.write("The Wire\n")
    f.write("========\n\n")
    f.write(report)
    f.write("\n")

print("Downloaded:")
print(found_url)
print("Saved to wire.txt")
