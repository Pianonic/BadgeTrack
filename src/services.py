from typing import Tuple
from peewee import fn
from .models import db, IpHash, Badge, Visit
from .rate_limiter import is_visit_allowed
import time
import os
import json
import logging

logger = logging.getLogger(__name__)

def update_visit_count(ip_hash_str: str, url_str: str) -> Tuple[int, bool]:
    """Update visit count for a URL and IP combination"""
    current_time = int(time.time())
    
    try:
        with db.atomic():
            # Get or create IP hash record
            ip_hash, _ = IpHash.get_or_create(hash=ip_hash_str)
            
            # Get or create badge record
            badge, badge_created = Badge.get_or_create(
                url=url_str,
                defaults={'created': current_time}
            )
            
            # Check if visit is allowed (rate limiting)
            if is_visit_allowed(ip_hash_str, url_str):
                # Get or create visit record for this IP-Badge combination
                visit, visit_created = Visit.get_or_create(
                    ip_hash=ip_hash,
                    badge=badge,
                    defaults={'last_visit': current_time}
                )
                
                # Only increment if this is a new visit or enough time has passed
                if visit_created or (current_time - visit.last_visit >= int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "172800"))):
                    visit.last_visit = current_time
                    visit.save()
                    
                    badge.visits += 1
                    badge.save()
                    
                    return badge.visits, True
            
            # Visit not allowed or not enough time passed, return current count
            return badge.visits, False
                
    except Exception as e:
        logger.error(f"Error updating visit count: {e}")
        # Try to get current count even if update failed
        try:
            badge = Badge.get(Badge.url == url_str)
            return badge.visits, False
        except Badge.DoesNotExist:
            return 0, False

def get_url_visit_count(url_str: str) -> int:
    """Get total visit count for a URL"""
    try:
        badge = Badge.get(Badge.url == url_str)
        return badge.visits
    except Badge.DoesNotExist:
        return 0

def get_system_statistics() -> dict:
    """Get system-wide statistics"""
    try:
        total_urls = Badge.select().count()
        total_visits = Badge.select(fn.SUM(Badge.visits)).scalar() or 0
        
        # Count badges created in last 24 hours
        day_ago = int(time.time()) - 86400
        recent_badges = Badge.select().where(
            Badge.created > day_ago
        ).count()
        
        return {
            "total_tracked_urls": total_urls,
            "total_visits": total_visits,
            "new_badges_today": recent_badges,
        }
    except Exception as e:
        logger.error(f"Error getting system statistics: {e}")
        return {
            "total_tracked_urls": 0,
            "total_visits": 0,
            "new_badges_today": 0,
        }

def get_app_info() -> dict:
    app_version = "N/A"
    default_env = "Production"

    try:
        version_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "version.json")
        if os.path.exists(version_path):
            with open(version_path, "r", encoding="utf-8") as f:
                version_data = json.load(f)
                app_version = version_data.get("version", "N/A")
        else:
            logger.warning("version.json not found for app info.")
    except Exception as e:
        logger.error(f"Error reading version.json for app info: {e}")

    current_env = os.getenv("APP_ENV", default_env)
    
    return {"version": app_version, "environment": current_env}

def load_template(template_name: str) -> str:
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", template_name)
    if not os.path.exists(template_path):
        alt_template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", template_name)
        if os.path.exists(alt_template_path):
            template_path = alt_template_path
        else:
            logger.error(f"Template '{template_name}' not found at {template_path} or {alt_template_path}")
            return "Template not found"
    
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading template '{template_name}': {e}")
        return "Error loading template"
