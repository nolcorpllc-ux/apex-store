#!/usr/bin/env python3
"""
Builds the complete SEO & Organic Traffic Architecture for Apex Hybrid Co., operated by NolCorp LLC:
1. 68 Static Product Landing Pages (/products/<handle>.html) with JSON-LD Product, Offer, AggregateRating, and BreadcrumbList schema + Nominative Fair-Use HYROX Compatibility SEO.
2. 16 High-Intent SEO Blog / Guide Pages (/articles/<slug>.html) with Article & FAQPage JSON-LD schema and internal product links.
3. Google Merchant Center RSS 2.0 XML Product Feed (/google_shopping_feed.xml) for Free Google Shopping Tab listings.
4. Pinterest / Meta Catalog CSV Feed (/pinterest_catalog_feed.csv).
5. Full XML Sitemap (/sitemap.xml), robots.txt (/robots.txt), and IndexNow verification key.
6. Injects crawlable static HTML product cards, guide links, and JSON-LD Store/ItemList/FAQPage schema directly into index.html (with ZERO item count tallies in navigation).
"""

import csv
import html
import json
import os
import re
import shutil
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://www.apexhybridco.com"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
INDEXNOW_KEY = "b7e3c9a4d2f841069c5e1a8f3b2d6e40"


def xml_text(value):
    """Escape text and URLs for XML element content and attributes."""
    return html.escape("" if value is None else str(value), quote=True)


def assert_no_trademark():
    """Fail the build if a trademark mark appears anywhere in published text."""
    mark = chr(8482)
    escapes = (mark, "&" + "trade;", "&" + "#8482;", "&" + "#x2122;", "&" + "#X2122;", "\\" + "u2122")
    skip = {".git", "__pycache__", "node_modules", "images"}
    suffixes = {".html", ".json", ".xml", ".js", ".py", ".txt", ".csv", ".css", ".md"}
    errors = []
    for dirpath, dirnames, filenames in os.walk(BASE_DIR):
        dirnames[:] = [name for name in dirnames if name not in skip]
        for name in filenames:
            if os.path.splitext(name)[1].lower() not in suffixes:
                continue
            path = os.path.join(dirpath, name)
            try:
                text = open(path, encoding="utf-8").read()
            except (OSError, UnicodeError):
                continue
            if any(token in text for token in escapes):
                errors.append(os.path.relpath(path, BASE_DIR))
    if errors:
        raise SystemExit("Trademark mark found:\n" + "\n".join(errors))


def _variant_ladders():
    """Handle -> size prices from each canonical product page."""
    ladders = {}
    products = os.path.join(BASE_DIR, "products")
    for name in os.listdir(products):
        if not name.endswith(".html"):
            continue
        text = open(os.path.join(products, name), encoding="utf-8", errors="replace").read()
        prices = re.search(r"var sizePrices = (\{.*?\});", text)
        canonical = re.search(
            r'rel="canonical" href="https://www\.apexhybridco\.com/products/([^"]+)\.html"',
            text,
        )
        if not prices or not canonical or canonical.group(1) in ladders:
            continue
        sizes = {key: float(value) for key, value in json.loads(prices.group(1)).items()}
        sku = re.search(r'var prodId = "(APC-C\d+)"', text)
        ladders[canonical.group(1)] = {
            "sizes": sizes,
            "min": min(sizes.values()),
            "sku": sku.group(1) if sku else "",
        }
    return ladders


def _json_object_at(text, start):
    opening = text.find("{", start)
    depth = 0
    in_string = False
    escaped = False
    for index in range(opening, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return opening, index + 1
    raise ValueError("unbalanced JSON")


def _product_nodes(node):
    found = []
    if isinstance(node, dict):
        if node.get("@type") == "Product" and node.get("offers"):
            found.append(node)
        for value in node.values():
            found.extend(_product_nodes(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(_product_nodes(value))
    return found


def assert_listed_prices():
    """Fail when a shown from-price or size offer disagrees with the live ladder."""
    ladders = _variant_ladders()
    errors = []

    def money(amount):
        return float(amount)

    for name in os.listdir(os.path.join(BASE_DIR, "products")):
        if not name.endswith(".html"):
            continue
        path = os.path.join(BASE_DIR, "products", name)
        text = open(path, encoding="utf-8", errors="replace").read()
        canonical = re.search(
            r'rel="canonical" href="https://www\.apexhybridco\.com/products/([^"]+)\.html"',
            text,
        )
        if not canonical or canonical.group(1) not in ladders:
            continue
        ladder = ladders[canonical.group(1)]
        meta = re.search(r'<meta property="product:price:amount" content="([^"]+)"', text)
        if meta and abs(money(meta.group(1)) - ladder["min"]) > 0.001:
            errors.append(f"{name}: product:price:amount {meta.group(1)} is not {ladder['min']:.2f}")
        marker = text.find('<script type="application/ld+json">')
        if marker < 0:
            continue
        start, end = _json_object_at(text, marker)
        data = json.loads(text[start:end])
        for product in _product_nodes(data):
            offers = product.get("offers") or {}
            if isinstance(offers, dict) and "lowPrice" in offers:
                if abs(money(offers["lowPrice"]) - ladder["min"]) > 0.001:
                    errors.append(f"{name}: lowPrice {offers['lowPrice']} is not {ladder['min']:.2f}")
            listed = offers.get("offers") if isinstance(offers, dict) else None
            if isinstance(offers, dict) and offers.get("@type") == "Offer":
                listed = [offers]
            found = {}
            for offer in listed or []:
                size = _offer_size(offer, ladder["sizes"])
                if size in ladder["sizes"]:
                    found[size] = money(offer.get("price"))
                    if abs(found[size] - ladder["sizes"][size]) > 0.001:
                        errors.append(f"{name}: {size} offer {offer.get('price')} is not {ladder['sizes'][size]:.2f}")
            missing = [size for size in ladder["sizes"] if size not in found]
            if missing:
                errors.append(f"{name}: JSON-LD missing {', '.join(missing)}")

    card_files = [os.path.join(BASE_DIR, "index.html")]
    for folder in ("collections", "articles", "seo_city_pages"):
        folder_path = os.path.join(BASE_DIR, folder)
        if os.path.isdir(folder_path):
            card_files.extend(
                os.path.join(folder_path, name)
                for name in os.listdir(folder_path)
                if name.endswith(".html")
            )
    for path in card_files:
        text = open(path, encoding="utf-8", errors="replace").read()
        rel = os.path.relpath(path, BASE_DIR)
        for match in re.finditer(
            r'<a\b[^>]*href="[^"]*products/([a-z0-9-]+)\.html"[^>]*>(.*?)</a>',
            text,
            re.S,
        ):
            handle, inner = match.group(1), match.group(2)
            if handle not in ladders or len(inner) > 2500:
                continue
            shown = re.search(r"<em>(?:from )?\$(\d+(?:\.\d{1,2})?)</em>", inner)
            if shown and abs(money(shown.group(1)) - ladders[handle]["min"]) > 0.001:
                errors.append(f"{rel}: {handle} card ${shown.group(1)} is not ${ladders[handle]['min']:.0f}")
            for amount in re.findall(r"\$(\d+(?:\.\d{1,2})?)", inner):
                value = money(amount)
                allowed = set(ladders[handle]["sizes"].values())
                if all(abs(value - price) > 0.001 for price in allowed):
                    errors.append(f"{rel}: {handle} shows ${amount}, not a live size price")
        for match in re.finditer(r'<article class="ShopStrip__card">(.*?)</article>', text, re.S):
            block = match.group(1)
            handle = re.search(r"products/([a-z0-9-]+)\.html", block)
            price = re.search(r'ShopStrip__price">\$(\d+(?:\.\d{1,2})?)', block)
            if not handle or not price or handle.group(1) not in ladders:
                continue
            if abs(money(price.group(1)) - ladders[handle.group(1)]["min"]) > 0.001:
                errors.append(
                    f"{rel}: {handle.group(1)} strip ${price.group(1)} is not ${ladders[handle.group(1)]['min']:.0f}"
                )
    floor = hyrx_design_minimum()
    label = f"{floor:.0f}" if abs(floor - round(floor)) < 0.001 else f"{floor:.2f}"
    index = open(os.path.join(BASE_DIR, "index.html"), encoding="utf-8").read()
    for phrase in (
        f"HYRX designs</strong> · from ${label}",
        f"HYRX designs · from ${label}",
    ):
        if index.count(phrase) != 1:
            errors.append(f"index.html: {phrase} appears {index.count(phrase)} times, expected once")
    if errors:
        raise SystemExit("Listed prices disagree with the live size ladder:\n" + "\n".join(errors[:80]))


def _offer_size(offer, sizes):
    """Match a JSON-LD offer to a sizePrices key, including towel sizes in the name."""
    sku_size = (offer.get("sku") or "").rsplit("-", 1)[-1]
    if sku_size in sizes:
        return sku_size
    name = offer.get("name") or ""
    for key in sizes:
        if key and key in name:
            return key
    return sku_size


def _page_variant_min(text):
    """Lowest size price on a product page, from sizePrices or the checkout map."""
    for marker in ("var sizePrices = ", "var prices = "):
        start = text.find(marker)
        if start < 0:
            continue
        brace = text.find("{", start)
        try:
            data, _ = json.JSONDecoder().raw_decode(text, brace)
        except json.JSONDecodeError:
            continue
        values = []

        def walk(node):
            if isinstance(node, dict):
                for value in node.values():
                    walk(value)
            elif isinstance(node, (int, float)) and not isinstance(node, bool):
                values.append(float(node))

        walk(data)
        if values:
            return min(values)
    return None


def hyrx_design_minimum():
    """Cheapest live variant on the HYRX collection."""
    coll = open(os.path.join(BASE_DIR, "collections", "hyrx.html"), encoding="utf-8").read()
    handles = list(dict.fromkeys(re.findall(r"products/([a-z0-9-]+)\.html", coll)))
    prices = []
    for handle in handles:
        path = os.path.join(BASE_DIR, "products", handle + ".html")
        if not os.path.exists(path):
            continue
        amount = _page_variant_min(open(path, encoding="utf-8").read())
        if amount is not None:
            prices.append(amount)
    if not prices:
        raise SystemExit("HYRX collection has no variant prices")
    return min(prices)


_FABRIC_LINE = re.compile(
    r"(?i)(?:\d+(?:\.\d+)?\s*oz|ring-spun|airlume|fleece|mesh|fabric|cotton|polyester|"
    r"heavyweight|lightweight|midweight|nylon|acrylic|leather)"
)
_HEAVY_CONFLICT = re.compile(
    r"(?i)(?<!\d)6(?:\.1)?\s+oz.{0,48}heavyweight|heavyweight.{0,48}(?<!\d)6(?:\.1)?\s+oz"
)


def _sentence_key(sentence):
    text = re.sub(r"\s+", " ", html.unescape(sentence)).strip().lower()
    return text.rstrip(".!?")


def _copy_sentences(fragment):
    plain = re.sub(r"<[^>]+>", " ", fragment)
    plain = re.sub(r"\s+", " ", html.unescape(plain)).strip()
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", plain) if part.strip()]


def _product_copy_html(page):
    """Description, spec list, and bullets. Not related products or the footer."""
    match = re.search(r"<main\b.*?</main>", page, flags=re.S | re.I)
    chunk = match.group(0) if match else page
    start = chunk.lower().find("<h1")
    if start == -1:
        return ""
    chunk = chunk[start:]
    for marker in ("Frequently Paired", "Related HYROX", 'class="ProductGrid"', "<footer"):
        at = chunk.find(marker)
        if at != -1:
            chunk = chunk[:at]
    return chunk


_MATERIAL_WORD = re.compile(
    r"(?i)\b(?:heavyweights?|lightweights?|midweights?|ring-spun|airlume|fleeces?|mesh|"
    r"fabrics?|cotton|polyester|nylon|acrylic|elastane|poplin|twill|garment-dyed|combed)\b"
    r"|\d+(?:\.\d+)?\s*oz"
)

# Handles that are not in the live Fourthwall catalog. Wording is the published blank.
_FABRIC_BY_HANDLE = {
    "apex-athletic-shoe-black-pink": "Lightweight mesh upper, cushioned sole.",
    "8-station-functional-race-division-oversized-stealth-hoodie": "80% cotton, 20% polyester; 100% cotton face; 9 oz; regular fit",
    "electrolyte-pacing-insulated-shaker-bottle": "Double-wall copper-lined vacuum-insulated stainless steel.",
}

# Fourthwall "More details" material line. No extras that the listing does not state.
# A 6.1 oz tee does not say heavyweight: that word next to 6.1 oz fails the build.
_EXACT_FABRIC = {
    '100-wall-balls-unbroken-sleeveless-muscle-tank': '100% airlume combed ring-spun cotton, lightweight fabric (4.2 oz), relaxed fit.',
    '1km-split': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    '200m-farmer-carry-survivors-club-barbell-crest-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    '26-27-world-series-lightweight-warmup-jacket': '100% polyester micro poplin',
    '8-runs-8-stations-zero-excuses-heavyweight-pump-cover-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'anaheim-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'anaheim-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'anaheim-race-day': '100% polyester, 2.21 oz, water-resistant',
    'anaheim-race-day-stitched': '100% polyester micro poplin',
    'anaheim-socal-open-division-pacific-coast-race-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'apex-8-station-race-day-tactical-duffle': '93% polyester, 7% nylon, UA Storm',
    'apex-aeroshell-lightweight-race-warmup-jacket': '100% polyester micro poplin',
    'atlanta-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'atlanta-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'atlanta-race-day-stitched': '100% polyester micro poplin',
    'burpee-broad-jumps-build-character-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'burpee-broad-jumps-build-character-warmup-hoodie': '80% cotton, 20% polyester; 100% cotton face; 9 oz; regular fit',
    'call-room': 'Heavyweight fabric (16.5 oz), 65% cotton, 35% recycled polyester, relaxed fit.',
    'cancun-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'cancun-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'cancun-race-day-stitched': '100% polyester micro poplin',
    'chicago-championship-division-navy-pier-hybrid-race-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'chicago-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'chicago-dallas-socal-world-series-prep-heavyweight-hoodie': '80% cotton, 20% polyester; 100% cotton face; 9 oz; regular fit',
    'chicago-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'chicago-race-day-stitched': '100% polyester micro poplin',
    'circuit-cities': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'compromised-running': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'compromised-running-club-breathable-race-tank': '100% airlume combed ring-spun cotton, lightweight fabric (4.2 oz), relaxed fit.',
    'compromised-running-club-fleece-hoodie': '80% cotton, 20% polyester; 100% cotton face; 9 oz; regular fit',
    'compromised-running-club-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'course-plate': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'dallas-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'dallas-lone-star-division-turf-threshold-hybrid-race-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'dallas-race-day': '100% polyester, 2.21 oz, water-resistant',
    'dallas-race-day-printable': '100% polyester, 2.21 oz, water-resistant',
    'dallas-race-day-stitched': '100% polyester micro poplin',
    'defend-my-sled-push-dept-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'defend-my-sled-push-fleece-hoodie': '80% cotton, 20% polyester; 100% cotton face; 9 oz; regular fit',
    'denver-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'denver-race-day': '100% polyester, 2.21 oz, water-resistant',
    'denver-race-day-stitched': '100% polyester micro poplin',
    'eight-marks': '100% carded cotton, heavyweight fabric (8.2 oz), relaxed fit.',
    'engine-biker-shorts-black': '78% polyester, 22% elastane, heavyweight fabric (8.55 oz).',
    'engine-biker-shorts-mint': '78% polyester, 22% elastane, heavyweight fabric (8.55 oz).',
    'engine-sports-bra-black': '78% polyester, 22% elastane, heavyweight fabric (8.55 oz).',
    'engine-sports-bra-mint': '78% polyester, 22% elastane, heavyweight fabric (8.55 oz).',
    'engine-training-tank-black': '93% polyester, 7% elastane, 7.08 oz',
    'engine-training-tank-mint': '93% polyester, 7% elastane, 7.08 oz',
    'field-issue': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'guadalajara-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'guadalajara-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'guadalajara-race-day-stitched': '100% polyester micro poplin',
    'hold-the-pace': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'hong-kong-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'hong-kong-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'hong-kong-race-day-stitched': '100% polyester micro poplin',
    'houston-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'houston-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'houston-race-day-stitched': '100% polyester micro poplin',
    'hybrid-8-station-windbreaker-track-jacket': '100% polyester micro poplin',
    'hyrx-cuff-beanie-black': '100% Turbo acrylic',
    'hyrx-cuff-beanie-heather-grey': '100% Turbo acrylic',
    'hyrx-dad-cap': '100% chino cotton twill',
    'hyrx-finish': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'hyrx-gym-sack-black': '100% polyester, 6.64 oz/yd² (225 g/m²)',
    'hyrx-gym-sack-burgundy': '100% polyester, 6.64 oz/yd² (225 g/m²)',
    'hyrx-low-cap': '100% cotton twill',
    'hyrx-mid-cap': '65% polyester, 35% cotton',
    'hyrx-pool-slide-black': 'Cushioned faux leather upper strap, lightweight polyurethane (PU) outsole.',
    'hyrx-pool-slide-burgundy': 'Cushioned faux leather upper strap, lightweight polyurethane (PU) outsole.',
    'hyrx-quarter-zip': '3-end fleece, 80% cotton, 20% recycled polyester, 8.25 oz, mock neck',
    'hyrx-rib-beanie-black': '50% recycled polyester and 50% acrylic',
    'hyrx-rib-beanie-light-blue': '50% recycled polyester and 50% acrylic',
    'hyrx-run-5-panel-black': '100% polyester',
    'hyrx-run-5-panel-light-blue-white': '100% polyester',
    'hyrx-station-crew': '80% cotton and 20% polyester, heavyweight fabric (9 oz), regular fit.',
    'hyrx-station-towel-black': '52% cotton, 48% polyester, 11.8 oz/yd² (400 g/m²)',
    'hyrx-station-towel-deep-olive': '52% cotton, 48% polyester, 11.8 oz/yd² (400 g/m²)',
    'hyrx-surf-5-panel': '100% recycled nylon, lightweight quick-dry fabric.',
    'hyrx-trucker': '47% cotton, 28% nylon, 25% polyester, or 65% polyester, 35% cotton',
    'hyrx-trucker-graphic': '60% cotton, 40% polyester',
    'las-vegas-championship-qualifier-sin-city-turf-club-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'las-vegas-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'las-vegas-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'las-vegas-race-day-stitched': '100% polyester micro poplin',
    'london-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'london-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'london-race-day-stitched': '100% polyester micro poplin',
    'miami-beach-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'miami-beach-heat-block-south-florida-endurance-race-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'miami-beach-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'miami-beach-race-day-stitched': '100% polyester micro poplin',
    'minneapolis-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'minneapolis-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'minneapolis-race-day-stitched': '100% polyester micro poplin',
    'monterrey-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'monterrey-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'monterrey-race-day-stitched': '100% polyester micro poplin',
    'nashville-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'nashville-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'nashville-race-day': '100% polyester, 2.21 oz, water-resistant',
    'nashville-race-day-stitched': '100% polyester micro poplin',
    'new-york-hudson-pier-metro-endurance-dept-race-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'outline-mark': '100% Airlume combed and ring-spun cotton, 6 oz, relaxed oversized fit with dropped shoulders.',
    'paris-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'paris-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'paris-race-day-stitched': '100% polyester micro poplin',
    'peak-sign': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'phoenix-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'phoenix-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'phoenix-race-day-stitched': '100% polyester micro poplin',
    'porta-potty-line-pr-pre-race-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'portland-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'portland-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'portland-race-day-stitched': '100% polyester micro poplin',
    'pro-division-lightweight-quarter-zip-race-shell': '100% polyester micro poplin',
    'push-heavy': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'roxzone-penalties-ruined-my-pr-athletic-race-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'roxzone-speed-dept': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'run-station-repeat-heavy-blend-hoodie': '80% cotton, 20% polyester; 100% cotton face; 9 oz; regular fit',
    'run-station-repeat-performance-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'run-station-repeat-sleeveless-race-day-muscle-tank': '100% airlume combed ring-spun cotton, lightweight fabric (4.2 oz), relaxed fit.',
    'san-diego-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'san-diego-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'san-diego-race-day-stitched': '100% polyester micro poplin',
    'sandbag-lunges-are-a-personal-attack-oversized-pump-cover': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'sled-push-dept-raw-armhole-conditioning-muscle-tank': '100% airlume combed ring-spun cotton, lightweight fabric (4.2 oz), relaxed fit.',
    'sled-push-enthusiast-race-day-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'sleeve-seal': 'Heavyweight fabric (16.5 oz), 65% cotton, 35% recycled polyester, relaxed fit.',
    'stem-type': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'sub-65-club-pace-pull-push-elite-division-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'the-erg-doesnt-care-how-you-feel-heavyweight-fleece-hoodie': '80% cotton, 20% polyester; 100% cotton face; 9 oz; regular fit',
    'the-erg-doesnt-care-how-you-feel-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'timing-gate': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'vancouver-crest': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'vancouver-hyrx': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'vancouver-race-day': '100% polyester, 2.21 oz, water-resistant',
    'vancouver-race-day-stitched': '100% polyester micro poplin',
    'wall-balls-bad-decisions-hoodie': '80% cotton, 20% polyester; 100% cotton face; 9 oz; regular fit',
    'wall-balls-bad-decisions-oversized-pump-cover': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'work-the-loop': 'Heavyweight fabric (16.5 oz), 65% cotton, 35% recycled polyester, relaxed fit.',
    'zone-2-all-week-redline-all-weekend-performance-tee': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
    'zone-2-engine-builder-embroidered-dad-hat': '100% chino cotton twill',
    'zone-5-engine': '100% ring-spun cotton, 6.1 oz, relaxed fit.',
}


def fabric_bullet_for(prod, page_text=""):
    """The single Fabric bullet, copied from the Fourthwall More details line."""
    handle = (prod or {}).get("handle") or ""
    if handle in _EXACT_FABRIC:
        return _EXACT_FABRIC[handle]
    if handle in _FABRIC_BY_HANDLE:
        return _FABRIC_BY_HANDLE[handle]
    blank = (prod or {}).get("fourthwall_blank") or ""
    low = blank.lower()
    if "6.1" in blank:
        return "100% ring-spun cotton, 6.1 oz, relaxed fit."
    if "7.08" in blank:
        return "93% polyester, 7% elastane, 7.08 oz"
    if "barnard" in low or "4.2" in blank:
        return "100% airlume combed ring-spun cotton, lightweight fabric (4.2 oz), relaxed fit."
    if "airlume" in low or re.search(r"\b6\s*oz\b", low):
        return "100% Airlume combed and ring-spun cotton, 6 oz, relaxed oversized fit with dropped shoulders."
    if "8.2" in blank:
        return "100% carded cotton, heavyweight fabric (8.2 oz), relaxed fit."
    if "16.5" in blank:
        return "Heavyweight fabric (16.5 oz), 65% cotton, 35% recycled polyester, relaxed fit."
    if "8.55" in blank:
        return "78% polyester, 22% elastane, heavyweight fabric (8.55 oz)."
    if "8.25" in blank or "3-end fleece" in low:
        return "3-end fleece, 80% cotton, 20% recycled polyester, 8.25 oz, mock neck"
    if "2.21" in blank:
        return "100% polyester, 2.21 oz, water-resistant"
    if "micro poplin" in low or "co200" in low:
        return "100% polyester micro poplin"
    cleaned = re.sub(r"(?i)\s*\(?fulfilled via fourthwall[^)]*\)?", "", blank)
    cleaned = re.sub(r"(?i),?\s*fulfilled via fourthwall.*$", "", cleaned).strip(" .")
    return cleaned or "See the product description."


def _split_sentences(text):
    text = html.unescape(text or "")
    text = re.sub(r"(?<!\.)\.\.(?!\.)", ".", text)
    text = re.sub(r"\b(Co|U\.S|Dr|Mr|Mrs|St|No|vs|yd)\.", lambda m: m.group(0)[:-1] + "\x00", text)
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]
    return [part.replace("\x00", ".") for part in parts]


def _percent_without_material(text):
    """True when a percentage is not followed by a material word.

    A discount such as "15% Off" is not a stripped fabric fragment. "100%," and
    "80% and" are: the material word is missing before the comma or the conjunction.
    """
    for match in re.finditer(r"\d+(?:\.\d+)?\s*%", text):
        rest = text[match.end():]
        window = re.split(r"[.;]", rest, maxsplit=1)[0]
        if re.match(r"\s*off\b", window, re.I):
            continue
        material = _FABRIC_TERM.search(window)
        before = window[: material.start()] if material else window
        if "," in before or re.match(r"\s*(?:and|or)\b", before, re.I):
            return True
        if material:
            continue
        if not re.search(r"[A-Za-z]", window):
            return True
    return False


def garble_hits(text):
    """Broken-fragment markers. An ellipsis of three dots is allowed."""
    if not text:
        return []
    hits = []
    if ",," in text:
        hits.append(",,")
    if re.search(r"(?<!\.)\.\.(?!\.)", text):
        hits.append("..")
    if _percent_without_material(text):
        hits.append("percent")
    if re.search(r"\b(?:and|or)\s*,", text, re.I):
        hits.append("dangling")
    if text.count("(") != text.count(")"):
        hits.append("parens")
    if re.search(r"\b\w+-\s", text):
        hits.append("hyphen")
    if re.search(r"\(\s*\)", text):
        hits.append("empty-paren")
    return hits


def _story_sentence_ok(sentence):
    """A description sentence that lost its material words is dropped whole."""
    sentence = sentence.strip()
    if not sentence:
        return False
    if _MATERIAL_WORD.search(sentence) or re.search(r"\d+(?:\.\d+)?\s*%", sentence):
        return False
    if garble_hits(sentence):
        return False
    if re.search(r"(?i)\b(?:relaxed fit|regular fit|blank as|fourthwall lists)\b", sentence):
        return False
    if len(re.sub(r"[^A-Za-z0-9]+", "", sentence)) < 12:
        return False
    return True


def scrub_fabric_text(text):
    """Drop a whole sentence that is fabric, weight, or a broken fragment."""
    kept = []
    for sentence in _split_sentences(text):
        if not _story_sentence_ok(sentence):
            continue
        if sentence[-1] not in ".!?":
            sentence += "."
        kept.append(sentence)
    return re.sub(r"\s{2,}", " ", " ".join(kept)).strip()


def ensure_story(text, minimum=80):
    """A product description has to be a real sentence, not only the fabric line."""
    text = re.sub(r"\s{2,}", " ", (text or "")).strip()
    text = re.sub(r"(?i)\s*It is part of the Apex Hybrid Co\. catalog\.?", "", text).strip()
    pad = "Made to order for Apex Hybrid Co. athletes."
    if len(text) < minimum and pad.lower() not in text.lower():
        text = (text + " " + pad).strip() if text else pad
    return text


# A Fabric bullet has to name a real material or weight, not just the word Fabric.
_FABRIC_TERM = re.compile(
    r"(?i)\b(?:cotton|polyester|poly|nylon|spandex|elastane|fleece|acrylic|rayon|"
    r"microfiber|terry|canvas|eva|rubber|oz|gsm|blend|mesh|poplin|oxford|twill|"
    r"stainless|polyurethane|leather|fabric)\b"
)
# Fourthwall names both towel blanks "White". The photo colorway is the label.
# Variant ids stay the add-to-cart payload; only the displayed name changes.
TOWEL_VARIANT_LABEL = {
    "3669ffea-c900-49da-be70-1a1a1a150aa8": "Black",
    "5ec97ff9-92f9-4e83-adca-8e3e130d2137": "Black",
    "b076de69-8d86-4141-aa16-b2a53655a67b": "Deep Olive",
    "488ab94b-5511-463e-8aeb-6d54606f06ac": "Deep Olive",
}


def towel_display_color(variant_id, fallback):
    """Site label for a towel variant. Does not change the variant id."""
    return TOWEL_VARIANT_LABEL.get(variant_id, fallback)


def _outside_fabric_text(page):
    """Page text that is not the Fabric bullet, a heading, a listing name, or a URL."""
    text = re.sub(r"<li\b[^>]*>\s*Fabric:.*?</li>", " ", page, count=1, flags=re.S | re.I)
    text = re.sub(r"<title\b[^>]*>.*?</title>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<h[1-6]\b[^>]*>.*?</h[1-6]>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<nav\b[^>]*>.*?</nav>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<a\b[^>]*>.*?</a>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<script\b(?![^>]*ld\+json)[^>]*>.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r'"(?:name|url|image|@id)"\s*:\s*"(?:\\.|[^"\\])*"', " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r'\s(?:href|src)="[^"]*"', " ", text)
    return text


def _marked_sentences(chunk, break_divs):
    """Turn block endings into sentence breaks, then split on punctuation."""
    chunk = re.sub(r"<br\s*/?>", ". ", chunk, flags=re.I)
    chunk = re.sub(r"</(?:h[1-6]|li|p|summary)\s*>", ". ", chunk, flags=re.I)
    if break_divs:
        chunk = re.sub(r"</div\s*>", ". ", chunk, flags=re.I)
    plain = re.sub(r"<[^>]+>", " ", chunk)
    plain = re.sub(r"\s+", " ", html.unescape(plain))
    return [part.strip(" .") for part in re.split(r"(?<=[.!?])\s+|\s+\.\s+", plain) if part.strip(" .")]


def _body_sentences(page):
    """Sentences from the whole body. Product-column blocks break sentences before related cards."""
    match = re.search(r"<body\b[^>]*>(.*)</body>", page, flags=re.S | re.I)
    body = match.group(1) if match else page
    body = re.sub(r"<header\b[^>]*>.*?</header>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<nav\b[^>]*>.*?</nav>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<footer\b[^>]*>.*?</footer>", " ", body, flags=re.S | re.I)
    cut = len(body)
    for marker in ("Frequently Paired", "Related HYROX", 'class="ProductGrid"', "ProductCard__Category"):
        at = body.find(marker)
        if at != -1:
            cut = min(cut, at)
    return _marked_sentences(body[:cut], True) + _marked_sentences(body[cut:], False)


def fabric_rule_errors(page, name="page"):
    """Return fabric-rule failures for one product page. Empty means the page passes."""
    errors = []
    if re.search(r'http-equiv="refresh"', page, re.I) or "<h1" not in page.lower():
        return errors
    bullets = re.findall(r"<li\b[^>]*>\s*(Fabric:.*?)</li>", page, flags=re.S | re.I)
    real = [item for item in bullets if _FABRIC_TERM.search(item)]
    if len(bullets) != 1 or len(real) != 1:
        errors.append(f"{name}: {len(real)} Fabric bullets with a material term ({len(bullets)} labeled)")
    outside = re.sub(r"<[^>]+>", " ", _outside_fabric_text(page))
    if _MATERIAL_WORD.search(outside):
        errors.append(f"{name}: fabric or weight text outside the Fabric bullet")
    og = re.search(r'<meta property="og:description" content="([^"]*)"', page)
    if not og:
        errors.append(f"{name}: missing og:description")
    elif len(html.unescape(og.group(1)).strip()) < 40:
        errors.append(f"{name}: og:description is under 40 characters")
    seen = {}
    for sentence in _body_sentences(page):
        key = _sentence_key(sentence)
        if len(key) < 20:
            continue
        if key in seen:
            errors.append(f"{name}: repeated sentence {sentence[:90]!r}")
            break
        seen[key] = True
    copy = _product_copy_html(page)
    story = []
    for bit in re.findall(r"<p\b[^>]*>.*?</p>", copy, flags=re.S | re.I):
        if re.search(r"\bid=[\"']usShipNote", bit):
            continue
        if re.search(r"<a\b", bit, re.I):
            continue
        if not re.search(r"font-size:\s*1[45]", bit):
            continue
        story.append(" ".join(_copy_sentences(bit)))
    blurb = re.sub(r"\s+", " ", " ".join(story)).strip()
    fabric_only = bool(real) and _sentence_key(blurb) == _sentence_key(
        re.sub(r"(?i)^fabric:\s*", "", real[0])
    )
    if len(blurb) < 80 or fabric_only:
        errors.append(f"{name}: description is {len(blurb)} characters")
    if _HEAVY_CONFLICT.search(re.sub(r"https?://\S+", " ", re.sub(r'\s(?:href|src)="[^"]*"', " ", page))):
        errors.append(f"{name}: calls a 6 or 6.1 oz tee heavyweight")
    return errors


def assert_fabric_stated_once():
    """One Fabric bullet. No fabric outside it. No repeated sentence. No stub description."""
    sample_path = os.path.join(BASE_DIR, "products", "compromised-running.html")
    sample = open(sample_path, encoding="utf-8").read()
    removed = re.sub(r"<li\b[^>]*>\s*Fabric:.*?</li>", "", sample, count=1, flags=re.S | re.I)
    self_test = fabric_rule_errors(removed, "c36-fixture")
    if not any("Fabric bullet" in item for item in self_test):
        raise SystemExit("Fabric self-test failed: removing the C36 Fabric bullet did not fail the build")
    errors = []
    products = os.path.join(BASE_DIR, "products")
    for name in sorted(os.listdir(products)):
        if not name.endswith(".html"):
            continue
        page = open(os.path.join(products, name), encoding="utf-8", errors="replace").read()
        errors.extend(fabric_rule_errors(page, name))
    if errors:
        raise SystemExit("Fabric line is repeated:\n" + "\n".join(errors[:60]))


def _page_copy_fields(page):
    """Visible body text plus the description fields the garble gate reads."""
    fields = []
    meta = re.search(r'<meta name="description" content="([^"]*)"', page)
    fields.append(("meta description", html.unescape(meta.group(1)) if meta else ""))
    og = re.search(r'<meta property="og:description" content="([^"]*)"', page)
    fields.append(("og:description", html.unescape(og.group(1)) if og else ""))
    for match in re.finditer(
        r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', page, flags=re.S | re.I
    ):
        for desc in re.finditer(r'"description"\s*:\s*"((?:\\.|[^"\\])*)"', match.group(1)):
            fields.append(("JSON-LD description", json.loads('"' + desc.group(1) + '"')))
    body = re.search(r"<body\b[^>]*>(.*)</body>", page, flags=re.S | re.I)
    chunk = body.group(1) if body else page
    chunk = re.sub(r"<header\b[^>]*>.*?</header>", " ", chunk, flags=re.S | re.I)
    chunk = re.sub(r"<nav\b[^>]*>.*?</nav>", " ", chunk, flags=re.S | re.I)
    chunk = re.sub(r"<footer\b[^>]*>.*?</footer>", " ", chunk, flags=re.S | re.I)
    chunk = re.sub(
        r"<section\b[^>]*>\s*<h2\b[^>]*>\s*Related HYROX.*?</section>",
        " ",
        chunk,
        flags=re.S | re.I,
    )
    chunk = re.sub(r"<script\b[^>]*>.*?</script>", " ", chunk, flags=re.S | re.I)
    chunk = re.sub(r"<style\b[^>]*>.*?</style>", " ", chunk, flags=re.S | re.I)
    chunk = re.sub(r"<[^>]+>", " ", chunk)
    fields.append(("visible text", re.sub(r"\s+", " ", html.unescape(chunk))))
    return fields


def garble_errors(page, name="page"):
    """Broken fragments in the description fields and the visible page text."""
    if re.search(r'http-equiv="refresh"', page, re.I) or "<h1" not in page.lower():
        return []
    errors = []
    for label, text in _page_copy_fields(page):
        hits = garble_hits(text)
        if hits:
            errors.append(f"{name}: {label} has {' '.join(hits)}")
    return errors


def assert_no_garbled_copy():
    """Fail when a description kept a fragment after the fabric words were removed."""
    samples = {
        ",,": "100%,, relaxed fit.",
        "..": "Roxzone Speed Dept..",
        "percent": "80% and 20%.",
        "dangling": "left and, right.",
        "parens": "unbalanced (paren.",
        "hyphen": "water-resistant micro- shell",
        "empty-paren": "empty () parens.",
    }
    for kind, text in samples.items():
        if kind not in garble_hits(text):
            raise SystemExit(f"Garble self-test failed: {kind!r} was not caught in {text!r}")
    if garble_hits("Wait...") or garble_hits("100% ring-spun cotton, 6.1 oz, relaxed fit.") or garble_hits("Shop Doubles 2-Packs (15% off your entire order with code TEAM15)"):
        raise SystemExit("Garble self-test flagged a clean sentence, an ellipsis, or a discount")
    fixture = (
        "<!DOCTYPE html><html><head>"
        '<meta name="description" content="100%,, relaxed fit.">'
        '<meta property="og:description" content="100%,, relaxed fit.">'
        '<script type="application/ld+json">{"@type":"Product","description":"100%,, relaxed fit."}</script>'
        "</head><body><h1>Fixture</h1><p>100%,, relaxed fit.</p></body></html>"
    )
    if not garble_errors(fixture, "garble-fixture"):
        raise SystemExit("Garble self-test failed: the fixture page did not fail the build")
    errors = []
    products = os.path.join(BASE_DIR, "products")
    for name in sorted(os.listdir(products)):
        if not name.endswith(".html"):
            continue
        page = open(os.path.join(products, name), encoding="utf-8", errors="replace").read()
        errors.extend(garble_errors(page, name))
    if errors:
        raise SystemExit("Garbled copy:\n" + "\n".join(errors[:60]))


_DOUBLED_PHRASE = re.compile(
    r"\b((?:[A-Za-z0-9][A-Za-z0-9'.&]*\s+){2,}[A-Za-z0-9][A-Za-z0-9'.&]*)\s+\1\b"
)
_SITEWIDE_META_KEYS = {
    "description",
    "og:title",
    "og:description",
    "twitter:title",
    "twitter:description",
}


def sitewide_garble_hits(text):
    """Broken copy in one text node, title, meta, or JSON-LD block."""
    if not text:
        return []
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    hits = []
    if re.search(r"\(\s*\)", text):
        hits.append("()")
    if _DOUBLED_PHRASE.search(text):
        hits.append("doubled")
    if " , " in text:
        hits.append(" , ")
    if "code ." in text:
        hits.append("code .")
    if re.search(r"\bUS Free\b", text):
        hits.append("US Free")
    # "gym in and Costa Mesa" is a missing city. "jog in and the photo" is a real sentence.
    if re.search(r"\b(?:gym|located|based|studio)\s+in\s+and\b", text, re.I):
        hits.append("in and")
    return hits


def _sitewide_copy_fields(page):
    """Title, social meta, JSON-LD, and each visible text node. Scripts stay out."""
    fields = []
    title = re.search(r"<title>(.*?)</title>", page, flags=re.S | re.I)
    if title:
        fields.append(("title", html.unescape(re.sub(r"<[^>]+>", "", title.group(1)))))
    for tag in re.finditer(r"<meta\b[^>]*>", page, flags=re.I):
        raw = tag.group(0)
        name = re.search(r'(?:name|property)="([^"]+)"', raw, flags=re.I)
        content = re.search(r'content="([^"]*)"', raw, flags=re.I)
        if not name or not content:
            continue
        key = name.group(1).lower()
        if key in _SITEWIDE_META_KEYS:
            fields.append((key, html.unescape(content.group(1))))
    for match in re.finditer(
        r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', page, flags=re.S | re.I
    ):
        fields.append(("JSON-LD", html.unescape(match.group(1))))
    body = re.search(r"<body\b[^>]*>(.*)</body>", page, flags=re.S | re.I)
    chunk = body.group(1) if body else page
    chunk = re.sub(r"<header\b[^>]*>.*?</header>", " ", chunk, flags=re.S | re.I)
    chunk = re.sub(r"<nav\b[^>]*>.*?</nav>", " ", chunk, flags=re.S | re.I)
    chunk = re.sub(r"<footer\b[^>]*>.*?</footer>", " ", chunk, flags=re.S | re.I)
    chunk = re.sub(r"<script\b[^>]*>.*?</script>", " ", chunk, flags=re.S | re.I)
    chunk = re.sub(r"<style\b[^>]*>.*?</style>", " ", chunk, flags=re.S | re.I)
    for node in re.findall(r">([^<]+)<", chunk):
        if node.strip():
            fields.append(("visible text", html.unescape(node)))
    return fields


def _catalog_title_map():
    """Listing title for each product handle. Card text has to match this."""
    titles = {}
    for prod in products:
        handle = prod.get("handle")
        title = (prod.get("title") or "").strip()
        if handle and title:
            titles[handle] = title
            seo = (prod.get("seo_title") or "").strip()
            if seo:
                titles.setdefault(handle + "\0seo", seo)
    return titles


def _handle_from_href(href):
    match = re.search(r"(?:^|/)([a-z0-9][a-z0-9-]*)\.html$", href or "")
    return match.group(1) if match else None


def _plain_text(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment or ""))).strip()


def card_title_mismatches(page):
    """Product card, shop-strip, spot, and featured-row titles that are not the catalog title."""
    titles = _catalog_title_map()
    mismatches = []

    def check(label, handle, shown):
        expected = titles.get(handle)
        if not expected:
            return
        shown = _plain_text(shown)
        seo = titles.get(handle + "\0seo", expected)
        if shown and shown not in {expected, seo}:
            mismatches.append((label, shown, expected))

    def handles_in(block):
        found = []
        for href in re.findall(r'href="([^"]+)"', block):
            handle = _handle_from_href(href)
            if handle in titles:
                found.append(handle)
        return found

    def title_handle(block):
        titled = re.search(
            r'class="[^"]*ProductCard__Title[^"]*"[^>]*>\s*<a\b[^>]*href="([^"]+)"',
            block,
            flags=re.S | re.I,
        )
        if titled:
            handle = _handle_from_href(titled.group(1))
            if handle in titles:
                return handle
        found = handles_in(block)
        return found[0] if found else None

    for pattern in (
        r'<a\b[^>]*class="[^"]*\bProductCard\b[^"]*"[^>]*>.*?</a>',
        r'<article\b[^>]*class="[^"]*\bProductCard\b[^"]*"[^>]*>.*?</article>',
    ):
        for block in re.finditer(pattern, page, flags=re.S | re.I):
            chunk = block.group(0)
            handle = title_handle(chunk)
            title = re.search(
                r'class="[^"]*ProductCard__Title[^"]*"[^>]*>(.*?)</(?:div|h2|h3)>',
                chunk,
                flags=re.S | re.I,
            )
            if handle and title:
                check("ProductCard__Title", handle, title.group(1))
    for block in re.finditer(
        r'<article\b[^>]*class="[^"]*ShopStrip__card[^"]*"[^>]*>.*?</article>', page, flags=re.S | re.I
    ):
        heading = re.search(r"<h3>\s*<a\b[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", block.group(0), flags=re.S | re.I)
        if heading:
            check("ShopStrip", _handle_from_href(heading.group(1)), heading.group(2))
    for block in re.finditer(
        r'<a\b[^>]*class="[^"]*SpotCard[^"]*"[^>]*>.*?</a>', page, flags=re.S | re.I
    ):
        chunk = block.group(0)
        href = re.search(r'href="([^"]+)"', chunk)
        strong = re.search(r"<strong>(.*?)</strong>", chunk, flags=re.S | re.I)
        if href and strong:
            check("SpotCard", _handle_from_href(href.group(1)), strong.group(1))
    for link in re.finditer(
        r'<a\b[^>]*href="([^"]+)"[^>]*style="color:#fff;font-weight:\s*800[^"]*"[^>]*>(.*?)</a>',
        page,
        flags=re.S | re.I,
    ):
        shown = _plain_text(link.group(2))
        if shown.lower().startswith("buy") or shown.startswith("+"):
            continue
        check("featured", _handle_from_href(link.group(1)), shown)
    return mismatches


def sitewide_garble_errors(page, name="page"):
    """Every HTML file: broken phrases plus a card title that is not the catalog title."""
    errors = []
    for label, text in _sitewide_copy_fields(page):
        hits = sitewide_garble_hits(text)
        if hits:
            errors.append(f"{name}: {label} has {', '.join(hits)}")
    for label, shown, expected in card_title_mismatches(page):
        errors.append(f"{name}: {label} {shown!r} != catalog {expected!r}")
    return errors


def assert_sitewide_garble():
    """Fail the build on sitewide garble, including articles, directory, and index pages."""
    dirty = {
        "()": "<html><head><title>Relay Team Kits ()</title></head><body><h1>Guide</h1><p>Clean sentence here.</p></body></html>",
        "doubled": "<html><head><title>Guide</title></head><body><h1>Guide</h1><p>Anaheim Dec 2026 Anaheim Dec 2026 race week.</p></body></html>",
        " , ": "<html><head><title>Wear</title></head><body><h1>Wear</h1><p>wear a , top like this one today.</p></body></html>",
        "code .": "<html><head><title>Dallas</title></head><body><h1>Dallas</h1><p>Save with code . today please.</p></body></html>",
        "US Free": "<html><head><title>Ship</title></head><body><h1>Ship</h1><p>They ship from the US Free US shipping.</p></body></html>",
        "in and": "<html><head><title>Gym</title></head><body><h1>Gym</h1><p>A gym in and Costa Mesa today.</p></body></html>",
        "card": (
            "<html><head><title>Card</title></head><body><h1>Card</h1>"
            '<a class="ProductCard" href="zone-5-engine.html"><div class="ProductCard__Title">Zone 5 Engine</div></a>'
            "</body></html>"
        ),
    }
    for kind, page in dirty.items():
        if not sitewide_garble_errors(page, "fixture"):
            raise SystemExit(f"Sitewide garble self-test failed: {kind!r} was not caught")
    clean = (
        "<html><head><title>Aerobic Engine</title>"
        '<meta name="description" content="Made to order. Ships from the US. Free US shipping.">'
        '<meta property="og:title" content="Aerobic Engine">'
        '<meta name="twitter:title" content="Aerobic Engine">'
        "</head><body><h1>Aerobic Engine</h1>"
        "<p>A gym in Irvine and Costa Mesa. Austin and Round Rock. A simple city tee for the jog in and the photo after. They ship from the US. Free US shipping.</p>"
        '<a class="ProductCard" href="zone-5-engine.html"><img alt="Aerobic Engine" />'
        '<div class="ProductCard__Title">Aerobic Engine</div></a>'
        "</body></html>"
    )
    clean_errors = sitewide_garble_errors(clean, "clean-fixture")
    if clean_errors:
        raise SystemExit("Sitewide garble self-test flagged a clean page:\n" + "\n".join(clean_errors))
    if sitewide_garble_hits("Austin and Round Rock check-in and warmup"):
        raise SystemExit("Sitewide garble self-test flagged Austin and or check-in and")
    if sitewide_garble_hits("A simple city tee for the jog in and the photo after."):
        raise SystemExit("Sitewide garble self-test flagged jog in and the photo after")
    errors = []
    for dirpath, dirnames, filenames in os.walk(BASE_DIR):
        dirnames[:] = [name for name in dirnames if name not in {".git", "__pycache__"}]
        for name in sorted(filenames):
            if not name.endswith(".html"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, BASE_DIR)
            page = open(path, encoding="utf-8", errors="replace").read()
            errors.extend(sitewide_garble_errors(page, rel))
    if errors:
        raise SystemExit("Sitewide garbled copy:\n" + "\n".join(errors[:80]))


def apply_copy_repairs(text):
    """Repair the known garble strings so a later scrub cannot publish them again."""
    if not text:
        return text
    replacements = (
        ("Anaheim Dec 2026 Anaheim Dec 2026", "Anaheim Dec 2026"),
        ("Relay Team Kits ()", "Relay Team Kits"),
        ("Top 4 Heavyweight Hybrid Pump Covers ()", "Top 4 Hybrid Pump Covers"),
        ("Yes! Apex Hybrid Co. is Made to order.", "Yes. Every Apex Hybrid Co. piece is made to order and ships from the US with free US shipping."),
        ("Apex Hybrid Co. is Made to order.", "Yes. Every Apex Hybrid Co. piece is made to order and ships from the US with free US shipping."),
        ("with code .", "with code DALLAS10."),
        ("in  and Costa Mesa", "in Irvine and Costa Mesa"),
        ("in  and costa mesa", "in Irvine and costa mesa"),
        (" ( &amp; Costa Mesa)", " (Irvine &amp; Costa Mesa)"),
        (" ( & Costa Mesa)", " (Irvine & Costa Mesa)"),
        (" ( &amp; costa mesa)", " (Irvine &amp; costa mesa)"),
        ("APC-C42..APC-C45", "APC-C42 to APC-C45"),
        ("APC-C36..APC-C41", "APC-C36 to APC-C41"),
        ("Sled Push Dept. Conditioning Muscle Tank", "conditioning muscle tank"),
        ("15% off your entire order with code TEAM15", "15% off your entire order with code TEAM15"),
        ("100 Wall Balls Unbroken* Heavyweight Tee (APC-C03)", "Apex Hybrid - Sled Push Enthusiast (APC-C03)"),
        ("jog in and the photo", "jog in, and the photo"),
        ("distance in and out", "distance into and out"),
        ("check-in and warmup", "check-in, and warmup"),
        ("check-in and corral", "check-in, and the corral"),
        ("walk-in and the", "walk-in, and the"),
        ("run-in and run-out", "run-in, and the run-out"),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    text = re.sub(r"(?<!Irvine)(?<!Irvine )[ \t]*/[ \t]*Costa Mesa", " Irvine / Costa Mesa", text)
    text = re.sub(r"(?<!Irvine)(?<!Irvine )[ \t]*/[ \t]*costa mesa", " Irvine / costa mesa", text)
    text = text.replace("Irvine  Irvine / Costa Mesa", "Irvine / Costa Mesa")
    text = text.replace("Irvine  Irvine / costa mesa", "Irvine / costa mesa")
    text = text.replace("in  Irvine / Costa Mesa", "in Irvine / Costa Mesa")
    text = text.replace("in  Irvine / costa mesa", "in Irvine / costa mesa")
    text = text.replace('" Irvine / Costa Mesa', '"Irvine / Costa Mesa')
    text = text.replace("( Irvine / Costa Mesa", "(Irvine / Costa Mesa")
    text = text.replace("📍  Irvine / Costa Mesa", "📍 Irvine / Costa Mesa")
    text = text.replace(")  Irvine / costa mesa", ") Irvine / costa mesa")
    text = re.sub(r"\bUS\s+Free US shipping\b", "US. Free US shipping", text)
    text = re.sub(
        r"wear a\s*,\s*top like the\s+Built For Heavy Legs Breathable Tech Shirt \(APC-C36, \$38\) or the Run\. Station\. Repeat\. Sleeveless Muscle Tank \(APC-C28, \$32\), paired with a heavyweight pump cover or AeroShell Warmup Jacket \(APC-C42, \$68\)",
        "wear a race top like the Built For Heavy Legs shirt (APC-C36, $38) or the Run. Station. Repeat. sleeveless tank (APC-C28, $32), with a pump cover or the AeroShell warmup jacket (APC-C42, $68)",
        text,
    )
    text = re.sub(r"\s*<li>Water-resistant 900D high-density Oxford[^<]*</li>", "", text)
    text = re.sub(r'\n\s*"Water-resistant 900D high-density Oxford[^"]*",', "", text)
    return text


def sync_card_titles(page):
    """Write each product card's visible title and alt from catalog.json."""
    titles = _catalog_title_map()

    def retitle(block, handle):
        title = titles.get(handle)
        if not title:
            return block
        esc = html.escape(title)

        def set_title(match):
            inner = match.group(2)
            shown = _plain_text(inner)
            seo = titles.get(handle + "\0seo", title)
            if shown in {title, seo}:
                return match.group(0)
            if re.search(r"<a\b", inner, flags=re.I):
                inner = re.sub(
                    r"(<a\b[^>]*>)(.*?)(</a>)",
                    lambda anchor: anchor.group(1) + esc + anchor.group(3),
                    inner,
                    count=1,
                    flags=re.S | re.I,
                )
            else:
                inner = esc
            return match.group(1) + inner + match.group(3)

        block = re.sub(
            r'(<(?:div|h2|h3)\b[^>]*class="[^"]*ProductCard__Title[^"]*"[^>]*>)(.*?)(</(?:div|h2|h3)>)',
            set_title,
            block,
            count=1,
            flags=re.S | re.I,
        )
        block = re.sub(
            r"(<h3>\s*<a\b[^>]*>)(.*?)(</a>\s*</h3>)",
            lambda match: match.group(0)
            if _plain_text(match.group(2)) in {title, titles.get(handle + "\0seo", title)}
            else match.group(1) + esc + match.group(3),
            block,
            count=1,
            flags=re.S | re.I,
        )
        block = re.sub(
            r"(<strong>)(.*?)(</strong>)",
            lambda match: match.group(0)
            if _plain_text(match.group(2)) in {title, titles.get(handle + "\0seo", title)}
            else match.group(1) + esc + match.group(3),
            block,
            count=1,
            flags=re.S | re.I,
        )

        def set_alt(match):
            if html.unescape(match.group(2)) == title:
                return match.group(0)
            return match.group(1) + html.escape(title, quote=True) + match.group(3)

        block = re.sub(r'(<img\b[^>]*\salt=")([^"]*)(")', set_alt, block, count=1)
        return block

    def card_sub(match):
        block = match.group(0)
        titled = re.search(
            r'class="[^"]*ProductCard__Title[^"]*"[^>]*>\s*<a\b[^>]*href="([^"]+)"',
            block,
            flags=re.S | re.I,
        )
        handle = _handle_from_href(titled.group(1)) if titled else None
        if handle not in titles:
            href = re.search(r'href="([^"]+)"', block)
            handle = _handle_from_href(href.group(1)) if href else None
        if handle not in titles:
            return block
        return retitle(block, handle)

    page = re.sub(
        r'<a\b[^>]*class="[^"]*\bProductCard\b[^"]*"[^>]*>.*?</a>',
        card_sub,
        page,
        flags=re.S | re.I,
    )
    page = re.sub(
        r'<article\b[^>]*class="[^"]*\bProductCard\b[^"]*"[^>]*>.*?</article>',
        card_sub,
        page,
        flags=re.S | re.I,
    )
    page = re.sub(
        r'<article\b[^>]*class="[^"]*ShopStrip__card[^"]*"[^>]*>.*?</article>',
        card_sub,
        page,
        flags=re.S | re.I,
    )
    page = re.sub(
        r'<a\b[^>]*class="[^"]*SpotCard[^"]*"[^>]*>.*?</a>',
        card_sub,
        page,
        flags=re.S | re.I,
    )

    def featured_name(match):
        handle = _handle_from_href(match.group(1))
        title = titles.get(handle)
        shown = _plain_text(match.group(2))
        if not title or shown.lower().startswith("buy") or shown.startswith("+"):
            return match.group(0)
        if shown in {title, titles.get(handle + "\0seo", title)}:
            return match.group(0)
        return match.group(0).replace(match.group(2), html.escape(title), 1)

    page = re.sub(
        r'<a\b[^>]*href="([^"]+)"[^>]*style="color:#fff;font-weight:\s*800[^"]*"[^>]*>(.*?)</a>',
        featured_name,
        page,
        flags=re.S | re.I,
    )

    def linked_alt(match):
        handle = _handle_from_href(match.group(2))
        title = titles.get(handle)
        if not title or html.unescape(match.group(3)) == title:
            return match.group(0)
        return match.group(1) + html.escape(title, quote=True) + match.group(4)

    page = re.sub(
        r'(<a\b[^>]*href="([^"]+)"[^>]*>\s*<img\b[^>]*\salt=")([^"]*)(")',
        linked_alt,
        page,
        flags=re.S | re.I,
    )
    return page


def repair_published_copy():
    """Apply the garble repairs and catalog card titles to published HTML, JSON, and XML."""
    changed = []
    for dirpath, dirnames, filenames in os.walk(BASE_DIR):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if ext not in {".html", ".json", ".xml"}:
                continue
            path = os.path.join(dirpath, name)
            if os.path.abspath(path) == os.path.abspath(__file__):
                continue
            original = open(path, encoding="utf-8").read()
            updated = apply_copy_repairs(original)
            if ext == ".html":
                updated = sync_card_titles(updated)
            if updated != original:
                open(path, "w", encoding="utf-8").write(updated)
                changed.append(os.path.relpath(path, BASE_DIR))
    return changed


# A Fabric bullet needs a real fiber or a measured weight. "fabric" by itself does not count.
_FIBER_WORD = re.compile(
    r"(?i)\b(?:cotton|polyester|nylon|elastane|spandex|fleece|acrylic|rayon|twill|poplin|"
    r"microfiber|terry|eva|rubber|canvas|mesh|leather|polyurethane|stainless|oxford)\b"
)
_MEASURED_WEIGHT = re.compile(r"(?i)\d+(?:\.\d+)?\s*(?:oz|gsm)\b")


def fabric_bullet_is_specific(bullet):
    """True when a Fabric bullet names a fiber or a weight in oz or gsm."""
    return bool(_FIBER_WORD.search(bullet or "") or _MEASURED_WEIGHT.search(bullet or ""))


def _story_paragraphs(page):
    copy = _product_copy_html(page)
    chunks = []
    for bit in re.findall(r"<p\b[^>]*>.*?</p>", copy, flags=re.S | re.I):
        if re.search(r"\bid=[\"']usShipNote", bit) or re.search(r"<a\b", bit, re.I):
            continue
        if not re.search(r"font-size:\s*1[45]", bit):
            continue
        chunks.append(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(bit))).strip())
    return [chunk for chunk in chunks if chunk]


def _description_fields(page):
    fields = []
    meta = re.search(r'<meta name="description" content="([^"]*)"', page)
    fields.append(("meta description", html.unescape(meta.group(1)) if meta else ""))
    og = re.search(r'<meta property="og:description" content="([^"]*)"', page)
    fields.append(("og:description", html.unescape(og.group(1)) if og else ""))
    for match in re.finditer(
        r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', page, flags=re.S | re.I
    ):
        for desc in re.finditer(r'"description"\s*:\s*"((?:\\.|[^"\\])*)"', match.group(1)):
            fields.append(("JSON-LD description", json.loads('"' + desc.group(1) + '"')))
    fields.append(("visible description", " ".join(_story_paragraphs(page))))
    return fields


def _starts_lowercase(text):
    stripped = re.sub(r"^[\s\"'(\[]+", "", text or "")
    return bool(stripped) and stripped[0].islower()


def _percent_without_fiber(text):
    for match in re.finditer(r"\d+(?:\.\d+)?\s*%", text or ""):
        rest = text[match.end():]
        if re.match(r"\s*(?:,|and\b|or\b)", rest, re.I):
            return True
        window = re.split(r"[.,;]", rest, maxsplit=1)[0]
        if re.match(r"\s*off\b", window, re.I):
            continue
        if not _FIBER_WORD.search(window):
            return True
    return False


def _own_titles(page):
    titles = set()
    h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", page, flags=re.S | re.I)
    if h1:
        titles.add(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(h1.group(1)))).strip().lower())
    bought = re.search(r'data-buy="(APC-C\d+)"', page) or re.search(r'prodId = "(APC-C\d+)"', page)
    pid = bought.group(1) if bought else ""
    for prod in products:
        if prod.get("id") == pid or (h1 and prod.get("title", "").strip().lower() in titles):
            for key in ("title", "seo_title"):
                name = (prod.get(key) or "").strip().lower()
                if name:
                    titles.add(name)
    return titles


