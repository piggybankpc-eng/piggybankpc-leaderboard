# 🔧 Docker Build Timeout Fix

## Issue: TLS handshake timeout with Docker Hub

This happens when the connection to Docker Hub is slow or interrupted.

## ✅ Solutions (Try in order):

### Solution 1: Retry the Build (Network might be temporary)

```bash
docker build -t piggybankpc-leaderboard . --no-cache
```

### Solution 2: Use Docker BuildKit (Faster & More Reliable)

```bash
DOCKER_BUILDKIT=1 docker build -t piggybankpc-leaderboard .
```

### Solution 3: Increase Docker Timeout

```bash
export DOCKER_CLIENT_TIMEOUT=300
export COMPOSE_HTTP_TIMEOUT=300
docker build -t piggybankpc-leaderboard .
```

### Solution 4: Configure Docker to Use Google DNS

```bash
# Edit Docker daemon config
sudo nano /etc/docker/daemon.json
```

Add:
```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

Then restart Docker:
```bash
sudo systemctl restart docker
```

Try building again:
```bash
docker build -t piggybankpc-leaderboard .
```

---

## 🚀 Alternative: Use Existing Python Image

If timeout persists, we can use a pre-pulled image:

```bash
# Pull the base image first (with retries)
docker pull python:3.11-slim

# Then build your app
docker build -t piggybankpc-leaderboard .
```

---

## ⚡ Quick Deploy Alternative

Since you already have the development environment running locally, we can deploy that directly!

```bash
# Navigate to your project
cd /home/john/Desktop/piggybankpc-leaderboard

# Generate production keys
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('BENCHMARK_SECURITY_KEY=' + secrets.token_urlsafe(32))"

# Create production .env
cat > .env.production << 'ENVEOF'
SECRET_KEY=YOUR-KEY-HERE
BENCHMARK_SECURITY_KEY=YOUR-KEY-HERE
FLASK_ENV=production
FLASK_APP=app.py
DATABASE_URL=sqlite:///instance/database.db
DOMAIN=piggybankpc.uk
YOUTUBE_CHANNEL=@piggybankpc
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
ENVEOF

# Edit and add your keys
nano .env.production

# Run with Gunicorn directly (no Docker needed!)
source venv/bin/activate
gunicorn --bind 0.0.0.0:5555 --workers 4 --timeout 120 app:app
```

This runs your app in production mode WITHOUT Docker!

---

Let me know which solution works! 🚀
