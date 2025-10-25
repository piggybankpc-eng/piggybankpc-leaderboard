# 🐷 PiggyBankPC Leaderboard

A Flask-based web application for the PiggyBankPC Benchmark Suite. Users can submit their benchmark results and compete on a public leaderboard showcasing budget hardware performance.

## 🚀 Features

- **🔐 User Authentication** - Secure registration and login system
- **📊 Public Leaderboard** - Compare budget builds and find the best value hardware
- **📤 Submission System** - Upload tamper-proof `.pbr` benchmark files
- **🔒 Cryptographic Verification** - All submissions are verified using HMAC-SHA256 signatures
- **🎯 Advanced Filtering** - Sort by FPS, price, GPU brand, and time period
- **👤 User Profiles** - View submission history and personal statistics
- **📱 Responsive Design** - Works perfectly on desktop and mobile
- **🐳 Docker Ready** - Easy deployment with Docker and Coolify

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Deployment Options](#-deployment-options)
  - [Option 1: Coolify (Recommended)](#option-1-coolify-recommended)
  - [Option 2: Docker Compose](#option-2-docker-compose)
  - [Option 3: Manual Installation](#option-3-manual-installation)
- [Configuration](#️-configuration)
- [Usage](#-usage)
- [Security](#-security)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)

## ⚡ Quick Start

### Prerequisites

- Python 3.8+ or Docker
- Git
- (Optional) Domain name for production

### Clone the Repository

```bash
git clone https://github.com/yourusername/piggybankpc-leaderboard.git
cd piggybankpc-leaderboard
```

### Quick Test (Development Mode)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

Visit `http://localhost:5555` in your browser.

## 🚀 Deployment Options

### Option 1: Coolify (Recommended)

**Best for:** Easy deployment with automatic SSL, monitoring, and backups

See [COOLIFY_DEPLOYMENT.md](COOLIFY_DEPLOYMENT.md) for detailed instructions.

**Quick Summary:**
1. Create new application in Coolify
2. Connect your Git repository
3. Set environment variables (SECRET_KEY, BENCHMARK_SECURITY_KEY)
4. Configure persistent volumes for `/app/instance` and `/app/uploads`
5. Deploy!

Coolify handles everything: nginx proxy, SSL certificates, restarts, and monitoring.

---

### Option 2: Docker Compose

**Best for:** Self-hosted deployment with minimal configuration

#### Step 1: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set your values
nano .env
```

**Required changes in `.env`:**
```bash
SECRET_KEY=<generate-with-openssl-rand-base64-32>
BENCHMARK_SECURITY_KEY=PIGGYBANK_PC_BENCHMARK_SECRET_2025
```

#### Step 2: Build and Run

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The application will be available at `http://your-server-ip:5555`

#### Step 3: Nginx Reverse Proxy (Optional)

If you want to use a domain name with SSL:

```nginx
# /etc/nginx/sites-available/piggybankpc

server {
    listen 80;
    server_name piggybankpc.yourdomain.com;

    location / {
        proxy_pass http://localhost:5555;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site and get SSL certificate:
```bash
sudo ln -s /etc/nginx/sites-available/piggybankpc /etc/nginx/sites-enabled/
sudo certbot --nginx -d piggybankpc.yourdomain.com
sudo systemctl reload nginx
```

---

### Option 3: Manual Installation

**Best for:** Development or custom server configurations

#### Step 1: Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# Fedora/RHEL
sudo dnf install python3 python3-pip nginx
```

#### Step 2: Set Up Application

```bash
# Create application directory
sudo mkdir -p /var/www/piggybankpc-leaderboard
cd /var/www/piggybankpc-leaderboard

# Clone repository
sudo git clone https://github.com/yourusername/piggybankpc-leaderboard.git .

# Create virtual environment
sudo python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create necessary directories
mkdir -p instance uploads

# Set permissions
sudo chown -R www-data:www-data /var/www/piggybankpc-leaderboard
```

#### Step 3: Configure Environment

```bash
# Create .env file
sudo nano .env
```

Add:
```bash
FLASK_ENV=production
SECRET_KEY=<generate-random-key>
BENCHMARK_SECURITY_KEY=PIGGYBANK_PC_BENCHMARK_SECRET_2025
```

#### Step 4: Create systemd Service

```bash
sudo nano /etc/systemd/system/piggybankpc.service
```

Add:
```ini
[Unit]
Description=PiggyBankPC Leaderboard
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/piggybankpc-leaderboard
Environment="PATH=/var/www/piggybankpc-leaderboard/venv/bin"
ExecStart=/var/www/piggybankpc-leaderboard/venv/bin/gunicorn \
    --bind 0.0.0.0:5555 \
    --workers 4 \
    --timeout 120 \
    'app:create_app()'

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable piggybankpc
sudo systemctl start piggybankpc
sudo systemctl status piggybankpc
```

#### Step 5: Configure Nginx (same as Docker option above)

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FLASK_ENV` | No | `development` | Flask environment (`development` or `production`) |
| `SECRET_KEY` | **Yes (prod)** | Random | Secret key for session encryption |
| `BENCHMARK_SECURITY_KEY` | **Yes** | Default key | HMAC key for verifying benchmark submissions |
| `DATABASE_URL` | No | SQLite | Database connection string |
| `UPLOAD_FOLDER` | No | `uploads` | Directory for storing `.pbr` files |

### Security Configuration

**CRITICAL:** Before deploying to production:

1. **Generate a secure SECRET_KEY:**
   ```bash
   openssl rand -base64 32
   ```

2. **Set BENCHMARK_SECURITY_KEY** to match your benchmark suite:
   - This key MUST be the same in both the leaderboard and the benchmark suite
   - Keep it secret - don't commit it to version control
   - If you change it, old submissions won't verify

3. **Use HTTPS** in production (Coolify handles this automatically)

## 📖 Usage

### For Users

#### 1. Register an Account
- Visit `/register`
- Choose a username (publicly visible)
- Provide email and password (min 8 characters)

#### 2. Run the Benchmark Suite
- Download from the landing page
- Run on your Ubuntu system with NVIDIA GPU
- Wait for all tests to complete
- Find your `.pbr` file in `submissions/` folder

#### 3. Submit Results
- Log in to the leaderboard
- Go to `/submit`
- Upload your `.pbr` file
- Results are automatically verified and added to the leaderboard!

#### 4. View Leaderboard
- Browse all submissions at `/leaderboard`
- Filter by price range, GPU brand, time period
- Sort by FPS, price-per-FPS, or date
- Click usernames to view their profiles

### For Administrators

#### Create Admin User

```bash
# If using Docker:
docker exec -it piggybankpc-leaderboard python3

# If manual install:
cd /var/www/piggybankpc-leaderboard
source venv/bin/activate
python3
```

Then in Python shell:
```python
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

## 🔒 Security

### How Submissions Are Verified

1. User runs the benchmark suite on their hardware
2. Suite generates results with hardware fingerprint
3. Results are signed with HMAC-SHA256 using the secret key
4. Signed package is base64 encoded into a `.pbr` file
5. User uploads `.pbr` to the leaderboard
6. Leaderboard decodes and verifies the signature
7. If valid → added to database | If invalid → rejected

### Anti-Tampering Protection

- ✅ **Cryptographic signing** prevents result modification
- ✅ **Hardware fingerprinting** ties results to specific hardware
- ✅ **Timestamp verification** ensures submission freshness
- ✅ **Signature comparison** uses constant-time to prevent timing attacks

### Additional Security Measures

- Password hashing with Werkzeug (bcrypt-based)
- CSRF protection ready (add Flask-WTF if needed)
- SQL injection protection (SQLAlchemy ORM)
- File upload validation (size, extension)
- Session security (httponly cookies)

## 🛠️ Development

### Project Structure

```
piggybankpc-leaderboard/
├── app.py                      # Main application factory
├── config.py                   # Configuration classes
├── models.py                   # Database models (User, Submission)
├── security.py                 # Benchmark security module
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker Compose configuration
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Authentication routes
│   ├── leaderboard.py          # Leaderboard display
│   ├── main.py                 # Landing page
│   ├── profile.py              # User profiles
│   └── submit.py               # Submission handling
│
├── templates/
│   ├── base.html               # Base template
│   ├── index.html              # Landing page
│   ├── leaderboard.html        # Leaderboard table
│   ├── login.html              # Login form
│   ├── register.html           # Registration form
│   ├── profile.html            # User profile
│   └── submit.html             # Upload form
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom styles
│   └── js/
│       └── main.js             # Custom JavaScript
│
├── instance/                   # Database (auto-created)
└── uploads/                    # Uploaded .pbr files
```

### Database Schema

**Users Table:**
- `id` (Primary Key)
- `username` (Unique, indexed)
- `email` (Unique, indexed)
- `password_hash`
- `created_at`
- `is_admin`

**Submissions Table:**
- `id` (Primary Key)
- `user_id` (Foreign Key → users.id)
- `hardware_fingerprint`
- `cpu_model`, `gpu_model`, `ram_total`
- `gpu_price`
- `fps_avg`, `fps_min`, `fps_max`
- `ai_tokens_per_sec`, `cpu_score`
- `submission_date`, `verified`
- `pbr_filename`, `benchmark_version`

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run Flask in debug mode
export FLASK_ENV=development
python app.py

# Check for errors in logs
tail -f logs/app.log
```

### Adding Features

Want to contribute? Here are some ideas:

- [ ] Admin dashboard for managing submissions
- [ ] API endpoints for programmatic access
- [ ] Export leaderboard to CSV/JSON
- [ ] Hardware comparison tool
- [ ] Email notifications
- [ ] Dark mode toggle
- [ ] Social sharing cards

## 🐛 Troubleshooting

### Application won't start

**Check Python version:**
```bash
python3 --version  # Should be 3.8+
```

**Check dependencies:**
```bash
pip install -r requirements.txt
```

**Check logs:**
```bash
# Docker:
docker-compose logs -f

# systemd:
sudo journalctl -u piggybankpc -f
```

### Database errors

**Reset database (WARNING: Deletes all data):**
```bash
rm instance/database.db
python app.py  # Will recreate tables
```

### Submission verification fails

**Check security key matches:**
- `.env` file: `BENCHMARK_SECURITY_KEY=...`
- Benchmark suite: `piggybank_benchmark_security.py` line 28

**Keys MUST be identical!**

### Port 5555 already in use

**Find what's using it:**
```bash
sudo lsof -i :5555
```

**Change port:**
- Edit `app.py` line (change 5555 to another port)
- Edit `docker-compose.yml` ports section
- Edit Dockerfile EXPOSE directive

## 📊 Performance Tips

### For Production

- Use PostgreSQL instead of SQLite (better concurrency)
- Enable Redis for session storage
- Use Nginx caching for static files
- Enable gzip compression
- Set up CDN for Bootstrap/Font Awesome

### Database Migration to PostgreSQL

```bash
# Install psycopg2
pip install psycopg2-binary

# Update .env
DATABASE_URL=postgresql://user:password@localhost/piggybankpc

# Create database
createdb piggybankpc

# Tables will auto-create on first run
```

## 📜 License

This project is part of the PiggyBankPC suite.
Free to use for personal and educational purposes.

## 🙏 Credits

- **PiggyBankPC** - Benchmark suite and concept
- **Flask** - Web framework
- **Bootstrap 5** - UI framework
- **Font Awesome** - Icons

## 🔗 Links

- [PiggyBankPC YouTube](https://youtube.com/@piggybankpc)
- [Benchmark Suite Repository](#)
- [Report Issues](#)

---

**Built with ❤️ for the budget PC community**

*Turn E-Waste Into Excellence!* 🐷💻
