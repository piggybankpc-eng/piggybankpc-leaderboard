# 🚀 Deploy WITHOUT Coolify - Direct Docker Method

Since Coolify isn't installed, let's deploy directly with Docker! This is actually simpler!

## ✅ Prerequisites Met:
- ✅ Code on GitHub
- ✅ Docker installed
- ✅ Ubuntu 24 server ready

---

## 🎯 Quick Deploy (5 Steps)

### Step 1: Clone Your Repo

```bash
cd ~
git clone https://github.com/piggybankpc-eng/piggybankpc-leaderboard.git
cd piggybankpc-leaderboard
```

### Step 2: Generate Secret Keys

```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('BENCHMARK_SECURITY_KEY=' + secrets.token_urlsafe(32))"
```

**Copy these outputs!**

### Step 3: Create .env File

```bash
cat > .env << 'ENVEOF'
# Security Keys (REPLACE WITH YOUR GENERATED KEYS!)
SECRET_KEY=YOUR-GENERATED-SECRET-KEY-HERE
BENCHMARK_SECURITY_KEY=YOUR-GENERATED-BENCHMARK-KEY-HERE

# Flask Configuration
FLASK_ENV=production
FLASK_APP=app.py

# Database
DATABASE_URL=sqlite:///instance/database.db

# Domain
DOMAIN=piggybankpc.uk

# YouTube
YOUTUBE_CHANNEL=@piggybankpc

# Python
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
ENVEOF
```

**Edit the file and paste your actual keys:**
```bash
nano .env
```

Replace `YOUR-GENERATED-SECRET-KEY-HERE` with your actual keys, then save (Ctrl+X, Y, Enter).

### Step 4: Build and Run!

```bash
# Build the Docker image
docker build -t piggybankpc-leaderboard .

# Run the container
docker run -d \
  --name piggybankpc-leaderboard \
  --restart unless-stopped \
  -p 5555:5555 \
  --env-file .env \
  -v $(pwd)/instance:/app/instance \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/logs:/app/logs \
  piggybankpc-leaderboard
```

### Step 5: Check It's Running!

```bash
# Check container status
docker ps | grep piggybankpc

# Check logs
docker logs piggybankpc-leaderboard --tail 50

# Test health endpoint
curl http://localhost:5555/health
```

**You should see:**
```json
{"status":"healthy","timestamp":"...","database":"healthy","version":"2.0.0"}
```

---

## 🌐 Access Your Site

**Locally:** http://localhost:5555
**From network:** http://YOUR-SERVER-IP:5555

---

## 🔒 Set Up Cloudflare Tunnel (Expose to Internet)

Since you mentioned using Cloudflare:

### Option A: Cloudflare Tunnel (Recommended - Free HTTPS!)

```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create piggybankpc

# Configure tunnel
cat > ~/.cloudflared/config.yml << 'CFEOF'
tunnel: piggybankpc
credentials-file: /home/john/.cloudflared/TUNNEL-ID.json

ingress:
  - hostname: piggybankpc.uk
    service: http://localhost:5555
  - service: http_status:404
CFEOF

# Run tunnel
cloudflared tunnel run piggybankpc
```

Then in Cloudflare dashboard:
1. Go to Zero Trust > Access > Tunnels
2. Find your tunnel
3. Add public hostname: piggybankpc.uk → http://localhost:5555

**Done! Your site is live at https://piggybankpc.uk with HTTPS!**

### Option B: Direct Port Forwarding

Open port 5555 in firewall:
```bash
sudo ufw allow 5555/tcp
```

Then access at: http://YOUR-SERVER-IP:5555

---

## 📋 Useful Commands

**View logs:**
```bash
docker logs piggybankpc-leaderboard -f
```

**Restart container:**
```bash
docker restart piggybankpc-leaderboard
```

**Stop container:**
```bash
docker stop piggybankpc-leaderboard
```

**Update code:**
```bash
cd ~/piggybankpc-leaderboard
git pull
docker stop piggybankpc-leaderboard
docker rm piggybankpc-leaderboard
docker build -t piggybankpc-leaderboard .
# Then run the docker run command from Step 4 again
```

---

## ✅ That's It!

**No Coolify needed!** You're deploying directly with Docker.

This is actually how many production sites run - simple, reliable, and easy to manage!

---

**Ready to deploy? Start with Step 1!** 🚀
