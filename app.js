const BEACON_NS = "https://abacus.jasoncameron.dev/hit/apexhybridco.com";
function trackHit(key) {
  try {
    if (!key) return;
    if (/bot|crawl|spider|slurp|headless|lighthouse/i.test(navigator.userAgent || "")) return;
    const clean = String(key).replace(/[^a-zA-Z0-9_-]/g, "_").slice(0, 62);
    // keepalive GET survives the move to Fourthwall. Abacus ignores POST (308).
    fetch(`${BEACON_NS}/${clean}`, { method: "GET", mode: "cors", keepalive: true, cache: "no-store" }).catch(() => {});
    if (window.goatcounter && typeof window.goatcounter.count === "function") {
      window.goatcounter.count({ path: clean, title: clean, event: true });
    }
  } catch (_) {}
}
window.apexTrackHit = trackHit;

const APPAREL = new Set([
  "Breathable Tech Shirts",
  "Race City Editions",
  "Muscle Tanks",
  "Women's",
  "Tees & Pump Covers",
  "Hoodies",
  "Windbreakers",
  "Training Gear",
]);

const PILLS = [
  ["apparel", "All apparel"],
  ["New", "New"],
  ["Breathable Tech Shirts", "Breathable Tech Shirts"],
  ["Race City Editions", "Race City Editions"],
  ["Muscle Tanks", "Muscle Tanks"],
  ["Women's", "Women's"],
  ["Tees & Pump Covers", "Race Tees & Pump Covers"],
  ["Hoodies", "Warmup Hoodies"],
  ["Windbreakers", "Windbreakers"],
  ["Training Gear", "Training Gear"],
];

const CITIES = [
  { sku: "APC-C16", code: "CHI", name: "Chicago", venue: "Navy Pier", when: "Feb 11–15, 2027", note: "Fast three-lap hall. Protect run one, then stay tall on the sled carpet.", run: 0.98, sled: 1.02 },
  { sku: "APC-C17", code: "DAL", name: "Dallas", venue: "Kay Bailey Hutchison", when: "November 2026", note: "High-grip sled carpet. Budget extra seconds on the push and the pull.", run: 0.99, sled: 1.1 },
  { sku: "APC-C18", code: "SOC", name: "Anaheim", venue: "SoCal Open", when: "December 2026", note: "Dry indoor air. This is the PR window if the first run stays honest.", run: 0.97, sled: 1 },
  { sku: "APC-C20", code: "LAS", name: "Las Vegas", venue: "Las Vegas Convention Center", when: "Mar 12–14, 2027", note: "Qualifier weekend. Even effort beats a hot first station.", run: 1, sled: 1.03 },
  { sku: "APC-C19", code: "MIA", name: "Miami", venue: "Beach convention hall", when: "March 2027", note: "Humidity shows up before station four. Open the run and wear the mesh.", run: 1.05, sled: 1.02 },
  { sku: "APC-C21", code: "NYC", name: "New York", venue: "Hudson Pier", when: "May 2027", note: "Metro lap, tight transitions. The Roxzone is where the clock leaks.", run: 0.99, sled: 1.01 },
];

const STATIONS = [
  ["01", "SkiErg", "skierg", 0.15, false],
  ["02", "Sled Push", "sledPush", 0.12, true],
  ["03", "Sled Pull", "sledPull", 0.12, true],
  ["04", "Burpee Broad Jump", "burpee", 0.13, false],
  ["05", "Row", "row", 0.14, false],
  ["06", "Farmer Carry", "farmer", 0.11, false],
  ["07", "Sandbag Lunges", "lunges", 0.12, false],
  ["08", "Wall Balls", "wall", 0.11, false],
];


const PROMO_CODES = {
  DALLAS10: { pct: 10, label: "10% off" },
}


