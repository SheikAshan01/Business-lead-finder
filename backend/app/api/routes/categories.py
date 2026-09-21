from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.business import Business, Category
from app.schemas.business import CategoryCreate, CategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    # Query categories and business count
    counts = dict(
        db.execute(
            select(Business.category_id, func.count(Business.id))
            .where(Business.category_id.is_not(None))
            .group_by(Business.category_id)
        ).all()
    )

    categories = db.scalars(select(Category).order_by(Category.name.asc())).all()
    results = []
    for cat in categories:
        results.append(
            CategoryOut(
                id=cat.id,
                name=cat.name,
                slug=cat.slug,
                enabled=cat.enabled,
                business_count=counts.get(cat.id, 0),
            )
        )
    return results


@router.post("", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    clean_name = payload.name.strip()
    slug = clean_name.lower().replace(" & ", "-").replace(" ", "-")

    existing = db.query(Category).filter(Category.name.ilike(clean_name)).first()
    if existing:
        return CategoryOut(
            id=existing.id,
            name=existing.name,
            slug=existing.slug,
            enabled=existing.enabled,
            business_count=0,
        )

    cat = Category(name=clean_name, slug=slug, enabled=True)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return CategoryOut(
        id=cat.id,
        name=cat.name,
        slug=cat.slug,
        enabled=cat.enabled,
        business_count=0,
    )
