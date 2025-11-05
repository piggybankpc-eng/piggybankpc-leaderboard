# PiggyBankPC Benchmark Suite

**Version:** 1.0.0
**Date:** October 2025
**Platform:** Linux (Ubuntu/Debian-based)

## Overview

The PiggyBankPC Benchmark Suite is a comprehensive testing tool designed to evaluate gaming and AI performance of budget PC builds. It combines GPU gaming benchmarks, AI/LLM inference testing, and CPU performance analysis with automatic overclock detection.

## Features

### 🎮 Gaming Performance (FPS Benchmark)
- **Interactive Heaven Benchmarking**
  - User-controlled quality and resolution settings
  - Automatic result capture from Heaven HTML output files
  - Prevents fake results or manual input errors
  - Supports multiple test configurations per session
  - Smart recommendations based on FPS results

**Supported Settings:**
- Resolutions: 1080p (1920x1080), 1440p (2560x1440), 4K (3840x2160)
- Quality Presets: Low, Medium, High, Ultra
- User selects settings manually in Heaven GUI
- Suite automatically captures: Average FPS, Min FPS, Max FPS, Resolution, Quality

**Smart Recommendations:**
- FPS ≥ 60: "Excellent! Try raising quality or resolution"
- FPS 30-59: "Playable! Consider lowering settings for 60 FPS"
- FPS < 30: "Low FPS! Try lower quality or resolution"

### 🤖 AI Performance (Ollama Benchmark)
- **LLM Inference Testing**
  - Tests local AI model performance (llama2:7b by default)
  - Measures tokens per second (tok/s)
  - Monitors GPU temperature and VRAM usage during inference
  - Real-time temperature tracking

**Metrics Captured:**
- Tokens generated
- Tokens per second
- Duration
- Average GPU temperature
- Maximum GPU temperature
- VRAM used

### 💻 CPU Performance (Sysbench/Geekbench)
- **CPU Benchmark with Overclock Analysis**
  - Automatic tool detection (Geekbench 6/5 or sysbench)
  - Multi-threaded testing using all available CPU threads
  - Real-time overclock detection and analysis

**Metrics Captured:**
- Events per second (sysbench) or Multi-core score (Geekbench)
- Test duration
- Threads used
- CPU overclock analysis
- RAM overclock analysis
- Stock performance estimates

### 🔧 Overclock Analysis (NEW!)

**CPU Overclock Detection:**
- Compares actual max frequency vs stock boost specifications
- Calculates overclock percentage above stock boost
- Supports popular CPUs:
  - Intel: i9-9900X, i9-9900K, i7-9700K
  - AMD: Ryzen 9 5950X, Ryzen 9 5900X, Ryzen 7 5800X
- Displays: Stock boost, Actual max, Overclock %

**RAM Overclock Detection:**
- Compares actual RAM speed vs JEDEC standards
- JEDEC DDR4 speeds: 2133, 2400, 2666, 2933, 3200 MHz
- Calculates overclock percentage above JEDEC
- Displays: JEDEC standard, Actual speed, Overclock %

**Performance Uplift Estimates:**
- Estimates stock CPU performance based on overclock %
- Calculates performance gain from overclocking
- Uses linear scaling assumption
- Displays: Actual score, Estimated stock score, Performance gain %

**Example Output:**
```
======================================================================
OVERCLOCK ANALYSIS
======================================================================

✓ CPU IS OVERCLOCKED!
  Stock Boost:  4.5 GHz
  Actual Max:   5.0 GHz
  Overclock:    +11.1%

💡 PERFORMANCE UPLIFT:
  Actual Score:     21759.21 events/sec
  Stock Estimate:   19584.00 events/sec
  Performance Gain: +11.1%

✓ RAM IS OVERCLOCKED!
  JEDEC Standard: 2666 MHz
  Actual Speed:   3200 MHz
  Overclock:      +20.0%

======================================================================
```

### 🔍 Hardware Detection
- **Automatic System Information Gathering**
  - CPU: Model, cores, threads, architecture, max frequency
  - GPU: Model, VRAM, driver version, clock speed, temperature
  - RAM: Total capacity, speed (MT/s), type (DDR4/DDR5), number of sticks
  - Automatic GPU price lookup from configuration

### 🔒 Security & Anti-Tampering
- **Cryptographic Signing**
  - All benchmark results signed with HMAC-SHA256
  - Hardware fingerprinting prevents result reuse on different systems
  - Timestamp verification prevents old result submission
  - Tamper detection ensures result integrity

## Architecture

### Core Components

