import asyncio
import json
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db import SessionLocal, get_db
from app.models.business import ScrapeJob
from app.schemas.business import ScrapeJobOut, ScrapeRequest
from app.services.jobs import execute_job
from app.workers.celery_app import celery_app

router = APIRouter(prefix="/scrape", tags=["scrape jobs"])
settings = get_settings()


def is_redis_available() -> bool:
    """Quick check if Redis broker is actively reachable within 200ms."""
    try:
        import redis
        client = redis.from_url(settings.redis_url, socket_connect_timeout=0.2, socket_timeout=0.2)
        return bool(client.ping())
    except Exception:
        return False


def run_job_sync(job_id: int):
    """Execute job in local background thread when Celery worker is offline."""
    db = SessionLocal()
    try:
        job = db.get(ScrapeJob, job_id)
        if job:
            execute_job(db, job)
    finally:
        db.close()


@router.post("", response_model=ScrapeJobOut, status_code=202)
def create_job(payload: ScrapeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    clean_cat = payload.category.strip()
    clean_loc = payload.location.strip()

    job = ScrapeJob(
        category=clean_cat,
        location=clean_loc,
        status="QUEUED",
        progress=0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Dispatch to Celery if broker reachable, otherwise run immediately in background task
    dispatched = False
    if is_redis_available():
        try:
            res = celery_app.send_task("scrape_job", args=[job.id])
            if res:
                dispatched = True
        except Exception:
            dispatched = False

    if not dispatched:
        background_tasks.add_task(run_job_sync, job.id)

    return job


@router.get("/jobs", response_model=list[ScrapeJobOut])
def list_jobs(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    return db.scalars(select(ScrapeJob).order_by(desc(ScrapeJob.created_at)).limit(limit)).all()


@router.get("/jobs/{job_id}", response_model=ScrapeJobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(ScrapeJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@router.get("/jobs/{job_id}/stream")
async def stream_job_progress(job_id: int):
    """Server-Sent Events (SSE) live progress stream for scrape jobs."""

    async def event_generator():
        last_progress = -1
        while True:
            db = SessionLocal()
            try:
                job = db.get(ScrapeJob, job_id)
                if not job:
                    yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                    break

                payload = {
                    "id": job.id,
                    "status": job.status,
                    "progress": job.progress,
                    "discovered": job.discovered,
                    "valid": job.valid,
                    "duplicates": job.duplicates,
                    "no_website": job.no_website,
                    "website_found": job.website_found,
                    "errors": job.errors,
                    "error_message": job.error_message,
                }
                yield f"data: {json.dumps(payload)}\n\n"

                if job.status in ("COMPLETED", "FAILED"):
                    break
            finally:
                db.close()

            await asyncio.sleep(0.2)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
