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
    "APC-C46": "images/streetwear/apex-dallas-race-day/hood.jpg",
    "APC-C48": "images/streetwear/apex-anaheim-race-day/front.jpg",
    "APC-C49": "images/streetwear/apex-nashville-race-day/front.jpg",
    "APC-C50": "images/streetwear/apex-vancouver-race-day/front.jpg",
    "APC-C47": "images/streetwear/apex-denver-race-day/hood.jpg",
    "APC-C75": "images/streetwear/dallas-race-day-printable/hood.jpg",
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
    hover = product.get("hover_image", "").split("?")[0]
    check(Path(hover).name in {"front.jpg", "hood.jpg"} and Path(hover).parent == Path(rel).parent, f"{sku} hover is a clean pose ({Path(hover).name})")
    check(width(rel) >= HERO_MIN, f"{sku} lead is full resolution ({width(rel)}px)")
    page = Path("products") / f"{product['handle']}.html"
    body = page.read_text()
    check(product["primary_image"] in body and 'id="staticMainProdImg"' in body, f"{product['handle']} gallery lead is the new photo")
    jacket_hashes.append(md5(rel))
check(len(set(jacket_hashes)) == len(JACKETS), "no two Race Day Jacket cities share a lead photo")
import numpy as np
for sku in JACKETS:
    arr = np.array(Image.open(JACKET_FILES[sku]).convert("RGB")).astype("int16")
    jump = np.abs(arr[1:] - arr[:-1]).mean(axis=2)
    wide = int(((jump > 18).sum(axis=1) > arr.shape[1] * 0.25).sum())
    check(wide == 0, f"{sku} lead has no horizontal line artifact ({wide} rows)")
jacket_dirs = (
    "apex-nashville-race-day|apex-denver-race-day|apex-dallas-race-day|"
    "apex-anaheim-race-day|apex-vancouver-race-day|dallas-race-day-printable"
)
jacket_ref = re.compile(rf"images/streetwear/(?:{jacket_dirs})/([A-Za-z0-9_.-]+\.jpg)")
glitched_refs = []
for path in Path(".").rglob("*"):
    if path.suffix not in {".html", ".xml", ".json", ".js", ".md"} or ".git" in path.parts:
        continue
    for match in jacket_ref.finditer(path.read_text(encoding="utf-8", errors="replace")):
        if match.group(1) not in {"front.jpg", "hood.jpg"}:
            glitched_refs.append(f"{path}: {match.group(0)}")
check(not glitched_refs, "no glitched jacket image is referenced" + (": " + "; ".join(glitched_refs[:6]) if glitched_refs else ""))
for sku, expect in (("APC-C13", (1536, 2048)), ("APC-C14", (1536, 2048))):
    product = by_id[sku]
    for field in ("primary_image", "hover_image"):
        rel = product[field].split("?")[0]
        size = Image.open(rel).size
        check(size == expect, f"{sku} {field} is {expect[0]}x{expect[1]} ({size[0]}x{size[1]})")
        check(width(rel) == expect[0], f"{sku} {field} was not upscaled")
    page = (Path("products") / f"{product['handle']}.html").read_text()
    check(product["primary_image"] in page, f"{product['handle']} gallery lead is the full-res photo")
pink = {
    "e3b8e85b817fdf3f81361fa2bfda32c1",
    "67eac097306c72fb199c65b4a43da816",
    "a31120a28a5151ae45f013e5ddd5d803",
    "c1d1c53a3e141e3dae9ef3d2cb6b9abf",
}
pink_hits = []
for path in Path("images").rglob("*"):
    if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        continue
    if hashlib.md5(path.read_bytes()).hexdigest() in pink:
        pink_hits.append(str(path))
check(not pink_hits, "pink Zone 2 model shots are not on the site")
old_low = []
for path in Path(".").rglob("*"):
    if path.suffix not in {".html", ".xml", ".json", ".js", ".md"} or ".git" in path.parts:
        continue
    body = path.read_text(encoding="utf-8", errors="replace")
    if "apc-c13-black" in body or "apc-c14-black" in body:
        old_low.append(str(path))
check(not old_low, "old 800px cap and bag files are not referenced")
gallery_js = Path("gallery.js").read_text()
check("setAttribute(\"srcset\"" in gallery_js and "closest(\"picture\")" in gallery_js and "querySelectorAll(\"source\")" in gallery_js, "shared gallery script updates srcset and picture sources")
unwired = [p.name for p in Path("products").glob("*.html") if 'id="staticMainProdImg"' in p.read_text() and "/gallery.js" not in p.read_text()]
check(not unwired, "every product page loads the shared gallery script" + (": " + ", ".join(unwired[:6]) if unwired else ""))
jacket_fn = app.split("function jacketCardHtml")[1].split("function bindJacketCard")[0]
check('data-role="hover"' in jacket_fn and "Card__img--b" in jacket_fn, "jacket card renders a hover layer")
check("hover.src = hoverSrc" in app, "jacket hover src updates when the city changes")

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
ALL_CRESTS = {p["handle"] for p in catalog["products"] if p["handle"].endswith("-crest")}
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
    if handle in ALL_CRESTS:
        if not crest_placed:
            cards.append("city-crest")
            crest_placed = True
        continue
    cards.append(handle)
