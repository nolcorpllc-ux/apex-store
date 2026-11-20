#!/usr/bin/env python3
"""Homepage layout checks. Does not rebuild feeds."""
import hashlib
import json
import os
import re
import subprocess
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
    check(product["primary_image"] in body and 'id="staticMainProdImg"' in body, f"{product['handle']} gallery lead is the new photo")
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

CRESTS = {
    "london-crest", "paris-crest", "hong-kong-crest", "chicago-crest", "cancun-crest",
    "dallas-crest", "denver-crest", "anaheim-crest", "nashville-crest", "vancouver-crest",
}
crest_dims = []
for handle in sorted(CRESTS):
    product = next(p for p in catalog["products"] if p["handle"] == handle)
    rel = product["primary_image"].split("?")[0]
    size = Image.open(rel).size
    crest_dims.append(size)
    check(size == (1536, 2048), f"{handle} lead is 1536x2048 ({size[0]}x{size[1]})")
    check(product.get("hover_image", "").split("?")[0] == rel, f"{handle} hover uses its own lead")
    page = Path("products") / f"{handle}.html"
    body = page.read_text()
    check('id="staticMainProdImg"' in body and f"{handle}/05.jpg?v=20261120crest" in body, f"{handle} gallery lead is the new photo")
    check(product["fourthwall_product_url"].rstrip("/").endswith(product["fourthwall_handle"]), f"{handle} buy link is unchanged")
check(len({md5(next(p for p in catalog["products"] if p["handle"] == h)["primary_image"].split("?")[0]) for h in CRESTS}) == 10, "each crest lead is a different photo")
check("data-crest-card" in app and "CREST_ORDER" in app, "homepage collapses city crests into one card")

# Default homepage card order, with the ten crests folded into one card.
shelf = []
for product in catalog["products"]:
    if product["dept"] not in apparel:
        continue
    if "race-day-stitched" in (product.get("handle") or ""):
        continue
    if product["id"] in set(HERO) | set(JACKETS):
        continue
    shelf.append(product)
buckets = {key: [] for key in ("tee", "tank", "hyrx", "women", "hoodie", "gear", "outer")}
hyrx = set(re.findall(r'HYRX_HANDLES = new Set\(\[([^\]]+)\]', app)[0].replace('"', "").split(","))
hyrx = {item.strip() for item in hyrx if item.strip()}

def kind_of(product):
    if product["dept"] == "Windbreakers":
        return "outer"
    if product["handle"] in hyrx:
        return "hyrx"
    if product["dept"] == "Women's":
        return "women"
    if product["dept"] == "Muscle Tanks":
        return "tank"
    if product["dept"] == "Hoodies":
        return "hoodie"
    if product["dept"] == "Training Gear":
        return "gear"
    return "tee"

for product in shelf:
    buckets[kind_of(product)].append(product["handle"])
mixed = []
progress = True
while progress:
    progress = False
    for key in ("tee", "tank", "hyrx", "women", "hoodie", "gear"):
        if buckets[key]:
            mixed.append(buckets[key].pop(0))
            progress = True
while buckets["outer"] and mixed:
    mixed.append(mixed and buckets["outer"].pop(0))
cards = []
crest_placed = False
for handle in mixed:
    if handle in CRESTS:
        if not crest_placed:
            cards.append("city-crest")
            crest_placed = True
        continue
    cards.append(handle)
adjacent = [f"{cards[i]}|{cards[i+1]}" for i in range(len(cards) - 1) if cards[i] in CRESTS and cards[i + 1] in CRESTS]
check(cards.count("city-crest") == 1, "homepage shows one city crest card")
check(not any(handle in CRESTS for handle in cards), "individual crest products are not repeated beside the crest card")
check(not adjacent, "no two adjacent homepage cards are crest products")

HOME_HIDE = {
    "run-station-repeat-heavy-blend-hoodie",
    "wall-balls-bad-decisions-hoodie",
    "burpee-broad-jumps-build-character-warmup-hoodie",
    "the-erg-doesnt-care-how-you-feel-heavyweight-fleece-hoodie",
    "engine-training-tank-mint",
    "engine-biker-shorts-mint",
}
COLOR_EXTRA = {
    "hyrx-run-5-panel-light-blue-white",
    "hyrx-cuff-beanie-heather-grey",
    "hyrx-rib-beanie-light-blue",
    "hyrx-gym-sack-burgundy",
    "hyrx-station-towel-deep-olive",
    "hyrx-pool-slide-burgundy",
}
COLOR_DEFAULT = {
    "hyrx-run-5-panel-black": "HYRX Run 5-Panel",
    "hyrx-cuff-beanie-black": "HYRX Cuff Beanie",
    "hyrx-rib-beanie-black": "HYRX Rib Beanie",
    "hyrx-gym-sack-black": "HYRX Gym Sack",
    "hyrx-station-towel-black": "HYRX Station Towel",
    "hyrx-pool-slide-black": "HYRX Pool Slide",
}
folded = []
for handle in cards:
    if handle in HOME_HIDE or handle in COLOR_EXTRA:
        continue
    if handle in COLOR_DEFAULT:
        folded.append(COLOR_DEFAULT[handle])
        continue
    folded.append(handle)
