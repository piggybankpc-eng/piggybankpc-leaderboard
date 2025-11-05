#!/bin/bash
# Build script for PiggyBankPC Benchmark AppImage

set -e

echo "🔨 Building PiggyBankPC Benchmark AppImage..."
echo "=============================================="

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Clean previous build
echo "📦 Cleaning previous build..."
rm -rf AppDir/usr/bin/*
rm -rf AppDir/usr/lib
rm -f PiggyBankPC-Benchmark-*.AppImage

# Create necessary directories
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/lib/python3/dist-packages
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps

# Copy benchmark scripts
echo "📋 Copying benchmark files..."
cp benchmark_runner.py AppDir/usr/bin/
cp csv_exporter.py AppDir/usr/bin/
cp security.py AppDir/usr/bin/
cp -r scripts AppDir/usr/bin/
cp -r config AppDir/usr/bin/
cp -r tools AppDir/usr/bin/ 2>/dev/null || true

# Create a simple icon (placeholder)
echo "🎨 Creating icon..."
convert -size 256x256 xc:red -fill white -gravity center \
  -pointsize 48 -annotate +0+0 'PBB' \
  AppDir/usr/share/icons/hicolor/256x256/apps/piggybankpc-benchmark.png 2>/dev/null || \
  cp /usr/share/pixmaps/python3.png AppDir/usr/share/icons/hicolor/256x256/apps/piggybankpc-benchmark.png 2>/dev/null || \
  echo "⚠ Could not create icon, AppImage will use default"

# Copy .desktop file
cp AppDir/piggybankpc-benchmark.desktop AppDir/usr/share/applications/

# Download appimagetool if not present
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "📥 Downloading appimagetool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool-x86_64.AppImage
fi

# Build the AppImage
echo "🏗️  Building AppImage..."
ARCH=x86_64 ./appimagetool-x86_64.AppImage AppDir PiggyBankPC-Benchmark.AppImage

# Make it executable
chmod +x PiggyBankPC-Benchmark.AppImage

echo ""
echo "✅ AppImage built successfully!"
echo "📦 Output: PiggyBankPC-Benchmark.AppImage"
echo "📏 Size: $(du -h PiggyBankPC-Benchmark.AppImage | cut -f1)"
echo ""
echo "🧪 Test it with: ./PiggyBankPC-Benchmark.AppImage"
echo "📤 Upload to GitHub Releases when ready!"
