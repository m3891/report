import urllib.request
import urllib.error
import re
from datetime import datetime, timedelta, UTC

HEADERS = {
    "User-Agent": "WireFetcher/2.0"
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
            print("GET:", r.geturl())
            return r.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError:
        return None
    except Exception as e:
        print(e)
        return None


today = datetime.now(UTC).date()

report = None
report_url = None

for i in range(10):

    d = today - timedelta(days=i)

    month = MONTHS[d.month - 1]

    page_url = (
        "https://publish.obsidian.md/"
        "s2underground/"
        "S2+Underground+PUBLISH/"
        "02+Wire+Reports/"
        f"{month}+{d.year}/"
        f"The+Wire+-+{month}+{d.day}%2C+{d.year}"
    )

    print()
    print("Checking:", page_url)

    html = fetch(page_url)

    if html is None:
        continue

    # Find hidden markdown URL
    m = re.search(r'window\.preloadPage=f\("([^"]+)"\)', html)

    if not m:
        print("No markdown link.")
        continue

    md_url = m.group(1)

    print("Markdown:", md_url)

    markdown = fetch(md_url)

    if markdown is None:
        continue

    # Save latest markdown for debugging
    with open("debug.md", "w", encoding="utf-8") as f:
        f.write(markdown)

    # Obsidian returns a text page instead of a 404.
    if markdown.lstrip().startswith("## Not Found") \
       or markdown.lstrip().startswith("Not Found"):
        print("Markdown not published yet.")
        continue

    start = markdown.find("//The Wire//")
    end = markdown.find("//END REPORT//")

    if start == -1 or end == -1:
        print("Report markers missing.")
        continue

    report = markdown[start:end + len("//END REPORT//")]
    report_url = md_url

    break


if report is None:
    raise RuntimeError("No Wire report found in the last 10 days.")


report = report.replace("\ufeff", "")
report = re.sub(r"\n{3,}", "\n\n", report)

with open("wire.txt", "w", encoding="utf-8") as f:
    f.write("The Wire\n")
    f.write("========\n\n")
    f.write(report)
    f.write("\n")

print()
print("SUCCESS")
print(report_url)
print("Saved wire.txt")
