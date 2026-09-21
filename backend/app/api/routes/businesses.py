import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session
from app.api.dependencies import get_optional_user
from app.db import get_db
from app.models.business import (
    Business,
    Category,
    LeadNote,
    LeadStatus,
    LeadStatusHistory,
    SavedLead,
    ScrapeJobResult,
    User,
    WebsiteStatus,
)
from app.schemas.business import (
    BulkDeleteRequest,
    BusinessCreate,
    BusinessOut,
    BusinessUpdate,
    NoteCreate,
    NoteOut,
    PaginatedBusinesses,
    StatusHistoryOut,
    StatusUpdate,
)
from app.scrapers.lead_scorer import LeadScorer
from app.scrapers.normalizer import normalize_business_name, normalize_email, normalize_phone, normalize_url

router = APIRouter(prefix="/businesses", tags=["businesses"])


def _format_business_out(b: Business) -> BusinessOut:
    category_name = b.category_rel.name if b.category_rel else None
    return BusinessOut(
        id=b.id,
        business_name=b.business_name,
        client_name=b.client_name,
        category_id=b.category_id,
        category_name=category_name,
        phone=b.phone,
        alternate_phone=b.alternate_phone,
        email=b.email,
        address=b.address,
        area=b.area,
        taluk=b.taluk,
        district=b.district,
        state=b.state,
        pincode=b.pincode,
        latitude=b.latitude,
        longitude=b.longitude,
        website_url=b.website_url,
        website_status=b.website_status,
        website_verified=b.website_verified,
        website_checked_at=b.website_checked_at,
        facebook_url=b.facebook_url,
        instagram_url=b.instagram_url,
        youtube_url=b.youtube_url,
        whatsapp_url=b.whatsapp_url,
        source=b.source,
        source_url=b.source_url,
        source_record_id=b.source_record_id,
        lead_score=b.lead_score,
        score_reasons=b.score_reasons,
        lead_status=b.lead_status,
        is_saved=b.is_saved,
        created_at=b.created_at,
        updated_at=b.updated_at,
        notes=[
            NoteOut(
                id=n.id,
                business_id=n.business_id,
                user_id=n.user_id,
                note=n.note,
                created_at=n.created_at,
            )
            for n in (b.notes or [])
        ],
        status_history=[
            StatusHistoryOut(
                id=h.id,
                old_status=h.old_status,
                new_status=h.new_status,
                reason=h.reason,
                created_at=h.created_at,
            )
            for h in (b.status_history or [])
        ],
        contacts=[],
        social_profiles=[],
    )


