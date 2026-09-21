from celery import Celery
from app.core.config import get_settings
from app.db import SessionLocal
from app.models.business import ScrapeJob
from app.services.jobs import execute_job

settings = get_settings()
celery_app = Celery("sra_lead_finder", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    broker_connection_retry_on_startup=False,
    broker_connection_max_retries=1,
    result_backend_max_retries=1,
    redis_socket_connect_timeout=0.5,
    redis_socket_timeout=0.5,
    redis_retry_on_timeout=False,
)


@celery_app.task(name="scrape_job", bind=True)
def scrape_job(self, job_id: int) -> dict:
    """Execute background scraping discovery job via Celery worker."""
    db = SessionLocal()
    try:
        job = db.get(ScrapeJob, job_id)
        if not job:
            return {"status": "error", "message": f"Job #{job_id} not found"}
        execute_job(db, job)
        return {
            "status": job.status,
            "discovered": job.discovered,
            "valid": job.valid,
            "duplicates": job.duplicates,
            "no_website": job.no_website,
            "website_found": job.website_found,
            "errors": job.errors,
        }
    finally:
        db.close()
