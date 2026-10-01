# IP-SAKTI Sahayak

IP-SAKTI Sahayak is an evidence-grounded information tool for exploring intellectual-property and regulatory materials relevant to Ayurveda, traditional knowledge, biodiversity, and access-and-benefit sharing.

## Problem

Legal and regulatory research can require tracing a question across multiple acts, rules, and source sections. Unsupported summaries and fabricated citations can make that research harder to verify.

## Solution

The application indexes a local source corpus, retrieves relevant sections, maps answer claims to source chunk IDs, validates citations, and can abstain when sufficient evidence is unavailable. It is informational decision support, not legal advice or a substitute for qualified counsel.

The repository is not affiliated with, certified by, or endorsed by any government agency. It does not provide live government-portal search or access to restricted TKDL formulation records.

## Architecture

```text
React/Vite frontend
    -> FastAPI REST API
        -> SQLAlchemy async database session
        -> source/document retrieval
        -> answer generation and citation validation
        -> PostgreSQL in production; SQLite for local development only
```

At startup, the backend initializes SQLAlchemy tables and loads the configured source manifest and corpus documents. The current schema initialization uses `create_all`; there is no versioned migration system.

## Technologies

- Frontend: React, Vite, Tailwind CSS, lucide-react
- Backend: Python, FastAPI, Pydantic Settings, SQLAlchemy async
- Database: PostgreSQL via `asyncpg` in production; SQLite fallback for local development
- Tests: pytest and pytest-asyncio

## Repository Structure

```text
backend/app/       FastAPI routes, settings, database, models, schemas, services
frontend/          React application, API client, Vite configuration
knowledge_base/    Source documents organized by jurisdiction
research/          Source manifest and research material
tests/             Backend tests
docs/              Project documentation
```

## Local Development

Prerequisites: Python 3.11 or newer and Node.js 18 or newer.

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
$env:PYTHONPATH = "backend"
python -m uvicorn app.main:app --reload --port 8000
```

In another terminal:

```powershell
cd frontend
npm ci
npm run dev
```

The Vite development server proxies `/api` to the local FastAPI server. With no database variables set in development, the backend uses its local SQLite database. To use PostgreSQL locally, set `DATABASE_URL` or all five `POSTGRES_*` variables in the backend environment.

Run tests from the repository root:

```powershell
$env:PYTHONPATH = "backend"
python -m pytest -q
```

Build the frontend from `frontend/` with `npm run build`.

## Environment Variable Names

The root `.env.example` lists backend variable names only. Provide actual values through a protected local `.env` or the backend hosting platform's secret/environment settings.

Backend settings include:

- `ENVIRONMENT`, `LOG_LEVEL`, `DEMO_MODE`, `CONFIDENTIAL_MODE_DEFAULT`
- `DATABASE_URL` or `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`
- `FRONTEND_URL` or `ALLOWED_ORIGINS`
- `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`
- `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSION`
- `TRANSLATION_PROVIDER`, `BHASHINI_API_KEY`, `BHASHINI_USER_ID`, `BHASHINI_PIPELINE_ID`
- `RETRIEVAL_TOP_K`, `RERANK_TOP_K`, `MIN_EVIDENCE_SCORE`, `ABSTAIN_ON_LOW_CONFIDENCE`

The only frontend variable in `frontend/.env.example` is `VITE_API_BASE_URL`, the deployed backend's HTTPS origin. Vite variables are public in the browser bundle. Never put database credentials or provider API keys in a `VITE_*` variable.

## Production Deployment

### Backend

- Configure `ENVIRONMENT` for production, disable `DEMO_MODE`, provide a reachable PostgreSQL `DATABASE_URL` (or all five `POSTGRES_*` settings), and set `FRONTEND_URL` to the deployed frontend origin.
- Production refuses missing PostgreSQL configuration, invalid production database schemes, missing CORS origins, and PostgreSQL initialization failures. It does not fall back to SQLite.
- Run the service with the repository root as its working directory, install with `python -m pip install -r backend/requirements.txt`, set `PYTHONPATH=backend`, and start with `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Startup creates missing tables, but `create_all` does not migrate existing schemas. Back up and migrate databases deliberately when the schema changes.

### Frontend on Vercel

- Set the Vercel project root directory to `frontend`; use `npm run build` with `dist` as the output directory.
- Configure `VITE_API_BASE_URL` to the actual deployed backend HTTPS origin. The production frontend rejects missing, localhost, non-HTTPS API origins.
- Configure `FRONTEND_URL` on the backend with the actual Vercel origin. No Vercel URL is assumed by this repository.
- If using `ALLOWED_ORIGINS` instead of `FRONTEND_URL`, provide a JSON array of exact HTTPS origins.
- Keep backend credentials and provider secrets exclusively in backend environment settings.

### Current Integration Status

The assistant route currently instantiates mock LLM, translation, and embedding providers. The `LLM_PROVIDER`, `LLM_API_KEY`, and translation settings do not wire a live provider into this route. Do not represent the assistant as a live generative service until a real provider integration is implemented and validated. Source portal scraping and restricted TKDL access are not implemented.

## Evidence, Citations, and Abstention

Assistant responses include claims and citations mapped to retrieved source chunk IDs. The citation validator checks that cited chunks are present in the retrieved evidence. When the corpus does not provide sufficient evidence, the response can return `insufficient_evidence` rather than inventing support. Source links and corpus verification metadata are informational; this application does not certify source currency or provide legal advice.