const FW_VARIANTS = {"APC-C01": {"slug": "apex-heavyweight-hybrid-tee-run-station-repeat", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-heavyweight-hybrid-tee-run-station-repeat", "price": 44.0, "variants": {"S": {"id": "c7204aca-5bc1-4903-921c-4103e7b7bcd0", "price": 38.0}, "M": {"id": "c68ce394-fabe-4b4b-a61a-1e62e02ee237", "price": 38.0}, "L": {"id": "c72c77ef-f0ad-4d13-b3fd-0df02dfe5a63", "price": 38.0}, "XL": {"id": "83622d4b-c74d-4062-bb05-6a828368330b", "price": 38.0}, "2XL": {"id": "b14e7097-2d16-4828-a929-5d112665caf7", "price": 40.0}, "3XL": {"id": "4e5706e1-a2b6-4211-a8de-274857fb3a56", "price": 42.0}, "4XL": {"id": "f711f9fc-e68d-476c-b656-4a815af373b5", "price": 44.0}}}, "APC-C02": {"slug": "apex-heavyweight-hybrid-tee-wall-balls-bad-decisions", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-heavyweight-hybrid-tee-wall-balls-bad-decisions", "price": 44.0, "variants": {"S": {"id": "c5c3892a-360f-47e8-8983-65326e233e93", "price": 38.0}, "M": {"id": "ae373f8e-e8e2-4460-9ff1-6d9f3eaddd05", "price": 38.0}, "L": {"id": "8ef10583-5990-4906-a210-71e5c2907158", "price": 38.0}, "XL": {"id": "3471d1e9-2d95-4fbe-a82b-02cc4ff0680e", "price": 38.0}, "2XL": {"id": "0a4ee0a0-dd49-4fcc-891f-57d1ab8af263", "price": 40.0}, "3XL": {"id": "e19cbab1-5e95-4f2c-a98e-34da7fe9001d", "price": 42.0}, "4XL": {"id": "bcfd497a-2f33-46fb-81df-1e900ea95250", "price": 44.0}}}, "APC-C03": {"slug": "apex-heavyweight-hybrid-tee-sled-push-enthusiast", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-heavyweight-hybrid-tee-sled-push-enthusiast", "price": 44.0, "variants": {"S": {"id": "7face9ce-5c7b-4629-9a16-c7793eaf4d44", "price": 38.0}, "M": {"id": "3e967b7d-6ad8-4eb0-b56d-d23daa10872d", "price": 38.0}, "L": {"id": "2eb357f2-3d6d-4494-86b6-154e37b4f718", "price": 38.0}, "XL": {"id": "5667ffbd-8464-4382-b64b-f15928758377", "price": 38.0}, "2XL": {"id": "9e27edf7-51bf-407c-a457-3eb55b0ed5b1", "price": 40.0}, "3XL": {"id": "e94dae93-849d-4494-b186-c4f65d377dea", "price": 42.0}, "4XL": {"id": "661f6129-62ca-4308-bb44-a16e322906bc", "price": 44.0}}}, "APC-C05": {"slug": "apex-heavyweight-hybrid-tee-burpee-broad-jumps", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-heavyweight-hybrid-tee-burpee-broad-jumps", "price": 44.0, "variants": {"S": {"id": "6edd799d-2122-465e-8fea-6e0498803987", "price": 38.0}, "M": {"id": "14375fcf-1cac-438f-990f-805f2a1b75fb", "price": 38.0}, "L": {"id": "90c529f7-eb33-4220-b462-957d5e6abedd", "price": 38.0}, "XL": {"id": "20dd1fc9-0ec0-4dc7-a31c-3132a282a88e", "price": 38.0}, "2XL": {"id": "6c886af4-09f2-413b-9a2f-72e0ad01e04e", "price": 40.0}, "3XL": {"id": "2e19d790-d2f8-402e-afbb-4718dbdc9981", "price": 42.0}, "4XL": {"id": "243f1f60-a43d-4acf-acdc-cdef5a83fe12", "price": 44.0}}}, "APC-C06": {"slug": "apex-heavyweight-hybrid-tee-the-erg-doesnt-care-how-you-feel", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-heavyweight-hybrid-tee-the-erg-doesnt-care-how-you-feel", "price": 44.0, "variants": {"S": {"id": "68df6817-246b-4007-ac95-bb9bfbbb8cae", "price": 38.0}, "M": {"id": "43dcbb25-5c49-4135-afc1-bff30abf0580", "price": 38.0}, "L": {"id": "52e493a7-23ca-4525-ba8c-232e984a1cf9", "price": 38.0}, "XL": {"id": "a488c09e-550f-4c49-820c-138ea5ab0994", "price": 38.0}, "2XL": {"id": "5943682b-132f-4ee2-b305-9f41dfa56ab0", "price": 40.0}, "3XL": {"id": "675a00fc-4bac-4aba-9f33-905064045487", "price": 42.0}, "4XL": {"id": "ae16ee4d-62df-4650-9cb8-53c1a8aead52", "price": 44.0}}}, "APC-C07": {"slug": "apex-heavyweight-hybrid-tee-porta-potty-line-pr", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-heavyweight-hybrid-tee-porta-potty-line-pr", "price": 44.0, "variants": {"S": {"id": "7c92c0e4-d216-4164-8ab8-92d2fb3b3300", "price": 38.0}, "M": {"id": "70ec0502-727e-4e16-bd22-103ea7b95d79", "price": 38.0}, "L": {"id": "bdffa63c-fa65-442d-a2e9-b58a3e0fba30", "price": 38.0}, "XL": {"id": "4cc2c891-e2d8-4927-86d7-f548ade47457", "price": 38.0}, "2XL": {"id": "5d3c008f-8d94-4d20-864c-d68ba7b69840", "price": 40.0}, "3XL": {"id": "cdf279c3-3d72-47fc-ba30-8e212e51c922", "price": 42.0}, "4XL": {"id": "cf96ba81-d8bf-4a3d-bd36-46e35f5601ef", "price": 44.0}}}, "APC-C08": {"slug": "apex-heavyweight-hybrid-tee-i-dont-need-to-defend-my-sled-push", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-heavyweight-hybrid-tee-i-dont-need-to-defend-my-sled-push", "price": 44.0, "variants": {"S": {"id": "312b10cb-f4d0-4e18-9d72-368d38c2c150", "price": 38.0}, "M": {"id": "fc74fbe2-0473-4436-a214-c66327fa123d", "price": 38.0}, "L": {"id": "b488851a-657d-4348-b7e7-3652ea44d216", "price": 38.0}, "XL": {"id": "b5a5cb27-ae1b-4ac5-965b-af5ebe7dcc96", "price": 38.0}, "2XL": {"id": "04c4c580-4d6d-4511-b742-90575a2f811b", "price": 40.0}, "3XL": {"id": "0a0b3b8b-8aab-4096-b24c-84d5efa2cd7d", "price": 42.0}, "4XL": {"id": "ae3fc74e-39ad-4dda-9a3e-5622ab5e7100", "price": 44.0}}}, "APC-C09": {"slug": "run-station-repeat-heavyweight-fleece-warmup-hoodie", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/run-station-repeat-heavyweight-fleece-warmup-hoodie", "price": 63.00, "variants": {"XS": {"id": "7d1b0e76-e17e-493c-8a79-23d4a9129316", "price": 58.0}, "S": {"id": "8dae9001-7052-4aba-ad20-57680b7e7508", "price": 58.0}, "M": {"id": "6caec690-8afd-44bb-8566-e232270d856b", "price": 58.0}, "L": {"id": "5e0986ef-ebc2-48d2-801b-1727d6e5e66b", "price": 58.0}, "XL": {"id": "176d4371-37a1-4eb4-bab0-c971b0ecdb51", "price": 58.0}, "2XL": {"id": "6254dadd-73ae-4777-9da1-29b60660b3ef", "price": 63.00}, "3XL": {"id": "29defe28-d413-4fdd-9e2f-84ee97266dfd", "price": 63.00}}}, "APC-C10": {"slug": "wall-balls-bad-decisions-brushed-fleece-pullover-hoodie", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/wall-balls-bad-decisions-brushed-fleece-pullover-hoodie", "price": 63.00, "variants": {"XS": {"id": "9dcb8fc2-40f2-44e8-a248-6e966b632807", "price": 58.0}, "S": {"id": "7545a9f0-3169-4918-8107-c6caa0aa559b", "price": 58.0}, "M": {"id": "4b60582b-d219-4491-a543-b42fb2b7e40d", "price": 58.0}, "L": {"id": "06660872-edb1-47b0-9ade-6b3d31fa98f8", "price": 58.0}, "XL": {"id": "12e17539-d1e3-48d9-80a9-41c16a6a7c60", "price": 58.0}, "2XL": {"id": "7b8e7c6a-d1f8-4d21-af73-8d7e193330de", "price": 63.00}, "3XL": {"id": "87f73a63-de61-4270-b9ac-c1af04661b8c", "price": 63.00}}}, "APC-C11": {"slug": "compromised-running-club-heavy-warmup-hoodie", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/compromised-running-club-heavy-warmup-hoodie", "price": 63.00, "variants": {"XS": {"id": "09ebf420-ca29-435e-8884-c4ed99a23200", "price": 58.0}, "S": {"id": "f5a4f975-06b7-4e38-9002-a8908588995a", "price": 58.0}, "M": {"id": "e686cf02-2840-4545-afa0-0a5c13741a31", "price": 58.0}, "L": {"id": "e7bc46ab-f42f-45c6-aebb-ed1bad633116", "price": 58.0}, "XL": {"id": "f4da2641-2534-4816-89f8-29bea7337b66", "price": 58.0}, "2XL": {"id": "2b1d8377-4021-418a-84f0-cc84b5cba47b", "price": 63.00}, "3XL": {"id": "21f9f457-4512-4f1a-89b5-fcd74e21d98a", "price": 63.00}}}, "APC-C12": {"slug": "sled-push-dept-the-footage-speaks-pullover-hoodie", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/sled-push-dept-the-footage-speaks-pullover-hoodie", "price": 63.00, "variants": {"XS": {"id": "c2c4b556-38b3-45fe-8671-f7c3098d9877", "price": 58.0}, "S": {"id": "b368c389-dad2-4166-8bdf-ec6c646b0e16", "price": 58.0}, "M": {"id": "7c04c499-643c-4f2c-8b59-995d4b9060e9", "price": 58.0}, "L": {"id": "b46ab63e-edcf-4be1-9821-a6b73dcc8a8c", "price": 58.0}, "XL": {"id": "6e3a13c8-8982-4062-ada8-8589c122ae7e", "price": 58.0}, "2XL": {"id": "efaff547-a0ba-4879-bfb5-c956e32895e4", "price": 63.00}, "3XL": {"id": "7cc96662-1bc1-4a72-ada2-8e6a350b1425", "price": 63.00}}}, "APC-C13": {"slug": "zone-2-engine-lab-low-profile-cotton-twill-cap", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/zone-2-engine-lab-low-profile-cotton-twill-cap", "price": 34.0, "variants": {"One size": {"id": "9b519b62-0e55-4531-8069-143fd4d145bb", "price": 34.0}}}, "APC-C14": {"slug": "8-station-race-day-50l-all-weather-gym-shoe-bag", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/8-station-race-day-50l-all-weather-gym-shoe-bag", "price": 74.0, "variants": {"One size": {"id": "a1c2426f-97bb-4493-b715-852ee8e840a5", "price": 74.0}}}, "APC-C16": {"slug": "apex-race-city-heavyweight-tee-chicago-championship-division", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-race-city-heavyweight-tee-chicago-championship-division", "price": 44.0, "variants": {"S": {"id": "c16f2888-d87c-4c3f-87d9-e2bd83dc0100", "price": 38.0}, "M": {"id": "08e0595f-274a-40ec-8785-c9ea0f5de0cd", "price": 38.0}, "L": {"id": "fcb679ba-d57a-43d9-a0be-2b2cbcdc383c", "price": 38.0}, "XL": {"id": "faa26a24-2e4b-4c5c-b74e-6467f3e121ab", "price": 38.0}, "2XL": {"id": "ee60d9cb-bc4f-4d18-b48f-02a28c447acc", "price": 40.0}, "3XL": {"id": "1bfd9e68-dfcd-4711-9e20-85d32e25b5b1", "price": 42.0}, "4XL": {"id": "84a3ff32-39eb-4fe1-8671-31b1944c796c", "price": 44.0}}}, "APC-C17": {"slug": "apex-race-city-heavyweight-tee-dallas-turf-threshold", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-race-city-heavyweight-tee-dallas-turf-threshold", "price": 44.0, "variants": {"S": {"id": "29d09b15-c469-4480-93ef-46fc56630660", "price": 38.0}, "M": {"id": "f904e25f-d52b-46d7-985e-bad081971aaa", "price": 38.0}, "L": {"id": "168c443a-0b9c-42d1-9d45-0b7895383e8b", "price": 38.0}, "XL": {"id": "204b8d9c-a8de-4233-8ae5-f72050073c66", "price": 38.0}, "2XL": {"id": "b27dba7d-d08d-4112-bec6-8e77e12cbff3", "price": 40.0}, "3XL": {"id": "0ef6640a-89cc-4582-8908-39af2ff1725b", "price": 42.0}, "4XL": {"id": "4901ae29-4874-41c5-a0aa-4c3b4fdcfa57", "price": 44.0}}}, "APC-C18": {"slug": "apex-race-city-heavyweight-tee-anaheim-socal-open-division", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-race-city-heavyweight-tee-anaheim-socal-open-division", "price": 44.0, "variants": {"S": {"id": "5b4995a6-f354-4919-874f-bc293c0015cd", "price": 38.0}, "M": {"id": "12168372-2f3b-4ce2-88df-258fd652cb78", "price": 38.0}, "L": {"id": "a2cf7e4e-5cdf-40fe-a1b7-141fdc023187", "price": 38.0}, "XL": {"id": "c62d440a-181a-4c58-b5e0-c8d605957801", "price": 38.0}, "2XL": {"id": "773832b9-b959-4606-a608-1a093ff09318", "price": 40.0}, "3XL": {"id": "4795338c-29bd-4c89-a3ca-b341b1fd77a5", "price": 42.0}, "4XL": {"id": "7ebaf79b-e154-4880-8895-64f872e0b30c", "price": 44.0}}}, "APC-C19": {"slug": "apex-race-city-heavyweight-tee-miami-beach-endurance-club", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-race-city-heavyweight-tee-miami-beach-endurance-club", "price": 44.0, "variants": {"S": {"id": "e13d66d2-84ab-42bd-a811-62287e0e96ca", "price": 38.0}, "M": {"id": "69e54c97-73d3-42f5-b618-64566649d017", "price": 38.0}, "L": {"id": "189a0ffd-7329-47d5-87a5-fb52cce4b135", "price": 38.0}, "XL": {"id": "a47a8156-007c-4ec9-a90e-7939f4510227", "price": 38.0}, "2XL": {"id": "3027f3ce-41b5-4bc6-a4a2-989396817490", "price": 40.0}, "3XL": {"id": "463543de-4d7f-4bd6-ab30-a271d2e1bdc4", "price": 42.0}, "4XL": {"id": "cba57d43-625d-48ad-a62f-9ae321f2d5a6", "price": 44.0}}}, "APC-C20": {"slug": "apex-race-city-heavyweight-tee-las-vegas-championship-qualifier", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-race-city-heavyweight-tee-las-vegas-championship-qualifier", "price": 44.0, "variants": {"S": {"id": "e95737cc-3b02-4b71-865c-cda9659fac93", "price": 38.0}, "M": {"id": "990391a8-3d50-4411-9b7c-2e1d7065a4e7", "price": 38.0}, "L": {"id": "a92d8fe2-33a0-4cf5-8fb9-00e0b6edbf08", "price": 38.0}, "XL": {"id": "54d568ee-0b1f-4a77-9211-2b8b9409a4d8", "price": 38.0}, "2XL": {"id": "4fc194b5-a765-4f71-b8ec-6c87a248bf9c", "price": 40.0}, "3XL": {"id": "75a34551-e6c6-49b9-968d-ff5579272d03", "price": 42.0}, "4XL": {"id": "c4e65319-d65c-44ea-b346-1d1895d0247d", "price": 44.0}}}, "APC-C21": {"slug": "apex-race-city-heavyweight-tee-new-york-hudson-pier-division", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-race-city-heavyweight-tee-new-york-hudson-pier-division", "price": 44.0, "variants": {"S": {"id": "6603a7ea-bddd-4224-9c82-f5a2b4f40a16", "price": 38.0}, "M": {"id": "2bb9a1de-99ae-48c3-838a-88310372249e", "price": 38.0}, "L": {"id": "a825800a-126f-462a-9e3a-36be4e31ca49", "price": 38.0}, "XL": {"id": "8548abd2-f4e2-40f8-9923-26ad15121428", "price": 38.0}, "2XL": {"id": "6be04a0b-846e-4e0b-8657-ecdd20341fc0", "price": 40.0}, "3XL": {"id": "a40b3f16-3d26-49a1-9980-fe9727f63769", "price": 42.0}, "4XL": {"id": "8e7a9ea4-b1c0-4d8c-8652-a218ed3c1637", "price": 44.0}}}, "APC-C22": {"slug": "apex-heavyweight-hybrid-tee-8-runs-8-stations-zero-excuses", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-heavyweight-hybrid-tee-8-runs-8-stations-zero-excuses", "price": 44.0, "variants": {"S": {"id": "4de0836a-116b-441f-a440-c8a408de6d56", "price": 38.0}, "M": {"id": "07d55661-2904-4347-ad01-b1b72abe6c7b", "price": 38.0}, "L": {"id": "55158248-39c7-409a-afff-216a2ee73cdd", "price": 38.0}, "XL": {"id": "d61e5407-2ee3-4f5f-a09b-d0dd892a7773", "price": 38.0}, "2XL": {"id": "e08f0fa7-47d3-40c1-b889-69ace767a27c", "price": 40.0}, "3XL": {"id": "a5edfbca-e9b3-4e3c-ad33-47f5d8b76a1a", "price": 42.0}, "4XL": {"id": "33d7cd8e-7e13-42ed-94f1-5bb6c18e8994", "price": 44.0}}}, "APC-C23": {"slug": "roxzone-penalties-ruined-my-pr-stopwatch-crest-athletic-race-tee", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/roxzone-penalties-ruined-my-pr-stopwatch-crest-athletic-race-tee", "price": 44.0, "variants": {"S": {"id": "8c697c2c-a31c-4960-b3aa-adcd5611045b", "price": 38.0}, "M": {"id": "0b1c3e9f-1d91-4a38-8661-b33493b49a99", "price": 38.0}, "L": {"id": "4ff60af6-a733-41c8-9960-aa99c086e533", "price": 38.0}, "XL": {"id": "8c103b35-a87b-4be1-8515-bd33bfd43b86", "price": 38.0}, "2XL": {"id": "8ee2abac-27f5-4ecb-ba1b-e308caa180b5", "price": 40.0}, "3XL": {"id": "8a00447d-76e2-4678-bc14-3e738a856073", "price": 42.0}, "4XL": {"id": "f5bc854f-41a0-40e8-b907-913c0819daaa", "price": 44.0}}}, "APC-C24": {"slug": "200m-farmer-carry-survivors-club-barbell-insignia-race-tee", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/200m-farmer-carry-survivors-club-barbell-insignia-race-tee", "price": 44.0, "variants": {"S": {"id": "5e454b8c-b481-4821-9f22-88e70ee0e37f", "price": 38.0}, "M": {"id": "346d6534-51f6-43b0-9423-c9a0ceb91b3c", "price": 38.0}, "L": {"id": "8f93bfcd-cf45-4dad-a03d-fbd48a365c1b", "price": 38.0}, "XL": {"id": "b0757e15-591d-44ab-9a9d-684f5a010565", "price": 38.0}, "2XL": {"id": "5860c552-42fe-4a51-9a4b-27e4b52bfd98", "price": 40.0}, "3XL": {"id": "eda3446b-3318-420b-8da1-c562399abdb7", "price": 42.0}, "4XL": {"id": "bb038cea-8ef0-4088-99c9-d150f194673d", "price": 44.0}}}, "APC-C25": {"slug": "sandbag-lunges-are-a-personal-attack-station-07-crest-pump-cover", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/sandbag-lunges-are-a-personal-attack-station-07-crest-pump-cover", "price": 44.0, "variants": {"S": {"id": "7eae10b8-0f3f-40a7-b3da-e342cd1937ca", "price": 38.0}, "M": {"id": "facf1e6b-1d8a-48b3-9593-1d236ab723df", "price": 38.0}, "L": {"id": "7d58e13b-ce6f-4cb0-8b9c-5e2480b03daf", "price": 38.0}, "XL": {"id": "6f5d8760-e6f2-495c-86c0-62f140531581", "price": 38.0}, "2XL": {"id": "5c444c93-ebf5-4934-9db2-1cd0c8d6ab12", "price": 40.0}, "3XL": {"id": "f1954b8d-a4b5-4c89-8a5f-a18629db6416", "price": 42.0}, "4XL": {"id": "b6897f4b-7530-4e1d-bc2d-6ab4a55ae546", "price": 44.0}}}, "APC-C26": {"slug": "zone-2-all-week-redline-weekend-185-bpm-tachometer-race-tee", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/zone-2-all-week-redline-weekend-185-bpm-tachometer-race-tee", "price": 44.0, "variants": {"S": {"id": "781a4baf-ad06-401a-8fea-aa497d25feca", "price": 38.0}, "M": {"id": "7702e84f-51af-42fa-ae93-d3aafa4a19db", "price": 38.0}, "L": {"id": "fcdd1763-5033-46d8-88df-e622d4052b8c", "price": 38.0}, "XL": {"id": "da08747c-0607-41c2-8eac-806bd9b72301", "price": 38.0}, "2XL": {"id": "e3c6baef-ecf3-42ea-bd69-c994ad4e9ef5", "price": 40.0}, "3XL": {"id": "dc0ab909-65e9-4631-8049-6e07a3d0866d", "price": 42.0}, "4XL": {"id": "1b1e3fc8-0e1f-42e4-a1d7-5bf38dde465c", "price": 44.0}}}, "APC-C27": {"slug": "sub-65-club-pace-pull-push-winged-crest-elite-division-tee", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/sub-65-club-pace-pull-push-winged-crest-elite-division-tee", "price": 44.0, "variants": {"S": {"id": "9247cf41-03c0-4965-9840-c74f7e6f2477", "price": 38.0}, "M": {"id": "efe2144c-edf8-4552-8c44-13e4ecc70542", "price": 38.0}, "L": {"id": "f7a31684-947f-4f19-8141-0478221d8912", "price": 38.0}, "XL": {"id": "a329e609-ca20-42fa-adcb-7575cd392eb1", "price": 38.0}, "2XL": {"id": "d1ca19dc-485a-4b5f-bae2-8ada2404d0a6", "price": 40.0}, "3XL": {"id": "932cc039-5e0d-4525-9beb-34bedc704b60", "price": 42.0}, "4XL": {"id": "04e7c5ec-b9cb-448c-bd2f-346ffbdda5ae", "price": 44.0}}}, "APC-C28": {"slug": "run-station-repeat-winged-crest-sleeveless-race-day-muscle-tank", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/run-station-repeat-winged-crest-sleeveless-race-day-muscle-tank", "price": 34.0, "variants": {"S": {"id": "8d35fac0-ea9c-4f3e-853e-6cb60b543b65", "price": 32.0}, "M": {"id": "c72dfd45-144e-4306-a028-711c15a6d658", "price": 32.0}, "L": {"id": "08fe4705-4241-4508-9174-75b4dd6acc79", "price": 32.0}, "XL": {"id": "1328feb2-532a-4aa8-b755-bb1ff2adcc11", "price": 32.0}, "2XL": {"id": "0a21bff6-d727-4993-8de3-5d4f867f3e5b", "price": 34.0}}}, "APC-C29": {"slug": "sled-push-dept-barbell-crest-conditioning-muscle-tank", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/sled-push-dept-barbell-crest-conditioning-muscle-tank", "price": 34.0, "variants": {"S": {"id": "ee532b28-050d-492d-a447-a975262ddb30", "price": 32.0}, "M": {"id": "0bc45bdd-8132-47b6-9ffc-38abf9fcbe44", "price": 32.0}, "L": {"id": "b85f66f4-2430-4f02-999d-65ad2f518719", "price": 32.0}, "XL": {"id": "0d70fd17-0281-4ab6-b549-563ffce47384", "price": 32.0}, "2XL": {"id": "88cbcb33-18d2-4437-93c0-cff4dd7e61ba", "price": 34.0}}}, "APC-C30": {"slug": "compromised-running-club-1000m-stopwatch-breathable-race-tank", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/compromised-running-club-1000m-stopwatch-breathable-race-tank", "price": 34.0, "variants": {"S": {"id": "d17716f7-8c5d-459a-b9e2-7f329ad10947", "price": 32.0}, "M": {"id": "df92d051-96b0-43d1-886d-1505adfaf0c7", "price": 32.0}, "L": {"id": "8e4c7692-deba-4f50-9025-e9d1ca50009c", "price": 32.0}, "XL": {"id": "94c992b8-21ca-4868-8425-d88a9fa23a8b", "price": 32.0}, "2XL": {"id": "2dadc3d8-c268-4319-a7f7-5dbd997f5d80", "price": 34.0}}}, "APC-C31": {"slug": "100-wall-balls-unbroken-winged-crest-sleeveless-muscle-tank", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/100-wall-balls-unbroken-winged-crest-sleeveless-muscle-tank", "price": 34.0, "variants": {"S": {"id": "aac13db6-e423-4ac8-87ba-9eb29c3e176f", "price": 32.0}, "M": {"id": "5c87cfc4-8080-419a-a2a7-ccb082977f3b", "price": 32.0}, "L": {"id": "bfa0bf6e-e45a-49cf-a742-85b62074ec4a", "price": 32.0}, "XL": {"id": "889c5b4b-8425-4f0d-bf2e-50f4594ab213", "price": 32.0}, "2XL": {"id": "d652b52d-7f9a-4f15-9153-9061a611fc18", "price": 34.0}}}, "APC-C32": {"slug": "burpee-broad-jumps-build-character-8-0-oz-warmup-hoodie", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/burpee-broad-jumps-build-character-8-0-oz-warmup-hoodie", "price": 63.00, "variants": {"XS": {"id": "5add8ab6-c9a0-4c43-8bfe-1771842a5461", "price": 58.0}, "S": {"id": "6193f3d6-fccc-481d-b493-8c06b68d4d9d", "price": 58.0}, "M": {"id": "151176d5-13a0-4afb-81a4-3edf6f740222", "price": 58.0}, "L": {"id": "ed173816-a15c-43e1-b1fa-0630825c49bb", "price": 58.0}, "XL": {"id": "1df12133-b013-4342-a712-6cc249ba527b", "price": 58.0}, "2XL": {"id": "d55b3a2a-323c-4007-8cf3-e0463b9e34ee", "price": 63.00}, "3XL": {"id": "1c0ca70a-8ef9-4d9f-9d69-4ea136a3bb45", "price": 63.00}}}, "APC-C33": {"slug": "the-erg-doesnt-care-how-you-feel-heavyweight-fleece-hoodie", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/the-erg-doesnt-care-how-you-feel-heavyweight-fleece-hoodie", "price": 63.00, "variants": {"XS": {"id": "2313798a-5651-4821-91d0-81ed4775ed72", "price": 58.0}, "S": {"id": "10959ca1-dbff-4df4-8713-ffbbcd6df723", "price": 58.0}, "M": {"id": "ff7ea849-58da-42fb-b9b2-033bcfb6efdc", "price": 58.0}, "L": {"id": "78f1465a-6d25-45ed-b287-548e93135679", "price": 58.0}, "XL": {"id": "6230fc26-5a17-4be0-aae0-6722a5b29b72", "price": 58.0}, "2XL": {"id": "cd66966a-a461-48a6-96c1-33beb5bfa28a", "price": 63.00}, "3XL": {"id": "281e8326-b981-41e2-9869-642ce8f84a20", "price": 63.00}}}, "APC-C34": {"slug": "chicago-dallas-socal-2026-2027-world-series-prep-winged-hoodie", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/chicago-dallas-socal-2026-2027-world-series-prep-winged-hoodie", "price": 63.00, "variants": {"XS": {"id": "85bb4f83-bff1-4998-9f68-b8a23b08dfb0", "price": 58.0}, "S": {"id": "dc53f607-5617-474d-abff-3eac666aee20", "price": 58.0}, "M": {"id": "9a69d869-5c34-440a-b058-fe89ca39a209", "price": 58.0}, "L": {"id": "b7d4593e-9ba1-4f1d-8d17-b09f3a69f59b", "price": 58.0}, "XL": {"id": "4811b656-fb01-4fc0-89aa-4cc71c7dc1c9", "price": 58.0}, "2XL": {"id": "136ea0e4-c417-4e9f-9b52-00ca6ca399e6", "price": 63.00}, "3XL": {"id": "31b5b1e2-256e-48cb-b2d3-fb8eadbba363", "price": 63.00}}}, "APC-C36": {"slug": "compromised-running-tech-shirt", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/compromised-running-tech-shirt", "price": 44.0, "variants": {"S": {"id": "20a671fa-a629-4b1a-83d7-52f3b44b1c48", "price": 38.0}, "M": {"id": "db9752e0-3cb3-4a43-b134-955028adc222", "price": 38.0}, "L": {"id": "ea1df055-96ab-44b8-8ed6-25357a1a2323", "price": 38.0}, "XL": {"id": "663e3316-511a-4372-aa92-497018ec0045", "price": 38.0}, "2XL": {"id": "7c5b1f8f-4190-4378-912b-f73f07175d2c", "price": 40.0}, "3XL": {"id": "10d223af-9e57-4bb4-8be5-745a2d5ff422", "price": 42.0}, "4XL": {"id": "612196b3-a43d-4644-bd12-4b8fc5cde9fb", "price": 44.0}}}, "APC-C37": {"slug": "1km-split-station-repeat-tech-tee", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/1km-split-station-repeat-tech-tee", "price": 44.0, "variants": {"S": {"id": "583681fa-9dc6-4a20-8070-9621ce729ed2", "price": 38.0}, "M": {"id": "33b52cc0-84b1-47cf-93d9-b1e62f3af5f0", "price": 38.0}, "L": {"id": "0d6c5852-0b4e-4904-acef-9782ddec3eed", "price": 38.0}, "XL": {"id": "88c75bfc-e9a6-4740-8a92-b7b126d09a2d", "price": 38.0}, "2XL": {"id": "17e6911c-b121-4e28-8fcc-88e401162d02", "price": 40.0}, "3XL": {"id": "4a62b4e5-b94b-4176-b61d-b104f25325f3", "price": 42.0}, "4XL": {"id": "a6520576-18bf-4b1e-86ae-3c207f1047b9", "price": 44.0}}}, "APC-C38": {"slug": "zone-4-zone-5-engine-shirt", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/zone-4-zone-5-engine-shirt", "price": 44.0, "variants": {"S": {"id": "277fd44c-15db-49a9-92a5-bd88aa4d3fa2", "price": 38.0}, "M": {"id": "a0432be5-8f80-4db0-9b82-8664c48d7b23", "price": 38.0}, "L": {"id": "3b1a3d13-ac15-4188-9c51-85e084b72db0", "price": 38.0}, "XL": {"id": "3a58907b-1f88-4088-9c75-335044b0040e", "price": 38.0}, "2XL": {"id": "65e5d909-b61a-43ac-833f-a6b4204a0725", "price": 40.0}, "3XL": {"id": "ee21708f-d305-4ba3-94a2-61c85799ef98", "price": 42.0}, "4XL": {"id": "6dd520bf-8f9a-49fd-8422-7442c8932293", "price": 44.0}}}, "APC-C40": {"slug": "push-heavy-run-fast-tech-shirt", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/push-heavy-run-fast-tech-shirt", "price": 44.0, "variants": {"S": {"id": "7448050c-3c2d-4e56-bbf8-c52c338e61a1", "price": 38.0}, "M": {"id": "fce65b02-47b6-438b-9d20-103498d70f21", "price": 38.0}, "L": {"id": "57e27a95-8741-4b00-8fc7-670a7c91b6a0", "price": 38.0}, "XL": {"id": "d92261de-1f9d-421e-aaf6-ec27f4d7ce9f", "price": 38.0}, "2XL": {"id": "aa6d646a-5495-47ef-816b-834d5eb2ef5a", "price": 40.0}, "3XL": {"id": "b16d2ed1-b884-4cdb-a969-bccd1bbb850f", "price": 42.0}, "4XL": {"id": "54a99075-2070-42fe-92ad-3269aae5a44f", "price": 44.0}}}, "APC-C41": {"slug": "roxzone-speed-dept-tee", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/roxzone-speed-dept-tee", "price": 44.0, "variants": {"S": {"id": "94a27f9d-b273-4cce-bc32-0d04ed95ff8d", "price": 38.0}, "M": {"id": "cd4cb1fc-9eef-46cd-a60d-8853b35c8b8e", "price": 38.0}, "L": {"id": "643813da-c3c4-45b3-99e0-31cd4df4cd04", "price": 38.0}, "XL": {"id": "99bfce11-d0d2-44c5-8f72-5b69f20f0f40", "price": 38.0}, "2XL": {"id": "a04c4874-fff1-4699-88c3-69dd9350ba3a", "price": 40.0}, "3XL": {"id": "7e74959a-29bb-4220-83d8-0c2770f0e7f4", "price": 42.0}, "4XL": {"id": "791fed22-3303-4de9-8020-130c94f3c8a4", "price": 44.0}}}, "APC-C42": {"slug": "apex-lightweight-race-warmup-jacket-hybrid-division", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-lightweight-race-warmup-jacket-hybrid-division", "price": 70.0, "variants": {"S": {"id": "1d4a10ad-8725-4c1c-af43-7b4a2e71df95", "price": 68.0}, "M": {"id": "c48fde75-2fe3-4149-b445-d1be28665ad3", "price": 68.0}, "L": {"id": "05d3d05b-848a-4432-9c1e-0e7a9e1af7b5", "price": 68.0}, "XL": {"id": "ca8c2f5b-0134-4ac1-be71-0dcc205d3129", "price": 68.0}, "2XL": {"id": "6d02c957-c50c-4bf7-847e-5ebf4fb5adfb", "price": 70.0}}}, "APC-C46": {"slug": "apex-dallas-race-day", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-dallas-race-day", "price": 70.0, "variants": {"XS": {"id": "88638db0-ac4c-4f93-ad88-d5748192096a", "price": 68.0}, "S": {"id": "93db90a0-3e22-4c6f-b7e9-942d269785ef", "price": 68.0}, "M": {"id": "7033864b-0915-448c-9967-226148d4217a", "price": 68.0}, "L": {"id": "d73d3810-ec7d-4935-817e-7bbdbe97eb29", "price": 68.0}, "XL": {"id": "a791d8c6-0c37-4d68-9525-a4a49bbb4c19", "price": 68.0}, "2XL": {"id": "211ecd05-1958-4409-911d-27c11d2a2e1a", "price": 70.0}, "3XL": {"id": "9d423e89-e54f-4368-acb1-097407fe9390", "price": 72.0}}}, "APC-C43": {"slug": "hybrid-8-station-windbreaker-track-jacket-01-skierg-to-08-wall-balls", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hybrid-8-station-windbreaker-track-jacket-01-skierg-to-08-wall-balls", "price": 70.0, "variants": {"S": {"id": "b984aded-2e52-44f9-8090-a1ba479c1569", "price": 68.0}, "M": {"id": "7af66ca4-8176-4c5d-9925-ca7b0ee85d3f", "price": 68.0}, "L": {"id": "586a1a3e-cdc7-4b76-b2a9-61b2ef7b7519", "price": 68.0}, "XL": {"id": "7d00e825-5ce2-451d-8344-35674f532034", "price": 68.0}, "2XL": {"id": "0d56b749-acbb-4258-b3ad-ef382e503de8", "price": 70.0}}}, "APC-C44": {"slug": "pro-division-lightweight-quarter-zip-shell-sub-65-warmup-track-top", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/pro-division-lightweight-quarter-zip-shell-sub-65-warmup-track-top", "price": 70.0, "variants": {"S": {"id": "8c2368cd-b62d-4cd3-8a9a-e30ab0fe503b", "price": 68.0}, "M": {"id": "0f043a40-8885-434d-a9f0-a53012bdc10f", "price": 68.0}, "L": {"id": "14cb80b7-74b4-43c9-839d-37b663f9de74", "price": 68.0}, "XL": {"id": "3082fab9-42be-414f-a898-2c59c739fc38", "price": 68.0}, "2XL": {"id": "937d9dda-1dc2-4164-9bab-47644a7650d6", "price": 70.0}}}, "APC-C45": {"slug": "26-27-world-series-lightweight-warmup-jacket-chicago-dallas-socal-nyc", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/26-27-world-series-lightweight-warmup-jacket-chicago-dallas-socal-nyc", "price": 70.0, "variants": {"S": {"id": "989cee7a-0737-4bfc-a693-9696f1ead10d", "price": 68.0}, "M": {"id": "9d933c04-3aef-4602-a7c9-df0429339bce", "price": 68.0}, "L": {"id": "ec91cc61-cfae-4341-9766-97859144e369", "price": 68.0}, "XL": {"id": "b6d8f181-3098-4d49-b582-b0b83ff1c97a", "price": 68.0}, "2XL": {"id": "7704d039-9dc8-4215-814a-d036480726bd", "price": 70.0}}}, "APC-C47": {"slug": "apex-denver-race-day", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-denver-race-day", "price": 72.0, "variants": {"XS": {"id": "d18be3b5-e1c0-41db-9c6e-4af872a0656e", "price": 68.0}, "S": {"id": "b4bb75cd-7351-41d2-8c5b-edb645c79901", "price": 68.0}, "M": {"id": "49a70789-ff66-4530-8883-b775102487c9", "price": 68.0}, "L": {"id": "04d6fe08-b677-455d-8f0b-34da2541ffbc", "price": 68.0}, "XL": {"id": "284b13ab-b857-4849-bfe9-f8437e23e0eb", "price": 68.0}, "2XL": {"id": "609497f7-f428-4269-b954-ce8b2975082e", "price": 70.0}, "3XL": {"id": "784f7aee-911e-4cbf-8a50-fc3955d0c9ed", "price": 72.0}}}, "APC-C48": {"slug": "apex-anaheim-race-day", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-anaheim-race-day", "price": 72.0, "variants": {"XS": {"id": "09b2e4e6-3b63-418f-9669-085406f68b76", "price": 68.0}, "S": {"id": "9aaaa0cc-34b8-44fd-b190-2fbd05010cfd", "price": 68.0}, "M": {"id": "84739359-672a-4505-a6ea-c85c4a654a82", "price": 68.0}, "L": {"id": "dfb61407-e94f-42a3-9040-5baf77f33357", "price": 68.0}, "XL": {"id": "6f908b2e-83dc-4f09-9ca0-4035aabe3bb0", "price": 68.0}, "2XL": {"id": "636e0288-b874-4af0-9029-65faeef71345", "price": 70.0}, "3XL": {"id": "aaba7ca1-cc86-4de2-b164-30d1fa6e6b70", "price": 72.0}}}, "APC-C49": {"slug": "apex-nashville-race-day", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-nashville-race-day", "price": 72.0, "variants": {"XS": {"id": "3b359a10-5903-41aa-a561-6f25116ecc0b", "price": 68.0}, "S": {"id": "cc1685fc-4451-4048-a24c-ec36c6840bf3", "price": 68.0}, "M": {"id": "33e2fb39-ec59-4f54-87c1-115abac69ddc", "price": 68.0}, "L": {"id": "544f0ee9-427c-40d5-bcba-9d521c178385", "price": 68.0}, "XL": {"id": "53f97ac6-0c6b-4944-a24c-fe7221789f8c", "price": 68.0}, "2XL": {"id": "2281f7f4-f0a0-4d78-b6a6-74acd468d0d6", "price": 70.0}, "3XL": {"id": "fa56b60f-2650-4043-9d0d-57e4df78abf0", "price": 72.0}}}, "APC-C50": {"slug": "apex-vancouver-race-day", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-vancouver-race-day", "price": 72.0, "variants": {"XS": {"id": "55bb3750-8434-4166-b1dd-414a77a343b7", "price": 68.0}, "S": {"id": "4f5ffa91-d8de-4a55-ae84-61f0e84db1c3", "price": 68.0}, "M": {"id": "14b9fd59-4309-4f54-ac2d-be4baab7b2b0", "price": 68.0}, "L": {"id": "756a654f-ea4d-4ee9-99c5-7ce6f60eff73", "price": 68.0}, "XL": {"id": "e8da8e96-d2a6-42b2-8e67-d52578ed34a1", "price": 68.0}, "2XL": {"id": "5d6b7c07-e61f-4bfa-a4fd-aea9b86c12f0", "price": 70.0}, "3XL": {"id": "336d2761-2b13-4060-b748-54a99426f77e", "price": 72.0}}}, "APC-C51": {"slug": "dallas-race-day-stitched", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/dallas-race-day-stitched", "price": 70.0, "variants": {"S": {"id": "38a4c0ba-4f5b-4767-a904-e5933a275ae1", "price": 68.0}, "M": {"id": "35f18670-8eea-4917-a999-f8fe9abfcd51", "price": 68.0}, "L": {"id": "051a0095-f822-4664-8441-d5aae7ef3fc7", "price": 68.0}, "XL": {"id": "e960cf70-613d-42fd-b4e2-9cfe7d7d607f", "price": 68.0}, "2XL": {"id": "912e8d11-ffb6-4014-a0b4-7b5caa165b96", "price": 70.0}}}, "APC-C52": {"slug": "denver-race-day-stitched", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/denver-race-day-stitched", "price": 70.0, "variants": {"S": {"id": "a43e4812-c89b-47ef-97da-696983d03795", "price": 68.0}, "M": {"id": "00ef5b78-7189-41f7-ab6e-b54f85328fe3", "price": 68.0}, "L": {"id": "216adb16-ec1a-4893-ac4c-020dff2eef59", "price": 68.0}, "XL": {"id": "2533ff5c-a0ad-45ea-aad8-7a4cee1558d7", "price": 68.0}, "2XL": {"id": "db0aa556-1bd3-45b5-acae-fb4d2026d1d5", "price": 70.0}}}, "APC-C53": {"slug": "anaheim-race-day-stitched", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/anaheim-race-day-stitched", "price": 70.0, "variants": {"S": {"id": "a55f5fff-7608-45d8-915c-892145a3cd38", "price": 68.0}, "M": {"id": "dcd868ef-3260-4cf6-b189-53141b9a187d", "price": 68.0}, "L": {"id": "449f2ef6-a3c4-4d47-b212-b86cdb904530", "price": 68.0}, "XL": {"id": "01c9fd04-90b7-4fbf-bcad-94bab8127316", "price": 68.0}, "2XL": {"id": "c2500e3e-fe9b-47ee-90ed-8dccd8ad49e1", "price": 70.0}}}, "APC-C54": {"slug": "nashville-race-day-stitched", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/nashville-race-day-stitched", "price": 70.0, "variants": {"S": {"id": "02c7859a-f8cd-4d53-91ab-24a156f8fc7d", "price": 68.0}, "M": {"id": "69b308be-209d-4e09-9e8e-af4e6a288e21", "price": 68.0}, "L": {"id": "445f25cd-17f6-467f-a92b-ba8332520537", "price": 68.0}, "XL": {"id": "30c043de-08b7-43a1-bcc1-c5729ad201d3", "price": 68.0}, "2XL": {"id": "ba10ae38-6398-4569-9f73-591aee0ae6a1", "price": 70.0}}}, "APC-C55": {"slug": "vancouver-race-day-stitched", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/vancouver-race-day-stitched", "price": 70.0, "variants": {"S": {"id": "8fe08f07-1c47-4c77-b5d2-d2b6ecda36f9", "price": 68.0}, "M": {"id": "2bdb0516-acba-4940-8d24-c83c8377e677", "price": 68.0}, "L": {"id": "0eff1b20-bf0e-404b-abda-8299b4b05643", "price": 68.0}, "XL": {"id": "2b83ca41-4a55-4da5-9554-e49d5f2ea80a", "price": 68.0}, "2XL": {"id": "6fdfbf8d-1395-46c3-bed8-151616936a6d", "price": 70.0}}}, "APC-C56": {"slug": "hyrx-finish", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-finish", "price": 38.0, "variants": {"S": {"id": "e73f0fb6-1559-463d-ad5a-d2b4327955c5", "price": 38.0}, "M": {"id": "a327d72a-28a6-4d17-a94f-0f7cc5d85bb1", "price": 38.0}, "L": {"id": "fa36084e-c4b3-46b5-84d7-af62db938a0a", "price": 38.0}, "XL": {"id": "fea0f6d7-7ec3-4a03-af52-44abd98d8f71", "price": 38.0}, "2XL": {"id": "33230674-0284-4dae-85df-e54e608d9c43", "price": 38.0}, "3XL": {"id": "2422593e-c37b-475f-ba8b-dc7f767ce667", "price": 38.0}, "4XL": {"id": "dc83d55a-b644-42c3-818a-8690e96e9cb7", "price": 38.0}}}, "APC-C57": {"slug": "cancun-race-day-windbreaker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/cancun-race-day-windbreaker", "price": 70.0, "variants": {"S": {"id": "f4942de4-966b-40dc-93b3-6e257b320de1", "price": 68.0}, "M": {"id": "6d1b6f53-d078-4c9d-93e4-7237c619737c", "price": 68.0}, "L": {"id": "c00ea05b-c385-48bb-bbcd-4369bfd4a4df", "price": 68.0}, "XL": {"id": "8fe51766-72a9-4085-a32b-eedad282f488", "price": 68.0}, "2XL": {"id": "acebab1a-7816-4c3d-82a7-6532783655c0", "price": 70.0}}}, "APC-C58": {"slug": "peak-sign", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/peak-sign", "price": 38.0, "variants": {"S": {"id": "645f1c7e-4907-4bcf-8a9e-daebd177734d", "price": 38.0}, "M": {"id": "57f58268-148b-4ecc-b505-709d256d88d2", "price": 38.0}, "L": {"id": "bec2848f-06e6-4899-8fda-42f1a43640ab", "price": 38.0}, "XL": {"id": "08301d79-e766-46d7-828f-3e97b5d8a29e", "price": 38.0}, "2XL": {"id": "6cba644c-4840-4420-9744-6e4de01cdb72", "price": 38.0}, "3XL": {"id": "ba4391d5-ad0e-4a5b-a8aa-0a61389c93d2", "price": 38.0}, "4XL": {"id": "4734dc81-3398-4abb-8ed6-eaed510c4ad9", "price": 38.0}}}, "APC-C59": {"slug": "stem-type", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/stem-type", "price": 38.0, "variants": {"S": {"id": "562ab181-736b-4ab7-8288-4fb8a1edd558", "price": 38.0}, "M": {"id": "9d1b33be-c2fd-42f9-bf42-ea1676d1b083", "price": 38.0}, "L": {"id": "79f41d9d-0bc5-4ee2-aa6d-342c5242d2c6", "price": 38.0}, "XL": {"id": "356e0c91-9eb4-4c04-abb6-e3f7b06fcf2f", "price": 38.0}, "2XL": {"id": "3af426cb-dd92-499a-8159-9a922c4539f1", "price": 38.0}, "3XL": {"id": "e802c7a8-1e32-471c-bd55-352c26236650", "price": 38.0}, "4XL": {"id": "7a0b5e92-0150-4013-a6c9-5af93f441d16", "price": 38.0}}}, "APC-C60": {"slug": "course-plate", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/course-plate", "price": 38.0, "variants": {"S": {"id": "53760bfb-1aad-474b-82e0-030833b23e61", "price": 38.0}, "M": {"id": "b8fc9941-355e-4b5f-9855-0dd49f1c83c5", "price": 38.0}, "L": {"id": "73c0cfb2-6fde-4323-934c-b6b8d4edb2e5", "price": 38.0}, "XL": {"id": "a2f84e86-bc8e-437c-90e8-7b5b5eb84482", "price": 38.0}, "2XL": {"id": "9573d27c-e7f0-4477-a77a-dd4ae491a6d5", "price": 38.0}, "3XL": {"id": "05da7ebe-4644-4f4b-8ba2-0dcc64df0ecd", "price": 38.0}, "4XL": {"id": "1ac7a9a1-2993-45cd-8f4b-55c5e91f12d1", "price": 38.0}}}, "APC-C61": {"slug": "timing-gate", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/timing-gate", "price": 38.0, "variants": {"S": {"id": "6312fa04-7e8a-46a8-be80-ea57b2ff7bc2", "price": 38.0}, "M": {"id": "f6cf9a06-1bfe-49f3-a6bd-b0cd444c80db", "price": 38.0}, "L": {"id": "ff6e0d2b-051e-48bd-9e80-a665448f832d", "price": 38.0}, "XL": {"id": "c0d002e1-31e5-4571-9d04-6943c1960e6a", "price": 38.0}, "2XL": {"id": "591f5df0-df60-4ec9-a981-e06eaf11185b", "price": 38.0}, "3XL": {"id": "cd248387-a4a6-4d79-aef9-c128cfac82fb", "price": 38.0}, "4XL": {"id": "62496ad0-23f5-437f-bcb8-42ca94ce4797", "price": 38.0}}}, "APC-C62": {"slug": "field-issue", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/field-issue", "price": 38.0, "variants": {"S": {"id": "6b8430fb-94cd-4810-931e-d2f5c6d9ca35", "price": 38.0}, "M": {"id": "28e3f93b-cd78-4f39-80b1-d94922ac25a6", "price": 38.0}, "L": {"id": "c72af6c9-5ccd-4a15-a3ae-bae139666947", "price": 38.0}, "XL": {"id": "9f6ed51c-676f-4538-9ea2-da85df2a2eee", "price": 38.0}, "2XL": {"id": "fa406485-1cf6-4e89-8518-7c8c17566d8e", "price": 38.0}, "3XL": {"id": "a44588ea-c7be-47e8-86b7-d536dc73903d", "price": 38.0}, "4XL": {"id": "fd7d50b2-f040-42ae-851a-15ff597e2349", "price": 38.0}}}, "APC-C63": {"slug": "circuit-cities", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/circuit-cities", "price": 38.0, "variants": {"S": {"id": "7188fb08-ef07-42b7-a8cb-f324f2d0b7c6", "price": 38.0}, "M": {"id": "5a3fe25a-0e4d-494e-a587-26dc8421ea7b", "price": 38.0}, "L": {"id": "a98cc769-0c36-46ee-93e1-444f9b2d3ee8", "price": 38.0}, "XL": {"id": "0293d30a-d2db-40ca-b7cd-adb5106e1d18", "price": 38.0}, "2XL": {"id": "ed8f454d-9fca-4f98-9d63-37bdcef63c28", "price": 38.0}, "3XL": {"id": "d7a5ae5b-1af0-45c1-82dd-c7e3a155fac7", "price": 38.0}, "4XL": {"id": "c326c08e-21ba-4e3f-b6aa-77f7cdae0f00", "price": 38.0}}}, "APC-C64": {"slug": "hold-the-pace", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hold-the-pace", "price": 38.0, "variants": {"S": {"id": "4a98dd22-b11e-44fc-a3d4-946fe783fcb4", "price": 38.0}, "M": {"id": "4e0fe150-d1cd-472e-84cd-cc0d8c951882", "price": 38.0}, "L": {"id": "ed67282e-1643-4ce3-8450-9615f571eac2", "price": 38.0}, "XL": {"id": "fbeaa441-b528-4abb-81b7-5e2afa155344", "price": 38.0}, "2XL": {"id": "bb7ed958-a897-43ce-952d-dcccff3c7901", "price": 38.0}, "3XL": {"id": "984f7a5a-dddb-4c38-aac9-61d8df4726f4", "price": 38.0}, "4XL": {"id": "d23af8d5-a2e4-4723-b4d8-bf88ed454a23", "price": 38.0}}}, "APC-C65": {"slug": "outline-mark", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/outline-mark", "price": 40.58, "variants": {"XS": {"id": "1daa4c9e-015a-42bb-acb7-83d4d3068782", "price": 38.0}, "S": {"id": "a0251260-31f9-43f8-8afa-ee7a0dd7d20b", "price": 38.0}, "M": {"id": "5a6256aa-5cc7-49cb-ba78-24e8556e5bfc", "price": 38.0}, "L": {"id": "86912b2a-0553-4269-8f9f-b643e3583a7e", "price": 38.0}, "XL": {"id": "80de7a2e-8455-4152-88d1-c9d04994fe6a", "price": 38.0}, "2XL": {"id": "dc594c4a-c28d-4d53-9511-508bccf3946c", "price": 38.78}, "3XL": {"id": "cdbe6508-c7ea-4a58-98bf-256afddd9a29", "price": 40.58}}}, "APC-C66": {"slug": "eight-marks", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/eight-marks", "price": 42.0, "variants": {"S": {"id": "13e9c32e-52b4-44a5-9695-9039c53aea5d", "price": 38.0}, "M": {"id": "0a2e5d0f-fbce-46ab-a2b9-a66fd0c627e0", "price": 38.0}, "L": {"id": "38840169-b513-42d8-a93f-1097041250d8", "price": 38.0}, "XL": {"id": "659e147c-1f25-4972-86b5-81b5c42a0f50", "price": 38.0}, "2XL": {"id": "8145b5ec-ab91-4419-b33e-275125952977", "price": 40.0}, "3XL": {"id": "bd0c610d-41a7-4de5-b0b5-9c64e70ac54d", "price": 42.0}}}, "APC-C67": {"slug": "call-room", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/call-room", "price": 69.1, "variants": {"XS": {"id": "a76090ce-97d0-4f10-b701-45ecd6e82c44", "price": 65.0}, "S": {"id": "180f74fc-7a5f-4faf-8120-7704faff72d7", "price": 65.0}, "M": {"id": "e919f2c3-0cfb-4275-8966-d30ba6d886b2", "price": 65.0}, "L": {"id": "b29e1884-cd3e-4d80-bdae-382b5144c69b", "price": 65.0}, "XL": {"id": "505c615a-499f-448f-b52e-ad840fd4aeff", "price": 65.0}, "2XL": {"id": "43bbb103-0596-434b-b360-59818d9fc017", "price": 67.1}, "3XL": {"id": "86752566-ab40-4739-a230-ab79410714db", "price": 69.1}}}, "APC-C68": {"slug": "sleeve-seal", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/sleeve-seal", "price": 69.1, "variants": {"XS": {"id": "abee2edf-0eea-439f-823a-9c6e11f7531b", "price": 65.0}, "S": {"id": "365a524b-fef1-4e17-be79-e724063f5024", "price": 65.0}, "M": {"id": "4b2ee9e5-400e-49b0-a785-fe80140fdaa5", "price": 65.0}, "L": {"id": "c736f69d-e59f-444d-8af2-b9e6bce6ec3f", "price": 65.0}, "XL": {"id": "89ef5e58-08ee-4ab7-845c-6924159b6ccc", "price": 65.0}, "2XL": {"id": "ce0c357a-0fae-4a9d-b99b-bdc7f541737c", "price": 67.1}, "3XL": {"id": "995b4e99-0a38-489c-9fca-59893e05116a", "price": 69.1}}}, "APC-C69": {"slug": "work-the-loop", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/work-the-loop", "price": 69.1, "variants": {"XS": {"id": "14db75c3-1a0f-4d84-ad50-796389182463", "price": 65.0}, "S": {"id": "6f519ccf-5646-45ac-85cf-5584abbbe0c2", "price": 65.0}, "M": {"id": "85038b48-fdd8-4496-9bcd-3cfbe505c1a3", "price": 65.0}, "L": {"id": "febf40bc-cc56-400f-9133-5346051fa5a4", "price": 65.0}, "XL": {"id": "0e83c521-4644-4bb0-a0d4-1c4e49c43381", "price": 65.0}, "2XL": {"id": "63a9a55d-669f-47b6-b088-da107c4bb101", "price": 67.1}, "3XL": {"id": "6fe053e7-3a25-4854-a3d9-1a7b3bded65e", "price": 69.1}}},"APC-C70": {"slug": "phoenix-race-day-windbreaker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/phoenix-race-day-windbreaker", "price": 70.0, "variants": {"S": {"id": "0b0ff21b-f8e1-4458-ba5d-b3f40c6be867", "price": 68.0}, "M": {"id": "a529a12a-1dc8-4e71-a77d-f5cea4de4fbb", "price": 68.0}, "L": {"id": "5e07f5e1-8cf3-4500-9645-aa9373502104", "price": 68.0}, "XL": {"id": "e6f6636c-a389-4d91-af91-60d343149fdf", "price": 68.0}, "2XL": {"id": "30e98bfb-723f-40c7-bd4e-c306c470e1ee", "price": 70.0}}}, "APC-C71": {"slug": "phoenix-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/phoenix-crest", "price": 44.0, "variants": {"S": {"id": "a534b315-7fa2-4562-95d6-106655c076fa", "price": 38.0}, "M": {"id": "a6c08ce4-0dda-4085-8f9e-28dd8cab7f56", "price": 38.0}, "L": {"id": "e34e3bbb-ed51-4012-8b48-da33732ffd6d", "price": 38.0}, "XL": {"id": "0f5a8049-c4c8-4a3c-993f-e93b274f940f", "price": 38.0}, "2XL": {"id": "6371549d-7a81-439c-96f4-f961e40aa2f6", "price": 40.0}, "3XL": {"id": "866911f7-6c7b-44dd-ade8-6f30fcf29498", "price": 42.0}, "4XL": {"id": "ceaf10c0-4c22-4cfe-bd33-91f6c314657b", "price": 44.0}}},"APC-C72": {"slug": "las-vegas-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/las-vegas-crest", "price": 44.0, "variants": {"S": {"id": "ab585931-bd6b-453d-b918-3f8d5b0fbe7c", "price": 38.0}, "M": {"id": "1cb140cb-9f34-42db-ab3a-ea402159cc0c", "price": 38.0}, "L": {"id": "73fd73d9-6ba7-448d-a0d0-fe0d2e4ccf7f", "price": 38.0}, "XL": {"id": "a33b4704-5e61-4958-b4db-49b87aed341e", "price": 38.0}, "2XL": {"id": "d54a8f85-0e8f-4486-9d43-b9bf425d4db3", "price": 40.0}, "3XL": {"id": "44dc8df4-bf8a-48a6-bdf3-7c7426041962", "price": 42.0}, "4XL": {"id": "bb2b10aa-be81-42ac-8afc-5e9bce149c23", "price": 44.0}}}, "APC-C73": {"slug": "guadalajara-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/guadalajara-crest", "price": 44.0, "variants": {"S": {"id": "32eb4aa8-50b6-40ea-9591-92bcf8345025", "price": 38.0}, "M": {"id": "50f3d577-8450-49e3-81b3-b048948abac7", "price": 38.0}, "L": {"id": "5892160e-6f19-408d-8267-16f2605df149", "price": 38.0}, "XL": {"id": "3ca405e8-111a-4193-8881-75d12fffa6c6", "price": 38.0}, "2XL": {"id": "fc9375eb-c892-41b0-8ee3-2e623ff5ed41", "price": 40.0}, "3XL": {"id": "b693c5a2-083c-4c15-8f62-b6a63610a60f", "price": 42.0}, "4XL": {"id": "03bd5110-d27e-4eac-941f-f60535ee35a2", "price": 44.0}}}, "APC-C74": {"slug": "apex-heavyweight-hybrid-tee-compromised-running-club", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-heavyweight-hybrid-tee-compromised-running-club", "price": 44.0, "variants": {"S": {"id": "00b46abe-f4bb-4dc0-82de-e7fe669f0579", "price": 38.0}, "M": {"id": "367c120b-affe-4f5c-b343-652c3ddcbdfb", "price": 38.0}, "L": {"id": "8d3cf41a-8f43-4e7c-8686-f6023d613ffd", "price": 38.0}, "XL": {"id": "f3676722-c952-43be-b761-ea6aac9cd420", "price": 38.0}, "2XL": {"id": "92067371-2226-4722-8303-8d30cba26c78", "price": 40.0}, "3XL": {"id": "387f6b07-7cea-4c56-a748-4421ff3831ca", "price": 42.0}, "4XL": {"id": "641c3210-09a8-4879-8462-a5996e6493fc", "price": 44.0}}}, "APC-C75": {"slug": "apex-dallas-race-day-printable", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/apex-dallas-race-day-printable", "price": 72.0, "variants": {"XS": {"id": "a19db7e8-5e2e-4662-a5af-d5d6c84b3175", "price": 68.0}, "S": {"id": "82d1522f-7910-45f3-8ebf-f5e13d4e94c7", "price": 68.0}, "M": {"id": "e31614ab-dfcf-45a8-ad95-23ee6b5741bf", "price": 68.0}, "L": {"id": "d6da4aa2-4734-4ebb-a4c2-49b47f0330bd", "price": 68.0}, "XL": {"id": "5177dc39-a60e-4373-be5e-0de64c05ee98", "price": 68.0}, "2XL": {"id": "875b9f34-2a3f-470f-a8ea-3e70dbb6487b", "price": 70.0}, "3XL": {"id": "d5bdaa68-ecc9-4d65-85bd-441cd1e7391b", "price": 72.0}}},"APC-C77": {"slug": "miami-beach-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/miami-beach-crest", "price": 44.0, "variants": {"S": {"id": "a60802f8-605a-44d2-8630-6f12b31414bf", "price": 38}, "M": {"id": "71caa0c6-6db1-4e7b-84e6-73bbf85a7c5f", "price": 38}, "L": {"id": "cdadc432-bedf-408a-b1a4-1f01f343935b", "price": 38}, "XL": {"id": "5300d41b-90cb-4308-b9cc-05e378e7e558", "price": 38}, "2XL": {"id": "65780fa4-6050-4025-a648-e16c5e2aa1dd", "price": 40}, "3XL": {"id": "289c168f-7223-46d6-92eb-5476d7179243", "price": 42}, "4XL": {"id": "77f982be-c4ae-43a5-86a1-a54e0575c2e4", "price": 44}}}, "APC-C78": {"slug": "houston-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/houston-crest", "price": 44.0, "variants": {"S": {"id": "59419bd7-7295-4623-9e14-ab3fcb084cf6", "price": 38}, "M": {"id": "4a941c40-be0c-49d7-9634-20627c9269ab", "price": 38}, "L": {"id": "76eaa20a-2d54-49a8-be4d-fc20073c8d8d", "price": 38}, "XL": {"id": "9d8d1493-0a43-4fbd-884c-db27a2b67b08", "price": 38}, "2XL": {"id": "88096d58-3e23-46e8-8be5-6b8fb7470f27", "price": 40}, "3XL": {"id": "d618265f-2140-4649-9806-0d0d24ef2c4e", "price": 42}, "4XL": {"id": "d05a3967-24a6-4691-92a1-ca92f916d0d4", "price": 44}}}, "APC-C79": {"slug": "monterrey-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/monterrey-crest", "price": 44.0, "variants": {"S": {"id": "cd9fa074-be5c-4f9b-a4ea-dad89f296f18", "price": 38}, "M": {"id": "76d24107-0d70-4cac-8337-d00dead9f4c8", "price": 38}, "L": {"id": "35764db1-da47-48a6-bd16-28da889eda44", "price": 38}, "XL": {"id": "15e199d7-711b-4fba-a328-844ef0bf19dd", "price": 38}, "2XL": {"id": "ab2759dd-0db9-49ce-8159-1c06f41a3b0a", "price": 40}, "3XL": {"id": "9781b51a-57b1-402b-b15d-0077a66d1d8e", "price": 42}, "4XL": {"id": "3475fb42-84e0-48b3-b27e-6b09137dd3c8", "price": 44}}}, "APC-C80": {"slug": "atlanta-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/atlanta-crest", "price": 44.0, "variants": {"S": {"id": "7c3b2d8e-0c92-45b0-b352-9e199ecc56f5", "price": 38}, "M": {"id": "206a4c71-ac73-4e2a-afca-4c0f152dbe41", "price": 38}, "L": {"id": "11f36d8c-90c9-4717-b147-110bf1b6ff21", "price": 38}, "XL": {"id": "19f729cd-a630-43d1-9a35-afa07c92db76", "price": 38}, "2XL": {"id": "3aca2fed-0903-44ad-ba3d-157facf98014", "price": 40}, "3XL": {"id": "552d28a0-4554-4cd2-b437-045652cf4aec", "price": 42}, "4XL": {"id": "764b1079-309f-46dc-80bc-9143c2d8e2b6", "price": 44}}}, "APC-C81": {"slug": "minneapolis-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/minneapolis-crest", "price": 44.0, "variants": {"S": {"id": "ff08b8f6-2956-40ca-a347-37ad5eafb21e", "price": 38}, "M": {"id": "849e9c3b-3052-4002-b0fc-3094a62452cd", "price": 38}, "L": {"id": "e767e6d9-12d1-4f59-a592-db7cd5894637", "price": 38}, "XL": {"id": "a94a0c37-1f8c-4dad-8012-c98069842200", "price": 38}, "2XL": {"id": "af539aac-55e3-4823-b33e-58146a736dc0", "price": 40}, "3XL": {"id": "defecb3c-66bd-47e7-90af-b35681228200", "price": 42}, "4XL": {"id": "e58231f6-a963-4cae-b0b0-09e8538eff52", "price": 44}}}, "APC-C82": {"slug": "san-diego-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/san-diego-crest", "price": 44.0, "variants": {"S": {"id": "5264d7ce-c4f4-4500-b787-8c2292715e4a", "price": 38}, "M": {"id": "6a8c0eb3-e2dd-416f-a506-56341925f45c", "price": 38}, "L": {"id": "7160f271-407c-4b90-9e92-12cc01f4f026", "price": 38}, "XL": {"id": "3b95b171-3ce2-458f-86e1-bfdb33429e8a", "price": 38}, "2XL": {"id": "2f42d8c9-f0ff-45ac-a7a5-b6846fc371ed", "price": 40}, "3XL": {"id": "a440eb56-e9a5-40d7-8949-69af23026a06", "price": 42}, "4XL": {"id": "96edf678-c0ec-421a-aa60-9082624217ac", "price": 44}}}, "APC-C83": {"slug": "portland-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/portland-crest", "price": 44.0, "variants": {"S": {"id": "df04c983-4f44-4bdb-8eaf-f4c8365a34e0", "price": 38}, "M": {"id": "e08d4c4f-86bd-46ff-8751-f563ce3b7012", "price": 38}, "L": {"id": "4f2a652d-cb2b-4801-97ba-cbd39d026a04", "price": 38}, "XL": {"id": "cb5c9be4-25ba-4ec1-8b5a-1c346e801fc1", "price": 38}, "2XL": {"id": "edd6f169-9295-4d64-9e37-b8441e6f16ff", "price": 40}, "3XL": {"id": "e7998830-11f5-4c83-a760-bacda71e2011", "price": 42}, "4XL": {"id": "28199a41-60ee-4d4b-80f0-d0f13ea63d91", "price": 44}}},"APC-C84": {"slug": "engine-training-tank-black", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/engine-training-tank-black", "price": 33, "variants": {"XS": {"id": "d3ea97cf-375b-415a-b5f7-bdc60dcfe215", "price": 33}, "S": {"id": "265d963e-e964-44d4-9021-36103b09312d", "price": 33}, "M": {"id": "fdf31e31-6751-4b0b-944c-8f0f424ef795", "price": 33}, "L": {"id": "e6e0797a-b54a-4887-8df3-0c5b7339010e", "price": 33}, "XL": {"id": "1a76b5b1-c33f-46da-83c8-e2fe65b95dca", "price": 33}, "2XL": {"id": "0d80b68c-8d39-476b-81e7-ffa29959b5c5", "price": 33}}}, "APC-C85": {"slug": "engine-training-tank-mint", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/engine-training-tank-mint", "price": 33, "variants": {"XS": {"id": "14ce775a-98ce-45aa-b422-df8f69fdad32", "price": 33}, "S": {"id": "4252871b-615d-484c-9f33-e85adc3d07b3", "price": 33}, "M": {"id": "e63cd1f6-9517-4356-9ad2-06888d35c20c", "price": 33}, "L": {"id": "b8969b43-10c5-406c-a0e1-f43ef4be8873", "price": 33}, "XL": {"id": "5af243e7-38fa-4d7b-ad2e-ee803ce27d40", "price": 33}, "2XL": {"id": "91c2d5ba-2ed8-4ed4-9d1b-e11d2fb67dc6", "price": 33}}},"APC-C86": {"slug": "atlanta-race-day-windbreaker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/atlanta-race-day-windbreaker", "price": 70, "variants": {"S": {"id": "b287a777-589f-42c8-966b-dad86de048a1", "price": 68.0}, "M": {"id": "8bfb972f-49a9-471c-8cdd-f8d50794a2d8", "price": 68.0}, "L": {"id": "4b1a050c-1b8e-4115-9a81-a54ed65ca13e", "price": 68.0}, "XL": {"id": "874fcade-991f-4692-bd69-822756fa8b1b", "price": 68.0}, "2XL": {"id": "744148ca-c055-4ce1-9246-b64af23183d0", "price": 70.0}}}, "APC-C87": {"slug": "houston-race-day-windbreaker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/houston-race-day-windbreaker", "price": 70, "variants": {"S": {"id": "86c0dd9a-25c8-4e4f-9db2-26eff2cbfaa7", "price": 68.0}, "M": {"id": "10803728-2e5c-46d8-b3f1-ef0140ff51ea", "price": 68.0}, "L": {"id": "47da30d4-31eb-4b70-8105-0d5f9d399169", "price": 68.0}, "XL": {"id": "4305787c-401e-474c-af09-4b891edeecda", "price": 68.0}, "2XL": {"id": "f0de39ed-a709-4b6c-8a1c-a362de6eb813", "price": 70.0}}}, "APC-C88": {"slug": "las-vegas-race-day-windbreaker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/las-vegas-race-day-windbreaker", "price": 70, "variants": {"S": {"id": "e3b8f27e-2647-4e4f-9947-62b1f9abd283", "price": 68.0}, "M": {"id": "943185f6-f723-4e33-852f-7bb3982ceabd", "price": 68.0}, "L": {"id": "72946e79-bc04-42e8-b9f9-31c5617c6416", "price": 68.0}, "XL": {"id": "cfab7980-dc4d-447b-99df-e25151e10564", "price": 68.0}, "2XL": {"id": "66274f95-6430-43c4-ba0b-b790e33510fe", "price": 70.0}}}, "APC-C89": {"slug": "miami-beach-race-day-windbreaker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/miami-beach-race-day-windbreaker", "price": 70, "variants": {"S": {"id": "7f12e670-c3c7-4c10-b669-042fe315bb57", "price": 68.0}, "M": {"id": "b429755e-eea6-4cbb-8e1b-432d4ef33dab", "price": 68.0}, "L": {"id": "aad36a7d-6e50-43dd-bf7e-6cf4fa4de5e3", "price": 68.0}, "XL": {"id": "034c4ab1-c6fa-4a7e-95a3-c1c15d5861ff", "price": 68.0}, "2XL": {"id": "505dfb7c-716a-433f-8ab6-35d10e264960", "price": 70.0}}},"APC-C90": {"slug": "chicago-race-day-windbreaker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/chicago-race-day-windbreaker", "price": 70, "variants": {"S": {"id": "2c62e211-6b00-4e1d-abc8-854d31b00e46", "price": 68.0}, "M": {"id": "3b2a82af-6819-4811-b9ad-867b2bc5df60", "price": 68.0}, "L": {"id": "cae00bf4-01b1-4e8d-b5b2-a97b0bca17c9", "price": 68.0}, "XL": {"id": "ed8f3896-8488-4ded-b3c7-2ab1e8d6d7df", "price": 68.0}, "2XL": {"id": "e5db23e0-d750-45a3-87ba-df851eee9fb5", "price": 70.0}}}, "APC-C91": {"slug": "guadalajara-race-day-windbreaker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/guadalajara-race-day-windbreaker", "price": 70, "variants": {"S": {"id": "9ca3d781-2178-4206-aad5-acd227fe014b", "price": 68.0}, "M": {"id": "603bca03-6f97-4def-a86c-8c3ed56551c7", "price": 68.0}, "L": {"id": "dfd0a546-ea3c-4e37-91a1-3a4649b5aee7", "price": 68.0}, "XL": {"id": "950e0b3c-0b62-40e7-9683-4b3aa94f7c4f", "price": 68.0}, "2XL": {"id": "812a9fd1-8a3b-4b80-943a-7d9494e52596", "price": 70.0}}}, "APC-C92": {"slug": "minneapolis-race-day-windbreaker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/minneapolis-race-day-windbreaker", "price": 70, "variants": {"S": {"id": "3157f78b-df20-4ed4-8c1f-97387d4694a6", "price": 68.0}, "M": {"id": "710ce504-818c-4783-8f46-dfdae1eaf3f2", "price": 68.0}, "L": {"id": "34d9672c-f7ef-4a79-9c1e-929a8430aadf", "price": 68.0}, "XL": {"id": "c36fcce1-d68f-4e07-a310-dbdd5bb583ab", "price": 68.0}, "2XL": {"id": "4660305d-10aa-4607-9054-e99276284800", "price": 70.0}}}, "APC-C93": {"slug": "monterrey-race-day-windbreaker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/monterrey-race-day-windbreaker", "price": 70, "variants": {"S": {"id": "139d343f-2145-4b59-9691-7340f268fe82", "price": 68.0}, "M": {"id": "936a431d-5a0b-43e2-aa28-1171a9322bfc", "price": 68.0}, "L": {"id": "e6824bb0-0cd0-423b-bb98-892e92ccba73", "price": 68.0}, "XL": {"id": "cc4c1ded-a807-412d-8a01-abc315a9d8d3", "price": 68.0}, "2XL": {"id": "de98e702-dc6b-4014-9128-e133def80d93", "price": 70.0}}}, "APC-C94": {"slug": "portland-race-day-windbreaker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/portland-race-day-windbreaker", "price": 70, "variants": {"S": {"id": "b56c90f5-cbea-417d-b302-5a12b83c8527", "price": 68.0}, "M": {"id": "2da57223-3604-4302-a341-7cf64f6273c0", "price": 68.0}, "L": {"id": "024420c9-65a4-446d-8b78-bb73151030a3", "price": 68.0}, "XL": {"id": "627ec9a7-ffc0-4c92-8be8-ef16fa401723", "price": 68.0}, "2XL": {"id": "238f83ff-6257-4cbe-bb3e-9c5f0638cb8f", "price": 70.0}}}, "APC-C95": {"slug": "san-diego-race-day-windbreaker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/san-diego-race-day-windbreaker", "price": 70, "variants": {"S": {"id": "7cb2a9b9-6d69-47ec-a38c-275641ecbb07", "price": 68.0}, "M": {"id": "7f3b9f45-b069-46ba-9bbe-4d63dc6f3977", "price": 68.0}, "L": {"id": "87a604b4-60a7-4bf3-b3ef-80d03bd961cb", "price": 68.0}, "XL": {"id": "4248049a-a6dc-4b03-a8e1-ab033577c511", "price": 68.0}, "2XL": {"id": "466cd0bb-6585-4ebf-8f5c-1a154b594d6b", "price": 70.0}}},"APC-C96": {"slug": "london-race-day-windbreaker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/london-race-day-windbreaker", "price": 70, "variants": {"S": {"id": "ea4ebd0c-53db-4040-887f-ab7103e27221", "price": 68.0}, "M": {"id": "a07747e0-c54b-425b-97be-34cc5cabe700", "price": 68.0}, "L": {"id": "8e540e63-e2e6-4e6d-80c0-bf85dbe35d25", "price": 68.0}, "XL": {"id": "c6872589-3c97-4f9d-b54c-21290e2b0771", "price": 68.0}, "2XL": {"id": "0514cc6d-5b3f-489e-aa08-c5eac28320a5", "price": 70.0}}}, "APC-C97": {"slug": "paris-race-day-windbreaker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/paris-race-day-windbreaker", "price": 70, "variants": {"S": {"id": "2749d6b2-fd67-4e96-8240-8488c373258d", "price": 68.0}, "M": {"id": "5746eb32-844b-4995-b48f-a826b42ca61b", "price": 68.0}, "L": {"id": "304f0dd3-2e04-4ce4-b231-15bd8d191b45", "price": 68.0}, "XL": {"id": "7049617e-48e6-419b-8424-f6a71f105204", "price": 68.0}, "2XL": {"id": "f90139bb-ef3e-427c-ab1b-15d07951c738", "price": 70.0}}}, "APC-C98": {"slug": "hong-kong-race-day-windbreaker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hong-kong-race-day-windbreaker", "price": 70, "variants": {"S": {"id": "13969f0e-3247-4ae1-b424-9a5225660bed", "price": 68.0}, "M": {"id": "e3ca04c9-715d-44bc-99d1-7d370b8532e6", "price": 68.0}, "L": {"id": "5226c7f7-01ea-4736-bd65-61a9b9c6764c", "price": 68.0}, "XL": {"id": "38cf14e6-24f2-4be7-8020-f1192d670fca", "price": 68.0}, "2XL": {"id": "776923ab-9033-40da-87e2-f45493d4293c", "price": 70.0}}},"APC-C99": {"slug": "london-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/london-crest", "price": 44, "variants": {"S": {"id": "7326ec68-ac5f-46e6-a541-ab993108333b", "price": 38.0}, "M": {"id": "dc540f2d-9248-40c7-b5d3-b0b26f4fdf20", "price": 38.0}, "L": {"id": "d68b04a2-4bd2-4ec5-957c-8c6e25787e53", "price": 38.0}, "XL": {"id": "e469a54b-7433-4ea5-a970-55fb0b0f7cc4", "price": 38.0}, "2XL": {"id": "5ceec424-7513-4327-9719-9a385f6af7e1", "price": 40.0}, "3XL": {"id": "36ab3c22-5a91-4b47-8c95-eeec3e758baf", "price": 42.0}, "4XL": {"id": "bfa15794-4421-4913-9de4-5a4c993be4dc", "price": 44.0}}}, "APC-C100": {"slug": "paris-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/paris-crest", "price": 44, "variants": {"S": {"id": "da131dcd-df45-431f-bdc8-011d7990a54c", "price": 38.0}, "M": {"id": "9bbf7151-2627-447e-ab00-b0fcded3f1f3", "price": 38.0}, "L": {"id": "e6371a6b-41f7-44bc-b699-c021250e7313", "price": 38.0}, "XL": {"id": "980109c9-356a-4645-863d-5190b305f24b", "price": 38.0}, "2XL": {"id": "2666c277-ac81-4730-a55e-99d65da8b4b5", "price": 40.0}, "3XL": {"id": "860fdff0-5aa5-43a2-afec-cb0ab9446a4a", "price": 42.0}, "4XL": {"id": "c0a12ca3-fd75-4bba-a6e6-6ba12fd46fe3", "price": 44.0}}}, "APC-C101": {"slug": "hong-kong-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hong-kong-crest", "price": 44, "variants": {"S": {"id": "8579872d-7ae1-45d1-b992-abcc6b4b78b8", "price": 38.0}, "M": {"id": "634dd3d1-1577-4a8c-a4e5-57da4e42bf3c", "price": 38.0}, "L": {"id": "ed6fc572-6dc6-43b7-ae50-aeabfe2ded7e", "price": 38.0}, "XL": {"id": "7671e0ca-be3e-49b4-b77a-da8b17b51ad5", "price": 38.0}, "2XL": {"id": "b596f869-e5f1-4380-955e-4ac32ace69da", "price": 40.0}, "3XL": {"id": "3cb236f1-b1c4-4f0c-914c-d1c3c9010536", "price": 42.0}, "4XL": {"id": "04a359b6-0221-4cf3-8bbd-d0de49d5f426", "price": 44.0}}}, "APC-C102": {"slug": "chicago-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/chicago-crest", "price": 44, "variants": {"S": {"id": "923b9276-a722-499f-ac99-cb50f6392f18", "price": 38.0}, "M": {"id": "a2874c91-fb9c-4e4d-a893-c9125ecf73b5", "price": 38.0}, "L": {"id": "792601c6-71b5-4537-937a-4fb97a7cef82", "price": 38.0}, "XL": {"id": "d49a01ff-dda2-479a-b3e4-44773117daa3", "price": 38.0}, "2XL": {"id": "b688eb4c-37da-4be4-bce1-4c6cdaa173ce", "price": 40.0}, "3XL": {"id": "b2758d93-6f56-4663-a245-624cec1fd88d", "price": 42.0}, "4XL": {"id": "276738d9-0a58-40bf-af65-d13590a40f2a", "price": 44.0}}}, "APC-C103": {"slug": "cancun-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/cancun-crest", "price": 44, "variants": {"S": {"id": "cb42d937-6426-4d3c-b235-31e5f974ad20", "price": 38.0}, "M": {"id": "dfe9a3f1-3491-497e-a139-a819c58c4a81", "price": 38.0}, "L": {"id": "95514ae7-e52a-441a-a744-bacefc5fcbff", "price": 38.0}, "XL": {"id": "d7cc6942-99b5-441f-9a48-d233fda223be", "price": 38.0}, "2XL": {"id": "0c8aecf2-ba4e-4993-9051-ad193b49f03a", "price": 40.0}, "3XL": {"id": "cc82e2e6-9100-4ee0-a288-e6d37f8c3663", "price": 42.0}, "4XL": {"id": "5b8d685c-a6e8-4480-82ad-85e3ebaf8586", "price": 44.0}}},"APC-C104": {"slug": "dallas-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/dallas-crest", "price": 44, "variants": {"S": {"id": "248b89fd-f3df-4e43-8a65-962465a66ac4", "price": 38.0}, "M": {"id": "96d2fa93-9ef4-4e5c-81b2-6a3c340ea9e9", "price": 38.0}, "L": {"id": "8f155a16-9995-4852-96d6-a1149361ba19", "price": 38.0}, "XL": {"id": "32c8e458-3231-40bf-9605-b342fc78fccc", "price": 38.0}, "2XL": {"id": "d0d93cbb-657c-4b22-85a6-399674319c31", "price": 40.0}, "3XL": {"id": "ed5d96e3-d00d-44d9-acfb-b18f83825b47", "price": 42.0}, "4XL": {"id": "dac2354b-a120-450c-a88e-c92b8463ff3c", "price": 44.0}}}, "APC-C105": {"slug": "denver-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/denver-crest", "price": 44, "variants": {"S": {"id": "21aaa71b-00dd-47a5-bf12-6164f24d3b66", "price": 38.0}, "M": {"id": "13cc9ebe-2371-487d-9611-87a2d2b8ad5b", "price": 38.0}, "L": {"id": "23ca6705-69bf-49dc-944b-24293ec72c61", "price": 38.0}, "XL": {"id": "c69e4652-59ed-4a06-87e1-83792468b180", "price": 38.0}, "2XL": {"id": "5bb43c54-a5da-42a4-9a4a-4c5a923204b0", "price": 40.0}, "3XL": {"id": "fcd9cb11-47a5-4734-9e66-7071ff458d95", "price": 42.0}, "4XL": {"id": "a88193ff-fe92-40a6-9a36-148a9218947d", "price": 44.0}}}, "APC-C106": {"slug": "anaheim-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/anaheim-crest", "price": 44, "variants": {"S": {"id": "d0b97a66-1886-4714-99cf-072d8b692f9c", "price": 38.0}, "M": {"id": "26d8fe02-bde8-4e4e-a49d-933a1d7337f1", "price": 38.0}, "L": {"id": "cb704244-db1e-43be-8d13-12b1586e8ee3", "price": 38.0}, "XL": {"id": "6e0fabad-f297-4e68-a102-5c121b7dc74a", "price": 38.0}, "2XL": {"id": "ad844c19-8b75-4f7f-adb6-a76e318b1aad", "price": 40.0}, "3XL": {"id": "db62f12e-3cc8-4c78-aba4-4dbd982acc02", "price": 42.0}, "4XL": {"id": "4682f030-70a8-4684-ba1d-72e1773ca877", "price": 44.0}}}, "APC-C107": {"slug": "nashville-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/nashville-crest", "price": 44, "variants": {"S": {"id": "8410ca89-4a2a-4ba7-afcb-1a4038a15012", "price": 38.0}, "M": {"id": "f931a7fa-682b-4352-bacb-3415c86aee34", "price": 38.0}, "L": {"id": "620e93fd-4435-4eab-895a-460a22defc5a", "price": 38.0}, "XL": {"id": "1ebc961f-0800-4c47-afce-1038b0a85842", "price": 38.0}, "2XL": {"id": "ee0846d3-3bde-448d-850c-805d0848204c", "price": 40.0}, "3XL": {"id": "01840c4a-650b-4a17-856e-6c8a3a76f070", "price": 42.0}, "4XL": {"id": "e33293f0-b270-46a3-a6fb-06fce6ba1b6a", "price": 44.0}}}, "APC-C108": {"slug": "vancouver-crest", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/vancouver-crest", "price": 44, "variants": {"S": {"id": "74cc8328-6150-400e-b708-38df6339bae5", "price": 38.0}, "M": {"id": "cdf1c7c7-2b29-4239-813b-2f02ab9a8a55", "price": 38.0}, "L": {"id": "c999a0b5-8546-4621-b339-bdadf3a631ac", "price": 38.0}, "XL": {"id": "96d3d984-18c2-453a-8996-a00bf788a7fe", "price": 38.0}, "2XL": {"id": "1620f420-3bac-41f5-9e13-17ef6e84e72c", "price": 40.0}, "3XL": {"id": "401aef45-2ccf-4a1b-a44c-1dc57ee7049a", "price": 42.0}, "4XL": {"id": "8764c153-97bd-4ae5-9f32-b562178184cb", "price": 44.0}}},"APC-C109": {"slug": "engine-sports-bra-black", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/engine-sports-bra-black", "price": 43.0, "variants": {"XS": {"id": "c40a7a18-0c89-4af2-840a-1825e4cd5b51", "price": 43.0}, "S": {"id": "d9cf72dc-7d12-4696-b444-9349af8bf0ae", "price": 43.0}, "M": {"id": "d5f98994-485d-49a9-a4ac-b09e9bb44dca", "price": 43.0}, "L": {"id": "d8a08e1a-a418-4d19-b130-4d9dd7305509", "price": 43.0}, "XL": {"id": "7032a022-1d2c-45ab-be3e-aa2675e3219b", "price": 43.0}, "2XL": {"id": "d7533dcd-3750-4660-988e-175ff1f97594", "price": 43.0}}}, "APC-C110": {"slug": "engine-sports-bra-mint", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/engine-sports-bra-mint", "price": 43.0, "variants": {"XS": {"id": "cb561182-0892-4a4b-b2a3-9b58b14da67b", "price": 43.0}, "S": {"id": "ba3c75bb-4f70-4392-b77d-7616bed88ff6", "price": 43.0}, "M": {"id": "1e405274-7154-4e01-93b3-88b3bb0d208d", "price": 43.0}, "L": {"id": "262fbc77-09c3-4140-8f61-6fc7461c6e7c", "price": 43.0}, "XL": {"id": "565507c8-c14f-4075-b7ce-4a734e9a5ba6", "price": 43.0}, "2XL": {"id": "bd869695-23e4-4772-a6e3-dd4ba9c76d27", "price": 43.0}}}, "APC-C111": {"slug": "engine-biker-shorts-black", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/engine-biker-shorts-black", "price": 38.0, "variants": {"XS": {"id": "b9cb3ed4-c53c-445e-87f4-0b20de0a1d01", "price": 38.0}, "S": {"id": "dfc9a694-cada-4809-b6de-2a86a9869267", "price": 38.0}, "M": {"id": "e77465af-f04a-4a7f-b4d3-95d99ac8a49a", "price": 38.0}, "L": {"id": "e7b07b1f-4a74-4cf2-bce8-f90ed9d50ffa", "price": 38.0}, "XL": {"id": "c547dd8b-4163-4d30-9495-711a785a1a9f", "price": 38.0}, "2XL": {"id": "30308846-c11c-4e52-9643-c69e0dddc7b6", "price": 38.0}, "3XL": {"id": "f9cdda30-2f80-4f08-84e2-0c85727133cf", "price": 38.0}}}, "APC-C112": {"slug": "engine-biker-shorts-mint", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/engine-biker-shorts-mint", "price": 38.0, "variants": {"XS": {"id": "311f25c4-c56a-490f-810a-ed3fb3c05c2c", "price": 38.0}, "S": {"id": "3604b744-fb8f-4880-818a-a6a54886888f", "price": 38.0}, "M": {"id": "7f9d8f1f-3366-413a-be35-57c681f5250e", "price": 38.0}, "L": {"id": "1d38b106-f77e-408d-a18d-21367a927db4", "price": 38.0}, "XL": {"id": "dbe600b3-7903-4cd7-b12b-f2dd383bd669", "price": 38.0}, "2XL": {"id": "d666bfd0-b5b0-4fe5-9baa-fb6c3668a16b", "price": 38.0}, "3XL": {"id": "2e6aa59e-fa2f-4ea0-bae8-4eb233ce8ea8", "price": 38.0}}}, "APC-C113": {"slug": "anaheim-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/anaheim-hyrx", "price": 44.0, "variants": {"S": {"id": "495168d1-1b2e-4ad1-9fe1-fd94cabd3421", "price": 38.0}, "M": {"id": "729bdcaa-fc47-465f-bba2-af201ce17bef", "price": 38.0}, "L": {"id": "94be63d9-7b6e-4048-bf4c-cb3d0151e1ef", "price": 38.0}, "XL": {"id": "60dffd89-0b3a-46a7-a394-2bc52a5a8352", "price": 38.0}, "2XL": {"id": "aa4ed78b-56c3-4286-92f7-f6bc20a70ca9", "price": 40.0}, "3XL": {"id": "7eab3ccf-9149-4f90-a646-c584033fae20", "price": 42.0}, "4XL": {"id": "6e4c8135-b30b-4aa6-a6e1-6c9bc91471e1", "price": 44.0}}}, "APC-C114": {"slug": "atlanta-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/atlanta-hyrx", "price": 44.0, "variants": {"S": {"id": "197f0cec-8dd5-4410-85b5-097826d20cce", "price": 38.0}, "M": {"id": "49edfc5b-6ebd-4b52-98df-23d8f793c19e", "price": 38.0}, "L": {"id": "6c49bf9b-74b9-4532-89cc-ca1392bc5955", "price": 38.0}, "XL": {"id": "aea1f98d-ae86-417e-8bc2-bfd7c00a0472", "price": 38.0}, "2XL": {"id": "99ec3352-607d-4fbc-9767-c8b82f7238f9", "price": 40.0}, "3XL": {"id": "590f991f-53c5-492b-a0c8-e53592635d82", "price": 42.0}, "4XL": {"id": "6566b7f6-d1a4-4d8c-a186-593cb3a8d402", "price": 44.0}}}, "APC-C115": {"slug": "cancun-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/cancun-hyrx", "price": 44.0, "variants": {"S": {"id": "25f6de17-45e2-477c-95ea-7d4d09bb66ea", "price": 38.0}, "M": {"id": "068c8a7b-fb58-48d2-8fdf-fa1075b84e4f", "price": 38.0}, "L": {"id": "62e12953-303d-418a-8946-8699825a6ad3", "price": 38.0}, "XL": {"id": "a2c637cd-394c-46ad-9eae-b259c11990cf", "price": 38.0}, "2XL": {"id": "d74a72d4-7d9c-419d-a20f-4ef573ef21dd", "price": 40.0}, "3XL": {"id": "bfde988e-6508-40f3-832b-d1f0af18e2ef", "price": 42.0}, "4XL": {"id": "b475877c-1395-4000-95e5-8ecd57881b00", "price": 44.0}}}, "APC-C116": {"slug": "chicago-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/chicago-hyrx", "price": 44.0, "variants": {"S": {"id": "160a93c7-821d-44e7-8722-961f451437e2", "price": 38.0}, "M": {"id": "02484852-5301-4694-9072-5f5bb01152c1", "price": 38.0}, "L": {"id": "bf719666-82d6-4a1f-b0fd-c995eb4b4a8e", "price": 38.0}, "XL": {"id": "a0dcf0e6-c55d-4dc8-8838-8e0903c6f4b0", "price": 38.0}, "2XL": {"id": "13f8ba0d-ca01-42ca-b05b-394b430db15e", "price": 40.0}, "3XL": {"id": "6156bb0c-ec66-4ef0-bdbd-53d8a42b1276", "price": 42.0}, "4XL": {"id": "377d3dd4-af3a-45c1-b317-29fc5ddb6cc6", "price": 44.0}}}, "APC-C117": {"slug": "guadalajara-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/guadalajara-hyrx", "price": 44.0, "variants": {"S": {"id": "8b8fc499-9bba-4823-86de-1af91df583b1", "price": 38.0}, "M": {"id": "5cf1c1c1-28dd-4c4c-b485-884838df4671", "price": 38.0}, "L": {"id": "6c87ea3f-5589-4052-9606-0044c3d942a7", "price": 38.0}, "XL": {"id": "8f11efea-73e4-4483-b4c5-e70e8f56d2f5", "price": 38.0}, "2XL": {"id": "5efe4feb-e598-4698-bd61-1f770d1603b7", "price": 40.0}, "3XL": {"id": "3c7790f8-9e65-444d-973a-bd276ece88cb", "price": 42.0}, "4XL": {"id": "171bf912-f4b4-4075-9e64-691a8e35c26d", "price": 44.0}}}, "APC-C118": {"slug": "hong-kong-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hong-kong-hyrx", "price": 44.0, "variants": {"S": {"id": "c9d4e62d-a5bb-4533-a38b-d5d70de7247d", "price": 38.0}, "M": {"id": "a7bc9a9b-fb7e-44ea-9186-ad1cf958c54e", "price": 38.0}, "L": {"id": "7b9eb646-05b0-4baf-a794-fd4b30901aa1", "price": 38.0}, "XL": {"id": "5b9814c5-f2b4-4394-a3f8-889ebec7a72e", "price": 38.0}, "2XL": {"id": "111955bb-5ab7-40bd-99bf-67dad5706582", "price": 40.0}, "3XL": {"id": "0c28a3ae-a7d0-483c-bee9-2c17fe31c55c", "price": 42.0}, "4XL": {"id": "dd08ded1-cc3b-415c-b73e-c1a0bd352327", "price": 44.0}}}, "APC-C119": {"slug": "houston-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/houston-hyrx", "price": 44.0, "variants": {"S": {"id": "77ee1d4b-9daf-4fc4-8fd8-02e621935a87", "price": 38.0}, "M": {"id": "39a911e1-da71-4386-8364-c38aa9862ce0", "price": 38.0}, "L": {"id": "a5fb03e6-62fd-4692-a652-79e1530cddf1", "price": 38.0}, "XL": {"id": "e94fb79e-85c8-4a73-8978-5aefdde23a62", "price": 38.0}, "2XL": {"id": "5bcbb649-2225-4711-b1da-2c0a8b673d49", "price": 40.0}, "3XL": {"id": "0cadda57-fe3d-4179-bbe0-317f9f046980", "price": 42.0}, "4XL": {"id": "0618650a-ac01-48c9-8f50-aaa2be692e70", "price": 44.0}}}, "APC-C120": {"slug": "las-vegas-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/las-vegas-hyrx", "price": 44.0, "variants": {"S": {"id": "4d7057f7-1ffd-435d-a7c9-5c878f4c7d20", "price": 38.0}, "M": {"id": "202a4aac-3e49-45f7-9bc5-10fcd2286649", "price": 38.0}, "L": {"id": "03d8d2a1-854a-4928-8293-a6e55b5578b3", "price": 38.0}, "XL": {"id": "6c4097d3-08ce-4640-aa8b-74a0b4e9ac8c", "price": 38.0}, "2XL": {"id": "20de03d9-1de7-4f91-aeda-95852c0e74b7", "price": 40.0}, "3XL": {"id": "1b0f60bd-e975-482c-9a99-0d7aad7ee67b", "price": 42.0}, "4XL": {"id": "83d26de3-cf5f-4e3c-9d63-ed42f6b49b59", "price": 44.0}}}, "APC-C121": {"slug": "london-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/london-hyrx", "price": 44.0, "variants": {"S": {"id": "f32b2834-e649-4502-9472-a5c871280948", "price": 38.0}, "M": {"id": "ba5abc13-c7c5-44da-b624-9637e191a790", "price": 38.0}, "L": {"id": "0ca31613-d37f-4a24-a488-e66f68a2bb0d", "price": 38.0}, "XL": {"id": "57a0a713-89ce-475c-9b51-4c7a4c15fd03", "price": 38.0}, "2XL": {"id": "d021e7ca-1ff2-4dce-89d4-e4310523e757", "price": 40.0}, "3XL": {"id": "a3118f67-8a4d-4588-8f4e-387872aa862c", "price": 42.0}, "4XL": {"id": "9ff32157-96bb-441b-a716-6c576d205ea5", "price": 44.0}}}, "APC-C122": {"slug": "hyrx-station-crew", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-station-crew", "price": 66.0, "variants": {"XS": {"id": "573cbf4f-7970-4d71-a97b-27d5f66a9d70", "price": 63.0}, "S": {"id": "9bd03e9b-5aa6-4340-b9ac-bd8d2e8b23df", "price": 63.0}, "M": {"id": "27b508de-636d-487c-b950-19834a4f2fe5", "price": 63.0}, "L": {"id": "44538ed3-29de-492b-8df4-bc4ce380148f", "price": 63.0}, "XL": {"id": "2548684e-43fd-4695-9cb3-8c3f2be511ea", "price": 63.0}, "2XL": {"id": "c4e40d42-d16a-44dc-a82a-bfbaa98b3d90", "price": 66.0}, "3XL": {"id": "98a2be8b-2894-40c9-8723-c556749df853", "price": 66.0}}}, "APC-C123": {"slug": "hyrx-quarter-zip", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-quarter-zip", "price": 50.0, "variants": {"S": {"id": "286be15b-5671-4b72-bec2-874923e13039", "price": 46.0}, "M": {"id": "cefb2f66-f270-4fd7-abca-36373f1b1b71", "price": 46.0}, "L": {"id": "d2d33746-3dae-457a-b096-215647f7cdb3", "price": 46.0}, "XL": {"id": "7f248618-80ac-40a3-a355-5cff9a3eba76", "price": 46.0}, "2XL": {"id": "b5949df3-f276-4a9a-b589-082d4d34520e", "price": 48.0}, "3XL": {"id": "17e12e0e-1f82-4bf9-9113-2a41bdcae1a2", "price": 50.0}}}, "APC-C124": {"slug": "hyrx-trucker", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-trucker", "price": 32.0, "variants": {"One size": {"id": "1d28304a-2bc7-49f3-b616-93c277d85e42", "price": 32.0}}}, "APC-C125": {"slug": "hyrx-trucker-graphic", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-trucker-graphic", "price": 34.0, "variants": {"One size": {"id": "a5b0fbb0-99a2-4b7b-86d6-f7dd30a7ff7e", "price": 34.0}}}, "APC-C126": {"slug": "hyrx-run-5-panel-black", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-run-5-panel-black", "price": 33.0, "variants": {"One size": {"id": "a2f9a4ac-2909-4060-bee4-2454bef1871b", "price": 33.0}}}, "APC-C127": {"slug": "hyrx-run-5-panel-light-blue-white", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-run-5-panel-light-blue-white", "price": 33.0, "variants": {"One size": {"id": "cd6b4b7a-1db4-4f29-853b-52b672f0815a", "price": 33.0}}}, "APC-C128": {"slug": "hyrx-surf-5-panel", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-surf-5-panel", "price": 38.0, "variants": {"One size": {"id": "cf28ea3b-45d7-4b31-aed1-475c8de2b711", "price": 38.0}}}, "APC-C129": {"slug": "hyrx-low-cap", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-low-cap", "price": 32.0, "variants": {"One size": {"id": "8ce81334-5548-4a54-b9cf-7049edc09550", "price": 32.0}}}, "APC-C130": {"slug": "hyrx-dad-cap", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-dad-cap", "price": 33.0, "variants": {"One size": {"id": "5a3c5e6e-b758-42fe-8e80-4a092f0d9dd2", "price": 33.0}}}, "APC-C131": {"slug": "hyrx-mid-cap", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-mid-cap", "price": 30.0, "variants": {"One size": {"id": "5751df52-b459-4495-9f14-854c93eaec05", "price": 30.0}}}, "APC-C132": {"slug": "hyrx-cuff-beanie-black", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-cuff-beanie-black", "price": 31.0, "variants": {"One size": {"id": "96abeaf1-dea7-4228-8a11-9ee510ab03c3", "price": 31.0}}}, "APC-C133": {"slug": "hyrx-cuff-beanie-heather-grey", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-cuff-beanie-heather-grey", "price": 31.0, "variants": {"One size": {"id": "5f38351d-8d46-432d-8cb6-77933cec4386", "price": 31.0}}}, "APC-C134": {"slug": "hyrx-rib-beanie-black", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-rib-beanie-black", "price": 33.0, "variants": {"One size": {"id": "8d79b8c4-f089-47c7-a3b7-e36d7d3cd03f", "price": 33.0}}}, "APC-C135": {"slug": "hyrx-rib-beanie-light-blue", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-rib-beanie-light-blue", "price": 33.0, "variants": {"One size": {"id": "54679c39-a3f5-4a33-b6c7-5914f3663273", "price": 33.0}}}, "APC-C136": {"slug": "hyrx-gym-sack-black", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-gym-sack-black", "price": 32.0, "variants": {"15\" x 17\"": {"id": "88e59350-b9e5-45ec-b1a2-35f5ddf032d5", "price": 32.0}}}, "APC-C137": {"slug": "hyrx-gym-sack-burgundy", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-gym-sack-burgundy", "price": 32.0, "variants": {"15\" x 17\"": {"id": "5aed23cc-dc15-4d00-bf95-f12169e205a1", "price": 32.0}}}, "APC-C138": {"slug": "hyrx-station-towel-black", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-station-towel-black", "price": 53.07, "variants": {"30\" x 60\"": {"id": "3669ffea-c900-49da-be70-1a1a1a150aa8", "price": 50.0}, "36\" x 72\"": {"id": "5ec97ff9-92f9-4e83-adca-8e3e130d2137", "price": 53.07}}}, "APC-C139": {"slug": "hyrx-station-towel-deep-olive", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-station-towel-deep-olive", "price": 53.07, "variants": {"30\" x 60\"": {"id": "b076de69-8d86-4141-aa16-b2a53655a67b", "price": 50.0}, "36\" x 72\"": {"id": "488ab94b-5511-463e-8aeb-6d54606f06ac", "price": 53.07}}}, "APC-C140": {"slug": "hyrx-pool-slide-black", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-pool-slide-black", "price": 55.0, "variants": {"6.5": {"id": "3870797f-e731-4ff5-8b51-4cb669563c31", "price": 55.0}, "7": {"id": "61b4954f-4144-430e-909f-aa5374806f4f", "price": 55.0}, "8": {"id": "e3c41930-5fa4-4454-a930-f113973853cb", "price": 55.0}, "8.5": {"id": "567a2584-26fc-4958-940a-d48bb891e492", "price": 55.0}, "9.5": {"id": "0e88edb8-93f9-4065-9f77-996d498acd09", "price": 55.0}, "10": {"id": "8dd58a29-e02e-4c7a-8e35-3fac56723386", "price": 55.0}, "11": {"id": "160b69b6-3d00-4c7f-9990-f1090d92ea07", "price": 55.0}, "11.5": {"id": "8fda91d3-246b-45ff-a175-4fdca4d63f6f", "price": 55.0}, "12.5": {"id": "83480ac2-6fe0-4c85-839e-9267ff6fba3d", "price": 55.0}}}, "APC-C141": {"slug": "hyrx-pool-slide-burgundy", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/hyrx-pool-slide-burgundy", "price": 55.0, "variants": {"6.5": {"id": "51a086ec-0b35-4fca-9f74-613c6c6e441d", "price": 55.0}, "7": {"id": "16ea8c37-f17d-4980-8ee0-e735ba61cc98", "price": 55.0}, "8": {"id": "df8cbe93-13cc-425c-8ac9-13056651535b", "price": 55.0}, "8.5": {"id": "5111eefa-1737-4fb1-93a2-8e6d46446aae", "price": 55.0}, "9.5": {"id": "b1bd52dd-6d6e-4be5-87fc-647449e3e7bc", "price": 55.0}, "10": {"id": "59b87df6-aaaa-48be-9aef-c49436e1e05e", "price": 55.0}, "11": {"id": "1baba3fc-ba15-44be-848d-12c96b7772c1", "price": 55.0}, "11.5": {"id": "e5e05718-4dca-43a7-9fc9-b4a6e15668cc", "price": 55.0}, "12.5": {"id": "ca52594c-017e-436f-ae2f-a44412fb903f", "price": 55.0}}}, "APC-C142": {"slug": "miami-beach-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/miami-beach-hyrx", "price": 44.0, "variants": {"S": {"id": "37c037bc-5888-4ef4-8843-9e8452a7dcc7", "price": 38.0}, "M": {"id": "e3e451e9-0879-4030-877e-4a78dfa21fe0", "price": 38.0}, "L": {"id": "d4639726-a1e0-41ed-8e9d-f26d4b705534", "price": 38.0}, "XL": {"id": "bc28e33d-8baf-4630-a565-74397a6ad5c5", "price": 38.0}, "2XL": {"id": "30a34022-bd65-4f3b-9ff1-15279ded2a29", "price": 40.0}, "3XL": {"id": "582c4574-5c1f-4c9e-99af-5cf429b14c52", "price": 42.0}, "4XL": {"id": "49819e45-2893-48d6-96f6-e8323317f8cd", "price": 44.0}}}, "APC-C143": {"slug": "minneapolis-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/minneapolis-hyrx", "price": 44.0, "variants": {"S": {"id": "95e30a39-1a93-4b8e-82b5-87c5d1ed151a", "price": 38.0}, "M": {"id": "17defa10-ac20-40c3-9f17-5f6ed1e64366", "price": 38.0}, "L": {"id": "faabe115-29ff-4641-acc1-4e8f0db5eba2", "price": 38.0}, "XL": {"id": "906f3ea9-6289-42cc-862d-cd18289fcfb2", "price": 38.0}, "2XL": {"id": "31a501f7-1696-44ec-8b41-ad5a5d866bb0", "price": 40.0}, "3XL": {"id": "f286ebfc-d860-4252-9391-413542ada968", "price": 42.0}, "4XL": {"id": "902c2fd9-40f3-4e97-a706-666b27290294", "price": 44.0}}}, "APC-C144": {"slug": "monterrey-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/monterrey-hyrx", "price": 44.0, "variants": {"S": {"id": "2cc2971f-fb04-4b6c-9215-593e8796e92c", "price": 38.0}, "M": {"id": "f1f5495c-be23-44bb-8067-b7de5edf79de", "price": 38.0}, "L": {"id": "89658a76-58d8-467d-b58e-a7bda3e97827", "price": 38.0}, "XL": {"id": "e69ee729-4aa6-4ae9-9259-904d40944fcd", "price": 38.0}, "2XL": {"id": "342445d4-94d7-46e4-af81-23aeb991db52", "price": 40.0}, "3XL": {"id": "781d14c3-3259-4d48-9d98-4c4717c9943d", "price": 42.0}, "4XL": {"id": "6b699906-7dc1-4121-a78b-0287d1471925", "price": 44.0}}}, "APC-C145": {"slug": "nashville-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/nashville-hyrx", "price": 44.0, "variants": {"S": {"id": "5e91dbbc-9553-4f2e-bad3-4b2deb9ab2a7", "price": 38.0}, "M": {"id": "c0f1cca2-f031-42b9-9c49-5f878b459c8b", "price": 38.0}, "L": {"id": "c9681fbb-d6ca-4446-87de-b06b03ee1a72", "price": 38.0}, "XL": {"id": "521bfa11-df51-4b43-bd2e-48686b9ed4bd", "price": 38.0}, "2XL": {"id": "05e12917-d1fb-4933-8965-f745eb09f8ee", "price": 40.0}, "3XL": {"id": "8709022c-c1f4-4369-8aad-93f56dab7dd3", "price": 42.0}, "4XL": {"id": "7f95ebc6-c6f1-4dd8-9a0c-d37bc28332ca", "price": 44.0}}}, "APC-C146": {"slug": "paris-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/paris-hyrx", "price": 44.0, "variants": {"S": {"id": "5e63ef1f-85b7-4c1a-98b0-b2ac61857dbd", "price": 38.0}, "M": {"id": "66ccf191-4954-40e2-91d1-ac13df058672", "price": 38.0}, "L": {"id": "fd42ab74-2371-4dbf-b61b-22bc44fc4604", "price": 38.0}, "XL": {"id": "9ffa6c83-9115-4b9e-9026-3400248b3f0f", "price": 38.0}, "2XL": {"id": "2cec6898-4ae2-4bd4-af72-61aee99e8c11", "price": 40.0}, "3XL": {"id": "5fd1426f-441b-4bb9-bc4b-d169db727057", "price": 42.0}, "4XL": {"id": "6fe481c9-ce49-4141-bad0-717f4c0ee34c", "price": 44.0}}}, "APC-C147": {"slug": "phoenix-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/phoenix-hyrx", "price": 44.0, "variants": {"S": {"id": "923eed62-65b0-491c-b35b-f15ca75ae2b2", "price": 38.0}, "M": {"id": "d5d45984-6ae5-4d43-8c9d-abfe744cb08e", "price": 38.0}, "L": {"id": "d82b5f47-69cb-4451-8b51-b9c9607512b9", "price": 38.0}, "XL": {"id": "a7dcd895-35c1-4d52-9287-cef67090f4f2", "price": 38.0}, "2XL": {"id": "191073c2-02a1-47f4-b92f-6f08f7cb5dfd", "price": 40.0}, "3XL": {"id": "4be765fe-1bcb-4556-907c-84f209bf6d76", "price": 42.0}, "4XL": {"id": "ceec88fc-22b3-47ca-bd30-77075f3a8fc6", "price": 44.0}}}, "APC-C148": {"slug": "portland-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/portland-hyrx", "price": 44.0, "variants": {"S": {"id": "6ed526d8-c22d-4b92-8713-0f71a417944c", "price": 38.0}, "M": {"id": "773a4ab8-0824-4cc4-ae3d-ca7cb623a275", "price": 38.0}, "L": {"id": "e52aeed1-12a4-4653-b2ec-2f32f5ded050", "price": 38.0}, "XL": {"id": "0ffea886-c22a-46d5-a038-3630d4b315e7", "price": 38.0}, "2XL": {"id": "c5f3e951-4804-40c2-87c1-7beca0430b85", "price": 40.0}, "3XL": {"id": "57404756-6dbb-4650-9afd-375d05dfe696", "price": 42.0}, "4XL": {"id": "b825d76e-2799-4071-a96b-ffb398cd7360", "price": 44.0}}}, "APC-C149": {"slug": "san-diego-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/san-diego-hyrx", "price": 44.0, "variants": {"S": {"id": "16d31d9f-926e-4874-a1ba-c47117c398b3", "price": 38.0}, "M": {"id": "345fc354-4862-4072-8791-0153c6fb429d", "price": 38.0}, "L": {"id": "9a4fc021-407c-463a-909c-bd0ce558150b", "price": 38.0}, "XL": {"id": "825c1dbe-9a76-4c49-bcfd-ba1def3ff683", "price": 38.0}, "2XL": {"id": "208f33b9-918c-4925-b9ae-93458110a24d", "price": 40.0}, "3XL": {"id": "bd1fcfba-46ab-42a6-af30-381e1f1d8996", "price": 42.0}, "4XL": {"id": "de68d378-0471-4b0e-ae60-c6c21e08d702", "price": 44.0}}}, "APC-C150": {"slug": "vancouver-hyrx", "url": "https://apex-hybrid-co-shop.fourthwall.com/products/vancouver-hyrx", "price": 44.0, "variants": {"S": {"id": "ef38d326-0c69-455e-84a1-6226956fd94d", "price": 38.0}, "M": {"id": "fa1c7d32-ab64-465d-b798-dd947c571cb7", "price": 38.0}, "L": {"id": "7897f7ba-80e4-46d7-b474-1fc32cc6eeba", "price": 38.0}, "XL": {"id": "9b5c1342-b1b0-413e-9282-092ff3d59d82", "price": 38.0}, "2XL": {"id": "4350e132-3aee-43f6-86ee-83de70e773f5", "price": 40.0}, "3XL": {"id": "82fbfff5-b321-4879-8bbb-3a437a8a25e6", "price": 42.0}, "4XL": {"id": "f58221ab-8318-4413-8500-ca6751359db8", "price": 44.0}}}};