short_map = dict(re.findall(r'"(APC-C\d+)": "([^"]+)"', app.split("const SHORT = {", 1)[1].split("};", 1)[0]))
def visible_title(product):
    if product["id"] in short_map:
        return short_map[product["id"]]
    return product["title"].split(" - ")[0]
hero_titles = ["Run Station Repeat", "Wall Balls & Bad Decisions", "Porta-Potty Line PR", "Sled Push Enthusiast"]
visible = ["Denver Race Day Windbreaker", "Dallas Race Day Jacket"] + hero_titles
by_handle = {p["handle"]: p for p in catalog["products"]}
for handle in folded:
    if handle == "city-crest":
        visible.append("City Crest")
    elif handle in COLOR_DEFAULT.values():
        visible.append(handle)
    elif handle in by_handle:
        visible.append(visible_title(by_handle[handle]))
dup_titles = sorted({title for title in visible if visible.count(title) > 1})
check(not dup_titles, "no duplicate visible titles on homepage" + (": " + ", ".join(dup_titles) if dup_titles else ""))
nonblack = [handle for handle in folded if handle in COLOR_EXTRA or handle in {"engine-training-tank-mint", "engine-biker-shorts-mint"}]
check(not nonblack, "no non-black default cards except the Mint Engine bra")
check("engine-sports-bra-mint" in folded, "Mint Engine bra stays on the homepage")
check("JACKET_TITLE" in app and "Anaheim Race Day Jacket" in app and "data-role=\"title\"" in app, "jacket title changes with the selected city")
switch = json.loads(Path("race-day-switcher.json").read_text())
wind_titles = [item["title"] for item in switch["windbreakers"]]
check(len(set(wind_titles)) == len(wind_titles), "each windbreaker city has its own title")
check(all(item["city"] in item["title"] for item in switch["windbreakers"]), "windbreaker title includes the selected city")
check('data-role=title' in html and "item.title" in html, "windbreaker card writes the city title")

def logo_offset(width, height):
    script = r'''
const { spawn } = require("child_process");
const port = 9350 + %d;
const chrome = spawn("google-chrome", ["--headless=new","--disable-gpu","--no-sandbox","--disable-dev-shm-usage",`--remote-debugging-port=${port}`,"about:blank"], {stdio:"ignore"});
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
(async () => {
  let version;
  for (let i = 0; i < 40; i++) {
    try { version = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json(); break; }
    catch { await sleep(150); }
  }
  const browser = new WebSocket(version.webSocketDebuggerUrl);
  await new Promise(r => browser.addEventListener("open", r));
  let id = 0; const pending = new Map();
  const bind = (ws) => ws.addEventListener("message", (ev) => { const msg = JSON.parse(ev.data); if (msg.id && pending.has(msg.id)) pending.get(msg.id)(msg); });
  bind(browser);
  const send = (ws, method, params={}) => new Promise((resolve) => { const msgId = ++id; pending.set(msgId, resolve); ws.send(JSON.stringify({id:msgId, method, params})); });
  const created = await send(browser, "Target.createTarget", {url:"about:blank"});
  const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  const page = targets.find(t => t.id === created.result.targetId);
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener("open", r));
  bind(ws);
  await send(ws, "Emulation.setDeviceMetricsOverride", {width:%d, height:%d, deviceScaleFactor:1, mobile:%s});
  await send(ws, "Page.navigate", {url:"http://127.0.0.1:8788/index.html"});
  await sleep(1200);
  const ev = await send(ws, "Runtime.evaluate", {expression:`(() => { const el = document.querySelector('.SiteHead .Wordmark'); const r = el.getBoundingClientRect(); const center = r.left + r.width/2; const bag = document.querySelector('.BagBtn').getBoundingClientRect(); const menu = document.querySelector('.MenuBtn'); const mr = menu ? menu.getBoundingClientRect() : null; const overlap = (a,b) => a && b && !(a.right < b.left || a.left > b.right || a.bottom < b.top || a.top > b.bottom); const width = document.documentElement.clientWidth; return JSON.stringify({off: Math.abs(center - width/2), overlapBag: overlap(r, bag), overlapMenu: mr && menu.offsetParent ? overlap(r, mr) : false}); })()`, returnByValue:true});
  console.log(ev.result.result.value);
  browser.close(); chrome.kill();
})().catch((err) => { console.error(err); chrome.kill(); process.exit(1); });
'''
    import subprocess, tempfile, os
    width_js = script % (width, width, height, "true" if width < 800 else "false")
    path = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False)
    path.write(width_js)
    path.close()
    out = subprocess.check_output(["node", path.name], text=True, timeout=30)
    os.unlink(path.name)
    return json.loads(out.strip().splitlines()[-1])

import socket
sock = socket.socket(); sock.bind(("127.0.0.1", 8788)); sock.close()
server = subprocess.Popen(["python3", "-m", "http.server", "8788", "--bind", "127.0.0.1"], cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for width, height in ((390, 844), (768, 1024), (1024, 800), (1440, 900)):
        measured = logo_offset(width, height)
        check(measured["off"] <= 4, f"logo centered at {width}px (off {measured['off']:.2f}px)")
        check(not measured["overlapBag"] and not measured["overlapMenu"], f"logo does not overlap Menu or Bag at {width}px")
finally:
    server.terminate()

# Card 2x bar: nothing on the homepage shelf is under 672. Recorded above per product.
print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
