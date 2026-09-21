import re
from urllib.parse import urlparse

# Indian Mobile Regex (10 digits starting with 6, 7, 8, 9)
MOBILE_RE = re.compile(r"^[6-9]\d{9}$")
# Standard Email Regex
EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def normalize_phone(value: str | None) -> str | None:
    """Normalize Indian phone numbers to standard 10-digit mobile or valid STD landline format."""
    if not value:
        return None
    # Remove all non-digits
    digits = re.sub(r"\D", "", value)

    # Remove international dialing prefix 0091
    if digits.startswith("0091") and len(digits) == 14:
        digits = digits[4:]
    # Remove country code 91 if 12 digits
    elif digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    # Remove leading 0 if 11 digits and the remaining 10 is a mobile number
    elif digits.startswith("0") and len(digits) == 11 and MOBILE_RE.match(digits[1:]):
        digits = digits[1:]

    # 10 digits starting with 6, 7, 8, or 9 (Indian Mobile / WLL)
    if len(digits) == 10 and MOBILE_RE.match(digits):
        return digits

    # Standard Indian Landline (starting with 0, 10-11 digits)
    if digits.startswith("0") and 10 <= len(digits) <= 11:
        return digits

    # Valid 10-digit landline without leading 0 (starts with 2, 3, 4)
    if len(digits) == 10 and digits[0] in "2345":
        return digits

    return None


def normalize_email(value: str | None) -> str | None:
    """Normalize and validate email syntax."""
    if not value:
        return None
    cleaned = value.strip().lower()
    if EMAIL_RE.match(cleaned):
        return cleaned
    return None


def normalize_business_name(value: str | None) -> str:
    """Normalize business name for consistent display and comparison while preserving acronyms."""
    if not value:
        return ""
    name = value.strip()
    name = re.sub(r"\s+", " ", name)
    return name


def normalize_url(value: str | None) -> str | None:
    """Normalize URL syntax and ensure scheme is present."""
    if not value:
        return None
    val = value.strip()
    if not val.startswith(("http://", "https://")):
        val = f"https://{val}"
    try:
        parsed = urlparse(val)
        if not parsed.netloc:
            return None
        # Clean trailing slash from root domain
        path = parsed.path.rstrip("/") if parsed.path else ""
        return f"{parsed.scheme}://{parsed.netloc}{path}"
    except Exception:
        return None
