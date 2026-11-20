#!/usr/bin/env python3
"""Homepage layout checks. Does not rebuild feeds."""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

HERO = ["APC-C01", "APC-C02", "APC-C03", "APC-C07"]
HERO_FILES = {
    "APC-C01": "images/streetwear/hyrx-art/apc-c01-03.jpg",
    "APC-C02": "images/streetwear/hyrx-art/apc-c02-03.jpg",
    "APC-C07": "images/streetwear/hyrx-art/apc-c07-03.jpg",
    "APC-C03": "images/streetwear/hyrx-art/apc-c03-03.jpg",
}
JACKETS = ["APC-C46", "APC-C48", "APC-C49", "APC-C50", "APC-C47", "APC-C75"]
JACKET_FILES = {
    "APC-C46": "images/streetwear/apex-dallas-race-day/03.jpg",
    "APC-C48": "images/streetwear/apex-anaheim-race-day/03.jpg",
    "APC-C49": "images/streetwear/apex-nashville-race-day/03.jpg",
    "APC-C50": "images/streetwear/apex-vancouver-race-day/03.jpg",
    "APC-C47": "images/streetwear/apex-denver-race-day/05.jpg",
    "APC-C75": "images/streetwear/dallas-race-day-printable/05.jpg",
}
CARD_MIN = 672
HERO_MIN = 1364
failures = []


def check(ok, message):
    print(("ok  " if ok else "FAIL") + " " + message)
    if not ok:
        failures.append(message)


def md5(path):
    return hashlib.md5(Path(path).read_bytes()).hexdigest()


def width(path):
    return Image.open(path).size[0]


html = Path("index.html").read_text()
main = html.split("<main>", 1)[1].split("</main>", 1)[0]
sections = re.findall(r"<section\b[^>]*>", main)
check(len(sections) >= 3, "homepage has the windbreaker, hero, and apparel sections")
check('id="race-day-switch"' in sections[0], "section 1 is the Race Day Windbreaker switcher")
check('class="Hero"' in sections[1], "section 2 is the hero")
check('id="apparel"' in sections[2], "section 3 is the Apparel & Race Gear grid")
check("Built for the 8th Station." in main and "Shop apparel" in main and "City editions" in main, "hero keeps its headline and both buttons")
for phrase in (
    "Best sellers",
    "Best seller",
    "Keep scrolling",
    "Race Day tees",
    "Every Day of the Block",
    "Shop by Training Block",
    "apexStickyPromoBar",
    'class="Train"',
    'class="Spot"',
    'class="Best"',
    'class="RW"',
    'class="Cities"',
    'id="best"',
):
    check(phrase not in html, f"removed from homepage: {phrase}")

hero_srcs = re.findall(r'<div class="Hero__gallery">([\s\S]*?)</div>\s*</div>\s*</section>', main)
check(bool(hero_srcs), "hero gallery parsed")
srcs = re.findall(r'src="([^"]+)"', hero_srcs[0] if hero_srcs else "")
check(len(srcs) == 4, f"hero has 4 tee images ({len(srcs)})")
check(len(set(srcs)) == 4, "hero tee image URLs are distinct")
hashes = []
for sku, rel in HERO_FILES.items():
    check(rel in "".join(srcs), f"{sku} uses {rel}")
    check(Path(rel).exists() and width(rel) >= HERO_MIN, f"{sku} lead is at least {HERO_MIN}px")
    hashes.append(md5(rel))
check(len(set(hashes)) == 4, "hero tee files are four different photos")
check('srcset="' in (hero_srcs[0] if hero_srcs else ""), "hero images declare a 2x source")

app = Path("app.js").read_text()
check("JACKET_ORDER" in app and "data-jacket-card" in app, "printed jackets collapse into one Race Day Jacket card")
check("Card__kind" not in app.split("function renderProducts")[1].split("function setDept")[0], "grid cards drop the kind sub-label")
check("QuickAdd" not in app.split("function renderProducts")[1].split("function setDept")[0], "grid cards drop size buttons")
check(">Buy</button>" in app, "grid cards keep one Buy button")
check("srcset=" in app, "card images declare a 2x source")
check("#EED202" not in html and "#EED202" not in Path("styles.css").read_text() and "#eed202" not in html.lower(), "no #EED202")

catalog = json.loads(Path("catalog.json").read_text())
by_id = {p["id"]: p for p in catalog["products"]}
jacket_hashes = []
for sku, rel in JACKET_FILES.items():
    product = by_id[sku]
    check(product["primary_image"].split("?")[0] == rel, f"{sku} card image is the Fourthwall lead")
    check(product.get("hover_image", "").split("?")[0] == rel, f"{sku} hover uses that same lead")
    check(width(rel) >= HERO_MIN, f"{sku} lead is full resolution ({width(rel)}px)")
    page = Path("products") / f"{product['handle']}.html"
    body = page.read_text()
    check(f"{rel}?v=20261120lead" in body and 'id="staticMainProdImg"' in body, f"{product['handle']} gallery lead is the new photo")
    jacket_hashes.append(md5(rel))
check(len(set(jacket_hashes)) == len(JACKETS), "no two Race Day Jacket cities share a lead photo")

# Homepage default shelf: apparel, without stitched windbreakers, hero tees, or printed jackets.
apparel = {
    "Breathable Tech Shirts",
    "Race City Editions",
    "Muscle Tanks",
    "Women's",
    "Tees & Pump Covers",
    "Hoodies",
    "Windbreakers",
    "Training Gear",
}
seen_paths = set(HERO_FILES.values()) | set(JACKET_FILES.values())
seen_hash = set(hashes) | set(jacket_hashes)
seen_ids = set(HERO) | set(JACKETS)
switch = json.loads(Path("race-day-switcher.json").read_text())
wind = switch["windbreakers"][0]["photo"].split("?")[0]
seen_paths.add(wind)
seen_hash.add(md5(wind))
dup_ids = []
dup_images = []
for product in catalog["products"]:
    if product["dept"] not in apparel:
        continue
    if "race-day-stitched" in (product.get("handle") or ""):
        continue
    if product["id"] in HERO or product["id"] in JACKETS:
        continue
    rel = (product.get("primary_image") or product.get("image") or "").split("?")[0]
    digest = md5(rel) if Path(rel).exists() else ""
    if product["id"] in seen_ids or rel in seen_paths or (digest and digest in seen_hash):
        dup_ids.append(product["handle"])
        dup_images.append(rel)
        continue
    seen_ids.add(product["id"])
    seen_paths.add(rel)
    if digest:
        seen_hash.add(digest)
    check(width(rel) >= CARD_MIN, f"{product['handle']} thumbnail is at least {CARD_MIN}px")
check(not dup_ids, "no duplicate product or image on the homepage" + (": " + ", ".join(dup_ids) if dup_ids else ""))

low = []
for product in catalog["products"]:
    paths = []
    for key in ("primary_image", "image", "hover_image", "alt_image"):
        val = product.get(key) or ""
        if val:
            paths.append(val.split("?")[0])
    for val in product.get("extra_images") or []:
        paths.append(val.split("?")[0])
    widths = [width(rel) for rel in dict.fromkeys(paths) if Path(rel).exists()]
    if widths and max(widths) < HERO_MIN:
        low.append(f"{product['handle']} ({max(widths)}px)")
print("LOW-RES (largest file under 1364px):")
for row in low:
    print("  " + row)
check(True, f"low-res slug count {len(low)}")

# Card 2x bar: nothing on the homepage shelf is under 672. Recorded above per product.
print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
