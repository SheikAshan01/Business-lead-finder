from app.models.business import WebsiteStatus
from app.scrapers.website_detector import classify_url_domain


def test_classify_no_website():
    status, url = classify_url_domain(None)
    assert status == WebsiteStatus.NO_WEBSITE
    assert url is None

    status, url = classify_url_domain("   ")
    assert status == WebsiteStatus.NO_WEBSITE


def test_classify_social_only_domains():
    status, _ = classify_url_domain("https://www.facebook.com/madurai.sweets")
    assert status == WebsiteStatus.SOCIAL_ONLY

    status, _ = classify_url_domain("https://instagram.com/sra_soft")
    assert status == WebsiteStatus.SOCIAL_ONLY

    status, _ = classify_url_domain("https://www.justdial.com/Madurai/Meenakshi-Store")
    assert status == WebsiteStatus.SOCIAL_ONLY

    status, _ = classify_url_domain("https://indiamart.com/company-profile")
    assert status == WebsiteStatus.SOCIAL_ONLY


def test_classify_official_domain():
    status, url = classify_url_domain("http://www.meenakshibakers.in")
    assert status == WebsiteStatus.WEBSITE_UNVERIFIED
    assert url == "http://www.meenakshibakers.in"
