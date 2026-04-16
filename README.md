# Ole Miss Campus Parking App — CSCI 387

A campus parking availability + management system for the University of Mississippi.
Two frontends share one MySQL database:

1. **Kivy desktop app** (`database/` — teammate's work) — the primary Milestone 3 deliverable.
2. **FastAPI web app** (`api/` — Jannatul's portfolio extension) — same backend logic exposed as a REST API with an HTML frontend.

Both apps talk to the same `parking_db` MySQL schema running in Docker.

## Prerequisites

- **VS Code** (recommended)
- **Docker Desktop** (for MySQL 8.0)
- **Python 3.10+**
- **Git**

## One-Time Setup

### 1. Clone the repo and open it in VS Code

```bash
git clone <repo-url>
cd olemiss-parking-github
code .
```

If `code .` does not work, open VS Code manually and choose **File → Open Folder**.

### 2. Start the database with Docker Compose

Port 3307 is used because many laptops already have MySQL on 3306.
From the project root, run:

```bash
docker compose up -d
```

This will:

- start a MySQL 8.0 container named `olemiss-parking`
- create the `parking_db` database
- automatically load `tables2.sql` and `tables_data.sql` on the first run
- keep database data in a Docker volume named `mysql_data`

Check that the container is running:

```bash
docker compose ps
```

On later days, teammates can just run:

```bash
docker compose up -d
```

If someone wants to fully reset the database and reload the starter SQL from scratch:

```bash
docker compose down -v
docker compose up -d
```

### 3. Set up the Python environment

In VS Code, open the integrated terminal in the repo root and run:

```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Seed usable passwords for the sample accounts

The starter data includes placeholder password hashes like `hashed_pw_001`, which
cannot be used for login. Run this once after the database is initialized:

```bash
cd api
source venv/bin/activate
python seed_passwords.py
cd ..
```

Test accounts after seeding:

| Email | Password | Role |
|---|---|---|
| kdavis@olemiss.edu | admin123 | admin |
| jdoe@go.olemiss.edu | student123 | student |
| jwilliams@olemiss.edu | faculty123 | faculty |
| smiller@gmail.com | visitor123 | visitor |

### 5. Run the web app

```bash
cd api
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

Then open <http://localhost:8000>.

## Running the Apps

### FastAPI Web App

```bash
cd api
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

Then open <http://localhost:8000>.

- `/` — login / signup
- `/map` — lot availability (students, faculty, visitors)
- `/admin` — full CRUD dashboard (admins only)
- `/docs` — auto-generated interactive API docs

### Kivy Desktop App

See `database/queries/` for the teammate's Kivy-side queries. Run instructions
are in that folder's own README (or wherever the Kivy entry point lives).

## Repository Layout

```
387_project/
├── README.md              ← you are here
├── .gitignore
│
├── tables2.sql            schema (parking_lots, permits, rules, users, ...)
├── tables_data.sql        sample data
│
├── admin_views.sql        5 SQL views powering dashboards
├── admin_queries.sql      8 admin read queries mapped to user stories
├── user_engine.sql        rule-engine + profile queries
├── crud_operations.sql    INSERT/UPDATE/DELETE templates
│
├── *.csv                  exports for analytics (Power BI / Tableau)
├── *.pdf                  milestone deliverables
│
├── database/              teammate's Kivy-app queries (Python)
│   └── queries/
│       └── users.py       bcrypt-backed user CRUD
│
├── backend/               standalone Python backend scripts (pre-FastAPI)
│   ├── db_connection.py
│   ├── admin_dashboard.py
│   ├── admin_lot_operations.py
│   ├── admin_permit_operations.py
│   └── user_operations.py
│
└── api/                   FastAPI web application
    ├── README.md          detailed web-app docs
    ├── requirements.txt
    ├── db.py              MySQL connection helper
    ├── auth.py            JWT + bcrypt + FastAPI dependencies
    ├── routes_public.py   login, register, public map data
    ├── routes_user.py     authenticated user endpoints
    ├── routes_admin.py    admin CRUD endpoints
    ├── main.py            FastAPI entry + static file serving
    ├── seed_passwords.py  one-time test-account password seeder
    └── static/
        ├── index.html     login / signup
        ├── map.html       user map view
        └── admin.html     admin dashboard
```

## Tech Stack

| Layer | Tech |
|---|---|
| Database | MySQL 8.0 (Docker) |
| Backend (web) | FastAPI, Pydantic, mysql-connector-python |
| Auth | JWT (PyJWT) + bcrypt |
| Frontend (web) | HTML / CSS / vanilla JS |
| Frontend (desktop) | Kivy |

## Troubleshooting

**`docker compose up -d` fails** — make sure Docker Desktop is installed and open.

**Port 3307 already in use** — change the port mapping in `docker-compose.yml`,
then update the port in `api/db.py`, `api/seed_passwords.py`, and any README commands.

**`python: command not found`** — on macOS use `python3`.

**`email-validator is not installed`** — `pip install email-validator` (already
in `requirements.txt` but if you installed before it was added, reinstall).

**Login fails with sample credentials** — you need to run `seed_passwords.py` once;
the sample data has placeholder hashes that bcrypt can't verify.

**Admin dashboard looks stale after changes** — hard-refresh the browser with
Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux). The static HTML is cached.

**A teammate pulled the repo but still sees old database data** — Docker volumes
persist between runs. Reset with:

```bash
docker compose down -v
docker compose up -d
```

## Team

CSCI 387 — Spring 2026 · University of Mississippi