def copy_quality_errors(page, name="page"):
    """Filler, weak fabric bullets, lowercase openings, and another product's name."""
    if re.search(r'http-equiv="refresh"', page, re.I) or "<h1" not in page.lower():
        return []
    errors = []
    bullets = re.findall(r"<li\b[^>]*>\s*Fabric:\s*(.*?)</li>", page, flags=re.S | re.I)
    for bullet in bullets:
        plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(bullet))).strip()
        if not fabric_bullet_is_specific(plain):
            errors.append(f"{name}: Fabric bullet is not a material ({plain[:60]})")
    fields = _description_fields(page)
    for label, text in fields:
        if label in ("meta description", "og:description", "visible description", "JSON-LD description") and _starts_lowercase(text):
            errors.append(f"{name}: {label} starts with a lowercase letter")
        if ",," in text or re.search(r"(?<!\.)\.\.(?!\.)", text) or _percent_without_fiber(text):
            errors.append(f"{name}: {label} has a broken percent or fragment")
    own = _own_titles(page)
    blob = " ".join(text for _, text in fields)
    for prod in products:
        for key in ("title", "seo_title"):
            title = re.sub(r"\s+", " ", prod.get(key) or "").strip()
            folded = title.lower()
            if len(title) < 18 or folded in own:
                continue
            if any(folded in own_title or own_title in folded for own_title in own if len(own_title) >= 8):
                continue
            if re.search(r"(?i)(?<![A-Za-z0-9])" + re.escape(title) + r"(?![A-Za-z0-9])", blob):
                errors.append(f"{name}: description names {title}")
                return errors
    return errors


def assert_copy_quality():
    """Self-test the copy gates, then scan every live product page."""
    if fabric_bullet_is_specific("fabric") or fabric_bullet_is_specific("Black") or fabric_bullet_is_specific("See the product description"):
        raise SystemExit("Fabric-bullet self-test failed: a bare word counted as a material")
    if not fabric_bullet_is_specific("80% cotton, 20% polyester; 100% cotton face; 9 oz; regular fit"):
        raise SystemExit("Fabric-bullet self-test failed: the 9 oz fleece line was rejected")
    repeat = (
        "<html><body><h1>Sample Tee</h1>"
        "<p style=\"font-size:15px\">Soft-hand graphic ink that holds a print in the dryer</p>"
        "<h2>Key Performance Specifications</h2>"
        "<ul><li>Soft-hand graphic ink that holds a print in the dryer</li></ul>"
        "</body></html>"
    )
    if not any("repeated sentence" in item for item in fabric_rule_errors(repeat, "repeat-fixture")):
        raise SystemExit("Repeat self-test failed: a spec repeated after the heading did not fail")
    lower = (
        "<html><head>"
        '<meta name="description" content="black hoodie with a sleeve seal.">'
        '<meta property="og:description" content="black hoodie with a sleeve seal.">'
        "</head><body><h1>Sample</h1>"
        '<p style="font-size:15px">black hoodie with a sleeve seal.</p></body></html>'
    )
    if not any("lowercase" in item for item in copy_quality_errors(lower, "case-fixture")):
        raise SystemExit("Lowercase self-test failed: a lowercase description did not fail")
    foreign = (
        "<html><head><meta name=\"description\" content=\"Also the Anaheim Race Day Windbreaker.\"></head>"
        "<body><h1>Sample Tee</h1>"
        '<p style="font-size:15px">Also the Anaheim Race Day Windbreaker.</p></body></html>'
    )
    if not any("Anaheim Race Day Windbreaker" in item for item in copy_quality_errors(foreign, "title-fixture")):
        raise SystemExit("Title self-test failed: another product's name in the description did not fail")
    broken = "80% and 20%,,"
    if not (_percent_without_fiber("80% and") and ",," in broken and re.search(r"(?<!\.)\.\.(?!\.)", "Dept..") and not re.search(r"(?<!\.)\.\.(?!\.)", "Wait...")):
        raise SystemExit("Fragment self-test failed: a bare percent, double comma, or double period was missed")
    errors = []
    folder = os.path.join(BASE_DIR, "products")
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".html"):
            continue
        page = open(os.path.join(folder, name), encoding="utf-8", errors="replace").read()
        errors.extend(copy_quality_errors(page, name))
    if errors:
        raise SystemExit("Copy quality failed:\n" + "\n".join(errors[:60]))


