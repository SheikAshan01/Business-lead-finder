from app.scrapers.base import RawBusiness
from app.scrapers.normalizer import (
    normalize_business_name,
    normalize_email,
    normalize_phone,
    normalize_url,
)
from app.scrapers.validator import BusinessValidator


def test_indian_phone_normalization():
    # Various formats of valid Indian numbers
    assert normalize_phone("+91 98765 43210") == "9876543210"
    assert normalize_phone("+919876543210") == "9876543210"
    assert normalize_phone("919876543210") == "9876543210"
    assert normalize_phone("09876543210") == "9876543210"
    assert normalize_phone("98765-43210") == "9876543210"
    assert normalize_phone("9876543210") == "9876543210"

    # Invalid numbers
    assert normalize_phone("123") is None
    assert normalize_phone("1234567890") is None  # Doesn't start with 6-9
    assert normalize_phone("+1 555-123-4567") is None
    assert normalize_phone(None) is None


def test_email_normalization():
    assert normalize_email(" Contact@Example.com ") == "contact@example.com"
    assert normalize_email("sales.madurai+leads@sra.in") == "sales.madurai+leads@sra.in"

    # Malformed emails
    assert normalize_email("business@") is None
    assert normalize_email("@domain.com") is None
    assert normalize_email("not-an-email") is None
    assert normalize_email(None) is None


def test_business_name_normalization():
    assert normalize_business_name("  SRA  Software   Solutions  ") == "SRA Software Solutions"
    assert normalize_business_name("A.B.C. Furniture") == "A.B.C. Furniture"
    assert normalize_business_name("hotel saravana bhavan") == "hotel saravana bhavan"
    assert normalize_business_name("") == ""


def test_url_normalization():
    assert normalize_url("example.com") == "https://example.com"
    assert normalize_url("http://myshop.in/") == "http://myshop.in"
    assert normalize_url("https://www.sra.com/contact/") == "https://www.sra.com/contact"
    assert normalize_url(None) is None


def test_validator_rejects_empty_or_bogus_names():
    invalid_raw = RawBusiness(business_name=".")
    assert BusinessValidator.clean_and_validate(invalid_raw) is None

    valid_raw = RawBusiness(
        business_name="Madurai Krishna Sweets",
        phone="+91 94433 12345",
        email=" Sweets@MK.com ",
    )
    cleaned = BusinessValidator.clean_and_validate(valid_raw)
    assert cleaned is not None
    assert cleaned.phone == "9443312345"
    assert cleaned.email == "sweets@mk.com"
