from fastapi import APIRouter, Depends, Query
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.business import Business, Location

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/districts")
def list_districts(db: Session = Depends(get_db)):
    """Return all 38 Tamil Nadu districts along with count of discovered businesses."""
    # Count businesses per district
    business_counts = dict(
        db.execute(
            select(Business.district, func.count(Business.id))
            .where(Business.district.is_not(None))
            .group_by(Business.district)
        ).all()
    )

    districts = db.scalars(
        select(distinct(Location.district))
        .where(Location.state == "Tamil Nadu")
        .order_by(Location.district.asc())
    ).all()

    return [
        {
            "district": d,
            "business_count": business_counts.get(d, 0),
        }
        for d in districts
    ]


@router.get("/taluks")
def list_taluks(district: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    """Return taluks for a specific district."""
    taluks = db.scalars(
        select(distinct(Location.taluk))
        .where(Location.district.ilike(district.strip()), Location.taluk.is_not(None))
        .order_by(Location.taluk.asc())
    ).all()
    return [{"district": district, "taluk": t} for t in taluks]


@router.get("")
def list_all_locations(db: Session = Depends(get_db)):
    """Return all location records."""
    locs = db.scalars(select(Location).order_by(Location.district.asc(), Location.taluk.asc())).all()
    return [
        {
            "id": l.id,
            "state": l.state,
            "district": l.district,
            "taluk": l.taluk,
            "area": l.area,
            "pincode": l.pincode,
        }
        for l in locs
    ]
