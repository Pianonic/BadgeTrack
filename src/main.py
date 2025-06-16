from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Annotated
from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    IntegerField,
)
import hashlib
import urllib.parse
import time
import threading
import secrets
import os
import json

# --- Auto-generate secure key ---
SECRET_KEY = secrets.token_urlsafe(32)

# --- Database setup ---
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "visitors.db")
db = SqliteDatabase(db_path)

class UrlStats(Model):
    url = CharField(max_length=200, unique=True)
    visit_count = IntegerField(default=0)

    class Meta:
        database = db

# Initialize database
db.connect()
db.create_tables([UrlStats])

# --- FastAPI setup ---
app = FastAPI(
    docs_url=None, 
    redoc_url=None, 
    openapi_url=None,  
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if not os.path.exists(static_dir):
    # For Docker deployment, static is at the root level
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
if not os.path.exists(assets_dir):
    # For Docker deployment, assets is at the root level
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# --- Rate Limiting & Visit Tracking ---
RATE_LIMIT_WINDOW = 172800  # 48 hours (2 days)
MAX_NEW_BADGES_PER_DAY = 10  # Maximum new badges per IP per day
rate_limit_cache = {}  # {ip_hash:url -> timestamp}
visit_cache_expiry = {}  # {cache_key -> expiry_timestamp}
new_badge_cache = {}  # {ip_hash -> [timestamps]}
lock = threading.Lock()

def cleanup_expired_cache():
    """Remove expired entries from rate limit cache"""
    now = int(time.time())
    with lock:
        # Clean visit rate limit cache
        expired_keys = [key for key, expiry in visit_cache_expiry.items() if expiry < now]
        for key in expired_keys:
            rate_limit_cache.pop(key, None)
            visit_cache_expiry.pop(key, None)
        
        # Clean new badge cache
        for ip_hash in list(new_badge_cache.keys()):
            # Remove timestamps older than 24 hours
            new_badge_cache[ip_hash] = [
                timestamp for timestamp in new_badge_cache[ip_hash]
                if now - timestamp < RATE_LIMIT_WINDOW
            ]
            # Remove empty entries
            if not new_badge_cache[ip_hash]:
                del new_badge_cache[ip_hash]

def is_rate_limited(ip_hash, url):
    """Check if IP is rate limited for this URL and update cache"""
    cleanup_expired_cache()  # Clean expired entries first
    
    now = int(time.time())
    key = f"{ip_hash}:{url}"
    
    with lock:
        last = rate_limit_cache.get(key, 0)
        if now - last < RATE_LIMIT_WINDOW:
            # Reset countdown - extend the rate limit period
            rate_limit_cache[key] = now
            visit_cache_expiry[key] = now + RATE_LIMIT_WINDOW
            return True
        
        # Update cache with new timestamp and expiry
        rate_limit_cache[key] = now
        visit_cache_expiry[key] = now + RATE_LIMIT_WINDOW
        return False

def can_create_new_badge(ip_hash):
    """Check if IP can create a new badge (max 10 per day)"""
    cleanup_expired_cache()  # Clean expired entries first
    
    now = int(time.time())
    
    with lock:
        if ip_hash not in new_badge_cache:
            new_badge_cache[ip_hash] = []
        
        # Count how many new badges created in last 24 hours
        recent_creations = len(new_badge_cache[ip_hash])
        
        if recent_creations >= MAX_NEW_BADGES_PER_DAY:
            return False
        
        # Add current timestamp
        new_badge_cache[ip_hash].append(now)
        return True

def get_ip_hash(ip: str) -> str:
    return hashlib.sha256((ip + SECRET_KEY).encode()).hexdigest()

class BadgeParams(BaseModel):
    url: Annotated[str, Field(strip_whitespace=True, min_length=1, max_length=200)]
    label: Annotated[str, Field(strip_whitespace=True, min_length=1, max_length=20)] = "visits"
    color: Annotated[str, Field(strip_whitespace=True, min_length=3, max_length=10)] = "4ade80"
    style: Annotated[str, Field(strip_whitespace=True, min_length=2, max_length=10)] = "flat"
    logo: Annotated[str, Field(strip_whitespace=True, max_length=20)] = ""

@app.get("/badge")
async def badge(
    request: Request,
    url: str,
    label: str = "visits",
    color: str = "4ade80",
    style: str = "flat",
    logo: str = "",
):
    # --- Validate input ---
    try:
        params = BadgeParams(url=url, label=label, color=color, style=style, logo=logo)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid parameters.")

    # --- Get client IP (X-Forwarded-For safe) ---
    ip = (
        request.headers.get("x-forwarded-for", request.client.host)
        .split(",")[0]
        .strip()
    )
    ip_hash = get_ip_hash(ip)    # --- Rate limiting ---
    if not is_rate_limited(ip_hash, params.url):
        # Increment visit count in database
        url_stats, created = UrlStats.get_or_create(
            url=params.url,
            defaults={'visit_count': 0}
        )
        
        # If this is a new URL, check if IP can create new badges
        if created:
            if not can_create_new_badge(ip_hash):
                # Delete the newly created entry since we're rejecting it
                url_stats.delete_instance()
                raise HTTPException(
                    status_code=429, 
                    detail=f"Rate limit exceeded. Maximum {MAX_NEW_BADGES_PER_DAY} new badges per day."
                )
        
        url_stats.visit_count += 1
        url_stats.save()

    # Get current visit count
    try:
        url_stats = UrlStats.get(UrlStats.url == params.url)
        count = url_stats.visit_count
    except UrlStats.DoesNotExist:
        count = 0

    # --- Build Shields.io badge URL ---
    shields_url = (
        f"https://img.shields.io/badge/"
        f"{urllib.parse.quote(params.label)}-{count}-{params.color}.svg"
        f"?style={params.style}"
    )
    if params.logo:
        shields_url += f"&logo={urllib.parse.quote(params.logo)}"

    # --- Security headers ---
    headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",    }
    
    return RedirectResponse(shields_url, headers=headers)

# --- HTML Templates ---
@app.get("/", response_class=HTMLResponse)
async def homepage():
    """Serve the glassmorphism badge generator homepage"""
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
    if not os.path.exists(template_path):
        # For Docker deployment, templates is at the root level
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "index.html")
    
    with open(template_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/about", response_class=HTMLResponse)
async def about_page():
    """Serve the about page"""
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "about.html")
    if not os.path.exists(template_path):
        # For Docker deployment, templates is at the root level
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "about.html")
    
    with open(template_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/app-info")
async def get_app_info():
    """Get application version and environment info"""
    try:
        version_path = os.path.join(os.path.dirname(__file__), "..", "version.json")
        if not os.path.exists(version_path):
            # For Docker deployment, version.json is at the root level
            version_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "version.json")
        
        with open(version_path, "r", encoding="utf-8") as f:
            version_data = json.load(f)
        return version_data
    except FileNotFoundError:
        return {"version": "N/A", "environment": "Unknown"}
    except Exception as e:
        return {"version": "Error", "environment": "Error"}

@app.get("/api/stats/{url}")
async def get_url_stats(url: str):
    """Get the latest visit count for a URL"""
    try:
        # Validate URL parameter
        if not url or len(url) > 200:
            raise HTTPException(status_code=400, detail="Invalid URL parameter")
        
        url_stats = UrlStats.get(UrlStats.url == url)
        return {
            "url": url,
            "visit_count": url_stats.visit_count,
            "last_updated": int(time.time())
        }
    except UrlStats.DoesNotExist:
        return {
            "url": url,
            "visit_count": 0,
            "last_updated": int(time.time())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")