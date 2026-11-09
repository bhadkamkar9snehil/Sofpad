"""Draw the status screen shown in the renders (240 x 320 portrait). Needs Pillow:  py -3.12 -m pip install pillow
Writes build/screen_ui.png. It is a mock-up of the planned firmware screen, not captured output."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "build" / "screen_ui.png"
W, H = 240, 320


def font(size, bold=False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(rf"C:\Windows\Fonts\{name}", size)


img = Image.new("RGB", (W, H), (8, 12, 20))
d = ImageDraw.Draw(img)
# status bar
d.rectangle([0, 0, W, 34], fill=(16, 24, 38))
d.text((12, 8), "Bluetooth 1", font=font(16), fill=(120, 190, 255))
d.rounded_rectangle([170, 10, 218, 26], radius=3, outline=(200, 210, 220), width=2)
d.rectangle([173, 13, 173 + 34, 23], fill=(90, 220, 140))
d.rectangle([219, 14, 222, 22], fill=(200, 210, 220))
d.text((140, 8), "82%", font=font(15), fill=(200, 210, 220))
# clock
d.text((W // 2, 92), "21:45", font=font(64, True), fill=(235, 240, 250), anchor="mm")
d.text((W // 2, 136), "Tuesday 10 Nov", font=font(18), fill=(130, 150, 175), anchor="mm")
# layer
d.rounded_rectangle([14, 168, W - 14, 214], radius=10, fill=(20, 34, 56))
d.text((28, 178), "LAYER", font=font(12), fill=(110, 140, 175))
d.text((28, 192), "Base  (QWERTY)", font=font(18, True), fill=(235, 240, 250))
# now playing
d.rounded_rectangle([14, 226, W - 14, 306], radius=10, fill=(20, 34, 56))
d.text((28, 236), "NOW PLAYING", font=font(12), fill=(110, 140, 175))
d.text((28, 254), "Living room  -  Vol 32", font=font(16), fill=(235, 240, 250))
d.rounded_rectangle([28, 284, W - 28, 292], radius=4, fill=(40, 60, 90))
d.rounded_rectangle([28, 284, 28 + 70, 292], radius=4, fill=(90, 160, 255))
OUT.parent.mkdir(exist_ok=True)
img.save(OUT)
print("wrote", OUT)
