import logging
import time
import httpx
from app.scrapers.base import BaseSourceAdapter, RawBusiness

logger = logging.getLogger("sra_leads.osm")

CATEGORY_SYNONYMS = {
    "restaurants": ["Restaurants", "Hotel", "Bhavan", "Mess", "Cafe", "Fast food", "Dining"],
    "hotels": ["Hotel", "Lodge", "Residency", "Resort", "Guest house"],
    "hospitals": ["Hospital", "Clinic", "Healthcare", "Eye care", "Nursing home"],
    "clinics": ["Clinic", "Doctors", "Dispensary", "Polyclinic"],
    "dental clinics": ["Dental clinic", "Dentist", "Dental care"],
    "pharmacies": ["Pharmacy", "Medicals", "Chemist", "Medical store"],
    "bakeries": ["Bakery", "Bakes", "Cake shop", "Sweets and bakery"],
    "supermarkets": ["Supermarket", "Hypermarket", "Departmental store", "Mart"],
    "grocery stores": ["Grocery", "Provision store", "Maligai kadai"],
    "garments": ["Garments", "Readymades", "Clothing", "Boutique"],
    "textiles": ["Textiles", "Silks", "Sarees", "Handlooms", "Fabric"],
    "jewellery": ["Jewellery", "Jewellers", "Gold mart", "Jewelry", "Silversmith"],
    "furniture": ["Furniture", "Timber and furniture", "Furnishing"],
    "electronics": ["Electronics", "Home appliances", "Electronic store"],
    "mobile shops": ["Mobile shop", "Cellular", "Phone store"],
    "bike dealers": ["Two wheeler showroom", "Motorcycle dealer", "Bike showroom"],
    "car dealers": ["Car dealer", "Automobile showroom", "Cars"],
    "auto service": ["Car service", "Automobile workshop", "Motor garage", "Auto electricals"],
    "mechanics": ["Mechanic works", "Two wheeler service", "Garage"],
    "schools": ["School", "Matriculation school", "Public school", "Vidyalaya"],
    "colleges": ["College", "Arts and science college", "Engineering college"],
    "coaching centres": ["Coaching center", "Tuition centre", "Academy"],
    "beauty parlours": ["Beauty parlour", "Ladies beauty care", "Salon"],
    "salons": ["Hair salon", "Men salon", "Barber shop"],
    "hardware": ["Hardware and paints", "Sanitaryware", "Building materials"],
    "electrical shops": ["Electricals", "Lighting and electricals"],
    "fitness & gyms": ["Gym", "Fitness center", "Health club"],
    "photography": ["Photo studio", "Photography", "Digital studio"],
}


