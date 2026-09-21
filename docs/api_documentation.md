# SRA Business Lead Finder - REST API Documentation

Base URL: `http://localhost:8000/api`  
Interactive OpenAPI UI: `http://localhost:8000/docs`  
ReDoc UI: `http://localhost:8000/redoc`

---

## 1. Authentication (`/api/auth`)

### `POST /api/auth/login`
Authenticate admin or agent and obtain JWT bearer tokens.

**Request:**
```json
{
  "email": "admin@sra.com",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@sra.com",
    "full_name": "SRA Administrator",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-09-21T11:00:00Z"
  }
}
```

---

## 2. Businesses & Leads (`/api/businesses`)

### `GET /api/businesses`
List and filter business leads with pagination and sorting.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Records per page (default: 25, max: 100)
- `search`: Global search across name, phone, email, address, district
- `category_id`: Filter by category ID
- `district`: Filter by Tamil Nadu district (e.g. `Madurai`, `Chennai`)
- `taluk`: Filter by taluk
- `website_status`: Filter by status (`NO_WEBSITE`, `WEBSITE_FOUND`, `SOCIAL_ONLY`, `WEBSITE_BROKEN`, `WEBSITE_UNVERIFIED`)
- `email_status`: `available` or `unavailable`
- `phone_status`: `available` or `unavailable`
- `min_score` / `max_score`: Integer range between 0 and 100
- `lead_status`: `NEW`, `CONTACTED`, `INTERESTED`, `FOLLOW_UP`, `CONVERTED`, `NOT_INTERESTED`
- `saved`: Boolean filter (`true` for bookmarked leads)
- `sort_by`: `lead_score`, `created_at`, `business_name`, `district`
- `sort_order`: `desc` or `asc`

### `PATCH /api/businesses/{id}/save`
Toggle bookmark status for the lead.

### `PATCH /api/businesses/{id}/status`
Update lead qualification status and append an audit history record.

**Request:**
```json
{
  "status": "INTERESTED",
  "reason": "Owner called, requested quote for website development"
}
```

### `POST /api/businesses/{id}/notes`
Attach an internal outreach note to the lead.

---

## 3. Discovery Scraper (`/api/scrape`)

### `POST /api/scrape`
Dispatch an automated discovery job across permitted sources.

**Request:**
```json
{
  "category": "Restaurants",
  "location": "Madurai"
}
```

**Response (202 Accepted):**
```json
{
  "id": 1,
  "category": "Restaurants",
  "location": "Madurai",
  "status": "QUEUED",
  "progress": 0,
  "discovered": 0,
  "valid": 0,
  "duplicates": 0,
  "no_website": 0,
  "website_found": 0,
  "errors": 0
}
```

### `GET /api/scrape/jobs/{id}/stream`
Server-Sent Events (SSE) live progress stream updating every second.

---

## 4. Exports (`/api/export`)

- `GET /api/export/csv`: Stream CSV file with all required columns.
- `GET /api/export/excel`: Stream styled `.xlsx` workbook with auto-fitted column widths.
