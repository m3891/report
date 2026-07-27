import urllib.request
import urllib.error
import re
from datetime import datetime, timedelta, UTC

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
            print("Final URL:", r.geturl())
            return r.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError:
        return None
    except Exception:
        return None



today = datetime.now(UTC).date()

html = None
found_url = None

for i in range(10):

    d = today - timedelta(days=i)

    month_name = MONTHS[d.month - 1]
    month_folder = f"{month_name}+{d.year}"

    page = f"The+Wire+-+{month_name}+{d.day}%2C+{d.year}"

    url = (
        "https://publish.obsidian.md/"
        "s2underground/"
        "S2+Underground+PUBLISH/"
        "02+Wire+Reports/"
        f"{month_folder}/"
        f"{page}"
    )

    print(f"Trying {url}")

    candidate = fetch(url)

    if candidate is None:
        continue

    # Save the downloaded page for debugging
    with open("debug.md", "a", encoding="utf-8") as f:
        f.write("\n========================\n")
        f.write(md_url + "\n\n")
        f.write(markdown or "fetch() returned None")
        f.write("\n")
        
    print("Downloaded page:", url)

    # Extract the markdown URL from the HTML
    m = re.search(r'window\.preloadPage=f\("([^"]+)"\)', candidate)

    if not m:
        continue

    md_url = m.group(1)

    print("Markdown URL:", md_url)

    markdown = fetch(md_url)

    with open("debug.md", "w", encoding="utf-8") as f:
        if markdown is None:
            f.write("fetch() returned None")
        else:
            f.write(markdown)
    
    if markdown is None:
        continue
    
    # Obsidian returns a "Not Found" page instead of a 404.
    if markdown.lstrip().startswith("Not Found"):
        print("Markdown file does not exist yet.")
        continue
    
    html = markdown
    found_url = md_url
    break

if html is None:
    print("No Wire report found in the last 10 days.")
    html = ""
    found_url = "None"
    
text = html

text = html.replace("\ufeff", "")

# ----------------------------------------------------
# Strip HTML
# ----------------------------------------------------

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
    with open("wire.txt", "w", encoding="utf-8") as f:
        f.write("No report markers found.\n")
        f.write(f"Last URL checked:\n{found_url}\n")
    print("Report markers not found.")
    exit(0)

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
