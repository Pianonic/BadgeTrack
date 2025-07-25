import hashlib
import secrets
import urllib.parse
import os
import logging

default_secret_key_placeholder = "your_super_secret_key_here_default_unsafe"
SECRET_KEY = os.getenv("SECRET_KEY", default_secret_key_placeholder)

if SECRET_KEY == default_secret_key_placeholder or len(SECRET_KEY) < 32:
    logging.warning(
        f"Using default or potentially insecure SECRET_KEY (length: {len(SECRET_KEY)}). For production, please set a strong, unique SECRET_KEY environment variable (at least 32 chars)."
    )
    if SECRET_KEY == default_secret_key_placeholder:
        logging.info("Generating a temporary SECRET_KEY for this session as a fallback.")
        SECRET_KEY = secrets.token_urlsafe(32)
    elif len(SECRET_KEY) < 32:
        logging.warning("Provided SECRET_KEY is too short. Consider generating a new one.")


def build_shields_url(label: str, count: int, color: str, style: str, logo: str = "") -> str:
    shields_url = (
        f"https://img.shields.io/badge/"
        f"{urllib.parse.quote(label)}-{count}-{color}.svg"
        f"?style={style}"
    )
    if logo:
        shields_url += f"&logo={urllib.parse.quote(logo)}"

    return shields_url


def get_security_headers() -> dict:
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }
