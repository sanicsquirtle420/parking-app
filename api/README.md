# Ole Miss Parking — FastAPI Web App

A functioning web version of the campus parking system.
Backend: FastAPI + MySQL (Docker). Frontend: plain HTML/JS pages.

## Quick Start

### 1. Start the database from the repo root

From the top-level project folder:

```bash
docker compose up -d
```

On the first run, Docker automatically loads `tables2.sql` and `tables_data.sql`.
The database remains stored in the `mysql_data` Docker volume after that.

### 2. Install Python dependencies

```bash
cd api
python -m venv venv
source venv/bin/activate        # (or `venv\Scripts\activate` on Windows)
pip install -r requirements.txt
```

### 3. Seed sample account passwords once

The starter SQL includes placeholder password hashes that cannot log in. Run:

```bash
python seed_passwords.py
```

### 4. Run the API

```bash
uvicorn main:app --reload --port 8000
```

Then open **http://localhost:8000** in your browser.

## Pages

| URL | Who | What |
|---|---|---|
| `/` | Everyone | Login / signup page |
| `/map` | Everyone | Map view of all lots |
| `/admin` | Admins only | Dashboard with CRUD |

## How Login Works

1. Same login form for everyone.
2. After auth, the server returns a JWT token + the user's role.
3. The frontend stores the token in `localStorage`.
4. Based on role:
   - `admin` → redirected to `/admin`
   - anyone else → redirected to `/map`
5. Every subsequent API request sends the token in the `Authorization: Bearer ...` header.

## Test Accounts (from sample data)

The sample users have placeholder password hashes (`hashed_pw_001`, etc.) that bcrypt can't verify. To log in you'll need to either:

**Option A — Register a new account** through `/` (the signup tab).

**Option B — Seed the included test accounts.**

Run:

```bash
python seed_passwords.py
```

Then log in with one of these:

- `kdavis@olemiss.edu` / `admin123`
- `jdoe@go.olemiss.edu` / `student123`
- `jwilliams@olemiss.edu` / `faculty123`
- `smiller@gmail.com` / `visitor123`

## API Docs

FastAPI auto-generates interactive docs at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## File Structure

```
api/
├── requirements.txt    pip dependencies
├── db.py               MySQL connection helper
├── auth.py             JWT + bcrypt + FastAPI auth dependencies
├── routes_public.py    login, register, map data (no auth)
├── routes_user.py      authenticated user endpoints (rule engine, profile)
├── routes_admin.py     admin CRUD endpoints (lots, rules, permits, users)
├── main.py             FastAPI app entry — includes all routes, serves static files
├── README.md           this file
└── static/
    ├── index.html      login + signup
    ├── map.html        user map view
    └── admin.html      admin dashboard
```

## Endpoint Cheat Sheet

### Public (no auth)
- `POST /api/login` — validate credentials, return JWT
- `POST /api/register` — create new user
- `GET /api/lots` — all lots for the map
- `GET /api/lots/browse?permit_type=V` — visitor mode

### Authenticated (Bearer token)
- `GET /api/me` — profile + permits
- `GET /api/me/check-parking/{lot_id}` — YES/NO rule engine
- `GET /api/me/available-lots` — all lots the user can park at now
- `GET /api/lots/{lot_id}/rules` — full rule schedule for a lot

### Admin only (Bearer token + role=admin)
- `GET /api/admin/dashboard` — utilization overview
- `GET/POST/PUT/DELETE /api/admin/lots[/{lot_id}]` — lot CRUD
- `POST/PUT/PATCH/DELETE /api/admin/rules[/{rule_id}]` — rule CRUD
- `PUT /api/admin/lots/{lot_id}/occupancy` — update occupancy (auto-logs)
- `GET/POST/PUT/DELETE /api/admin/permits[/{permit_id}]` — permit CRUD
- `GET /api/admin/users` — list users (optional `?search=...`)
- `POST/PUT/DELETE /api/admin/user-permits[/{user_id}/{permit_id}]` — user permit CRUD
- `PUT /api/admin/bulk-renew/{permit_id}` — bulk renewal
