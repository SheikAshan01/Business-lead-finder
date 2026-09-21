from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import admin, auth, businesses, categories, dashboard, export, jobs, locations
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db import Base, engine
import app.models  # noqa: F401

# Initialize logging
configure_logging()

settings = get_settings()

# Ensure all 13 database tables are created
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="SRA Software Solutions internal business lead discovery and qualification platform. Find. Verify. Connect.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router, prefix="/api")
app.include_router(businesses.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(locations.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": settings.app_name,
        "tagline": settings.tagline,
    }
