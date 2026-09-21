import json
import re
from urllib.parse import urlparse
from rapidfuzz.fuzz import ratio
from app.models.business import Business, WebsiteStatus

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^(?:\+91|91)?[6-9]\d{9}$")


def normalize_phone(value: str | None) -> str | None:
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if len(digits) != 10 or not PHONE_RE.match(digits):
        return None
    return digits


def normalize_email(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().lower()
    return value if EMAIL_RE.match(value) else None


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def is_official_website(value: str | None) -> bool:
    if not value:
        return False
    host = urlparse(value).netloc.lower()
    blocked = ("facebook.com", "instagram.com", "youtube.com", "justdial.com", "google.com")
    return bool(host) and not any(item in host for item in blocked)


def score_business(business: Business) -> tuple[int, list[str]]:
    points = 0
    reasons: list[str] = []
    checks = [(business.phone, 20, "Phone available"), (business.email, 15, "Email available"), (business.address, 10, "Address available")]
    for value, weight, reason in checks:
        if value:
            points += weight
            reasons.append(f"{reason} +{weight}")
    if business.website_status == WebsiteStatus.NO_WEBSITE:
        points += 20
        reasons.append("Website missing +20")
    if any((business.facebook_url, business.instagram_url, business.youtube_url, business.whatsapp_url)):
        points += 15
        reasons.append("Social profile available +15")
    if business.source:
        points += 20
        reasons.append("Verified source +20")
    return min(points, 100), reasons


def apply_normalization(business: Business) -> Business:
    business.phone = normalize_phone(business.phone)
    business.email = normalize_email(business.email)
    if business.website_url and is_official_website(business.website_url):
        business.website_status = WebsiteStatus.WEBSITE_UNVERIFIED
    elif business.website_url:
        business.website_status = WebsiteStatus.SOCIAL_ONLY
    else:
        business.website_status = WebsiteStatus.NO_WEBSITE
    score, reasons = score_business(business)
    business.lead_score = score
    business.score_reasons = json.dumps(reasons)
    return business


def likely_duplicate(left: Business, right: Business) -> bool:
    if left.phone and right.phone and left.phone == right.phone:
        return True
    if left.email and right.email and left.email == right.email:
        return True
    names = ratio(normalize_name(left.business_name), normalize_name(right.business_name))
    addresses = ratio((left.address or "").lower(), (right.address or "").lower())
    return names >= 92 and addresses >= 70
