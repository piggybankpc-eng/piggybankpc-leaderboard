# 🚀 PiggyBankPC Leaderboard - Production Deployment Guide

**Deploy your revenue-generating leaderboard to piggybankpc.uk in under an hour!**

---

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ Ubuntu 24 server (your i9-9900X with 64GB RAM)
- ✅ Coolify installed and running
- ✅ Domain purchased: **piggybankpc.uk** (£5.21/year - brilliant!)
- ✅ GitHub account
- ✅ Cloudflare account (for tunnel/DNS)
- ✅ SSH access to your server

---

## 🔑 Step 1: Generate Production Secret Keys

**IMPORTANT:** Never use default keys in production!

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate BENCHMARK_SECURITY_KEY
python3 -c "import secrets; print('BENCHMARK_SECURITY_KEY=' + secrets.token_urlsafe(32))"
```

**Save these keys!** You'll need them in Step 5.

---

## 📦 Step 2: Push to GitHub

### 2.1 Initialize Git Repository (if not done)

```bash
cd /home/john/Desktop/piggybankpc-leaderboard

# Initialize git
git init

# Add .gitignore (CRITICAL - prevents secrets from being committed!)
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Flask
instance/
*.db
*.sqlite

# Secrets (NEVER COMMIT THESE!)
.env
.env.local
.env.*.local

# Uploads & logs
uploads/
logs/
*.log

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Test files
test_benchmark*.pbr
TEST_*.md
*_ADDED.md
CONFIG_*.md
FILE_FORMAT_FIX.md
WHATS_NEXT.md
EOF

# Add all files
git add .

# Initial commit
git commit -m "Initial commit - PiggyBankPC Leaderboard v2.0 (Gaming + AI)"
```

### 2.2 Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `piggybankpc-leaderboard`
3. Description: "Budget GPU leaderboard with gaming FPS + AI/LLM benchmarks"
4. Visibility: **Private** (keep your secrets safe!)
5. Click "Create repository"

### 2.3 Push to GitHub

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/piggybankpc-leaderboard.git

# Push to main branch
git branch -M main
git push -u origin main
```

---

## 🐳 Step 3: Deploy with Coolify

### 3.1 Access Coolify Dashboard

Open your Coolify dashboard (usually at `http://your-server-ip:8000`)

### 3.2 Create New Application

1. Click **"+ New Resource"**
2. Select **"Application"**
3. Choose **"GitHub App"**
4. Select your repository: `piggybankpc-leaderboard`
5. Click **"Continue"**

### 3.3 Configure Build Settings

**Build Pack:** Docker

**Dockerfile Location:** `/Dockerfile` (default)

**Docker Compose Location:** `/docker-compose.yml`

**Port:** `5555`

**Health Check Path:** `/health`

### 3.4 Configure Domains

**Domain:** `piggybankpc.uk`