```
benchmark-suite/
├── scripts/
│   ├── benchmark_runner.py         # Main orchestrator
│   ├── fps_benchmark.py             # Interactive Heaven FPS testing
│   ├── ai_benchmark.py              # Ollama LLM inference testing
│   ├── cpu_benchmark.py             # CPU performance testing
│   ├── overclock_analyzer.py        # NEW: Overclock detection & analysis
│   ├── hardware_detection.py        # System hardware detection
│   ├── dependency_checker.py        # Dependency verification
│   └── gpu_price_config.json        # GPU price database
├── results/                          # Benchmark results (JSON)
├── build-appimage.sh                # AppImage build script
└── README.md                        # This file
```

### Benchmark Flow

1. **Dependency Check** → Verify all required tools are installed
2. **Hardware Detection** → Gather system information
3. **FPS Benchmark** → Interactive Heaven testing with automatic result capture
4. **AI Benchmark** → Ollama LLM inference testing
5. **CPU Benchmark** → Sysbench/Geekbench with overclock analysis
6. **Result Generation** → Sign and save results to .pbr file

## Interactive FPS Testing Workflow

**How it works:**

1. **Heaven Launches** - Suite opens Unigine Heaven with GUI
2. **User Controls** - User manually selects:
   - Resolution (1080p, 1440p, 4K, etc.)
   - Quality preset (Low, Medium, High, Ultra)
   - Clicks "RUN" to start benchmark
   - Clicks "Benchmark" button when finished to save results
3. **Automatic Capture** - Suite automatically:
   - Detects new HTML result file in home directory
   - Parses FPS data (Average, Min, Max)
   - Extracts resolution and quality settings
   - No manual input required - prevents fake results!
4. **Smart Suggestions** - Suite analyzes results and recommends:
   - Raise settings if FPS is high (≥60)
   - Lower settings if FPS is low (<30)
   - Try higher resolution if performance allows
5. **Multiple Tests** - User can run additional tests or skip to AI/CPU

**Why Interactive Mode?**
- Gives users full control over test settings
- Automatic result parsing prevents typos or fake results
- Allows testing at multiple quality/resolution combinations
- Results are cryptographically signed for integrity

## Result Format

**Output File:** `benchmark_results_YYYYMMDD_HHMMSS.json`

```json
{
  "fps": {
    "benchmark_type": "unigine_heaven_interactive",
    "status": "completed",
    "configurations": {
      "2560p1440_high": {
        "status": "completed",
        "average_fps": 113.5,
        "min_fps": 17.0,
        "max_fps": 225.4,
        "resolution": "2560x1440",
        "quality": "High",
        "result_file": "/home/john/Unigine_Heaven_Benchmark_4.0_20251026_1245.html",
        "timestamp": "2025-10-26T12:45:51.772125"
      }
    },
    "timestamp": "2025-10-26T12:45:57.582443"
  },
  "ai": {
    "benchmark_type": "ollama",
    "model": "llama2:7b",
    "status": "completed",
    "tokens_generated": 1177,
    "duration_seconds": 67.49,
    "tokens_per_second": 17.44,
    "avg_gpu_temp": 48.2,
    "max_gpu_temp": 51,
    "vram_used": "10286 MiB",
    "timestamp": "2025-10-26T12:47:05.168888"
  },
  "cpu": {
    "benchmark_type": "sysbench",
    "status": "completed",
    "threads_used": 20,
    "events_per_second": 21706.87,
    "total_time_seconds": 60.0009,
    "duration_seconds": 60.02,
    "overclock_analysis": {
      "cpu": {
        "overclocked": false,
        "stock_base_ghz": 3.5,
        "stock_boost_ghz": 4.5,
        "actual_max_ghz": 4.5,
        "base_overclock_percent": 28.6,
        "boost_overclock_percent": 0.0
      },
      "ram": {
        "overclocked": false,
        "jedec_standard_mhz": 2666,
        "actual_speed_mhz": 2666,
        "overclock_percent": 0.0
      },
      "stock_performance_estimate": {}
    },
    "timestamp": "2025-10-26T12:48:05.264168"
  },
  "system_info": {
    "cpu": {
      "detected": true,
      "model": "Intel(R) Core(TM) i9-9900X CPU @ 3.50GHz",
      "cores": "10",
      "threads": "20",
      "architecture": "x86_64",
      "max_mhz": "4500.0000"
    },
    "gpu": {
      "detected": true,
      "model": "NVIDIA GeForce RTX 3060",
      "vram": "12288 MiB",
      "driver_version": "580.95.05",
      "clock_speed": "210 MHz, 405 MHz",
      "temperature": "40°C"
    },
    "ram": {
      "detected": true,
      "total": "62Gi",
      "speed": "2666 MT/s",
      "type": "DDR4",
      "sticks": "4"
    },
    "gpu_price": 230.0
  }
}
```

