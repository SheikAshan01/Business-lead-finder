from app.models.business import Business, WebsiteStatus
from app.services.data_quality import apply_normalization, normalize_email, normalize_phone


def test_phone_normalization():
    assert normalize_phone("+91 98765 43210") == "9876543210"
    assert normalize_phone("123") is None


def test_email_normalization():
    assert normalize_email(" Business@Example.COM ") == "business@example.com"
    assert normalize_email("business@") is None


def test_scoring_never_invents_data():
    business = apply_normalization(Business(business_name="A shop", source="authorized-api"))
    assert business.phone is None
    assert business.email is None
    assert business.website_status == WebsiteStatus.NO_WEBSITE
    assert business.lead_score == 40
