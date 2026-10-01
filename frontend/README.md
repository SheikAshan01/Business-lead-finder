# 🚀 SRA Business Lead Finder — Frontend Portal

<div align="center">

![Next.js](https://img.shields.io/badge/Next.js-15.1-black?style=for-the-badge&logo=next.js)
![React](https://img.shields.io/badge/React-19-blue?style=for-the-badge&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?style=for-the-badge&logo=typescript)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css)
![TanStack](https://img.shields.io/badge/TanStack_Table-v8-FF4154?style=for-the-badge&logo=react-table)
![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)

**Find. Verify. Connect.** — A modern, high-performance SaaS portal for automated business discovery, qualification, and B2B outreach across Tamil Nadu.

</div>

---

## 📌 Overview

The **SRA Business Lead Finder Frontend** is an enterprise-grade web application tailored for outreach teams, digital agencies, and sales agents. It interfaces with the backend web-scraping engine to uncover commercial establishments lacking an official website, compute explainable 100-point qualification scores, and streamline customer acquisition via direct CRM workflows (WhatsApp, Email, Audit Proposals).

---

## ✨ Key Features & Modules

### 1. 📊 Executive Dashboard (`/dashboard`)
- **KPI Metrics**: Real-time counters for Total Leads, No-Website Opportunities, Valid Phone Numbers, Verified Emails, and High-Score Prospects.
- **Visual Analytics**: Interactive distribution breakdowns by category, district, and pipeline status.
- **Quick Actions**: One-click jumps to scraper jobs, export tools, and outreach funnels.

### 2. ⚡ Live Scraping Engine Controller (`/scraper`)
- **Targeted Parameters**: Select from all 38 Tamil Nadu districts and 45+ business categories or input custom queries.
- **Real-Time SSE Progress Stream**: Live Server-Sent Events monitor job status, discovered leads, valid counts, and website discovery rates in real time.
- **Source Adapters**: Interacts with OpenStreetMap (Overpass API) and Google Places data pipelines.

### 3. 📋 Lead Management & Data Grid (`/leads`)
- **High-Performance TanStack Table**: Sortable, filterable columns with multi-criteria search.
- **No-Website Opportunity Badge**: Instant visual flags for businesses with missing or invalid websites.
- **Instant Outreach**: One-click WhatsApp message triggers and mailto links.
- **Export Capabilities**: Clean CSV and formatted Excel (`.xlsx`) downloads with custom filters.

### 4. 📈 Interactive Sales Pipeline (`/pipeline`)
- **Stage Management**: Track leads through `NEW` ➔ `CONTACTED` ➔ `INTERESTED` ➔ `FOLLOW_UP` ➔ `CONVERTED` ➔ `NOT_INTERESTED`.
- **Note Threads & Activity Logs**: Record agent touchpoints and interaction history per business.

### 5. 📑 Client Audit & Pitch Proposal Modal
- **Instant Digital Audit**: Computes an automated website presence scorecard.
- **Pitch Deck Generator**: Generates customized proposal templates highlighting why the client needs a professional web presence.

### 6. 💬 Direct WhatsApp Outreach Integration
- **Zero-Friction Messaging**: Pre-filled, high-converting Tamil Nadu B2B outreach copy.
- **Phone Sanitization**: Automatically normalizes Indian phone numbers (`+91`).

### 7. 🛡️ User & Team Administration (`/admin`, `/settings`)
- **Role-Based Access Control**: `Admin` and `Agent` role differentiation.
- **Configurable Endpoints**: Easily switch between staging, local development, and production API backends.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Framework** | [Next.js 15](https://nextjs.org/) (App Router, Server & Client Components) |
| **UI Library** | [React 19](https://react.dev/) |
| **Language** | [TypeScript 5](https://www.typescriptlang.org/) (Strict typing throughout) |
| **Styling** | [Tailwind CSS 3.4](https://tailwindcss.com/) + PostCSS + clsx + tailwind-merge |
| **Data Tables** | [TanStack React Table v8](https://tanstack.com/table/v8) |
| **Async State** | [TanStack React Query v5](https://tanstack.com/query/v5) |
| **Icons** | [Lucide React](https://lucide.dev/) |
| **Validation** | [Zod v3](https://zod.dev/) |
| **Containerization** | Docker (Multi-stage Alpine Linux build) |

---

## 📁 Project Structure

```plaintext
frontend/
├── app/                              # Next.js App Router
│   ├── admin/page.tsx               # Admin user management
│   ├── categories/page.tsx          # Business category directory
│   ├── dashboard/page.tsx           # Main analytics dashboard
│   ├── jobs/page.tsx                # Background scraper jobs history
│   ├── leads/page.tsx               # Main lead directory with data grid
│   ├── locations/page.tsx           # Tamil Nadu districts & locations
│   ├── login/page.tsx               # Authentication & login screen
│   ├── pipeline/page.tsx            # CRM sales pipeline stages
│   ├── saved/page.tsx               # Bookmarked leads
│   ├── scraper/page.tsx             # Scraper trigger & live SSE monitor
│   ├── settings/page.tsx            # User and app preferences
│   ├── globals.css                  # Global styles & Tailwind layers
│   ├── layout.tsx                   # Root layout with sidebar & shell
│   └── page.tsx                     # Landing / route redirector
├── components/                       # Reusable UI components
│   ├── ClientAuditProposalModal.tsx # Proposal generator modal
│   ├── Header.tsx                   # Top navigation header
│   ├── LeadDetailsModal.tsx         # Full lead dossier modal
│   ├── Sidebar.tsx                  # Collapsible navigation sidebar
│   └── WhatsAppModal.tsx            # WhatsApp outreach composer
├── lib/                             # Core utilities and services
│   ├── api.ts                       # Typed REST API client & DTO definitions
│   └── utils.ts                     # Formatting, styling & string helpers
├── public/                          # Static assets, icons, manifest
│   ├── icon.png
│   └── manifest.json
├── Dockerfile                       # Multi-stage production container
├── next.config.ts                   # Next.js configuration
├── package.json                     # Dependencies and scripts
├── postcss.config.mjs               # PostCSS configuration
├── tailwind.config.ts               # Tailwind CSS theme configuration
└── tsconfig.json                    # TypeScript compiler settings
```

---

## ⚙️ Prerequisites

Ensure you have the following installed on your system:
- **Node.js**: `v20.x` or `v22.x` (LTS recommended) — [Download](https://nodejs.org/)
- **npm**: `v10.x` or higher
- **Git**
- **FastAPI Backend Service**: Running on `http://localhost:8000` (or your remote API URL)

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone git@github.com:SheikAshan01/Scraping-Tool.git
cd Scraping-Tool
```

### 2. Configure Environment Variables
Create a `.env.local` file in the root of the `frontend` folder:

```bash
# In Windows PowerShell:
New-Item -ItemType File -Name .env.local
```

Add your backend API endpoint:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

> [!NOTE]
> If `NEXT_PUBLIC_API_URL` is omitted, the application automatically defaults to `http://localhost:8000/api`.

### 3. Install Dependencies
```bash
npm install
```

### 4. Start the Development Server
```bash
npm run dev
```

Visit **[http://localhost:3000](http://localhost:3000)** in your browser. The application will automatically reload when you modify files.

---

## 🔑 Default Credentials

The frontend interfaces with the backend authentication system. Use the following default accounts to log in:

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@sra.com` | `admin123` | Full Access (Scraping, Admin, Settings, Outreach) |
| **Outreach Agent** | `agent@sra.com` | `agent123` | Leads Explorer, Pipeline, Notes, Exports |

---

## 📦 Available Scripts

In the project directory, you can run:

| Command | Description |
| :--- | :--- |
| `npm run dev` | Runs the Next.js app in development mode with HMR on `http://localhost:3000` |
| `npm run build` | Compiles the production application bundle with strict TypeScript verification |
| `npm start` | Starts the production server using the compiled `.next` build |
| `npm run lint` | Runs ESLint to check for code quality and syntax issues |

---

## 🐳 Running with Docker

You can containerize and run the frontend using the included multi-stage Dockerfile:

### 1. Build the Docker Image
```bash
docker build -t scraping-tool-frontend .
```

### 2. Run the Container
```bash
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://backend:8000/api scraping-tool-frontend
```

Open [http://localhost:3000](http://localhost:3000) to view the running app.

---

## 🔌 API & Backend Connectivity

The frontend communicates with the **FastAPI Backend** through typed endpoints defined in [lib/api.ts](lib/api.ts):

- `POST /api/auth/login` — Authentication & JWT bearer token issuance
- `GET /api/leads` — Paginated and filtered lead queries
- `POST /api/leads/export` — Trigger CSV/Excel file export
- `POST /api/scraper/start` — Initiate asynchronous scraping tasks
- `GET /api/scraper/stream/{job_id}` — Server-Sent Events (SSE) live progress feed
- `PATCH /api/leads/{id}/status` — Move lead between CRM stages
- `POST /api/leads/{id}/notes` — Append outreach interaction notes

---

## 👥 Authors & Maintainers

- **Developer**: Sheik Ashan ([@SheikAshan01](https://github.com/SheikAshan01))
- **Organization**: SRA Software Solutions
