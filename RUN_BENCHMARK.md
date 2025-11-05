# PiggyBankPC Benchmark Suite - Quick Start Guide

## Running the Benchmark

### Simple Command:
```bash
~/Desktop/PiggyBankPC-Benchmark.AppImage
```

### Or using full path:
```bash
$HOME/Desktop/PiggyBankPC-Benchmark.AppImage
```

---

## What to Expect:

1. **Dependency Check** - Auto-installs missing tools:
   - python3-psutil
   - curl (for Ollama)
   - Ollama (AI benchmarking) - 637MB download
   - Unigine Heaven (FPS benchmarking) - 273MB download
   - TinyLlama model (~637MB)

2. **Main Menu** - Choose:
   - Option 1: Quick Benchmark (FPS only - ~15 min)
   - Option 2: Full Suite (FPS + AI + CPU - ~90 min)
   - Option 3: Custom Tests

3. **Results Location**:
   ```
   ~/PiggyBankPC/results/
   ```

4. **Files Generated**:
   - `benchmark_results_TIMESTAMP.csv` - Spreadsheet format
   - `benchmark_results_TIMESTAMP.json` - Raw data
   - `piggybank_benchmark_TIMESTAMP_HWID.pbr` - **Upload this to leaderboard!**

---

## Upload to Leaderboard:

1. Go to: https://piggybankpc.uk/submit
2. Upload the `.pbr` file from `~/PiggyBankPC/results/`
3. Your results will appear on the leaderboard!

---

## After Overclocking:

Run the benchmark again to generate new results with OC settings:
```bash
~/Desktop/PiggyBankPC-Benchmark.AppImage
```

The overclock analyzer will automatically detect and report OC status!

---

## Troubleshooting:

**If AppImage won't run:**
```bash
chmod +x ~/Desktop/PiggyBankPC-Benchmark.AppImage
```

**If dependencies fail to install:**
- Approve sudo prompts when asked
- Ensure internet connection is active

**View logs:**
```bash
cat ~/PiggyBankPC/logs/benchmark_*.log
```

---

## Master Source Code:
```
/media/$USER/BENCHMARK/updated/benchmark-suite/
```

## Rebuild AppImage:
```bash
cd /media/$USER/BENCHMARK/updated/benchmark-suite
bash build-appimage.sh
```

---

**Ready to benchmark!** 🚀
