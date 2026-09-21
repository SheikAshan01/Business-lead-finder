import pytest
from app.scrapers.adapters.osm_overpass import OSMOverpassAdapter
from app.scrapers.tn_data import DISTRICT_METADATA, generate_district_prospects


def test_all_38_tn_districts_covered():
    assert len(DISTRICT_METADATA) >= 38
    for district, meta in DISTRICT_METADATA.items():
        assert "std" in meta
        assert "pincode" in meta
        assert "lat" in meta
        assert "lon" in meta
        assert len(meta["streets"]) >= 4


def test_prospect_generation_mobile_shops_dindigul():
    prospects = generate_district_prospects("Mobile Shops", "Dindigul", count=25)
    assert len(prospects) == 25
    for p in prospects:
        assert p.district == "Dindigul"
        assert p.phone is not None and len(p.phone) >= 10
        assert p.address is not None and "Dindigul" in p.address
        assert p.latitude != 0.0 and p.longitude != 0.0


def test_osm_adapter_resilient_discovery():
    adapter = OSMOverpassAdapter()
    results = adapter.search("Mobile Shops", "Dindigul", limit=20)
    assert len(results) >= 20
    for r in results:
        assert r.business_name
        assert r.district == "Dindigul"
        assert r.phone is not None
