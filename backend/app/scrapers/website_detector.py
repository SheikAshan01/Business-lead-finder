from datetime import datetime
from urllib.parse import urlparse
import httpx
from app.models.business import WebsiteStatus

# Aggregator, marketplace, social, and directory domains that should NOT be counted as official websites
NON_OFFICIAL_DOMAINS = (
    "facebook.com",
    "fb.me",
    "instagram.com",
    "youtube.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "wa.me",
    "whatsapp.com",
    "justdial.com",
    "indiamart.com",
    "sulekha.com",
    "tradeindia.com",
    "google.com",
    "maps.google.com",
    "goo.gl",
    "yellowpages.in",
    "urbanpro.com",
    "zomato.com",
    "swiggy.com",
    "magicpin.in",
)


def classify_url_domain(url: str | None) -> tuple[WebsiteStatus, str | None]:
    """Check domain to determine if it is social/directory or potentially genuine."""
    if not url or not url.strip():
        return WebsiteStatus.NO_WEBSITE, None

    clean_url = url.strip()
    if not clean_url.startswith(("http://", "https://")):
        clean_url = f"https://{clean_url}"

    try:
        parsed = urlparse(clean_url)
        host = (parsed.netloc or "").lower()
        if not host:
            return WebsiteStatus.NO_WEBSITE, None

        for domain in NON_OFFICIAL_DOMAINS:
            if domain in host:
                return WebsiteStatus.SOCIAL_ONLY, clean_url

        return WebsiteStatus.WEBSITE_UNVERIFIED, clean_url
    except Exception:
        return WebsiteStatus.NO_WEBSITE, None


async def verify_website(url: str | None) -> tuple[WebsiteStatus, bool, datetime]:
    """Asynchronously probe website via HTTP HEAD/GET to verify if it is live and official."""
    checked_at = datetime.utcnow()
    initial_status, clean_url = classify_url_domain(url)

    if initial_status == WebsiteStatus.NO_WEBSITE or not clean_url:
        return WebsiteStatus.NO_WEBSITE, False, checked_at

    if initial_status == WebsiteStatus.SOCIAL_ONLY:
        return WebsiteStatus.SOCIAL_ONLY, False, checked_at

    # Attempt live probe
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SRA-Business-Lead-Finder/1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        async with httpx.AsyncClient(timeout=4.0, follow_redirects=True, verify=False) as client:
            try:
                resp = await client.head(clean_url, headers=headers)
            except Exception:
                resp = await client.get(clean_url, headers=headers)

            if 200 <= resp.status_code < 400:
                # Re-verify final redirect host is not a social domain
                final_host = urlparse(str(resp.url)).netloc.lower()
                if any(domain in final_host for domain in NON_OFFICIAL_DOMAINS):
                    return WebsiteStatus.SOCIAL_ONLY, False, checked_at
                return WebsiteStatus.WEBSITE_FOUND, True, checked_at
            else:
                return WebsiteStatus.WEBSITE_BROKEN, False, checked_at
    except (httpx.ConnectError, httpx.TimeoutException, httpx.RequestError):
        return WebsiteStatus.WEBSITE_BROKEN, False, checked_at
    except Exception:
        return WebsiteStatus.WEBSITE_UNVERIFIED, False, checked_at
