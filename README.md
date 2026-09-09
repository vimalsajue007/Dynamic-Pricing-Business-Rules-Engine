# Dynamic Pricing & Business Rules Engine

A full-stack platform that lets administrators define pricing rules —
customer type, quantity, category, location, dates, promo codes — as
**data**, not code. The pricing calculation itself lives in one reusable
engine (`backend/app/services/pricing_engine.py`) that is completely
independent of the API layer, so it's testable in isolation and callable
from anywhere (routes, background jobs, scripts).

```
Base Price → Applicable Rules → Discounts → Additional Charges → Tax → Final Price
```

## Stack

| Layer      | Tech |
|------------|------|
| Backend    | Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, Redis, JWT |
| Frontend   | React 18, Vite, TypeScript, MUI 6, Chart.js, Axios, React Router |
| Database   | MySQL 8.0 |
| Infra      | Docker & Docker Compose |



## Quick start (Docker — recommended)

```bash
cp backend/.env.example backend/.env

docker compose up --build
```

- API: http://localhost:8000 (Swagger docs at **/docs**, ReDoc at **/redoc**)
- Frontend: http://localhost:5173
- MySQL: exposed on host port **3307** (container port 3306)
- Redis: exposed on host port **6380**

Alembic migrations run automatically on backend container start
(`alembic upgrade head`, see `backend/Dockerfile`).

To load demo data (an admin account, sample products/customers/rules/promo):

```bash
docker compose exec backend python seed_data.py
```

This creates login `admin@example.com` / `Admin@12345`. **The very first
user to register through `/api/v1/auth/register` also automatically
becomes an admin** — you don't have to use the seed script.

## Running locally without Docker

### Backend

```bash
cd backend
python -m venv .venv 
Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  

alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000/api/v1
npm run dev
```

### Running the tests

```bash
cd backend
pytest -v
```

The test suite exercises the pricing engine directly — AND/OR condition
logic, priority ordering, exclusive vs. stackable rules, per-action and
global discount caps, date windows, and promo code validation — without
needing a database connection.

## Windows notes

This project is regularly built and run on Windows 11 / PowerShell. A few
things that tend to trip people up there, already addressed in this
codebase:

- **`%` in a MySQL password**: the DSN is built from separate env vars and
  URL-encoded in code (`app/core/config.py`), so a literal `%` in
  `MYSQL_PASSWORD` won't break the connection string.
- **Docker hostnames vs. `localhost`**: inside `docker-compose.yml`,
  `MYSQL_HOST=db` and `REDIS_HOST=redis` (service names). If you run the
  backend outside Docker against a Dockerized DB, set `MYSQL_HOST=localhost`
  and `MYSQL_PORT=3307` (the mapped host port) in your local `.env`.
  instead.
- **Auth**: this project uses a single `Authorization: Bearer <token>`
  header (HTTPBearer-style) everywhere — no Swagger OAuth2 password-flow
  mismatch to fight with. Paste the access token straight into the
  Swagger "Authorize" dialog.
- **Email validation**: `EmailStr` fields rely on `email-validator`
  (pinned in `requirements.txt`) rather than a hand-rolled regex.

## How the pricing engine resolves conflicting rules

Rules are evaluated in ascending `priority` order (lower number = higher
priority):

1. Each rule's `condition_logic` (`AND`/`OR`) decides whether **all** or
   **any** of its conditions must match.
2. A rule with **no conditions** always matches (useful for a blanket/
   default action).
3. If a rule is flagged **exclusive**, no further (lower-priority) rules
   are evaluated once it matches — a hard stop.
4. If a rule is flagged **non-stackable**, it only applies when nothing
   else has applied yet in this calculation; otherwise it's skipped.
   Stackable rules (the default) simply combine.
5. The combined discount from all matched rules is capped at
   `MAX_TOTAL_DISCOUNT_PERCENT` (default 60%) of the subtotal, so pricing
   is always predictable and never goes negative.
6. Promo codes are validated and applied **after** rule discounts, against
   the post-rule-discount subtotal, respecting minimum purchase, maximum
   discount, usage limits, and the active date window.
7. Tax is calculated last, on the taxable amount after both rule and
   promo discounts.

Rule Testing (`/testing` in the UI, `POST /api/v1/pricing/test` in the
API) runs this exact same logic without persisting anything, so admins
can validate a rule before flipping it active.

## Key API endpoints

All endpoints are namespaced under `/api/v1`. Full interactive docs are
at `/docs`.

| Method | Path                     | Notes |
|--------|--------------------------|-------|
| POST   | `/auth/register`          | first user becomes admin |
| POST   | `/auth/login`              | returns access + refresh tokens |
| POST   | `/auth/refresh`            | |
| GET    | `/auth/me`                  | |
| GET/POST/PUT/DELETE | `/products`, `/categories`, `/customers` | admin-only writes, search/filter/pagination on GET |
| GET/POST/PUT/DELETE | `/pricing-rules`         | conditions + actions nested in one payload |
| GET/POST/PUT/DELETE | `/promotions`             | |
| POST   | `/pricing/preview`         | calculates **and persists** to history |
| POST   | `/pricing/test`             | calculates **without** persisting — shows matched/non-matched rules |
| GET    | `/pricing/history`          | paginated, filterable by product/customer |
| GET    | `/dashboard/summary`        | totals, most-applied rules, 14-day activity trend (Redis-cached, 60s) |

## Postman

Import `postman_collection.json`. It uses a collection variable
`{{base_url}}` (default `http://localhost:8000/api/v1`) and
`{{access_token}}`, which the login request auto-populates via a small
test script.

## Deliverables checklist

- [x] Complete FastAPI backend, layered (core / models / schemas / api / services)
- [x] Complete React + TypeScript frontend (violet MUI theme)
- [x] MySQL schema via SQLAlchemy models
- [x] Alembic migration (initial schema)
- [x] Redis caching (dashboard summary; invalidated on writes)
- [x] Docker & Docker Compose (db, redis, backend, frontend)
- [x] Swagger / ReDoc API docs (built into FastAPI)
- [x] Postman collection
- [x] Unit tests for the pricing engine (12 tests, run with `pytest`)
- [x] README with setup instructions
- [x] `.env.example` (backend and frontend)
