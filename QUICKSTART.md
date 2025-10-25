# 🚀 Quick Start Guide - PiggyBankPC Leaderboard

Get the leaderboard running in under 5 minutes!

## 🎯 Choose Your Method

### 🐳 Docker Compose (Easiest)

**Perfect if you have Docker installed:**

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd piggybankpc-leaderboard

# 2. Set environment variables
cp .env.example .env
nano .env  # Set SECRET_KEY and BENCHMARK_SECURITY_KEY

# 3. Start it up!
docker-compose up -d

# 4. Visit http://localhost:5555
```

Done! The leaderboard is running.

---

### 💻 Local Development (Fastest for testing)

**Perfect for testing on your desktop:**

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd piggybankpc-leaderboard

# 2. Run the installer
chmod +x install.sh
./install.sh

# 3. Edit .env (set BENCHMARK_SECURITY_KEY)
nano .env

# 4. Start the server
source venv/bin/activate
python app.py
```

Visit `http://localhost:5555` and you're ready!

---

### ☁️ Coolify (Best for production)

**Perfect for your AI server with Cloudflare tunnel:**

1. **Push to Git:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-git-url>
   git push -u origin main
   ```

2. **Create in Coolify:**
   - Open Coolify dashboard
   - New → Application → Public Repository
   - Paste your Git URL
   - Set port: `5555`

3. **Set Environment Variables in Coolify:**
   ```
   FLASK_ENV=production
   SECRET_KEY=<generate-with-openssl-rand-base64-32>
   BENCHMARK_SECURITY_KEY=PIGGYBANK_PC_BENCHMARK_SECRET_2025
   ```

4. **Add Persistent Volumes:**
   - `./instance` → `/app/instance`
   - `./uploads` → `/app/uploads`

5. **Deploy!**

Coolify handles nginx, SSL, and auto-restart.

---

## 🧪 Test It Works

### 1. Access the Landing Page
Open `http://localhost:5555` (or your domain)

You should see:
- PiggyBankPC logo and title
- Statistics cards (0 submissions initially)
- "Download Benchmark Suite" button
- Register/Login links

### 2. Register an Account
1. Click **Register**
2. Fill in:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `password123`
3. Click **Register**

You should be redirected to login.

### 3. Login
1. Enter username/email and password
2. Click **Login**

You should see "Welcome back, testuser!"

### 4. View Your Profile
1. Click your username in the navbar
2. Click **My Profile**

You should see:
- Your statistics (all zeros)
- Empty submissions list
- "Submit Your First Benchmark" button

### 5. View Leaderboard
1. Click **Leaderboard** in navbar

You should see:
- Filter options
- Empty leaderboard (no submissions yet)
- Statistics showing 1 unique user

---

## 📤 Test Submission (Need a .pbr file)

To fully test submissions, you need a valid `.pbr` file from the benchmark suite.

### Create a Test .pbr File

If you don't have one yet, you can create a mock one for testing:

```bash
# On the server/locally, run Python
python3

# Then paste this:
from security import BenchmarkSecurity
from pathlib import Path

security = BenchmarkSecurity(base_dir='.', signing_key='PIGGYBANK_PC_BENCHMARK_SECRET_2025')

test_results = {
    'system_info': {
        'cpu': {'model': 'Intel i9-9900X', 'cores': '10'},
        'gpu': {'model': 'GTX 1060 6GB', 'vram': '6GB'},
        'gpu_price': 68,
        'ram': {'total': '64GB'}
    },
    'fps': {
        'status': 'completed',
        'average_fps': 85.5,
        'min_fps': 75.2,
        'max_fps': 95.1
    },
    'ai': {
        'status': 'completed',
        'tokens_per_second': 45.3
    },
    'cpu': {
        'status': 'completed',
        'events_per_second': 1234.56
    }
}

signed = security.sign_results(test_results)
filepath = security.create_submission_file(signed, Path('uploads'))
print(f"Test file created: {filepath}")
```

This creates a valid `.pbr` file you can upload!

### Upload Test File

1. Login to the leaderboard
2. Click **Submit**
3. Upload the `.pbr` file
4. Click **Upload & Submit**

You should see:
- Success message
- Redirect to leaderboard
- Your submission appears in the table!

---

## ✅ Success Checklist

- [ ] Landing page loads correctly
- [ ] Can register new account
- [ ] Can login with credentials
- [ ] Can view profile page
- [ ] Can view leaderboard
- [ ] Can upload .pbr file (if you have one)
- [ ] Submission appears on leaderboard
- [ ] Can logout

## 🔧 Troubleshooting Quick Fixes

### Port 5555 already in use
```bash
# Find what's using it
sudo lsof -i :5555

# Kill it or change port in app.py
```

### Database errors
```bash
# Delete and recreate
rm instance/database.db
python app.py  # Auto-creates new database
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Signature verification fails
Make sure `BENCHMARK_SECURITY_KEY` in `.env` matches the key in `security.py` line 28!

---

## 🎉 You're Ready!

Your PiggyBankPC Leaderboard is up and running!

**Next Steps:**
1. Customize the landing page download links
2. Add your logo to `static/images/`
3. Deploy to production (see README.md)
4. Share with your YouTube community!

---

**Need Help?**
- Full docs: [README.md](README.md)
- Coolify deployment: [COOLIFY_DEPLOYMENT.md](COOLIFY_DEPLOYMENT.md)
- Check logs: `docker-compose logs -f` or `tail -f logs/app.log`