## Signed Result File (.pbr)

**Output File:** `piggybankpc_benchmark_YYYYMMDD_HHMMSS.pbr`

```json
{
  "version": "1.0.0",
  "timestamp": "2025-10-26T12:48:05.264168",
  "hardware_fingerprint": "a3f5e8c2d1b4...",
  "results": { /* Full benchmark results */ },
  "signature": "3a7b9f2e8d5c1a4f..."
}
```

**Security Features:**
- HMAC-SHA256 signature prevents tampering
- Hardware fingerprint tied to specific system
- Timestamp verification
- Leaderboard validates signature before accepting submission

## Dependencies

### Required Tools

**System Tools:**
- `lscpu` - CPU information
- `dmidecode` - RAM information (requires sudo)
- `nvidia-smi` - NVIDIA GPU information
- `stress-ng` - System stress testing (optional)

**Benchmark Tools:**
- **Unigine Heaven 4.0** - GPU/FPS benchmark (required)
  - Location: `~/Unigine_Heaven-4.0/`
  - Must have `heaven` launcher script
- **Ollama** - AI/LLM inference (required)
  - Service must be running: `sudo systemctl start ollama`
  - Model required: `llama2:7b`
- **Sysbench** or **Geekbench** - CPU benchmark (one required)
  - Sysbench: `sudo apt install sysbench`
  - Geekbench: Download from geekbench.com

**Python Packages:**
- `psutil` - System monitoring
- `requests` - HTTP requests for Ollama
- `cryptography` - Result signing

### Installation

**Install system dependencies:**
```bash
sudo apt update
sudo apt install sysbench stress-ng dmidecode
```

**Install Python packages:**
```bash
pip install psutil requests cryptography
```

**Install Ollama:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl start ollama
ollama pull llama2:7b
```

**Install Unigine Heaven:**
```bash
# Download from: https://benchmark.unigine.com/heaven
# Extract to ~/Unigine_Heaven-4.0/
# Ensure heaven launcher script is executable
chmod +x ~/Unigine_Heaven-4.0/heaven
```

## Usage

### Running from AppImage

```bash
./PiggyBankPC-Benchmark.AppImage
```

**Main Menu Options:**
1. **Run All Benchmarks** - Full test suite (FPS → AI → CPU)
2. **FPS Only** - Interactive Heaven testing only
3. **AI Only** - Ollama inference testing only
4. **CPU Only** - CPU performance testing only
5. **System Info** - Display hardware detection only
6. **Exit** - Quit application

### Running Individual Benchmarks

```bash
# FPS Benchmark (Interactive)
python3 scripts/fps_benchmark.py /path/to/results

# AI Benchmark
python3 scripts/ai_benchmark.py /path/to/results

# CPU Benchmark with Overclock Analysis
python3 scripts/cpu_benchmark.py /path/to/results