let fwCheckoutBusy = false;

function fetchWithTimeout(url, options, ms) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), ms);
  return fetch(url, Object.assign({}, options, { signal: ctrl.signal })).finally(() => clearTimeout(timer));
}

function leaveForFourthwall(url) {
  if (!url) return;
  window.location.href = (window.apexUtmUrl || String)(fourthwallUrlWithPromo(url));
}

async function checkoutViaFourthwallApi(items, fallbackUrl) {
  if (fwCheckoutBusy) return;
  fwCheckoutBusy = true;
  let left = false;
  const go = (url) => {
    if (left) return;
    left = true;
    fwCheckoutBusy = false;
    clearTimeout(watchdog);
    leaveForFourthwall(url);
  };
  const watchdog = setTimeout(() => go(fallbackUrl), 5000);
  try {
    try { toast("Opening secure checkout…"); } catch (_) {}
    const cartItems = [];
    const variants = (typeof FW_VARIANTS === "undefined") ? null : FW_VARIANTS;
    for (const item of items || []) {
      const entry = variants && variants[item.id];
      if (entry && entry.variants) {
        const sz = item.size || sizeChoice[item.id] || "L";
        const v = entry.variants[sz] || entry.variants.L || Object.values(entry.variants)[0];
        if (v && v.id) {
          cartItems.push({ id: v.id, quantity: Math.max(1, Number(item.qty) || 1) });
        }
      }
    }
    if (!cartItems.length) throw new Error("no_variant");
    const addRes = await fetchWithTimeout("https://apex-hybrid-co-shop.fourthwall.com/cart/add.js", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: cartItems }),
    }, 4000);
    if (!addRes.ok) throw new Error("cart_add_failed");
    const addData = await addRes.json();
    const cartId = addData && addData.cart && addData.cart.id;
    if (!cartId) throw new Error("no_cart_id");
    const chkRes = await fetchWithTimeout("https://apex-hybrid-co-shop.fourthwall.com/api/v2/checkout/cart", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cartId, cartCurrency: "USD" }),
    }, 4000);
    if (!chkRes.ok) throw new Error("checkout_create_failed");
    const chkData = await chkRes.json();
    if (chkData && chkData.id) {
      const promoInfo = resolvePromo(activePromo);
      if (promoInfo) {
        if (promoInfo.code === "DALLAS10") {
          await fetchWithTimeout(`https://apex-hybrid-co-shop.fourthwall.com/api/v2/checkout/${encodeURIComponent(chkData.id)}/code`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code: "DALLAS10" }),
          }, 4000).catch(() => {});
        }
      }
      const checkoutUrl = `https://apex-hybrid-co-shop.fourthwall.com/checkout/${encodeURIComponent(chkData.id)}`;
      go(checkoutUrl);
      return;
    }
    throw new Error("no_checkout_id");
  } catch (_) {
    go(fallbackUrl);
  }
}

