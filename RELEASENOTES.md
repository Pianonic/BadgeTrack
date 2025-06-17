## Release Notes - v1.0.4 (June 17, 2025)

### Changes:
- Renamed `main.py` to `wsgi.py` for clarity in production environments.
- Replaced all `print` statements with `logger` calls for improved logging and debugging capabilities across the application.
- Removed unnecessary comments and docstrings to streamline the codebase.
- Updated `Dockerfile` to reflect the renaming of `main.py` to `wsgi.py` (previously `asgi.py`).
- **Dynamic API Version**: The FastAPI application version is now dynamically loaded from `version.json`.
- **Development Environment Detection**: Running `python wsgi.py` now automatically sets the application environment to "Development", reflected in `/api/app-info`.
- **Environment Variable Configuration**: Key application parameters are now configurable via environment variables:
    - `SECRET_KEY`: For securing IP hashes.
    - `RATE_LIMIT_WINDOW_SECONDS`: Cooldown for visit tracking per IP/URL.
    - `MAX_NEW_BADGES_PER_DAY`: Limit on new badge creations per IP.
    - `LOG_LEVEL`: Application-wide logging level.
    - `APP_ENV`: Application environment (e.g., Production, Development).
    - `UVICORN_HOST`, `UVICORN_PORT`, `UVICORN_LOG_LEVEL`: For local development server via `wsgi.py`.
- Updated `compose.yml` to include new environment variables.
- Updated `README.md` with documentation for the new environment variables.