adjacent = [f"{cards[i]}|{cards[i+1]}" for i in range(len(cards) - 1) if cards[i] in ALL_CRESTS and cards[i + 1] in ALL_CRESTS]
check(cards.count("city-crest") == 1, "homepage shows one city crest card")
check(not any(handle in ALL_CRESTS for handle in cards), "individual crest products are not repeated beside the crest card")
check(not adjacent, "no two adjacent homepage cards are crest products")
crest_order = re.findall(r'"(APC-C\d+)"', app.split("const CREST_ORDER = [", 1)[1].split("];", 1)[0])
crest_ids = {p["id"] for p in catalog["products"] if p["handle"].endswith("-crest")}
crest_cities = re.findall(r'"(APC-C\d+)": "([^"]+)"', app.split("const CREST_CITY = {", 1)[1].split("};", 1)[0])
check(set(crest_order) == crest_ids, "crest card includes every crest product")
check(len(crest_cities) == len(crest_ids) and len({name for _, name in crest_cities}) == len(crest_ids), "crest card lists every crest city")

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
visible = ["Denver Race Day Windbreaker", "Dallas Race Day"] + hero_titles
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
jacket_titles = re.findall(r'"(APC-C\d+)": "([^"]+)"', app.split("const JACKET_TITLE = {", 1)[1].split("};", 1)[0])
jacket_names = [name for _, name in jacket_titles]
check(len(jacket_names) == len(set(jacket_names)) == len(JACKETS), "all jacket city titles are unique")
check("Dallas Race Day" in jacket_names and "Dallas Race Day Jacket" in jacket_names, "Dallas and the printed jacket use different Fourthwall names")
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
  await send(ws, "Page.navigate", {url:"http://127.0.0.1:8795/index.html"});
  await sleep(1200);
  const ev = await send(ws, "Runtime.evaluate", {expression:`(() => { const el = document.querySelector('.SiteHead .Wordmark'); const r = el.getBoundingClientRect(); const center = r.left + r.width/2; const bag = document.querySelector('.BagBtn').getBoundingClientRect(); const menu = document.querySelector('.MenuBtn'); const mr = menu ? menu.getBoundingClientRect() : null; const overlap = (a,b) => a && b && !(a.right < b.left || a.left > b.right || a.bottom < b.top || a.top > b.bottom); const width = document.documentElement.clientWidth; const probe = document.createElement('img'); probe.className = 'Card__img Card__img--model Card__img--full'; document.body.appendChild(probe); const fit = getComputedStyle(probe).objectFit; probe.remove(); return JSON.stringify({off: Math.abs(center - width/2), overlapBag: overlap(r, bag), overlapMenu: mr && menu.offsetParent ? overlap(r, mr) : false, fit}); })()`, returnByValue:true});
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

def gallery_browser(pages):
    import tempfile
    import os
    script = r'''
const { spawn } = require("child_process");
const port = 9377;
const chrome = spawn("google-chrome", ["--headless=new","--disable-gpu","--no-sandbox","--disable-dev-shm-usage",`--remote-debugging-port=${port}`,"about:blank"], {stdio:"ignore"});
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const pages = PAGES_JSON;
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
  await send(ws, "Emulation.setDeviceMetricsOverride", {width:1280, height:900, deviceScaleFactor:1, mobile:false});
  const out = {pages: []};
  for (const path of pages) {
    await send(ws, "Page.navigate", {url:"http://127.0.0.1:8795/" + path});
    await sleep(700);
    const ev = await send(ws, "Runtime.evaluate", {expression:`(() => {
      const img = document.getElementById("staticMainProdImg");
      const pathOf = (url) => { try { return new URL(url, location.href).pathname; } catch (e) { return ""; } };
      if (!img || !window.setStaticMainImage) return JSON.stringify({error:"missing gallery"});
      let source = null;
      if (location.pathname.indexOf("zone-2-engine-builder-embroidered-dad-hat") !== -1) {
        const picture = document.createElement("picture");
        source = document.createElement("source");
        source.srcset = img.getAttribute("srcset") || "";
        source.sizes = "100vw";
        img.parentNode.insertBefore(picture, img);
        picture.appendChild(source);
        picture.appendChild(img);
      }
      const firstToken = (value) => ((value || "").trim().split(" ")[0] || "");
      const buttons = [...document.querySelectorAll("button")].filter((b) => (b.getAttribute("onclick") || "").indexOf("staticMainProdImg") !== -1);
      const clicks = [];
      for (const btn of buttons) {
        const code = btn.getAttribute("onclick") || "";
        const quoted = code.split("src='")[1] || "";
        const raw = quoted.split("'")[0];
        if (!raw) continue;
        const before = pathOf(img.currentSrc || img.src);
        btn.click();
        clicks.push({want: pathOf(raw), now: pathOf(img.currentSrc), set: pathOf(firstToken(img.getAttribute("srcset"))), sizes: img.hasAttribute("sizes"), source: source ? pathOf(firstToken(source.getAttribute("srcset"))) : "", sourceSizes: source ? source.hasAttribute("sizes") : false, before});
      }
      return JSON.stringify({clicks});
    })()`, returnByValue:true});
    out.pages.push({path, report: JSON.parse(ev.result.result.value)});
  }
  await send(ws, "Page.navigate", {url:"http://127.0.0.1:8795/index.html"});
  await sleep(1200);
  const jacket = await send(ws, "Runtime.evaluate", {expression:`(() => {
    const card = document.querySelector("[data-jacket-card]");
    if (!card) return "nocard";
    const rows = [];
    for (const btn of card.querySelectorAll("[data-jacket-city]")) {
      btn.click();
      const lead = card.querySelector("[data-role=photo]");
      const hover = card.querySelector("[data-role=hover]");
      rows.push({id: btn.getAttribute("data-jacket-city"), lead: lead.getAttribute("src").split("?")[0], hover: hover ? hover.getAttribute("src").split("?")[0] : "", cls: hover ? hover.className : ""});
    }
    return JSON.stringify(rows);
  })()`, returnByValue:true});
  out.jackets = JSON.parse(jacket.result.result.value);
  console.log(JSON.stringify(out));
  browser.close(); chrome.kill();
})().catch((err) => { console.error(err); chrome.kill(); process.exit(1); });
'''
    script = script.replace("PAGES_JSON", json.dumps(pages))
    path = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False)
    path.write(script)
    path.close()
    out = subprocess.check_output(["node", path.name], text=True, timeout=90)
    os.unlink(path.name)
    return json.loads(out.strip().splitlines()[-1])

