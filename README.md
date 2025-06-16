<p align="center">
  <img src="assets/logo.png" width="200" alt="BadgeTrack Logo" />
</p>
<p align="center">
  <strong>BadgeTrack is a Visitor Badge Server.</strong>
  A powerful FastAPI-based service for generating beautiful visitor badges.
</p>
<p align="center">
  <a href="https://github.com/PianoNic/BadgeTrack"><img src="https://badgetrack.pianonic.ch/badge?url=https://github.com/PianoNic/BadgeTrack&label=visitors&color=237e61&style=flat&logo=github" alt="Visitor badge"/></a>
  <a href="#-installation"><img src="https://img.shields.io/badge/Self--Host-Instructions-237e61.svg" /></a>
</p>

---

## 🚀 Features

- ⚡ **Dual Rate Limiting**:  
  - Daily visit tracking per URL (24-hour cooldown per IP/URL)  
  - New badge creation limit (10 new badges per IP per day)
- 🎨 **Customizable Badges**: Multiple colors, styles, and logos supported
- 🗄️ **Efficient Database**: Clean URL-based storage with visit counters
- 🔐 **SQL Injection Safe**: Parameterized queries protect against attacks
- 📊 **Shields.io Integration**: Beautiful badges powered by Shields.io
- 💾 **Memory Efficient**: In-memory rate limiting cache with auto-cleanup

After installation, BadgeTrack will be accessible at  
- `http://localhost:8925` (Docker)  
- `http://localhost:8000` (direct)  
- Or your own domain, e.g. `https://badgetrack.pianonic.ch`

---

## 🛠️ API Usage

### Basic Badge

```markdown
![visitors](https://badgetrack.pianonic.ch/badge?url=https://github.com/YourUser/YourRepo)
```

### Custom Badge

```markdown
![visitors](https://badgetrack.pianonic.ch/badge?url=https://github.com/YourUser/YourRepo&label=visitors&color=4ade80&style=flat&logo=github)
```

### Live Examples

- Basic:  
  `https://badgetrack.pianonic.ch/badge?url=https://github.com/microsoft/vscode`
- Custom:  
  `https://badgetrack.pianonic.ch/badge?url=https://example.com&label=visitors&color=blue&style=for-the-badge&logo=github`

### Parameters

| Parameter | Default   | Description                        | Example                                 |
|-----------|-----------|------------------------------------|-----------------------------------------|
| `url`     | *required*| The URL to track visits for        | `https://github.com/user/repo`          |
| `label`   | `visits`  | Badge label text                   | `visitors`, `views`, `hits`             |
| `color`   | `4ade80`  | Badge color (green theme)          | `4ade80`, `22c55e`, `green`             |
| `style`   | `flat`    | Badge style                        | `flat`, `plastic`, `for-the-badge`      |
| `logo`    | *none*    | Brand logo                         | `github`, `gitlab`, `docker`            |

---

## 🏷️ Markdown Table Example

| Badge Type | Example Markdown | Preview |
|------------|------------------|---------|
| Basic | `![visitors](https://badgetrack.pianonic.ch/badge?url=https://github.com/YourUser/YourRepo)` | ![visitors](https://badgetrack.pianonic.ch/badge?url=https://github.com/YourUser/YourRepo) |
| Custom | `![visitors](https://badgetrack.pianonic.ch/badge?url=https://github.com/YourUser/YourRepo&label=visitors&color=4ade80&style=flat&logo=github)` | ![visitors](https://badgetrack.pianonic.ch/badge?url=https://github.com/YourUser/YourRepo&label=visitors&color=4ade80&style=flat&logo=github) |

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

Use this Docker Compose configuration to run the latest published image:

```yaml
services:
  badgetrack:
    image: pianonic/badgetrack:latest
    container_name: badgetrack
    ports:
      - "8925:8000"
    volumes:
      - ./data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

```powershell
# Run with the latest image
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

### Environment Variables

- `PYTHONUNBUFFERED=1` - Ensures real-time log output
- Volume mounting preserves database between container restarts

---

## 📜 License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for more details.

---

<p align="center">Made with ❤️ by PianoNic</p>
