from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import os
import logging
import json
from .models import initialize_database, close_database
from .schemas import BadgeParams, TagStatsResponse, SystemStatsResponse
from .services import update_visit_count, get_tag_visit_count, get_system_statistics, get_app_info, load_template
from .utils import build_shields_url, get_security_headers

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting BadgeTrack application...")
    if not initialize_database():
        raise RuntimeError("Failed to initialize database")
    yield
    logger.info("Shutting down BadgeTrack application...")
    close_database()

def get_app_version():
    try:
        version_file_path = os.path.join(os.path.dirname(__file__), "..", "version.json")
        if os.path.exists(version_file_path):
            with open(version_file_path, "r", encoding="utf-8") as f:
                return json.load(f).get("version", "unknown")
        else:
            logger.warning(f"version.json not found at {version_file_path}, using 'unknown' version.")
            return "unknown"
    except Exception as e:
        logger.error(f"Error reading version.json for app version: {e}")
        return "unknown"

app = FastAPI(
    title="BadgeTrack",
    description="A reliable visit tracking service for dynamic badges",
    version=get_app_version(),
    docs_url=None, 
    redoc_url=None, 
    openapi_url=None,
    lifespan=lifespan
)

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if not os.path.exists(static_dir):
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
if not os.path.exists(assets_dir):
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

@app.get("/badge")
async def badge(
    request: Request,
    response: Response,
    tag: str,
    label: str = "visits",
    color: str = "4ade80",
    style: str = "flat",
    logo: str = "",
):
    try:
        params = BadgeParams(tag=tag, label=label, color=color, style=style, logo=logo)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid parameters.")

    cookie_id = request.cookies.get("visitor_id")

    try:
        count, was_incremented, new_cookie_id = update_visit_count(cookie_id, params.tag)
        if new_cookie_id:
            response.set_cookie(key="visitor_id", value=new_cookie_id, max_age=31536000, httponly=True, samesite="Lax")
    except ValueError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating visit count: {e}")
        count = get_tag_visit_count(params.tag)

    shields_url = build_shields_url(params.label, count, params.color, params.style, params.logo)

    headers = get_security_headers()
    return RedirectResponse(shields_url, headers=headers)

@app.get("/api/stats/{tag}", response_model=TagStatsResponse)
async def get_tag_stats_endpoint(tag: str):
    try:
        if not tag or len(tag) > 200:
            raise HTTPException(status_code=400, detail="Invalid tag parameter")
        
        count = get_tag_visit_count(tag)
        return TagStatsResponse(
            tag=tag,
            visit_count=count,
            last_updated=int(time.time())
        )
    except Exception as e:
        logger.error(f"Error getting tag stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/stats", response_model=SystemStatsResponse)
async def get_system_stats_endpoint():
    try:
        stats = get_system_statistics()
        
        return SystemStatsResponse(
            total_tracked_tags=stats["total_tracked_tags"],
            total_visits=stats["total_visits"],
            new_badges_today=stats["new_badges_today"]
        )
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving stats")

@app.get("/api/app-info")
async def get_app_info_endpoint():
    return get_app_info()

@app.get("/", response_class=HTMLResponse)
async def homepage():
    content = load_template("index.html")
    return HTMLResponse(content=content)

@app.get("/about", response_class=HTMLResponse)
async def about_page():
    content = load_template("about.html")
    return HTMLResponse(content=content)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": int(time.time())}

if __name__ == "__main__":
    os.environ["APP_ENV"] = "Development"
    logger.info(f"Running src.main directly in {os.getenv('APP_ENV')} mode (intended for local testing).")
    
    import uvicorn
    uvicorn_host = os.getenv("UVICORN_HOST", "127.0.0.1")
    uvicorn_port = int(os.getenv("UVICORN_PORT", "8000"))
    uvicorn_log_level = os.getenv("UVICORN_LOG_LEVEL", "info").lower()

    logger.info(f"Starting Uvicorn for src.main: host={uvicorn_host}, port={uvicorn_port}, log_level={uvicorn_log_level}")
    uvicorn.run(app, host=uvicorn_host, port=uvicorn_port, log_level=uvicorn_log_level)