# The 11 listing names Fourthwall no longer uses. Slugs and URLs may still contain "heavyweight".
OLD_HEAVY_LISTING_NAMES = (
    "Apex Heavyweight Hybrid - Run. Station. Repeat.",
    "Apex Heavyweight Hybrid - Wall Balls & Bad Decisions",
    "Apex Heavyweight Hybrid - Sled Push Enthusiast",
    "Apex Heavyweight Hybrid - Burpee Broad Jumps",
    "Apex Heavyweight Hybrid - The Erg Doesn't Care How You Feel",
    "Apex Race City Heavyweight - Chicago Championship Division",
    "Apex Race City Heavyweight - Dallas Turf & Threshold",
    "Apex Race City Heavyweight - Anaheim SoCal Open Division",
    "Apex Race City Heavyweight - Miami Beach Endurance Club",
    "Apex Race City Heavyweight - Las Vegas Championship Qualifier",
    "Apex Race City Heavyweight - New York Hudson Pier Division",
    "Heavyweight Tee",
    "Heavyweight ring-spun fleece",
    "Oversized Heavyweight Gym Sweatshirt",
)
GUIDE_LINKS_REQUIRED = 6
# Unique hyphenated tokens in published HTML, CSS, JS, JSON, XML, CSV, TXT, and MD,
# including each file's path. The floor is that exact count, with a per-page baseline.
SLUG_TOKEN_MINIMUM = 3375
SLUG_PAGE_BASELINE = {
    'a4b8c9d0e1f234567890abcdef123456.txt': 0,
    'a8f4c2e9d1b740639c5e2a1f8b3d7e90.txt': 0,
    'a8f9d2e4c7b14f6093e5d8c2a1b4e7f0.txt': 0,
    'about.html': 17,
    'app.js': 1208,
    'articles/2026-2027-north-america-hybrid-race-calendar-course-and-turf-guide.html': 270,
    'articles/48-hour-post-race-recovery-protocol-cold-plunge-compression-red-light.html': 271,
    'articles/anaheim-socal-dec-2026-hyrox-race-gear-warmup-jackets-tech-shirts.html': 284,
    'articles/away-race-travel-packing-list-collapsible-foam-roller-shoe-case.html': 278,
    'articles/best-breathable-shirt-for-hyrox-compromised-running-sled-push.html': 272,
    'articles/best-hybrid-athlete-race-day-gear-and-recovery-tools-2026.html': 271,
    'articles/best-hyrox-shirts-breathable-race-tops-and-training-apparel-guide.html': 269,
    'articles/best-pump-cover-for-functional-fitness-racing.html': 266,
    'articles/bulletproof-knees-and-shins-for-compromised-running.html': 265,
    'articles/burpee-broad-jumps-80m-pacing-technique-and-breathing-strategy.html': 259,
    'articles/cancun-feb-2027-hyrox-heat-humidity-race-gear-and-warmup.html': 296,
    'articles/chicago-navy-pier-nov-2026-hyrox-race-gear-warmup-jackets-tech-shirts.html': 285,
    'articles/cold-plunge-and-red-light-recovery-routine-for-endurance-runners.html': 279,
    'articles/cold-plunge-vs-sauna-contrast-therapy-timing-for-hybrid-athletes.html': 258,
    'articles/compromised-running-pacing-calculator-and-1km-split-strategy.html': 265,
    'articles/compromised-running-shirt-hybrid-athlete.html': 258,
    'articles/custom-run-club-hybrid-gym-wholesale-team-shirts.html': 268,
    'articles/dallas-nov-2026-hyrox-race-gear-warmup-jackets-tech-shirts.html': 289,
    'articles/doubles-hybrid-race-strategy-how-to-split-stations-with-your-partner.html': 263,
    'articles/farmer-carry-grip-strength-liquid-chalk-and-dead-hang-guide.html': 277,
    'articles/funny-hyrox-workout-shirts-wall-balls-sled-push-roxzone.html': 280,
    'articles/heavyweight-gym-pump-covers-and-functional-racing-apparel-guide.html': 268,
    'articles/home-recovery-corner-setup-under-300-for-endurance-athletes.html': 272,
    'articles/how-to-cut-3-minutes-off-your-roxzone-and-compromised-running-splits.html': 269,
    'articles/how-to-train-for-your-first-hybrid-fitness-race-8-week-plan.html': 269,
    'articles/hybrid-athlete-gift-guide-2026.html': 299,
    'articles/hybrid-race-simulation-workouts-half-and-full-sim-to-predict-your-finish-time.html': 271,
    'articles/hyrox-anaheim-2026-socal-race-shirt-doubles-relay-team-kits.html': 268,
    'articles/hyrox-anaheim-socal-open-division-apparel.html': 262,
    'articles/hyrox-chicago-2026-last-minute-race-shirt-doubles-2-pack-shipping.html': 269,
    'articles/hyrox-chicago-navy-pier-race-day-shirt.html': 266,
    'articles/hyrox-dallas-2026-race-week-apparel-doubles-partner-shirts.html': 269,
    'articles/hyrox-dallas-lone-star-race-tee.html': 262,
    'articles/hyrox-las-vegas-qualifier-shirt.html': 260,
    'articles/hyrox-miami-beach-race-day-shirt.html': 254,
    'articles/hyrox-nyc-hudson-pier-race-shirt.html': 262,
    'articles/hyrox-pro-division-race-day-kit-checklist-2026.html': 271,
    'articles/hyrox-relay-team-matching-shirts-4-pack-2026.html': 274,
    'articles/hyrox-warmup-routine-and-start-corral-gear-guide-2026.html': 274,
    'articles/index.html': 235,
    'articles/las-vegas-feb-2027-hyrox-race-gear-warmup-jackets-tech-shirts.html': 287,
    'articles/lower-leg-circulation-stack-compression-boots-ems-foot-mat-cupping.html': 269,
    'articles/matching-hyrox-doubles-team-shirts-2026.html': 274,
    'articles/miami-beach-mar-2027-hyrox-race-gear-warmup-jackets-tech-shirts.html': 292,
    'articles/new-york-pier-may-2027-warmup-jacket-breathable-hybrid-race-shirt-guide.html': 285,
    'articles/porta-potty-line-pr-funny-hybrid-race-shirt.html': 281,
    'articles/post-hyrox-recovery-kit-sore-legs-wall-balls-sled-pull.html': 279,
    'articles/race-week-taper-carb-loading-and-cold-plunge-recovery-timeline.html': 270,
    'articles/racing-a-hybrid-fitness-race-at-altitude-denver-pacing-hydration-and-gear.html': 278,
    'articles/red-light-therapy-panel-vs-belt-660nm-850nm-recovery-guide.html': 277,
    'articles/respiratory-muscle-training-vo2-max-and-zone-2-heart-rate-guide.html': 269,
    'articles/roxzone-transition-drills-cut-dead-time-between-stations.html': 287,
    'articles/sandbag-lunges-100m-station-7-pacing-posture-and-leg-recovery.html': 265,
    'articles/skierg-rowerg-1000m-pacing-split-targets-hybrid-race.html': 259,
    'articles/sled-push-and-sled-pull-turf-friction-survival-protocol.html': 268,
    'articles/sled-push-enthusiast-workout-shirt.html': 267,
    'articles/sub-90-minute-hybrid-race-pacing-plan-station-by-station-split-targets.html': 287,
    'articles/the-week-after-a-hybrid-race-7-day-recovery-and-return-to-training-plan.html': 275,
    'articles/treadmill-compromised-running-workouts-for-winter-hybrid-race-training.html': 270,
    'articles/two-day-strength-plan-for-hybrid-racers-sled-push-lunges-and-wall-balls.html': 275,
    'articles/wall-balls-station-8-unbroken-rep-strategy-and-mobility-prep.html': 272,
    'articles/weighted-vest-murph-and-compromised-running-protocol-2026.html': 276,
    'articles/what-to-eat-before-a-hybrid-fitness-race-nutrition-and-hydration-plan.html': 268,
    'articles/what-to-wear-for-first-hyrox-race.html': 273,
    'articles/what-to-wear-hyrox-anaheim-chicago-dallas-2026.html': 281,
    'articles/zone-2-chest-strap-heart-rate-training-plan-hybrid-racers.html': 264,
    'b7e3c9a4d2f841069c5e1a8f3b2d6e40.txt': 0,
    'catalog.json': 1929,
    'collections/accessories.html': 46,
    'collections/hyrx.html': 79,
    'collections/new.html': 85,
    'collections/race-day-windbreakers.html': 47,
    'collections/shoes.html': 26,
    'collections/tanks.html': 37,
    'collections/tees.html': 117,
    'collections/tops.html': 29,
    'collections/windbreakers.html': 70,
    'collections/womens.html': 32,
    'contact.html': 16,
    'directory.html': 271,
    'feed.xml': 449,
    'fourthwall_city_jacket_variants.json': 43,
    'fourthwall_feed_variants.json': 397,
    'fourthwall_full_catalog_sync.json': 265,
    'gift-guide.html': 62,
    'google8a7e6d0a7e3acfb0.html': 4,
    'google_merchant_feed.xml': 1372,
    'google_shopping_feed.xml': 1372,
    'google_shopping_feed_ghpages.xml': 1372,
    'gyms/gyms_directory.json': 68,
    'gyms/index.html': 271,
    'index.html': 297,
    'llms.txt': 421,
    'perks-bar.js': 7,
    'pinterest_catalog_feed.csv': 1155,
    'privacy.html': 17,
    'products/100-wall-balls-unbroken-sleeveless-muscle-tank.html': 177,
    'products/1km-split.html': 187,
    'products/200m-farmer-carry-survivors-club-barbell-crest-tee.html': 183,
    'products/26-27-world-series-lightweight-warmup-jacket.html': 174,
    'products/8-runs-8-stations-zero-excuses-heavyweight-pump-cover-tee.html': 180,
    'products/8-station-functional-race-division-oversized-stealth-hoodie.html': 78,
    'products/aeromesh-breathable-breathable-hyrox-race-tech-tee.html': 7,
    'products/aeromesh-laser-vented-breathable-hyrox-race-tech-tee.html': 7,
    'products/anaheim-crest.html': 53,
    'products/anaheim-hyrx.html': 54,
    'products/anaheim-race-day-stitched.html': 180,
    'products/anaheim-race-day.html': 177,
    'products/anaheim-socal-open-division-pacific-coast-race-tee.html': 177,
    'products/apc-c01.html': 193,
    'products/apc-c02.html': 194,
    'products/apc-c03.html': 192,
    'products/apc-c04.html': 7,
    'products/apc-c05.html': 195,
    'products/apc-c06.html': 196,
    'products/apc-c07.html': 184,
    'products/apc-c08.html': 180,
    'products/apc-c09.html': 180,
    'products/apc-c10.html': 180,
    'products/apc-c100.html': 54,
    'products/apc-c101.html': 54,
    'products/apc-c102.html': 54,
    'products/apc-c103.html': 54,
    'products/apc-c104.html': 54,
    'products/apc-c105.html': 54,
    'products/apc-c106.html': 54,
    'products/apc-c107.html': 54,
    'products/apc-c108.html': 54,
    'products/apc-c109.html': 52,
    'products/apc-c11.html': 185,
    'products/apc-c110.html': 52,
    'products/apc-c111.html': 54,
    'products/apc-c112.html': 54,
    'products/apc-c113.html': 55,
    'products/apc-c114.html': 54,
    'products/apc-c115.html': 54,
    'products/apc-c116.html': 54,
    'products/apc-c117.html': 54,
    'products/apc-c118.html': 54,
    'products/apc-c119.html': 54,
    'products/apc-c12.html': 181,
    'products/apc-c120.html': 54,
    'products/apc-c121.html': 55,
    'products/apc-c122.html': 68,
    'products/apc-c123.html': 65,
    'products/apc-c124.html': 44,
    'products/apc-c125.html': 44,
    'products/apc-c126.html': 43,
    'products/apc-c127.html': 43,
    'products/apc-c128.html': 47,
    'products/apc-c129.html': 48,
    'products/apc-c13.html': 171,
    'products/apc-c130.html': 44,
    'products/apc-c131.html': 42,
    'products/apc-c132.html': 40,
    'products/apc-c133.html': 40,
    'products/apc-c134.html': 40,
    'products/apc-c135.html': 40,
    'products/apc-c136.html': 42,
    'products/apc-c137.html': 42,
    'products/apc-c138.html': 45,
    'products/apc-c139.html': 45,
    'products/apc-c14.html': 165,
    'products/apc-c140.html': 57,
    'products/apc-c141.html': 57,
    'products/apc-c142.html': 54,
    'products/apc-c143.html': 54,
    'products/apc-c144.html': 54,
    'products/apc-c145.html': 54,
    'products/apc-c146.html': 54,
    'products/apc-c147.html': 54,
    'products/apc-c148.html': 54,
    'products/apc-c149.html': 54,
    'products/apc-c15.html': 82,
    'products/apc-c150.html': 54,
    'products/apc-c16.html': 178,
    'products/apc-c17.html': 179,
    'products/apc-c18-anaheim-socal-tee.html': 178,
    'products/apc-c18.html': 178,
    'products/apc-c19.html': 179,
    'products/apc-c20.html': 179,
    'products/apc-c21.html': 180,
    'products/apc-c22.html': 180,
    'products/apc-c23.html': 181,
    'products/apc-c24.html': 183,
    'products/apc-c25.html': 183,
    'products/apc-c26.html': 185,
    'products/apc-c27.html': 184,
    'products/apc-c28.html': 178,
    'products/apc-c29.html': 176,
    'products/apc-c30.html': 188,
    'products/apc-c31.html': 177,
    'products/apc-c32.html': 180,
    'products/apc-c33.html': 180,
    'products/apc-c34.html': 181,
    'products/apc-c35.html': 79,
    'products/apc-c36.html': 191,
    'products/apc-c37.html': 187,
    'products/apc-c38.html': 188,
    'products/apc-c39.html': 7,
    'products/apc-c40.html': 189,
    'products/apc-c41.html': 190,
    'products/apc-c42.html': 179,
    'products/apc-c43.html': 177,
    'products/apc-c44.html': 177,
    'products/apc-c45.html': 175,
    'products/apc-c46.html': 179,
    'products/apc-c47.html': 178,
    'products/apc-c48.html': 178,
    'products/apc-c49.html': 178,
    'products/apc-c50.html': 178,
    'products/apc-c51.html': 182,
    'products/apc-c52.html': 182,
    'products/apc-c53.html': 181,
    'products/apc-c54.html': 181,
    'products/apc-c55.html': 181,
    'products/apc-c56.html': 194,
    'products/apc-c57.html': 185,
    'products/apc-c58.html': 54,
    'products/apc-c59.html': 53,
    'products/apc-c60.html': 53,
    'products/apc-c61.html': 53,
    'products/apc-c62.html': 53,
    'products/apc-c63.html': 54,
    'products/apc-c64.html': 53,
    'products/apc-c65.html': 53,
    'products/apc-c66.html': 50,
    'products/apc-c67.html': 54,
    'products/apc-c68.html': 56,
    'products/apc-c69.html': 55,
    'products/apc-c70.html': 183,
    'products/apc-c71.html': 52,
    'products/apc-c72.html': 52,
    'products/apc-c73.html': 52,
    'products/apc-c74.html': 53,
    'products/apc-c75.html': 55,
    'products/apc-c76.html': 32,
    'products/apc-c77.html': 52,
    'products/apc-c78.html': 52,
    'products/apc-c79.html': 52,
    'products/apc-c80.html': 52,
    'products/apc-c81.html': 52,
    'products/apc-c82.html': 52,
    'products/apc-c83.html': 52,
    'products/apc-c84.html': 51,
    'products/apc-c85.html': 51,
    'products/apc-c86.html': 183,
    'products/apc-c87.html': 183,
    'products/apc-c88.html': 183,
    'products/apc-c89.html': 183,
    'products/apc-c90.html': 185,
    'products/apc-c91.html': 183,
    'products/apc-c92.html': 183,
    'products/apc-c93.html': 183,
    'products/apc-c94.html': 183,
    'products/apc-c95.html': 183,
    'products/apc-c96.html': 185,
    'products/apc-c97.html': 185,
    'products/apc-c98.html': 185,
    'products/apc-c99.html': 54,
    'products/apex-8-station-race-day-tactical-duffle.html': 164,
    'products/apex-aeroshell-lightweight-race-warmup-jacket.html': 178,
    'products/apex-athletic-shoe-black-pink.html': 31,
    'products/atlanta-crest.html': 51,
    'products/atlanta-hyrx.html': 53,
    'products/atlanta-race-day-stitched.html': 182,
    'products/burpee-broad-jumps-build-character-tee.html': 194,
    'products/burpee-broad-jumps-build-character-warmup-hoodie.html': 180,
    'products/call-room.html': 53,
    'products/cancun-crest.html': 53,
    'products/cancun-hyrx.html': 53,
    'products/cancun-race-day-stitched.html': 184,
    'products/chicago-championship-division-navy-pier-hybrid-race-tee.html': 177,
    'products/chicago-crest.html': 53,
    'products/chicago-dallas-socal-world-series-prep-heavyweight-hoodie.html': 181,
    'products/chicago-hyrx.html': 53,
    'products/chicago-race-day-stitched.html': 184,
    'products/circuit-cities.html': 53,
    'products/compromised-running-club-breathable-race-tank.html': 187,
    'products/compromised-running-club-fleece-hoodie.html': 184,
    'products/compromised-running-club-tee.html': 52,
    'products/compromised-running-society-club-tee.html': 7,
    'products/compromised-running.html': 190,
    'products/coolcore--turf-and-sled-breathable-tech-shirt.html': 7,
    'products/coolcore-anti-chafe-turf-and-sled-breathable-tech-shirt.html': 7,
    'products/course-plate.html': 52,
    'products/dallas-crest.html': 53,
    'products/dallas-lone-star-division-turf-threshold-hybrid-race-tee.html': 178,
    'products/dallas-race-day-printable.html': 54,
    'products/dallas-race-day-stitched.html': 181,
    'products/dallas-race-day.html': 178,
    'products/defend-my-sled-push-dept-tee.html': 180,
    'products/defend-my-sled-push-fleece-hoodie.html': 181,
    'products/denver-crest.html': 53,
    'products/denver-race-day-stitched.html': 181,
    'products/denver-race-day.html': 177,
    'products/dry-pace--threshold-hyrox-tech-tee.html': 8,
    'products/dry-pace-moisture-wicking-threshold-hyrox-tech-tee.html': 7,
    'products/eight-marks.html': 49,
    'products/electrolyte-pacing-insulated-shaker-bottle.html': 81,
    'products/engine-biker-shorts-black.html': 53,
    'products/engine-biker-shorts-mint.html': 53,
    'products/engine-sports-bra-black.html': 51,
    'products/engine-sports-bra-mint.html': 51,
    'products/engine-training-tank-black.html': 50,
    'products/engine-training-tank-mint.html': 50,
    'products/featherweight-tri-blend-zero-drag-sub60-race-tee.html': 7,
    'products/field-issue.html': 52,
    'products/guadalajara-crest.html': 51,
    'products/guadalajara-hyrx.html': 53,
    'products/guadalajara-race-day-stitched.html': 182,
    'products/hold-the-pace.html': 52,
    'products/hong-kong-crest.html': 53,
    'products/hong-kong-hyrx.html': 53,
    'products/hong-kong-race-day-stitched.html': 184,
    'products/houston-crest.html': 51,
    'products/houston-hyrx.html': 53,
    'products/houston-race-day-stitched.html': 182,
    'products/hybrid-8-station-windbreaker-track-jacket.html': 176,
    'products/hyperbreathe--roxzone-speed-dept-tech-tee.html': 7,
    'products/hyperbreathe-seamless-roxzone-speed-dept-tech-tee.html': 7,
    'products/hyrx-cuff-beanie-black.html': 39,
    'products/hyrx-cuff-beanie-heather-grey.html': 39,
    'products/hyrx-dad-cap.html': 43,
    'products/hyrx-finish.html': 193,
    'products/hyrx-gym-sack-black.html': 41,
    'products/hyrx-gym-sack-burgundy.html': 41,
    'products/hyrx-low-cap.html': 47,
    'products/hyrx-mid-cap.html': 41,
    'products/hyrx-pool-slide-black.html': 56,
    'products/hyrx-pool-slide-burgundy.html': 56,
    'products/hyrx-quarter-zip.html': 64,
    'products/hyrx-rib-beanie-black.html': 39,
    'products/hyrx-rib-beanie-light-blue.html': 39,
    'products/hyrx-run-5-panel-black.html': 42,
    'products/hyrx-run-5-panel-light-blue-white.html': 42,
    'products/hyrx-station-crew.html': 67,
    'products/hyrx-station-towel-black.html': 44,
    'products/hyrx-station-towel-deep-olive.html': 44,
    'products/hyrx-surf-5-panel.html': 46,
    'products/hyrx-trucker-graphic.html': 43,
    'products/hyrx-trucker.html': 43,
    'products/las-vegas-championship-qualifier-sin-city-turf-club-tee.html': 178,
    'products/las-vegas-crest.html': 51,
    'products/las-vegas-hyrx.html': 53,
    'products/las-vegas-race-day-stitched.html': 182,
    'products/london-crest.html': 53,
    'products/london-hyrx.html': 54,
    'products/london-race-day-stitched.html': 184,
    'products/miami-beach-crest.html': 51,
    'products/miami-beach-heat-block-south-florida-endurance-race-tee.html': 178,
    'products/miami-beach-hyrx.html': 53,
    'products/miami-beach-race-day-stitched.html': 182,
    'products/minneapolis-crest.html': 51,
    'products/minneapolis-hyrx.html': 53,
    'products/minneapolis-race-day-stitched.html': 182,
    'products/monterrey-crest.html': 51,
    'products/monterrey-hyrx.html': 53,
    'products/monterrey-race-day-stitched.html': 182,
    'products/nashville-crest.html': 53,
    'products/nashville-hyrx.html': 53,
    'products/nashville-race-day-stitched.html': 180,
    'products/nashville-race-day.html': 177,
    'products/new-york-hudson-pier-metro-endurance-dept-race-tee.html': 179,
    'products/outline-mark.html': 52,
    'products/paris-crest.html': 53,
    'products/paris-hyrx.html': 53,
    'products/paris-race-day-stitched.html': 184,
    'products/peak-sign.html': 53,
    'products/phoenix-crest.html': 51,
    'products/phoenix-hyrx.html': 53,
    'products/phoenix-race-day-stitched.html': 182,
    'products/porta-potty-line-pr-pre-race-tee.html': 184,
    'products/portland-crest.html': 51,
    'products/portland-hyrx.html': 53,
    'products/portland-race-day-stitched.html': 182,
    'products/pro-division-lightweight-quarter-zip-race-shell.html': 176,
    'products/push-heavy.html': 189,
    'products/roxzone-penalties-ruined-my-pr-athletic-race-tee.html': 181,
    'products/roxzone-speed-dept.html': 190,
    'products/run-station-repeat-heavy-blend-hoodie.html': 180,
    'products/run-station-repeat-performance-tee.html': 192,
    'products/run-station-repeat-sleeveless-race-day-muscle-tank.html': 178,
    'products/san-diego-crest.html': 51,
    'products/san-diego-hyrx.html': 53,
    'products/san-diego-race-day-stitched.html': 182,
    'products/sandbag-lunges-are-a-personal-attack-oversized-pump-cover.html': 183,
    'products/sled-push-dept-raw-armhole-conditioning-muscle-tank.html': 176,
    'products/sled-push-enthusiast-race-day-tee.html': 191,
    'products/sleeve-seal.html': 55,
    'products/stem-type.html': 52,
    'products/sub-65-club-pace-pull-push-elite-division-tee.html': 184,
    'products/the-erg-doesnt-care-how-you-feel-heavyweight-fleece-hoodie.html': 180,
    'products/the-erg-doesnt-care-how-you-feel-tee.html': 195,
    'products/timing-gate.html': 52,
    'products/vancouver-crest.html': 53,
    'products/vancouver-hyrx.html': 53,
    'products/vancouver-race-day-stitched.html': 180,
    'products/vancouver-race-day.html': 177,
    'products/venttech-perforated-zone4-zone5-hybrid-training-shirt.html': 7,
    'products/wall-balls-bad-decisions-hoodie.html': 180,
    'products/wall-balls-bad-decisions-oversized-pump-cover.html': 193,
    'products/work-the-loop.html': 54,
    'products/zone-2-all-week-redline-all-weekend-performance-tee.html': 185,
    'products/zone-2-engine-builder-embroidered-dad-hat.html': 170,
    'products/zone-5-engine.html': 188,
    'returns.html': 21,
    'robots.txt': 4,
    'rss.xml': 449,
    'seo_articles.json': 654,
    'seo_city_pages/anaheim-socal-dec-2026-hyrox-race-gear-warmup-jackets-tech-shirts.html': 278,
    'seo_city_pages/anaheim-socal-dec-2026-hyrox-race-gear-warmup-jackets-tech-shirts.md': 18,
    'seo_city_pages/best-pump-cover-for-functional-fitness-racing.html': 259,
    'seo_city_pages/chicago-navy-pier-nov-2026-hyrox-race-gear-warmup-jackets-tech-shirts.html': 279,
    'seo_city_pages/chicago-navy-pier-nov-2026-hyrox-race-gear-warmup-jackets-tech-shirts.md': 20,
    'seo_city_pages/compromised-running-shirt-hybrid-athlete.html': 251,
    'seo_city_pages/dallas-nov-2026-hyrox-race-gear-warmup-jackets-tech-shirts.html': 283,
    'seo_city_pages/dallas-nov-2026-hyrox-race-gear-warmup-jackets-tech-shirts.md': 28,
    'seo_city_pages/heavyweight-gym-pump-covers-and-functional-racing-apparel-guide.html': 262,
    'seo_city_pages/hyrox-anaheim-2026-socal-race-shirt-doubles-relay-team-kits.html': 262,
    'seo_city_pages/hyrox-anaheim-socal-open-division-apparel.html': 255,
    'seo_city_pages/hyrox-chicago-2026-last-minute-race-shirt-doubles-2-pack-shipping.html': 263,
    'seo_city_pages/hyrox-chicago-navy-pier-race-day-shirt.html': 259,
    'seo_city_pages/hyrox-dallas-2026-race-week-apparel-doubles-partner-shirts.html': 263,
    'seo_city_pages/hyrox-dallas-lone-star-race-tee.html': 255,
    'seo_city_pages/hyrox-las-vegas-qualifier-shirt.html': 253,
    'seo_city_pages/hyrox-miami-beach-race-day-shirt.html': 247,
    'seo_city_pages/hyrox-nyc-hudson-pier-race-shirt.html': 255,
    'seo_city_pages/las-vegas-feb-2027-hyrox-race-gear-warmup-jackets-tech-shirts.html': 281,
    'seo_city_pages/las-vegas-feb-2027-hyrox-race-gear-warmup-jackets-tech-shirts.md': 25,
    'seo_city_pages/miami-beach-mar-2027-hyrox-race-gear-warmup-jackets-tech-shirts.html': 286,
    'seo_city_pages/miami-beach-mar-2027-hyrox-race-gear-warmup-jackets-tech-shirts.md': 27,
    'seo_city_pages/new-york-pier-may-2027-warmup-jacket-breathable-hybrid-race-shirt-guide.html': 279,
    'seo_city_pages/new-york-pier-may-2027-warmup-jacket-breathable-hybrid-race-shirt-guide.md': 22,
    'seo_city_pages/sled-push-enthusiast-workout-shirt.html': 260,
    'seo_city_pages/what-to-wear-for-first-hyrox-race.html': 266,
    'seo_city_pages/what-to-wear-hyrox-anaheim-chicago-dallas-2026.html': 275,
    'shipping.html': 16,
    'sitemap.xml': 217,
    'styles.css': 97,
    'team_affiliate_program.json': 75,
    'team_orders.html': 442,
    'terms.html': 18,
    'utm.js': 3,
    'wristband.html': 208,
}
_SLUG_FILE_EXTS = {".html", ".css", ".js", ".json", ".xml", ".csv", ".txt", ".md"}
_SLUG_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+){1,}")
_DANGLING_PREP = re.compile(
    r"(?i)\bfrom with\b|\bCut from\s+(?:with|for|to|of|on|in|at|by|into|over)\b"
)
_ABBREV = {"co", "u", "us", "dr", "mr", "mrs", "st", "no", "vs", "yd", "inc", "dept"}


