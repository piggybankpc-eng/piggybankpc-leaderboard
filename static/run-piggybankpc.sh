#!/bin/bash
# PiggyBankPC Client Launcher
# Downloads and runs the client agent on your PC

echo "=========================================="
echo "🐷 PiggyBankPC Benchmark Client Launcher"
echo "=========================================="
echo ""

# Download client
echo "📥 Downloading client agent..."
curl -sL https://piggybankpc.uk/static/piggybankpc-client.py -o /tmp/piggybankpc-client.py

if [ $? -ne 0 ]; then
    echo "❌ Download failed!"
    exit 1
fi

echo "✓ Downloaded"
echo ""

# Make executable
chmod +x /tmp/piggybankpc-client.py

# Run client
echo "🚀 Starting client..."
echo ""
python3 /tmp/piggybankpc-client.py

# Cleanup
rm -f /tmp/piggybankpc-client.py
