from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.business import Business, Category, LeadStatus, WebsiteStatus
from app.schemas.business import ChartItem, DashboardCharts, DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def stats(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count(Business.id))) or 0
    no_website = db.scalar(select(func.count(Business.id)).where(Business.website_status == WebsiteStatus.NO_WEBSITE)) or 0
    website = db.scalar(select(func.count(Business.id)).where(Business.website_status == WebsiteStatus.WEBSITE_FOUND)) or 0
    saved = db.scalar(select(func.count(Business.id)).where(Business.is_saved.is_(True))) or 0
    converted = db.scalar(select(func.count(Business.id)).where(Business.lead_status == LeadStatus.CONVERTED)) or 0
    phone = db.scalar(select(func.count(Business.id)).where(Business.phone.is_not(None))) or 0
    email = db.scalar(select(func.count(Business.id)).where(Business.email.is_not(None))) or 0
    high_score = db.scalar(select(func.count(Business.id)).where(Business.lead_score >= 75)) or 0

    return DashboardStats(
        total=total,
        no_website=no_website,
        website_found=website,
        saved=saved,
        converted=converted,
        phone=phone,
        email=email,
        high_score=high_score,
    )


@router.get("/charts", response_model=DashboardCharts)
def charts(db: Session = Depends(get_db)):
    # 1. Businesses by Category
    cat_rows = db.execute(
        select(Category.name, func.count(Business.id))
        .join(Category, Business.category_id == Category.id)
        .group_by(Category.name)
        .order_by(desc(func.count(Business.id)))
        .limit(6)
    ).all()
    by_category = [ChartItem(label=r[0], count=r[1]) for r in cat_rows]

    # 2. Businesses by District
    dist_rows = db.execute(
        select(Business.district, func.count(Business.id))
        .where(Business.district.is_not(None))
        .group_by(Business.district)
        .order_by(desc(func.count(Business.id)))
        .limit(6)
    ).all()
    by_district = [ChartItem(label=r[0], count=r[1]) for r in dist_rows]

    # 3. No Website by District
    no_web_dist_rows = db.execute(
        select(Business.district, func.count(Business.id))
        .where(Business.district.is_not(None), Business.website_status == WebsiteStatus.NO_WEBSITE)
        .group_by(Business.district)
        .order_by(desc(func.count(Business.id)))
        .limit(6)
    ).all()
    no_website_by_district = [ChartItem(label=r[0], count=r[1]) for r in no_web_dist_rows]

    # 4. Lead Status Distribution
    status_rows = db.execute(
        select(Business.lead_status, func.count(Business.id))
        .group_by(Business.lead_status)
        .order_by(desc(func.count(Business.id)))
    ).all()
    status_distribution = [
        ChartItem(
            label=r[0].value if hasattr(r[0], "value") else str(r[0]),
            count=r[1],
        )
        for r in status_rows
    ]

    return DashboardCharts(
        by_category=by_category,
        by_district=by_district,
        no_website_by_district=no_website_by_district,
        status_distribution=status_distribution,
    )