**Enable HTTPS:** ✅ (Coolify handles Let's Encrypt automatically)

---

## 🔧 Step 4: Configure Environment Variables in Coolify

In Coolify's "Environment Variables" section, add these:

```bash
# Security Keys (use the ones you generated in Step 1!)
SECRET_KEY=your-generated-secret-key-here
BENCHMARK_SECURITY_KEY=your-generated-benchmark-key-here

# Flask Configuration
FLASK_ENV=production
FLASK_APP=app.py

# Database (SQLite for start, upgrade to PostgreSQL later)
DATABASE_URL=sqlite:///instance/database.db

# Domain
DOMAIN=piggybankpc.uk

# YouTube Channel
YOUTUBE_CHANNEL=@piggybankpc

# Python Settings
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

**Save the environment variables!**

---

## 🌐 Step 5: Configure Cloudflare DNS

### 5.1 Point Domain to Server

1. Log in to Cloudflare
2. Select domain: `piggybankpc.uk`
3. Go to **DNS** > **Records**
4. Add A Record:
   - **Type:** A
   - **Name:** @ (root domain)
   - **IPv4 address:** Your server's public IP
   - **Proxy status:** Proxied (orange cloud)
   - **TTL:** Auto
5. Click **"Save"**

### 5.2 Add WWW Record (Optional)

- **Type:** CNAME
- **Name:** www
- **Target:** piggybankpc.uk
- **Proxy status:** Proxied
- **TTL:** Auto

### 5.3 Configure SSL/TLS

1. Go to **SSL/TLS** tab
2. Set encryption mode: **"Full (strict)"**
3. Enable **"Always Use HTTPS"**
4. Enable **"Automatic HTTPS Rewrites"**

---

## 🚀 Step 6: Deploy!

Back in Coolify:

1. Click **"Deploy"** button
2. Watch the build logs (this takes 3-5 minutes)
3. Wait for: `✅ Deployment successful`

**Check the logs for:**
```
🚀 PiggyBankPC Leaderboard starting in PRODUCTION mode
📊 Database: sqlite:///instance/database.db
```

---

## ✅ Step 7: Verify Deployment

### 7.1 Check Health Endpoint

```bash
curl https://piggybankpc.uk/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T22:30:00.123456",
  "database": "healthy",
  "version": "2.0.0"
}
```

### 7.2 Test the Site

Visit: **https://piggybankpc.uk**

**You should see:**
- ✅ Homepage loads
- ✅ Green padlock (HTTPS working)
- ✅ Fast loading time
- ✅ Register/Login works
- ✅ Leaderboard shows Gaming FPS + AI Tokens/s columns

### 7.3 Test Benchmark Upload

1. Register a test account
2. Go to `/submit`
3. Upload `test_benchmark_encoded.pbr`
4. Verify diagnostic page shows:
   - Thermal throttling issues
   - Amazon affiliate links
   - YouTube CTAs
   - Click tracking works

---

## 📊 Step 8: Create Your First Admin Account

SSH into your server:

```bash
# Access Coolify's container
docker exec -it piggybankpc-leaderboard /bin/bash

# Open Python shell
python3

# Create admin user
from app import app
from models import db, User

with app.app_context():
    admin = User(username='admin', email='your-email@gmail.com')
    admin.set_password('your-secure-password')
    admin.is_admin = True
    db.session.add(admin)
    db.session.commit()
    print(f'✅ Admin user created: {admin.username}')

exit()
```

Now you can access analytics at `/analytics` (admin only).

---

## 🔄 Step 9: Set Up Auto-Deploy (CI/CD)

Coolify can auto-deploy when you push to GitHub!

### In Coolify Dashboard:

1. Go to your application settings
2. Find **"Git Integration"**
3. Enable **"Auto Deploy on Push"**
4. Select branch: `main`

**Now whenever you:**
```bash
git add .
git commit -m "Added new feature"
git push
```

**Coolify automatically:**
- Detects the push
- Builds new Docker image
- Deploys with zero downtime
- Rolls back if health check fails

---

## 📈 Step 10: Monitor Your Application

### View Logs in Coolify

1. Go to your application
2. Click **"Logs"** tab
3. Real-time logs appear!

### View Metrics

Coolify shows:
- CPU usage
- Memory usage
- Request count
- Response times

### Set Up Alerts (Optional)

Coolify can send alerts to:
- Discord webhook
- Telegram
- Email

Configure in **Settings** > **Notifications**

---

## 🔧 Common Issues & Solutions

### Issue 1: "SECRET_KEY not set" Error

**Problem:** Container fails to start

**Solution:**
```bash
# Verify environment variables in Coolify
# Make sure SECRET_KEY and BENCHMARK_SECURITY_KEY are set
# Redeploy after adding them
```

### Issue 2: Database Not Persisting

**Problem:** Data disappears after restart

**Solution:**
```bash
# Ensure volume mounts are configured in Coolify:
# ./instance:/app/instance
# ./uploads:/app/uploads
```

### Issue 3: 502 Bad Gateway

**Problem:** Nginx can't reach the app

**Solution:**
```bash
# Check health endpoint
docker logs piggybankpc-leaderboard