def _surface_text(page):
    """Visible copy and meta, with URLs, scripts, and the cross-sell block removed."""
    text = re.sub(r'<div\b[^>]*data-cross-sell="1"[^>]*>.*?</div>', " ", page, flags=re.S | re.I)
    text = re.sub(r"<header\b[^>]*>.*?</header>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<nav\b[^>]*>.*?</nav>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<footer\b[^>]*>.*?</footer>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.S | re.I)
    metas = re.findall(
        r'<meta\b[^>]*(?:name|property)="(?:description|og:description|og:title|twitter:title|twitter:description)"[^>]*content="([^"]*)"',
        page,
        flags=re.I,
    )
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\s(?:href|src)=" + r'"[^"]*"', " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text + " " + " ".join(metas)))


def _lowercase_after_period(text):
    for match in re.finditer(r"([A-Za-z]+)\.\s+([a-z])", text or ""):
        if match.group(1).lower() in _ABBREV or len(match.group(1)) <= 1:
            continue
        return match.group(0)
    return ""


def _repeated_clauses(text):
    """A capitalized name or clause of 12 or more characters used twice."""
    plain = re.sub(r"\s+", " ", html.unescape(text or "")).strip()
    phrases = re.findall(
        r"(?:[A-Z][A-Za-z0-9+]*)(?:[ &-](?:[A-Z][A-Za-z0-9+]*|\d+))*",
        plain,
    )
    counts = {}
    for phrase in phrases:
        if len(phrase) < 12:
            continue
        key = phrase.lower()
        counts[key] = counts.get(key, 0) + 1
        if counts[key] >= 2:
            return phrase
    return ""


GUIDE_LINK_PAGES = (
"100-wall-balls-unbroken-sleeveless-muscle-tank.html",
    "1km-split.html",
    "200m-farmer-carry-survivors-club-barbell-crest-tee.html",
    "26-27-world-series-lightweight-warmup-jacket.html",
    "8-runs-8-stations-zero-excuses-heavyweight-pump-cover-tee.html",
    "8-station-functional-race-division-oversized-stealth-hoodie.html",
    "anaheim-race-day-stitched.html",
    "anaheim-race-day.html",
    "anaheim-socal-open-division-pacific-coast-race-tee.html",
    "apc-c01.html",
    "apc-c02.html",
    "apc-c03.html",
    "apc-c05.html",
    "apc-c06.html",
    "apc-c07.html",
    "apc-c08.html",
    "apc-c09.html",
    "apc-c10.html",
    "apc-c11.html",
    "apc-c12.html",
    "apc-c13.html",
    "apc-c14.html",
    "apc-c15.html",
    "apc-c16.html",
    "apc-c17.html",
    "apc-c18-anaheim-socal-tee.html",
    "apc-c18.html",
    "apc-c19.html",
    "apc-c20.html",
    "apc-c21.html",
    "apc-c22.html",
    "apc-c23.html",
    "apc-c24.html",
    "apc-c25.html",
    "apc-c26.html",
    "apc-c27.html",
    "apc-c28.html",
    "apc-c29.html",
    "apc-c30.html",
    "apc-c31.html",
    "apc-c32.html",
    "apc-c33.html",
    "apc-c34.html",
    "apc-c35.html",
    "apc-c36.html",
    "apc-c37.html",
    "apc-c38.html",
    "apc-c40.html",
    "apc-c41.html",
    "apc-c42.html",
    "apc-c43.html",
    "apc-c44.html",
    "apc-c45.html",
    "apc-c46.html",
    "apc-c47.html",
    "apc-c48.html",
    "apc-c49.html",
    "apc-c50.html",
    "apc-c51.html",
    "apc-c52.html",
    "apc-c53.html",
    "apc-c54.html",
    "apc-c55.html",
    "apc-c56.html",
    "apc-c57.html",
    "apc-c70.html",
    "apc-c86.html",
    "apc-c87.html",
    "apc-c88.html",
    "apc-c89.html",
    "apc-c90.html",
    "apc-c91.html",
    "apc-c92.html",
    "apc-c93.html",
    "apc-c94.html",
    "apc-c95.html",
    "apc-c96.html",
    "apc-c97.html",
    "apc-c98.html",
    "apex-8-station-race-day-tactical-duffle.html",
    "apex-aeroshell-lightweight-race-warmup-jacket.html",
    "atlanta-race-day-stitched.html",
    "burpee-broad-jumps-build-character-tee.html",
    "burpee-broad-jumps-build-character-warmup-hoodie.html",
    "cancun-race-day-stitched.html",
    "chicago-championship-division-navy-pier-hybrid-race-tee.html",
    "chicago-dallas-socal-world-series-prep-heavyweight-hoodie.html",
    "chicago-race-day-stitched.html",
    "compromised-running-club-breathable-race-tank.html",
    "compromised-running-club-fleece-hoodie.html",
    "compromised-running.html",
    "dallas-lone-star-division-turf-threshold-hybrid-race-tee.html",
    "dallas-race-day-stitched.html",
    "dallas-race-day.html",
    "defend-my-sled-push-dept-tee.html",
    "defend-my-sled-push-fleece-hoodie.html",
    "denver-race-day-stitched.html",
    "denver-race-day.html",
    "electrolyte-pacing-insulated-shaker-bottle.html",
    "guadalajara-race-day-stitched.html",
    "hong-kong-race-day-stitched.html",
    "houston-race-day-stitched.html",
    "hybrid-8-station-windbreaker-track-jacket.html",
    "hyrx-finish.html",
    "las-vegas-championship-qualifier-sin-city-turf-club-tee.html",
    "las-vegas-race-day-stitched.html",
    "london-race-day-stitched.html",
    "miami-beach-heat-block-south-florida-endurance-race-tee.html",
    "miami-beach-race-day-stitched.html",
    "minneapolis-race-day-stitched.html",
    "monterrey-race-day-stitched.html",
    "nashville-race-day-stitched.html",
    "nashville-race-day.html",
    "new-york-hudson-pier-metro-endurance-dept-race-tee.html",
    "paris-race-day-stitched.html",
    "phoenix-race-day-stitched.html",
    "porta-potty-line-pr-pre-race-tee.html",
    "portland-race-day-stitched.html",
    "pro-division-lightweight-quarter-zip-race-shell.html",
    "push-heavy.html",
    "roxzone-penalties-ruined-my-pr-athletic-race-tee.html",
    "roxzone-speed-dept.html",
    "run-station-repeat-heavy-blend-hoodie.html",
    "run-station-repeat-performance-tee.html",
    "run-station-repeat-sleeveless-race-day-muscle-tank.html",
    "san-diego-race-day-stitched.html",
    "sandbag-lunges-are-a-personal-attack-oversized-pump-cover.html",
    "sled-push-dept-raw-armhole-conditioning-muscle-tank.html",
    "sled-push-enthusiast-race-day-tee.html",
    "sub-65-club-pace-pull-push-elite-division-tee.html",
    "the-erg-doesnt-care-how-you-feel-heavyweight-fleece-hoodie.html",
    "the-erg-doesnt-care-how-you-feel-tee.html",
    "vancouver-race-day-stitched.html",
    "vancouver-race-day.html",
    "wall-balls-bad-decisions-hoodie.html",
    "wall-balls-bad-decisions-oversized-pump-cover.html",
    "zone-2-all-week-redline-all-weekend-performance-tee.html",
    "zone-2-engine-builder-embroidered-dad-hat.html",
    "zone-5-engine.html",
)
_GUIDE_BOX_RE = re.compile(
    r"<h2\b[^>]*>\s*Related\b[^<]*Buyer Guides\s*</h2>\s*<ul\b[^>]*>(.*?)</ul>",
    re.S | re.I,
)


def guide_boxes(page):
    """Every Related … Buyer Guides list, including headings that do not say HYROX."""
    boxes = []
    for match in _GUIDE_BOX_RE.finditer(page or ""):
        boxes.append(re.findall(r'href="[^"]*articles/', match.group(1)))
    return boxes


def _guide_link_count(page):
    return sum(len(links) for links in guide_boxes(page))


def guide_link_errors(page, name, baselines=None):
    """An empty buyer-guides box fails. A ca1a8bf page may not lose a link."""
    baselines = GUIDE_LINK_PAGES if baselines is None else baselines
    errors = []
    boxes = guide_boxes(page)
    for links in boxes:
        if not links:
            errors.append(f"{name}: Related Buyer Guides box is empty")
    count = sum(len(links) for links in boxes)
    required = GUIDE_LINKS_REQUIRED if name in baselines else 0
    if count < required:
        errors.append(f"{name}: guide links {count} < ca1a8bf {required}")
    return errors


def collect_slug_tokens(texts):
    """Hyphenated tokens in the given texts. Paths are not added."""
    tokens = set()
    for text in texts:
        tokens.update(_SLUG_TOKEN_RE.findall(text or ""))
    return tokens


def iter_slug_files():
    """Published text files. Markdown is not part of this count."""
    for dirpath, dirnames, filenames in os.walk(BASE_DIR):
        dirnames[:] = [name for name in dirnames if name not in {".git", "__pycache__", "node_modules"}]
        for name in filenames:
            if os.path.splitext(name)[1].lower() not in _SLUG_FILE_EXTS:
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, BASE_DIR)
            try:
                text = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            yield rel, text


def slug_file_tokens(rel, text):
    return set(_SLUG_TOKEN_RE.findall(rel)) | set(_SLUG_TOKEN_RE.findall(text or ""))


def slug_page_counts():
    return {rel: len(slug_file_tokens(rel, text)) for rel, text in iter_slug_files()}


def slug_page_shortfall(baseline, current):
    """Pages whose published token count fell below the frozen per-page count."""
    missed = []
    for rel, required in (baseline or {}).items():
        have = current.get(rel, 0)
        if have < required:
            missed.append(f"{rel}: {have} < {required}")
    return missed


def slug_token_count():
    """Unique hyphenated tokens across published text files and their paths."""
    tokens = set()
    for rel, text in iter_slug_files():
        tokens |= slug_file_tokens(rel, text)
    return len(tokens)


def lowercase_spec_bullets(page):
    found = []
    for ul in re.findall(r'<ul\b[^>]*class="HighlightsList"[^>]*>(.*?)</ul>', page or "", flags=re.S | re.I):
        for li in re.findall(r"<li\b[^>]*>(.*?)</li>", ul, flags=re.S | re.I):
            plain = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", li))).strip()
            plain = re.sub(r"""^[\s"'(\[]+""", "", plain)
            if plain and plain[0].islower():
                found.append(plain)
    return found


def _meta_contents(page, key):
    for tag in re.findall(r"<meta\b[^>]*>", page or "", flags=re.I):
        name = re.search(r'(?:name|property)="([^"]+)"', tag, flags=re.I)
        content = re.search(r'content="([^"]*)"', tag, flags=re.I)
        if name and content and name.group(1).lower() == key:
            yield html.unescape(content.group(1))


def twitter_garble_errors(page, name="page"):
    errors = []
    for text in _meta_contents(page, "twitter:description"):
        if ",," in text:
            errors.append(f"{name}: twitter:description has ,,")
        if re.search(r"(?<!\.)\.\.(?!\.)", text):
            errors.append(f"{name}: twitter:description has ..")
        if _percent_without_fiber(text):
            errors.append(f"{name}: twitter:description has a percent with no fiber")
        if re.search(r"(?i)\bAlso the\b", text):
            errors.append(f"{name}: twitter:description has Also the")
        clause = _repeated_clauses(text)
        if clause:
            errors.append(f"{name}: twitter:description repeats {clause!r}")
    return errors


def og_repeat_errors(page, name="page"):
    errors = []
    for text in _meta_contents(page, "og:description"):
        clause = _repeated_clauses(text)
        if clause:
            errors.append(f"{name}: og:description repeats {clause!r}")
    return errors


C36_SECOND_ROW = "Add to Bag - $"
C36_LINKS = ("wristband.html", "team_orders.html", "gyms/index.html")


def c36_section_errors(page, name):
    errors = []
    if C36_SECOND_ROW not in (page or ""):
        errors.append(f"{name}: missing the second buy row")
    for marker in C36_LINKS:
        if marker not in (page or ""):
            errors.append(f"{name}: missing {marker}")
    opens = len(re.findall(r"<section\b", page or "", flags=re.I))
    closes = len(re.findall(r"</section>", page or "", flags=re.I))
    if opens != closes:
        errors.append(f"{name}: section tags are not balanced ({opens} open, {closes} close)")
    return errors


_BLANK_CODE = re.compile(
    r"(?i)(?:\bcode\s+_{2,}|\bwith\s+\.(?!\d)|\bcode\s+\)|(?<!\w)\(\s*\)|<code\b[^>]*>\s*</code>)"
)
_DOUBLED_WORD = re.compile(r"\b([A-Za-z]{4,})\s+\1\b")
_DUFFLE_BANNED = re.compile(r"(?i)(?<![\w-])(?:900D|MOLLE|3-in-1|50L|50-liter)(?![\w-])")


CONFIRMED_PROMO_CODES = {
    "DALLAS10": 10,
    "TEAM15": 15,
    "CLUB10": 10,
    "DOUBLES10": 10,
    "DADBOD10": 10,
    "COACHSU10": 10,
}
_CODE_TOKEN = re.compile(r"\b([A-Z][A-Z0-9]{2,}(?:10|15|25))\b")
_BLANK_CODE_FORM = re.compile(
    r"(?i)(?:\bcode\s+for\b|\bcode\s{2,}for\b|\buse code for\b|\bcode\s*\(or\b|\bcode\s*\(e\.g\b|\bwith code\s*\+|\bcode\s+\)|(?<!\w)\(\s*\))"
)


NEVER_DISPLAY_CODES = ("HYR" + "OX10",)
FORBIDDEN_GENERATOR_CODES = ("HYR" + "OX10", "HYR" + "OX15", "TEAM" + "25")


def never_display_errors(text, name="page"):
    """Codes that exist at checkout but must never appear in a served file."""
    if not text:
        return []
    return [f"{name}: never-display code {code}" for code in NEVER_DISPLAY_CODES if code in text]


def duplicate_perk_code_errors(text, name="page"):
    """A gym card shows exactly one athlete code."""
    if not text or "Athlete Perks Code" not in text:
        return []
    errors = []
    for match in re.finditer(r"Athlete Perks Code:(.*?)</span>", text, flags=re.S):
        tokens = _CODE_TOKEN.findall(match.group(1))
        if len(tokens) != 1:
            shown = ", ".join(tokens) if tokens else "none"
            errors.append(f"{name}: perk card must show one code ({shown})")
    return errors


def md_prose_errors(text, name="page"):
    """Served markdown must not glue 'Made to order.' onto the previous sentence or use a double space."""
    if not text:
        return []
    errors = []
    for number, line in enumerate(text.splitlines(), 1):
        core = line[:-2] if line.endswith("  ") else line
        if re.search(r" {2,}", core):
            errors.append(f"{name}:{number}: double space")
        if re.search(r"(?<![.!?]) Made to order\.", core):
            errors.append(f"{name}:{number}: Made to order run-on")
    return errors


_PROMO_WORD = re.compile(r"(?i)\b(?:code|promo|coupon|use)\b")
_PROMOISH = re.compile(r"\b([A-Za-z]{2,}\d+[A-Za-z0-9]*|[A-Z]{6,})\b")
_OFFER_PCT = re.compile(
    r"(?i)(?:\b(?:15|20|25)\s*%\s*off\b|\bsave\s+(?:15|20|25)\s*%|\binstant\s+(?:15|20|25)\s*%|\b(?:15|20|25)\s*%\s*[–-]\s*(?:15|20|25)\s*%)"
)
_EMPTY_HEADING = re.compile(r"<h[1-6]\b[^>]*>\s*</h[1-6]>", re.I)


_PROMO_AFTER = re.compile(
    r"^(?:\s+|[^A-Za-z0-9]{1,8})*(?:codes?\s+)?([A-Za-z]{2,}\d+[A-Za-z0-9]*|[A-Z]{6,})\b"
)


def promoish_errors(text, name="page"):
    """Uppercase promo-looking tokens, and lowercase codes, next to code, promo, coupon, or use."""
    if not text:
        return []
    errors = []
    for word in _PROMO_WORD.finditer(text):
        window = text[word.end():word.end() + 48]
        match = _PROMO_AFTER.match(window)
        if not match:
            continue
        token = match.group(1)
        if ":" in window[:8] and not any(ch.isdigit() for ch in token):
            continue
        if token != token.upper():
            errors.append(f"{name}: lowercase code {token}")
        elif token not in CONFIRMED_PROMO_CODES:
            errors.append(f"{name}: unlisted promo token {token}")
    return errors


def code_percent_errors(text, name="page"):
    """A percent written next to a confirmed code has to be that code's percent."""
    if not text:
        return []
    errors = []
    for match in re.finditer(r"\b(" + "|".join(CONFIRMED_PROMO_CODES) + r")\b", text):
        window = text[match.end():match.end() + 32]
        pct = re.search(r"\b(10|15|20|25)\s*%", window)
        if not pct:
            continue
        got = int(pct.group(1))
        expect = CONFIRMED_PROMO_CODES[match.group(1)]
        if got != expect:
            errors.append(f"{name}: {match.group(1)} is next to {got}%")
    return errors


def offer_percent_errors(text, name="page"):
    """A 15%, 20%, or 25% offer has to name the confirmed code that creates it."""
    if not text:
        return []
    errors = []
    for match in _OFFER_PCT.finditer(text):
        snippet = re.sub(r"\s+", " ", match.group(0)).strip()
        nearby = text[match.start():match.end() + 40]
        if re.search(r"(?i)commission", nearby):
            continue
        if re.search(r"(?i)(?:20|25)\s*%", snippet):
            errors.append(f"{name}: percent offer {snippet} has no confirmed code")
            continue
        window = text[max(0, match.start() - 70):match.end() + 70]
        if "TEAM15" not in window:
            errors.append(f"{name}: 15% offer is not tied to TEAM15")
    return errors


def empty_heading_errors(text, name="page"):
    if text and _EMPTY_HEADING.search(text):
        return [f"{name}: empty heading"]
    return []


def copy_button_errors(text, name="page"):
    """A copy button writes the same code the card displays."""
    if not text:
        return []
    errors = []
    for match in re.finditer(r"writeText\('([A-Z0-9]+)'\)", text):
        copied = match.group(1)
        window = text[max(0, match.start() - 400):match.start()]
        shown = _CODE_TOKEN.findall(window)
        if shown and shown[-1] != copied:
            errors.append(f"{name}: copy button writes {copied} but shows {shown[-1]}")
    return errors


def code_list_errors(text, name="page"):
    """app.js and team_orders checkout maps match the confirmed codes and percents."""
    if not text:
        return []
    errors = []
    for match in re.finditer(r"(?:PROMO_CODES|CHECKOUT_CODES)\s*=\s*\{", text):
        depth = 1
        end = match.end()
        while end < len(text) and depth:
            if text[end] == "{":
                depth += 1
            elif text[end] == "}":
                depth -= 1
            end += 1
        body = text[match.end():end - 1]
        found = {}
        for key, pct in re.findall(r"\b([A-Z][A-Z0-9]+)\s*:\s*\{[^}]*?\bpct:\s*(\d+)", body):
            found[key] = int(pct)
        for key, pct in re.findall(r"\b([A-Z][A-Z0-9]+)\s*:\s*(\d+)", body):
            found.setdefault(key, int(pct))
        for key, pct in found.items():
            if key not in CONFIRMED_PROMO_CODES:
                errors.append(f"{name}: code list has {key}")
            elif pct != CONFIRMED_PROMO_CODES[key]:
                errors.append(f"{name}: {key} is listed at {pct}%")
        for key in CONFIRMED_PROMO_CODES:
            if key not in found:
                errors.append(f"{name}: code list is missing {key}")
    return errors


def jsonld_code_errors(text, name="page"):
    if not text:
        return []
    errors = []
    for match in re.finditer(r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', text, flags=re.S | re.I):
        block = html.unescape(match.group(1))
        label = name + " JSON-LD"
        errors.extend(promoish_errors(block, label))
        errors.extend(code_percent_errors(block, label))
        errors.extend(offer_percent_errors(block, label))
    return errors


def generator_text_errors(text, name="generator"):
    """A rebuild must not be able to publish a removed or unconfirmed code."""
    if not text:
        return []
    errors = []
    for token in FORBIDDEN_GENERATOR_CODES:
        if token in text:
            errors.append(f"{name}: generator still contains {token}")
    for token in set(_CODE_TOKEN.findall(text)):
        if token not in CONFIRMED_PROMO_CODES:
            errors.append(f"{name}: unconfirmed generator code {token}")
    return errors


def generator_source_errors():
    errors = []
    for name in ("build_seo_and_feeds.py", "sync_fourthwall_feed_variants.py", "checkout-code.js"):
        path = os.path.join(BASE_DIR, name)
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        errors.extend(generator_text_errors(text, name))
    return errors


def promo_code_errors(text, name="page"):
    """Blank code forms, and any code token next to the word code that is not confirmed."""
    if not text:
        return []
    visible = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.S | re.I)
    visible = re.sub(r"<style\b[^>]*>.*?</style>", " ", visible, flags=re.S | re.I)
    errors = []
    if _BLANK_CODE_FORM.search(visible):
        errors.append(f"{name}: blank promo code")
    for match in re.finditer(r"(?i)\b(?:promo\s+)?codes?\b", visible):
        window = visible[match.end():match.end() + 48]
        for token in _CODE_TOKEN.findall(window):
            if token not in CONFIRMED_PROMO_CODES:
                errors.append(f"{name}: unconfirmed code {token}")
    return errors


def blank_code_errors(text, name="page"):
    """Blank discount-code forms. A real code such as DALLAS10 is allowed."""
    if not text:
        return []
    visible = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.S | re.I)
    visible = re.sub(r"<style\b[^>]*>.*?</style>", " ", visible, flags=re.S | re.I)
    if _BLANK_CODE.search(visible):
        return [f"{name}: blank discount code"]
    return []


def doubled_word_errors(text, name="page"):
    """A word repeated inside one text node, such as 'breathable'."""
    nodes = re.findall(r">([^<]+)<", text or "")
    if "<" not in (text or ""):
        nodes = [text or ""]
    for node in nodes:
        plain = re.sub(r"\s+", " ", html.unescape(node)).strip()
        match = _DOUBLED_WORD.search(plain)
        if match:
            return [f"{name}: doubled word {match.group(0)!r}"]
    return []


def public_copy_chunks(name, text):
    """Prose strings from a feed, JSON, or text file. JSON syntax is not prose."""
    if name.endswith(".json"):
        chunks = []
        for match in re.finditer(r'"((?:\\.|[^"\\])*)"', text or ""):
            try:
                chunks.append(json.loads('"' + match.group(1) + '"'))
            except json.JSONDecodeError:
                continue
        return chunks
    if name.endswith((".xml", ".html")):
        plain = re.sub(r"<script\b[^>]*>.*?</script>", " ", text or "", flags=re.S | re.I)
        return [html.unescape(node) for node in re.findall(r">([^<]+)<", plain) if node.strip()]
    return [text or ""]


def paired_section_errors(page, name="page"):
    """Every Frequently Paired card has to be a complete card inside the grid."""
    errors = []
    for match in re.finditer(r"<h2\b[^>]*>\s*Frequently Paired.*?</section>", page or "", flags=re.S | re.I):
        block = match.group(0)
        start = block.find('<div class="ProductGrid">')
        if start < 0:
            errors.append(f"{name}: Frequently Paired section has no grid")
            continue
        pos = start + len('<div class="ProductGrid">')
        depth = 1
        grid_end = None
        while pos < len(block):
            nxt = re.search(r"</?div\b", block[pos:])
            if not nxt:
                break
            at = pos + nxt.start()
            if nxt.group(0).startswith("</"):
                depth -= 1
                if depth == 0:
                    grid_end = at
                    break
            else:
                depth += 1
            pos = at + 4
        if grid_end is None:
            errors.append(f"{name}: Frequently Paired grid is not closed")
            continue
        grid = block[start:grid_end]
        after = block[grid_end + len("</div>"):]
        after_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", after)).strip()
        if after_text or re.search(r'class="ProductCard"', after):
            errors.append(f"{name}: Frequently Paired content sits outside the grid")
        for card in re.finditer(r'<a\b[^>]*class="[^"]*\bProductCard\b[^"]*"[^>]*>.*?</a>', grid, flags=re.S | re.I):
            chunk = card.group(0)
            if "ProductCard__Media" not in chunk or "ProductCard__Title" not in chunk or "<img" not in chunk:
                errors.append(f"{name}: Frequently Paired card is incomplete")
                break
    return errors


def duffle_claim_errors(text, name="page"):
    visible = re.sub(r"https?://\S+", " ", text or "")
    if _DUFFLE_BANNED.search(visible):
        return [f"{name}: duffle claim is not in the Fourthwall spec"]
    return []


def cross_sell_errors(page, name="page"):
    errors = []
    titles = {}
    for prod in products:
        handle = prod.get("handle")
        title = (prod.get("title") or "").strip()
        if handle and title:
            titles[handle] = title
    for match in re.finditer(
        r'<div\b[^>]*class="[^"]*\bCrossSell\b[^"]*"[^>]*>\s*<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        page or "",
        flags=re.S | re.I,
    ):
        handle = _handle_from_href(match.group(1))
        expected = titles.get(handle)
        if not expected:
            continue
        shown = _plain_text(match.group(2))
        if shown not in {expected, "Also the " + expected}:
            errors.append(f"{name}: cross-sell {shown!r} != catalog {expected!r}")
    return errors


def regression_errors(page, name="page"):
    if re.search(r'http-equiv="refresh"', page, re.I) or "<h1" not in page.lower():
        return []
    errors = []
    fields = []
    for label, pattern in (
        ("meta description", r'<meta name="description" content="([^"]*)"'),
        ("og:description", r'<meta property="og:description" content="([^"]*)"'),
        ("twitter:description", r'<meta name="twitter:description" content="([^"]*)"'),
    ):
        match = re.search(pattern, page)
        fields.append((label, html.unescape(match.group(1)) if match else ""))
    for match in re.finditer(r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', page, flags=re.S | re.I):
        for desc in re.finditer(r'"description"\s*:\s*"((?:\\.|[^"\\])*)"', match.group(1)):
            fields.append(("JSON-LD description", json.loads('"' + desc.group(1) + '"')))
    visible = " ".join(_story_paragraphs(page))
    fields.append(("visible description", visible))
    surface = _surface_text(page)
    for label, text in fields:
        if label == "twitter:description" and _starts_lowercase(text):
            errors.append(f"{name}: twitter:description starts with a lowercase letter")
        hit = _lowercase_after_period(text)
        if hit:
            errors.append(f"{name}: {label} has a lowercase sentence {hit!r}")
        if "in./yd" in text or "It is part of the Apex Hybrid Co. catalog." in text:
            errors.append(f"{name}: {label} has a broken unit or the catalog filler")
        if label in ("og:description", "twitter:description"):
            clause = _repeated_clauses(text)
            if clause:
                errors.append(f"{name}: {label} repeats {clause!r}")
    if _DANGLING_PREP.search(surface):
        errors.append(f"{name}: dangling preposition fragment")
    for title in OLD_HEAVY_LISTING_NAMES:
        if title.lower() in surface.lower():
            errors.append(f"{name}: old listing name {title}")
    return errors


def assert_restored_sections():
    """Self-test the regression gates, then check guides, C36, slugs, and old names."""
    if not _lowercase_after_period("Wraps from front to back. quick-dry performance."):
        raise SystemExit("Lowercase-sentence self-test failed")
    if not _repeated_clauses("Comfort Colors 1717. Blank: Comfort Colors 1717."):
        raise SystemExit("Repeated-clause self-test failed: Comfort Colors was not caught")
    if not _repeated_clauses("Oversized black Bella+Canvas tee. Bella+Canvas oversized tee."):
        raise SystemExit("Repeated-clause self-test failed: Bella+Canvas was not caught")
    if not _DANGLING_PREP.search("Cut from with a soft brushed interior."):
        raise SystemExit("Dangling-preposition self-test failed")
    filler = '<html><head><meta name="twitter:description" content="black hoodie."></head><body><h1>X</h1><p style="font-size:15px">It is part of the Apex Hybrid Co. catalog.</p></body></html>'
    fixture_errors = regression_errors(filler, "regression-fixture")
    if not any("twitter:description starts" in item for item in fixture_errors):
        raise SystemExit("Twitter lowercase self-test failed")
    if not any("catalog filler" in item for item in fixture_errors):
        raise SystemExit("Catalog-filler self-test failed")
    self_tests = []

    def fail_check(label, errors, needle):
        self_tests.append(label)
        if not any(needle in item for item in errors):
            raise SystemExit(f"Self-test failed: {label}")

    old_name = '<html><body><h1>Sample</h1><p>Apex Heavyweight Hybrid - Run. Station. Repeat.</p></body></html>'
    fail_check("old listing name", regression_errors(old_name, "name-fixture"), "old listing name")
    for phrase in ("Heavyweight Tee", "Heavyweight ring-spun fleece", "Oversized Heavyweight Gym Sweatshirt"):
        page = f"<html><body><h1>Sample</h1><p>Shop the {phrase} today.</p></body></html>"
        fail_check(phrase, regression_errors(page, "name-fixture"), "old listing name")
    kept_url = '<html><body><h1>Sample</h1><a href="https://example.com/apex-heavyweight-hybrid-tee-run-station-repeat">Shop</a></body></html>'
    self_tests.append("old name ignores a URL")
    if any("old listing name" in item for item in regression_errors(kept_url, "url-fixture")):
        raise SystemExit("Old-name self-test flagged a URL slug")
    empty_box = (
        '<html><body><h1>Sample</h1><h2>Related Training, Pacing &amp; Recovery Buyer Guides</h2>'
        '<ul></ul></body></html>'
    )
    fail_check("empty guide box", guide_link_errors(empty_box, "hyrx-finish.html"), "empty")
    short_box = (
        '<html><body><h1>Sample</h1><h2>Related HYROX Training, Pacing &amp; Recovery Buyer Guides</h2>'
        '<ul><li><a href="../articles/one-guide.html">One</a></li></ul></body></html>'
    )
    fail_check("per-page guide floor", guide_link_errors(short_box, "hyrx-finish.html"), "ca1a8bf")
    full_box = short_box.replace("</ul>", '<li><a href="../articles/two.html">Two</a></li>' * 5 + "</ul>")
    self_tests.append("full guide box passes")
    if guide_link_errors(full_box, "hyrx-finish.html"):
        raise SystemExit("Guide self-test failed: six links were flagged")
    self_tests.append("slug per-page floor")
    if not slug_page_shortfall({"products/a.html": 4}, {"products/a.html": 3}):
        raise SystemExit("Slug self-test missed a per-page drop")
    self_tests.append("slug per-page exact count passes")
    if slug_page_shortfall({"products/a.html": 4}, {"products/a.html": 4}):
        raise SystemExit("Slug self-test flagged an exact per-page count")
    bullet = '<html><body><h1>Sample</h1><ul class="HighlightsList"><li>lining, elastic cuffs, and a drawcord hem.</li></ul></body></html>'
    self_tests.append("lowercase spec bullet")
    if not lowercase_spec_bullets(bullet):
        raise SystemExit("Spec-bullet self-test failed: a lowercase bullet did not fail")
    c36 = open(os.path.join(BASE_DIR, "products", "compromised-running.html"), encoding="utf-8").read()
    fail_check("second buy row", c36_section_errors(c36.replace("Add to Bag - $", "Add to Bag · $"), "c36"), "second buy row")
    fail_check("wristband link", c36_section_errors(c36.replace("wristband.html", "wristband-gone.html"), "c36"), "wristband.html")
    fail_check("team link", c36_section_errors(c36.replace("team_orders.html", "team-gone.html"), "c36"), "team_orders.html")
    fail_check("gym link", c36_section_errors(c36.replace("gyms/index.html", "gyms/gone.html"), "c36"), "gyms/index.html")
    twitter = '<html><head><meta name="twitter:description" content="{text}"></head><body><h1>Sample</h1></body></html>'
    fail_check("twitter ,,", twitter_garble_errors(twitter.format(text="100%,, relaxed fit."), "tw"), ",,")
    fail_check("twitter percent", twitter_garble_errors(twitter.format(text="Save 15% today."), "tw"), "percent")
    fail_check("twitter ..", twitter_garble_errors(twitter.format(text="Jackets APC-C42..APC-C45."), "tw"), "..")
    fail_check("twitter Also the", twitter_garble_errors(twitter.format(text="Also the Anaheim Race Day Windbreaker."), "tw"), "Also the")
    fail_check(
        "twitter repeated clause",
        twitter_garble_errors(twitter.format(text="Sled Push Dept. tee and another Sled Push Dept. tank."), "tw"),
        "repeats",
    )
    og = '<html><head><meta content="Comfort Colors 1717. Blank: Comfort Colors 1717." property="og:description"></head><body><h1>Sample</h1></body></html>'
    fail_check("og repeated clause", og_repeat_errors(og, "og"), "repeats")
    jsonld = (
        '<html><head><script type="application/ld+json">{"description":"black hoodie with a sleeve seal."}</script></head>'
        "<body><h1>Sample</h1><p style=\"font-size:15px\">Black hoodie with a sleeve seal.</p></body></html>"
    )
    fail_check("JSON-LD lowercase", copy_quality_errors(jsonld, "jsonld"), "JSON-LD description")
    broken_grid = (
        '<section><h2>Frequently Paired Tees</h2><div class="ProductGrid">'
        '<a class="ProductCard" href="a.html"><div class="ProductCard__Media"><img alt="A"></div>'
        '<div class="ProductCard__Title">A</div></a></div>'
        '<div class="ProductCard__Title">Built For Heavy Legs</div></section>'
    )
    fail_check("paired card outside grid", paired_section_errors(broken_grid, "paired"), "outside the grid")
    whole_grid = (
        '<section><h2>Frequently Paired Tees</h2><div class="ProductGrid">'
        '<a class="ProductCard" href="a.html"><div class="ProductCard__Media"><img alt="A"></div>'
        '<div class="ProductCard__Title">A</div></a></div></section>'
    )
    self_tests.append("complete paired card passes")
    if paired_section_errors(whole_grid, "paired"):
        raise SystemExit("Paired-card self-test flagged a complete card")
    fail_check("blank code ___", blank_code_errors("Use Code ___ for 15% Off", "code"), "blank discount code")
    fail_check("blank with .", blank_code_errors("15% OFF Doubles 2-Packs with .", "code"), "blank discount code")
    fail_check("blank code )", blank_code_errors("Save 15% (code ) today", "code"), "blank discount code")
    fail_check("blank ( )", blank_code_errors("Relay Team Kits ( )", "code"), "blank discount code")
    self_tests.append("DALLAS10 is not a blank code")
    if blank_code_errors("10% off with code DALLAS10.", "code"):
        raise SystemExit("Blank-code self-test flagged DALLAS10")
    fail_check("doubled word", doubled_word_errors("<h4>Breathable Breathable Tech Shirts</h4>", "art"), "Breathable")
    self_tests.append("jog in and passes")
    if sitewide_garble_hits("A simple city tee for the jog in and the photo after."):
        raise SystemExit("Garble self-test flagged jog in and the photo after")
    unbalanced = c36.replace("</section>", "</section></section>", 1)
    fail_check("balanced section", c36_section_errors(unbalanced, "c36"), "not balanced")
    fail_check("duffle 50L", duffle_claim_errors("A 50L bag with MOLLE and a 3-in-1 carry.", "duffle"), "duffle claim")
    self_tests.append("duffle Fourthwall spec passes")
    if duffle_claim_errors("27.4 L. LEVELED strap system. 93% polyester, 7% nylon, UA Storm.", "duffle"):
        raise SystemExit("Duffle self-test flagged the Fourthwall spec")
    foreign_sell = '<div class="CrossSell" data-cross-sell="1"><a href="zone-5-engine.html">Also the Zone 5 Engine</a></div>'
    fail_check("cross-sell catalog title", cross_sell_errors(foreign_sell, "sell"), "cross-sell")
    fail_check("code  for", promo_code_errors("code  for 15% off Doubles 2-Packs", "promo"), "blank promo code")
    fail_check("code (or )", promo_code_errors("apply code (or ) at checkout", "promo"), "blank promo code")
    fail_check("Use code for", promo_code_errors("Yes! Use code for 15% off", "promo"), "blank promo code")
    fail_check("code (e.g.", promo_code_errors("15% off with code (e.g., $36)", "promo"), "blank promo code")
    hidden_team = "TEAM" + "25"
    hidden_fifteen = "HYR" + "OX15"
    fail_check("unconfirmed removed code", promo_code_errors("use code " + hidden_team + " for 25% off", "promo"), hidden_team)
    fail_check("unconfirmed removed fifteen", promo_code_errors("promo code " + hidden_fifteen, "promo"), hidden_fifteen)
    self_tests.append("confirmed DALLAS10 passes")
    if promo_code_errors("Apply code DALLAS10 for 10% off the entire order.", "promo"):
        raise SystemExit("Promo self-test flagged DALLAS10")
    self_tests.append("confirmed TEAM15 passes")
    if promo_code_errors("Apply code TEAM15 for 15% off the entire order.", "promo"):
        raise SystemExit("Promo self-test flagged TEAM15")
    fail_check(
        "duplicate perk code",
        duplicate_perk_code_errors("Athlete Perks Code: <strong>DALLAS10</strong> / <strong>DALLAS10</strong></span>", "gym"),
        "one code",
    )
    self_tests.append("one perk code passes")
    if duplicate_perk_code_errors("Athlete Perks Code: <strong>COACHSU10</strong></span>", "gym"):
        raise SystemExit("Perk-code self-test flagged a single COACHSU10 card")
    hidden_display = NEVER_DISPLAY_CODES[0]
    fail_check("never-display hidden code", never_display_errors("<!-- Sticky " + hidden_display + " wristband -->", "page"), hidden_display)
    self_tests.append("DALLAS10 may be displayed")
    if never_display_errors("Apply code DALLAS10 for 10% off the entire order.", "page"):
        raise SystemExit("Never-display self-test flagged DALLAS10")
    fail_check("md run-on", md_prose_errors("Order at https://www.apexhybridco.com Made to order.", "city.md"), "run-on")
    fail_check("md double space", md_prose_errors("Roxzone Speed Dept.  Tech Tee", "city.md"), "double space")
    self_tests.append("clean markdown passes")
    if md_prose_errors("Order at https://www.apexhybridco.com. Made to order.", "city.md"):
        raise SystemExit("Markdown self-test flagged a finished sentence")
    fail_check("lowercase code", promoish_errors("use code dallas10 at checkout", "promo"), "lowercase")
    fail_check("promo without the word code", promoish_errors("apply promo SAVE20 today", "promo"), "SAVE20")
    fail_check("all-caps promo token", promoish_errors("coupon APEXVIP", "promo"), "APEXVIP")
    self_tests.append("confirmed promo token passes")
    if promoish_errors("use code DALLAS10", "promo"):
        raise SystemExit("Promo-token self-test flagged DALLAS10")
    fail_check("wrong percent", code_percent_errors("DALLAS10 for 25% off", "pct"), "25%")
    self_tests.append("matching percent passes")
    if code_percent_errors("TEAM15 for 15% off the entire order", "pct"):
        raise SystemExit("Percent self-test flagged TEAM15 at 15%")
    fail_check("untied 15% offer", offer_percent_errors("Doubles 2-Packs (15% off) today", "offer"), "TEAM15")
    fail_check("25% offer", offer_percent_errors("Save 25% on a 10-pack", "offer"), "25%")
    self_tests.append("TEAM15 offer passes")
    if offer_percent_errors("15% off your entire order with code TEAM15", "offer"):
        raise SystemExit("Offer self-test flagged TEAM15")
    fail_check("empty heading", empty_heading_errors('<h3 style="color:#fff;"></h3>', "head"), "empty heading")
    self_tests.append("filled heading passes")
    if empty_heading_errors("<h3>Team orders</h3>", "head"):
        raise SystemExit("Heading self-test flagged a real heading")
    fail_check(
        "copy button mismatch",
        copy_button_errors("Athlete Perks Code: <strong>COACHSU10</strong> writeText('DALLAS10')", "copy"),
        "COACHSU10",
    )
    self_tests.append("copy button match passes")
    if copy_button_errors("Athlete Perks Code: <strong>DALLAS10</strong> writeText('DALLAS10')", "copy"):
        raise SystemExit("Copy-button self-test flagged a matching code")
    fail_check("json doubled word", doubled_word_errors("lightweight breathable breathable tech shirt", "md"), "breathable")
    bad_list = code_list_errors("const PROMO_CODES = { DALLAS10: { pct: 25, label: 'x' } }", "list")
    fail_check("code list percent", bad_list, "25%")
    self_tests.append("JSON-LD code scan")
    ld = '<script type="application/ld+json">{"text":"use promo SAVE20"}</script>'
    if not jsonld_code_errors(ld, "ld"):
        raise SystemExit("JSON-LD self-test missed SAVE20")
    fail_check(
        "generator forbidden code",
        generator_text_errors("sticky " + NEVER_DISPLAY_CODES[0] + " banner", "generator.py"),
        "contains",
    )
    assert_restored_sections.self_test_count = len(self_tests)
    folder = os.path.join(BASE_DIR, "products")
    guide_total = 0
    errors = []
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".html"):
            continue
        page = open(os.path.join(folder, name), encoding="utf-8", errors="replace").read()
        guide_total += _guide_link_count(page)
        errors.extend(guide_link_errors(page, name))
        errors.extend(paired_section_errors(page, name))
        errors.extend(cross_sell_errors(page, name))
        if name in {"apex-8-station-race-day-tactical-duffle.html", "apc-c14.html"}:
            errors.extend(duffle_claim_errors(page, name))
        errors.extend(lowercase_spec_bullets(page) and [f"{name}: spec bullet starts lowercase ({lowercase_spec_bullets(page)[0][:60]})"])
        errors.extend(regression_errors(page, name))
    for name in ("compromised-running.html", "apc-c36.html"):
        page = open(os.path.join(folder, name), encoding="utf-8").read()
        errors.extend(c36_section_errors(page, name))
        for marker in (
            "Frequently Paired",
            "Related HYROX",
            "Add to Bag",
            "Print errors and defects are replaced or refunded",
            "Fabric: 100% ring-spun cotton, 6.1 oz, relaxed fit.",
        ):
            if marker not in page:
                errors.append(f"{name}: missing section {marker}")
    tokens = slug_token_count()
    if tokens < SLUG_TOKEN_MINIMUM:
        raise SystemExit(f"Slug-token count {tokens} is below the published baseline {SLUG_TOKEN_MINIMUM}")
    short = slug_page_shortfall(SLUG_PAGE_BASELINE, slug_page_counts())
    if short:
        raise SystemExit("Slug tokens dropped on a published file:\n" + "\n".join(short[:40]))
    # The same names must not survive in articles, collection pages, or feeds.
    for dirpath, dirnames, filenames in os.walk(BASE_DIR):
        dirnames[:] = [item for item in dirnames if item not in {".git", "__pycache__", "node_modules"}]
        for name in filenames:
            if not name.endswith((".html", ".xml", ".csv", ".js", ".json", ".txt", ".md")):
                continue
            path = os.path.join(dirpath, name)
            text = open(path, encoding="utf-8", errors="replace").read()
            surface = _surface_text(text) if name.endswith(".html") else re.sub(r"https?://\S+", " ", text)
            rel = os.path.relpath(path, BASE_DIR)
            if name.endswith(".js"):
                errors.extend(never_display_errors(text, rel))
                errors.extend(code_list_errors(text, rel))
                errors.extend(promoish_errors(text, rel))
                errors.extend(code_percent_errors(text, rel))
                errors.extend(offer_percent_errors(text, rel))
            if name.endswith(".html"):
                errors.extend(twitter_garble_errors(text, rel))
                errors.extend(og_repeat_errors(text, rel))
                errors.extend(blank_code_errors(text, rel))
                errors.extend(promo_code_errors(text, rel))
                errors.extend(never_display_errors(text, rel))
                errors.extend(duplicate_perk_code_errors(text, rel))
                errors.extend(jsonld_code_errors(text, rel))
                errors.extend(promoish_errors(text, rel))
                errors.extend(code_percent_errors(text, rel))
                errors.extend(offer_percent_errors(text, rel))
                errors.extend(empty_heading_errors(text, rel))
                errors.extend(copy_button_errors(text, rel))
                errors.extend(code_list_errors(text, rel))
                if rel.startswith("articles/"):
                    errors.extend(doubled_word_errors(text, rel))
                for match in re.finditer(
                    r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', text, flags=re.S | re.I
                ):
                    for desc in re.finditer(r'"description"\s*:\s*"((?:\\.|[^"\\])*)"', match.group(1)):
                        value = json.loads('"' + desc.group(1) + '"')
                        if _starts_lowercase(value):
                            errors.append(f"{os.path.relpath(path, BASE_DIR)}: JSON-LD description starts lowercase")
            elif name.endswith((".xml", ".csv", ".json", ".txt", ".md")):
                errors.extend(blank_code_errors(text, rel))
                errors.extend(promo_code_errors(text, rel))
                errors.extend(never_display_errors(text, rel))
                errors.extend(duffle_claim_errors(text, rel))
                if name.endswith(".md"):
                    errors.extend(md_prose_errors(text, rel))
                    errors.extend(doubled_word_errors(text, rel))
                if name.endswith(".json"):
                    for chunk in public_copy_chunks(name, text):
                        errors.extend(doubled_word_errors(chunk, rel))
                errors.extend(promoish_errors(text, rel))
                errors.extend(code_percent_errors(text, rel))
                errors.extend(offer_percent_errors(text, rel))
                for chunk in public_copy_chunks(name, text):
                    for hit in sitewide_garble_hits(chunk):
                        errors.append(f"{rel}: public copy has {hit}")
                        break
            for title in OLD_HEAVY_LISTING_NAMES:
                if title.lower() in surface.lower():
                    errors.append(f"{os.path.relpath(path, BASE_DIR)}: old listing name {title}")
            if _DANGLING_PREP.search(surface) and name.endswith(".html"):
                errors.append(f"{os.path.relpath(path, BASE_DIR)}: dangling preposition fragment")
            if "in./yd" in surface:
                errors.append(f"{os.path.relpath(path, BASE_DIR)}: broken unit in./yd")
            if "It is part of the Apex Hybrid Co. catalog." in surface:
                errors.append(f"{os.path.relpath(path, BASE_DIR)}: catalog filler")
    errors.extend(generator_source_errors())
    if errors:
        raise SystemExit("Restored-section checks failed:\n" + "\n".join(errors[:60]))


