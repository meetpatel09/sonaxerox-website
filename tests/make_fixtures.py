#!/usr/bin/env python3
"""Generate every test photo / PDF into tests/.fixtures (deterministic, nothing is downloaded, nothing is committed).

    python3 tests/make_fixtures.py          # the normal set (about 10 s)
    python3 tests/make_fixtures.py --slow   # + the heavy photos used by the slow tests
"""
import math, os, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
FIX = HERE / ".fixtures"
FONT_PATHS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf", "/Library/Fonts/Arial.ttf", "C:/Windows/Fonts/arial.ttf"]


def font(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def pdfs():
    import pymupdf
    for name, n in (("p6.pdf", 6), ("p35.pdf", 35)):
        d = pymupdf.open()
        for i in range(1, n + 1):
            pg = d.new_page(width=595, height=842)
            pg.insert_text((72, 200), f"PAGE-{i}", fontsize=60)
            pg.insert_text((72, 300), "Small text for zoom testing: the quick brown fox jumps over the lazy dog.", fontsize=9)
        d.save(FIX / name)
    # a synthetic e-Aadhaar style page: two cards at the bottom (the Aadhaar tool crops them by position)
    W, H = 612, 792
    d = pymupdf.open(); pg = d.new_page(width=W, height=H)
    pg.insert_text((50, 60), "e-Aadhaar (test file)", fontsize=14)
    for x0, label in ((0.0784 * W, "FRONT"), (0.5071 * W, "BACK")):
        cw = 253.6; ch = cw / (85.6 / 54); bottom = 0.9264 * H; top = bottom - ch
        pg.draw_rect(pymupdf.Rect(x0, top, x0 + cw, bottom), color=None, fill=(1, 0.99, 0.96))
        pg.draw_rect(pymupdf.Rect(x0, top, x0 + cw, top + 20), color=None, fill=(0.93, 0.45, 0.35))
        pg.insert_text((x0 + 8, top + 14), "Government of India", fontsize=9, color=(1, 1, 1))
        pg.draw_rect(pymupdf.Rect(x0 + 10, top + 34, x0 + 62, top + 98), color=None, fill=(0.55, 0.68, 0.88))
        pg.insert_text((x0 + 72, top + 55), "Meet Patel", fontsize=13, color=(0.42, 0.42, 0.42))
        pg.insert_text((x0 + 72, top + 72), "DOB: 01/01/1996", fontsize=8.5, color=(0.55, 0.55, 0.55))
        pg.insert_text((x0 + 50, top + 135), "1234 5678 9012", fontsize=16, color=(0.15, 0.15, 0.15))
        pg.insert_text((x0 + 8, top + 152), label, fontsize=7, color=(0.5, 0.5, 0.5))
    d.save(FIX / "card.pdf")
    d.save(FIX / "card_locked.pdf", encryption=pymupdf.PDF_ENCRYPT_AES_256, user_pw="TESTPASS1", owner_pw="owner")


def markers():
    """Four coloured squares exactly under the scan tool's default corner dots (8% inset)."""
    W, H = 1600, 1200
    yy, xx = np.mgrid[0:H, 0:W]
    bg = np.stack([150 + 30 * np.sin(xx / 200), 150 + 30 * np.sin(yy / 170), 160 + 0 * xx], -1).astype(np.uint8)
    im = Image.fromarray(bg); d = ImageDraw.Draw(im)
    for x, y, c in ((0.08 * W, 0.08 * H, (230, 20, 30)), (0.92 * W, 0.08 * H, (20, 200, 40)), (0.92 * W, 0.92 * H, (20, 40, 230)), (0.08 * W, 0.92 * H, (250, 220, 0))):
        d.rectangle([x - 45, y - 45, x + 45, y + 45], fill=c)
    d.text((W / 2 - 200, H / 2), "MARKERS", font=font(90), fill=(30, 30, 30))
    im.save(FIX / "markers.jpg", quality=95)
    import pillow_heif
    pillow_heif.register_heif_opener()
    im.save(FIX / "markers.heic", quality=85)


def tilted_paper():
    pw, ph = 800, 1000
    paper = Image.new("RGB", (pw, ph), (250, 250, 245)); pd = ImageDraw.Draw(paper)
    for i in range(14):
        pd.text((90, 160 + i * 52), "The quick brown fox jumps over the lazy dog %02d" % i, font=font(26), fill=(40, 40, 50))
    for x, y, c in ((20, 20, (230, 20, 30)), (pw - 80, 20, (20, 200, 40)), (pw - 80, ph - 80, (20, 40, 230)), (20, ph - 80, (250, 220, 0))):
        pd.rectangle([x, y, x + 60, y + 60], fill=c)
    rot = paper.rotate(-12, expand=True, resample=Image.BICUBIC, fillcolor=(0, 0, 0))
    mask = Image.new("L", (pw, ph), 255).rotate(-12, expand=True)
    table = Image.new("RGB", (1600, 1200), (70, 55, 45))
    table.paste(rot, ((1600 - rot.width) // 2, (1200 - rot.height) // 2), mask)
    table.save(FIX / "tilted_paper.jpg", quality=95)


def keystone(t0_deg, name):
    """A flat checkerboard 'photographed' with a known top/bottom squeeze, so the Vertical slider has an exact answer."""
    W, H, cell = 1600, 1200, 100
    yy, xx = np.mgrid[0:H, 0:W]
    flat = np.where(((xx // cell) + (yy // cell)) % 2 == 0, 30, 240).astype(np.uint8); flat = np.stack([flat] * 3, -1)
    im = Image.fromarray(flat); d = ImageDraw.Draw(im)
    for x, y, c in ((10, 10, (230, 20, 30)), (W - 70, 10, (20, 200, 40)), (W - 70, H - 70, (20, 40, 230)), (10, H - 70, (250, 220, 0))):
        d.rectangle([x, y, x + 60, y + 60], fill=c)
    flat = np.asarray(im).astype(np.float32)
    phi = math.radians(t0_deg); s, c = math.sin(phi), math.cos(phi); f = 1.3 * max(W, H); cx, cy = W / 2, H / 2
    X, Y = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5); dx, dy = X - cx, Y - cy; dd = f + dy * s
    Sx = cx + f * dx / dd; Sy = cy + f * dy * c / dd
    x0 = np.floor(Sx - 0.5).astype(int); y0 = np.floor(Sy - 0.5).astype(int); fx = (Sx - 0.5) - x0; fy = (Sy - 0.5) - y0
    out = np.full((H, W, 3), 128, np.float32); ok = (x0 >= 0) & (y0 >= 0) & (x0 < W - 1) & (y0 < H - 1)
    xi = np.clip(x0, 0, W - 2); yi = np.clip(y0, 0, H - 2)
    for ch in range(3):
        v = (flat[yi, xi, ch] * (1 - fx) * (1 - fy) + flat[yi, xi + 1, ch] * fx * (1 - fy) + flat[yi + 1, xi, ch] * (1 - fx) * fy + flat[yi + 1, xi + 1, ch] * fx * fy)
        out[..., ch] = np.where(ok, v, 128)
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(FIX / name, quality=95)


def doc_photo():
    """A phone photo of a certificate: uneven light, a shadow band, yellow cast, noise, stored sideways with an EXIF rotation flag."""
    rng = np.random.default_rng(3)
    W, H = 3000, 4000
    page = Image.new("RGB", (W, H), (252, 250, 244)); d = ImageDraw.Draw(page)
    d.text((200, 160), "SONA XEROX — SAMPLE CERTIFICATE", font=font(110), fill=(30, 30, 40))
    y = 420
    for i in range(26):
        line = ("Name of candidate: Kamlesh Patel   Roll no. %05d   Result: PASS   Grade: A" % (1000 + i * 7)) if i % 5 == 0 else "The quick brown fox jumps over the lazy dog, again and again, to test printing clarity."
        d.text((200, y), line, font=font(58), fill=(55, 55, 70)); y += 96
    d.rectangle([200, 2950, 760, 3750], fill=(70, 50, 40))                   # a big dark block (like an ID photo)
    d.ellipse([1900, 2950, 2700, 3750], outline=(190, 30, 40), width=24)    # a red stamp
    d.text((1990, 3300), "PASSED", font=font(120), fill=(190, 30, 40))
    a = np.asarray(page).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    light = 1.0 - 0.45 * ((xx / W) * 0.5 + (yy / H) * 0.9) / 1.4
    band = 1.0 - 0.28 * np.exp(-(((xx - 0.35 * W) - (yy - 0.5 * H) * 0.6) / (0.12 * W)) ** 2)
    a = a * (light * band)[..., None] * np.array([1.0, 0.95, 0.80], dtype=np.float32)[None, None, :]
    a += rng.normal(0, 5, a.shape)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    ex = Image.Exif(); ex[0x0112] = 6
    img.rotate(90, expand=True).save(FIX / "doc_photo.jpg", quality=88, exif=ex)


def other_images():
    rng = np.random.default_rng(1)
    W2, H2 = 2400, 1600
    yy, xx = np.mgrid[0:H2, 0:W2].astype(np.float32)
    sky = np.stack([90 + 60 * (yy / H2), 140 + 60 * (yy / H2), 230 - 40 * (yy / H2)], -1)
    ground = np.stack([60 + 30 * (xx / W2), 120 + 40 * (1 - yy / H2), 50 + 20 * (xx / W2)], -1)
    p = Image.fromarray(np.clip(np.where((yy < H2 * 0.55)[..., None], sky, ground), 0, 255).astype(np.uint8)); dd = ImageDraw.Draw(p)
    dd.ellipse([300, 500, 900, 1100], fill=(220, 170, 120)); dd.rectangle([1300, 700, 1900, 1300], fill=(200, 60, 50)); dd.ellipse([1700, 150, 2000, 450], fill=(255, 230, 120))
    arr = np.asarray(p).astype(np.float32) * 0.42 + rng.normal(0, 3, (H2, W2, 3))
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(FIX / "photo_dark.jpg", quality=90)
    png = Image.new("RGBA", (800, 800), (0, 0, 0, 0)); g = ImageDraw.Draw(png)
    g.ellipse([100, 100, 700, 700], fill=(220, 40, 60, 255)); g.text((250, 350), "LOGO", font=font(140), fill=(255, 255, 255, 255))
    png.save(FIX / "logo.png")
    yy, xx = np.mgrid[0:4500, 0:6000].astype(np.float32)
    big = np.stack([128 + 100 * np.sin(xx / 500), 128 + 100 * np.sin(yy / 400), 128 + 100 * np.sin((xx + yy) / 700)], -1)
    Image.fromarray(np.clip(big, 0, 255).astype(np.uint8)).save(FIX / "big.jpg", quality=85)
    small = Image.fromarray((rng.random((60, 40, 3)) * 255).astype(np.uint8))
    for i in range(31):
        small.save(FIX / f"tiny_{i:02d}.jpg")
    (FIX / "garbage.jpg").write_text("not an image at all")
    (FIX / "fake.heic").write_bytes(b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00heicmif1garbage-garbage-garbage")


def slow_images():
    rng = np.random.default_rng(7)
    yy, xx = np.mgrid[0:6000:4, 0:9000:4]
    small = np.stack([128 + 100 * np.sin(xx / 300), 128 + 100 * np.sin(yy / 250), 128 + 100 * np.sin((xx + yy) / 400)], -1).astype(np.uint8)
    Image.fromarray(small).resize((9000, 6000), Image.BILINEAR).save(FIX / "huge.jpg", quality=80)          # 54 megapixels
    for i in range(6):                                                                                       # incompressible: forces the PDF size fallback
        Image.fromarray((rng.random((2000, 3000, 3)) * 255).astype(np.uint8)).save(FIX / f"noise_{i}.jpg", quality=92)


def ensure(slow=False, force=False):
    FIX.mkdir(exist_ok=True)
    stamp = FIX / (".done-slow" if slow else ".done")
    if stamp.exists() and not force:
        return
    pdfs(); markers(); tilted_paper(); keystone(24, "keystone.jpg"); keystone(-24, "keystone_neg.jpg"); doc_photo(); other_images()
    if slow:
        slow_images()
    stamp.write_text("ok")


if __name__ == "__main__":
    ensure(slow="--slow" in sys.argv, force=True)
    print("fixtures ready in", FIX)
