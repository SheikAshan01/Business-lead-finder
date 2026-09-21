import logging
import httpx
from app.core.config import get_settings
from app.scrapers.base import BaseSourceAdapter, RawBusiness

logger = logging.getLogger("sra_leads.google_places")
settings = get_settings()


class GooglePlacesAdapter(BaseSourceAdapter):
    """Adapter for official Google Places API (New & Legacy Nearby/Text Search)."""

    name = "Google Places API"
    source_type = "API"
    enabled = bool(settings.google_places_api_key)
    rate_limit = 60
    terms_url = "https://cloud.google.com/maps-platform/terms"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.google_places_api_key

    def search(self, category: str, location: str, limit: int = 50) -> list[RawBusiness]:
        if not self.api_key:
            logger.info("Google Places API key is not configured. Skipping Google Places source.")
            return []

        results: list[RawBusiness] = []
        endpoint = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        query_str = f"{category} in {location}, Tamil Nadu"
        params = {
            "query": query_str,
            "key": self.api_key,
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(endpoint, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    places = data.get("results", [])[:limit]
                    for p in places:
                        place_id = p.get("place_id")
                        name = p.get("name")
                        address = p.get("formatted_address")
                        geom = p.get("geometry", {}).get("location", {})
                        lat = geom.get("lat")
                        lng = geom.get("lng")

                        # Lookup place details for official phone and website
                        phone = None
                        website = None
                        if place_id:
                            try:
                                det_resp = client.get(
                                    "https://maps.googleapis.com/maps/api/place/details/json",
                                    params={
                                        "place_id": place_id,
                                        "fields": "formatted_phone_number,international_phone_number,website",
                                        "key": self.api_key,
                                    },
                                    timeout=6.0,
                                )
                                if det_resp.status_code == 200:
                                    det = det_resp.json().get("result", {})
                                    phone = det.get("formatted_phone_number") or det.get("international_phone_number")
                                    website = det.get("website")
                            except Exception as det_err:
                                logger.debug(f"Place details lookup failed for {name}: {det_err}")

                        results.append(
                            RawBusiness(
                                business_name=name,
                                category=category,
                                phone=phone,
                                address=address,
                                district=location,
                                state="Tamil Nadu",
                                latitude=lat,
                                longitude=lng,
                                website_url=website,
                                source="Google Places",
                                source_url=f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                                source_record_id=f"gplaces:{place_id}",
                            )
                        )
                else:
                    logger.warning(f"Google Places API responded with status {resp.status_code}")
        except Exception as e:
            logger.error(f"Error fetching from Google Places: {e}")

        return results