def assert_published_xml_parses():
    """Fail the build if any published XML file does not parse."""
    assert_no_trademark()
    assert_listed_prices()
    assert_fabric_stated_once()
    assert_no_garbled_copy()
    assert_sitewide_garble()
    assert_copy_quality()
    assert_restored_sections()
    import xml.etree.ElementTree as ET
    errors = []
    for dirpath, dirnames, filenames in os.walk(BASE_DIR):
        dirnames[:] = [name for name in dirnames if name not in {".git", "__pycache__"}]
        for name in filenames:
            if not name.endswith(".xml"):
                continue
            path = os.path.join(dirpath, name)
            try:
                ET.parse(path)
            except ET.ParseError as exc:
                errors.append(f"{os.path.relpath(path, BASE_DIR)}: {exc}")
    if errors:
        raise SystemExit("XML parse failed:\n" + "\n".join(errors))


PRICE_FIELD_RE = re.compile(r"^\d+\.\d{2} USD$")
IMAGE_LINK_RE = re.compile(r"^https?://\S+$")


def assert_published_csv_feeds():
    """Fail the build if a CSV feed row is the wrong width or has a bad price or image."""
    errors = []
    for dirpath, dirnames, filenames in os.walk(BASE_DIR):
        dirnames[:] = [name for name in dirnames if name not in {".git", "__pycache__"}]
        for name in filenames:
            if not name.endswith(".csv"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, BASE_DIR)
            with open(path, newline="", encoding="utf-8") as handle:
                rows = list(csv.reader(handle))
            if not rows:
                errors.append(f"{rel}: empty CSV")
                continue
            header = rows[0]
            width = len(header)
            price_at = header.index("price") if "price" in header else None
            image_at = header.index("image_link") if "image_link" in header else None
            if "feed" in name.lower() and (price_at is None or image_at is None):
                errors.append(f"{rel}: header is missing price or image_link")
            for line_no, row in enumerate(rows[1:], start=2):
                if len(row) != width:
                    errors.append(f"{rel}:{line_no}: {len(row)} columns, header has {width}")
                    continue
                if price_at is not None and not PRICE_FIELD_RE.fullmatch(row[price_at].strip()):
                    errors.append(f"{rel}:{line_no}: malformed price {row[price_at]!r}")
                if image_at is not None and not IMAGE_LINK_RE.fullmatch(row[image_at].strip()):
                    errors.append(f"{rel}:{line_no}: malformed image_link {row[image_at]!r}")
    if errors:
        raise SystemExit("CSV feed check failed:\n" + "\n".join(errors))

with open(os.path.join(BASE_DIR, "catalog.json"), "r", encoding="utf-8") as f:
    catalog = json.load(f)

products = [p for p in catalog["products"] if str(p.get("id", "")).startswith("APC-C")]
guides = catalog["guides"]
product_by_id = {p["id"]: p for p in products}
fw_slugs_map = {}
for _p in products:
    _u = _p.get("fourthwall_product_url") or ""
    _vid = _p.get("fourthwall_default_variant_id") or ""
    if _u and _vid:
        _slug = _u.split("?")[0].rstrip("/").split("/")[-1]
        fw_slugs_map[_slug] = _vid


os.makedirs(os.path.join(BASE_DIR, "products"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "articles"), exist_ok=True)


def google_category_for(prod):
    dept = prod.get("dept", "")
    category = prod.get("category", "")
    # Headwear is a clothing accessory. Do not bury it under the Training Gear
    # department's Sporting Goods bucket. Gym bags stay non-apparel.
    if category == "Headwear":
        return "Apparel & Accessories > Clothing Accessories > Hats"
    if dept in ("Tees & Pump Covers", "Breathable Tech Shirts", "Race City Editions", "Muscle Tanks"):
        return "Apparel & Accessories > Clothing > Shirts & Tops"
    if dept == "Hoodies":
        # Google's taxonomy has no "Sweatshirts & Hoodies" node; hoodies and
        # sweatshirts belong under Shirts & Tops (212).
        return "Apparel & Accessories > Clothing > Shirts & Tops"
    if dept in ("Lightweight Jackets", "Race Day Windbreakers", "Windbreakers"):
        return "Apparel & Accessories > Clothing > Outerwear > Coats & Jackets"
    if dept == "Shoes":
        return "Apparel & Accessories > Shoes > Athletic Shoes"
    if dept == "Training Gear":
        return "Sporting Goods > Exercise & Fitness"
    return "Health & Beauty > Health Care > Massage & Relaxation"


# Fourthwall names the sublimation blank "White". These towels are not white.
BLANK_COLOR_OVERRIDE = {
    "APC-C138": "Black",
    "APC-C139": "Deep Olive",
}
RETIRED_CART_IDS = {"APC-C15", "APC-C35"}

_FABRIC_CLAUSE = re.compile(
    r"(?i)(?:\d+(?:\.\d+)?\s+oz|heavyweight\s+fabric|lightweight\s+fabric|"
    r"midweight\s+fabric|ring-spun|airlume)"
)


def normalize_fabric_copy(text):
    """Use the real fabric, and never call a 6.1 oz tee heavyweight."""
    if not text:
        return text
    text = text.replace(
        "100% ring-spun cotton, heavyweight fabric (6.1 oz), relaxed fit",
        "100% ring-spun cotton, 6.1 oz, relaxed fit",
    )
    text = text.replace(
        "100% ring-spun cotton. Heavyweight fabric (6.1 oz). Relaxed fit.",
        "100% ring-spun cotton, 6.1 oz, relaxed fit.",
    )
    text = re.sub(r"(?i)heavyweight fabric \(6\.1 oz\)", "6.1 oz ring-spun cotton", text)
    text = re.sub(r"(?i)6\.1 oz heavyweight", "6.1 oz", text)
    text = re.sub(r"(?i)heavyweight fabric \(6 oz\)", "6 oz", text)
    text = re.sub(r"(?i)\bBlack heavyweight tee\b", "Black tee", text)
    text = re.sub(r"(?i)\bA heavyweight tee\b", "A tee", text)
    return text


def strip_fabric_clauses(text):
    """Remove fabric and weight sentences so the bullets can state them once."""
    text = normalize_fabric_copy(text)
    if not text:
        return ""
    kept = [
        part
        for part in re.split(r"(?<=[.?!])\s+", text)
        if part and not _FABRIC_CLAUSE.search(part)
    ]
    return re.sub(r"\s{2,}", " ", " ".join(kept)).strip()


def published_variant_map(prod):
    """Variant map for a product page. Towel blanks named White use the real color."""
    variants = prod.get("fourthwall_variants") or {}
    if not isinstance(variants, dict):
        return {}
    override = BLANK_COLOR_OVERRIDE.get(prod.get("id"))
    if override:
        sizes = variants.get(override) or variants.get("White") or variants.get("Black")
        if isinstance(sizes, dict):
            return {override: sizes}
        return {}
    return black_only_variant_map(variants)


def strip_retired_cart_script(html):
    """Retired pages keep their note. They do not keep a cart or a fallback product."""

    def repl(match):
        block = match.group(0)
        if "var prodVariants" not in block and "fallbackUrl" not in block and "syncAddLink" not in block:
            return block
        pid = re.search(r'var prodId = "([^"]+)"', block)
        pid = pid.group(1) if pid else ""
        return (
            "<script>\n  (function(){\n    try {\n"
            '      var isBot = /bot|crawl|spider|slurp|headless|lighthouse/i.test(navigator.userAgent || "");\n'
            "      if (isBot) return;\n"
            '      var ns = "https://abacus.jasoncameron.dev/hit/apexhybridco.com";\n'
            f'      ["pageviews_total","product_views_total","view_{pid}"].forEach(function(k){{\n'
            '        fetch(ns + "/" + k, {method:"GET", mode:"cors", keepalive:true, cache:"no-store"}).catch(function(){});\n'
            "      });\n    } catch (e) {}\n  })();\n  </script>"
        )

    return re.sub(r"<script>\s*\(function\(\)\{.*?\}\)\(\);\s*</script>", repl, html, flags=re.S)


def generate_product_pages(only_ids=None):
    for prod in products:
        if only_ids is not None and prod["id"] not in only_ids:
            continue
        handle = prod["handle"]
        title = prod["title"]
        seo_title = prod.get("seo_title", f"{title}  -  HYROX & Hybrid Race Gear")
        price = f"{prod['retail_price']:.2f}"
        list_price = f"{(prod.get('list_price') or prod['retail_price']):.2f}"
        img_url = f"{SITE_URL}/{prod['image']}"
        canonical = f"{SITE_URL}/products/{handle}.html"
        raw_desc = prod["short_desc"]
        fabric = fabric_bullet_for(prod)
        highlights = []
        for item in prod.get("highlights", []):
            lowered = (item or "").lower()
            if lowered.startswith("blank quality") or lowered.startswith("blank options") or lowered.startswith("fabric:"):
                continue
            cleaned = scrub_fabric_text(item)
            if not cleaned:
                continue
            highlights.append(cleaned)
        highlights.insert(0, f"Fabric: {fabric}")
        short_desc = ensure_story(scrub_fabric_text(raw_desc))
        dept = prod["dept"]

        related = [p for p in products if p["dept"] == dept and p["id"] != prod["id"]][:4]
        if len(related) < 4:
            related += [p for p in products if p["id"] != prod["id"] and p not in related][: (4 - len(related))]

        json_ld = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
                        {"@type": "ListItem", "position": 2, "name": dept, "item": f"{SITE_URL}/?dept={html.escape(dept)}"},
                        {"@type": "ListItem", "position": 3, "name": title, "item": canonical},
                    ],
                },
                {
                    "@type": "Product",
                    "@id": f"{canonical}#product",
                    "name": seo_title,
                    "sku": prod["id"],
                    "mpn": prod["id"],
                    "image": [img_url]
                    + ([f"{SITE_URL}/{prod['alt_image']}"] if prod.get("alt_image") else [])
                    + [f"{SITE_URL}/{extra}" for extra in (prod.get("extra_images") or [])],
                    "description": short_desc,
                    "keywords": f"HYROX shirts, breathable HYROX race shirt, {title}, {dept}, hybrid athlete apparel, 8-station functional fitness gear",
                    "brand": {"@type": "Brand", "name": "Apex Hybrid Co"},
                    "category": dept,
                    "offers": {
                        "@type": "Offer",
                        "url": canonical,
                        "priceCurrency": "USD",
                        "price": price,
                        "priceValidUntil": "2027-12-31",
                        "availability": "https://schema.org/InStock",
                        "itemCondition": "https://schema.org/NewCondition",
                        "seller": {"@type": "Organization", "name": "Apex Hybrid Co., operated by NolCorp LLC"},
                        "shippingDetails": {
                            "@type": "OfferShippingDetails",
                            "shippingRate": {"@type": "MonetaryAmount", "value": "0.00", "currency": "USD"},
                            "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "US"},
                            "deliveryTime": {
                                "@type": "ShippingDeliveryTime",
                                "handlingTime": {"@type": "QuantitativeValue", "minValue": 3, "maxValue": 5, "unitCode": "DAY"},
                            },
                        },
                        "hasMerchantReturnPolicy": {
                            "@type": "MerchantReturnPolicy",
                            "applicableCountry": "US",
                            "returnPolicyCategory": "https://schema.org/MerchantReturnNotPermitted",
                        },
                    },
                },
            ],
        }
        if prod.get("id") in RACE_DAY_HANDLING_IDS:
            handling = json_ld["@graph"][1]["offers"]["shippingDetails"]["deliveryTime"]["handlingTime"]
            handling["minValue"] = 10
            handling["maxValue"] = 14
        priced_for_schema = fourthwall_size_prices(prod)
        if len({amount for _, amount in priced_for_schema}) > 1:
            base_offer = json_ld["@graph"][1]["offers"]
            schema_offers = []
            for size, amount in priced_for_schema:
                offer = json.loads(json.dumps(base_offer))
                offer["price"] = f"{amount:.2f}"
                offer["name"] = f"{title} - {size}"
                offer["sku"] = f"{prod['id']}-{size}"
                schema_offers.append(offer)
            json_ld["@graph"][1]["offers"] = {
                "@type": "AggregateOffer",
                "lowPrice": f"{min(amount for _, amount in priced_for_schema):.2f}",
                "highPrice": f"{max(amount for _, amount in priced_for_schema):.2f}",
                "priceCurrency": "USD",
                "offerCount": len(schema_offers),
                "offers": schema_offers,
            }

        highlights_html = "\n".join(f"<li>{html.escape(h)}</li>" for h in highlights)
        related_html = "\n".join(
            f"""
            <a href="{r['handle']}.html" class="ProductCard" style="text-decoration:none; color:inherit;">
              <div class="ProductCard__Media" style="height:180px;">
                <img src="../{r['image']}" alt="{html.escape(r['title'])}" loading="lazy" />
              </div>
              <div class="ProductCard__Body">
                <div class="ProductCard__Category">{html.escape(r['category'])}</div>
                <div class="ProductCard__Title" style="font-size:14px;">{html.escape(r['title'])}</div>
                <div class="ProductCard__PriceRow">
                  <span class="PriceWhole" style="font-size:18px;">${r['retail_price']:.2f}</span>
                </div>
              </div>
            </a>
            """
            for r in related
        )

        is_fw = str(prod.get("id", "")).startswith("APC-C") or prod.get("fulfillment_partner") == "Fourthwall"
        if is_fw:
            fw_blank = html.escape(prod.get("fourthwall_blank") or "Premium Athletic Blank")
            fw_url = prod.get("fourthwall_product_url") or prod.get("checkout_url") or f"../index.html?buy={prod['id']}&fulfillment=fourthwall"
            fulfillment_line = f'<div style="font-size:12.5px; color:#0f172a; font-weight:700; margin-top:6px; background:#f1f5f9; padding:8px 10px; border-radius:6px; border-left:3px solid #2563eb;">✓ Made to order. Free US shipping. Secure checkout and fulfillment by Fourthwall. <a href="{html.escape(fw_url)}" style="color:#2563eb;text-decoration:underline;">Instant 1-Click Checkout →</a></div>'
            buy_href = fw_url
            top_buy_label = f"Instant Checkout (${price})"
            main_buy_label = "Buy Now  -  Instant Checkout"
        else:
            fulfillment_line = f'<div style="font-size:12.5px; color:#0f172a; font-weight:700; margin-top:6px; background:#f0fdf4; padding:8px 10px; border-radius:6px; border-left:3px solid #16a34a;">✓ Made to order. Free US shipping</div>'
            buy_href = f"../index.html?buy={prod['id']}"
            top_buy_label = f"Quick Checkout (${price})"
            main_buy_label = "Instant Stripe Checkout"

        race_day_ids = {"APC-C46", "APC-C47", "APC-C48", "APC-C49", "APC-C50"}
        priced_sizes = fourthwall_size_prices(prod)
        if priced_sizes:
            size_names = [sz for sz, _ in priced_sizes]
        else:
            size_order = ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"]
            if prod.get("id") in race_day_ids:
                known = list((prod.get("fourthwall_variants") or {}).keys())
                size_names = [sz for sz in size_order if sz in known]
            elif prod.get("has_sizes"):
                size_names = ["S", "M", "L", "XL", "2XL"]
            else:
                size_names = []
        size_price_map = {sz: price for sz, price in priced_sizes}

        def _size_btn(sz, active=False):
            border = "2px solid #0f172a" if active else "1.5px solid #cbd5e1"
            bg = "#0f172a" if active else "#fff"
            color = "#fff" if active else "#0f172a"
            return (
                f'<button type="button" class="StaticSizeBtn" data-size="{sz}" '
                f'onclick="window.selectStaticSize(\'{sz}\',this)" '
                f'style="cursor:pointer; min-width:44px; padding:8px 12px; border-radius:6px; '
                f'border:{border}; background:{bg}; color:{color}; font-weight:800; font-size:13px;">{sz}</button>'
            )

        size_buttons = "\n              ".join(_size_btn(sz, sz == "L") for sz in size_names)
        extra_gallery_html = ""
        for idx, path in enumerate(prod.get("extra_images") or [], start=3):
            label = "Worn" if idx == 3 else "Worn, plain back"
            extra_gallery_html += (
                f'<button type="button" onclick="document.getElementById(\'staticMainProdImg\').src=\'../{path}\'" '
                f'style="cursor:pointer; border:2px solid #cbd5e1; border-radius:8px; padding:6px; background:#f8fafc; color:#0f172a; display:flex; align-items:center; gap:8px; font-weight:700; font-size:12.5px;">'
                f'<img src="../{path}" alt="{html.escape(title)} {html.escape(label)}" style="width:48px; height:48px; object-fit:cover; border-radius:4px;" />'
                f'<span>{idx}. {html.escape(label)}</span></button>'
            )
        ship_note_html = ""
        if prod.get("id") in race_day_ids:
            denver_display = "block" if prod.get("id") == "APC-C47" else "none"
            ship_note_html = (
                '<p id="raceDayShipNote" style="font-size:13.5px; color:#0f172a; font-weight:700; margin:8px 0 0; line-height:1.45;">'
                "Made to order. Ships from overseas and arrives in about 10–14 business days. Free US shipping.</p>"
                f'<p id="raceDayDenverNote" style="font-size:13.5px; color:#0f172a; font-weight:800; margin:6px 0 0; line-height:1.45; display:{denver_display};">'
                "Won't arrive before Denver race weekend (Nov 12–15).</p>"
            )
        elif prod.get("id") in STITCHED_RACE_IDS:
            ship_note_html = (
                '<p id="usShipNote" style="font-size:13.5px; color:#0f172a; font-weight:700; margin:8px 0 0; line-height:1.45;">'
                + STITCHED_SHIP_LINE + "</p>"
            )
        elif prod.get("id") in NA_PACKABLE_IDS:
            ship_note_html = (
                '<p id="usShipNote" style="font-size:13.5px; color:#0f172a; font-weight:700; margin:8px 0 0; line-height:1.45;">'
                + NA_SHIP_LINE + "</p>"
            )
        else:
            ship_note_html = (
                '<p id="usShipNote" style="font-size:13.5px; color:#0f172a; font-weight:700; margin:8px 0 0; line-height:1.45;">'
                "Made to order. Ships from the US and arrives in about 7–10 business days. Free US shipping.</p>"
            )

        page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" href="/favicon.ico" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(seo_title)} | Apex Hybrid Co., operated by NolCorp LLC</title>
  <meta name="description" content="{html.escape(short_desc)} Made to order. Free US shipping from Apex Hybrid Co." />
  <meta name="keywords" content="hyrox shirts, breathable hyrox shirt, {html.escape(title)}, {html.escape(prod['category'])}, {html.escape(dept)}, hybrid athlete gear, functional fitness recovery" />
  <link rel="canonical" href="{canonical}" />
  <meta property="og:type" content="product" />
  <meta property="og:title" content="{html.escape(seo_title)} | Apex Hybrid Co." />
  <meta property="og:description" content="{html.escape(short_desc)}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="{img_url}" />
  <meta property="og:site_name" content="Apex Hybrid Co." />
  <meta property="product:price:amount" content="{price}" />
  <meta property="product:price:currency" content="USD" />
  <meta property="product:availability" content="in stock" />
  <meta property="og:availability" content="instock" />
  <meta property="product:condition" content="new" />
  <meta property="product:brand" content="Apex Hybrid Co." />
  <meta property="product:retailer_item_id" content="{prod['id']}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{html.escape(seo_title)}" />
  <meta name="twitter:description" content="{html.escape(short_desc)}" />
  <meta name="twitter:image" content="{img_url}" />
  <link rel="stylesheet" href="../styles.css?v=20261026v3" />
  <script type="application/ld+json">
{json.dumps(json_ld, indent=2)}
  </script>
