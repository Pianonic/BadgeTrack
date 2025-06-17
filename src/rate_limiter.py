from .models import db, IpHash, Badge, Visit
import time
import logging
import os

logger = logging.getLogger(__name__)

RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "172800"))

def is_visit_allowed(ip_hash_str: str, url_str: str) -> bool:
    """Check if a visit from this IP to this URL is allowed based on rate limiting"""
    now = int(time.time())
    try:
        # Get IP hash record
        ip_hash = IpHash.get_or_none(IpHash.hash == ip_hash_str)
        if not ip_hash:
            return True  # First time seeing this IP, allow visit
        
        # Get badge record
        badge = Badge.get_or_none(Badge.url == url_str)
        if not badge:
            return True  # First time seeing this URL, allow visit
            
        # Check if there's a recent visit from this IP to this badge
        visit_record = Visit.get_or_none(
            (Visit.ip_hash == ip_hash) & (Visit.badge == badge)
        )
        
        if not visit_record:
            return True  # No previous visit from this IP to this badge
        
        # Check if enough time has passed since last visit
        return (now - visit_record.last_visit) >= RATE_LIMIT_WINDOW_SECONDS
    except Exception as e:
        logger.error(f"Error checking visit rate limit: {e}")
        return True  # Allow visit on error to avoid blocking legitimate users

def cleanup_old_records():
    """Clean up old records to save space"""
    now = int(time.time())
    week_ago = now - 604800  # 7 days
    
    try:
        with db.atomic():
            # Clean up old visit records
            deleted_visits = Visit.delete().where(
                Visit.last_visit < week_ago
            ).execute()
            
            logger.info(f"Cleaned up {deleted_visits} old visit records.")
            
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def get_rate_limit_info() -> dict:
    return {
        "rate_limit_window_hours": RATE_LIMIT_WINDOW_SECONDS // 3600,
        "cleanup_retention_days": 7
    }