let activePromo = "";
try {
  activePromo = (sessionStorage.getItem("apx_promo_code") || "").trim().toUpperCase();
} catch (_) {}

function resolvePromo(code) {
  const c = String(code || "").trim().toUpperCase();
  if (!c) return null;
  if (PROMO_CODES[c]) return { code: c, pct: PROMO_CODES[c].pct, label: PROMO_CODES[c].label };
  return null;
}

function setPromoCode(rawCode, notify = true) {
  const info = resolvePromo(rawCode);
  if (!info) {
    if (rawCode && notify) toast(`Promo code "${String(rawCode).toUpperCase()}" is not valid`);
    return false;
  }
  activePromo = info.code;
  try {
    sessionStorage.setItem("apx_promo_code", activePromo);
  } catch (_) {}
  trackHit(`promo_${activePromo}`);
  if (notify) toast(`Promo ${activePromo} (${info.pct}% off) applied!`);
  renderCart();
  return true;
}

window.apexSetPromo = (c) => setPromoCode(c, true);

function clearPromoCode() {
  activePromo = "";
  try {
    sessionStorage.removeItem("apx_promo_code");
  } catch (_) {}
  renderCart();
}

function fourthwallUrlWithPromo(url) {
  if (!url) return url;
  const info = resolvePromo(activePromo);
  if (!info) return url;
  const sep = url.includes("?") ? "&" : "?";
  return `${url}${sep}discount=${encodeURIComponent(info.code)}&promo=${encodeURIComponent(info.code)}`;
}