</head>
<body>
  <header class="TopHeader">
    <div class="TopHeader__Main">
      <div class="Container TopHeader__Inner">
        <a href="../index.html" class="BrandLogo">
          <span class="BrandLogo__Mark">APEX</span>
          <span class="BrandLogo__Sub">HYBRID CO.</span>
        </a>
        <div style="margin-left:auto; display:flex; gap:14px; align-items:center;">
          <a href="../index.html" style="color:#fff; font-size:13px; font-weight:700;">← Back to Full Catalog &amp; News Hub</a>
          <a href="{buy_href}" class="Btn Btn--BuyNow" style="width:auto; padding:8px 16px;">{top_buy_label}</a>
        </div>
      </div>
    </div>
  </header>

  <main class="Container" style="padding:28px 20px 60px;">
    <nav aria-label="Breadcrumb" style="font-size:12.5px; color:#555; margin-bottom:18px;">
      <a href="../index.html" style="color:#0066ff; font-weight:700;">Home</a> ›
      <a href="../index.html?dept={html.escape(dept)}" style="color:#0066ff; font-weight:700;">{html.escape(dept)}</a> ›
      <span>{html.escape(title)}</span>
    </nav>

    <div class="ProdModalGrid" style="background:#fff; border:1px solid #e4e6eb; border-radius:12px; padding:28px;">
      <div class="ProdModalMedia" style="display:flex; flex-direction:column; gap:12px;">
        <img id="staticMainProdImg" src="../{prod['image']}" alt="{html.escape(seo_title)}" style="width:100%; border-radius:10px; object-fit:contain; max-height:480px; background:#0b0f17;" />
        {f'''<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
          <button type="button" onclick="document.getElementById('staticMainProdImg').src='../{prod['image']}'" style="cursor:pointer; border:2px solid #0066ff; border-radius:8px; padding:6px; background:#0f172a; color:#fff; display:flex; align-items:center; gap:8px; font-weight:700; font-size:12.5px;">
            <img src="../{prod['image']}" alt="{html.escape(title)}  -  Primary View" style="width:48px; height:48px; object-fit:cover; border-radius:4px;" />
            <span>1. Front</span>
          </button>
          <button type="button" onclick="document.getElementById('staticMainProdImg').src='../{prod['alt_image']}'" style="cursor:pointer; border:2px solid #cbd5e1; border-radius:8px; padding:6px; background:#f8fafc; color:#0f172a; display:flex; align-items:center; gap:8px; font-weight:700; font-size:12.5px;">
            <img src="../{prod['alt_image']}" alt="{html.escape(title)} back view" style="width:48px; height:48px; object-fit:cover; border-radius:4px;" />
            <span>2. Black Edition</span>
          </button>
          {extra_gallery_html}
        </div>''' if prod.get("alt_image") else ""}
      </div>
      <div>
        <div style="font-size:11.5px; font-weight:800; color:#0066ff; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px;">
          {html.escape(dept)} · {html.escape(prod['category'])}
        </div>
        <h1 style="font-size:24px; line-height:1.25; margin-bottom:10px;">{html.escape(title)}</h1>
        <div style="padding:12px 0; border-top:1px solid #eee; border-bottom:1px solid #eee; margin-bottom:14px;">
          <div style="display:flex; align-items:baseline; gap:10px;">
            <span id="staticPrice" style="font-size:28px; font-weight:900;">${price}</span>
          </div>
          <div style="font-size:13px; color:#0e8345; font-weight:700; margin-top:4px;">
            ✓ {html.escape(prod['stock_status'])} · {html.escape(prod['ship_time'])}
          </div>
          {ship_note_html}
          {fulfillment_line}
        </div>
        <div id="staticVariantBox" style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:14px 16px; margin-bottom:16px;">

          {f"""<div style="margin-bottom:14px;">
            <div style="font-size:11.5px; font-weight:800; text-transform:uppercase; letter-spacing:0.05em; color:#0f172a; margin-bottom:6px;">Select Size (Unisex Athletic Fit): <span id="staticSizeLabel" style="color:#0066ff;">L</span></div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
              {size_buttons}
            </div>
          </div>""" if prod.get("has_sizes") else ""}
          <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <button type="button" id="staticBuyNowBtn" data-buy="{prod['id']}" onclick="window.launchStaticCheckout(this)" class="Btn Btn--BuyNow" style="flex:1.4; min-width:220px; padding:14px 20px; font-size:14.5px; font-weight:900; text-align:center; cursor:pointer; border:none;">Buy Now - Instant Checkout · ${price} →</button>
            <a id="staticAddBagLink" href="../index.html?add={prod['id']}&size=L&color=Black" class="Btn Btn--Cart" style="flex:1; min-width:150px; padding:14px 18px; font-size:14px; font-weight:800; text-align:center;">Add to Bag · ${price}</a>
          </div>
        </div>
        <p style="font-size:14.5px; color:#222; line-height:1.6; margin-bottom:14px;">{html.escape(short_desc)}</p>
        <h2 style="font-size:14px; text-transform:uppercase; letter-spacing:0.05em; color:#444; margin-bottom:6px;">Key Performance Specifications</h2>
        <ul class="HighlightsList">
          {highlights_html}
        </ul>
        <div style="margin:14px 0; padding:14px 16px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; font-size:13.5px; color:#1e293b; line-height:1.55;">
          <div style="font-weight:800; color:#0f172a; text-transform:uppercase; letter-spacing:0.04em; font-size:12px; margin-bottom:6px;">✓ Fit and Race-Day Guarantee</div>
          <div>Made to order. Free US shipping. Print errors and defects are replaced or refunded. Secure checkout and fulfillment by Fourthwall.</div>
        </div>
        <div style="display:flex; gap:10px; margin-top:16px; flex-wrap:wrap;">
          <a href="../index.html?add={prod['id']}" class="Btn Btn--Cart" style="padding:13px 22px; font-size:14px; text-align:center;">Add to Bag  -  ${price}</a>
          <a href="{buy_href}" class="Btn Btn--BuyNow" style="padding:13px 22px; font-size:14px; text-align:center;">{main_buy_label}</a>
        </div>
        <div style="margin-top:16px;background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:#f8fafc;border:1.5px solid #0066ff;border-radius:10px;padding:14px 16px;">
          <p style="font-size:12.5px;color:#cbd5e1;margin:0 0 10px;line-height:1.45;">Made to order. Free US shipping. Secure checkout and fulfillment by Fourthwall.</p>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <a href="../team_orders.html" style="background:#0066ff;color:#fff;text-decoration:none;padding:6px 11px;border-radius:6px;font-size:12px;font-weight:800;">Team orders</a>
            <a href="../wristband.html" style="background:#0f172a;border:1px solid #475569;color:#fff;text-decoration:none;padding:6px 11px;border-radius:6px;font-size:12px;font-weight:800;">⏱️ Free Printable Split Wristband</a>
            <a href="../gyms/index.html" style="background:#0f172a;border:1px solid #475569;color:#38bdf8;text-decoration:none;padding:6px 11px;border-radius:6px;font-size:12px;font-weight:800;">🏋️ HYROX Gym Finder (72 Hubs)</a>
          </div>
        </div>
      </div>
    </div>

    <section style="margin-top:42px;">
      <h2 style="font-size:20px; margin-bottom:16px;">Frequently Paired {html.escape(dept)} &amp; HYROX Prep Gear</h2>
      <div class="ProductGrid">
        {related_html}
      </div>
    </section>

    <section style="margin-top:36px; background:#fff; border:1px solid #e4e6eb; border-radius:12px; padding:24px;">
      <h2 style="font-size:18px; margin-bottom:12px;">Related HYROX Training, Pacing &amp; Recovery Buyer Guides</h2>
      <ul style="padding-left:20px; line-height:1.9; font-size:14px;">
        {chr(10).join(
            f'<li><a href="../articles/{g["slug"]}.html" style="color:#0066ff; font-weight:700;">{html.escape(g["title"])}</a>  -  <span style="color:#475569;">{html.escape(g["category"])} ({html.escape(g["read_time"])})</span></li>'
            for g in (
                [x for x in guides if prod["id"] in x.get("recommended_skus", [])]
                + [x for x in guides if prod["id"] not in x.get("recommended_skus", [])]
            )[:6]
        )}
      </ul>
    </section>
  </main>

  <footer class="SiteFooter">
    <div class="Container">
      <p><strong>Apex Hybrid Co., operated by NolCorp LLC</strong> · <a href="../contact.html">Contact</a> · <a href="../about.html">About</a> · <a href="../shipping.html">Shipping</a> · <a href="../returns.html">Returns</a> · <a href="../privacy.html">Privacy</a> · <a href="../terms.html">Terms</a> · <a href="mailto:apexhybridco@gmail.com" style="color:#38bdf8;">apexhybridco@gmail.com</a> · <a href="../index.html" style="color:#38bdf8;">Return to Storefront</a></p>
      <p style="font-size:11.5px; color:#94a3b8; margin-top:8px;">Apex Hybrid Co., operated by NolCorp LLC is an independent athletic &amp; recovery brand engineered for athletes competing in HYROX, DEKA, CrossFit, and functional fitness events. Not affiliated with or endorsed by HYROX World GmbH.</p>
    </div>
  <div id="apexStickyPromoBar" style="position:fixed;bottom:0;left:0;right:0;z-index:90;background:linear-gradient(90deg,#0f172a 0%,#1e293b 55%,#0f172a 100%);color:#f8fafc;border-top:2px solid #0066ff;padding:9px 14px;box-shadow:0 -6px 24px rgba(0,0,0,0.38);font-family:system-ui,-apple-system,sans-serif;">
    <div style="max-width:1240px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 14px;font-size:12.5px;">
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <span style="background:#0066ff;color:#fff;font-weight:900;font-size:10.5px;padding:3px 8px;border-radius:999px;text-transform:uppercase;letter-spacing:0.07em;">Shipping</span>
        <span>Free US shipping. Secure checkout and fulfillment by Fourthwall.</span>
        
      </div>
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <a href="../wristband.html" style="background:#0066ff;color:#fff;text-decoration:none;padding:5px 11px;border-radius:6px;font-weight:800;font-size:12px;">⏱️ Free Printable Split Wristband →</a>
        <a href="../gyms/index.html" style="background:#1e293b;border:1px solid #475569;color:#e2e8f0;text-decoration:none;padding:5px 11px;border-radius:6px;font-weight:700;font-size:12px;">🏋️ HYROX Gym Directory (72 Hubs)</a>
        <a href="../team_orders.html" style="color:#38bdf8;text-decoration:none;font-weight:800;font-size:12px;">Doubles 2-Packs →</a>
      </div>
    </div>
  </div>
  </footer>
  <script src="/checkout-code.js"></script>
  <script>
  (function(){{
    var prodId = {json.dumps(prod['id'])};
    var prodVariants = {json.dumps(published_variant_map(prod))};
    var sizePrices = {json.dumps(size_price_map)};
    var defaultVid = {json.dumps(prod.get('fourthwall_default_variant_id', ''))};
    var fallbackUrl = {json.dumps(buy_href)};
    var fwSlugs = {json.dumps(fw_slugs_map)};
    var state = {{
      color: {json.dumps(BLANK_COLOR_OVERRIDE.get(prod["id"], "Black"))},
      size: {json.dumps("L" if prod.get("has_sizes") else "One Size")},
      blank: "Black"
    }};
    function syncAddLink() {{
      var addEl = document.getElementById("staticAddBagLink");
      if (addEl) {{
        addEl.setAttribute("href", "../index.html?add=" + encodeURIComponent(prodId) + "&size=" + encodeURIComponent(state.size) + "&color=" + encodeURIComponent(state.color) + "&blank=" + encodeURIComponent(state.blank));
      }}
    }}
    window.selectStaticColor = function(c, imgSrc, btn) {{
      state.color = c;
      var img = document.getElementById("staticMainProdImg");
      if (img && imgSrc) img.src = imgSrc;
      var lbl = document.getElementById("staticColorLabel");
      if (lbl) lbl.textContent = (c === "White" ? "Black" : "Black");
      var btns = document.querySelectorAll(".StaticColorBtn");
      for (var i = 0; i < btns.length; i++) {{
        var active = btns[i].getAttribute("data-color") === c;
        btns[i].style.background = active ? "#0f172a" : "#fff";
        btns[i].style.color = active ? "#fff" : "#0f172a";
        btns[i].style.border = active ? "2px solid #0f172a" : "1.5px solid #cbd5e1";
      }}
      syncAddLink();
    }};
    window.selectStaticBlank = function(b, btn) {{
      state.blank = b;
      var lbl = document.getElementById("staticBlankLabel");
      if (lbl) lbl.textContent = b;
      var btns = document.querySelectorAll(".StaticBlankBtn");
      for (var i = 0; i < btns.length; i++) {{
        var active = btns[i].getAttribute("data-blank") === b;
        btns[i].style.background = active ? "#0f172a" : "#fff";
        btns[i].style.color = active ? "#fff" : "#0f172a";
        btns[i].style.border = active ? "2px solid #0f172a" : "1.5px solid #cbd5e1";
      }}
      syncAddLink();
    }};
    window.selectStaticSize = function(s, btn) {{
      state.size = s;
      var picked = prodVariants[s];
      var price = (sizePrices && sizePrices[s] != null) ? sizePrices[s] : (picked && picked.price != null ? picked.price : null);
      if (price != null) {{
        var priced = "$" + Number(price).toFixed(2);
        var buy = document.getElementById("staticBuyNowBtn");
        if (buy && buy.textContent.indexOf("$") !== -1) buy.textContent = buy.textContent.replace(/\$[\d.]+/, priced);
        var add = document.getElementById("staticAddBagLink");
        if (add && add.textContent.indexOf("$") !== -1) add.textContent = add.textContent.replace(/\$[\d.]+/, priced);
        var big = document.getElementById("staticPrice");
        if (big) big.textContent = priced;
      }}
      var lbl = document.getElementById("staticSizeLabel");
      if (lbl) lbl.textContent = s;
      var btns = document.querySelectorAll(".StaticSizeBtn");
      for (var i = 0; i < btns.length; i++) {{
        var active = btns[i].getAttribute("data-size") === s;
        btns[i].style.background = active ? "#0f172a" : "#fff";
        btns[i].style.color = active ? "#fff" : "#0f172a";
        btns[i].style.border = active ? "2px solid #0f172a" : "1.5px solid #cbd5e1";
      }}
      syncAddLink();
    }};
    function variantId(val) {{
      if (!val) return "";
      if (typeof val === "object") return val.id || "";
      return val;
    }}
    function getSelectedVariantId() {{
      var map = prodVariants[state.color] || prodVariants["Black"] || prodVariants["Default"];
      if (!map || typeof map !== "object" || map.id) map = prodVariants;
      return variantId(map[state.size]) || variantId(map["L"]) || variantId(map["One Size"]) || variantId(map["One size"]) || defaultVid;
    }}
    function redirectFourthwallVariant(vid, triggerEl, fbHref) {{
      try {{ hit("checkout_clicks_total"); hit("checkout_" + prodId); }} catch (e) {{}}
      if (!vid) {{
        window.location.href = fbHref || fallbackUrl;
        return;
      }}
      var prevText = triggerEl ? triggerEl.textContent : "";
      if (triggerEl) {{
        triggerEl.style.opacity = "0.75";
        triggerEl.textContent = "Opening Secure Checkout…";
      }}
      fetch("https://apex-hybrid-co-shop.fourthwall.com/cart/add.js", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ items: [{{ id: vid, quantity: 1 }}] }})
      }}).then(function(r){{ return r.json(); }}).then(function(d){{
        var cid = d && d.cart && d.cart.id;
        if (!cid) throw new Error("no_cart");
        return fetch("https://apex-hybrid-co-shop.fourthwall.com/api/v2/checkout/cart", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ cartId: cid, cartCurrency: "USD" }})
        }});
      }}).then(function(r){{ return r.json(); }}).then(function(chk){{
        if (chk && chk.id) {{
          apexFinishCheckout(chk.id, function (url) {{ window.location.href = url; }});
        }} else {{
          window.location.href = fbHref || fallbackUrl;
        }}
      }}).catch(function(){{
        if (triggerEl) {{
          triggerEl.textContent = prevText;
          triggerEl.style.opacity = "1";
        }}
        window.location.href = fbHref || fallbackUrl;
      }});
    }}
    window.launchStaticCheckout = function(btn) {{
      redirectFourthwallVariant(getSelectedVariantId(), btn, fallbackUrl);
    }};
    document.addEventListener("click", function(ev){{
      var link = ev.target && ev.target.closest ? ev.target.closest('a[href*="apex-hybrid-co-shop.fourthwall.com/products/"]') : null;
      if (!link) return;
      var href = link.getAttribute("href") || "";
      var slug = href.split("?")[0].replace(/\/+$/, "").split("/").pop();
      var vid = getSelectedVariantId() || fwSlugs[slug];
      if (!vid) return;
      ev.preventDefault();
      redirectFourthwallVariant(vid, link, href);
    }});
    try {{
      var isBot = /bot|crawl|spider|slurp|headless|lighthouse/i.test(navigator.userAgent || "");
      var ns = "https://abacus.jasoncameron.dev/hit/apexhybridco.com";
      var hit = function(k){{
        if (isBot || !k) return;
        try {{ fetch(ns + "/" + k, {{method:"GET", mode:"cors", keepalive:true, cache:"no-store"}}).catch(function(){{}}); }} catch (e) {{}}
        var sendGc = function(){{
          if (window.goatcounter && window.goatcounter.count) {{
            window.goatcounter.count({{path: k, title: k, event: true}});
            return true;
          }}
          return false;
        }};
        if (!sendGc()) {{
          var tries = 0;
          var timer = setInterval(function(){{ tries++; if (sendGc() || tries > 25) clearInterval(timer); }}, 200);
        }}
      }};
      document.addEventListener("click", function(ev){{
        var add = ev.target && ev.target.closest ? ev.target.closest("a[href*='index.html?add=']") : null;
        if (!add) return;
        hit("cart_add_total");
        hit("cart_add_" + prodId);
      }});
      hit("pageviews_total");
      hit("product_views_total");
      hit("view_{prod['id']}");
    }} catch (_) {{}}
  }})();
  </script>
