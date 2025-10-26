#!/bin/bash
cd /home/john/Desktop/piggybankpc-leaderboard

# Load environment variables
export SECRET_KEY="Mt4OKdKRVms7XlYZ_hB_RU_3wI41134xzlGwQShaG_k"
export BENCHMARK_SECURITY_KEY="VSo3wxz9QsoDXAG22JH83__HA2i9AA8QjGy5u4EHJXk"
export FLASK_ENV="production"
export FLASK_APP="app.py"
export DATABASE_URL="sqlite:////home/john/Desktop/piggybankpc-leaderboard/instance/database.db"
export DOMAIN="piggybankpc.uk"
export YOUTUBE_CHANNEL="@piggybankpc"
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Email Configuration
export MAIL_SERVER="smtp.gmail.com"
export MAIL_PORT="587"
export MAIL_USE_TLS="true"
export MAIL_USERNAME="piggybankpc@gmail.com"
export MAIL_PASSWORD="cifx tsde xiob xims"
export MAIL_DEFAULT_SENDER="noreply@piggybankpc.uk"

# Activate venv
source venv/bin/activate

# Create logs directory
mkdir -p logs

# Start Gunicorn
gunicorn --bind 0.0.0.0:5555 \
         --workers 4 \
         --timeout 120 \
         --access-logfile logs/access.log \
         --error-logfile logs/error.log \
         --log-level info \
         --daemon \
         --pid gunicorn.pid \
         app:app

sleep 1

if [ -f gunicorn.pid ]; then
    echo "🚀 Production server started on port 5555!"
    echo "PID: $(cat gunicorn.pid)"
else
    echo "❌ Server failed to start. Check logs/error.log"
fi
