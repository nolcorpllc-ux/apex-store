#!/usr/bin/env python3
"""Pull live Fourthwall variants for the Merchant Center feed.

Fourthwall is the source of truth for sizes, colors, prices and stock. This
reads the public schema.org Offer list on each product's Fourthwall page and
writes fourthwall_feed_variants.json, which build_seo_and_feeds.py uses for
google_shopping_feed.xml / google_merchant_feed.xml.

Run before rebuilding the feed:  python3 sync_fourthwall_feed_variants.py
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE_DIR, "fourthwall_feed_variants.json")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (apexhybridco feed sync)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def offers_from_page(page):
    for block in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', page, re.S):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        for node in data if isinstance(data, list) else [data]:
            if isinstance(node, dict) and node.get("@type") == "Product" and node.get("offers"):
                offers = node["offers"]
                return offers if isinstance(offers, list) else [offers]
    return []


def main():
    catalog = json.load(open(os.path.join(BASE_DIR, "catalog.json"), encoding="utf-8"))
    out = {"pulled": datetime.now(timezone.utc).isoformat(timespec="seconds"), "source": "Fourthwall product page schema.org offers", "products": {}}
    failures = []
    for prod in catalog["products"]:
        pid = str(prod.get("id", ""))
        url = (prod.get("fourthwall_product_url") or "").split("?")[0]
        if not pid.startswith("APC-C") or not url:
            continue
        try:
            offers = offers_from_page(fetch(url))
        except Exception as exc:  # network error: keep going, report below
            failures.append(f"{pid}: {exc}")
            continue
        variants = []
        for o in offers:
            name = o.get("name") or ""
            color, _, size = name.rpartition(",")
            if not color:
                color, size = "", name
            vid = ""
            m = re.search(r"variant=([0-9a-f-]{36})", o.get("url") or "")
            if m:
                vid = m.group(1)
            variants.append({
                "color": color.strip(),
                "size": size.strip(),
                "variant_id": vid,
                "price": float(o.get("price")),
                "currency": o.get("priceCurrency") or "USD",
                "in_stock": (o.get("availability") or "").endswith("InStock"),
            })
        if not variants:
            failures.append(f"{pid}: no offers found on {url}")
            continue
        out["products"][pid] = {"url": url, "variants": variants}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(f"Fourthwall feed variants: {len(out['products'])} products written to {OUT}")
    for line in failures:
        print("  FAIL", line)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
