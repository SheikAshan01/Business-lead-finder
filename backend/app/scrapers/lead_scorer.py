import json
from app.models.business import Business, WebsiteStatus
from app.scrapers.base import RawBusiness


class LeadScorer:
    """Computes an explainable, rule-based qualification score (0-100) for discovered leads."""

    @staticmethod
    def calculate_score(
        phone: str | None,
        email: str | None,
        address: str | None,
        website_status: WebsiteStatus,
        has_social: bool,
        source: str | None,
    ) -> tuple[int, list[str], str]:
        """Returns (score: int, reasons: list[str], reasons_json: str)."""
        score = 0
        reasons: list[str] = []

        # 1. No official website (Prime opportunity for SRA website development!)
        if website_status == WebsiteStatus.NO_WEBSITE:
            score += 20
            reasons.append("Website missing +20")
        elif website_status == WebsiteStatus.WEBSITE_BROKEN:
            score += 15
            reasons.append("Website broken/needs revamp +15")
        elif website_status == WebsiteStatus.SOCIAL_ONLY:
            score += 15
            reasons.append("Only social page / no official domain +15")

        # 2. Phone available (High outreach potential)
        if phone:
            score += 20
            reasons.append("Phone available +20")

        # 3. Email available (Direct digital communication)
        if email:
            score += 15
            reasons.append("Email available +15")

        # 4. Physical address available (Verified physical presence)
        if address:
            score += 10
            reasons.append("Address available +10")

        # 5. Social profile available (Business actively engages online)
        if has_social:
            score += 15
            reasons.append("Social profile available +15")

        # 6. Verified data source
        if source and source != "unknown":
            score += 20
            reasons.append(f"Verified source ({source}) +20")

        final_score = min(score, 100)
        return final_score, reasons, json.dumps(reasons)

    @classmethod
    def score_business(cls, b: Business) -> tuple[int, list[str], str]:
        has_social = bool(
            b.facebook_url or b.instagram_url or b.youtube_url or b.whatsapp_url or (b.social_profiles and len(b.social_profiles) > 0)
        )
        return cls.calculate_score(
            phone=b.phone,
            email=b.email,
            address=b.address,
            website_status=b.website_status,
            has_social=has_social,
            source=b.source,
        )

    @classmethod
    def score_raw(cls, raw: RawBusiness, website_status: WebsiteStatus) -> tuple[int, list[str], str]:
        has_social = bool(raw.facebook_url or raw.instagram_url or raw.youtube_url or raw.whatsapp_url)
        return cls.calculate_score(
            phone=raw.phone,
            email=raw.email,
            address=raw.address,
            website_status=website_status,
            has_social=has_social,
            source=raw.source,
        )
