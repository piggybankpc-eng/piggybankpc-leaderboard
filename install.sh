#!/bin/bash
# PiggyBankPC Leaderboard - Quick Installation Script

set -e

echo "=================================="
echo "PiggyBankPC Leaderboard Installer"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Install it with: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p instance uploads logs

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env

    # Generate a random SECRET_KEY
    SECRET_KEY=$(openssl rand -base64 32)
    sed -i "s|your-secret-key-here-generate-with-openssl-rand-base64-32|$SECRET_KEY|" .env

    echo "✓ .env file created with random SECRET_KEY"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and set your BENCHMARK_SECURITY_KEY!"
    echo "   This MUST match the key in your benchmark suite."
fi

echo ""
echo "=================================="
echo "✅ Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file and set BENCHMARK_SECURITY_KEY:"
echo "   nano .env"
echo ""
echo "2. Start development server:"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "3. Visit http://localhost:5555"
echo ""
echo "For production deployment, see README.md"
echo ""