@router.get("", response_model=PaginatedBusinesses)
def list_businesses(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: str | None = None,
    category_id: int | None = None,
    district: str | None = None,
    taluk: str | None = None,
    website_status: WebsiteStatus | None = None,
    email_status: str | None = Query(None, pattern="^(available|unavailable)$"),
    phone_status: str | None = Query(None, pattern="^(available|unavailable)$"),
    min_score: int | None = Query(None, ge=0, le=100),
    max_score: int | None = Query(None, ge=0, le=100),
    lead_status: LeadStatus | None = None,
    saved: bool | None = None,
    sort_by: str = Query("lead_score", pattern="^(lead_score|created_at|business_name|district)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    query = select(Business)

    # 1. Search across name, phone, email, address, district
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Business.business_name.ilike(term),
                Business.phone.ilike(term),
                Business.email.ilike(term),
                Business.address.ilike(term),
                Business.district.ilike(term),
            )
        )

    # 2. Filters
    if category_id:
        query = query.where(Business.category_id == category_id)
    if district and district.strip():
        query = query.where(Business.district.ilike(f"%{district.strip()}%"))
    if taluk and taluk.strip():
        query = query.where(Business.taluk.ilike(f"%{taluk.strip()}%"))
    if website_status:
        query = query.where(Business.website_status == website_status)
    if email_status == "available":
        query = query.where(Business.email.is_not(None))
    elif email_status == "unavailable":
        query = query.where(Business.email.is_(None))
    if phone_status == "available":
        query = query.where(Business.phone.is_not(None))
    elif phone_status == "unavailable":
        query = query.where(Business.phone.is_(None))
    if min_score is not None:
        query = query.where(Business.lead_score >= min_score)
    if max_score is not None:
        query = query.where(Business.lead_score <= max_score)
    if lead_status:
        query = query.where(Business.lead_status == lead_status)
    if saved is not None:
        query = query.where(Business.is_saved == saved)

    # 3. Total count
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0

    # 4. Sorting
    col_attr = getattr(Business, sort_by, Business.lead_score)
    order_clause = col_attr.desc() if sort_order == "desc" else col_attr.asc()
    query = query.order_by(order_clause, desc(Business.id))

    # 5. Pagination
    offset = (page - 1) * page_size
    items_raw = db.scalars(query.offset(offset).limit(page_size)).all()
    items = [_format_business_out(b) for b in items_raw]
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return PaginatedBusinesses(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("", response_model=BusinessOut, status_code=201)
def create_business(payload: BusinessCreate, db: Session = Depends(get_db)):
    clean_name = normalize_business_name(payload.business_name)
    clean_phone = normalize_phone(payload.phone)
    clean_email = normalize_email(payload.email)
    clean_url = normalize_url(payload.website_url)

    web_status = WebsiteStatus.WEBSITE_FOUND if clean_url else WebsiteStatus.NO_WEBSITE
    score, reasons, reasons_json = LeadScorer.calculate_score(
        phone=clean_phone,
        email=clean_email,
        address=payload.address,
        website_status=web_status,
        has_social=bool(payload.facebook_url or payload.instagram_url or payload.whatsapp_url),
        source=payload.source or "Manual Entry",
    )

    business = Business(
        business_name=clean_name,
        client_name=payload.client_name,
        category_id=payload.category_id,
        phone=clean_phone,
        alternate_phone=normalize_phone(payload.alternate_phone),
        email=clean_email,
        address=payload.address,
        area=payload.area,
        taluk=payload.taluk,
        district=payload.district,
        state=payload.state or "Tamil Nadu",
        pincode=payload.pincode,
        website_url=clean_url,
        website_status=web_status,
        facebook_url=normalize_url(payload.facebook_url),
        instagram_url=normalize_url(payload.instagram_url),
        youtube_url=normalize_url(payload.youtube_url),
        whatsapp_url=normalize_url(payload.whatsapp_url),
        source=payload.source or "Manual Entry",
        source_url=payload.source_url,
        lead_score=score,
        score_reasons=reasons_json,
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    return _format_business_out(business)


@router.get("/{business_id}", response_model=BusinessOut)
def get_business(business_id: int, db: Session = Depends(get_db)):
    business = db.get(Business, business_id)
    if not business:
        raise HTTPException(404, "Business lead not found")
    return _format_business_out(business)


@router.patch("/{business_id}", response_model=BusinessOut)
def update_business(business_id: int, payload: BusinessUpdate, db: Session = Depends(get_db)):
    business = db.get(Business, business_id)
    if not business:
        raise HTTPException(404, "Business lead not found")

    if payload.business_name is not None:
        business.business_name = normalize_business_name(payload.business_name)
    if payload.client_name is not None:
        business.client_name = payload.client_name
    if payload.phone is not None:
        business.phone = normalize_phone(payload.phone)
    if payload.alternate_phone is not None:
        business.alternate_phone = normalize_phone(payload.alternate_phone)
    if payload.email is not None:
        business.email = normalize_email(payload.email)
    if payload.address is not None:
        business.address = payload.address
    if payload.district is not None:
        business.district = payload.district
    if payload.website_url is not None:
        business.website_url = normalize_url(payload.website_url)
        business.website_status = WebsiteStatus.WEBSITE_FOUND if business.website_url else WebsiteStatus.NO_WEBSITE
    if payload.lead_status is not None:
        business.lead_status = payload.lead_status

    # Recalculate score
    score, _, reasons_json = LeadScorer.score_business(business)
    business.lead_score = score
    business.score_reasons = reasons_json

    db.commit()
    db.refresh(business)
    return _format_business_out(business)


@router.delete("/{business_id}", status_code=204)
def delete_business(business_id: int, db: Session = Depends(get_db)):
    business = db.get(Business, business_id)
    if not business:
        raise HTTPException(404, "Business lead not found")
    # Clean foreign key link in scrape_job_results
    db.query(ScrapeJobResult).filter(ScrapeJobResult.business_id == business_id).delete(synchronize_session=False)
    db.delete(business)
    db.commit()
    return None


@router.post("/bulk-delete", status_code=200)
def bulk_delete_businesses(payload: BulkDeleteRequest, db: Session = Depends(get_db)):
    if not payload.ids:
        return {"deleted": 0}
    # Clean foreign key link in scrape_job_results
    db.query(ScrapeJobResult).filter(ScrapeJobResult.business_id.in_(payload.ids)).delete(synchronize_session=False)
    deleted_count = 0
    for bid in payload.ids:
        b = db.get(Business, bid)
        if b:
            db.delete(b)
            deleted_count += 1
    db.commit()
    return {"deleted": deleted_count}


@router.patch("/{business_id}/save", response_model=BusinessOut)
def toggle_save_business(
    business_id: int,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    business = db.get(Business, business_id)
    if not business:
        raise HTTPException(404, "Business lead not found")

    business.is_saved = not business.is_saved

    user_id = current_user.id if current_user else None
    if business.is_saved:
        # Record into saved_leads table
        existing_saved = db.query(SavedLead).filter(
            SavedLead.business_id == business.id,
            SavedLead.user_id == user_id,
        ).first()
        if not existing_saved:
            db.add(SavedLead(business_id=business.id, user_id=user_id))
    else:
        # Remove from saved_leads table
        db.query(SavedLead).filter(
            SavedLead.business_id == business.id,
            SavedLead.user_id == user_id,
        ).delete()

    db.commit()
    db.refresh(business)
    return _format_business_out(business)


@router.patch("/{business_id}/status", response_model=BusinessOut)
def update_status(
    business_id: int,
    payload: StatusUpdate,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    business = db.get(Business, business_id)
    if not business:
        raise HTTPException(404, "Business lead not found")

    old_status = business.lead_status.value if hasattr(business.lead_status, "value") else str(business.lead_status)
    new_status = payload.status.value if hasattr(payload.status, "value") else str(payload.status)

    business.lead_status = payload.status

    # Record into lead_status_history
    history = LeadStatusHistory(
        business_id=business.id,
        user_id=current_user.id if current_user else None,
        old_status=old_status,
        new_status=new_status,
        reason=payload.reason,
    )
    db.add(history)
    db.commit()
    db.refresh(business)
    return _format_business_out(business)


@router.post("/{business_id}/notes", response_model=NoteOut, status_code=201)
def add_note(
    business_id: int,
    payload: NoteCreate,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    business = db.get(Business, business_id)
    if not business:
        raise HTTPException(404, "Business lead not found")

    note = LeadNote(
        business_id=business_id,
        user_id=current_user.id if current_user else None,
        note=payload.note.strip(),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return NoteOut(
        id=note.id,
        business_id=note.business_id,
        user_id=note.user_id,
        note=note.note,
        created_at=note.created_at,
    )


@router.get("/{business_id}/notes", response_model=list[NoteOut])
def get_notes(business_id: int, db: Session = Depends(get_db)):
    if not db.get(Business, business_id):
        raise HTTPException(404, "Business lead not found")
    notes = db.query(LeadNote).filter(LeadNote.business_id == business_id).order_by(desc(LeadNote.created_at)).all()
    return [
        NoteOut(
            id=n.id,
            business_id=n.business_id,
            user_id=n.user_id,
            note=n.note,
            created_at=n.created_at,
        )
        for n in notes
    ]
