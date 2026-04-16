"""
api/main.py
===========
FastAPI entry point. Ties together all the routes and serves the
static HTML files.

RUN IT:
  cd api
  pip install -r requirements.txt
  uvicorn main:app --reload --port 8000

Then open: http://localhost:8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from routes_public import router as public_router
from routes_user import router as user_router
from routes_admin import router as admin_router


app = FastAPI(
    title="Ole Miss Campus Parking API",
    description="Backend for the Ole Miss parking app — students, faculty, visitors, and admins.",
    version="1.0.0",
)

# CORS — allow any origin for development. Lock this down in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(public_router, tags=["public"])
app.include_router(user_router, tags=["user"])
app.include_router(admin_router, tags=["admin"])


# Serve static HTML pages
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root():
    """Landing page — login form."""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/map")
def map_page():
    """User map view."""
    return FileResponse(os.path.join(STATIC_DIR, "map.html"))


@app.get("/admin")
def admin_page():
    """Admin dashboard."""
    return FileResponse(os.path.join(STATIC_DIR, "admin.html"))


@app.get("/health")
def health():
    """Quick ping to check the API is up."""
    return {"status": "ok"}
