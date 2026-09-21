import uuid
from app.db import SessionLocal
from app.models.business import Business
from app.scrapers.base import RawBusiness
from app.scrapers.deduplicator import Deduplicator, DuplicateStatus


def test_deduplicator_exact_and_fuzzy():
    db = SessionLocal()
    tag = uuid.uuid4().hex[:6]
    test_phone = f"9876{tag[:6]}"
    test_email = f"sales_{tag}@abcfurniture.com"
    test_district = f"Dist_{tag}"
    try:
        # 1. Existing business in DB
        biz = Business(
            business_name=f"ABC Furniture Madurai {tag}",
            phone=test_phone,
            email=test_email,
            address="100, West Masi Street",
            district=test_district,
        )
        db.add(biz)
        db.commit()
        db.refresh(biz)

        # 2. Test exact phone duplicate
        raw1 = RawBusiness(
            business_name="Completely Different Store",
            phone=test_phone,
            district=test_district,
        )
        status, match, reason = Deduplicator.check_duplicate(raw1, db)
        assert status == DuplicateStatus.DUPLICATE
        assert match.id == biz.id
        assert "Exact phone match" in reason

        # 3. Test exact email duplicate
        raw2 = RawBusiness(
            business_name="Random Name",
            email=test_email,
            district=test_district,
        )
        status, match, reason = Deduplicator.check_duplicate(raw2, db)
        assert status == DuplicateStatus.DUPLICATE
        assert match.id == biz.id
        assert "Exact email match" in reason

        # 4. Test fuzzy duplicate (e.g. "A.B.C Furniture Madurai")
        raw3 = RawBusiness(
            business_name=f"A.B.C Furniture Madurai {tag}",
            address="100, West Masi St",
            district=test_district,
        )
        status, match, reason = Deduplicator.check_duplicate(raw3, db)
        assert status in (DuplicateStatus.DUPLICATE, DuplicateStatus.POSSIBLE_DUPLICATE)
        assert match.id == biz.id

        # 5. Test unique business
        raw4 = RawBusiness(
            business_name="Thirunelveli Halwa Centre",
            phone="9443399999",
            district=test_district,
        )
        status, match, reason = Deduplicator.check_duplicate(raw4, db)
        assert status == DuplicateStatus.UNIQUE
        assert match is None
    finally:
        db.rollback()
        db.close()
