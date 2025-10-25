# 🚀 Quick Deployment Checklist

Use this checklist to deploy PiggyBankPC Leaderboard to production!

## ☑️ Pre-Deployment Checklist

- [ ] Domain purchased: piggybankpc.uk ✅ (£5.21/year)
- [ ] Coolify installed on server
- [ ] GitHub account ready
- [ ] Cloudflare account ready

## ☑️ Secret Keys Generated

```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('BENCHMARK_SECURITY_KEY=' + secrets.token_urlsafe(32))"
```

- [ ] SECRET_KEY generated and saved
- [ ] BENCHMARK_SECURITY_KEY generated and saved

## ☑️ Git Repository

- [ ] Git initialized
- [ ] .gitignore created (prevents .env from being committed!)
- [ ] All files committed
- [ ] GitHub repository created (private!)
- [ ] Code pushed to GitHub

```bash
git init
git add .
git commit -m "Initial commit - PiggyBankPC Leaderboard v2.0"
git remote add origin https://github.com/YOUR_USERNAME/piggybankpc-leaderboard.git
git push -u origin main
```

## ☑️ Coolify Configuration

- [ ] New application created in Coolify
- [ ] GitHub repository connected
- [ ] Build pack set to: Docker
- [ ] Port set to: 5555
- [ ] Health check path set to: /health
- [ ] Domain configured: piggybankpc.uk
- [ ] HTTPS enabled

## ☑️ Environment Variables in Coolify

- [ ] SECRET_KEY added
- [ ] BENCHMARK_SECURITY_KEY added
- [ ] FLASK_ENV=production
- [ ] FLASK_APP=app.py
- [ ] DATABASE_URL configured
- [ ] PYTHONUNBUFFERED=1
- [ ] PYTHONDONTWRITEBYTECODE=1

## ☑️ Cloudflare DNS

- [ ] A record created pointing to server IP
- [ ] Proxy status: Proxied (orange cloud)
- [ ] SSL/TLS mode: Full (strict)
- [ ] Always Use HTTPS: Enabled
- [ ] WWW redirect configured (optional)

## ☑️ Deployment

- [ ] Deploy button clicked in Coolify
- [ ] Build logs checked (no errors)
- [ ] Deployment successful message received
- [ ] Health check passing

## ☑️ Post-Deployment Testing

- [ ] Visit https://piggybankpc.uk
- [ ] HTTPS working (green padlock)
- [ ] Homepage loads correctly
- [ ] Check /health endpoint returns 200
- [ ] Register test account
- [ ] Upload test benchmark
- [ ] Verify diagnostic page shows:
  - [ ] Issues detected
  - [ ] Amazon affiliate links
  - [ ] YouTube CTAs
  - [ ] Click tracking working
- [ ] Check leaderboard shows:
  - [ ] Gaming FPS column
  - [ ] AI Tokens/s column
  - [ ] Price/Token column
  - [ ] Sorting works

## ☑️ Admin Account

- [ ] SSH into server
- [ ] Create admin account
- [ ] Test admin login
- [ ] Check /analytics access

## ☑️ Security Verification

- [ ] Debug mode OFF (check logs)
- [ ] SECRET_KEY not in git history
- [ ] .env not committed to git
- [ ] HTTPS certificate valid
- [ ] Health endpoint accessible
- [ ] File upload limits working
- [ ] Strong admin password set

## ☑️ Monitoring Setup

- [ ] Coolify auto-deploy enabled
- [ ] Health checks configured
- [ ] Log monitoring working
- [ ] Resource usage visible

## ☑️ Backup Configuration

- [ ] Database backup strategy planned
- [ ] Uploads folder backup planned
- [ ] Manual backup tested

## 🎉 Launch!

Once all boxes are checked, you're LIVE!

Visit: **https://piggybankpc.uk** 🚀

---

## 📝 Quick Commands Reference

**View logs:**
```bash
docker logs piggybankpc-leaderboard --tail 100 -f
```

**Restart container:**
```bash
docker restart piggybankpc-leaderboard
```

**Check health:**
```bash
curl https://piggybankpc.uk/health
```

**Access container shell:**
```bash
docker exec -it piggybankpc-leaderboard /bin/bash
```

**Manual backup:**
```bash
docker exec piggybankpc-leaderboard tar -czf /tmp/backup.tar.gz /app/instance /app/uploads
docker cp piggybankpc-leaderboard:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz
```

---

## 🆘 Emergency Contacts

- **Coolify Docs:** https://coolify.io/docs
- **Flask Docs:** https://flask.palletsprojects.com/
- **Cloudflare Support:** https://dash.cloudflare.com/

---

**You've got this! Time to go live! 🚀💰**
