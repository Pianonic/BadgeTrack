<p align="center">
  <img src="assets/logo.png" width="200" alt="BadgeTrack Logo">
</p>
<p align="center">
  <strong>BadgeTrack is a Visitor Badge Server.</strong> 
  A powerful FastAPI-based service for generating beautiful visitor badges.
</p>
<p align="center">
  <a><img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FYourUser%2FBadgeTrack&count_bg=%234ADE80&title_bg=%23555555&icon=github.svg&icon_color=%23E7E7E7&title=Visits&edge_flat=false"/></a>
  <a href="#-installation"><img src="https://img.shields.io/badge/Self--Host-Instructions-4ade80.svg"/></a>
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

## 📦 Installation

### Quick Start:

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/YourUser/BadgeTrack.git
   cd BadgeTrack
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```powershell
   cd src
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Docker:
```powershell
docker-compose up --build
```

After installation, BadgeTrack will be accessible at http://localhost:8925 (Docker) or http://localhost:8000 (direct)

## 🛠️ API Usage

### Basic Badge
```markdown
![visitors](http://localhost:8925/badge?url=https://github.com/YourUser/YourRepo)
```

### Custom Badge
```markdown
![visitors](http://localhost:8925/badge?url=https://github.com/YourUser/YourRepo&label=visitors&color=4ade80&style=flat&logo=github)
```

### Live Examples
- Basic: `http://localhost:8925/badge?url=https://github.com/microsoft/vscode`
- Custom: `http://localhost:8925/badge?url=https://example.com&label=visitors&color=blue&style=for-the-badge&logo=github`

### Parameters

| Parameter | Default | Description | Example |
|-----------|---------|-------------|---------|
| `url` | *required* | The URL to track visits for | `https://github.com/user/repo` |
| `label` | `visits` | Badge label text | `visitors`, `views`, `hits` |
| `color` | `4ade80` | Badge color (green theme) | `4ade80`, `22c55e`, `green` |
| `style` | `flat` | Badge style | `flat`, `plastic`, `for-the-badge` |
| `logo` | *none* | Brand logo | `github`, `gitlab`, `docker` |

## 🐳 Docker Deployment

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

## 📜 License
This project is licensed under the MIT License. 
See the [LICENSE](LICENSE) file for more details.

---
<p align="center">Made with ❤️ by PianoNic</p>
