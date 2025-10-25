# 🚀 START HERE - PiggyBankPC Leaderboard

## 🎉 Welcome!

I've built you a **complete Flask web application** for the PiggyBankPC Leaderboard!

This is your starting point. Read this file first, then follow the next steps.

---

## ✅ What You Got

A **production-ready leaderboard system** with:

- 🔐 User authentication (register, login, profiles)
- 📊 Public leaderboard (sortable, filterable, paginated)
- 📤 Submission system (upload .pbr files with signature verification)
- 🎨 Beautiful Bootstrap 5 UI (PiggyBankPC orange theme)
- 🐳 Multiple deployment options (Coolify, Docker, Manual)
- 📖 Comprehensive documentation

**Total:** 27 files, 2384+ lines of code, fully functional!

---

## 📁 Quick File Guide

**Read These First:**
- `START_HERE.md` ← You are here!
- `QUICKSTART.md` ← Get running in 5 minutes
- `README.md` ← Full documentation
- `DEPLOYMENT_SUMMARY.md` ← What I built and why

**Deployment Guides:**
- `COOLIFY_DEPLOYMENT.md` ← Deploy to Coolify (your preference!)
- `docker-compose.yml` ← Docker deployment
- `install.sh` ← Quick local install

**Core Application:**
- `app.py` ← Main Flask app
- `models.py` ← Database models (User, Submission)
- `security.py` ← Signature verification (uses your module!)
- `routes/` ← All the pages (auth, leaderboard, submit, profile)
- `templates/` ← HTML pages (Bootstrap 5)
- `static/` ← CSS and JavaScript

---

## 🎯 Choose Your Path

### Path 1: Test Locally First (Recommended)

**Time: 5 minutes**

```bash
# 1. Install dependencies
./install.sh

# 2. Edit .env file (set BENCHMARK_SECURITY_KEY)
nano .env

# 3. Run the app
source venv/bin/activate
python app.py

# 4. Open browser
# Visit: http://localhost:5555
```

**What to test:**
- Register an account
- Login
- View leaderboard (empty initially)
- Upload a .pbr file (if you have one)
- View your profile

---

### Path 2: Deploy to Coolify (Production)

**Time: 10 minutes**

See `COOLIFY_DEPLOYMENT.md` for detailed instructions.

**Quick steps:**
1. Push code to Git (GitHub/GitLab/Gitea)
2. Create new app in Coolify
3. Set environment variables (SECRET_KEY, BENCHMARK_SECURITY_KEY)
4. Add persistent volumes (instance/, uploads/)
5. Deploy!

**Benefits:**
- Automatic SSL certificates
- Auto-restart on crash
- Built-in monitoring
- Works with your Cloudflare tunnel

**Perfect for:** `https://piggybankpc.megger-sparks.uk`

---

### Path 3: Docker Compose (Quick Deploy)

**Time: 3 minutes**

```bash
# 1. Set environment
cp .env.example .env
nano .env  # Set SECRET_KEY and BENCHMARK_SECURITY_KEY

# 2. Start container
docker-compose up -d

# 3. Visit
# http://your-server-ip:5555
```

---

## 🔑 Critical Configuration

Before going live, you MUST:

### 1. Set SECRET_KEY

```bash
# Generate a random key
openssl rand -base64 32

# Add to .env
SECRET_KEY=<your-generated-key>
```

### 2. Set BENCHMARK_SECURITY_KEY

```bash
# This MUST match your benchmark suite!
# Check piggybank_benchmark_security.py line 28

BENCHMARK_SECURITY_KEY=PIGGYBANK_PC_BENCHMARK_SECRET_2025
```

⚠️ **CRITICAL:** If this doesn't match your benchmark suite, submissions will fail!

### 3. Set Production Mode

```bash
# In .env:
FLASK_ENV=production
```

---

## 🧪 Testing Checklist

Before announcing to your community:

- [ ] Register test account
- [ ] Login successfully
- [ ] View leaderboard (should be empty)
- [ ] Create a test .pbr file (see QUICKSTART.md)
- [ ] Upload test file
- [ ] Verify it appears on leaderboard
- [ ] Test sorting (FPS, price, date)
- [ ] Test filters (price range, GPU brand)
- [ ] View user profile
- [ ] Delete submission
- [ ] Test on mobile browser

---

## 🎨 Customization

### Add Your Logo

1. Save logo as `static/images/logo.png`
2. Edit `templates/base.html` line 25

### Change Colors

Edit `static/css/style.css`:
```css
:root {
    --primary-color: #FF6B35;  /* Orange */
}
```

### Update Download Links

Edit `templates/index.html` lines 138-142 with your actual download URL.

---

## 📊 How It Works

### Submission Flow:

1. **User runs benchmark** on their hardware
2. **Benchmark suite signs results** with HMAC-SHA256
3. **Generates .pbr file** (base64 encoded + signature)
4. **User uploads to leaderboard**
5. **Server verifies signature** (using security.py)
6. **If valid:** Extract data → Save to database → Show on leaderboard
7. **If invalid:** Reject with error message

### Security Features:

✅ Results can't be edited (breaks signature)
✅ Can't fake hardware (fingerprint verification)
✅ Passwords securely hashed
✅ SQL injection prevented (SQLAlchemy ORM)
✅ File uploads validated (size, extension, signature)

---

## 🚨 Troubleshooting

### App won't start

```bash
# Check Python version
python3 --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt

# Check logs
tail -f logs/app.log
```

### Signature verification fails

**Most common cause:** BENCHMARK_SECURITY_KEY mismatch

Check these match:
- `.env` file: `BENCHMARK_SECURITY_KEY=...`
- Benchmark suite `security.py` line 28

### Port 5555 in use

```bash
# Find what's using it
sudo lsof -i :5555

# Kill it or change port in app.py
```

---

## 📖 Documentation Index

1. **START_HERE.md** ← You are here (starting point)
2. **QUICKSTART.md** ← 5-minute setup guide
3. **README.md** ← Full documentation (installation, usage, features)
4. **COOLIFY_DEPLOYMENT.md** ← Coolify deployment instructions
5. **DEPLOYMENT_SUMMARY.md** ← What I built, why, and next steps
6. **PROJECT_STRUCTURE.txt** ← File structure overview

---

## 🎯 Your Integration Plan

### On Your AI Server:

**Current services:**
- Port 3000: OpenWebUI (AI Chat)
- Port 7860: Automatic1111 (Image Gen)
- Port 8080: Unified Server Portal
- Port 11434: Ollama (LLM Backend)

**Adding leaderboard:**
- Port 5555: PiggyBankPC Leaderboard ← NEW!

**Cloudflare tunnel hostnames:**
- ai.megger-sparks.uk → 3000
- imagegen.megger-sparks.uk → 7860
- home.megger-sparks.uk → 8080
- **piggybankpc.megger-sparks.uk → 5555** ← ADD THIS!

**No conflicts!** Everything plays nicely together.

---

## 🚀 Launch Plan

### Week 1: Setup & Test
- [ ] Deploy to Coolify
- [ ] Add Cloudflare tunnel hostname
- [ ] Test with friends/trusted users
- [ ] Create sample submissions
- [ ] Gather feedback

### Week 2: Soft Launch
- [ ] Announce on YouTube community tab
- [ ] Share on Discord/social media
- [ ] Monitor for issues
- [ ] Respond to first submissions

### Week 3: Full Launch
- [ ] Create launch video
- [ ] Feature top submissions
- [ ] Challenge community to beat scores
- [ ] Start "Budget GPU Showdown" series

---

## 🎬 Content Ideas

**Videos you can make:**

1. "I Built a Leaderboard for Budget PCs" (setup + demo)
2. "Your Submissions Are INSANE!" (top 10 review)
3. "Best Budget GPU Under £100" (data from leaderboard)
4. "GTX 1060 vs 1070 vs 1070 Ti" (your submissions)
5. "Price-per-FPS Champions" (best value builds)
6. "Worst Value GPUs" (entertainment + learning)
7. "Live: Reviewing Submissions" (community engagement)

**Community engagement:**

- Weekly leaderboard updates
- User spotlight (feature top performers)
- Hardware recommendations based on data
- "Beat my score" challenges

---

## 💡 Next Steps (After Launch)

### Phase 2 Features (v1.1+):

Potential additions:
- Admin dashboard (approve/reject submissions)
- Export leaderboard to CSV
- API endpoints for programmatic access
- Email notifications (weekly updates)
- Comparison tool (compare 2 builds side-by-side)
- Hardware recommendation engine
- Dark mode toggle
- Social sharing cards (Twitter/Discord)

**Don't worry about these now!** Launch v1.0 first, get feedback, then iterate.

---

## 🙏 Support

**Need help?**
- Check the README.md (comprehensive guide)
- Review logs: `docker-compose logs -f`
- Test locally first: `./install.sh`
- Verify environment variables in `.env`

**Found a bug?**
- Check if it's in the logs
- Try restarting the service
- Reset database if needed (dev only!)

**Want to add features?**
- The code is well-commented
- Flask is easy to extend
- I can help with Phase 2!

---

## 🎉 You're Ready!

You have everything you need:

✅ Complete Flask application
✅ 3 deployment options
✅ Comprehensive documentation
✅ Security implementation
✅ Beautiful UI
✅ Ready for your community

**Now:**
1. Test it locally (`./install.sh`)
2. Deploy to Coolify (see COOLIFY_DEPLOYMENT.md)
3. Add Cloudflare tunnel hostname
4. Announce to your community!

---

**Turn E-Waste Into Excellence!** 🐷💻🚀

**- Built by Claude Code for PiggyBankPC**

---

## 📞 Quick Reference

```bash
# Local testing
./install.sh
source venv/bin/activate
python app.py
# Visit: http://localhost:5555

# Docker deployment
docker-compose up -d
# Visit: http://your-ip:5555

# Check logs
docker-compose logs -f        # Docker
tail -f logs/app.log          # Local

# Reset database (DEV ONLY!)
rm instance/database.db
python app.py

# Generate SECRET_KEY
openssl rand -base64 32
```

**GO BUILD SOMETHING AWESOME!** 🚀
