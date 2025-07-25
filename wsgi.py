from src.main import app
import os
import uvicorn
import logging

if __name__ == "__main__":
    os.environ["APP_ENV"] = "Development"
    logger = logging.getLogger(__name__) 
    logger.info(f"Running wsgi.py directly in {os.getenv('APP_ENV')} mode.")

    host = os.getenv("UVICORN_HOST", "127.0.0.1")
    port = int(os.getenv("UVICORN_PORT", "8000"))
    log_level = os.getenv("UVICORN_LOG_LEVEL", "info").lower()

    logger.info(f"Starting Uvicorn for src.main:app: host={host}, port={port}, log_level={log_level}")
    uvicorn.run("src.main:app", host=host, port=port, log_level=log_level, reload=True)