class OSMOverpassAdapter(BaseSourceAdapter):
    """Permitted live OpenStreetMap discovery adapter.

    Queries official OpenStreetMap Nominatim live endpoints for 100% authentic,
    geolocated commercial entities mapped across Tamil Nadu. Never invents data.
    """

    name = "OpenStreetMap Overpass TN"
    source_type = "OPEN_DATA"
    enabled = True
    rate_limit = 30
    terms_url = "https://www.openstreetmap.org/copyright"

    def __init__(self, endpoint: str = "https://nominatim.openstreetmap.org/search"):
        self.endpoint = endpoint

    def search(self, category: str, location: str, limit: int = 50) -> list[RawBusiness]:
        results: list[RawBusiness] = []
        seen_names = set()
        seen_ids = set()

        headers = {
            "User-Agent": "SRA-Business-Lead-Finder/1.0 (contact@srasoftwaresolutions.com)",
            "Accept": "application/json",
        }

        # Determine queries using sector variations to find real establishments
        cat_lower = category.strip().lower()
        synonyms = CATEGORY_SYNONYMS.get(cat_lower, [category.strip()])

        search_queries = []
        # Primary query
        search_queries.append(f"{category} in {location}, Tamil Nadu")
        # Synonyms queries
        for syn in synonyms[:4]:
            q_str = f"{syn} in {location}, Tamil Nadu"
            if q_str not in search_queries:
                search_queries.append(q_str)
        search_queries.append(f"{category}, {location}, Tamil Nadu")

        for q in search_queries:
            if len(results) >= limit:
                break

            try:
                params = {
                    "q": q,
                    "format": "json",
                    "addressdetails": 1,
                    "extratags": 1,
                    "limit": min(limit - len(results), 25),
                }
                with httpx.Client(timeout=8.0) as client:
                    resp = client.get(self.endpoint, params=params, headers=headers)
                    if resp.status_code == 200:
                        items = resp.json()
                        if isinstance(items, list):
                            for item in items:
                                osm_key = f"{item.get('osm_type')}:{item.get('osm_id')}"
                                if osm_key in seen_ids:
                                    continue

                                rec = self._parse_nominatim_item(item, category, location)
                                if rec and rec.business_name.lower() not in seen_names:
                                    seen_names.add(rec.business_name.lower())
                                    seen_ids.add(osm_key)
                                    results.append(rec)
                                    if len(results) >= limit:
                                        break
            except Exception as e:
                logger.warning(f"Nominatim query '{q}' error: {e}")

            time.sleep(1.0)  # Complies with OpenStreetMap usage policy (1 req/sec)

        return results[:limit]

    def _parse_nominatim_item(self, item: dict, category: str, default_location: str) -> RawBusiness | None:
        """Parse raw OpenStreetMap Nominatim response into verified RawBusiness."""
        addr = item.get("address", {})
        extratags = item.get("extratags") or {}

        # 1. Business name extraction
        name = (
            item.get("name")
            or extratags.get("name")
            or extratags.get("name:en")
            or addr.get("amenity")
            or addr.get("shop")
            or addr.get("building")
        )
        if not name:
            display = item.get("display_name", "")
            parts = [p.strip() for p in display.split(",") if p.strip()]
            if parts:
                name = parts[0]

        if not name or len(name) < 2:
            return None

        # 2. GPS Coordinates (Real exact coordinates from OpenStreetMap)
        try:
            lat = float(item.get("lat", 0))
            lon = float(item.get("lon", 0))
        except (ValueError, TypeError):
            lat, lon = None, None

        # 3. Address components
        road = addr.get("road") or addr.get("pedestrian") or addr.get("suburb") or addr.get("neighbourhood")
        town = addr.get("town") or addr.get("city") or addr.get("village") or default_location
        district = addr.get("state_district") or addr.get("county") or default_location
        postcode = addr.get("postcode")
        state = addr.get("state") or "Tamil Nadu"

        address_parts = [p for p in [road, town, district, postcode] if p]
        full_address = ", ".join(address_parts) if address_parts else item.get("display_name")

        # 4. Contact tags (Directly from OSM tags; None if not provided)
        phone = (
            extratags.get("phone")
            or extratags.get("contact:phone")
            or extratags.get("mobile")
            or extratags.get("contact:mobile")
        )
        email = extratags.get("email") or extratags.get("contact:email")
        website = extratags.get("website") or extratags.get("contact:website") or extratags.get("url")

        facebook = extratags.get("contact:facebook") or extratags.get("facebook")
        instagram = extratags.get("contact:instagram") or extratags.get("instagram")
        whatsapp = extratags.get("contact:whatsapp") or extratags.get("whatsapp")

        osm_type = item.get("osm_type", "node")
        osm_id = item.get("osm_id", "")

        return RawBusiness(
            business_name=name,
            category=category,
            phone=phone,
            email=email,
            address=full_address,
            district=district,
            taluk=addr.get("county") or town,
            state=state,
            pincode=postcode,
            latitude=lat,
            longitude=lon,
            website_url=website,
            facebook_url=facebook,
            instagram_url=instagram,
            whatsapp_url=whatsapp,
            source="OpenStreetMap",
            source_url=f"https://www.openstreetmap.org/{osm_type}/{osm_id}" if osm_id else None,
            source_record_id=f"osm:{osm_type}/{osm_id}" if osm_id else None,
            extra_tags=extratags,
        )
