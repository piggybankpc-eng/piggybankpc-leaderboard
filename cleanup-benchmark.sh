#!/bin/bash
# PiggyBankPC Benchmark Cleanup Script
# Removes all benchmark files and results for fresh testing

echo "=========================================="
echo "PiggyBankPC Benchmark Cleanup Script"
echo "=========================================="
echo ""

# Function to safely remove files/directories
safe_remove() {
    if [ -e "$1" ]; then
        echo "✓ Removing: $1"
        rm -rf "$1"
    else
        echo "- Not found: $1 (skipping)"
    fi
}

echo "Cleaning up benchmark files..."
echo ""

# Remove AppImage from Desktop
safe_remove "$HOME/Desktop/PiggyBankPC-Benchmark.AppImage"

# Remove AppImage from Downloads (in case downloaded there)
safe_remove "$HOME/Downloads/PiggyBankPC-Benchmark.AppImage"

# Remove instructions file
safe_remove "$HOME/Desktop/RUN_BENCHMARK.md"
safe_remove "$HOME/Downloads/RUN_BENCHMARK.md"

# Remove results directory
safe_remove "$HOME/PiggyBankPC/results"

# Remove logs directory
safe_remove "$HOME/PiggyBankPC/logs"

# Remove entire PiggyBankPC directory if empty
if [ -d "$HOME/PiggyBankPC" ]; then
    if [ -z "$(ls -A $HOME/PiggyBankPC)" ]; then
        echo "✓ Removing empty directory: $HOME/PiggyBankPC"
        rmdir "$HOME/PiggyBankPC"
    else
        echo "⚠ $HOME/PiggyBankPC not empty, keeping it"
    fi
fi

# Remove any Heaven result files from home directory
echo ""
echo "Cleaning up Heaven benchmark results..."
rm -f "$HOME"/Unigine_Heaven_Benchmark_*.html 2>/dev/null && echo "✓ Removed Heaven HTML results" || echo "- No Heaven results found"

# Remove cloned repository if exists
safe_remove "$HOME/piggybankpc-leaderboard"
safe_remove "$HOME/Desktop/piggybankpc-leaderboard"
safe_remove "$HOME/Downloads/piggybankpc-leaderboard"

echo ""
echo "=========================================="
echo "Cleanup Complete!"
echo "=========================================="
echo ""
echo "What was removed:"
echo "  - AppImage files from Desktop/Downloads"
echo "  - RUN_BENCHMARK.md instructions"
echo "  - Results directory (~PiggyBankPC/results/)"
echo "  - Logs directory (~PiggyBankPC/logs/)"
echo "  - Heaven HTML result files"
echo "  - Cloned repository (if present)"
echo ""
echo "What was kept:"
echo "  - Installed dependencies (Ollama, Unigine Heaven, etc.)"
echo "  - System packages (sysbench, python3-psutil, etc.)"
echo ""
echo "Ready for fresh test! Download and run the benchmark again."
echo ""
