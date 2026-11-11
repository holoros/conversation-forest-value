# Patches headlines on two finished graphics whose source scripts run in R on another machine (November 11, 2026).
# 1. Leakage map: headline states the finding; Brazil callout says "imports" to match the source and the article.
# 2. How Maine's trees are used: headline states the finding; three-sentence deck cut to one.
# Usage: python3 <script>   (reads and writes PNGs in this folder; the unpatched files stay in git history)
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def fit(path, text, width):
    """Font size at which `text` is `width` pixels wide."""
    s = 20
    while ImageFont.truetype(path, s + 1).getlength(text) <= width:
        s += 1
    return s


# ---- 1. leakage map ----
p = os.path.join(HERE, "2026-11-10_follow-the-wood-leakage-map-nofooter_DRAFT.png")
im = Image.open(p).convert("RGB"); d = ImageDraw.Draw(im)
size = fit(SERIF_B, "Follow the wood, and the leakage", 1281)
d.rectangle([600, 40, 2999, 168], fill=(255, 255, 255))
f = ImageFont.truetype(SERIF_B, size)
d.text((640, 135), "The wood behind a paper towel now travels farther", font=f, fill=(31, 77, 54), anchor="ls")
# Brazil callout: find the box interior from its black border, clear it, and redraw three centered lines
arr = np.array(im)[2380:2620, 1560:2380].astype(int)
dark = (arr.sum(axis=2) < 120)
rows = np.where(dark.sum(axis=1) > 400)[0]; cols = np.where(dark.sum(axis=0) > 100)[0]
top, bot, left, right = rows.min() + 2380, rows.max() + 2380, cols.min() + 1560, cols.max() + 1560
d.rectangle([left + 8, top + 8, right - 8, bot - 8], fill=(255, 255, 255))
lines = ["Brazil supplies about 82% of", "the hardwood pulp the U.S. imports,", "mostly from eucalyptus plantations"]
fs = fit(SANS, "mostly from eucalyptus plantations", 663)
while ImageFont.truetype(SANS, fs).getlength(lines[1]) > (right - left - 40):
    fs -= 1
fb = ImageFont.truetype(SANS, fs)
cy = (top + bot) / 2 - 7
for i, t in enumerate(lines):
    d.text(((left + right) / 2, cy + (i - 1) * 55), t, font=fb, fill=(0, 0, 0), anchor="mm")
im.save(p)

# ---- 2. how Maine's trees are used ----
p = os.path.join(HERE, "2023_how-maines-trees-are-used-nofooter_DATA.png")
im = Image.open(p).convert("RGB"); d = ImageDraw.Draw(im)
assert im.size[1] == 2000, "already patched"
bg = im.getpixel((20, 20))
size = fit(SERIF_B, "How Maine's trees are used", 1262)
dsize = fit(SANS, "to 44%.", 176)
d.rectangle([60, 30, 3899, 365], fill=bg)
d.text((104, 132), "A fifth of Maine's harvest leaves the state as raw wood", font=ImageFont.truetype(SERIF_B, size), fill=(22, 59, 39), anchor="ls")
d.text((105, 215), "Maine landowners harvested 10.0 million green tons of wood in 2023, and pulpwood's share has fallen from 57% to 44% since 2011.",
       font=ImageFont.truetype(SANS, dsize), fill=(60, 70, 65), anchor="ls")
# close the gap left by the shorter deck
arr = np.array(im); gap = 110
arr[250:-gap] = arr[250 + gap:]
im = Image.fromarray(arr[:-gap])
im.save(p)
print("patched")
