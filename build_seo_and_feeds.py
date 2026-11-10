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
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://www.apexhybridco.com"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
INDEXNOW_KEY = "b7e3c9a4d2f841069c5e1a8f3b2d6e40"

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
    if dept == "Lightweight Jackets":
        return "Apparel & Accessories > Clothing > Outerwear > Coats & Jackets"
    if dept == "Training Gear":
        return "Sporting Goods > Exercise & Fitness"
    return "Health & Beauty > Health Care > Massage & Relaxation"


def generate_product_pages():
    for prod in products:
        handle = prod["handle"]
        title = prod["title"]
        seo_title = prod.get("seo_title", f"{title}  -  HYROX & Hybrid Race Gear")
        price = f"{prod['retail_price']:.2f}"
        list_price = f"{(prod.get('list_price') or prod['retail_price']):.2f}"
        img_url = f"{SITE_URL}/{prod['image']}"
        canonical = f"{SITE_URL}/products/{handle}.html"
        short_desc = prod["short_desc"]
        highlights = prod.get("highlights", [])
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
                    "image": [img_url] + ([f"{SITE_URL}/{prod['alt_image']}"] if prod.get("alt_image") else []),
                    "description": short_desc + " " + " ".join(highlights),
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
                                "handlingTime": {"@type": "QuantitativeValue", "minValue": 1, "maxValue": 2, "unitCode": "DAY"},
                                "transitTime": {"@type": "QuantitativeValue", "minValue": 2, "maxValue": 5, "unitCode": "DAY"},
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
                  <span class="PriceList">${(r.get('list_price') or r['retail_price']):.2f}</span>
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

        page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(seo_title)} | Apex Hybrid Co., operated by NolCorp LLC</title>
  <meta name="description" content="{html.escape(short_desc)} Free US Ground Shipping &amp; 30-Day Returns at Apex Hybrid Co." />
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
          <span class="BrandLogo__Sub">HYBRID &amp; RECOVERY CO.</span>
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
            <span>1. Black Edition (Front Crest)</span>
          </button>
          <button type="button" onclick="document.getElementById('staticMainProdImg').src='../{prod['alt_image']}'" style="cursor:pointer; border:2px solid #cbd5e1; border-radius:8px; padding:6px; background:#f8fafc; color:#0f172a; display:flex; align-items:center; gap:8px; font-weight:700; font-size:12.5px;">
            <img src="../{prod['alt_image']}" alt="{html.escape(title)}  -  Bone Edition View" style="width:48px; height:48px; object-fit:cover; border-radius:4px;" />
            <span>2. Black Edition</span>
          </button>
        </div>''' if prod.get("alt_image") else ""}
      </div>
      <div>
        <div style="font-size:11.5px; font-weight:800; color:#0066ff; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px;">
          {html.escape(dept)} · {html.escape(prod['category'])}
        </div>
        <h1 style="font-size:24px; line-height:1.25; margin-bottom:10px;">{html.escape(title)}</h1>
        <div style="display:flex; align-items:center; gap:8px; font-size:13px; margin-bottom:12px;">
          <span class="Stars">★★★★★</span>
          <strong>{prod['rating']} out of 5</strong>
          <span style="color:#525866;">({prod['reviews']} verified athlete reviews)</span>
        </div>
        <div style="padding:12px 0; border-top:1px solid #eee; border-bottom:1px solid #eee; margin-bottom:14px;">
          <div style="display:flex; align-items:baseline; gap:10px;">
            <span style="font-size:28px; font-weight:900;">${price}</span>
            <span style="font-size:14px; color:#525866; ">List: ${list_price}</span>
          </div>
          <div style="font-size:13px; color:#0e8345; font-weight:700; margin-top:4px;">
            ✓ {html.escape(prod['stock_status'])} · {html.escape(prod['ship_time'])}
          </div>
          {fulfillment_line}
        </div>
        <div id="staticVariantBox" style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:14px 16px; margin-bottom:16px;">
          {f"""<div style="margin-bottom:12px;">
            <div style="font-size:11.5px; font-weight:800; text-transform:uppercase; letter-spacing:0.05em; color:#0f172a; margin-bottom:6px;">1. Select Colorway: <span id="staticColorLabel" style="color:#0066ff;">Black</span></div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
              <button type="button" class="StaticColorBtn" data-color="Black" onclick="window.selectStaticColor('Black','../{prod['image']}',this)" style="cursor:pointer; padding:7px 14px; border-radius:6px; border:2px solid #0f172a; background:#0f172a; color:#fff; font-weight:800; font-size:12.5px;">Black</button>
              <button type="button" class="StaticColorBtn" data-color="White" onclick="window.selectStaticColor('White','../{prod.get('alt_image') or prod['image']}',this)" style="cursor:pointer; padding:7px 14px; border-radius:6px; border:1.5px solid #cbd5e1; background:#fff; color:#0f172a; font-weight:700; font-size:12.5px;">Black</button>
            </div>
          </div>""" if prod.get("alt_image") else ""}
          {f"""<div style="margin-bottom:12px;">
            <div style="font-size:11.5px; font-weight:800; text-transform:uppercase; letter-spacing:0.05em; color:#0f172a; margin-bottom:6px;">2. Select Shirt Blank / Material: <span id="staticBlankLabel" style="color:#0066ff;">{"3.8 oz Breathable Workout Tee" if dept == "Breathable Tech Shirts" else "6.1 oz Heavyweight Cotton"}</span></div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:8px;">
              <button type="button" class="StaticBlankBtn" data-blank="6.1 oz Heavyweight Cotton" onclick="window.selectStaticBlank('6.1 oz Heavyweight Cotton',this)" style="cursor:pointer; text-align:left; padding:9px 12px; border-radius:8px; border:{'1.5px solid #cbd5e1' if dept == 'Breathable Tech Shirts' else '2px solid #0f172a'}; background:{'#fff' if dept == 'Breathable Tech Shirts' else '#0f172a'}; color:{'#0f172a' if dept == 'Breathable Tech Shirts' else '#fff'};">
                <div style="font-weight:800; font-size:12.5px;">6.1 oz Heavyweight Cotton</div>
                <div style="font-size:11px; opacity:0.82;">Structured garment-dyed street &amp; pump cover drape</div>
              </button>
              <button type="button" class="StaticBlankBtn" data-blank="3.8 oz Breathable Workout Tee" onclick="window.selectStaticBlank('3.8 oz Breathable Workout Tee',this)" style="cursor:pointer; text-align:left; padding:9px 12px; border-radius:8px; border:{'2px solid #0f172a' if dept == 'Breathable Tech Shirts' else '1.5px solid #cbd5e1'}; background:{'#0f172a' if dept == 'Breathable Tech Shirts' else '#fff'}; color:{'#fff' if dept == 'Breathable Tech Shirts' else '#0f172a'};">
                <div style="font-weight:800; font-size:12.5px;">3.8 oz Breathable Workout Tee</div>
                <div style="font-size:11px; opacity:0.82;">Sweat-wicking race &amp; turf training technical knit</div>
              </button>
            </div>
          </div>""" if dept in ("Tees & Pump Covers", "Race City Editions", "Breathable Tech Shirts") else ""}
          {f"""<div style="margin-bottom:14px;">
            <div style="font-size:11.5px; font-weight:800; text-transform:uppercase; letter-spacing:0.05em; color:#0f172a; margin-bottom:6px;">Select Size (Unisex Athletic Fit): <span id="staticSizeLabel" style="color:#0066ff;">L</span></div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
              <button type="button" class="StaticSizeBtn" data-size="S" onclick="window.selectStaticSize('S',this)" style="cursor:pointer; min-width:44px; padding:8px 12px; border-radius:6px; border:1.5px solid #cbd5e1; background:#fff; color:#0f172a; font-weight:800; font-size:13px;">S</button>
              <button type="button" class="StaticSizeBtn" data-size="M" onclick="window.selectStaticSize('M',this)" style="cursor:pointer; min-width:44px; padding:8px 12px; border-radius:6px; border:1.5px solid #cbd5e1; background:#fff; color:#0f172a; font-weight:800; font-size:13px;">M</button>
              <button type="button" class="StaticSizeBtn" data-size="L" onclick="window.selectStaticSize('L',this)" style="cursor:pointer; min-width:44px; padding:8px 12px; border-radius:6px; border:2px solid #0f172a; background:#0f172a; color:#fff; font-weight:800; font-size:13px;">L</button>
              <button type="button" class="StaticSizeBtn" data-size="XL" onclick="window.selectStaticSize('XL',this)" style="cursor:pointer; min-width:44px; padding:8px 12px; border-radius:6px; border:1.5px solid #cbd5e1; background:#fff; color:#0f172a; font-weight:800; font-size:13px;">XL</button>
              <button type="button" class="StaticSizeBtn" data-size="2XL" onclick="window.selectStaticSize('2XL',this)" style="cursor:pointer; min-width:44px; padding:8px 12px; border-radius:6px; border:1.5px solid #cbd5e1; background:#fff; color:#0f172a; font-weight:800; font-size:13px;">2XL</button>
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
          <div style="font-weight:800; color:#0f172a; text-transform:uppercase; letter-spacing:0.04em; font-size:12px; margin-bottom:6px;">✓ Fit, Fabric &amp; Race-Day Guarantee</div>
          <div>Made to order. Free US shipping. Print errors and defects are replaced or refunded. Secure checkout and fulfillment by Fourthwall.</div>
        </div>
        <div class="ReviewSnippetBox">
          <strong>★★★★★ Verified HYROX &amp; Hybrid Athlete Review:</strong><br/>
          “{html.escape(prod.get('review_quote', ''))}”
        </div>
        <div style="display:flex; gap:10px; margin-top:16px; flex-wrap:wrap;">
          <a href="../index.html?add={prod['id']}" class="Btn Btn--Cart" style="padding:13px 22px; font-size:14px; text-align:center;">Add to Bag  -  ${price}</a>
          <a href="{buy_href}" class="Btn Btn--BuyNow" style="padding:13px 22px; font-size:14px; text-align:center;">{main_buy_label}</a>
        </div>
        <div style="margin-top:16px;background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:#f8fafc;border:1.5px solid #0066ff;border-radius:10px;padding:14px 16px;">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:6px;">
            <span style="font-size:11px;font-weight:900;text-transform:uppercase;color:#38bdf8;letter-spacing:0.06em;">⚡ 2026 Race-Week Express US Dispatch (Chicago · Dallas · Anaheim)</span>
            <span style="font-size:11.5px;color:#4ade80;font-weight:800;">✓ 2–4 Day US Delivery</span>
          </div>
          <p style="font-size:12.5px;color:#cbd5e1;margin:0 0 10px;line-height:1.45;">Free US shipping. Secure checkout and fulfillment by Fourthwall.</p>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <a href="../team_orders.html" style="background:#0066ff;color:#fff;text-decoration:none;padding:6px 11px;border-radius:6px;font-size:12px;font-weight:800;">Shop Doubles 2-Packs (15% Off) →</a>
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
  <!-- Sticky HYROX10 + Free Printable Split Wristband + Gym Directory Conversion Bar -->
  <div id="apexStickyPromoBar" style="position:fixed;bottom:0;left:0;right:0;z-index:90;background:linear-gradient(90deg,#0f172a 0%,#1e293b 55%,#0f172a 100%);color:#f8fafc;border-top:2px solid #0066ff;padding:9px 14px;box-shadow:0 -6px 24px rgba(0,0,0,0.38);font-family:system-ui,-apple-system,sans-serif;">
    <div style="max-width:1240px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 14px;font-size:12.5px;">
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <span style="background:#0066ff;color:#fff;font-weight:900;font-size:10.5px;padding:3px 8px;border-radius:999px;text-transform:uppercase;letter-spacing:0.07em;">Race-Week Perks</span>
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
    var prodId = {json.dumps(prod['id'])};
    var prodVariants = {json.dumps(prod.get('fourthwall_variants', {}))};
    var defaultVid = {json.dumps(prod.get('fourthwall_default_variant_id', ''))};
    var fallbackUrl = {json.dumps(buy_href)};
    var fwSlugs = {json.dumps(fw_slugs_map)};
    var state = {{
      color: "Black",
      size: {json.dumps("L" if prod.get("has_sizes") else "One Size")},
      blank: {json.dumps("3.8 oz Breathable Workout Tee" if dept == "Breathable Tech Shirts" else "6.1 oz Heavyweight Cotton")}
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
    function getSelectedVariantId() {{
      var byColor = prodVariants[state.color] || prodVariants["Black"] || prodVariants["Default"] || {{}};
      return byColor[state.size] || byColor["L"] || byColor["One Size"] || defaultVid;
    }}
    function redirectFourthwallVariant(vid, triggerEl, fbHref) {{
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
          window.location.href = "https://apex-hybrid-co-shop.fourthwall.com/checkout/" + encodeURIComponent(chk.id);
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
      var hit = function(k){{ if (!isBot) fetch(ns + "/" + k, {{method:"GET", mode:"cors", keepalive:true, cache:"no-store"}}).catch(function(){{}}); }};
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
        with open(os.path.join(BASE_DIR, "products", f"{handle}.html"), "w", encoding="utf-8") as out:
            out.write(page_html)
        sku_lower = prod["id"].lower()
        with open(os.path.join(BASE_DIR, "products", f"{sku_lower}.html"), "w", encoding="utf-8") as out_sku:
            out_sku.write(page_html)
        if prod["id"] == "APC-C18":
            with open(os.path.join(BASE_DIR, "products", "apc-c18-anaheim-socal-tee.html"), "w", encoding="utf-8") as out_c18:
                out_c18.write(page_html)


def generate_article_pages():
    for art in guides:
        slug = art["slug"]
        title = art["title"]
        cat = art["category"]
        summary = art["summary"]
        canonical = f"{SITE_URL}/articles/{slug}.html"
        rec_skus = art.get("recommended_skus", [])
        rec_products = [product_by_id[s] for s in rec_skus if s in product_by_id]
        if not rec_products:
            rec_products = [product_by_id[s] for s in ("APC-C36", "APC-C42", "APC-E01", "APC-E12") if s in product_by_id]

        hero_prod = rec_products[0]
        hero_img = f"{SITE_URL}/{hero_prod['image']}"
        faqs = art.get("faqs", [
            (
                f"What is the top-rated gear for {cat}?",
                f"Our highest-rated choices are {hero_prod['title']} (${hero_prod['retail_price']:.2f}, SKU {hero_prod['id']}) alongside our AeroMesh Laser-Vented Tech Shirt (APC-C36, $36) and Apex AeroShell Lightweight Warmup Jacket (APC-C42, $64) - all shipping free in 2–4 business days."
            ),
            (
                "How do I get 15% off Doubles or multi-item race orders?",
                "Add any 2 or more items to your bag at Apex Hybrid Co., operated by NolCorp LLC and apply code  at checkout for 15% off plus Free 2–4 Day US Shipping and 30-Day Free Returns."
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
                <span style="color:#94a3b8;font-size:12px;">★ {p['rating']} ({p['reviews']} reviews) · <strong style="color:#4ade80;">${p['retail_price']:.2f}</strong> · Free 2–4 Day US Shipping</span>
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
                  <div style="font-size:12px;color:#0e8345;font-weight:700;margin-bottom:8px;">Made to order · Free US shipping</div>
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
          <span class="BrandLogo__Sub">HYBRID &amp; RECOVERY CO.</span>
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
      <div class="ArticleEyebrow">{html.escape(cat)} · {html.escape(art['read_time'])} · Free 2–4 Day US Shipping</div>
      <h1 style="font-size:28px; line-height:1.22; margin:8px 0 14px;">{html.escape(title)}</h1>
      <p style="font-size:16px; color:#444; border-left:3px solid #0066ff; padding-left:14px; margin-bottom:20px;">
        {html.escape(summary)}
      </p>

      <!-- Top Quick-Buy Express Checkout Strip -->
      <section aria-label="Express 1-Click Checkout" style="background:#0f172a;color:#fff;padding:16px 18px;border-radius:10px;margin-bottom:26px;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
          <span style="font-size:12px;font-weight:900;text-transform:uppercase;letter-spacing:0.08em;color:#38bdf8;">⚡ Featured Gear In This Guide  -  Instant 1-Click Checkout</span>
          <span style="font-size:12px;color:#cbd5e1;">Bundle 2+ Items: Use Code <strong style="color:#fff;"></strong> for 15% Off + Free US Shipping</span>
        </div>
        <div style="display:grid;gap:8px;">
{top_strip_pills}
        </div>
      </section>
        <div style="margin-top:16px;background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:#f8fafc;border:1.5px solid #0066ff;border-radius:10px;padding:14px 16px;">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:6px;">
            <span style="font-size:11px;font-weight:900;text-transform:uppercase;color:#38bdf8;letter-spacing:0.06em;">⚡ 2026 Race-Week Express US Dispatch (Chicago · Dallas · Anaheim)</span>
            <span style="font-size:11.5px;color:#4ade80;font-weight:800;">✓ 2–4 Day US Delivery</span>
          </div>
          <p style="font-size:12.5px;color:#cbd5e1;margin:0 0 10px;line-height:1.45;">Free US shipping. Secure checkout and fulfillment by Fourthwall.</p>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <a href="../team_orders.html" style="background:#0066ff;color:#fff;text-decoration:none;padding:6px 11px;border-radius:6px;font-size:12px;font-weight:800;">Shop Doubles 2-Packs (15% Off) →</a>
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
  <!-- Sticky HYROX10 + Free Printable Split Wristband + Gym Directory Conversion Bar -->
  <div id="apexStickyPromoBar" style="position:fixed;bottom:0;left:0;right:0;z-index:90;background:linear-gradient(90deg,#0f172a 0%,#1e293b 55%,#0f172a 100%);color:#f8fafc;border-top:2px solid #0066ff;padding:9px 14px;box-shadow:0 -6px 24px rgba(0,0,0,0.38);font-family:system-ui,-apple-system,sans-serif;">
    <div style="max-width:1240px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 14px;font-size:12.5px;">
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <span style="background:#0066ff;color:#fff;font-weight:900;font-size:10.5px;padding:3px 8px;border-radius:999px;text-transform:uppercase;letter-spacing:0.07em;">Race-Week Perks</span>
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
          window.location.href = "https://apex-hybrid-co-shop.fourthwall.com/checkout/" + encodeURIComponent(chk.id);
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
          <span class="BrandLogo__Sub">HYBRID &amp; RECOVERY CO.</span>
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
      <p><strong>Apex Hybrid Co., operated by NolCorp LLC</strong> · <a href="../index.html" style="color:#38bdf8;">Return to Storefront</a></p>
    </div>
  <!-- Sticky HYROX10 + Free Printable Split Wristband + Gym Directory Conversion Bar -->
  <div id="apexStickyPromoBar" style="position:fixed;bottom:0;left:0;right:0;z-index:90;background:linear-gradient(90deg,#0f172a 0%,#1e293b 55%,#0f172a 100%);color:#f8fafc;border-top:2px solid #0066ff;padding:9px 14px;box-shadow:0 -6px 24px rgba(0,0,0,0.38);font-family:system-ui,-apple-system,sans-serif;">
    <div style="max-width:1240px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 14px;font-size:12.5px;">
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
        <span style="background:#0066ff;color:#fff;font-weight:900;font-size:10.5px;padding:3px 8px;border-radius:999px;text-transform:uppercase;letter-spacing:0.07em;">Race-Week Perks</span>
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


def catalog_size_variant_ids(prod):
    """Sold size -> Fourthwall variant id from catalog.json.

    Read the Black map or a flat size map. Ignore White and Default keys:
    those copies reuse the same variant ids and are not evidence of color.
    """
    fv = prod.get("fourthwall_variants") or {}
    if not isinstance(fv, dict) or not fv:
        return {}
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
    if variant_price == retail and list_price > retail:
        return money_usd(list_price), money_usd(variant_price)
    return money_usd(variant_price), money_usd(variant_price)


def merchant_item_xml(prod, *, item_id, title, price, sale_price, apparel=None):
    link = f"{SITE_URL}/products/{prod['handle']}.html"
    image = prod.get("image") or ""
    img_link = image if image.startswith("http") else f"{SITE_URL}/{image.lstrip('/')}"
    g_cat = merchant_category_for(prod)
    availability = "in_stock" if (apparel or {}).get("in_stock", True) else "out_of_stock"
    lines = [
        "    <item>",
        f"      <g:id>{html.escape(item_id)}</g:id>",
        f"      <g:title>{html.escape(title)}</g:title>",
        f"      <g:description>{html.escape(prod['short_desc'])}</g:description>",
        f"      <g:link>{html.escape(link)}</g:link>",
        f"      <g:image_link>{html.escape(img_link)}</g:image_link>",
        "      <g:condition>new</g:condition>",
        f"      <g:availability>{availability}</g:availability>",
        f"      <g:price>{price}</g:price>",
        "      <g:brand>Apex Hybrid Co</g:brand>",
        f"      <g:mpn>{html.escape(prod['id'])}</g:mpn>",
        "      <g:identifier_exists>no</g:identifier_exists>",
    ]
    if apparel:
        lines.append(f"      <g:item_group_id>{html.escape(prod['id'])}</g:item_group_id>")
        lines.append("      <g:age_group>adult</g:age_group>")
        lines.append("      <g:gender>unisex</g:gender>")
        if apparel.get("color"):
            lines.append(f"      <g:color>{html.escape(apparel['color'])}</g:color>")
        if apparel.get("size"):
            lines.append(f"      <g:size>{html.escape(apparel['size'])}</g:size>")
    lines.extend([
        f"      <g:google_product_category>{html.escape(g_cat)}</g:google_product_category>",
        f"      <g:product_type>{html.escape(prod['dept'])} &gt; {html.escape(prod['category'])}</g:product_type>",
        "      <g:shipping>",
        "        <g:country>US</g:country>",
        "        <g:service>Standard Ground</g:service>",
        "        <g:price>0.00 USD</g:price>",
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
                    apparel={**offer, "color": FEED_COLOR},
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
        color = sold_color(prod)
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
    <title>Apex Hybrid Co., operated by NolCorp LLC  -  HYROX Shirts, Breathable Race Apparel &amp; Recovery Feed</title>
    <link>{SITE_URL}</link>
    <description>Official Google Merchant Center product feed for Apex Hybrid Co., operated by NolCorp LLC (www.apexhybridco.com)  -  HYROX shirts, breathable tech tees, 2026/2027 race-city shirts, and recovery hardware.</description>
{chr(10).join(items_xml)}
  </channel>
</rss>
"""
    for filename in ("google_shopping_feed.xml", "google_merchant_feed.xml"):
        with open(os.path.join(BASE_DIR, filename), "w", encoding="utf-8") as f:
            f.write(rss_xml)
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
        for art in guides:
            art_url = f"{SITE_URL}/articles/{art['slug']}.html"
            items_xml.append(
                f"""    <item>
      <title>{html.escape(art['title'])}</title>
      <link>{art_url}</link>
      <guid isPermaLink="true">{art_url}</guid>
      <pubDate>{pub_rfc822}</pubDate>
      <category>{html.escape(art.get('category', 'HYROX & Hybrid Racing Guide'))}</category>
      <description>{html.escape(art.get('summary', ''))}</description>
    </item>"""
            )
        for prod in products:
            prod_url = f"{SITE_URL}/products/{prod['handle']}.html"
            fw_url = prod.get("fourthwall_product_url") or prod.get("checkout_url") or f"{SITE_URL}/?buy={prod['id']}"
            desc = f"{prod['short_desc']}  -  Price: ${prod['retail_price']:.2f} USD ({prod['ship_time']}). Direct Checkout: {fw_url}"
            items_xml.append(
                f"""    <item>
      <title>{html.escape(prod.get('seo_title', prod['title']))} (${prod['retail_price']:.2f})</title>
      <link>{prod_url}</link>
      <guid isPermaLink="true">{prod_url}</guid>
      <pubDate>{pub_rfc822}</pubDate>
      <category>{html.escape(prod.get('dept', 'Hybrid Race Gear'))}</category>
      <description>{html.escape(desc)}</description>
    </item>"""
            )

        feed_doc = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>Apex Hybrid Co.  -  HYROX Race Streetwear, Breathable Tech Shirts, Buyer Guides &amp; Recovery Hardware</title>
    <link>{SITE_URL}/</link>
    <description>Official RSS 2.0 &amp; WebSub feed for Apex Hybrid Co. ({SITE_URL})  -  {len(guides)} data-backed HYROX &amp; hybrid racing buyer guides, 2026/2027 race-city apparel (Chicago, Dallas, Anaheim, Las Vegas, Miami, NYC), and 45 performance apparel &amp; race-gear products.</description>
    <language>en-us</language>
    <lastBuildDate>{pub_rfc822}</lastBuildDate>
    <managingEditor>apexhybridco@gmail.com (Apex Hybrid Co.)</managingEditor>
    <webMaster>apexhybridco@gmail.com (Apex Hybrid Co.)</webMaster>
    <atom:link href="{self_url}" rel="self" type="application/rss+xml" />
    <atom:link href="https://pubsubhubbub.appspot.com/" rel="hub" />
    <atom:link href="https://pubsubhubbub.superfeedr.com/" rel="hub" />
{chr(10).join(items_xml)}
  </channel>
</rss>
"""
        with open(os.path.join(BASE_DIR, filename), "w", encoding="utf-8") as f:
            f.write(feed_doc)


def generate_pinterest_csv_feed():
    csv_path = os.path.join(BASE_DIR, "pinterest_catalog_feed.csv")
    fieldnames = [
        "id",
        "title",
        "description",
        "link",
        "image_link",
        "price",
        "sale_price",
        "availability",
        "condition",
        "google_product_category",
        "product_type",
        "brand",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for prod in products:
            writer.writerow(
                {
                    "id": prod["id"],
                    "title": prod.get("seo_title", prod["title"]),
                    "description": prod["short_desc"],
                    "link": f"{SITE_URL}/products/{prod['handle']}.html",
                    "image_link": f"{SITE_URL}/{prod['image']}",
                    "price": f"{prod['retail_price']:.2f} USD",
                    "sale_price": "",
                    "availability": "in stock",
                    "condition": "new",
                    "google_product_category": google_category_for(prod),
                    "product_type": f"{prod['dept']} > {prod['category']}",
                    "brand": "Apex Hybrid Co., operated by NolCorp LLC",
                }
            )



def generate_returns_page():
    """Return & exchange policy page for Google Merchant Center (matches Offer JSON-LD)."""
    page = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
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
    <loc>{u}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>
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

    for k_str in (INDEXNOW_KEY, "a8f9d2e4c7b14f6093e5d8c2a1b4e7f0", "a4b8c9d0e1f234567890abcdef123456", "a8f4c2e9d1b740639c5e2a1f8b3d7e90"):
        with open(os.path.join(BASE_DIR, f"{k_str}.txt"), "w", encoding="utf-8") as f:
            f.write(k_str)

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
        f"- [HYROX Doubles 2-Packs, Boutique Gym Bulk Kits & Coach Partner Portal]({SITE_URL}/team_orders.html): Mix-and-match Doubles 2-Packs (2x AeroMesh Breathable Tech Tees $62, 2x Race City Tees $58, 2x AeroShell Warmup Jackets $108, 2x Heavyweight Fleece Hoodies $96, Full Doubles Race-Day Kit $178), 5-Pack Relay Kits ($145), 10-Pack Boutique Gym Drops ($268), plus our $0-upfront Boutique HYROX Gym & Independent Coach Partner Program (complimentary coach sample piece + custom 10%-off athlete code + $25 bonus per 5 shirts sold). Contact: apexhybridco@gmail.com.",
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
                f"- [{p['title']}]({SITE_URL}/products/{p['handle']}.html)  -  **${float(p['retail_price']):.2f} USD** (SKU: `{p['id']}`, Category: {p['category']}, Rating: {p['rating']}★ from {p['reviews']} reviews, {p['ship_time']}). {p['short_desc']}"
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
        badge_class = "top-rated" if p["badge"] == "Top Rated" else ("new-release" if p["badge"] == "New Release" else "")
        badge_html = f'<span class="ProductCard__Badge {badge_class}">{html.escape(p["badge"])}</span>' if p["badge"] else ""
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
                <div class="ProductCard__RatingRow">
                  <span class="Stars">★★★★★</span>
                  <span class="ProductCard__RatingNum">{p['rating'].__format__('.1f')}</span>
                  <span class="ProductCard__ReviewCount">({p['reviews']})</span>
                </div>
                <div class="ProductCard__PriceRow">
                  <span class="PriceWhole"><sup>$</sup>{whole}<sup>{cents}</sup></span>
                  <span class="PriceList">List: ${(p.get('list_price') or p['retail_price']):.2f}</span>
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
                "description": "Breathable HYROX race shirts, laser-vented AeroMesh tech tees, 2026/2027 race-city shirts (Chicago, Dallas, Anaheim, Miami, Vegas, NYC), sleeveless muscle tanks, and clinical recovery hardware.",
                "telephone": "+1-949-805-4935",
                "email": "apexhybridco@gmail.com",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "",
                    "addressLocality": "Irvine",
                    "addressRegion": "CA",
                    "postalCode": "92618",
                    "addressCountry": "US",
                },
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
                            "text": "Our 4.0 oz AeroMesh Laser-Vented Tech Shirt (APC-C36), Dry-Pace Threshold Tech Tee (APC-C37), and Sleeveless Winged Crest Muscle Tanks (APC-C28) are engineered specifically for 8-station hybrid racing with laser-perforated shoulder ventilation and flatlock anti-chafe seams."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": "Do you carry 2026/2027 HYROX race-city shirts for Chicago, Dallas, Anaheim, Miami, Las Vegas, and New York?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Yes. Our Race City Editions collection includes Winged Apex Crest tees for Chicago Navy Pier (APC-C16), Dallas Lone Star Division (APC-C17), Anaheim SoCal (APC-C18), Miami Beach (APC-C19), Las Vegas (APC-C20), and New York Hudson Pier (APC-C21) with free 2–4 day US shipping."
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

if __name__ == "__main__":
    generate_product_pages()
    generate_article_pages()
    generate_google_shopping_feed()
    generate_editorial_rss_feeds()
    generate_pinterest_csv_feed()
    generate_returns_page()
    generate_sitemap_and_robots()
    enforce_delisted_noindex()
    # inject_static_seo_into_index() disabled to preserve clean index.html
    print(f"Successfully generated {len(products)} product pages, {len(guides)} SEO articles, Shopping XML/CSV feeds, and sitemap.xml")
