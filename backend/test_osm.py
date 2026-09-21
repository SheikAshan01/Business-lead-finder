import urllib.parse
import httpx

query = """[out:json][timeout:15];
(
  node["amenity"="restaurant"](around:20000, 10.3673, 77.9803);
  way["amenity"="restaurant"](around:20000, 10.3673, 77.9803);
);
out center 30;"""

endpoints = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

for ep in endpoints:
    print(f"Testing {ep} ...")
    try:
        # GET request
        r = httpx.get(ep, params={"data": query}, timeout=10)
        print("  GET status:", r.status_code)
        if r.status_code == 200:
            print(f"  SUCCESS! Found {len(r.json().get('elements', []))} elements")
            for el in r.json().get("elements", [])[:3]:
                print("   *", el.get("tags", {}).get("name"))
            break
    except Exception as e:
        print("  Error:", e)
