# Coolify Deployment Guide for PiggyBankPC Leaderboard

This guide will help you deploy the PiggyBankPC Leaderboard to Coolify.

## Prerequisites

- Coolify installed and running on your server
- Git repository containing this application (GitHub, GitLab, or Gitea)
- Domain name configured (optional but recommended)

## Deployment Steps

### 1. Create New Application in Coolify

1. Log into your Coolify dashboard
2. Click **"+ New"** → **"Application"**
3. Choose **"Public Repository"** or connect your Git account
4. Enter repository URL or select from connected repos

### 2. Configure Build Settings

In the Coolify application settings:

**Build Pack:** Docker (Dockerfile)
**Port:** 5555
**Base Directory:** / (or the subdirectory if not at root)

### 3. Set Environment Variables

In the **Environment Variables** section, add:

```bash
FLASK_ENV=production
SECRET_KEY=<generate-random-key>
BENCHMARK_SECURITY_KEY=PIGGYBANK_PC_BENCHMARK_SECRET_2025
```

**IMPORTANT:** Generate a secure SECRET_KEY:
```bash
openssl rand -base64 32
```

### 4. Configure Persistent Storage

Add two persistent storage volumes in Coolify:

**Volume 1 - Database:**
- Source: `./instance`
- Destination: `/app/instance`

**Volume 2 - Uploads:**
- Source: `./uploads`
- Destination: `/app/uploads`

### 5. Deploy

1. Click **"Deploy"**
2. Coolify will:
   - Clone your repository
   - Build the Docker image
   - Start the container
   - Configure nginx proxy
   - Set up SSL (if domain configured)

### 6. Access Your Application

- **Local Network:** `http://your-server-ip:5555`
- **With Domain:** `https://piggybankpc.yourdomain.com`

Coolify automatically handles:
- ✅ Nginx reverse proxy
- ✅ SSL certificates (via Let's Encrypt)
- ✅ Auto-restart on crash
- ✅ Log collection
- ✅ Health checks

## Post-Deployment

### Create Admin User (Optional)

SSH into your server and run:

```bash
# Access the container
docker exec -it piggybankpc-leaderboard bash

# Open Python shell
python3

# Create admin user
from app import create_app
from models import db, User

app = create_app('production')
with app.app_context():
    admin = User(username='admin', email='admin@example.com', is_admin=True)
    admin.set_password('your-secure-password')
    db.session.add(admin)
    db.session.commit()
    print("Admin user created!")
```

### Configure Cloudflare Tunnel (If Using)

Since you already have Cloudflare tunnel set up:

1. Add a new public hostname in Cloudflare Tunnel dashboard
2. **Subdomain:** `piggybankpc` (or your choice)
3. **Domain:** `megger-sparks.uk`
4. **Service:** `http://localhost:5555`
5. Save

Your app will be accessible at: `https://piggybankpc.megger-sparks.uk`

## Coolify Features You Get

### Automatic Backups
Coolify can backup your volumes:
1. Go to **Backups** in your application
2. Enable scheduled backups
3. Choose frequency (daily recommended)

### Monitoring
- View logs in real-time
- Check resource usage (CPU, RAM)
- Monitor uptime

### Easy Updates
When you push changes to your Git repo:
1. Coolify can auto-deploy on push (enable in settings)
2. Or manually click **"Redeploy"** in Coolify

## Troubleshooting

### Application won't start
Check logs in Coolify:
```bash
# Or via SSH:
docker logs piggybankpc-leaderboard
```

### Database issues
Ensure the `instance` volume is mounted correctly and the container has write permissions.

### Port conflicts
If port 5555 is taken, change it in:
- Coolify port settings
- Dockerfile (EXPOSE directive)
- docker-compose.yml (ports mapping)

## Security Checklist

- [ ] Changed SECRET_KEY from default
- [ ] Updated BENCHMARK_SECURITY_KEY to match your benchmark suite
- [ ] Enabled SSL via Cloudflare or Coolify
- [ ] Set up regular backups
- [ ] Configured firewall (UFW) if not using Cloudflare tunnel

## Support

For Coolify-specific issues:
- Coolify Docs: https://coolify.io/docs
- Coolify Discord: https://discord.gg/coolify

For PiggyBankPC Leaderboard issues:
- Check README.md
- Review application logs
