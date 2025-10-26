# 📁 Important Files & Commands - PiggyBankPC Leaderboard

Quick reference for managing your production deployment.

---

## 🔑 Critical Files

### Production Environment
**Location:** `/home/john/Desktop/piggybankpc-leaderboard/.env.production`
```bash
# Contains all production secrets and configuration
SECRET_KEY=Mt4OKdKRVms7XlYZ_hB_RU_3wI41134xzlGwQShaG_k
BENCHMARK_SECURITY_KEY=VSo3wxz9QsoDXAG22JH83__HA2i9AA8QjGy5u4EHJXk
FLASK_ENV=production
DOMAIN=piggybankpc.uk
DATABASE_URL=sqlite:////home/john/Desktop/piggybankpc-leaderboard/instance/database.db
```

### Production Startup Script
**Location:** `/home/john/Desktop/piggybankpc-leaderboard/start_production.sh`
```bash
# Run this to start the production server
./start_production.sh
```
**Important:** This starts Gunicorn on port 5555 with 4 workers in daemon mode.

### Database
**Location:** `/home/john/Desktop/piggybankpc-leaderboard/instance/database.db`
- SQLite database file
- Contains all leaderboard submissions, users, benchmarks
- **BACKUP THIS REGULARLY!**

### Cloudflare Tunnel Service
**Location:** `/etc/systemd/system/cloudflared.service`
- System service that runs the Cloudflare tunnel
- Routes traffic from piggybankpc.uk → localhost:5555

---

## 🚀 Essential Commands

### Start Production Server
```bash
cd /home/john/Desktop/piggybankpc-leaderboard
./start_production.sh
```

### Check Server Status
```bash
# Check if server is running
ps aux | grep gunicorn

# Check the PID
cat /home/john/Desktop/piggybankpc-leaderboard/gunicorn.pid

# Check health endpoint
curl http://localhost:5555/health
```

### Stop Production Server
```bash
# Get the PID
PID=$(cat /home/john/Desktop/piggybankpc-leaderboard/gunicorn.pid)

# Stop the server
kill $PID

# Or force kill if needed
kill -9 $PID
```

### View Logs
```bash
# Access logs
tail -f /home/john/Desktop/piggybankpc-leaderboard/logs/access.log

# Error logs
tail -f /home/john/Desktop/piggybankpc-leaderboard/logs/error.log

# View last 50 lines
tail -n 50 /home/john/Desktop/piggybankpc-leaderboard/logs/error.log
```

### Restart Server
```bash
cd /home/john/Desktop/piggybankpc-leaderboard

# Stop
kill $(cat gunicorn.pid)

# Wait a moment
sleep 2

# Start
./start_production.sh
```

---

## 🔄 Update Code from GitHub

```bash
cd /home/john/Desktop/piggybankpc-leaderboard

# Pull latest changes
git pull

# Stop server
kill $(cat gunicorn.pid)

# Activate venv and install any new dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart server
./start_production.sh
```

---

## 🌐 Cloudflare Configuration

### Tunnel Details
- **Tunnel Name:** ai-server
- **Tunnel ID:** 4c170ccf-78cc-4580-8947-cf5e6f19e339
- **Public Hostnames:**
  - ap.piggybankpc.uk → http://localhost:5555
  - piggybankpc.uk → http://localhost:5555

### DNS Records
```
CNAME: piggybankpc.uk → 4c170ccf-78cc-4580-8947-cf5e6f19e339.cfargotunnel.com
CNAME: ap.piggybankpc.uk → 4c170ccf-78cc-4580-8947-cf5e6f19e339.cfargotunnel.com
```

### Cloudflare Tunnel Commands
```bash
# Check tunnel status
sudo systemctl status cloudflared

# Restart tunnel
sudo systemctl restart cloudflared

# View tunnel logs
sudo journalctl -u cloudflared -f
```

---

## 🗄️ Database Management

