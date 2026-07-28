import urllib.request
from PIL import Image

URL = "https://radar.weather.gov/ridge/standard/KCLE_0.gif"

# Download latest radar
urllib.request.urlretrieve(URL, "radar_original.gif")

# Open image
img = Image.open("radar_original.gif")

# Resize (maintains aspect ratio)
img.thumbnail((350, 350))

# Reduce colors
img = img.convert("P", palette=Image.ADAPTIVE, colors=16)

# Save optimized GIF
img.save(
    "radar.gif",
    optimize=True,
)

print("Saved radar.gif")
