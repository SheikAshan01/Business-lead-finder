from app.models.business import Business, WebsiteStatus
from app.scrapers.lead_scorer import LeadScorer


def test_lead_score_all_available():
    # Maximum score: no website (+20), phone (+20), email (+15), address (+10), social (+15), source (+20) = 100
    score, reasons, _ = LeadScorer.calculate_score(
        phone="9876543210",
        email="contact@business.com",
        address="12, West Masi Street, Madurai",
        website_status=WebsiteStatus.NO_WEBSITE,
        has_social=True,
        source="OpenStreetMap",
    )
    assert score == 100
    assert "Website missing +20" in reasons
    assert "Phone available +20" in reasons
    assert "Email available +15" in reasons
    assert "Address available +10" in reasons
    assert "Social profile available +15" in reasons


def test_lead_score_minimal_fields():
    # When business only has name and source
    score, reasons, _ = LeadScorer.calculate_score(
        phone=None,
        email=None,
        address=None,
        website_status=WebsiteStatus.WEBSITE_FOUND,
        has_social=False,
        source="OpenStreetMap",
    )
    # Only verified source (+20)
    assert score == 20
    assert len(reasons) == 1
    assert "Verified source (OpenStreetMap) +20" in reasons


def test_lead_score_business_model():
    b = Business(
        business_name="Meenakshi Bhavan",
        phone="9876543210",
        email=None,
        address="Opposite Temple, Madurai",
        website_status=WebsiteStatus.NO_WEBSITE,
        source="OpenStreetMap",
    )
    score, reasons, _ = LeadScorer.score_business(b)
    # Website missing (20) + Phone (20) + Address (10) + Source (20) = 70
    assert score == 70
    assert "Website missing +20" in reasons
    assert "Phone available +20" in reasons
    assert "Address available +10" in reasons
