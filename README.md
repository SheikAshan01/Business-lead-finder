# SRA Business Lead Finder

**Find. Verify. Connect.**

An internal business discovery and qualification platform built for **SRA Software Solutions**. The system targets commercial establishments across **Tamil Nadu**, identifies businesses lacking an official website, validates and normalizes contact details, detects duplicates using RapidFuzz, computes an explainable 100-point qualification score, and equips agents with a modern SaaS dashboard.

---

## Key Features

1. **Targeted Tamil Nadu Discovery**: Hierarchical coverage across all 38 districts with 45+ business categories and custom category/location input.
2. **Modular Source Adapters**: Live OpenStreetMap Overpass API adapter and Google Places API interface with plug-and-play architecture.
3. **No-Website Opportunity Detection**: Asynchronously verifies whether a business has an official website or only social media pages (Facebook, Instagram, Justdial) to prioritize digital acquisition.
4. **Data Normalization & Zero-Hallucination**: Standardizes Indian phone numbers (+91, 10-digit mobile) and validates emails without fabricating missing information.
5. **Fuzzy Deduplication (RapidFuzz)**: Identifies duplicates via exact phone/email matching and fuzzy token similarity on business names and addresses.
6. **100-Point Explainable Qualification Score**: Transparent scoring formula with clear point breakdowns.
7. **Next.js SaaS Dashboard**: Built with TypeScript, Tailwind CSS, TanStack Table, responsive KPI metrics, and live distribution charts.
8. **CRM Outreach Features**: Status tracking (`NEW`, `CONTACTED`, `INTERESTED`, `FOLLOW_UP`, `CONVERTED`, `NOT_INTERESTED`), note threads, and audit history.
9. **One-Click Exports**: Formatted CSV and styled Excel (`.xlsx`) downloads supporting selective, filtered, and no-website exports.
10. **Live Job Progress**: Real-time Server-Sent Events (SSE) stream displaying discovered, valid, duplicate, and website counters.

---

## Architecture Overview

- **Frontend**: Next.js 15+ (App Router), TypeScript, Tailwind CSS, TanStack Table, Lucide Icons.
- **Backend**: FastAPI (Python 3.12+), SQLAlchemy 2, Pydantic v2, Alembic, PostgreSQL / SQLite fallback.
- **Background Engine**: Celery worker, Redis broker, httpx async website prober.
- **Deduplication**: RapidFuzz fuzzy token-sort similarity.

---

## Quick Start (Local Development)

### 1. One-Click Launcher (PowerShell)

Run the automated development script from the project root:

```powershell
.\scripts\run_dev.ps1
```

This script will automatically:
- Create database tables and seed all 38 Tamil Nadu districts, 46 categories, and default users.
- Start the FastAPI backend on [http://localhost:8000](http://localhost:8000).
- Launch the Next.js frontend on [http://localhost:3000](http://localhost:3000).

### 2. Manual Setup Without Docker

#### Backend:
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python ..\scripts\seed_tamil_nadu.py
uvicorn app.main:app --reload --port 8000
```

#### Frontend:
```powershell
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Default Credentials

| Account | Email | Password | Role |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@sra.com` | `admin123` | Admin |
| **Outreach Agent** | `agent@sra.com` | `agent123` | Agent |

---

## Run with Docker

```bash
docker compose up --build
```

Services initialized:
- `frontend`: Next.js application on port 3000
- `backend`: FastAPI REST API on port 8000
- `postgres`: PostgreSQL 16 database on port 5432
- `redis`: Redis message queue on port 6379
- `worker`: Celery background scraping worker

---

## Testing

Run the comprehensive pytest suite covering normalization, deduplication, website detection, lead scoring, and API routes:

```powershell
cd backend
..\.venv\Scripts\pytest.exe -v
```

Frontend build and type verification:

```powershell
cd frontend
npm run build
```

---

## Documentation

- System Architecture & ER Diagram: [docs/architecture.md](docs/architecture.md)
- REST API Documentation: [docs/api_documentation.md](docs/api_documentation.md)
- OpenAPI Interactive UI: [http://localhost:8000/docs](http://localhost:8000/docs)
# Business-lead-finder
