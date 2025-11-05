#!/bin/bash
# PiggyBankPC Benchmark Installer
# Installs dependencies and downloads benchmark suite

set -e  # Exit on error

echo "============================================"
echo "PiggyBankPC Benchmark Installer"
echo "============================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Please do not run this script as root"
    echo "We will ask for sudo password when needed"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "ERROR: Cannot detect operating system"
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Step 1: Check system hardware
echo "=== Step 1: Checking System Hardware ==="
echo ""

# Check CPU
if command -v lscpu >/dev/null 2>&1; then
    CPU_MODEL=$(lscpu | grep "Model name:" | cut -d: -f2 | xargs)
    echo "CPU: $CPU_MODEL"
else
    echo "WARNING: lscpu not found, cannot detect CPU"
    CPU_MODEL="Unknown"
fi

# Check GPU
if command -v nvidia-smi >/dev/null 2>&1; then
    GPU_MODEL=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo "Unknown")
    echo "GPU: $GPU_MODEL"
else
    echo "WARNING: nvidia-smi not found"
    echo "INFO: This is needed for NVIDIA GPU detection"
    GPU_MODEL="Unknown"
fi

# Check RAM
if command -v free >/dev/null 2>&1; then
    RAM_TOTAL=$(free -h | grep Mem: | awk '{print $2}')
    echo "RAM: $RAM_TOTAL"
else
    echo "WARNING: free command not found"
    RAM_TOTAL="Unknown"
fi

echo ""

# Step 2: Check dependencies
echo "=== Step 2: Checking Dependencies ==="
echo ""

MISSING_DEPS=""

# Check for Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo "[ ] Python 3: NOT FOUND (REQUIRED)"
    MISSING_DEPS="$MISSING_DEPS python3"
else
    PYTHON_VERSION=$(python3 --version)
    echo "[x] Python 3: $PYTHON_VERSION"
fi

# Check for curl
if ! command -v curl >/dev/null 2>&1; then
    echo "[ ] curl: NOT FOUND (REQUIRED)"
    MISSING_DEPS="$MISSING_DEPS curl"
else
    echo "[x] curl: Found"
fi

# Check for Unigine Heaven (optional)
if [ -d "$HOME/Unigine_Heaven-4.0" ]; then
    echo "[x] Unigine Heaven: Found at $HOME/Unigine_Heaven-4.0"
    HAS_HEAVEN=1
else
    echo "[ ] Unigine Heaven: Not found"
    HAS_HEAVEN=0
    INSTALL_HEAVEN=1
fi

# Check for Ollama (optional)
if command -v ollama >/dev/null 2>&1; then
    echo "[x] Ollama: Found (for AI benchmarks)"
    HAS_OLLAMA=1
else
    echo "[ ] Ollama: Not found"
    HAS_OLLAMA=0
    INSTALL_OLLAMA=1
fi

# Check for sysbench (optional)
if command -v sysbench >/dev/null 2>&1; then
    echo "[x] Sysbench: Found (for CPU benchmarks)"
    HAS_SYSBENCH=1
else
    echo "[ ] Sysbench: Not found"
    HAS_SYSBENCH=0
    INSTALL_SYSBENCH=1
fi

echo ""

# Step 3: Install missing required dependencies
if [ -n "$MISSING_DEPS" ]; then
    echo "=== Step 3: Installing Required Dependencies ==="
    echo ""
    echo "Missing: $MISSING_DEPS"
    echo ""
    read -p "Install missing dependencies? (y/n): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
            echo "Running: sudo apt update && sudo apt install -y $MISSING_DEPS"
            sudo apt update && sudo apt install -y $MISSING_DEPS
        elif [ "$OS" = "fedora" ]; then
            echo "Running: sudo dnf install -y $MISSING_DEPS"
            sudo dnf install -y $MISSING_DEPS
        elif [ "$OS" = "arch" ]; then
            echo "Running: sudo pacman -S --noconfirm $MISSING_DEPS"
            sudo pacman -S --noconfirm $MISSING_DEPS
        else
            echo "ERROR: Unsupported OS for automatic installation"
            echo "Please install manually: $MISSING_DEPS"
            exit 1
        fi
        echo ""
        echo "Dependencies installed!"
    else
        echo "Skipping dependency installation"
        echo "WARNING: Benchmark may not work without required dependencies"
    fi
else
    echo "=== Step 3: All Required Dependencies Present ==="
fi

echo ""

# Step 4: Install optional benchmark tools
echo "=== Step 4: Installing Optional Benchmark Tools ==="
echo ""

# Install Unigine Heaven
if [ -n "$INSTALL_HEAVEN" ]; then
    echo "Installing Unigine Heaven (for accurate FPS benchmarks)..."
    read -p "Download and install Unigine Heaven? (~1.5GB download) (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Downloading Unigine Heaven 4.0..."

        HEAVEN_URL="https://assets.unigine.com/d/Unigine_Heaven-4.0.run"
        HEAVEN_INSTALLER="/tmp/Unigine_Heaven-4.0.run"

        curl -L "$HEAVEN_URL" -o "$HEAVEN_INSTALLER"

        if [ -f "$HEAVEN_INSTALLER" ]; then
            chmod +x "$HEAVEN_INSTALLER"
            echo "Running installer..."
            "$HEAVEN_INSTALLER"
            rm -f "$HEAVEN_INSTALLER"
            echo "[x] Unigine Heaven installed!"
            HAS_HEAVEN=1
        else
            echo "Download failed, will use fallback benchmark"
        fi
    else
        echo "Skipping Unigine Heaven (will use fallback benchmark)"
    fi
    echo ""
fi

