import re
from enum import Enum
from rapidfuzz.fuzz import ratio, token_sort_ratio
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.models.business import Business
from app.scrapers.base import RawBusiness


class DuplicateStatus(str, Enum):
    UNIQUE = "UNIQUE"
    POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"
    DUPLICATE = "DUPLICATE"


def clean_for_fuzzy(text: str | None) -> str:
    if not text:
        return ""
    # Lowercase and remove all non-alphanumeric chars
    return re.sub(r"[^a-z0-9]", "", text.lower())


class Deduplicator:
    """Detects exact and fuzzy duplicates against existing database records."""

    @staticmethod
    def check_duplicate(raw: RawBusiness, db: Session) -> tuple[DuplicateStatus, Business | None, str]:
        """Check raw record against existing database records."""
        # 1. Exact Phone Match
        if raw.phone:
            match = db.scalar(
                select(Business).where(
                    or_(Business.phone == raw.phone, Business.alternate_phone == raw.phone)
                )
            )
            if match:
                return DuplicateStatus.DUPLICATE, match, f"Exact phone match with #{match.id} ({match.phone})"

        # 2. Exact Email Match
        if raw.email:
            match = db.scalar(
                select(Business).where(Business.email.ilike(raw.email))
            )
            if match:
                return DuplicateStatus.DUPLICATE, match, f"Exact email match with #{match.id} ({match.email})"

        # 3. Exact Website Match
        if raw.website_url:
            match = db.scalar(
                select(Business).where(Business.website_url.ilike(raw.website_url))
            )
            if match:
                return DuplicateStatus.DUPLICATE, match, f"Exact website match with #{match.id} ({match.website_url})"

        # 4. Fuzzy Business Name & Address Match (RapidFuzz)
        # Search existing candidates in the same district or state
        query = select(Business)
        if raw.district:
            query = query.where(Business.district.ilike(f"%{raw.district}%"))
        candidates = db.scalars(query.limit(200)).all()

        raw_clean_name = clean_for_fuzzy(raw.business_name)
        raw_clean_addr = clean_for_fuzzy(raw.address)

        for candidate in candidates:
            cand_clean_name = clean_for_fuzzy(candidate.business_name)
            cand_clean_addr = clean_for_fuzzy(candidate.address)

            name_sim = ratio(raw_clean_name, cand_clean_name)
            token_sim = token_sort_ratio(raw.business_name.lower(), candidate.business_name.lower())
            best_name_sim = max(name_sim, token_sim)

            # Check address similarity if both addresses exist
            addr_sim = ratio(raw_clean_addr, cand_clean_addr) if (raw_clean_addr and cand_clean_addr) else 0

            # High confidence duplicate: Name >= 92% and address >= 70%
            if best_name_sim >= 92 and (addr_sim >= 70 or not cand_clean_addr or not raw_clean_addr):
                return (
                    DuplicateStatus.DUPLICATE,
                    candidate,
                    f"Fuzzy name similarity ({best_name_sim:.1f}%) and address ({addr_sim:.1f}%) with #{candidate.id}",
                )

            # Possible duplicate: Name >= 85%
            if best_name_sim >= 85:
                return (
                    DuplicateStatus.POSSIBLE_DUPLICATE,
                    candidate,
                    f"Possible duplicate: name similarity ({best_name_sim:.1f}%) with #{candidate.id}",
                )

        return DuplicateStatus.UNIQUE, None, "No duplicate detected"