# Overclock Analyzer (Standalone)
python3 scripts/overclock_analyzer.py
```

### Building AppImage

```bash
cd /home/john/Desktop/benchmark-suite
./build-appimage.sh
```

**Output:** `PiggyBankPC-Benchmark.AppImage` (portable, no installation needed)

## Leaderboard Integration

### Submitting Results

1. **Run Benchmark Suite** - Complete all tests
2. **Locate .pbr File** - Find in results directory
3. **Upload to Leaderboard** - Visit website and upload
4. **Automatic Validation** - Signature verified, data extracted
5. **View Results** - Appears on leaderboard with overclock badges

### Leaderboard Display

**Your submission shows:**
- Rank with trophy icons (🏆 1st, 🥈 2nd, 🥉 3rd)
- Username with official build badge (if applicable)
- CPU and GPU models
- GPU price
- **FPS score with resolution & quality** (NEW!)
- AI tokens/sec
- **CPU benchmark score** (NEW!)
- **Overclock badges** - CPU +X%, RAM +Y% (NEW!)
- Price per FPS efficiency
- Submission date

**Filtering & Sorting:**
- Sort by: FPS, AI Tokens/sec, GPU Price, Date
- Filter by: Price range, GPU brand (NVIDIA/AMD/Intel), Time period
- Future: Filter by overclocked vs stock systems

## Benchmark Timing

**Approximate Duration:**

| Benchmark | Duration |
|-----------|----------|
| FPS (per test) | ~3-5 minutes (user-controlled) |
| AI (Ollama) | ~60-90 seconds |
| CPU (Sysbench) | ~60 seconds |
| CPU (Geekbench) | ~10-15 minutes |
| **Total (Full Suite)** | ~15-20 minutes |

## GPU Price Database

**File:** `scripts/gpu_price_config.json`

Maintains budget GPU pricing:

```json
{
  "NVIDIA GeForce GTX 1650": 100.0,
  "NVIDIA GeForce GTX 1660": 120.0,
  "NVIDIA GeForce RTX 3060": 230.0,
  "AMD Radeon RX 6600": 200.0
}
```

**To add your GPU price:**
1. Edit `scripts/gpu_price_config.json`
2. Add entry: `"Your GPU Model": price_in_gbp`
3. Rebuild AppImage

## Known CPU Specifications (Overclock Detection)

**File:** `scripts/overclock_analyzer.py` - `CPU_SPECS` dictionary

Currently supports:
- Intel: i9-9900X, i9-9900K, i7-9700K
- AMD: Ryzen 9 5950X, Ryzen 9 5900X, Ryzen 7 5800X

**To add your CPU:**
```python
CPU_SPECS = {
    "Your CPU Model": {
        "base": 3.5,    # Base frequency in GHz
        "boost": 4.5,   # Max boost frequency in GHz
        "cores": 10     # Core count
    }
}
```

If your CPU is not in the database, overclock analysis will show "overclocked: false" even if overclocked.

## Troubleshooting

### Heaven Not Launching
**Problem:** Heaven exits immediately or doesn't show GUI

**Solution:**
- Ensure using `heaven` launcher script, not `heaven_x64` binary
- Check permissions: `chmod +x ~/Unigine_Heaven-4.0/heaven`
- Verify X11 display: `echo $DISPLAY`

### Ollama Connection Failed
**Problem:** AI benchmark fails with connection error

**Solution:**
```bash
# Check Ollama service
sudo systemctl status ollama

# Start if not running
sudo systemctl start ollama

# Verify model is installed
ollama list

# Pull model if missing
ollama pull llama2:7b
```

### Sysbench Not Found
**Problem:** CPU benchmark skipped

**Solution:**
```bash
# Install sysbench
sudo apt install sysbench

# Or install Geekbench
# Download from: https://www.geekbench.com/
```

### Permission Denied for dmidecode
**Problem:** RAM overclock detection fails

**Solution:**
- dmidecode requires sudo access
- Run benchmark suite with: `sudo ./PiggyBankPC-Benchmark.AppImage`
- Or add to sudoers for passwordless dmidecode

### AppImage Won't Execute
**Problem:** "Permission denied" when running AppImage

**Solution:**
```bash
chmod +x PiggyBankPC-Benchmark.AppImage
./PiggyBankPC-Benchmark.AppImage
```

## Version History

### Version 1.0.0 (October 2025)
- ✨ Interactive FPS testing with automatic result capture
- ✨ Overclock analysis for CPU and RAM
- ✨ Performance uplift estimates
- ✨ Smart recommendations based on FPS results
- ✨ Multi-configuration FPS testing support
- ✨ Enhanced result format with resolution & quality
- ✨ Cryptographic signing for tamper-proof results
- ✨ Leaderboard integration with overclock badges
- 🔧 Automatic hardware detection
- 🔧 Dependency checking
- 🔧 AppImage packaging for easy distribution

## Contributing

To add support for your hardware:

1. **Add GPU Price:**
   - Edit `scripts/gpu_price_config.json`
   - Add your GPU model and UK price

2. **Add CPU Specs:**
   - Edit `scripts/overclock_analyzer.py`
   - Add your CPU to `CPU_SPECS` dictionary

3. **Submit PR:**
   - Fork repository
   - Make changes
   - Test with your hardware
   - Submit pull request

## License

MIT License - See LICENSE file for details

## Support

- **Issues:** Report bugs or request features on GitHub
- **Community:** Join Discord for support and discussion
- **YouTube:** Watch @piggybankpc for build guides and tips

## Credits

**Created by:** PiggyBankPC
**YouTube:** @piggybankpc
**Purpose:** Budget PC gaming & AI performance testing

**Built with:**
- Python 3.x
- Unigine Heaven 4.0
- Ollama
- Sysbench/Geekbench
- Flask (Leaderboard)
- SQLite (Leaderboard Database)

---

**Ready to benchmark your budget build? Run the suite and see how you rank! 🏆**