### Backup Database
```bash
# Create timestamped backup
cp /home/john/Desktop/piggybankpc-leaderboard/instance/database.db \
   /home/john/Desktop/piggybankpc-leaderboard/instance/database-backup-$(date +%Y%m%d-%H%M%S).db
```

### Restore Database
```bash
# Stop server first
kill $(cat /home/john/Desktop/piggybankpc-leaderboard/gunicorn.pid)

# Restore from backup
cp /home/john/Desktop/piggybankpc-leaderboard/instance/database-backup-YYYYMMDD-HHMMSS.db \
   /home/john/Desktop/piggybankpc-leaderboard/instance/database.db

# Restart server
./start_production.sh
```

---

## 📦 Directory Structure

```
/home/john/Desktop/piggybankpc-leaderboard/
├── app.py                    # Main Flask application
├── .env.production           # Production environment variables
├── start_production.sh       # Production startup script
├── gunicorn.pid              # Running server process ID
├── venv/                     # Python virtual environment
├── instance/
│   └── database.db           # SQLite database (BACKUP THIS!)
├── uploads/                  # User uploaded images
├── logs/
│   ├── access.log           # HTTP access logs
│   └── error.log            # Application error logs
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
└── routes/                  # Application routes
```

---

## 🔐 GitHub Repository

**URL:** https://github.com/piggybankpc-eng/piggybankpc-leaderboard

### Push Changes
```bash
cd /home/john/Desktop/piggybankpc-leaderboard

# Stage changes
git add .

# Commit
git commit -m "Your commit message"

# Push (requires Personal Access Token)
git push origin main
```

**Git Credentials:**
- Username: piggybankpc-eng
- Email: piggybankpc@gmail.com
- Auth: Personal Access Token (not regular password!)

---

## 🏥 Health Check

**Endpoint:** http://localhost:5555/health

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "healthy",
  "timestamp": "2025-10-25T22:39:55.566373",
  "version": "2.0.0"
}
```

**Check from command line:**
```bash
curl http://localhost:5555/health
```

**Public health check:**
```bash
curl https://ap.piggybankpc.uk/health
```

---

## 🆘 Troubleshooting

### Server Won't Start
```bash
# Check if port 5555 is already in use
ss -tulpn | grep 5555

# If something's using it, find and kill it
sudo lsof -ti:5555 | xargs kill -9

# Try starting again
./start_production.sh
```

### Database Errors
```bash
# Check database file exists
ls -lh /home/john/Desktop/piggybankpc-leaderboard/instance/database.db

# Check permissions
chmod 666 /home/john/Desktop/piggybankpc-leaderboard/instance/database.db
chmod 777 /home/john/Desktop/piggybankpc-leaderboard/instance/
```

### Cloudflare Tunnel Not Working
```bash
# Restart tunnel service
sudo systemctl restart cloudflared

# Check tunnel status
sudo systemctl status cloudflared

# View tunnel logs for errors
sudo journalctl -u cloudflared -n 50
```

---

## 📞 Quick Reference

| What | Command |
|------|---------|
| Start server | `cd /home/john/Desktop/piggybankpc-leaderboard && ./start_production.sh` |
| Stop server | `kill $(cat /home/john/Desktop/piggybankpc-leaderboard/gunicorn.pid)` |
| Check status | `curl http://localhost:5555/health` |
| View errors | `tail -f /home/john/Desktop/piggybankpc-leaderboard/logs/error.log` |
| Backup DB | `cp instance/database.db instance/database-backup-$(date +%Y%m%d).db` |
| Update code | `git pull && kill $(cat gunicorn.pid) && ./start_production.sh` |

---

**Live Site:** https://ap.piggybankpc.uk or https://piggybankpc.uk

**Server:** Ubuntu 24 at /home/john/Desktop/piggybankpc-leaderboard

**Port:** 5555 (localhost only, exposed via Cloudflare tunnel)