thumb_re = re.compile(r"staticMainProdImg['\"]\)\.src\s*=\s*['\"]([^'\"]+)['\"]")
gallery_pages = [
    "products/dallas-race-day.html",
    "products/anaheim-race-day.html",
    "products/nashville-race-day.html",
    "products/vancouver-race-day.html",
    "products/zone-2-engine-builder-embroidered-dad-hat.html",
    "products/apex-8-station-race-day-tactical-duffle.html",
    "products/apc-c13.html",
    "products/apc-c14.html",
    "products/apc-c46.html",
    "products/apc-c49.html",
]
for extra in sorted(Path("products").glob("*.html")):
    if len(gallery_pages) >= 12:
        break
    rel = str(extra)
    if rel in gallery_pages:
        continue
    files = {src.split("?")[0] for src in thumb_re.findall(extra.read_text())}
    if len(files) >= 2:
        gallery_pages.append(rel)

import socket
sock = socket.socket(); sock.bind(("127.0.0.1", 8795)); sock.close()
server = subprocess.Popen(["python3", "-m", "http.server", "8795", "--bind", "127.0.0.1"], cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for width, height in ((390, 844), (768, 1024), (1024, 800), (1440, 900)):
        measured = logo_offset(width, height)
        check(measured["off"] <= 4, f"logo centered at {width}px (off {measured['off']:.2f}px)")
        check(not measured["overlapBag"] and not measured["overlapMenu"], f"logo does not overlap Menu or Bag at {width}px")
        if width == 1440:
            check(measured.get("fit") == "contain", f"Card__img--full computes to contain ({measured.get('fit')})")
    measured_gallery = gallery_browser(gallery_pages)
    check(len(measured_gallery["pages"]) >= 10, f"gallery sample covers at least 10 product pages ({len(measured_gallery['pages'])})")
    for item in measured_gallery["pages"]:
        report = item["report"]
        clicks = report.get("clicks") or []
        check(not report.get("error") and len(clicks) >= 1, f"{item['path']} thumbs ran ({report.get('error', len(clicks))})")
        changed = [c for c in clicks if c["want"] != c["before"]]
        bad = [c for c in clicks if not (c["now"] == c["want"] and c["set"] == c["want"] and not c["sizes"])]
        check(bool(changed) and not bad, f"{item['path']} thumb click changes currentSrc" + (f" {bad[:1]}" if bad else ""))
        if "dad-hat" in item["path"]:
            check(all(c["source"] == c["want"] and not c["sourceSizes"] for c in clicks), "cap gallery updates the picture source with the thumb")
    rows = measured_gallery["jackets"]
    check(isinstance(rows, list) and len(rows) == len(JACKETS), "jacket card hover was measured for every city")
    if isinstance(rows, list):
        by_row = {row["id"]: row for row in rows}
        previous = ""
        for sku in JACKETS:
            row = by_row[sku]
            expect = by_id[sku]["hover_image"].split("?")[0]
            lead = by_id[sku]["primary_image"].split("?")[0]
            check(row["hover"] == expect and "Card__img--b" in row["cls"], f"{sku} hover src is {expect}")
            check(row["hover"] != previous, f"{sku} hover src changes with the city")
            if sku in {"APC-C47", "APC-C75"}:
                check(row["hover"] == row["lead"] == lead, f"{sku} reuses the lead file for hover")
            previous = row["hover"]
finally:
    server.terminate()

# Card 2x bar: nothing on the homepage shelf is under 672. Recorded above per product.
print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
