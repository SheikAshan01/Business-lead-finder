from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import admin, auth, businesses, categories, dashboard, export, jobs, license, locations, outreach
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
app.include_router(license.router, prefix="/api")
app.include_router(outreach.router, prefix="/api")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": settings.app_name,
        "tagline": settings.tagline,
    }


# Static Frontend Hosting (Single-Port Production Architecture)
import sys
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response


def get_frontend_dir() -> Path:
    if hasattr(sys, "_MEIPASS"):
        meipass_frontend = Path(sys._MEIPASS) / "frontend" / "out"
        if meipass_frontend.exists():
            return meipass_frontend

    candidates = [
        Path(__file__).resolve().parent.parent.parent / "frontend" / "out",
        Path(r"D:\scrap_tool\frontend\out"),
        Path(sys.executable).resolve().parent / "frontend" / "out",
    ]
    for c in candidates:
        if c.exists():
            return c
    return Path(r"D:\scrap_tool\frontend\out")


FRONTEND_DIR = get_frontend_dir()

# Mount Next.js _next assets
if (FRONTEND_DIR / "_next").exists():
    app.mount("/_next", StaticFiles(directory=str(FRONTEND_DIR / "_next")), name="next_assets")


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Pass through for API, docs, and OpenAPI endpoints
    clean_path = full_path.strip("/")
    if (
        clean_path.startswith("api")
        or clean_path.startswith("docs")
        or clean_path.startswith("redoc")
        or clean_path == "openapi.json"
    ):
        return Response(status_code=404)

    # Root request
    if not clean_path:
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)

    target_file = FRONTEND_DIR / clean_path

    # Direct static file match (e.g. icon.png, manifest.json, favicon.ico)
    if target_file.is_file():
        return FileResponse(target_file)

    # Next.js export routes (e.g. /pipeline -> pipeline.html, /leads -> leads.html)
    html_target = FRONTEND_DIR / f"{clean_path}.html"
    if html_target.is_file():
        return FileResponse(html_target)

    # Sub-directory index (e.g. /pipeline/index.html)
    sub_index = FRONTEND_DIR / clean_path / "index.html"
    if sub_index.is_file():
        return FileResponse(sub_index)

    # SPA client-side fallback
    fallback_index = FRONTEND_DIR / "index.html"
    if fallback_index.exists():
        return FileResponse(fallback_index)

    return Response(content="SRA Frontend assets not found.", status_code=404)