let PRODUCTS = [];
let GUIDES = [];
let dept = "apparel";
let sort = "featured";
let query = "";
let cart = [];
let express = null;
const sizeChoice = {};
const colorChoice = {};
const blankChoice = {};

function hasBlankChoice() {
  return false;
}
function blankOf(p) {
  if (!p) return "heavy";
  if (blankChoice[p.id]) return blankChoice[p.id];
  return p.dept === "Breathable Tech Shirts" ? "light" : "heavy";
}
function blankLabel(p) {
  if (!hasBlankChoice(p)) return "";
  return blankOf(p) === "light"
    ? " Breathable Workout Tee"
    : "Heavyweight cotton tee";
}
let labTab = "calculator";
let activeArticle = null;
let toastTimer = 0;

const $ = (sel) => document.querySelector(sel);
const money = (n) => Number(n).toLocaleString("en-US", { style: "currency", currency: "USD" });
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function sizeOf(p) {
  if (sizeChoice[p.id]) return sizeChoice[p.id];
  if (!p || !p.has_sizes) return "";
  const sizes = sizesFor(p);
  if (sizes.includes("L")) return "L";
  if (sizes.includes("10")) return "10";
  return sizes[0] || "";
}

const SIZE_RANK = ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"];

function isRaceDayJacket(p) {
  return Boolean(p && /^APC-C4[6-9]$|^APC-C50$/.test(p.id));
}

