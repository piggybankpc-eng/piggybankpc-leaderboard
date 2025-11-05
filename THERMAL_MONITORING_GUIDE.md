# PiggyBankPC Thermal Monitoring & CPU AI Benchmark - Complete Guide

## Overview

This document covers the comprehensive thermal monitoring system and CPU AI benchmark added to the PiggyBankPC benchmark suite.

---

## Table of Contents

1. [Features Added](#features-added)
2. [File Locations](#file-locations)
3. [How It Works](#how-it-works)
4. [Thermal Data Collected](#thermal-data-collected)
5. [Database Schema](#database-schema)
6. [User Experience](#user-experience)
7. [Revenue Integration](#revenue-integration)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)

---

## Features Added

### 1. Thermal Monitoring During Benchmarks

**What it does:**
- Monitors GPU and CPU temperature/utilization during all benchmarks
- Collects data every 5 seconds
- Saves thermal metrics to .pbr files
- Displays on leaderboard after upload

**Benchmarks with thermal monitoring:**
- ✅ FPS Benchmark (Heaven) - Interactive mode with background thread
- ✅ AI Token Benchmark (GPU) - GPU & CPU metrics
- ✅ AI Token Benchmark (CPU) - CPU metrics (NEW!)

### 2. CPU AI Token Benchmark

**What it does:**
- Runs Ollama LLM on CPU only (disables GPU)
- Tests CPU token generation performance
- Monitors CPU thermal behavior under AI workload
- Compares CPU vs GPU AI performance

### 3. Intel 13th/14th Gen CPU Tracking

**What it does:**
- Automatically detects Intel 13th/14th gen CPUs
- Flags submissions in database
- Shows BIOS update warnings
- Allows admin to track affected systems

### 4. Diagnostic Analysis

**What it does:**
- Detects CPU thermal throttling (85°C+)
- Detects GPU thermal throttling (83°C+)
- Recommends thermal paste, coolers, fans
- Links to affiliate products with pricing

---

## File Locations

### Core Benchmark Files

#### FPS Benchmark
```
Location: scripts/fps_benchmark.py
Lines: 255-346 (Interactive Heaven thermal monitoring)

Key Functions:
- _run_heaven_interactive() - Main interactive benchmark
- Background monitoring thread (lines 269-306)
- Thermal metrics collection (lines 319-336)
```

#### AI Benchmark (GPU)
```
Location: scripts/ai_benchmark.py
Lines: 112-265 (GPU AI benchmark with thermal monitoring)

Key Functions:
- run_ollama_benchmark() - GPU AI benchmark
- Thermal monitoring during token generation (lines 177-204)
- Comprehensive thermal_metrics (lines 230-247)
```

#### AI Benchmark (CPU)
```
Location: scripts/ai_benchmark.py
Lines: 282-423 (CPU-only AI benchmark)

Key Functions:
- run_ollama_cpu_benchmark() - CPU AI benchmark
- Forces CPU-only with CUDA_VISIBLE_DEVICES=''
- CPU thermal monitoring (lines 352-366)
- CPU thermal_metrics (lines 381-390)
```

#### Hardware Detection
```
Location: scripts/hardware_detection.py
Lines: 432-472 (CPU stats collection)

Key Functions:
- get_current_cpu_stats() - Get CPU temp & utilization
- Uses lm-sensors or /sys/class/thermal fallback
- Parses top output for CPU utilization
```

### Web Application Files

#### Database Models
```
Location: models.py
Lines: 97-107 (Thermal metrics columns)
Lines: 135-136 (Intel 13th/14th gen tracking)

Columns Added:
- gpu_temp_min, gpu_temp_avg, gpu_temp_max
- gpu_util_min, gpu_util_avg, gpu_util_max
- cpu_temp_min, cpu_temp_avg, cpu_temp_max
- cpu_util_min, cpu_util_avg, cpu_util_max
- intel_13_14_gen_cpu (boolean, indexed)
```

#### Submission Processing
```
Location: routes/submit.py
Lines: 116-151 (Extract thermal data from pbr files)
Lines: 292-295 (Detect Intel 13th/14th gen CPUs)

Key Functions:
- extract_submission_data() - Parses pbr files
- is_intel_13_14_gen_cpu() - Detects affected Intel CPUs
```

#### Diagnostics Engine
```
Location: utils/diagnostics.py
Lines: 44-85 (CPU thermal throttling detection)
Lines: 87-116 (GPU thermal throttling detection)

Key Functions:
- analyze_submission() - Main diagnostic analysis
- Detects thermal throttling
- Recommends products with affiliate links
```

#### Diagnostic Configuration
```
Location: diagnostic_config.py
Lines: 9-16 (YouTube video links)
Lines: 18-30 (Affiliate product links)
Lines: 32-100 (Product database)

Products:
- Arctic MX-4 CPU thermal paste (£6.99)
- Noctua NT-H1 GPU thermal paste (£8.95)
- Noctua NH-U12S CPU cooler (£49.99)
- Thermal pads, case fans, RAM
```

#### Leaderboard Display
```
Location: templates/leaderboard.html
Lines: 288-343 (Thermal metrics display section)

Features:
- Shows GPU/CPU temp (min/avg/max)
- Shows GPU/CPU utilization (min/avg/max)
- Color-coded warnings (yellow/red for high temps)
- "Throttling!" badge when temps exceed limits
```

### Installation & Deployment

#### Install Script
```
Location: static/install-piggybankpc.sh
Lines: 293-338 (Version checking & AppImage download)
Lines: 367-426 (Benchmark type selection menu)

Options:
1. Quick (FPS only)
2. Full (FPS + AI + CPU)
3. FPS only
4. AI/Tokens (GPU)
5. AI/Tokens (CPU only) ← NEW!
6. CPU only
7. Skip
```

#### Benchmark Runner
```
Location: benchmark_runner.py (and AppDir/usr/bin/benchmark_runner.py)
Lines: 198-227 (Custom benchmark menu)
Lines: 452-465 (Command-line arguments)
Lines: 470-515 (Argument handling)

Command-line flags:
--quick      # Quick benchmark (FPS only)
--full       # Full suite
--fps        # FPS only
--ai         # AI GPU benchmark
--ai-cpu     # AI CPU benchmark ← NEW!
--cpu        # CPU benchmark
```

#### Build & Version Files
```
Location: build-appimage.sh
- Builds AppImage from AppDir/
- Updates static/appimage-version.txt
- Version format: Unix timestamp

Location: static/appimage-version.txt
- Current version: 1762380996
- Checked by install script for updates
```

### Database Migrations

```
Location: migrations/add_thermal_metrics.sql
- Adds 10 thermal metric columns to submissions table

Location: migrations/add_intel_cpu_tracking.sql
- Adds intel_13_14_gen_cpu column
- Creates index for fast queries
```

---

## How It Works

### 1. FPS Benchmark Flow (Interactive Heaven)

```
User runs installer → Chooses FPS benchmark
    ↓
Install script: "$APPIMAGE_PATH" --fps --no-deps-check
    ↓
benchmark_runner.py: Calls fps_benchmark.run_benchmark()
    ↓
fps_benchmark.py: run_unigine_heaven() → _run_heaven_interactive()
    ↓
Launch Heaven GUI with subprocess.Popen()
    ↓
Start background monitoring thread:
  - Every 5 seconds:
    - Get GPU temp/util from hardware_detector
    - Get CPU temp/util from hardware_detector
    - Append to lists: gpu_temps, gpu_utils, cpu_temps, cpu_utils
    ↓
process.wait() - Wait for user to close Heaven
    ↓
Stop monitoring thread
    ↓
Parse Heaven HTML results file (FPS data)
    ↓
Calculate thermal_metrics (min/avg/max for all)
    ↓
Add thermal_metrics to result dict
    ↓
Save to .pbr file (base64-encoded JSON)
    ↓
User uploads .pbr to leaderboard
    ↓
Server: extract_submission_data() parses thermal_metrics
    ↓
Server: Saves to database (gpu_temp_max, cpu_temp_max, etc.)
    ↓
Server: analyze_submission() detects thermal throttling
    ↓
Server: Creates DiagnosticIssue with product recommendations
    ↓
Leaderboard: User sees thermal data in detail dropdown
```

### 2. AI CPU Benchmark Flow

```
User runs installer → Chooses "5. AI/Tokens (CPU only)"
    ↓
Install script: "$APPIMAGE_PATH" --ai-cpu --no-deps-check
    ↓
benchmark_runner.py: Calls ai_benchmark.run_ollama_cpu_benchmark()
    ↓
ai_benchmark.py: Set env CUDA_VISIBLE_DEVICES='' (disable GPU)
    ↓
Run: ollama run llama2:7b "prompt..."
    ↓
Monitor output line-by-line:
  - Every 10 lines:
    - Get CPU temp from hardware_detector
    - Get CPU utilization from hardware_detector
    - Append to lists: cpu_temps, cpu_utils
    ↓
Calculate tokens/second
    ↓
Calculate thermal_metrics (cpu_temp_min/avg/max, cpu_util_min/avg/max)
    ↓
Save to .pbr file
    ↓
(Same upload/processing flow as above)
```

### 3. Intel CPU Detection Flow

```
User uploads .pbr file
    ↓
routes/submit.py: extract_submission_data()
    ↓
Create Submission object with cpu_model
    ↓
is_intel_13_14_gen_cpu(cpu_model) - Check for patterns:
  - "13th gen", "14th gen"
  - "i9-13", "i9-14", "i7-13", "i7-14", etc.
    ↓
If detected:
  - submission.intel_13_14_gen_cpu = True
  - Log warning
    ↓
Save to database
    ↓
Diagnostics: Show BIOS update warning in thermal throttling issues
```

---

## Thermal Data Collected

### GPU Metrics

| Metric | Description | Unit | Collected From |
|--------|-------------|------|----------------|
| gpu_temp_min | Minimum GPU temperature | °C | nvidia-smi |
| gpu_temp_avg | Average GPU temperature | °C | nvidia-smi |
| gpu_temp_max | Maximum GPU temperature | °C | nvidia-smi |
| gpu_util_min | Minimum GPU utilization | % | nvidia-smi |
| gpu_util_avg | Average GPU utilization | % | nvidia-smi |
| gpu_util_max | Maximum GPU utilization | % | nvidia-smi |

### CPU Metrics

| Metric | Description | Unit | Collected From |
|--------|-------------|------|----------------|
| cpu_temp_min | Minimum CPU temperature | °C | lm-sensors or /sys/class/thermal |
| cpu_temp_avg | Average CPU temperature | °C | lm-sensors or /sys/class/thermal |
| cpu_temp_max | Maximum CPU temperature | °C | lm-sensors or /sys/class/thermal |
| cpu_util_min | Minimum CPU utilization | % | top command |
| cpu_util_avg | Average CPU utilization | % | top command |
| cpu_util_max | Maximum CPU utilization | % | top command |

### Sampling Rate

- **FPS Benchmark**: Every 5 seconds during Heaven test
- **AI GPU Benchmark**: Every 10 lines of output (~every 1-2 seconds)
- **AI CPU Benchmark**: Every 10 lines of output (~every 5-10 seconds, slower on CPU)

---

## Database Schema

### Submissions Table (Thermal Metrics)

```sql
ALTER TABLE submissions ADD COLUMN gpu_temp_min FLOAT;
ALTER TABLE submissions ADD COLUMN gpu_temp_avg FLOAT;
ALTER TABLE submissions ADD COLUMN gpu_temp_max FLOAT;
ALTER TABLE submissions ADD COLUMN gpu_util_min FLOAT;
ALTER TABLE submissions ADD COLUMN gpu_util_avg FLOAT;
ALTER TABLE submissions ADD COLUMN gpu_util_max FLOAT;

ALTER TABLE submissions ADD COLUMN cpu_temp_min FLOAT;
ALTER TABLE submissions ADD COLUMN cpu_temp_avg FLOAT;
ALTER TABLE submissions ADD COLUMN cpu_temp_max FLOAT;
ALTER TABLE submissions ADD COLUMN cpu_util_min FLOAT;
ALTER TABLE submissions ADD COLUMN cpu_util_avg FLOAT;
ALTER TABLE submissions ADD COLUMN cpu_util_max FLOAT;
```

### Submissions Table (Intel CPU Tracking)

```sql
ALTER TABLE submissions ADD COLUMN intel_13_14_gen_cpu BOOLEAN DEFAULT 0;
CREATE INDEX idx_intel_13_14_gen_cpu ON submissions(intel_13_14_gen_cpu);
```

### Query Examples

```sql
-- Find all submissions with thermal throttling
SELECT id, user_id, gpu_model, cpu_model, gpu_temp_max, cpu_temp_max
FROM submissions
WHERE gpu_temp_max >= 83 OR cpu_temp_max >= 85;

-- Find Intel 13th/14th gen submissions
SELECT id, user_id, cpu_model, cpu_temp_max
FROM submissions
WHERE intel_13_14_gen_cpu = 1;

-- Average temperatures by GPU model
SELECT gpu_model,
       AVG(gpu_temp_avg) as avg_gpu_temp,
       AVG(cpu_temp_avg) as avg_cpu_temp
FROM submissions
WHERE gpu_temp_avg IS NOT NULL
GROUP BY gpu_model
ORDER BY avg_gpu_temp DESC;
```

---

## User Experience

### Installation & First Run

1. User runs install script:
   ```bash
   curl -sL piggybankpc.uk/static/install-piggybankpc.sh -o install.sh
   chmod +x install.sh
   ./install.sh
   ```

2. Installer checks for lm-sensors:
   - If not found: Prompts to install
   - If declined: Uses /sys/class/thermal fallback

3. User sees benchmark menu:
   ```
   Select Benchmark Type:
     1. Quick (FPS only, ~15 min)
     2. Full (FPS + AI + CPU, ~90 min)
     3. FPS only
     4. AI/Tokens (GPU)
     5. AI/Tokens (CPU only) ← NEW!
     6. CPU only
     7. Skip (run later manually)
   ```

### During FPS Benchmark

1. Heaven launches in fullscreen
2. Background: Thermal monitoring collects data every 5 seconds
3. User runs benchmark manually:
   - Click settings
   - Click RUN
   - Let it run ~1 minute
   - Click "Benchmark" button to save
   - Close Heaven
4. Terminal shows: "📊 Collecting thermal data in background..."
5. Script parses HTML results + thermal data
6. Saves to .pbr file

### During AI CPU Benchmark

1. Ollama starts generating tokens on CPU
2. Terminal shows: "Generating tokens on CPU........"
3. Background: CPU temp/util monitored every 10 lines
4. Takes longer than GPU (~5-10x slower)
5. Completes and shows tokens/second
6. Thermal data saved to .pbr file

### Leaderboard View

1. User uploads .pbr file
2. Leaderboard shows submission
3. Click row to expand details:
   ```
   Detailed System Information

   CPU Details          RAM Details           GPU Test Settings
   ...                  ...                   ...

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   🌡️ Thermal Metrics (During Benchmark)

   GPU Thermal Data                CPU Thermal Data
   Temperature: 65°C / 78°C / 82°C Temperature: 52°C / 65°C / 89°C
                (min/avg/max)                   (min/avg/max) ⚠️ Throttling!
   Utilization: 75% / 92% / 98%    Utilization: 35% / 58% / 85%
                (min/avg/max)                   (min/avg/max)
   ```

4. If thermal throttling detected:
   - User sees diagnostic page with:
     - Issue description
     - FPS gain estimate
     - Fix difficulty/time/cost
     - YouTube video link
     - Affiliate product recommendations

---

## Revenue Integration

### Diagnostic Issues with Products

#### CPU Thermal Throttling (85°C+)

**Products Recommended (in order):**
1. Arctic MX-4 Thermal Paste (£6.99) - **First recommendation** (cheapest fix)
2. Noctua NH-U12S CPU Cooler (£49.99) - If paste doesn't work
3. Arctic P12 120mm Case Fan (£7.99) - Improve airflow

**Why this order:**
- Thermal paste is the cheapest/easiest fix first
- Most CPUs just need fresh paste
- Only recommend cooler upgrade if paste isn't enough

#### GPU Thermal Throttling (83°C+)

**Products Recommended:**
1. Noctua NT-H1 Thermal Paste (£8.95) - For GPU die
2. Gelid GP-Extreme Thermal Pads (£8.99) - For memory chips
3. Arctic P12 120mm Case Fan (£7.99) - Improve airflow

### Affiliate Link Configuration

```python
# Location: diagnostic_config.py

AFFILIATE_LINKS = {
    'Noctua NT-H1': 'https://amzn.to/4nj7P1z',
    'Arctic MX-4': 'https://amzn.to/PLACEHOLDER',  # TODO: Add your link
    'thermal_pads': 'https://amzn.to/4ht4USI',
    'noctua_cooler': 'https://amzn.to/PLACEHOLDER',  # TODO: Add your link
    'arctic_fan': 'https://amzn.to/PLACEHOLDER',  # TODO: Add your link
}
```

**To add your affiliate links:**
1. Sign up for Amazon Associates
2. Generate affiliate links for each product
3. Replace PLACEHOLDER entries in diagnostic_config.py
4. Git commit and push changes

---

## Testing

### Test Thermal Monitoring

**On a test PC:**

```bash
# Run FPS benchmark only
~/PiggyBankPC/PiggyBankPC-Benchmark.AppImage --fps --no-deps-check

# Check if thermal data is in the .pbr file
cd ~/PiggyBankPC/results
ls -lt *.pbr | head -1  # Find newest file

# Decode and check thermal_metrics
python3 -c "
import base64
import json
with open('filename.pbr', 'r') as f:
    lines = f.readlines()
    data = json.loads(base64.b64decode(lines[-1].strip()))
    fps = data['data']['results']['fps']
    for config_name, config in fps['configurations'].items():
        if 'thermal_metrics' in config:
            print('✓ Thermal metrics found!')
            print(json.dumps(config['thermal_metrics'], indent=2))
        else:
            print('✗ No thermal_metrics!')
"
```

### Test CPU AI Benchmark

```bash
# Run CPU AI benchmark
~/PiggyBankPC/PiggyBankPC-Benchmark.AppImage --ai-cpu --no-deps-check

# Should show:
# "RUNNING AI TOKEN GENERATION BENCHMARK (CPU ONLY)"
# "Backend: CPU (GPU disabled)"
# "Generating tokens on CPU........"

# Check results
cd ~/PiggyBankPC/results
ls -lt *.pbr | head -1
```

### Test Intel CPU Detection

```bash
# Run Python test
cd ~/Desktop/piggybankpc-leaderboard
source venv/bin/activate

python3 -c "
from routes.submit import is_intel_13_14_gen_cpu

# Test cases
cpus = [
    'Intel(R) Core(TM) i9-13900K',
    'Intel(R) Core(TM) i7-14700K',
    'Intel(R) Core(TM) i5-12600K',  # Should be False
    'AMD Ryzen 9 5900X',             # Should be False
]

for cpu in cpus:
    result = is_intel_13_14_gen_cpu(cpu)
    print(f'{cpu}: {result}')
"
```

### Test Leaderboard Display

1. Upload a .pbr file with thermal data
2. Go to leaderboard
3. Find your submission
4. Click to expand details
5. Verify "Thermal Metrics" section appears
6. Check temperatures are color-coded:
   - Normal: black text
   - Warning (80-84°C GPU, 85-89°C CPU): yellow
   - Critical (85°C+ GPU, 90°C+ CPU): red
   - "Throttling!" badge appears at thresholds

---

## Troubleshooting

### No Thermal Data in .pbr File

**Symptoms:**
- .pbr file uploads successfully
- But thermal_metrics section is missing or empty

**Possible Causes:**

1. **Running old AppImage version**
   ```bash
   # Check version
   cat ~/PiggyBankPC/config/appimage-version.txt

   # Should be: 1762380996 or newer
   # If older, re-run installer and say 'y' to update
   ```

2. **lm-sensors not working**
   ```bash
   # Test sensors
   sensors

   # If error, reconfigure:
   sudo sensors-detect --auto

   # Or check fallback:
   cat /sys/class/thermal/thermal_zone0/temp
   # Should show temperature in millidegrees (e.g., 45000 = 45°C)
   ```

3. **nvidia-smi not working**
   ```bash
   # Test GPU detection
   nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader

   # Should show temperature like: 45
   ```

4. **Running from wrong location**
   ```bash
   # Always run from:
   ~/PiggyBankPC/PiggyBankPC-Benchmark.AppImage

   # NOT from:
   # ~/Desktop/benchmark-suite/...
   # ./PiggyBankPC-Benchmark.AppImage (wrong directory)
   ```

### Thermal Data Not Showing on Leaderboard

**Check database:**
```python
from app import app, db
from models import Submission

with app.app_context():
    sub = Submission.query.order_by(Submission.id.desc()).first()
    print(f'GPU Max Temp: {sub.gpu_temp_max}')
    print(f'CPU Max Temp: {sub.cpu_temp_max}')
    # Should NOT be None
```

**If None:**
1. Check migrations were applied:
   ```bash
   sqlite3 instance/leaderboard.db
   .schema submissions
   # Should include gpu_temp_min, gpu_temp_max, etc.
   ```

2. Check extraction in routes/submit.py:
   ```python
   # Add debug logging at line 148
   print(f"DEBUG thermal_metrics: {thermal_metrics}")
   ```

### CPU AI Benchmark Uses GPU Instead of CPU

**Symptoms:**
- AI benchmark runs fast (like GPU speed)
- GPU utilization high during "CPU-only" benchmark

**Fix:**
Check environment variable is set:
```python
# In ai_benchmark.py line 333:
env = os.environ.copy()
env['CUDA_VISIBLE_DEVICES'] = ''  # This MUST be set

# Verify with:
print(f"CUDA_VISIBLE_DEVICES: {env.get('CUDA_VISIBLE_DEVICES')}")
# Should print: CUDA_VISIBLE_DEVICES:
```

### Install Script Shows Wrong Version

**Problem:**
- Install script says "Latest version already installed"
- But AppImage is old

**Fix:**
```bash
# Force refresh
rm ~/PiggyBankPC/config/appimage-version.txt
rm ~/PiggyBankPC/PiggyBankPC-Benchmark.AppImage

# Re-run installer
./install.sh
# Should prompt to download new version
```

---

## Version History

### v1.0 (1762375125) - Initial Release
- Basic FPS benchmark
- No thermal monitoring

### v2.0 (1762377415) - Thermal Monitoring Added
- Added thermal monitoring to FPS benchmark
- But only in non-interactive mode (not used by installer)
- **Bug**: Interactive mode had no thermal monitoring

### v2.1 (1762379492) - Fixed Interactive Mode
- **CRITICAL FIX**: Added thermal monitoring to interactive Heaven mode
- Background thread monitors temps while user runs Heaven
- This is the first version that actually works!

### v2.2 (1762380695) - CPU AI Benchmark Added
- New: AI Token Benchmark (CPU only)
- Enhanced AI GPU benchmark with CPU monitoring
- Comprehensive thermal_metrics for both AI benchmarks

### v2.3 (1762380996) - Current Version
- Added CPU AI benchmark to install script menu (option 5)
- Added --ai-cpu command-line argument
- Install script now offers CPU AI testing

---

## Future Enhancements

### Potential Additions

1. **Real-time Temperature Display**
   - Show overlay during fullscreen benchmarks
   - Requires X11/Wayland overlay tool

2. **Historical Thermal Tracking**
   - Track temperature trends over multiple runs
   - Show thermal degradation over time
   - Alert users if temps increasing

3. **Thermal Throttling Severity Levels**
   - Light: 83-85°C GPU, 85-90°C CPU
   - Moderate: 85-88°C GPU, 90-95°C CPU
   - Severe: 88°C+ GPU, 95°C+ CPU

4. **Automatic Product Recommendations**
   - Based on specific GPU/CPU model
   - Consider case size, cooler compatibility
   - Price range filtering

5. **Before/After Thermal Paste Tracking**
   - Link submissions before and after repaste
   - Show FPS gain + temperature drop
   - Gamification: "Thermal Hero" achievements

---

## Support & Contact

- **GitHub**: https://github.com/piggybankpc-eng/piggybankpc-leaderboard
- **Website**: https://piggybankpc.uk
- **Install Script**: https://piggybankpc.uk/static/install-piggybankpc.sh

---

## Credits

Thermal monitoring system and CPU AI benchmark developed with Claude Code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
