from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session
from app.api.dependencies import require_admin
from app.db import get_db
from app.models.business import AuditLog, Business, Category, Location, ScrapeJob, Source, User
from app.schemas.auth import UserOut
from app.schemas.business import SourceOut

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/sources", response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db)):
    return db.scalars(select(Source).order_by(Source.id.asc())).all()


@router.patch("/sources/{source_id}/toggle", response_model=SourceOut)
def toggle_source(source_id: int, db: Session = Depends(get_db)):
    source = db.get(Source, source_id)
    if not source:
        raise HTTPException(404, "Source not found")
    source.enabled = not source.enabled
    db.commit()
    db.refresh(source)
    return source


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.id.asc())).all()


@router.patch("/users/{user_id}/toggle-active")
def toggle_user_active(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    user.is_active = not user.is_active
    db.commit()
    return {"id": user.id, "is_active": user.is_active}


@router.get("/logs")
def list_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.scalars(select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit)).all()
    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "details": l.details,
            "created_at": l.created_at,
        }
        for l in logs
    ]


@router.get("/system-stats")
def get_system_stats(db: Session = Depends(get_db)):
    users_count = db.scalar(select(func.count(User.id))) or 0
    categories_count = db.scalar(select(func.count(Category.id))) or 0
    locations_count = db.scalar(select(func.count(Location.id))) or 0
    businesses_count = db.scalar(select(func.count(Business.id))) or 0
    jobs_count = db.scalar(select(func.count(ScrapeJob.id))) or 0
    sources_count = db.scalar(select(func.count(Source.id))) or 0

    return {
        "users_count": users_count,
        "categories_count": categories_count,
        "locations_count": locations_count,
        "businesses_count": businesses_count,
        "jobs_count": jobs_count,
        "sources_count": sources_count,
        "status": "operational",
    }