# Install Ollama
if [ -n "$INSTALL_OLLAMA" ]; then
    echo "Installing Ollama (for AI/LLM benchmarks)..."
    read -p "Download and install Ollama? (~500MB) (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Downloading Ollama installer..."
        curl -fsSL https://ollama.com/install.sh | sh

        if command -v ollama >/dev/null 2>&1; then
            echo "[x] Ollama installed!"
            echo ""
            echo "Downloading llama2:7b model (for AI benchmark)..."
            echo "This may take several minutes..."
            ollama pull llama2:7b
            echo "[x] LLM model downloaded!"
            HAS_OLLAMA=1
        else
            echo "Installation failed, AI benchmark will be skipped"
        fi
    else
        echo "Skipping Ollama (AI benchmark will be skipped)"
    fi
    echo ""
fi

# Install Sysbench
if [ -n "$INSTALL_SYSBENCH" ]; then
    echo "Installing Sysbench (for CPU benchmarks)..."
    read -p "Install Sysbench? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
            sudo apt install -y sysbench
        elif [ "$OS" = "fedora" ]; then
            sudo dnf install -y sysbench
        elif [ "$OS" = "arch" ]; then
            sudo pacman -S --noconfirm sysbench
        fi

        if command -v sysbench >/dev/null 2>&1; then
            echo "[x] Sysbench installed!"
            HAS_SYSBENCH=1
        fi
    else
        echo "Skipping Sysbench (CPU benchmark will be skipped)"
    fi
    echo ""
fi

echo ""

# Step 5: Download benchmark AppImage
echo "=== Step 5: Downloading Benchmark AppImage ==="
echo ""

DOWNLOAD_DIR="$HOME/Desktop"
mkdir -p "$DOWNLOAD_DIR"

APPIMAGE_PATH="$DOWNLOAD_DIR/PiggyBankPC-Benchmark.AppImage"

if [ -f "$APPIMAGE_PATH" ]; then
    echo "AppImage already exists at: $APPIMAGE_PATH"
    read -p "Re-download? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing AppImage"
    else
        echo "Downloading from piggybankpc.uk..."
        curl -L "https://piggybankpc.uk/static/PiggyBankPC-Benchmark.AppImage" \
             -o "$APPIMAGE_PATH"
        chmod +x "$APPIMAGE_PATH"
        echo "Downloaded to: $APPIMAGE_PATH"
    fi
else
    echo "Downloading from piggybankpc.uk..."
    curl -L "https://piggybankpc.uk/static/PiggyBankPC-Benchmark.AppImage" \
         -o "$APPIMAGE_PATH"
    chmod +x "$APPIMAGE_PATH"
    echo "Downloaded to: $APPIMAGE_PATH"
fi

echo ""

# Step 5: Ask for GPU price
echo "=== Step 5: GPU Price Information ==="
echo ""
echo "Detected GPU: $GPU_MODEL"
read -p "How much did your GPU cost? (in GBP): " GPU_PRICE

# Save to config
mkdir -p "$HOME/PiggyBankPC/config"
echo "$GPU_MODEL = £$GPU_PRICE" >> "$HOME/PiggyBankPC/config/gpu-prices.txt"
echo "Price saved!"
echo ""

# Step 6: Ready to run
echo "============================================"
echo "Installation Complete!"
echo "============================================"
echo ""
echo "Your system:"
echo "  CPU: $CPU_MODEL"
echo "  GPU: $GPU_MODEL (£$GPU_PRICE)"
echo "  RAM: $RAM_TOTAL"
echo ""
echo "AppImage location:"
echo "  $APPIMAGE_PATH"
echo ""
echo "Select Benchmark Type:"
echo "  1. Quick (FPS only, ~15 min)"
echo "  2. Full (FPS + AI + CPU, ~90 min)"
echo "  3. FPS only"
echo "  4. AI/Tokens only"
echo "  5. CPU only"
echo "  6. Skip (run later manually)"
echo ""
read -p "Choice (1-6): " BENCHMARK_CHOICE
echo ""

case $BENCHMARK_CHOICE in
    1)
        echo "Starting Quick benchmark (FPS only, ~15 min)..."
        echo ""
        "$APPIMAGE_PATH" --quick --no-deps-check
        BENCHMARK_RAN=1
        ;;
    2)
        echo "Starting Full benchmark (FPS + AI + CPU, ~90 min)..."
        echo ""
        "$APPIMAGE_PATH" --full --no-deps-check
        BENCHMARK_RAN=1
        ;;
    3)
        echo "Starting FPS benchmark..."
        echo ""
        "$APPIMAGE_PATH" --fps --no-deps-check
        BENCHMARK_RAN=1
        ;;
    4)
        echo "Starting AI/Tokens benchmark..."
        echo ""
        "$APPIMAGE_PATH" --ai --no-deps-check
        BENCHMARK_RAN=1
        ;;
    5)
        echo "Starting CPU benchmark..."
        echo ""
        "$APPIMAGE_PATH" --cpu --no-deps-check
        BENCHMARK_RAN=1
        ;;
    6)
        echo "Skipping benchmark. You can run it anytime with:"
        echo "  $APPIMAGE_PATH"
        BENCHMARK_RAN=0
        ;;
    *)
        echo "Invalid choice. Skipping benchmark."
        echo "You can run it anytime with:"
        echo "  $APPIMAGE_PATH"
        BENCHMARK_RAN=0
        ;;
esac

if [ "$BENCHMARK_RAN" -eq 1 ]; then
    echo ""
    echo "Benchmark complete!"
    echo "Results saved to: $HOME/PiggyBankPC/results/"
    echo ""
    echo "Next steps:"
    echo "1. Go to https://piggybankpc.uk/submit"
    echo "2. Upload the .pbr file from results folder"
    echo "3. View your score on the leaderboard!"
fi

echo ""
echo "Thank you for using PiggyBankPC!"
