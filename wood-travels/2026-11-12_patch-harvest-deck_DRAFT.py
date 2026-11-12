# Adds the harvest decline to the deck of the "How Maine's trees are used" chart (November 12, 2026),
# after Adam Daigneault asked that the falling total harvest be shown. The by-product annual series is not
# in this folder, so the right panel stays as shares and the decline goes in the deck.
# Figures: 13.5 million green tons in 2011 and 10.0 million in 2023 (Maine Forest Service Wood Processor
# Reports, as shown on maineforestdashboard.com); (13.5 - 10.0) / 13.5 = 26%.
# Usage: python3 <script>   (run once on the image patched on November 11, 2026)
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
p = os.path.join(HERE, "2023_how-maines-trees-are-used-nofooter_DATA.png")
im = Image.open(p).convert("RGB"); d = ImageDraw.Draw(im)
assert im.size == (3900, 1890), "expects the November 11 patched image"
bg = im.getpixel((20, 20))
s = 20
while ImageFont.truetype(SANS, s + 1).getlength("to 44%.") <= 176:
    s += 1
d.rectangle([60, 150, 3899, 250], fill=bg)
d.text((105, 215), "Maine landowners harvested 10.0 million green tons of wood in 2023, down 26% from 13.5 million in 2011, and pulpwood's share fell from 57% to 44%.",
       font=ImageFont.truetype(SANS, s), fill=(60, 70, 65), anchor="ls")
im.save(p)
print("patched", ImageFont.truetype(SANS, s).getlength("Maine landowners harvested 10.0 million green tons of wood in 2023, down 26% from 13.5 million in 2011, and pulpwood's share fell from 57% to 44%."))
