#!/bin/bash
#
# Piggy Bank PC - Benchmark Suite Launcher
# Simple startup script for the USB benchmark suite
#

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$SCRIPT_DIR"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║         PIGGY BANK PC - BENCHMARK SUITE LAUNCHER              ║"
echo "║          GPU Performance Testing for YouTube                  ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python3 is not installed"
    echo "SOLUTION: Install Python3 using: sudo apt install python3"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python3 found: $PYTHON_VERSION"

# Create necessary directories
mkdir -p "$BASE_DIR/results"
mkdir -p "$BASE_DIR/logs"
mkdir -p "$BASE_DIR/config"

# Check if GPU prices config exists
if [ ! -f "$BASE_DIR/config/gpu-prices.txt" ]; then
    echo "⚠ GPU price configuration not found"
    echo "Creating default configuration..."
    mkdir -p "$BASE_DIR/config"
    cat > "$BASE_DIR/config/gpu-prices.txt" << 'EOF'
# GPU Price Configuration File
# Format: GPU_MODEL = £PRICE
# Add one GPU per line
GTX 1060 6GB = £68
GTX 1070 = £89
GTX 1070 Ti = £120
GTX 1080 Ti = £250
RTX 2080 Ti = £187
RTX 3060 12GB = £230
RTX 3090 = £600
Quadro K1200 4GB = £25
Radeon Pro WX 5100 8GB = £47
EOF
fi

echo "✓ Configuration verified"

# Check for required Python packages
echo ""
echo "Checking Python dependencies..."

# Check for psutil (system monitoring)
if ! python3 -c "import psutil" 2>/dev/null; then
    echo "⚠ Installing missing package: psutil"
    python3 -m pip install --user psutil > /dev/null 2>&1 || true
fi

# Check for GPU detection tools
if ! command -v nvidia-smi &> /dev/null; then
    echo "⚠ NVIDIA drivers not detected"
    echo "  Note: GPU tests may fail without NVIDIA drivers"
fi

# Check for benchmark tools
if ! command -v sysbench &> /dev/null; then
    echo "⚠ sysbench not found"
    echo "  CPU benchmarks may be skipped"
fi

echo "✓ Dependencies checked"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Starting Benchmark Suite..."
echo "Working directory: $BASE_DIR"
echo "Results will be saved to: $BASE_DIR/results"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# Run the benchmark suite
cd "$BASE_DIR"
python3 benchmark_runner.py "$BASE_DIR"

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Benchmark suite completed successfully"
    echo "Results saved to: $BASE_DIR/results"
else
    echo ""
    echo "❌ Benchmark suite encountered an error"
    echo "Check logs in: $BASE_DIR/logs"
    exit 1
fi