# Verify port 5555 is exposed
docker ps | grep piggybankpc
```

### Issue 4: Slow Uploads

**Problem:** Large benchmark files timeout

**Solution:**
```bash
# Increase Gunicorn timeout in Dockerfile (already set to 120s)
# Or adjust in Coolify environment:
GUNICORN_TIMEOUT=180
```

---

## 🚀 Performance Optimization

### Use PostgreSQL Instead of SQLite (Recommended for Production)

```bash
# In Coolify, add a PostgreSQL database
# Then update DATABASE_URL:
DATABASE_URL=postgresql://username:password@postgres:5432/piggybankpc
```

### Enable Redis for Session Storage

```bash
# Add Redis container in Coolify
# Update environment:
REDIS_URL=redis://redis:6379/0
SESSION_TYPE=redis
```

### Add CDN for Static Files

Use Cloudflare's caching:
1. Go to Cloudflare dashboard
2. Enable **"Auto Minify"** (CSS, JS, HTML)
3. Set **"Browser Cache TTL"** to 4 hours

---

## 🔒 Security Checklist

Before going live, verify:

- ✅ SECRET_KEY is random and secure
- ✅ BENCHMARK_SECURITY_KEY is random and secure
- ✅ .env file is in .gitignore (NEVER committed to git)
- ✅ HTTPS is enabled with valid certificate
- ✅ Debug mode is OFF in production
- ✅ Database backups are configured
- ✅ Firewall allows only ports 80 and 443
- ✅ Admin account has strong password
- ✅ File upload size limits are set
- ✅ Rate limiting is enabled

---

## 📦 Backup Your Data

### Manual Backup

```bash
# SSH into server
docker exec piggybankpc-leaderboard tar -czf /tmp/backup.tar.gz /app/instance /app/uploads

# Copy to local machine
docker cp piggybankpc-leaderboard:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz
```

### Automated Backups with Coolify

Coolify Pro includes automated backups to S3/Backblaze.

---

## 🎯 What's Next?

Your leaderboard is LIVE! 🎉

### Immediate Actions:

1. **Test Everything:**
   - Register account
   - Upload benchmark
   - Check diagnostics
   - Verify affiliate links work
   - Test click tracking

2. **Create Content:**
   - Record YouTube videos about your benchmarks
   - Update diagnostic_config.py with video IDs
   - Share on social media

3. **Monitor Revenue:**
   - Check Amazon Associates dashboard
   - Track YouTube analytics
   - Monitor site traffic in Cloudflare

4. **Optimize:**
   - Upload more benchmark data
   - Test on different hardware
   - Gather community submissions

### Future Enhancements:

- Add Discord bot integration
- Create API for benchmark tool
- Build Windows/Linux benchmark client
- Add comparison charts
- Implement leaderboard filters
- Create "Best Value" recommendations page

---

## 📞 Need Help?

**Check Logs:**
```bash
# In Coolify
Click "Logs" tab

# Or via SSH:
docker logs piggybankpc-leaderboard --tail 100 -f
```

**Restart Container:**
```bash
docker restart piggybankpc-leaderboard
```

**Rebuild from Scratch:**
In Coolify, click "Force Rebuild"

---

## 🎉 Congratulations!

Your **PiggyBankPC Leaderboard** is now live at:

### **https://piggybankpc.uk** 🚀

You've built the **ONLY** leaderboard that benchmarks:
- 🎮 Gaming FPS
- 🤖 AI/LLM Tokens/s
- 💰 Price-per-performance
- 🔧 Automatic diagnostics
- 💵 Revenue generation

**Start promoting and watch the traffic (and revenue) roll in!** 💰💰💰

---

**Built by Claude Code for PiggyBankPC**  
**The Future of Budget PC Benchmarking** 🐷💻