function sizesFor(p) {
  if (!p || !p.has_sizes) return [];
  const fw = FW_VARIANTS[p.id] && FW_VARIANTS[p.id].variants;
  const known = fw ? Object.keys(fw) : (isRaceDayJacket(p) ? Object.keys(p.fourthwall_variants || {}) : []);
  if (known.length) {
    const ordered = SIZE_RANK.filter((sz) => known.includes(sz));
    const extra = known.filter((sz) => !ordered.includes(sz));
    return ordered.concat(extra);
  }
  return ["S", "M", "L", "XL", "2XL"];
}

function selectedPrice(p) {
  const sz = sizeOf(p);
  const fw = FW_VARIANTS[p.id] && FW_VARIANTS[p.id].variants && FW_VARIANTS[p.id].variants[sz];
  if (fw && fw.price != null) return Number(fw.price);
  const variant = p && p.fourthwall_variants && p.fourthwall_variants[sz];
  if (variant && variant.price != null) return Number(variant.price);
  return Number(p.retail_price);
}
function colorOf(p) {
  return colorChoice[p.id] || "black";
}
function photoOf(p) {
  // Black-only storefront: never swap to a white colorway.
  return p.image;
}
function findProduct(sku) {
  return PRODUCTS.find((p) => p.id === sku);
}
function colorLabel(p) {
  if (p && p.color) return p.color;
  return p.image ? "Black" : "";
}
function hoverPhotoOf(p) {
  // Prefer a distinct black back/alt; never a white colorway.
  const alt = p.alt_image || "";
  if (!alt) return "";
  if (/-white/i.test(alt) || /white\.png/i.test(alt)) return "";
  if (alt.split("?")[0] === (p.image || "").split("?")[0]) return "";
  return alt;
}

function matchesDept(p) {
  if (dept === "New") return p.badge === "New";
  if (dept === "apparel") return APPAREL.has(p.dept);
  if (dept === "all") return true;
  const wanted = (dept === "Lightweight Jackets" || dept === "Race Day Windbreakers") ? "Windbreakers" : dept;
  return p.dept === wanted;
}

