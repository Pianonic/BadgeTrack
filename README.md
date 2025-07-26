<p align="center">
  <img src="assets/logo.png" width="200" alt="BadgeTrack Logo" />
</p>
<p align="center">
  <strong>BadgeTrack is a Visitor Badge Server.</strong>
  A powerful service for generating beautiful visitor badges.
</p>
<p align="center">
  <a href="https://github.com/PianoNic/BadgeTrack"><img src="https://badgetrack.pianonic.ch/badge?tag=badge-track&label=visits&color=237e61&style=flat" alt="visits" /></a>
  <a href="https://badgetrack.pianonic.ch/"><img src="https://img.shields.io/badge/Create%20Badge-badgetrack.pianonic.ch-237e61.svg"/></a>
  <a href="#-installation"><img src="https://img.shields.io/badge/Self--Host-Instructions-237e61.svg" /></a>
</p>

---

## 🚀 Features

- ⚡ **Unique Visitor Tracking**:  
  - Each visitor is counted only once per badge tag, preventing repeat counts.
- 🎨 **Customizable Badges**: Multiple colors, styles, and logos supported
- 🗄️ **Efficient Database**: Clean URL-based storage with visit counters
- 🔐 **SQL Injection Safe**: Parameterized queries protect against attacks
- 📊 **Shields.io Integration**: Beautiful badges powered by Shields.io
- 💾 **Memory Efficient**: In-memory rate limiting cache with auto-cleanup
- 🐳 **Docker Ready**: Multi-architecture Docker images available

After installation, BadgeTrack will be accessible at  
- `http://localhost:8925` (Docker, if using default `compose.yml` port)  
- `http://localhost:8000` (direct execution via `python wsgi.py` with default Uvicorn port)  
- Or your own domain, e.g. `https://badgetrack.pianonic.ch`

---

## ⚙️ Configuration

BadgeTrack can be configured using environment variables. This is especially useful when deploying with Docker via `compose.yml` or other orchestration methods.

| Variable                    | Default (in code if not set)          | Description                                                                                                |
| --------------------------- | ------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `APP_ENV`                   | `Production`                          | Sets the application environment. Affects things like debug messages and how `version.json` environment is treated. Set to `Development` for local dev.    |
| `LOG_LEVEL`                 | `INFO`                                | Controls the application's logging verbosity (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).       |
| `SECRET_KEY`                | (auto-generated, 32-char secure hex)  | **IMPORTANT**: A secret key used for hashing and security. **Set a strong, unique value (>=32 chars) in production!**   |
| `UVICORN_HOST`              | `127.0.0.1`                           | Host address for Uvicorn when running `wsgi.py` directly (e.g., `0.0.0.0` to expose). Not typically set in `compose.yml`. |
| `UVICORN_PORT`              | `8000`                                | Port for Uvicorn when running `wsgi.py` directly. Not typically set in `compose.yml` as Docker handles port mapping. |                            |
| `UVICORN_LOG_LEVEL`         | `info`                                | Log level for the Uvicorn server itself when running `wsgi.py` directly.                                     |

When using `compose.yml`, these can be set under the `environment` section for the `badgetrack` service as shown below.

---
## 🐳 Docker Deployment

### Images

BadgeTrack provides official Docker images for multiple architectures:

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/pianonic/badgetrack:latest

# Pull from Docker Hub
docker pull pianonic/badgetrack:latest
```

### Production Deployment (Latest Image)

Use this Docker Compose configuration (`compose.yml`) to run the latest published image:

```yaml
services:
  badgetrack:
    image: pianonic/badgetrack:latest # Or ghcr.io/pianonic/badgetrack:latest
    container_name: badgetrack
    ports:
      - "8925:8000" # External port : Internal Uvicorn port (default 8000)
    volumes:
      - ./data:/app/data # Persists the SQLite database
    environment:
      - PYTHONUNBUFFERED=1   # Ensures Python logs appear in real-time
      - APP_ENV=Production   # Set to Production for live deployments
      - LOG_LEVEL=INFO       # Adjust as needed: DEBUG, INFO, WARNING, ERROR, CRITICAL
      - SECRET_KEY=your_very_strong_and_unique_secret_key_please_change_me # IMPORTANT: Set a strong, unique key!
    restart: unless-stopped
```

To run:

```powershell
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Local Development

```powershell
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t badgetrack .
docker run -p 8925:8000 -v ${PWD}/data:/app/data badgetrack
```

The service will be available at `http://localhost:8925`

### Environment Variables in Docker

- `PYTHONUNBUFFERED=1`: Ensures real-time log output from Python within the container.
- Volume mounting (`./data:/app/data`): Preserves the SQLite database (`data/visitors.db`) between container restarts.
- Other variables like `APP_ENV`, `SECRET_KEY`, etc., configure the application as described in the [⚙️ Configuration](#️-configuration) section.

---

## 📜 License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for more details.

---

<p align="center">Made with ❤️ by PianoNic</p>
