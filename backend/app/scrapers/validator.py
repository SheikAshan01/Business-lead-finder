import re
from app.scrapers.base import RawBusiness
from app.scrapers.normalizer import normalize_business_name, normalize_email, normalize_phone, normalize_url


class BusinessValidator:
    """Validates and cleans business records ensuring strict data accuracy."""

    @staticmethod
    def is_valid_name(name: str | None) -> bool:
        if not name:
            return False
        cleaned = name.strip()
        if len(cleaned) < 2:
            return False
        # Must contain at least one alphanumeric character
        if not re.search(r"[a-zA-Z0-9]", cleaned):
            return False
        return True

    @classmethod
    def clean_and_validate(cls, raw: RawBusiness) -> RawBusiness | None:
        """Clean raw record, validate mandatory fields, and ensure no hallucinated data."""
        if not cls.is_valid_name(raw.business_name):
            return None

        # Clean fields
        raw.business_name = normalize_business_name(raw.business_name)
        raw.phone = normalize_phone(raw.phone)
        raw.alternate_phone = normalize_phone(raw.alternate_phone)
        raw.email = normalize_email(raw.email)
        raw.website_url = normalize_url(raw.website_url)
        raw.facebook_url = normalize_url(raw.facebook_url)
        raw.instagram_url = normalize_url(raw.instagram_url)
        raw.youtube_url = normalize_url(raw.youtube_url)
        raw.whatsapp_url = normalize_url(raw.whatsapp_url)

        # Ensure address is cleaned or None
        if raw.address:
            raw.address = raw.address.strip()
            if not raw.address:
                raw.address = None

        return raw
