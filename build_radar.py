import io
import urllib.request
from PIL import Image

URL = "https://radar.weather.gov/ridge/standard/KCLE_0.gif"
WIDTH = 300      # try 250-400
COLORS = 16      # try 8-32

req = urllib.request.Request(URL, headers={"User-Agent": "WinlinkCustomReport/3.0"})
with urllib.request.urlopen(req, timeout=30) as r:
    data = r.read()

img = Image.open(io.BytesIO(data)).convert("RGB")   # RGB first: real resampling + real quantize
h = round(img.height * WIDTH / img.width)
img = img.resize((WIDTH, h), Image.LANCZOS)         # full frame, no crop
img = img.quantize(colors=COLORS, method=Image.MEDIANCUT, dither=Image.NONE)
img.save("radar.gif", optimize=True)

print("Saved radar.gif", img.size)