function visibleProducts() {
  const q = query.trim().toLowerCase();
  let list = PRODUCTS.filter((p) => {
    if (!q && !matchesDept(p)) return false;
    if (q) {
      const hay = `${p.title} ${p.seo_title || ""} ${p.short_desc || ""} ${p.dept} ${p.category}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
  if (sort === "price-asc") list.sort((a, b) => a.retail_price - b.retail_price);
  else if (sort === "price-desc") list.sort((a, b) => b.retail_price - a.retail_price);
  else if (sort === "rating") list.sort((a, b) => b.rating - a.rating || b.reviews - a.reviews);
  else if (!q) list = mixShelf(list);
  return list;
}

const HYRX_HANDLES = new Set(["call-room","circuit-cities","course-plate","eight-marks","field-issue","hold-the-pace","hyrx-finish","outline-mark","peak-sign","sleeve-seal","stem-type","timing-gate","work-the-loop","hyrx-station-crew","hyrx-quarter-zip","hyrx-trucker","hyrx-trucker-graphic","hyrx-run-5-panel-black","hyrx-run-5-panel-light-blue-white","hyrx-surf-5-panel","hyrx-low-cap","hyrx-dad-cap","hyrx-mid-cap","hyrx-cuff-beanie-black","hyrx-cuff-beanie-heather-grey","hyrx-rib-beanie-black","hyrx-rib-beanie-light-blue","hyrx-gym-sack-black","hyrx-gym-sack-burgundy","hyrx-station-towel-black","hyrx-station-towel-deep-olive","hyrx-pool-slide-black","hyrx-pool-slide-burgundy","miami-beach-hyrx","minneapolis-hyrx","monterrey-hyrx","nashville-hyrx","paris-hyrx","phoenix-hyrx","portland-hyrx","san-diego-hyrx","vancouver-hyrx"]);
const RACE_DAY_JACKETS = new Set(["APC-C46","APC-C47","APC-C48","APC-C49","APC-C50","APC-C75"]);

function isOuterwear(p) {
  return p.dept === "Windbreakers";
}

function shelfKind(p) {
  if (isOuterwear(p)) return "outer";
  if (HYRX_HANDLES.has(p.handle)) return "hyrx";
  if (p.dept === "Women's") return "women";
  if (p.dept === "Muscle Tanks") return "tank";
  if (p.dept === "Hoodies") return "hoodie";
  if (p.dept === "Training Gear") return "gear";
  return "tee";
}

function mixShelf(list) {
  const buckets = { tee: [], tank: [], hyrx: [], women: [], hoodie: [], gear: [], outer: [] };
  list.forEach((p) => buckets[shelfKind(p)].push(p));
  const order = ["tee", "tank", "hyrx", "women", "hoodie", "gear"];
  const rest = [];
  let added = true;
  while (added) {
    added = false;
    order.forEach((key) => {
      if (buckets[key].length) {
        rest.push(buckets[key].shift());
        added = true;
      }
    });
  }
  const outer = buckets.outer;
  if (!outer.length || !rest.length) return list;
  const out = [];
  let ri = 0;
  let oi = 0;
  while (oi < outer.length || ri < rest.length) {
    for (let n = 0; n < 2 && ri < rest.length; n++) out.push(rest[ri++]);
    if (oi < outer.length && ri < rest.length) out.push(outer[oi++]);
    else if (oi < outer.length && ri >= rest.length) break;
  }
  while (ri < rest.length) out.push(rest[ri++]);
  while (oi < outer.length) out.push(outer[oi++]);
  return out;
}

function collectionName() {
  if (query.trim()) return "Search";
  const hit = PILLS.find(([id]) => id === dept);
  return hit ? hit[1] : "Apparel";
}

function renderPills() {
  $("#deptPills").innerHTML = PILLS.map(([id, label]) => `
    <button class="Pill" type="button" data-dept="${esc(id)}" aria-pressed="${dept === id && !query ? "true" : "false"}">${esc(label)}</button>
  `).join("");
}

const SHORT = {
  "APC-C36": "Built For Heavy Legs",
  "APC-C37": "1KM Split",
  "APC-C38": "Aerobic Engine",
  "APC-C40": "Push Heavy Run Fast",
  "APC-C41": "Roxzone Speed Dept.",
  "APC-C16": "Apex Race City Heavyweight - Chicago Championship Division",
  "APC-C17": "Apex Race City Heavyweight - Dallas Turf & Threshold",
  "APC-C18": "Apex Race City Heavyweight - Anaheim SoCal Open Division",
  "APC-C19": "Apex Race City Heavyweight - Miami Beach Endurance Club",
  "APC-C20": "Apex Race City Heavyweight - Las Vegas Championship Qualifier",
  "APC-C21": "Apex Race City Heavyweight - New York Hudson Pier Division",
  "APC-C28": "Run Station Repeat Loop",
  "APC-C29": "Sled Push Department",
  "APC-C30": "Heavy Legs Run Club 1000M",
  "APC-C31": "100 Wall Balls Unbroken",
  "APC-C22": "Zero Excuses",
  "APC-C23": "Roxzone Penalties",
  "APC-C24": "Farmer Carry Survivors Club",
  "APC-C25": "Sandbag Lunges",
  "APC-C26": "Redline Weekend",
  "APC-C27": "Sub-65 Club",
  "APC-C01": "Apex Heavyweight Hybrid - Run. Station. Repeat.",
  "APC-C02": "Apex Heavyweight Hybrid - Wall Balls & Bad Decisions",
  "APC-C03": "Apex Heavyweight Hybrid - Sled Push Enthusiast",
  "APC-C05": "Apex Heavyweight Hybrid - Burpee Broad Jumps",
  "APC-C06": "Apex Heavyweight Hybrid - The Erg Doesn't Care How You Feel",
  "APC-C07": "Porta-Potty Line PR",
  "APC-C08": "Defend My Sled Push",
  "APC-C34": "World Series Prep",
  "APC-C35": "8-Station Division",
  "APC-C32": "Build Character",
  "APC-C33": "Erg Doesn't Care",
  "APC-C09": "Run Station Repeat",
  "APC-C10": "Wall Balls & Bad Decisions",
  "APC-C11": "Heavy Legs Run Club KM",
  "APC-C12": "The Footage Speaks",
  "APC-C42": "Apex Lightweight Race Warmup - Hybrid Division",
  "APC-C43": "Hybrid 8-Station",
  "APC-C44": "Pro Division",
  "APC-C45": "World Series Warmup",
  "APC-C46": "Dallas Race Day",
  "APC-C47": "Denver Race Day",
  "APC-C48": "Anaheim Race Day",
  "APC-C49": "Nashville Race Day",
  "APC-C50": "Vancouver Race Day",
  "APC-C51": "Dallas Race Day Windbreaker",
  "APC-C52": "Denver Race Day Windbreaker",
  "APC-C53": "Anaheim Race Day Windbreaker",
  "APC-C54": "Nashville Race Day Windbreaker",
  "APC-C55": "Vancouver Race Day Windbreaker",
};

function shortTitle(p) {
  if (SHORT[p.id]) return SHORT[p.id];
  return p.title.split(" - ")[0].replace(/^["“]|["”]$/g, "").trim();
}

function ratingMarkup(p) {
  const score = Number(p.rating || 0);
  if (!score) return "";
  const full = Math.max(0, Math.min(5, Math.round(score)));
  const stars = `${"★".repeat(full)}${"☆".repeat(5 - full)}`;
  const reviews = p.reviews ? ` · ${p.reviews}` : "";
  return `<p class="Rating"><span class="Stars" aria-hidden="true">${stars}</span><span>${score.toFixed(1)}${reviews}</span></p>`;
}

function renderProducts() {
  const grid = $("#productGrid");
  const list = visibleProducts();
  $("#collectionTitle").textContent = collectionName();
  const count = $("#collectionCount");
  if (count) count.textContent = "";
  renderPills();
  if (!list.length) {
    grid.innerHTML = `<div class="Empty"><p>Nothing in this cut matches that search.</p><button class="Btn Btn--ghost" type="button" data-clear-search="1">Clear search</button></div>`;
    return;
  }
  grid.innerHTML = list.map((p) => {
    const swatches = ""; // black-only — no color toggle
    const hoverSrc = hoverPhotoOf(p);
    const hover = hoverSrc ? `<img class="Card__img Card__img--b" src="${esc(hoverSrc)}" alt="" loading="lazy" decoding="async" width="1000" height="1250" />` : "";
    const was = "";
    const badge = p.badge === "New" ? `<span style="position:absolute;top:8px;left:8px;z-index:2;background:#0066ff;color:#fff;font-size:10px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;padding:3px 7px;border-radius:999px">New</span>` : "";
    const sizes = p.has_sizes
      ? sizesFor(p).map((sz) => `<button type="button" data-quick-add="${p.id}" data-size="${sz}" aria-label="Add size ${sz}">${sz}</button>`).join("")
      : `<button type="button" data-quick-add="${p.id}">Add</button>`;
    return `
      <article class="Card">
        <div class="Card__media">
          ${badge}
          <button class="Card__hit" type="button" data-quick="${p.id}" aria-label="Quick view ${esc(p.title)}">
            <img class="Card__img" src="${esc(photoOf(p))}" alt="${esc(p.seo_title || p.title)}" loading="lazy" decoding="async" width="1000" height="1250" />
            ${hover}
          </button>
          <div class="QuickAdd" aria-label="Add ${esc(shortTitle(p))} to bag">${sizes}</div>
        </div>
        <div class="Card__body">
          <div class="Card__top">
            <h3><button type="button" data-quick="${p.id}">${esc(shortTitle(p))}</button></h3>
            ${RACE_DAY_JACKETS.has(p.id) ? `<p style="margin:2px 0 0;font-size:11px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:#0066ff">Race Day Jacket</p>` : ""}
            <div class="Price"><span>${money(p.retail_price)}</span>${was}</div>
          </div>
          ${ratingMarkup(p)}
          <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:8px">
            ${swatches}
            <button class="Btn Btn--cobalt" type="button" data-buy="${p.id}" style="margin-left:auto;padding:7px 12px;font-size:12.5px;border-radius:6px">Buy Now →</button>
          </div>
        </div>
      </article>`;
  }).join("");
}

function setDept(next) {
  dept = next;
  query = "";
  const input = $("#searchInput");
  if (input) input.value = "";
  renderProducts();
  const shop = $("#apparel");
  if (shop) shop.scrollIntoView({ behavior: "smooth", block: "start" });
}

function variantLabel(p) {
  return [colorLabel(p), blankLabel(p), p.has_sizes ? `Size ${sizeOf(p)}` : ""].filter(Boolean).join(" · ");
}

function isFourthwallItem(p) {
  return Boolean(p && (FW_VARIANTS[p.id] || p.fulfillment_partner === "Fourthwall" || String(p.id || "").startsWith("APC-C") || p.fourthwall_product_url));
}

function lineFrom(p, qty = 1) {
  const variant = variantLabel(p);
  const isFw = isFourthwallItem(p);
  return {
    key: `${p.id}__${variant}`,
    id: p.id,
    title: p.title,
    image: photoOf(p),
    price: selectedPrice(p),
    qty,
    size: sizeOf(p) || "L",
    blank: blankLabel(p),
    variant,
    is_fourthwall: isFw,
    fulfillment_partner: isFw ? "Fourthwall" : (p.fulfillment_partner || "US  Direct Wholesale"),
    fourthwall_blank: isFw ? (p.fourthwall_blank || "Athletic Blank") : "",
    fourthwall_handle: isFw ? (p.fourthwall_handle || p.handle || "") : "",
    fourthwall_product_url: isFw ? (p.fourthwall_product_url || p.checkout_url || "") : "",
    stripe_price_id: p.stripe_price_id || "",
    stripe_product_id: p.stripe_product_id || "",
    stripe_account_id: p.stripe_account_id || "",
  };
}

function addToCart(sku, openDrawer = true, track = true) {
  const p = findProduct(sku);
  if (!p) return;
  if (track) {
    trackHit("cart_add_total");
    trackHit(`cart_add_${p.id}`);
  }
  const line = lineFrom(p);
  const existing = cart.find((item) => item.key === line.key);
  if (existing) existing.qty += 1;
  else cart.push(line);
  renderCart();
  toast(`${shortTitle(p)} added${variantLabel(p) ? ` · ${variantLabel(p)}` : ""}`);
  if (openDrawer) openSheet("cartDrawer");
}

function changeQty(key, delta) {
  const item = cart.find((entry) => entry.key === key);
  if (!item) return;
  item.qty += delta;
  if (item.qty <= 0) cart = cart.filter((entry) => entry.key !== key);
  renderCart();
}

function renderCart() {
  const count = cart.reduce((sum, item) => sum + item.qty, 0);
  const sub = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
  $("#cartCount").textContent = String(count);
  const box = $("#cartItems");
  if (!cart.length) {
    box.innerHTML = `<p class="Empty">Your bag is empty. Grab a race tee or warmup layer to get started.</p>`;
  } else {
    box.innerHTML = cart.map((item) => `
      <div class="Line">
        <img src="${esc(item.image)}" alt="" />
        <div>
          <strong>${esc(item.title)}</strong>
          <div class="StripeId">${esc(item.variant)}</div>
          <div class="Qty">
            <button type="button" data-qty="-1" data-key="${esc(item.key)}" aria-label="Decrease quantity">−</button>
            <span>${item.qty}</span>
            <button type="button" data-qty="1" data-key="${esc(item.key)}" aria-label="Increase quantity">+</button>
            <strong style="margin-left:auto">${money(item.price * item.qty)}</strong>
          </div>
        </div>
      </div>
    `).join("");
  }
  const promoInfo = resolvePromo(activePromo);
  const discAmt = promoInfo ? sub * (promoInfo.pct / 100) : 0;
  const finalSub = Math.max(0, sub - discAmt);
  if (cart.length) {
    box.insertAdjacentHTML(
      "beforeend",
      `<div style="margin-top:12px;padding-top:12px;border-top:1px solid #e5e7eb">
        <div style="display:flex;gap:6px;align-items:center">
          <input id="cartPromoInput" type="text" value="${esc(activePromo)}" placeholder="Promo code" style="flex:1;padding:7px 10px;border:1px solid #d1d5db;border-radius:6px;font-size:12px;text-transform:uppercase" />
          <button type="button" class="Btn Btn--plain" data-apply-promo="cart" style="padding:7px 12px;font-size:12px">Apply</button>
        </div>
        ${promoInfo ? `<div style="display:flex;justify-content:space-between;font-size:12px;color:#059669;font-weight:700;margin-top:6px"><span>✓ ${esc(promoInfo.label)}</span><span>−${money(discAmt)}</span></div>` : ""}
      </div>`
    );
  }
  $("#cartSubtotal").textContent = promoInfo ? `${money(finalSub)} (${promoInfo.pct}% off)` : money(sub);
}

function openSheet(id) {
  document.querySelectorAll(".Sheet.is-open").forEach((el) => {
    if (el.id !== id) {
      el.classList.remove("is-open");
      el.setAttribute("aria-hidden", "true");
      el.setAttribute("inert", "");
    }
  });
  const sheet = document.getElementById(id);
  if (!sheet) return;
  sheet.classList.add("is-open");
  sheet.setAttribute("aria-hidden", "false");
  sheet.removeAttribute("inert");
  document.body.classList.add("is-locked");
  const close = sheet.querySelector(".IconBtn");
  if (close) close.focus();
}
function closeSheet(id) {
  const sheet = document.getElementById(id);
  if (!sheet) return;
  sheet.classList.remove("is-open");
  sheet.setAttribute("aria-hidden", "true");
  sheet.setAttribute("inert", "");
  if (![...document.querySelectorAll(".Sheet.is-open")].length) {
    document.body.classList.remove("is-locked");
  }
}
function closeAll() {
  document.querySelectorAll(".Sheet.is-open").forEach((sheet) => closeSheet(sheet.id));
}

function openProduct(sku) {
  const p = findProduct(sku);
  if (!p) return;
  trackHit("product_views_total");
  trackHit(`view_${p.id}`);
  const was = "";
  const swatches = `
    <div class="Swatches" style="position:static;margin:12px 0">
      <button class="Swatch Swatch--black" type="button" data-color="black" data-sku="${p.id}" aria-label="Black" aria-pressed="true" disabled></button>
      <span>Color: <strong>Black</strong></span>
    </div>`;
  const blankSelector = "";
  const shownPrice = selectedPrice(p);
  const sizes = p.has_sizes ? `<div class="Sizes" style="margin:12px 0">${sizesFor(p).map((sz) => `
    <button class="SizeBtn" type="button" data-size="${sz}" data-sku="${p.id}" aria-pressed="${sizeOf(p) === sz}">${sz}</button>
  `).join("")}</div>` : "";
  const isFw = isFourthwallItem(p);
  const raceDayShip = isRaceDayJacket(p);
  const fulfillmentLine = "Print errors and defects are replaced or refunded. Secure checkout and fulfillment by Fourthwall.";
  const shipNote = raceDayShip
    ? `<p style="margin-top:8px;font-size:13.5px;font-weight:700;color:#0f172a">Made overseas. Ships in about 10–14 business days. Free US shipping.</p>`
    : ["APC-C43","APC-C51","APC-C52","APC-C53","APC-C54","APC-C55"].indexOf(p.id) !== -1
    ? `<p style="margin-top:8px;font-size:13.5px;font-weight:700;color:#0f172a">Made to order. Ships from the US or Canada. Free US shipping.</p>`
    : `<p style="margin-top:8px;font-size:13.5px;font-weight:700;color:#0f172a">Made to order. Ships from the US. Free US shipping.</p>`;
  const buyBtnLabel = "Buy Now - Instant Checkout";
  const withoutMade = (text) => String(text || "")
    .replace(/made to order\s*·\s*made to order\s*·?/gi, "")
    .replace(/made to order\s*[.·]?\s*/gi, "")
    .replace(/\s*·\s*·\s*/g, " · ")
    .replace(/\s{2,}/g, " ")
    .replace(/\s+\./g, ".")
    .trim();
  const highlights = (p.highlights || [])
    .map(withoutMade)
    .filter((h) => h && !/^fulfillment:\s*$/i.test(h));
  $("#productModalContent").innerHTML = `
    <div class="ProductLayout">
      <div class="ProductLayout__photo"><img src="${esc(photoOf(p))}" alt="${esc(p.title)}" /></div>
      <div class="ProductLayout__copy">
        <div class="Card__dept">${esc(p.dept)} · ${esc(p.category || "")}</div>
        <h2>${esc(p.title)}</h2>
        <div class="Price"><span>${money(shownPrice)}</span>${was}</div>
        ${shipNote}
        <p style="margin-top:10px;font-size:13px;font-weight:600;color:#0f172a">${esc(fulfillmentLine)}</p>
        ${blankSelector}
        ${swatches}
        ${sizes}
        <div class="Card__actions" style="margin-top:14px;margin-bottom:14px">
          <button class="Btn Btn--cobalt" type="button" data-buy="${p.id}" style="font-weight:800">${esc(buyBtnLabel)} · ${money(shownPrice)} →</button>
          <button class="Btn Btn--plain" type="button" data-add="${p.id}">Add to bag</button>
        </div>
        <p style="margin-top:10px">${esc(withoutMade(p.short_desc || ""))}</p>
        <ul class="Highlights">${highlights.map((h) => `<li>${esc(h)}</li>`).join("")}</ul>
        ${p.review_quote ? `<blockquote class="Quote">${esc(p.review_quote)}</blockquote>` : ""}
      </div>
    </div>`;
  openSheet("productModal");
}

function checkoutLines() {
  return express || cart;
}

function openCheckout(lines) {
  express = lines;
  const bag = checkoutLines();
  if (!bag.length) {
    toast("Add a piece before checkout");
    return;
  }
  closeSheet("productModal");
  closeSheet("cartDrawer");
  trackHit("checkout_clicks_total");
  bag.forEach((item) => { if (item && item.id) trackHit(`checkout_${item.id}`); });
  const fwBag = bag.filter((item) => item.is_fourthwall);
  if (fwBag.length) {
    const fallback = fwBag[0] ? fwBag[0].fourthwall_product_url : "https://apex-hybrid-co-shop.fourthwall.com";
    checkoutViaFourthwallApi(fwBag, fallback);
    return;
  }
  const rawSub = bag.reduce((sum, item) => sum + item.price * item.qty, 0);
  const promoInfo = resolvePromo(activePromo);
  const discAmt = promoInfo ? rawSub * (promoInfo.pct / 100) : 0;
  const sub = Math.max(0, rawSub - discAmt);
  const hasFw = bag.some((item) => item.is_fourthwall);
  const hasWs = bag.some((item) => !item.is_fourthwall);
  const checkoutTitle = "Secure checkout";
  const checkoutDesc = "Made to order. Free US shipping. Print errors and defects are replaced or refunded. Secure checkout and fulfillment by Fourthwall.";
  const submitLabel = `Complete Order · ${money(sub)}`;
  $("#checkoutModalContent").innerHTML = `
    <h2 style="letter-spacing:-0.04em;font-size:32px">${esc(checkoutTitle)}</h2>
    <p style="color:#5e6672;margin:6px 0 14px">${esc(checkoutDesc)}</p>
    <div style="margin-bottom:14px">
      ${bag.map((item) => `
        <div class="Row"><span>${item.qty} × ${esc(item.title)} <span class="StripeId">${esc(item.variant)}</span></span><strong>${money(item.price * item.qty)}</strong></div>
        <div class="StripeId">Free US shipping${item.is_fourthwall && item.fourthwall_product_url ? ` · <a href="${esc(item.fourthwall_product_url)}" target="_blank" rel="noopener" style="color:#2563eb;font-weight:700">Secure checkout and fulfillment by Fourthwall</a>` : ""}</div>
      `).join("")}
      <div style="margin:10px 0;display:flex;gap:8px;align-items:center">
        <input id="checkoutPromoInput" type="text" value="${esc(activePromo)}" placeholder="Promo code" style="flex:1;padding:8px 10px;border:1px solid #d1d5db;border-radius:6px;font-size:13px;text-transform:uppercase" />
        <button type="button" class="Btn Btn--plain" data-apply-promo="checkout" style="padding:8px 14px;font-size:13px">Apply Code</button>
      </div>
      ${promoInfo ? `<div class="Row" style="color:#059669;font-weight:700"><span>Promo (${esc(promoInfo.code)} · ${promoInfo.pct}% off)</span><strong>−${money(discAmt)}</strong></div>` : ""}
      <div class="Row" style="margin-top:8px"><span>US delivery</span><strong>Free</strong></div>
      <div class="Row"><span>Total</span><strong>${money(sub)}</strong></div>
    </div>
    <form class="CheckoutForm" id="checkoutForm">
      <div class="CheckoutGrid">
        <label class="Field">Full name<input name="name" required autocomplete="name" /></label>
        <label class="Field">Email<input name="email" type="email" required autocomplete="email" /></label>
        <label class="Field full">Street<input name="street" required autocomplete="address-line1" /></label>
        <label class="Field">City and state<input name="city" required autocomplete="address-level2" /></label>
        <label class="Field">ZIP<input name="zip" required autocomplete="postal-code" /></label>
      </div>
      <button class="Btn Btn--cobalt Btn--full" type="submit" style="margin-top:8px">${esc(submitLabel)}</button>
    </form>`;
  openSheet("checkoutModal");
  $("#checkoutForm").addEventListener("submit", submitOrder);
}

function submitOrder(event) {
  event.preventDefault();
  const data = new FormData(event.target);
  const bag = checkoutLines();
  const rawSub = bag.reduce((sum, item) => sum + item.price * item.qty, 0);
  const promoInfo = resolvePromo(activePromo);
  const discAmt = promoInfo ? rawSub * (promoInfo.pct / 100) : 0;
  const sub = Math.max(0, rawSub - discAmt);
  const orderId = `APX-${Math.floor(100000 + Math.random() * 900000)}`;
  trackHit("order_submits_total");
  const name = String(data.get("name") || "").trim();
  const email = String(data.get("email") || "").trim();
  const street = String(data.get("street") || "").trim();
  const city = String(data.get("city") || "").trim();
  const zip = String(data.get("zip") || "").trim();
  const lines = bag.map((item) => {
    const stripe = [item.stripe_price_id, item.stripe_product_id, item.stripe_account_id].filter(Boolean).join(" | ");
    const fulfill = item.is_fourthwall ? `Fourthwall (${item.fourthwall_blank})` : "US  Direct Wholesale";
    return `- ${item.qty}x ${item.title} (${item.variant}) ${money(item.price * item.qty)} [Fulfillment: ${fulfill} | ${stripe}]`;
  }).join("\n");
  const hasFw = bag.some((item) => item.is_fourthwall);
  const subject = encodeURIComponent(`Order ${orderId}  -  ${hasFw ? "Fourthwall & Stripe" : "Stripe"} Checkout (${money(sub)})`);
  const promoLine = promoInfo ? `\nPromo Code: ${promoInfo.code} (${promoInfo.pct}% Off, -${money(discAmt)})` : "";
  const body = encodeURIComponent(`Order ID: ${orderId}\nCustomer: ${name} (${email})\nShip To: ${street}, ${city} ${zip}\nFulfillment: ${hasFw ? "Fourthwall US Apparel Production / Direct US Dispatch" : "US  Direct Wholesale"}${promoLine}\n\nItems:\n${lines}\n\nTotal: ${money(sub)} (Free US shipping)`);
  $("#checkoutModalContent").innerHTML = `
    <h2 style="letter-spacing:-0.04em;font-size:32px">Order ${esc(orderId)} is reserved</h2>
    <p style="margin:8px 0 14px">Thanks ${esc(name)}  -  your order is reserved for ${esc(city)} ${esc(zip)}. Click below to confirm your order and receive your instant payment and tracking link.</p>
    ${bag.map((item) => `<div class="Row"><span>${item.qty} × ${esc(item.title)}</span><strong>${money(item.price * item.qty)}</strong></div>`).join("")}
    <div class="Row"><span>Total</span><strong>${money(sub)}</strong></div>
    <a class="Btn Btn--cobalt Btn--full" style="margin-top:16px" href="mailto:apexhybridco@gmail.com?subject=${subject}&body=${body}">Email me the Stripe payment link</a>
    <button class="Btn Btn--ghost Btn--full" type="button" style="margin-top:8px" data-close="checkoutModal">Done</button>`;
  if (!express) cart = [];
  express = null;
  renderCart();
}

function fmt(totalSeconds) {
  const s = Math.max(0, Math.round(totalSeconds));
  const m = Math.floor(s / 60);
  const rem = s % 60;
  return `${m}:${String(rem).padStart(2, "0")}`;
}

function currentCity() {
  const id = $("#calcCity") ? $("#calcCity").value : "CHI";
  return CITIES.find((city) => city.code === id) || CITIES[0];
}

function updateRaceSplitCalculator() {
  const finishEl = $("#calcTargetFinish");
  const divEl = $("#calcDivision");
  const table = $("#splitTable");
  if (!finishEl || !divEl || !table) return;
  const target = (parseInt(finishEl.value, 10) || 70) * 60;
  const division = divEl.value;
  const city = currentCity();
  let runShare = division === "pro" ? 0.5 : division === "doubles" ? 0.56 : 0.53;
  const roxShare = 0.068;
  let stationShare = 1 - runShare - roxShare;
  if (division === "doubles") stationShare *= 0.72;
  let run = target * runShare * city.run;
  const rox = target * roxShare;
  const pool = target * stationShare;
  const stationTimes = STATIONS.map(([, , , weight, sled]) => pool * weight * (sled ? city.sled : 1));
  const raw = run + rox + stationTimes.reduce((sum, n) => sum + n, 0);
  const scale = target / raw;
  run *= scale;
  const stations = stationTimes.map((n) => n * scale);
  const roxScaled = rox * scale;
  const perKm = run / 8;
  const rows = [
    ["Run 1–8", `${fmt(perKm)} / km`, fmt(run)],
    ...STATIONS.map(([, name], i) => [`${STATIONS[i][0]}  ${name}`, "Station", fmt(stations[i])]),
    ["Roxzone", "All transitions", fmt(roxScaled)],
  ];
  const total = run + stations.reduce((s, n) => s + n, 0) + roxScaled;
  table.innerHTML = `
    <thead><tr><th>Piece</th><th>Read</th><th>Time</th></tr></thead>
    <tbody>
      ${rows.map(([a, b, c]) => `<tr><td>${esc(a)}</td><td>${esc(b)}</td><td>${esc(c)}</td></tr>`).join("")}
      <tr class="total"><td>Finish</td><td>${esc(city.name)}</td><td>${fmt(total)}</td></tr>
    </tbody>`;
  const note = $("#calcNote");
  if (note) {
    const divNote = division === "pro" ? "Pro sleds take a larger share of the clock." : division === "doubles" ? "Doubles share the stations. The run is still yours." : "Open division pacing, even from the first kilometer.";
    note.textContent = `${city.name} · ${city.venue}, ${city.when}. ${city.note} ${divNote}`;
  }
  const calcCta = $("#calcCheckoutBar");
  if (calcCta) {
    const cityProd = findProduct(city.sku);
    const cityPrice = cityProd ? money(cityProd.retail_price) : "$38";
    calcCta.innerHTML = `
      <button class="Btn Btn--cobalt" type="button" data-buy="${esc(city.sku)}" style="font-weight:800">Buy ${esc(city.name)} Race Tee (${cityPrice}) — Instant Checkout →</button>
      <button class="Btn Btn--plain" type="button" data-buy="APC-C36">Buy Built For Heavy Legs →</button>
      <a class="Btn Btn--ghost" href="team_orders.html" style="text-decoration:none">Doubles 2-Pack Bundles (15% Off) →</a>
    `;
  }
}

function renderLabCities() {
  $("#labCities").innerHTML = CITIES.map((city) => `
    <button class="CityPick" type="button" data-city="${city.code}" data-sku="${city.sku}">
      <span>${esc(city.when)}</span>
      <strong>${esc(city.name)}</strong>
      <p>${esc(city.venue)}. ${esc(city.note)}</p>
    </button>
  `).join("");
}

function renderArticles() {
  const list = $("#articleList");
  if (!list) return;
  if (!activeArticle && GUIDES[0]) activeArticle = GUIDES[0].slug;
  list.innerHTML = GUIDES.map((guide) => `
    <button type="button" data-article="${esc(guide.slug)}" aria-current="${guide.slug === activeArticle}">${esc(guide.title)}</button>
  `).join("");
  const guide = GUIDES.find((item) => item.slug === activeArticle) || GUIDES[0];
  const reader = $("#articleReader");
  if (!guide || !reader) return;
  const recs = (guide.recommended_skus || []).map((sku) => findProduct(sku)).filter(Boolean);
  reader.innerHTML = `
    <p class="Card__dept" style="color:#00f0ff">${esc(guide.category)} · ${esc(guide.read_time)}</p>
    <h3>${esc(guide.title)}</h3>
    <div class="Prose">${guide.body_html || ""}</div>
    <div class="Recs">
      ${recs.map((p) => `
        <div class="Rec">
          <img src="${esc(p.image)}" alt="" />
          <strong>${esc(p.title)}</strong>
          <div>${money(p.retail_price)}</div>
          <div style="display:flex;gap:6px;margin-top:6px">
            <button class="Btn Btn--cobalt" type="button" data-buy="${p.id}" style="flex:1;padding:7px 10px;font-size:12px">Buy Now →</button>
            <button class="Btn Btn--plain" type="button" data-add="${p.id}" style="padding:7px 10px;font-size:12px">+ Bag</button>
          </div>
        </div>`).join("")}
    </div>`;
}

function openLab(tab, slug) {
  labTab = tab || "calculator";
  if (slug) activeArticle = slug;
  document.querySelectorAll("[data-tab]").forEach((button) => {
    button.setAttribute("aria-pressed", button.dataset.tab === labTab ? "true" : "false");
  });
  document.querySelectorAll(".LabPane").forEach((pane) => {
    pane.hidden = pane.dataset.pane !== labTab;
  });
  renderArticles();
  updateRaceSplitCalculator();
  openSheet("raceLab");
}

function toast(message) {
  const node = $("#toast");
  node.textContent = message;
  node.classList.add("is-on");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => node.classList.remove("is-on"), 2200);
}

function onClick(event) {
  const deptBtn = event.target.closest("[data-dept]");
  if (deptBtn && deptBtn.dataset.dept) {
    event.preventDefault();
    setDept(deptBtn.dataset.dept);
    $("#siteNav").classList.remove("is-open");
    return;
  }
  const lab = event.target.closest("[data-lab]");
  if (lab) {
    openLab(lab.dataset.lab, lab.dataset.article || null);
    return;
  }
  const tab = event.target.closest("[data-tab]");
  if (tab) {
    openLab(tab.dataset.tab);
    return;
  }
  const article = event.target.closest("[data-article]");
  if (article) {
    activeArticle = article.dataset.article;
    renderArticles();
    if (!$("#raceLab").classList.contains("is-open")) openLab("articles", activeArticle);
    return;
  }
  const quickAdd = event.target.closest("[data-quick-add]");
  if (quickAdd) {
    const sku = quickAdd.dataset.quickAdd;
    if (quickAdd.dataset.size) sizeChoice[sku] = quickAdd.dataset.size;
    addToCart(sku, false);
    return;
  }
  const color = event.target.closest("[data-color]");
  if (color) {
    // Black-only storefront — ignore other colors selections.
    colorChoice[color.dataset.sku] = "black";
    renderProducts();
    if ($("#productModal").classList.contains("is-open")) openProduct(color.dataset.sku);
    return;
  }
  const blank = event.target.closest("[data-blank]");
  if (blank) {
    blankChoice[blank.dataset.sku] = blank.dataset.blank;
    if ($("#productModal").classList.contains("is-open")) openProduct(blank.dataset.sku);
    return;
  }
  const size = event.target.closest("[data-size]");
  if (size) {
    sizeChoice[size.dataset.sku] = size.dataset.size;
    renderProducts();
    if ($("#productModal").classList.contains("is-open")) openProduct(size.dataset.sku);
    return;
  }
  const quick = event.target.closest("[data-quick]");
  if (quick) {
    openProduct(quick.dataset.quick);
    return;
  }
  const fwLink = event.target.closest('a[href*="apex-hybrid-co-shop.fourthwall.com/products/"]');
  if (fwLink) {
    const href = fwLink.getAttribute("href") || "";
    const slug = href.split("?")[0].replace(/\/+$/, "").split("/").pop();
    const matchedSku = Object.keys(FW_VARIANTS).find((k) => (FW_VARIANTS[k].url || "").endsWith("/" + slug));
    if (matchedSku) {
      event.preventDefault();
      trackHit("checkout_clicks_total");
      trackHit(`checkout_${matchedSku}`);
      const p = findProduct(matchedSku) || { id: matchedSku, fourthwall_product_url: href };
      checkoutViaFourthwallApi([{ id: matchedSku, size: sizeChoice[matchedSku] || "L", qty: 1 }], p.fourthwall_product_url || href);
      return;
    }
  }
  const buy = event.target.closest("[data-buy]");
  if (buy) {
    const p = findProduct(buy.dataset.buy);
    if (p) {
      event.preventDefault();
      trackHit("checkout_clicks_total");
      trackHit(`checkout_${p.id}`);
      checkoutViaFourthwallApi([lineFrom(p)], p.fourthwall_product_url);
    }
    return;
  }
  const add = event.target.closest("[data-add]");
  if (add) {
    addToCart(add.dataset.add, true);
    return;
  }
  const qty = event.target.closest("[data-qty]");
  if (qty) {
    changeQty(qty.dataset.key, Number(qty.dataset.qty));
    return;
  }
  const city = event.target.closest("[data-city]");
  if (city && $("#calcCity")) {
    $("#calcCity").value = city.dataset.city;
    updateRaceSplitCalculator();
    if (city.dataset.sku && event.target.closest("#labCities")) {
      closeSheet("raceLab");
      openProduct(city.dataset.sku);
    }
    return;
  }
  const promoBtn = event.target.closest("[data-apply-promo]");
  if (promoBtn) {
    const mode = promoBtn.dataset.applyPromo;
    const input = document.getElementById(mode === "checkout" ? "checkoutPromoInput" : "cartPromoInput");
    if (input) {
      const val = input.value.trim();
      if (!val) clearPromoCode();
      else setPromoCode(val, true);
      if (mode === "checkout") openCheckout(express);
    }
    return;
  }
  if (event.target.closest("[data-bag]")) {
    openSheet("cartDrawer");
    return;
  }
  if (event.target.closest("[data-checkout-cart]")) {
    express = null;
    openCheckout(null);
    return;
  }
  if (event.target.closest("[data-clear-search]")) {
    query = "";
    $("#searchInput").value = "";
    renderProducts();
    return;
  }
  if (event.target.closest("[data-clear-cart]")) cart = [];
  const closer = event.target.closest("[data-close]");
  if (closer) {
    closeSheet(closer.dataset.close);
    renderCart();
    return;
  }
  const menu = event.target.closest("#menuBtn");
  if (menu) {
    const nav = $("#siteNav");
    const open = nav.classList.toggle("is-open");
    menu.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.classList.toggle("nav-open", open);
    return;
  }
  if (event.target.closest("#siteNav a")) {
    const nav = $("#siteNav");
    if (nav) nav.classList.remove("is-open");
    document.body.classList.remove("nav-open");
    const btn = $("#menuBtn");
    if (btn) btn.setAttribute("aria-expanded", "false");
  }
}

function boot(data) {
  const RETIRED_SKUS = new Set([]); // retired logos, never show in grid or quick view
  PRODUCTS = (data.products || []).filter((p) => !RETIRED_SKUS.has(p.id));
  GUIDES = data.guides || [];
  renderLabCities();
  renderProducts();
  renderCart();
  renderArticles();
  updateRaceSplitCalculator();
  const params = new URLSearchParams(window.location.search);
  const urlQ = params.get("q") || "";
  if (urlQ) {
    query = urlQ;
    const searchBox = document.getElementById("searchInput");
    if (searchBox) searchBox.value = urlQ;
    renderProducts();
  }
  const urlPromo = params.get("promo") || params.get("discount") || params.get("code") || params.get("ref") || "";
  if (urlPromo) {
    setPromoCode(urlPromo, true);
  }
  const reqDept = params.get("dept") || "";
  if (reqDept) {
    dept = (reqDept === "Lightweight Jackets" || reqDept === "Race Day Windbreakers") ? "Windbreakers" : reqDept;
    renderProducts();
  }
  const reqQty = Math.max(1, parseInt(params.get("qty") || "1", 10) || 1);
  const buy = findProduct(params.get("buy") || "");
  const add = findProduct(params.get("add") || "");
  const targetProd = buy || add;
  if (targetProd) {
    if (params.get("size")) sizeChoice[targetProd.id] = params.get("size");
    if (params.get("color")) colorChoice[targetProd.id] = "black";
    if (params.get("blank")) blankChoice[targetProd.id] = String(params.get("blank")).toLowerCase().includes("light") ? "light" : "heavy";
  }
  if (buy) {
    if (isFourthwallItem(buy)) {
      trackHit("checkout_clicks_total");
      trackHit(`checkout_${buy.id}`);
      checkoutViaFourthwallApi([lineFrom(buy, reqQty)], buy.fourthwall_product_url);
      return;
    }
    openCheckout([lineFrom(buy, reqQty)]);
  } else if (add) {
    if (params.get("checkout") === "1" && isFourthwallItem(add)) {
      trackHit("checkout_clicks_total");
      trackHit(`checkout_${add.id}`);
      checkoutViaFourthwallApi([lineFrom(add, reqQty)], add.fourthwall_product_url);
      return;
    }
    addToCart(add.id, true, false);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  trackHit("pageviews_total");
  trackHit("pageviews_home");
  try {
    if (!sessionStorage.getItem("apx_uv_tracked")) {
      sessionStorage.setItem("apx_uv_tracked", "1");
      trackHit("unique_sessions_total");
    }
  } catch (_) {}
  document.body.addEventListener("click", onClick);
  const searchForm = $("#searchForm");
  if (searchForm) {
    searchForm.addEventListener("submit", (event) => {
      event.preventDefault();
      query = $("#searchInput").value;
      renderProducts();
      const apparel = $("#apparel");
      if (apparel) apparel.scrollIntoView({ behavior: "smooth" });
    });
  }
  const searchInput = $("#searchInput");
  if (searchInput) {
    searchInput.addEventListener("input", (event) => {
      query = event.target.value;
      renderProducts();
    });
  }
  const sortSelect = $("#sortSelect");
  if (sortSelect) {
    sortSelect.addEventListener("change", (event) => {
      sort = event.target.value;
      renderProducts();
    });
  }
  ["calcTargetFinish", "calcDivision", "calcCity"].forEach((id) => {
    const node = document.getElementById(id);
    if (node) node.addEventListener("change", updateRaceSplitCalculator);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeAll();
  });
  fetch("catalog.json?v=20261119hyrxcity2")
    .then((res) => {
      if (!res.ok) throw new Error("catalog");
      return res.json();
    })
    .then(boot)
    .catch(() => {
      $("#productGrid").innerHTML = `<div class="Error"><p>The catalog didn’t load. Refresh the page.</p></div>`;
    });
});

window.openProductModal = openProduct;
window.closeProductModal = () => closeSheet("productModal");
window.addToCart = addToCart;
window.openCheckoutModal = () => { express = null; openCheckout(null); };
window.closeCheckoutModal = () => closeSheet("checkoutModal");
window.updateRaceSplitCalculator = updateRaceSplitCalculator;
window.filterByDepartment = setDept;
window.toggleCartDrawer = (open) => (open ? openSheet("cartDrawer") : closeSheet("cartDrawer"));
window.openRaceLab = openLab;