<script data-goatcounter="https://apexhybridco.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</body>
</html>
"""
        if prod["id"] in RETIRED_CART_IDS:
            page_html = strip_retired_cart_script(page_html)
        with open(os.path.join(BASE_DIR, "products", f"{handle}.html"), "w", encoding="utf-8") as out:
            out.write(page_html)
        sku_lower = prod["id"].lower()
        with open(os.path.join(BASE_DIR, "products", f"{sku_lower}.html"), "w", encoding="utf-8") as out_sku:
            out_sku.write(page_html)
        if prod["id"] == "APC-C18":
            with open(os.path.join(BASE_DIR, "products", "apc-c18-anaheim-socal-tee.html"), "w", encoding="utf-8") as out_c18:
                out_c18.write(page_html)


BLOCKED_SHOP_IDS = {"APC-C04", "APC-C39"}
FALLBACK_SHOP_IDS = ("APC-C36", "APC-C28", "APC-C42", "APC-C13", "APC-C11", "APC-C14")


def is_shop_strip_product(prod):
    """Black catalog products only. Never the retired logo SKUs."""
    if not prod or prod.get("id") in BLOCKED_SHOP_IDS:
        return False
    img = (prod.get("image") or "").lower()
    if "black" not in img and "race-day" not in img:
        return False
    return bool(prod.get("fourthwall_product_url") and prod.get("handle"))


def shop_strip_products(rec_skus):
    """First three featured products, then best-fit black fallbacks."""
    picks = []
    seen = set()
    for sku in list(rec_skus or []) + list(FALLBACK_SHOP_IDS):
        if sku in seen:
            continue
        seen.add(sku)
        prod = product_by_id.get(sku)
        if not is_shop_strip_product(prod):
            continue
        picks.append(prod)
        if len(picks) == 3:
            break
    return picks


def shop_the_gear_html(picks, prefix):
    """Compact buy strip. List prices only. No shipping-speed copy."""
    cards = []
    for prod in picks:
        title = html.escape(prod["title"])
        amount = float(prod["retail_price"])
        price = f"${amount:.0f}" if amount == int(amount) else f"${amount:.2f}"
        page = html.escape(f"{prefix}products/{prod['handle']}.html")
        img = html.escape(f"{prefix}{prod['image']}")
        buy = html.escape(prod["fourthwall_product_url"])
        cards.append(
            f"""          <article class="ShopStrip__card">
            <a class="ShopStrip__media" href="{page}"><img src="{img}" alt="{title}" /></a>
            <h3><a href="{page}">{title}</a></h3>
            <p class="ShopStrip__price">{price}</p>
            <div class="ShopStrip__actions">
              <a class="ShopStrip__buy" href="{buy}">Buy · {price}</a>
              <a class="ShopStrip__view" href="{page}">View</a>
            </div>
          </article>"""
        )
    inner = "\n".join(cards)
    return f"""      <section class="ShopStrip" data-shop-strip="gear" aria-label="Shop the gear">
        <style>
          .ShopStrip{{margin:0 0 26px}}
          .ShopStrip h2{{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:#38bdf8;margin:0 0 10px}}
          .ShopStrip__row{{display:flex;gap:12px;overflow-x:auto;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;padding-bottom:4px}}
          .ShopStrip__card{{flex:1 1 0;min-width:210px;scroll-snap-align:start;background:#0b0f17;color:#f8fafc;border:1px solid #1f2937;border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:8px}}
          .ShopStrip__media{{display:block;background:#0b0f17;border-radius:8px;overflow:hidden}}
          .ShopStrip__media img{{width:100%;height:140px;object-fit:contain;background:#0b0f17}}
          .ShopStrip__card h3{{font-size:14px;line-height:1.3;font-weight:800;margin:0}}
          .ShopStrip__card h3 a{{color:#fff;text-decoration:none}}
          .ShopStrip__price{{margin:0;font-size:18px;font-weight:900;color:#fff}}
          .ShopStrip__actions{{display:flex;gap:8px;margin-top:auto}}
          .ShopStrip__buy{{flex:1;text-align:center;background:#0066ff;color:#fff;text-decoration:none;font-weight:800;border-radius:8px;padding:8px 10px;font-size:13px}}
          .ShopStrip__view{{display:inline-flex;align-items:center;justify-content:center;border:1px solid #475569;color:#fff;text-decoration:none;border-radius:8px;padding:8px 10px;font-size:13px;font-weight:700}}
        </style>
        <h2>Shop the gear</h2>
        <div class="ShopStrip__row">
{inner}
        </div>
      </section>"""


def generate_article_pages():
    for art in guides:
        slug = art["slug"]
        title = art["title"]
        cat = art["category"]
        summary = art["summary"]
        canonical = f"{SITE_URL}/articles/{slug}.html"
        rec_skus = art.get("recommended_skus", [])
        shop_strip = shop_the_gear_html(shop_strip_products(rec_skus), "../")
        rec_products = [product_by_id[s] for s in rec_skus if s in product_by_id]
        if not rec_products:
            rec_products = [product_by_id[s] for s in ("APC-C36", "APC-C42", "APC-E01", "APC-E12") if s in product_by_id]

        hero_prod = rec_products[0]
        hero_img = f"{SITE_URL}/{hero_prod['image']}"
        faqs = art.get("faqs", [
            (
                f"What is the top-rated gear for {cat}?",
                f"Our choices include {hero_prod['title']} (${hero_prod['retail_price']:.2f}, SKU {hero_prod['id']}). Made to order. Free US shipping. Secure checkout and fulfillment by Fourthwall."
            ),
            (
                "How do I get 15% off Doubles or multi-item race orders?",
                "Made to order. Free US shipping. Print errors and defects are replaced or refunded. Secure checkout and fulfillment by Fourthwall."
            )
        ])

        json_ld = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Article",
                    "headline": title,
                    "description": summary,
                    "image": hero_img,
                    "author": {"@type": "Organization", "name": "Apex Hybrid Performance Lab"},
                    "publisher": {
                        "@type": "Organization",
                        "name": "Apex Hybrid Co., operated by NolCorp LLC",
                        "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/images/streetwear/apc-c36-black.png?v=20261026v1"},
                    },
                    "datePublished": "2026-10-20",
                    "dateModified": TODAY,
                    "mainEntityOfPage": canonical,
                },
                {
                    "@type": "FAQPage",
                    "mainEntity": [
                        {
                            "@type": "Question",
                            "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a},
                        }
                        for q, a in faqs
                    ],
                },
                {
                    "@type": "ItemList",
                    "name": f"Recommended Gear  -  {title}",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": idx + 1,
                            "item": {
                                "@type": "Product",
                                "name": p["title"],
                                "sku": p["id"],
                                "image": f"{SITE_URL}/{p['image']}",
                                "url": f"{SITE_URL}/products/{p['handle']}.html",
                                "offers": {
                                    "@type": "Offer",
                                    "priceCurrency": "USD",
                                    "price": f"{p['retail_price']:.2f}",
                                    "availability": "https://schema.org/InStock",
                                    "url": f"{SITE_URL}/?buy={p['id']}",
                                },
                            },
                        }
                        for idx, p in enumerate(rec_products)
                    ],
                },
            ],
        }

        top_strip_pills = "\n".join(
            f"""          <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;background:#1e293b;padding:10px 14px;border-radius:8px;border:1px solid #334155;flex-wrap:wrap;">
            <div style="display:flex;align-items:center;gap:12px;min-width:220px;flex:1;">
              <a href="../products/{p['handle']}.html" style="flex-shrink:0;">
                <img src="../{p['image']}" alt="{html.escape(p['title'])}" style="width:52px;height:52px;object-fit:cover;border-radius:6px;border:1px solid #475569;" loading="eager" />
              </a>
              <div style="min-width:0;">
                <a href="../products/{p['handle']}.html" style="color:#fff;font-weight:800;font-size:13.5px;text-decoration:none;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{html.escape(p['title'])}</a>
                <span style="color:#94a3b8;font-size:12px;"><strong style="color:#4ade80;">${p['retail_price']:.2f}</strong> · Free US shipping</span>
              </div>
            </div>
            <div style="display:flex;gap:6px;flex-shrink:0;align-items:center;">
              <a href="{p.get('fourthwall_product_url') or ('../index.html?buy=' + p['id'])}" class="Btn Btn--BuyNow" style="width:auto;padding:8px 14px;font-size:12.5px;font-weight:800;background:#0066ff;color:#fff;border-radius:6px;text-decoration:none;">Buy Now  -  ${p['retail_price']:.2f} (Free US Shipping)</a>
              <a href="../index.html?add={p['id']}" class="Btn Btn--Cart" style="width:auto;padding:8px 10px;font-size:12px;font-weight:700;background:#334155;color:#fff;border-radius:6px;text-decoration:none;">+ Add to Bag</a>
            </div>
          </div>"""
            for p in rec_products[:4]
        )

        rec_html = "\n".join(
            f"""
            <article class="ProductCard" style="display:flex;flex-direction:column;justify-content:space-between;">
              <div>
                <a href="../products/{p['handle']}.html" class="ProductCard__Media" style="height:185px;display:block;">
                  <img src="../{p['image']}" alt="{html.escape(p['title'])}" loading="lazy" />
                </a>
                <div class="ProductCard__Body">
                  <div class="ProductCard__Category">{html.escape(p['category'])}</div>
                  <div class="ProductCard__Title" style="font-size:14.5px;font-weight:800;">
                    <a href="../products/{p['handle']}.html" style="color:inherit;text-decoration:none;">{html.escape(p['title'])}</a>
                  </div>
                  <div class="ProductCard__PriceRow" style="margin:6px 0;">
                    <span class="PriceWhole" style="font-size:19px;font-weight:900;">${p['retail_price']:.2f}</span>
                    <span class="PriceList" style="color:#64748b;font-size:13px;">${(p.get('list_price') or p['retail_price']):.2f}</span>
                  </div>
                  <div style="font-size:12px;color:#0e8345;font-weight:700;margin-bottom:8px;">{article_ship_line(p)}</div>
                </div>
              </div>
              <div style="padding:0 14px 14px;display:flex;flex-direction:column;gap:6px;">
                <a href="{p.get('fourthwall_product_url') or ('../index.html?buy=' + p['id'])}" class="Btn Btn--BuyNow" style="text-align:center;padding:10px 12px;font-weight:800;font-size:13px;background:#0066ff;color:#fff;border-radius:7px;text-decoration:none;">Buy Now  -  ${p['retail_price']:.2f} (Free Shipping)</a>
                <div style="display:flex;gap:6px;">
                  <a href="../index.html?add={p['id']}" class="Btn Btn--Cart" style="flex:1;text-align:center;padding:8px;font-size:12.5px;background:#0f172a;color:#fff;border-radius:6px;text-decoration:none;">+ Add to Bag</a>
                  <a href="../products/{p['handle']}.html" class="Btn Btn--QuickView" style="padding:8px 10px;font-size:12.5px;border:1px solid #cbd5e1;border-radius:6px;text-decoration:none;color:#0f172a;font-weight:700;">Specs</a>
                </div>
              </div>
            </article>
            """
            for p in rec_products
        )

        other_articles_html = "\n".join(
            f'<li><a href="{a["slug"]}.html" style="color:#0066ff; font-weight:700;">{html.escape(a["title"])}</a> <span style="color:#666;">({a["read_time"]})</span></li>'
            for a in guides
            if a["slug"] != slug
        )

        page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" href="/favicon.ico" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)} | Apex Hybrid Co., operated by NolCorp LLC</title>
  <meta name="description" content="{html.escape(summary)}" />
  <meta name="keywords" content="hyrox shirts, breathable hyrox shirt, lightweight warmup jacket, {html.escape(cat)}, hybrid athlete guide, functional race prep, cold plunge recovery" />
  <link rel="canonical" href="{canonical}" />
  <meta property="og:type" content="article" />
  <meta property="og:title" content="{html.escape(title)}" />
  <meta property="og:description" content="{html.escape(summary)}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="{hero_img}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{html.escape(title)}" />
  <meta name="twitter:description" content="{html.escape(summary)}" />
  <meta name="twitter:image" content="{hero_img}" />
  <link rel="stylesheet" href="../styles.css?v=20261026v3" />
  <script type="application/ld+json">
{json.dumps(json_ld, indent=2)}
  </script>
</head>
<body>
  <header class="TopHeader">
    <div class="TopHeader__Main">
      <div class="Container TopHeader__Inner">
        <a href="../index.html" class="BrandLogo">
          <span class="BrandLogo__Mark">APEX</span>
          <span class="BrandLogo__Sub">HYBRID CO.</span>
        </a>
        <div style="margin-left:auto; display:flex; gap:14px; align-items:center; flex-wrap:wrap;">
          <a href="../index.html#articles" style="color:#fff; font-size:13px; font-weight:700;">← All Buyer Guides</a>
          <a href="tel:" style="color:#cbd5e1; font-size:12.5px; font-weight:700; text-decoration:none;">24/7 Athlete Line: </a>
          <a href="{hero_prod.get('fourthwall_product_url') or ('../index.html?buy=' + hero_prod['id'])}" class="Btn Btn--BuyNow" style="width:auto; padding:8px 16px;">1-Click Buy Top Pick (${hero_prod['retail_price']:.2f})</a>
        </div>
      </div>
    </div>
  </header>

  <main class="Container" style="max-width:980px; padding:28px 20px 64px;">
    <article style="background:#fff; border:1px solid #e4e6eb; border-radius:12px; padding:32px;">
      <div class="ArticleEyebrow">{html.escape(cat)} · {html.escape(art['read_time'])} · Free US shipping</div>
      <h1 style="font-size:28px; line-height:1.22; margin:8px 0 14px;">{html.escape(title)}</h1>
      <p style="font-size:16px; color:#444; border-left:3px solid #0066ff; padding-left:14px; margin-bottom:20px;">
        {html.escape(summary)}
      </p>

{shop_strip}

      <section aria-label="Featured gear checkout" style="background:#0f172a;color:#fff;padding:16px 18px;border-radius:10px;margin-bottom:26px;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
          <span style="font-size:12px;font-weight:900;text-transform:uppercase;letter-spacing:0.08em;color:#38bdf8;">⚡ Featured Gear In This Guide  -  Instant 1-Click Checkout</span>
          <span style="font-size:12px;color:#cbd5e1;">Made to order. Free US shipping</span>
        </div>
        <div style="display:grid;gap:8px;">
{top_strip_pills}
        </div>
      </section>
        <div style="margin-top:16px;background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:#f8fafc;border:1.5px solid #0066ff;border-radius:10px;padding:14px 16px;">
          <p style="font-size:12.5px;color:#cbd5e1;margin:0 0 10px;line-height:1.45;">Made to order. Free US shipping. Secure checkout and fulfillment by Fourthwall.</p>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <a href="../team_orders.html" style="background:#0066ff;color:#fff;text-decoration:none;padding:6px 11px;border-radius:6px;font-size:12px;font-weight:800;">Team orders</a>
            <a href="../wristband.html" style="background:#0f172a;border:1px solid #475569;color:#fff;text-decoration:none;padding:6px 11px;border-radius:6px;font-size:12px;font-weight:800;">⏱️ Free Printable Split Wristband</a>
            <a href="../gyms/index.html" style="background:#0f172a;border:1px solid #475569;color:#38bdf8;text-decoration:none;padding:6px 11px;border-radius:6px;font-size:12px;font-weight:800;">🏋️ HYROX Gym Finder (72 Hubs)</a>
          </div>
        </div>

      <div class="Modal__ArticleBody" style="font-size:15px; line-height:1.7;">
        {art['body_html']}
      </div>

      <section style="margin-top:32px; padding-top:24px; border-top:1px solid #e4e6eb;">
        <h2 style="font-size:20px; margin-bottom:6px;">Shop Featured HYROX Race Apparel &amp; Recovery Hardware (1-Click Checkout)</h2>
        <p style="font-size:13.5px; color:#475569; margin-bottom:16px;">Made to order. Free US shipping. Secure checkout and fulfillment by Fourthwall.</p>
        <div class="ProductGrid">
          {rec_html}
        </div>
      </section>

      <section style="margin-top:32px; padding-top:20px; border-top:1px solid #e4e6eb;">
        <h3 style="font-size:16px; margin-bottom:10px;">More Hybrid Training, Race-City &amp; Buyer Guides</h3>
        <ul style="padding-left:20px; line-height:1.8; font-size:14px;">
          {other_articles_html}
        </ul>
      </section>
    </article>
  </main>

  <footer class="SiteFooter">
    <div class="Container">
      <p><strong>Apex Hybrid Co., operated by NolCorp LLC</strong> · <a href="../contact.html">Contact</a> · <a href="../about.html">About</a> · <a href="../shipping.html">Shipping</a> · <a href="../returns.html">Returns</a> · <a href="../privacy.html">Privacy</a> · <a href="../terms.html">Terms</a> · <a href="mailto:apexhybridco@gmail.com" style="color:#38bdf8;">apexhybridco@gmail.com</a> · <a href="../index.html" style="color:#38bdf8;">Return to Storefront</a></p>
    </div>
  <div id="apexStickyPromoBar" style="position:fixed;bottom:0;left:0;right:0;z-index:90;background:linear-gradient(90deg,#0f172a 0%,#1e293b 55%,#0f172a 100%);color:#f8fafc;border-top:2px solid #0066ff;padding:9px 14px;box-shadow:0 -6px 24px rgba(0,0,0,0.38);font-family:system-ui,-apple-system,sans-serif;">
    <div style="max-width:1240px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 14px;font-size:12.5px;">
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <span style="background:#0066ff;color:#fff;font-weight:900;font-size:10.5px;padding:3px 8px;border-radius:999px;text-transform:uppercase;letter-spacing:0.07em;">Shipping</span>
        <span>Free US shipping. Secure checkout and fulfillment by Fourthwall.</span>
        
      </div>
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <a href="../wristband.html" style="background:#0066ff;color:#fff;text-decoration:none;padding:5px 11px;border-radius:6px;font-weight:800;font-size:12px;">⏱️ Free Printable Split Wristband →</a>
        <a href="../gyms/index.html" style="background:#1e293b;border:1px solid #475569;color:#e2e8f0;text-decoration:none;padding:5px 11px;border-radius:6px;font-weight:700;font-size:12px;">🏋️ HYROX Gym Directory (72 Hubs)</a>
        <a href="../team_orders.html" style="color:#38bdf8;text-decoration:none;font-weight:800;font-size:12px;">Doubles 2-Packs →</a>
      </div>
    </div>
  </div>
  </footer>
  <script src="/checkout-code.js"></script>
  <script>
  (function(){{
    var fwSlugs = {json.dumps(fw_slugs_map)};
    document.addEventListener("click", function(ev){{
      var link = ev.target && ev.target.closest ? ev.target.closest('a[href*="apex-hybrid-co-shop.fourthwall.com/products/"]') : null;
      if (!link) return;
      var href = link.getAttribute("href") || "";
      var slug = href.split("?")[0].replace(/\/+$/, "").split("/").pop();
      var vid = fwSlugs[slug];
      if (!vid) return;
      ev.preventDefault();
      var prevText = link.textContent;
      link.style.opacity = "0.75";
      link.textContent = "Opening Secure Checkout…";
      fetch("https://apex-hybrid-co-shop.fourthwall.com/cart/add.js", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ items: [{{ id: vid, quantity: 1 }}] }})
      }}).then(function(r){{ return r.json(); }}).then(function(d){{
        var cid = d && d.cart && d.cart.id;
        if (!cid) throw new Error("no_cart");
        return fetch("https://apex-hybrid-co-shop.fourthwall.com/api/v2/checkout/cart", {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ cartId: cid, cartCurrency: "USD" }})
        }});
      }}).then(function(r){{ return r.json(); }}).then(function(chk){{
        if (chk && chk.id) {{
          apexFinishCheckout(chk.id, function (url) {{ window.location.href = url; }});
        }} else {{
          window.location.href = href;
        }}
      }}).catch(function(){{
        link.textContent = prevText;
        link.style.opacity = "1";
        window.location.href = href;
      }});
    }});
    try {{
      var isBot = /bot|crawl|spider|slurp|headless|lighthouse/i.test(navigator.userAgent || "");
      var ns = "https://abacus.jasoncameron.dev/hit/apexhybridco.com";
      var hit = function(k){{ if (!isBot) fetch(ns + "/" + k, {{method:"GET", mode:"cors", keepalive:true, cache:"no-store"}}).catch(function(){{}}); }};
      hit("pageviews_total");
      hit("article_views_total");
    }} catch (_) {{}}
  }})();
  </script>
<script data-goatcounter="https://apexhybridco.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</body>
</html>
"""
        with open(os.path.join(BASE_DIR, "articles", f"{slug}.html"), "w", encoding="utf-8") as out:
            out.write(page_html)
        city_page_path = os.path.join(BASE_DIR, "seo_city_pages", f"{slug}.html")
        if os.path.exists(city_page_path) or any(k in slug for k in ("chicago", "dallas", "anaheim", "las-vegas", "miami", "new-york", "nyc", "first-hyrox", "pump-cover", "compromised-running-shirt", "sled-push-enthusiast")):
            city_html = page_html.replace(f"/articles/{slug}.html", f"/seo_city_pages/{slug}.html")
            for g_other in guides:
                oslug = g_other["slug"]
                city_html = city_html.replace(f'href="{oslug}.html"', f'href="../articles/{oslug}.html"')
            # City URLs stay published, but they duplicate the article. Canonical
            # and og:url must name the article or Search Console treats them as copies.
            article_url = f"{SITE_URL}/articles/{slug}.html"
            city_html = city_html.replace(
                f'<link rel="canonical" href="{SITE_URL}/seo_city_pages/{slug}.html" />',
                f'<link rel="canonical" href="{article_url}" />',
                1,
            )
            city_html = city_html.replace(
                f'<meta property="og:url" content="{SITE_URL}/seo_city_pages/{slug}.html" />',
                f'<meta property="og:url" content="{article_url}" />',
                1,
            )
            with open(city_page_path, "w", encoding="utf-8") as out_city:
                out_city.write(city_html)

    # Also generate articles/index.html hub page
    hub_cards = "\n".join(
        f'''        <article class="GuideCard" style="background:#fff; border:1px solid #e4e6eb; border-radius:10px; padding:20px; display:flex; flex-direction:column; justify-content:space-between;">
          <div>
            <div class="GuideCard__Cat" style="font-size:11.5px; font-weight:800; color:#0066ff; text-transform:uppercase; margin-bottom:6px;">{html.escape(g["category"])}</div>
            <h2 style="font-size:17px; line-height:1.35; margin-bottom:8px;"><a href="{g["slug"]}.html" style="color:#0f172a; text-decoration:none;">{html.escape(g["title"])}</a></h2>
            <p style="font-size:13.5px; color:#475569; line-height:1.55;">{html.escape(g["summary"])}</p>
          </div>
          <div style="margin-top:14px; display:flex; justify-content:space-between; align-items:center; padding-top:10px; border-top:1px solid #f1f5f9;">
            <span style="font-size:12px; color:#64748b; font-weight:700;">{html.escape(g["read_time"])}</span>
            <a href="{g["slug"]}.html" class="Btn Btn--QuickView" style="width:auto; padding:6px 14px; text-decoration:none;">Read Guide →</a>
          </div>
        </article>'''
        for g in guides
    )
    hub_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" href="/favicon.ico" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>HYROX Training, Pacing, Race-City &amp; Recovery Buyer Guides ({len(guides)} Guides) | Apex Hybrid Co.</title>
  <meta name="description" content="Explore all {len(guides)} data-backed HYROX &amp; hybrid athlete training protocols, start-corral warmup guides, 1km pacing strategies, 2026/2027 race-city guides, and recovery blueprints." />
  <link rel="canonical" href="{SITE_URL}/articles/index.html" />
  <link rel="stylesheet" href="../styles.css?v=20261026v3" />
</head>
<body>
  <header class="TopHeader">
    <div class="TopHeader__Main">
      <div class="Container TopHeader__Inner">
        <a href="../index.html" class="BrandLogo">
          <span class="BrandLogo__Mark">APEX</span>
          <span class="BrandLogo__Sub">HYBRID CO.</span>
        </a>
        <div style="margin-left:auto; display:flex; gap:14px; align-items:center;">
          <a href="../team_orders.html" style="color:#38bdf8; font-size:13px; font-weight:700;">Doubles 2-Packs &amp; Coach Program →</a>
          <a href="../index.html" style="color:#fff; font-size:13px; font-weight:700;">← Back to Full 45-Product Storefront</a>
        </div>
      </div>
    </div>
  </header>
  <main class="Container" style="padding:32px 20px 64px;">
    <h1 style="font-size:28px; margin-bottom:8px;">HYROX &amp; Hybrid Athlete Training, Pacing &amp; Recovery Hub ({len(guides)} Guides)</h1>
    <p style="font-size:15px; color:#475569; margin-bottom:24px;">Station-by-station pacing calculators, start-corral warmup protocols, 2026/2027 race-city gear checklists, and 48-hour post-race recovery blueprints.</p>
    <div class="GuidesGrid">
{hub_cards}
    </div>
  </main>
  <footer class="SiteFooter">
    <div class="Container">
      <p><strong>Apex Hybrid Co., operated by NolCorp LLC</strong> · <a href="../contact.html">Contact</a> · <a href="../about.html">About</a> · <a href="../shipping.html">Shipping</a> · <a href="../returns.html">Returns</a> · <a href="../privacy.html">Privacy</a> · <a href="../terms.html">Terms</a> · <a href="../index.html" style="color:#38bdf8;">Return to Storefront</a></p>
      <p>Secure checkout and fulfillment by Fourthwall.</p>
    </div>
  <div id="apexStickyPromoBar" style="position:fixed;bottom:0;left:0;right:0;z-index:90;background:linear-gradient(90deg,#0f172a 0%,#1e293b 55%,#0f172a 100%);color:#f8fafc;border-top:2px solid #0066ff;padding:9px 14px;box-shadow:0 -6px 24px rgba(0,0,0,0.38);font-family:system-ui,-apple-system,sans-serif;">
    <div style="max-width:1240px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 14px;font-size:12.5px;">
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <span style="background:#0066ff;color:#fff;font-weight:900;font-size:10.5px;padding:3px 8px;border-radius:999px;text-transform:uppercase;letter-spacing:0.07em;">Shipping</span>
        <span>Free US shipping. Secure checkout and fulfillment by Fourthwall.</span>
        
      </div>
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <a href="../wristband.html" style="background:#0066ff;color:#fff;text-decoration:none;padding:5px 11px;border-radius:6px;font-weight:800;font-size:12px;">⏱️ Free Printable Split Wristband →</a>
        <a href="../gyms/index.html" style="background:#1e293b;border:1px solid #475569;color:#e2e8f0;text-decoration:none;padding:5px 11px;border-radius:6px;font-weight:700;font-size:12px;">🏋️ HYROX Gym Directory (72 Hubs)</a>
        <a href="../team_orders.html" style="color:#38bdf8;text-decoration:none;font-weight:800;font-size:12px;">Doubles 2-Packs →</a>
      </div>
    </div>
  </div>
  </footer>
  <script>
  (function(){{
    try {{
      if (/bot|crawl|spider|slurp|headless|lighthouse/i.test(navigator.userAgent || "")) return;
      var ns = "https://abacus.jasoncameron.dev/hit/apexhybridco.com";
      fetch(ns + "/pageviews_total", {{method:"GET", mode:"cors", keepalive:true, cache:"no-store"}}).catch(function(){{}});
      fetch(ns + "/article_views_total", {{method:"GET", mode:"cors", keepalive:true, cache:"no-store"}}).catch(function(){{}});
    }} catch (_) {{}}
  }})();
  </script>
<script data-goatcounter="https://apexhybridco.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</body>
</html>'''
    with open(os.path.join(BASE_DIR, "articles", "index.html"), "w", encoding="utf-8") as out:
        out.write(hub_html)


def is_apparel_product(prod):
    """Apparel is whatever the Merchant category already classifies as apparel."""
    return google_category_for(prod).startswith("Apparel & Accessories")


# Delisted artwork. Never emit these even if they reappear in the catalog.
BANNED_FEED_IDS = {"APC-C04", "APC-C39"}


def sold_color(prod):
    """Return black only with a source other than a duplicated White variant map.

    White/Default maps often repeat the Black variant id and do not prove a
    second color is sold. A black image filename, or an explicit black-only
    description on a product with no colorways, does.
    """
    image = (prod.get("image") or "").lower()
    if "-black." in image or "-black?" in image:
        return "black"
    if prod.get("has_colorways") is False:
        blob = f"{prod.get('short_desc') or ''} {prod.get('title') or ''}".lower()
        if "black" in blob:
            return "black"
    return None


SIZE_KEYS = {"XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL", "One size", "One Size"}


def black_only_variant_map(variants):
    """Publish only the Black size map. White and Default repeat those ids."""
    if not isinstance(variants, dict) or not variants:
        return {}
    if set(variants).issubset(SIZE_KEYS):
        return variants
    black = variants.get("Black")
    if isinstance(black, dict):
        return {"Black": black}
    return {k: v for k, v in variants.items() if k == "Black" or k in SIZE_KEYS}


def catalog_size_variant_ids(prod):
    """Sold size -> Fourthwall variant id from catalog.json.

    Read the Black map or a flat size map. Ignore White and Default keys:
    those copies reuse the same variant ids and are not evidence of color.
    """
    fv = prod.get("fourthwall_variants") or {}
    if not isinstance(fv, dict) or not fv:
        return {}
    override = BLANK_COLOR_OVERRIDE.get(prod.get("id"))
    if override:
        sizes = fv.get(override) or fv.get("White") or fv.get("Black")
        if isinstance(sizes, dict):
            ids = {}
            for size, val in sizes.items():
                if isinstance(val, str) and val:
                    ids[size] = val
                elif isinstance(val, dict) and val.get("id"):
                    ids[size] = val["id"]
            return ids
    if all(isinstance(v, dict) and v.get("id") for v in fv.values()):
        return {size: info["id"] for size, info in fv.items()}
    black = fv.get("Black")
    if isinstance(black, dict):
        ids = {}
        for size, val in black.items():
            if isinstance(val, str) and val:
                ids[size] = val
            elif isinstance(val, dict) and val.get("id"):
                ids[size] = val["id"]
        return ids
    return {}


def load_city_jacket_variant_file():
    """Live Fourthwall pull for Denver, Anaheim, Nashville, and Vancouver."""
    path = os.path.join(BASE_DIR, "fourthwall_city_jacket_variants.json")
    if not os.path.exists(path):
        return {}
    data = json.load(open(path, encoding="utf-8"))
    return data


def fourthwall_size_prices(prod):
    """Live size order and prices from the Fourthwall checkout map."""
    entry = load_fourthwall_variant_prices().get(prod.get("id")) or {}
    variants = entry.get("variants") or {}
    order = ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL", "One Size", "One size"]
    sizes = [sz for sz in order if sz in variants]
    sizes += [sz for sz in variants if sz not in sizes]
    sold_out = set()
    snapshot = load_fourthwall_feed_variants().get(prod.get("id")) or {}
    for variant in snapshot.get("variants") or []:
        if variant.get("size") and variant.get("in_stock") is False:
            sold_out.add(variant["size"])
    priced = []
    for size in sizes:
        info = variants.get(size) or {}
        if info.get("price") is None or size in sold_out:
            continue
        priced.append((size, float(info["price"])))
    return priced


def load_fourthwall_variant_prices():
    """Size prices and ids from app.js FW_VARIANTS, the checkout source."""
    path = os.path.join(BASE_DIR, "app.js")
    text = open(path, encoding="utf-8").read()
    marker = "const FW_VARIANTS = "
    start = text.find(marker)
    if start < 0:
        raise RuntimeError("FW_VARIANTS missing from app.js")
    raw = text[start + len(marker):].split("\n", 1)[0].rstrip().rstrip(";")
    return json.loads(raw)


FEED_COLOR = "Black"  # every Apex product is sold in black only
MERCHANT_CATEGORY_OVERRIDES = {
    # Gym bag: a real Google taxonomy node (103) instead of the generic
    # Sporting Goods bucket, so the item carries full apparel-style attributes.
    "Gym Bags": "Luggage & Bags > Duffel Bags",
}


def merchant_category_for(prod):
    return MERCHANT_CATEGORY_OVERRIDES.get(prod.get("category", "")) or google_category_for(prod)


def load_fourthwall_feed_variants():
    """Live Fourthwall offers written by sync_fourthwall_feed_variants.py."""
    path = os.path.join(BASE_DIR, "fourthwall_feed_variants.json")
    if not os.path.exists(path):
        return {}
    return json.load(open(path, encoding="utf-8")).get("products") or {}


def fourthwall_snapshot_offers(prod, snapshot):
    """Sizes, prices and stock straight from the Fourthwall product page."""
    entry = snapshot.get(prod["id"])
    if not entry:
        return []
    return [
        {"size": v["size"], "variant_id": v["variant_id"], "price": float(v["price"]),
         "in_stock": bool(v.get("in_stock", True))}
        for v in entry.get("variants") or []
        if v.get("size") and v.get("price") is not None
    ]


def verified_size_offers(prod, fw_variants, city_jackets=None):
    """Sizes whose catalog variant id matches Fourthwall and has a price.

    Returns (offers, gaps). Offers are not invented: a size is dropped when
    either source lacks it or the ids disagree. The city-jacket file is
    authoritative for APC-C47 through APC-C50 and must agree with catalog
    and the checkout map.
    """
    catalog_ids = catalog_size_variant_ids(prod)
    fw_entry = (fw_variants.get(prod["id"]) or {}).get("variants") or {}
    city = (city_jackets or {}).get(prod["id"])
    if city:
        offers = []
        gaps = []
        expected_url = city["url"]
        actual_url = prod.get("fourthwall_product_url") or ""
        if actual_url != expected_url:
            gaps.append(f"{prod['id']}: Fourthwall URL {actual_url} != verified {expected_url}")
        prices = city_jackets["prices"]
        for size, variant_id in city["variants"].items():
            price = float(prices[size])
            cat_id = catalog_ids.get(size)
            fw_size = fw_entry.get(size) or {}
            if cat_id != variant_id or fw_size.get("id") != variant_id or float(fw_size.get("price") or -1) != price:
                gaps.append(f"{prod['id']} {size}: city-jacket record disagrees with catalog or checkout map")
                continue
            offers.append({"size": size, "variant_id": variant_id, "price": price})
        extra = [size for size in list(catalog_ids) + list(fw_entry) if size not in city["variants"]]
        for size in sorted(set(extra)):
            gaps.append(f"{prod['id']} {size}: size is not in the verified city-jacket pull")
        return offers, gaps
    offers = []
    gaps = []
    for size, variant_id in catalog_ids.items():
        fw_size = fw_entry.get(size)
        if not fw_size or fw_size.get("id") != variant_id or fw_size.get("price") is None:
            gaps.append(f"{prod['id']} {size}: catalog/Fourthwall variant mismatch")
            continue
        offers.append({
            "size": size,
            "variant_id": variant_id,
            "price": float(fw_size["price"]),
        })
    fw_only = [size for size in fw_entry if size not in catalog_ids]
    for size in fw_only:
        gaps.append(f"{prod['id']} {size}: Fourthwall size missing from catalog")
    if not catalog_ids and not fw_entry:
        gaps.append(f"{prod['id']}: no size variants in catalog or Fourthwall")
    return offers, gaps


def money_usd(amount):
    return f"{float(amount):.2f} USD"


def feed_prices(prod, variant_price):
    """Keep the existing list/sale pair when it still applies to this size."""
    retail = float(prod["retail_price"])
    list_price = float(prod.get("list_price") or retail)
    return money_usd(variant_price), money_usd(variant_price)


RACE_DAY_HANDLING_IDS = {"APC-C46", "APC-C47", "APC-C48", "APC-C49", "APC-C50", "APC-C75"}
STITCHED_RACE_IDS = {"APC-C51", "APC-C52", "APC-C53", "APC-C54", "APC-C55", "APC-C57", "APC-C70"}
NA_PACKABLE_IDS = {"APC-C43", "APC-C51", "APC-C52", "APC-C53", "APC-C54", "APC-C55", "APC-C57", "APC-C70"}
NA_SHIP_LINE = "Made to order. Ships from the US or Canada. Free US shipping."
STITCHED_SHIP_LINE = "Made to order. Ships from the US or Canada. Free US shipping."
OVERSEAS_SHIP_LINE = "Made overseas. Ships in about 10–14 business days. Free US shipping."


def feed_description(prod):
    desc = (prod.get("short_desc") or "").strip()
    if prod.get("id") in RACE_DAY_HANDLING_IDS and "overseas" not in desc.lower():
        desc = f"{desc} {OVERSEAS_SHIP_LINE}".strip()
    if prod.get("id") == "APC-C70" and "US or Canada" not in desc:
        desc = f"{desc} Ships from the US or Canada. Free US shipping.".strip()
    elif prod.get("id") in STITCHED_RACE_IDS and "US or Canada" not in desc:
        desc = f"{desc} {STITCHED_SHIP_LINE}".strip()
    elif prod.get("id") in NA_PACKABLE_IDS and "US or Canada" not in desc:
        desc = f"{desc} {NA_SHIP_LINE}".strip()
    url = prod.get("fourthwall_product_url") or ""
    if url:
        desc = f"{desc} {url}".strip()
    return desc


def merchant_item_xml(prod, *, item_id, title, price, sale_price, apparel=None):
    link = f"{SITE_URL}/products/{prod['handle']}.html"
    image = prod.get("image") or ""
    img_link = image if image.startswith("http") else f"{SITE_URL}/{image.lstrip('/')}"
    g_cat = merchant_category_for(prod)
    availability = "in_stock" if (apparel or {}).get("in_stock", True) else "out_of_stock"
    lines = [
        "    <item>",
        f"      <g:id>{xml_text(item_id)}</g:id>",
        f"      <g:title>{xml_text(title)}</g:title>",
        f"      <g:description>{xml_text(feed_description(prod))}</g:description>",
        f"      <g:link>{xml_text(link)}</g:link>",
        f"      <g:image_link>{xml_text(img_link)}</g:image_link>",
    ]
    if prod.get("id") in NA_PACKABLE_IDS:
        for extra in [prod.get("alt_image")] + list(prod.get("extra_images") or []):
            if not extra:
                continue
            extra_link = extra if str(extra).startswith("http") else f"{SITE_URL}/{str(extra).lstrip('/')}"
            lines.append(f"      <g:additional_image_link>{xml_text(extra_link)}</g:additional_image_link>")
    lines += [
        "      <g:condition>new</g:condition>",
        f"      <g:availability>{availability}</g:availability>",
        f"      <g:price>{price}</g:price>",
        "      <g:brand>Apex Hybrid Co</g:brand>",
        f"      <g:mpn>{xml_text(prod['id'])}</g:mpn>",
        "      <g:identifier_exists>no</g:identifier_exists>",
    ]
    if apparel:
        lines.append(f"      <g:item_group_id>{xml_text(prod['id'])}</g:item_group_id>")
        lines.append("      <g:age_group>adult</g:age_group>")
        lines.append("      <g:gender>unisex</g:gender>")
        if apparel.get("color"):
            lines.append(f"      <g:color>{xml_text(apparel['color'])}</g:color>")
        if apparel.get("size"):
            lines.append(f"      <g:size>{xml_text(apparel['size'])}</g:size>")
    lines.extend([
        f"      <g:google_product_category>{xml_text(g_cat)}</g:google_product_category>",
        f"      <g:product_type>{xml_text(prod['dept'])} &gt; {xml_text(prod['category'])}</g:product_type>",
    ])
    if prod.get("id") in {"APC-C37", "APC-C38", "APC-C40", "APC-C41"}:
        lines.append("      <g:material>6.1 oz ring-spun cotton</g:material>")
    lines.extend([
        "      <g:shipping>",
        "        <g:country>US</g:country>",
        "        <g:service>Standard Ground</g:service>",
        "        <g:price>0.00 USD</g:price>",
    ])
    if prod.get("id") in RACE_DAY_HANDLING_IDS:
        lines.extend([
            "        <g:min_handling_time>10</g:min_handling_time>",
            "        <g:max_handling_time>14</g:max_handling_time>",
        ])
    else:
        lines.extend([
            "        <g:min_handling_time>3</g:min_handling_time>",
            "        <g:max_handling_time>5</g:max_handling_time>",
        ])
    lines.extend([
        "      </g:shipping>",
        "    </item>",
    ])
    return "\n".join(lines)


def generate_google_shopping_feed():
    """Write google_merchant_feed.xml and google_shopping_feed.xml.

    Clothing, including the Headwear cap, gets one item per verified size.
    Products with no verified sizes are omitted rather than given a guessed
    size. The gym bag stays a non-apparel row. APC-C04 and APC-C39 are never
    emitted.
    """
    fw_snapshot = load_fourthwall_feed_variants()
    fw_variants = load_fourthwall_variant_prices()
    city_file = load_city_jacket_variant_file()
    city_products = city_file.get("products") or {}
    if city_products:
        city_products = dict(city_products)
        city_products["prices"] = city_file.get("prices") or {}
    items_xml = []
    gaps = []
    apparel_products = []
    non_apparel = []
    for prod in products:
        if prod["id"] in BANNED_FEED_IDS or prod.get("handle") in DELISTED_NOINDEX_HANDLES:
            gaps.append(f"{prod['id']}: banned design excluded")
            continue
        image = (prod.get("image") or "").lower()
        if "apc-c04" in image or "apc-c39" in image:
            gaps.append(f"{prod['id']}: banned artwork image excluded")
            continue
        title = prod.get("seo_title") or prod["title"]
        fw_offers = fourthwall_snapshot_offers(prod, fw_snapshot)
        if fw_offers:
            # Fourthwall is the source of truth: one item per live variant,
            # each with category, age group, gender, color and size.
            apparel_products.append(prod["id"])
            for offer in fw_offers:
                price, sale = feed_prices(prod, offer["price"])
                item_id = prod["id"] if len(fw_offers) == 1 else f"{prod['id']}-{offer['size']}"
                variant_title = title if len(fw_offers) == 1 else f"{title} - {offer['size']}"
                items_xml.append(merchant_item_xml(
                    prod,
                    item_id=item_id,
                    title=variant_title,
                    price=price,
                    sale_price=sale,
                    apparel={**offer, "color": BLANK_COLOR_OVERRIDE.get(prod["id"], FEED_COLOR)},
                ))
            continue
        gaps.append(f"{prod['id']}: not in fourthwall_feed_variants.json; fell back to catalog variants")
        if not is_apparel_product(prod):
            retail = float(prod["retail_price"])
            price, sale = feed_prices(prod, retail)
            items_xml.append(merchant_item_xml(
                prod,
                item_id=prod["id"],
                title=title,
                price=price,
                sale_price=sale,
            ))
            non_apparel.append(prod["id"])
            continue
        offers, offer_gaps = verified_size_offers(prod, fw_variants, city_products)
        gaps.extend(offer_gaps)
        if not offers:
            gaps.append(f"{prod['id']}: apparel omitted; no verified sold sizes")
            continue
        color = BLANK_COLOR_OVERRIDE.get(prod["id"]) or sold_color(prod)
        if not color:
            gaps.append(f"{prod['id']}: color omitted; no black image or black-only description")
        apparel_products.append(prod["id"])
        for offer in offers:
            price, sale = feed_prices(prod, offer["price"])
            # One sold size keeps the existing product id. Multiple sizes need
            # a stable suffix so each variant stays unique.
            item_id = prod["id"] if len(offers) == 1 else f"{prod['id']}-{offer['size']}"
            variant_title = title if len(offers) == 1 else f"{title} - {offer['size']}"
            items_xml.append(merchant_item_xml(
                prod,
                item_id=item_id,
                title=variant_title,
                price=price,
                sale_price=sale,
                apparel={**offer, "color": color},
            ))

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:g="http://base.google.com/ns/1.0" version="2.0">
  <channel>
    <title>Apex Hybrid Co</title>
    <link>{SITE_URL}</link>
    <description>Apex Hybrid Co product feed - hybrid training apparel</description>
{chr(10).join(items_xml)}
  </channel>
</rss>
"""
    shopping_path = os.path.join(BASE_DIR, "google_shopping_feed.xml")
    with open(shopping_path, "w", encoding="utf-8") as f:
        f.write(rss_xml)
    shutil.copyfile(shopping_path, os.path.join(BASE_DIR, "google_shopping_feed_ghpages.xml"))
    with open(os.path.join(BASE_DIR, "google_merchant_feed.xml"), "w", encoding="utf-8") as f:
        f.write(rss_xml)
    assert_published_xml_parses()
    summary = {
        "items": len(items_xml),
        "apparel_products": apparel_products,
        "non_apparel": non_apparel,
        "gaps": gaps,
    }
    print(
        f"Merchant feed: {len(items_xml)} items, "
        f"{len(apparel_products)} apparel products, "
        f"{len(non_apparel)} non-apparel, {len(gaps)} gaps"
    )
    for gap in gaps:
        print(f"  gap: {gap}")
    return summary



def strip_speed_claims(text):
    """Drop retired speed claims from editorial RSS titles and summaries on every rebuild."""
    if not text:
        return text
    repls = [
        ("Last-Minute Race Shirt & Doubles 2-Pack Fast US Shipping", "Chicago Navy Pier Race Shirt & Doubles 2-Pack"),
        ("Fast US Shipping", "Free US Shipping"),
        ("Priority Texas Dispatch", "Dallas Nov 2026 guide"),
        ("Dallas Nov 2026 Priority Dispatch", "Dallas Nov 2026 guide"),
        ("Priority Texas & US fulfillment open for ", "Guide for "),
        ("Anaheim Dec 2026 SoCal Dispatch", "Anaheim Dec 2026"),
        ("Dispatched directly from our Orange County / US fulfillment network for ", "Made to order for "),
        ("and fast local  dispatch.", " Made to order. Ships from the US and arrives in about 7–10 business days."),
        ("Lock in guaranteed after production US delivery on ", "Shop "),
        ("Guaranteed US Delivery for ", ""),
        ("Quick-Ship ", ""),
        ("Zero-Lead-Time ", "Made-to-order "),
        (
            "Roxzone Speed Dept. & Built For Heavy Legs breathable tech shirts (APC-C36..APC-C41)",
            "Built For Heavy Legs (APC-C36) and the 6.1 oz ring-spun cotton tees 1KM Split (APC-C37), Aerobic Engine (APC-C38), Push Heavy Run Fast (APC-C40), and Roxzone Speed Dept. (APC-C41)",
        ),
        (
            "Roxzone Speed Dept. &amp; Built For Heavy Legs breathable tech shirts (APC-C36..APC-C41)",
            "Built For Heavy Legs (APC-C36) and the 6.1 oz ring-spun cotton tees 1KM Split (APC-C37), Aerobic Engine (APC-C38), Push Heavy Run Fast (APC-C40), and Roxzone Speed Dept. (APC-C41)",
        ),
    ]
    for old, new in repls:
        text = text.replace(old, new)
    return text


def article_ship_line(prod):
    """Shipping line for a product card inside a guide."""
    if prod.get("id") in RACE_DAY_HANDLING_IDS:
        return "Made overseas. Ships in about 10–14 business days. Free US shipping."
    if prod.get("id") in STITCHED_RACE_IDS:
        return STITCHED_SHIP_LINE
    if prod.get("id") in NA_PACKABLE_IDS:
        return NA_SHIP_LINE
    return "Made to order. Ships from the US. Free US shipping."


def generate_editorial_rss_feeds():
    """
    Generates standards-compliant RSS 2.0 + Atom + WebSub hub feeds (feed.xml and rss.xml)
    containing all 30 buyer guides and top product releases for RSS aggregators, WebSub hubs,
    and search crawler feed discovery.
    """
    pub_rfc822 = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    for filename in ("feed.xml", "rss.xml"):
        self_url = f"{SITE_URL}/{filename}"
        items_xml = []
        items_xml.append(
            f"""    <item>
      <title>{xml_text("Gifts for Hybrid Athletes: Holiday Gift Guide")}</title>
      <link>{xml_text(SITE_URL + "/gift-guide.html")}</link>
      <guid isPermaLink="true">{xml_text(SITE_URL + "/gift-guide.html")}</guid>
      <pubDate>{xml_text(pub_rfc822)}</pubDate>
      <category>{xml_text("Gift Guide")}</category>
      <description>{xml_text("Black gifts for hybrid athletes, grouped by price. Regular list prices. Made to order. Free US shipping.")}</description>
    </item>"""
        )
        for art in guides:
            art_url = f"{SITE_URL}/articles/{art['slug']}.html"
            items_xml.append(
                f"""    <item>
      <title>{xml_text(strip_speed_claims(art['title']))}</title>
      <link>{xml_text(art_url)}</link>
      <guid isPermaLink="true">{xml_text(art_url)}</guid>
      <pubDate>{xml_text(pub_rfc822)}</pubDate>
      <category>{xml_text(strip_speed_claims(art.get('category', 'HYROX & Hybrid Racing Guide')))}</category>
      <description>{xml_text(strip_speed_claims(art.get('summary', '')))}</description>
    </item>"""
            )
        for prod in products:
            prod_url = f"{SITE_URL}/products/{prod['handle']}.html"
            fw_url = prod.get("fourthwall_product_url") or prod.get("checkout_url") or f"{SITE_URL}/?buy={prod['id']}"
            desc = f"{prod['short_desc']}  -  Price: ${prod['retail_price']:.2f} USD ({prod['ship_time']}). Direct Checkout: {fw_url}"
            if prod["id"] in BLANK_COLOR_OVERRIDE:
                desc = re.sub(r"\bWhite\b", BLANK_COLOR_OVERRIDE[prod["id"]], desc)
            items_xml.append(
                f"""    <item>
      <title>{xml_text(prod.get('seo_title', prod['title']))} (${prod['retail_price']:.2f})</title>
      <link>{xml_text(prod_url)}</link>
      <guid isPermaLink="true">{xml_text(prod_url)}</guid>
      <pubDate>{xml_text(pub_rfc822)}</pubDate>
      <category>{xml_text(prod.get('dept', 'Hybrid Race Gear'))}</category>
      <description>{xml_text(desc)}</description>
    </item>"""
            )

        feed_doc = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>Apex Hybrid Co</title>
    <link>{SITE_URL}/</link>
    <description>Apex Hybrid Co product and training updates</description>
    <language>en-us</language>
    <lastBuildDate>{pub_rfc822}</lastBuildDate>
    <managingEditor>apexhybridco@gmail.com (Apex Hybrid Co.)</managingEditor>
    <webMaster>apexhybridco@gmail.com (Apex Hybrid Co.)</webMaster>
    <atom:link href="{xml_text(self_url)}" rel="self" type="application/rss+xml" />
    <atom:link href="https://pubsubhubbub.appspot.com/" rel="hub" />
    <atom:link href="https://pubsubhubbub.superfeedr.com/" rel="hub" />
{chr(10).join(items_xml)}
  </channel>
</rss>
"""
        with open(os.path.join(BASE_DIR, filename), "w", encoding="utf-8") as f:
            f.write(feed_doc)
    assert_published_xml_parses()


def generate_pinterest_csv_feed():
    csv_path = os.path.join(BASE_DIR, "pinterest_catalog_feed.csv")
    fieldnames = [
        "id",
        "title",
        "description",
        "link",
        "image_link",
        "price",
        "availability",
        "condition",
        "google_product_category",
        "product_type",
        "brand",
        "size",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\r\n",
        )
        writer.writeheader()
        for prod in products:
            priced = fourthwall_size_prices(prod)
            if not priced:
                priced = [("", float(prod["retail_price"]))]
            base = {
                "title": prod.get("seo_title", prod["title"]),
                "description": feed_description(prod) if "US or Canada" in (prod.get("short_desc") or "") or prod.get("id") in NA_PACKABLE_IDS else (prod["short_desc"] + (" " + prod["fourthwall_product_url"] if prod.get("fourthwall_product_url") else "")).strip(),
                "link": f"{SITE_URL}/products/{prod['handle']}.html",
                "image_link": f"{SITE_URL}/{prod['image']}",
                "availability": "in stock",
                "condition": "new",
                "google_product_category": merchant_category_for(prod),
                "product_type": f"{prod['dept']} > {prod['category']}",
                "brand": "Apex Hybrid Co., operated by NolCorp LLC",
            }
            if prod["id"] in BLANK_COLOR_OVERRIDE:
                base["description"] = re.sub(r"\bWhite\b", BLANK_COLOR_OVERRIDE[prod["id"]], base["description"])
                base["title"] = re.sub(r"\bWhite\b", BLANK_COLOR_OVERRIDE[prod["id"]], base["title"])
            multi = len(priced) > 1
            for size, amount in priced:
                row = dict(base)
                row["id"] = f"{prod['id']}-{size}" if multi and size else prod["id"]
                row["title"] = f"{base['title']} - {size}" if multi and size else base["title"]
                row["price"] = f"{amount:.2f} USD"
                row["size"] = size
                writer.writerow(row)
    assert_published_csv_feeds()


def generate_returns_page():
    """Return & exchange policy page for Google Merchant Center (matches Offer JSON-LD)."""
    page = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" href="/favicon.ico" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Returns, Exchanges &amp; Shipping | Apex Hybrid Co.</title>
  <meta name="description" content="Print errors and defects are replaced or refunded. Made-to-order items are not eligible for general returns. Free US shipping from Apex Hybrid Co." />
  <link rel="canonical" href="https://www.apexhybridco.com/returns.html" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="styles.css" />
  <style>.Policy{max-width:760px;margin:0 auto;padding:56px 20px 80px;line-height:1.65}.Policy h1{font-size:34px;margin-bottom:8px}.Policy h2{font-size:21px;margin:34px 0 8px}.Policy ul{padding-left:20px}.Policy a{color:#0066ff;font-weight:600}</style>
</head>
<body>
  <header class="SiteHead"><div class="Wrap" style="padding:16px 20px"><a class="Wordmark" href="index.html"><span class="Wordmark__text"><strong>Apex</strong><span>Hybrid Co.</span></span></a></div></header>
  <main class="Policy">
    <h1>Returns and shipping</h1>
    <p>Apex Hybrid Co., operated by NolCorp LLC. Products are made to order.</p>
    <h2>Print errors and defects</h2>
    <p>A print error or visible quality issue is replaced or refunded. Email <a href="mailto:apexhybridco@gmail.com">apexhybridco@gmail.com</a> with the order number and a photo of the item on a flat, well-lit surface.</p>
    <h2>General returns</h2>
    <p>Made-to-order items are not eligible for general returns or fit exchanges.</p>
    <h2>Shipping</h2>
    <p>Free US shipping. Secure checkout and fulfillment by Fourthwall.</p>
    <p><a href="contact.html">Contact</a> · <a href="about.html">About</a> · <a href="shipping.html">Shipping</a> · <a href="privacy.html">Privacy</a> · <a href="terms.html">Terms</a></p>
    <p><a href="index.html">&larr; Back to the shop</a></p>
  </main>
<script data-goatcounter="https://apexhybridco.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</body>
</html>
"""
    with open(os.path.join(BASE_DIR, "returns.html"), "w", encoding="utf-8") as f:
        f.write(page)

def generate_sitemap_and_robots():
    urls = [
        (f"{SITE_URL}/", "1.0", "daily"),
        (f"{SITE_URL}/team_orders.html", "0.95", "daily"),
        (f"{SITE_URL}/gyms/index.html", "0.95", "daily"),
        (f"{SITE_URL}/directory.html", "0.95", "daily"),
        (f"{SITE_URL}/wristband.html", "0.95", "daily"),
        (f"{SITE_URL}/articles/index.html", "0.9", "daily"),
        (f"{SITE_URL}/gift-guide.html", "0.9", "weekly"),
        (f"{SITE_URL}/returns.html", "0.6", "monthly"),
        (f"{SITE_URL}/contact.html", "0.5", "monthly"),
        (f"{SITE_URL}/about.html", "0.5", "monthly"),
        (f"{SITE_URL}/shipping.html", "0.5", "monthly"),
        (f"{SITE_URL}/privacy.html", "0.4", "yearly"),
        (f"{SITE_URL}/terms.html", "0.4", "yearly"),
    ]
    city_dir = os.path.join(BASE_DIR, "seo_city_pages")
    if os.path.isdir(city_dir):
        for fn in sorted(os.listdir(city_dir)):
            if fn.endswith(".html"):
                urls.append((f"{SITE_URL}/seo_city_pages/{fn}", "0.9", "weekly"))
    for art in guides:
        urls.append((f"{SITE_URL}/articles/{art['slug']}.html", "0.9", "weekly"))
    for prod in products:
        urls.append((f"{SITE_URL}/products/{prod['handle']}.html", "0.8", "weekly"))

    url_entries = "\n".join(
        f"""  <url>
    <loc>{xml_text(u)}</loc>
    <lastmod>{xml_text(TODAY)}</lastmod>
    <changefreq>{xml_text(freq)}</changefreq>
    <priority>{xml_text(prio)}</priority>
  </url>"""
        for u, prio, freq in urls
    )

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{url_entries}
</urlset>
"""
    with open(os.path.join(BASE_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_xml)
    assert_published_xml_parses()

    robots_txt = f"""User-agent: *
Allow: /

# Explicitly allow AI Search & Answer Engines (ChatGPT Search, Perplexity, Grok, Claude, Google, Bing)
User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: GPTBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    with open(os.path.join(BASE_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots_txt)

    # Only this key is accepted by IndexNow. Older key files stay hosted and are not rewritten.
    with open(os.path.join(BASE_DIR, f"{INDEXNOW_KEY}.txt"), "w", encoding="utf-8") as f:
        f.write(INDEXNOW_KEY)

    # Also generate llms.txt dynamically from products and guides
    llms_lines = [
        "# Apex Hybrid Co., operated by NolCorp LLC",
        "",
        f"> Official Storefront: {SITE_URL} (also accessible at https://apexhybridco.com and https://nolan2j-ui.github.io/apex-store/)",
        "> Race shirts, city shirts, muscle tanks, warmup hoodies, and warmup jackets. Made to order. Free US shipping. Secure checkout and fulfillment by Fourthwall.",
        "",
        "## Brand & Merchant Overview",
        "- **Business Name:** Apex Hybrid Co., operated by NolCorp LLC",
        "- **Fulfillment:** Fourthwall. ",
        "- **Support Email:** apexhybridco@gmail.com",
        f"- **Primary Website:** {SITE_URL}/",
        f"- **Doubles 2-Packs, Boutique Gym Bulk Kits & $0-Upfront HYROX Coach Partner Portal:** {SITE_URL}/team_orders.html",
        f"- **HYROX Gym Finder & Certified Coach Directory (72 Verified North America Hubs):** {SITE_URL}/gyms/ (and {SITE_URL}/directory.html)",
        f"- **Free Printable HYROX Race-Day Pace & 8-Station Split Wristband Generator :** {SITE_URL}/wristband.html",
        f"- **XML Sitemap:** {SITE_URL}/sitemap.xml",
        f"- **RSS 2.0 & WebSub Editorial Feed:** {SITE_URL}/feed.xml",
        f"- **RSS 2.0 Mirror Feed:** {SITE_URL}/rss.xml",
        f"- **Google Merchant Shopping Feed:** {SITE_URL}/google_shopping_feed.xml",
        f"- **Pinterest Product Catalog Feed:** {SITE_URL}/pinterest_catalog_feed.csv",
        "- **Shipping Policy:** Free US shipping ($0.00 USD). Made to order. Secure checkout and fulfillment by Fourthwall.",
        "- **Return Policy:** Print errors and defects are replaced or refunded. No general returns.",
        "- **Checkout:** Instant PCI-DSS Level 1 Stripe Checkout (Visa, Mastercard, American Express, Discover, Apple Pay).",
        "",
        "## Doubles 2-Packs, Team Bulk Kits & $0-Upfront Boutique HYROX Coach Partner Program",
        f"- [HYROX Doubles 2-Packs, Boutique Gym Bulk Kits & Coach Partner Portal]({SITE_URL}/team_orders.html): Made to order apparel. Free US shipping. Secure checkout and fulfillment by Fourthwall. Contact: apexhybridco@gmail.com.",
        "",
        f"## Complete Product Catalog ({len(products)} Verified In-Stock SKUs)",
        ""
    ]
    by_dept = {}
    for p in products:
        by_dept.setdefault(p["dept"], []).append(p)
    for dept, items in by_dept.items():
        llms_lines.append(f"### {dept} ({len(items)} SKUs)")
        for p in items:
            llms_lines.append(
                f"- [{p['title']}]({SITE_URL}/products/{p['handle']}.html)  -  **${float(p['retail_price']):.2f} USD** (SKU: `{p['id']}`, Category: {p['category']}, {p['ship_time']}). {p['short_desc']}"
            )
        llms_lines.append("")
    llms_lines.append(f"## Athlete Buyer Guides & Training Protocols ({len(guides)} Articles)")
    llms_lines.append("")
    for g in guides:
        llms_lines.append(
            f"- [{g['title']}]({SITE_URL}/articles/{g['slug']}.html) ({g.get('category', 'Guide')} · {g.get('read_time', '5 min read')}): {g.get('summary', '')}"
        )
    llms_lines.append("")
    with open(os.path.join(BASE_DIR, "llms.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(llms_lines))


def inject_static_seo_into_index():
    index_path = os.path.join(BASE_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        index_html = f.read()

    # Build static product cards so search crawlers index all 68 products + links on the homepage
    static_cards = []
    for p in products:
        badge_html = ""
        whole = int(p["retail_price"])
        cents = f"{round((p['retail_price'] - whole) * 100):02d}"
        static_cards.append(
            f"""          <article class="ProductCard" data-sku="{p['id']}">
            <div>
              <div class="ProductCard__Media" onclick="openProductModal('{p['id']}')">
                {badge_html}
                <img src="{p['image']}" alt="{html.escape(p.get('seo_title', p['title']))}" loading="lazy" />
              </div>
              <div class="ProductCard__Body">
                <div class="ProductCard__Category">{html.escape(p['category'])}</div>
                <h2 class="ProductCard__Title" onclick="openProductModal('{p['id']}')">
                  <a href="products/{p['handle']}.html" onclick="event.stopPropagation();">{html.escape(p['title'])}</a>
                </h2>
                <div class="ProductCard__PriceRow">
                  <span class="PriceWhole"><sup>$</sup>{whole}<sup>{cents}</sup></span>
                </div>
                <div class="ProductCard__Delivery"><strong>{html.escape(p['ship_time'])}</strong></div>
                <div class="ProductCard__Stock">✓ {html.escape(p['stock_status'])}</div>
                <p class="ProductCard__Desc">{html.escape(p['short_desc'])}</p>
              </div>
            </div>
            <div style="padding: 0 16px 16px;">
              <div class="ProductCard__Actions">
                <button class="Btn Btn--Cart" onclick="addToCart('{p['id']}', 1)">Add to Bag</button>
                <a href="products/{p['handle']}.html" class="Btn Btn--QuickView" title="Full Specs">Specs</a>
              </div>
            </div>
          </article>"""
        )

    static_guides = []
    for g in guides:
        static_guides.append(
            f"""        <article class="GuideCard">
          <div>
            <div class="GuideCard__Cat">{html.escape(g['category'])}</div>
            <h3><a href="articles/{g['slug']}.html">{html.escape(g['title'])}</a></h3>
            <p>{html.escape(g['summary'])}</p>
          </div>
          <div class="GuideCard__Footer">
            <span>{html.escape(g['read_time'])}</span>
            <a href="articles/{g['slug']}.html" class="Btn Btn--QuickView" style="width:auto; padding:6px 14px;">Read Full Guide →</a>
          </div>
        </article>"""
        )

    store_schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "OnlineStore",
                "@id": f"{SITE_URL}/#organization",
                "name": "Apex Hybrid Co., operated by NolCorp LLC",
                "url": f"{SITE_URL}/",
                "logo": f"{SITE_URL}/images/streetwear/apc-c36-black.png?v=20261026v1",
                "description": "Race shirts, city shirts, muscle tanks, warmup hoodies, and warmup jackets. Made to order. Free US shipping.",
                "email": "apexhybridco@gmail.com",
            },
            {
                "@type": "WebSite",
                "@id": f"{SITE_URL}/#website",
                "url": f"{SITE_URL}/",
                "name": "Apex Hybrid Co., operated by NolCorp LLC  -  HYROX Shirts, Breathable Race Apparel & Recovery Lab",
                "publisher": {"@id": f"{SITE_URL}/#organization"},
            },
            {
                "@type": "FAQPage",
                "@id": f"{SITE_URL}/#faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "What are the best breathable HYROX shirts for race day?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Built For Heavy Legs (APC-C36) is a 6.1 oz ring-spun cotton tee. 1KM Split, Aerobic Engine, Push Heavy Run Fast, and Roxzone Speed Dept. are 6.1 oz ring-spun cotton tees in Tees & Pump Covers. Made to order. Free US shipping."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "Do you carry 2026/2027 HYROX race-city shirts for Chicago, Dallas, Anaheim, Miami, Las Vegas, and New York?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Yes. Our Race City Editions collection includes Winged Apex Crest tees for Chicago Navy Pier (APC-C16), Dallas Lone Star Division (APC-C17), Anaheim SoCal (APC-C18), Miami Beach (APC-C19), Las Vegas (APC-C20), and New York Hudson Pier (APC-C21). They are made to order, ship from the US, UK, EU or Canada. Free US shipping."
                        }
                    }
                ]
            },
            {
                "@type": "ItemList",
                "name": "Apex Hybrid Co., operated by NolCorp LLC Full Catalog",
                "numberOfItems": len(products),
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": idx + 1,
                        "url": f"{SITE_URL}/products/{p['handle']}.html",
                        "name": p.get("seo_title", p["title"]),
                    }
                    for idx, p in enumerate(products)
                ],
            },
        ],
    }

    index_html = re.sub(
        r'<div class="ProductGrid" id="productGrid">.*?</div>\s*</div>\s*</div>\s*</div>\s*</main>',
        lambda m: f'<div class="ProductGrid" id="productGrid">\n{chr(10).join(static_cards)}\n          </div>\n        </div>\n      </div>\n    </div>\n  </main>',
        index_html,
        flags=re.DOTALL,
    )

    index_html = re.sub(
        r'<div class="GuidesGrid" id="guidesGrid">.*?</div>\s*</div>\s*</section>',
        lambda m: f'<div class="GuidesGrid" id="guidesGrid">\n{chr(10).join(static_guides)}\n      </div>\n    </div>\n  </section>',
        index_html,
        flags=re.DOTALL,
    )

    schema_block = f'  <script type="application/ld+json" id="seoSchemaJsonLd">\n{json.dumps(store_schema, indent=2)}\n  </script>\n</head>'
    if 'id="seoSchemaJsonLd"' in index_html:
        index_html = re.sub(
            r'\s*<script type="application/ld\+json" id="seoSchemaJsonLd">.*?</script>\s*</head>',
            lambda m: "\n" + schema_block,
            index_html,
            flags=re.DOTALL,
        )
    else:
        index_html = index_html.replace("</head>", schema_block)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)



DELISTED_NOINDEX_HANDLES = ["apc-c04", "apc-c39"]

def enforce_delisted_noindex():
    """Delisted SKUs: robots noindex,nofollow, no Product JSON-LD, never in sitemap."""
    import re as _re, json as _json
    for h in DELISTED_NOINDEX_HANDLES:
        fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "products", f"{h}.html")
        if not os.path.exists(fp):
            continue
        s = open(fp, encoding="utf-8").read()
        s = _re.sub(r'\s*<meta name="robots"[^>]*>', "", s)
        s = s.replace("<head>", '<head>\n  <meta name="robots" content="noindex,nofollow" />', 1)
        def _strip(m):
            try:
                d = _json.loads(m.group(1))
            except Exception:
                return m.group(0)
            if isinstance(d, dict) and "@graph" in d:
                d["@graph"] = [g for g in d["@graph"] if g.get("@type") != "Product"]
                if not d["@graph"]:
                    return ""
                return '<script type="application/ld+json">\n' + _json.dumps(d, indent=2) + '\n</script>'
            if isinstance(d, dict) and d.get("@type") == "Product":
                return ""
            return m.group(0)
        s = _re.sub(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', _strip, s, flags=_re.S)
        open(fp, "w", encoding="utf-8").write(s)
    sm = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sitemap.xml")
    if os.path.exists(sm):
        x = open(sm, encoding="utf-8").read()
        for h in DELISTED_NOINDEX_HANDLES:
            x = _re.sub(r'\s*<url>\s*<loc>[^<]*/products/' + h + r'\.html</loc>.*?</url>', "", x, flags=_re.S)
        open(sm, "w", encoding="utf-8").write(x)

# Whole-token rewrites. Fabric words are only removed after these slugs are
# rewritten, so a rebuild cannot split a product URL again.
SLUG_REWRITES = (
    ("aeromesh-breathable-breathable-hyrox-race-tech-tee", "compromised-running"),
    ("aeromesh-laser-vented-breathable-hyrox-race-tech-tee", "compromised-running"),
    ("coolcore--turf-and-sled-breathable-tech-shirt", "push-heavy"),
    ("coolcore-anti-chafe-turf-and-sled-breathable-tech-shirt", "push-heavy"),
    ("dry-pace--threshold-hyrox-tech-tee", "1km-split"),
    ("dry-pace-moisture-wicking-threshold-hyrox-tech-tee", "1km-split"),
    ("hyperbreathe--roxzone-speed-dept-tech-tee", "roxzone-speed-dept"),
    ("hyperbreathe-seamless-roxzone-speed-dept-tech-tee", "roxzone-speed-dept"),
    ("venttech-perforated-zone4-zone5-hybrid-training-shirt", "zone-5-engine"),
    ("aeromeshtm-breathable-breathable-tech-shirt-built-for-compromised-running", "compromised-running-tech-shirt"),
    ("aeromeshtm-laser-vented-breathable-tech-shirt-built-for-compromised-running", "compromised-running-tech-shirt"),
    ("coolcoretm--turf-sled-tech-shirt-push-heavy-run-fast", "push-heavy-run-fast-tech-shirt"),
    ("coolcoretm-anti-chafe-turf-sled-tech-shirt-push-heavy-run-fast", "push-heavy-run-fast-tech-shirt"),
    ("dry-pacetm--threshold-tech-tee-1km-split-station-repeat", "1km-split-station-repeat-tech-tee"),
    ("dry-pacetm-moisture-wicking-threshold-tech-tee-1km-split-station-repeat", "1km-split-station-repeat-tech-tee"),
    ("hyperbreathetm--conditioning-tee-roxzone-speed-dept", "roxzone-speed-dept-tee"),
    ("hyperbreathetm-seamless-conditioning-tee-roxzone-speed-dept", "roxzone-speed-dept-tee"),
    ("venttechtm-perforated-hybrid-training-shirt-zone-4-zone-5-engine", "zone-4-zone-5-engine-shirt"),
)


def scrub_text(text):
    """Repair product links, then drop claims that must not appear on the site."""
    text = text.replace(
        "27_aeromesh_tech_tee_black.png",
        "streetwear/apc-c36-black.jpg",
    )
    for old, new in SLUG_REWRITES:
        text = text.replace(old, new)
    for city in ("Dallas", "Denver", "Anaheim", "Nashville", "Vancouver"):
        name = f"{city} Race Day"
        text = text.replace(f"Apex {name} Jacket | Apex Hybrid Co", name)
        text = text.replace(f"Apex {name} Jacket", name)
        text = text.replace(f"Apex &quot;{name}&quot;", name)
        text = text.replace(f'Apex "{name}"', name)
        text = text.replace(f"Apex {name}", name)
    text = text.replace(chr(8482), "")
    text = text.replace("&" + "trade;", "").replace("&" + "#8482;", "").replace("&" + "#x2122;", "")
    text = re.sub(r"(?i)aeromesh", "Built For Heavy Legs", text)
    text = re.sub(r"(?i)coolcore", "Push Heavy Run Fast", text)
    text = re.sub(r"(?i)venttech", "Aerobic Engine", text)
    text = re.sub(r"(?i)dry-pace", "1km Split", text)
    text = re.sub(r"(?i)hyperbreathe", "Roxzone Speed Dept.", text)
    text = re.sub(r"(?i)laser-vented", "breathable", text)
    text = re.sub(r"(?i)anti-chafe", "", text)
    text = re.sub(r"(?i)moisture-wicking", "", text)
    text = re.sub(r"(?i)seamlessly", "cleanly", text)
    text = re.sub(r"(?i)seamless", "", text)
    text = re.sub(r"(?i)official hyrox", "HYROX", text)
    text = text.replace(
        "Because Apex Hybrid Co., operated by NolCorp LLC is headquartered in Irvine, CA (Orange County) with California fulfillment, Anaheim and SoCal orders arrive in 1–3 business days with free shipping.",
        "Made to order. Free US shipping.",
    )
    text = re.sub(r"(?i)headquartered in [^.<]*", "Made to order", text)
    text = re.sub(r"(?i)headquartered", "", text)
    text = re.sub(r"(?i)with California fulfillment", "", text)
    text = re.sub(r"(?i)California fulfillment", "", text)
    text = re.sub(
        r"(?i)from our California, Texas, and East Coast fulfillment centers",
        "",
        text,
    )
    text = re.sub(r"(?i)Texas & California fulfillment hubs", "", text)
    text = re.sub(r"(?i)Clinical Recovery Hardware · Direct US Warehouse Dispatch", "", text)
    text = re.sub(r"(?i)Clinical Recovery Hardware", "", text)
    text = re.sub(r"(?i)30-Day Trial &amp; Warranty", "", text)
    text = re.sub(r"(?i)30-Day Trial & Warranty", "", text)
    text = re.sub(r"(?i)30-day free exchanges", "Print errors and defects are replaced or refunded", text)
    text = re.sub(r"(?i)\bIrvine\b(?!\s*(?:and|&|/)\s*Costa)", "", text)
    text = re.sub(r"(?i)warehouse", "", text)
    text = re.sub(r"(?i)clinical", "", text)
    text = re.sub(r"(?i)30-day", "", text)
    text = re.sub(
        r"(?i)Just 20 minutes north of our[^,]*,\s*CA headquarters,\s*",
        "",
        text,
    )
    text = re.sub(r"(?i)headquarters", "", text)
    text = re.sub(r"(?i)Designed in\s*,\s*CA\s*[-–]\s*", "", text)
    text = text.replace("Newport Beach / , CA", "Newport Beach, CA")
    text = text.replace("Newport Beach / , ca", "Newport Beach, CA")
    text = text.replace("e.g. , CA", "e.g. your city")
    text = re.sub(r"\s+, CA\b", "", text)
    text = re.sub(r"\s+, ca\b", "", text)
    text = text.replace("Carbon Black and Warm Bone colorways", "Carbon Black")
    text = text.replace("Carbon Black and Warm Bone", "Carbon Black")
    text = text.replace("Carbon Black or Warm Bone", "Carbon Black")
    text = text.replace("in Carbon Black and Warm Bone", "in Carbon Black")
    text = re.sub(r"(?i)Vintage Black and Bone White", "black", text)
    text = re.sub(r"(?i)Vintage Black \+ Bone White", "black", text)
    text = re.sub(r"(?i)Black \+ Bone White", "black", text)
    text = re.sub(r"(?i)Bone White", "black", text)
    text = re.sub(r"(?i)black or bone", "in black", text)
    text = re.sub(r"(?i)Black or Bone", "Carbon Black", text)
    text = re.sub(r'"Warm Bone"\s*,\s*', "", text)
    text = re.sub(r',\s*"Warm Bone"', "", text)
    text = text.replace("Warm Bone", "Carbon Black")
    text = text.replace("white/bone", "other colors")
    text = text.replace("Btn--bone", "Btn--plain")
    text = text.replace("Swatch--bone", "Swatch--light")
    text = re.sub(r"(?i)\s*\(plus lightweight\s+3\.8\s*-?\s*oz[^)]*\)", "", text)
    text = re.sub(r"(?i)\s*OR lightweight\s+3\.8\s*-?\s*oz breathable workout knit", "", text)
    text = re.sub(r"(?i)Ultra-Light\s+3\.8\s*-?\s*oz\s*(?:&amp;|&)\s*", "", text)
    text = text.replace("3.8\\u20134.0 oz", "lightweight")
    text = text.replace("3.8\\u20134.2 oz", "lightweight")
    text = re.sub(r"(?i)3\.8\s*[\u2013\-]\s*4\.\d\s*-?\s*oz", "lightweight", text)
    text = re.sub(r"(?i)3\.8\s*-?\s*oz", "", text)
    text = re.sub(r"(?i)3\.8\s*[\u2013\-]\s*", "lightweight ", text)
    text = text.replace(" (or  warmup fleece)", "")
    text = text.replace("(or  warmup fleece)", "")
    text = re.sub(r"(?i)ASICS-style", "", text)
    text = re.sub(r"(?i)\bASICS\b", "", text)
    text = re.sub(
        r"(?i)\b(?:4\.0|4\.2|4\.3|6\.5|8\.0|8\.5|9\.0|14)\s*oz(?:/yd²|/yd\u00b2)?",
        "",
        text,
    )
    text = re.sub(r"(?i)\b9\s*oz\b", "", text)
    text = re.sub(r"(?i)6\.0\s+to\s+6\.5\s*oz(?:/yd²|/yd\u00b2)?", "", text)
    text = re.sub(
        r"(?i)sweat-wicking\s+60/40 combed ringspun cotton/poly performance blend",
        "100% ring-spun cotton, 6.1 oz",
        text,
    )
    text = text.replace("Heavyweight ring-spun cotton/poly brushed warmup fleece", "brushed fleece")
    text = text.replace("8-Station Race Day 50L All-Weather Gym &amp; Shoe Bag", "8-Station Haul")
    text = text.replace("8-Station Race Day 50L All-Weather Gym & Shoe Bag", "8-Station Haul")
    text = text.replace("8-Station Race Day 50L gym and shoe bag", "8-Station Haul")
    text = text.replace("8-Station 50L Race Day Duffle", "8-Station Haul")
    text = text.replace("8-Station 50L gym and shoe bag", "8-Station Haul")
    text = text.replace("8-Station race day duffle", "8-Station Haul")
    text = text.replace("50L Race Day Tactical Duffle", "8-Station Haul")
    text = text.replace("50L Tactical Duffle", "8-Station Haul")
    text = text.replace("50L Race Day Duffle", "8-Station Haul")
    text = text.replace("50L Race Duffles", "8-Station Haul")
    text = text.replace("8-Station race duffle", "8-Station Haul")
    text = text.replace("8-Station Race Day bag", "8-Station Haul")
    text = text.replace("8-Station 50L bag", "8-Station Haul")
    return apply_copy_repairs(text)


def scrub_published_files():
    """Keep a rebuild from writing mangled product links or retired claims."""
    exts = {".html", ".js", ".json", ".xml", ".csv", ".txt", ".css", ".md"}
    for dirpath, dirnames, filenames in os.walk(BASE_DIR):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue
        for name in filenames:
            path = os.path.join(dirpath, name)
            if os.path.splitext(name)[1].lower() not in exts:
                continue
            if os.path.abspath(path) == os.path.abspath(__file__):
                continue
            original = open(path, encoding="utf-8").read()
            updated = scrub_text(original)
            if updated != original:
                open(path, "w", encoding="utf-8").write(updated)


if __name__ == "__main__":
    generate_product_pages()
    generate_article_pages()
    generate_google_shopping_feed()
    generate_editorial_rss_feeds()
    generate_pinterest_csv_feed()
    generate_returns_page()
    generate_sitemap_and_robots()
    enforce_delisted_noindex()
    scrub_published_files()
    assert_published_xml_parses()
    assert_published_csv_feeds()
    # inject_static_seo_into_index() disabled to preserve clean index.html
    print(f"Successfully generated {len(products)} product pages, {len(guides)} SEO articles, Shopping XML/CSV feeds, and sitemap.xml")
