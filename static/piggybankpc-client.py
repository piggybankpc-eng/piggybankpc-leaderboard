#!/usr/bin/env python3
"""
PiggyBankPC Client Agent
Runs on user's PC to execute benchmarks and report to server
"""
import subprocess
import sys
import os
import json
import platform
from pathlib import Path
import urllib.request
import time

# Configuration
SERVER_URL = "https://piggybankpc.uk"
CLIENT_VERSION = "1.0.0"


class PiggyBankPCClient:
    """Client agent for running benchmarks locally"""

    def __init__(self):
        self.home_dir = Path.home()
        self.work_dir = self.home_dir / "PiggyBankPC"
        self.work_dir.mkdir(exist_ok=True)

        self.system_info = {}
        self.dependencies_ok = False
        self.appimage_path = None

    def print_header(self):
        """Display client header"""
        print("=" * 70)
        print("🐷 PiggyBankPC Client Agent v" + CLIENT_VERSION)
        print("=" * 70)
        print()

    def detect_hardware(self):
        """Detect local system hardware"""
        print("🔍 Detecting system hardware...")

        self.system_info = {
            'cpu': {},
            'gpu': {},
            'ram': {},
            'os': platform.system()
        }

        # Detect CPU
        try:
            if platform.system() == 'Linux':
                result = subprocess.run(['lscpu'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'Model name:' in line:
                            self.system_info['cpu']['model'] = line.split(':', 1)[1].strip()
                        elif 'CPU(s):' in line and 'On-line' not in line:
                            self.system_info['cpu']['cores'] = line.split(':', 1)[1].strip()
                    self.system_info['cpu']['detected'] = True
                    print(f"  ✓ CPU: {self.system_info['cpu'].get('model', 'Unknown')}")
        except Exception as e:
            self.system_info['cpu'] = {'detected': False, 'error': str(e)}
            print(f"  ⚠ CPU: Could not detect - {e}")

        # Detect GPU
        try:
            if platform.system() == 'Linux':
                result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.system_info['gpu']['model'] = result.stdout.strip()
                    self.system_info['gpu']['detected'] = True
                    print(f"  ✓ GPU: {self.system_info['gpu']['model']}")
        except Exception as e:
            self.system_info['gpu'] = {'detected': False, 'error': str(e)}
            print(f"  ⚠ GPU: Could not detect - {e}")

        # Detect RAM
        try:
            if platform.system() == 'Linux':
                result = subprocess.run(['free', '-h'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith('Mem:'):
                            parts = line.split()
                            if len(parts) >= 2:
                                self.system_info['ram']['total'] = parts[1]
                                self.system_info['ram']['detected'] = True
                                print(f"  ✓ RAM: {parts[1]}")
        except Exception as e:
            self.system_info['ram'] = {'detected': False, 'error': str(e)}
            print(f"  ⚠ RAM: Could not detect - {e}")

        print()
        return self.system_info

    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("📋 Checking dependencies...")

        missing = []

        # Check for Unigine Heaven
        heaven_paths = [
            self.home_dir / "Unigine_Heaven-4.0",
            Path("/opt/unigine/heaven"),
            self.home_dir / ".local/share/unigine/heaven"
        ]

        heaven_found = False
        for path in heaven_paths:
            if path.exists():
                heaven_found = True
                print(f"  ✓ Unigine Heaven found at {path}")
                break

        if not heaven_found:
            print("  ⚠ Unigine Heaven not found (will use fallback benchmark)")
            missing.append("Unigine Heaven (optional)")

        # Check for Ollama (for AI benchmark)
        try:
            result = subprocess.run(['which', 'ollama'], capture_output=True, timeout=5)
            if result.returncode == 0:
                print("  ✓ Ollama found for AI benchmarks")
            else:
                print("  ⚠ Ollama not found (AI benchmark will be skipped)")
                missing.append("Ollama (optional)")
        except:
            print("  ⚠ Ollama not found")
            missing.append("Ollama (optional)")

        # Check for sysbench (for CPU benchmark)
        try:
            result = subprocess.run(['which', 'sysbench'], capture_output=True, timeout=5)
            if result.returncode == 0:
                print("  ✓ Sysbench found for CPU benchmarks")
            else:
                print("  ⚠ Sysbench not found (CPU benchmark will be skipped)")
                missing.append("Sysbench (optional)")
        except:
            print("  ⚠ Sysbench not found")
            missing.append("Sysbench (optional)")

        print()
        self.dependencies_ok = True
        return missing

    def download_appimage(self):
        """Download benchmark AppImage"""
        print("⬇️  Downloading PiggyBankPC Benchmark AppImage...")

        # Check if already exists
        local_paths = [
            self.work_dir / "PiggyBankPC-Benchmark.AppImage",
            self.home_dir / "Desktop" / "PiggyBankPC-Benchmark.AppImage",
            self.home_dir / "Downloads" / "PiggyBankPC-Benchmark.AppImage"
        ]

        for path in local_paths:
            if path.exists():
                print(f"  ✓ Found existing AppImage at {path}")
                self.appimage_path = path
                # Make executable
                os.chmod(path, 0o755)
                return path

        # Download from server
        download_url = f"{SERVER_URL}/static/PiggyBankPC-Benchmark.AppImage"
        download_path = self.work_dir / "PiggyBankPC-Benchmark.AppImage"

        try:
            print(f"  Downloading from {download_url}...")
            urllib.request.urlretrieve(download_url, download_path)
            os.chmod(download_path, 0o755)
            print(f"  ✓ Downloaded to {download_path}")
            self.appimage_path = download_path
            return download_path
        except Exception as e:
            print(f"  ✗ Download failed: {e}")
            return None

    def get_gpu_price(self):
        """Ask user for GPU price"""
        print()
        print("💰 GPU Price Information")
        print("-" * 70)

        if not self.system_info.get('gpu', {}).get('detected'):
            print("⚠ Could not detect GPU - please enter manually")
            gpu_model = input("GPU Model: ").strip()
        else:
            gpu_model = self.system_info['gpu']['model']
            print(f"Detected GPU: {gpu_model}")

        while True:
            try:
                price_str = input(f"How much did your {gpu_model} cost? (£): ").strip()
                price = float(price_str.replace('£', '').replace(',', ''))
                if price >= 0:
                    print(f"  ✓ Recorded price: £{price:.2f}")
                    print()
                    return price, gpu_model
                else:
                    print("  ⚠ Price must be positive")
            except ValueError:
                print("  ⚠ Invalid price format")

    def run_benchmark(self, benchmark_type='quick'):
        """Run benchmark locally"""
        if not self.appimage_path or not self.appimage_path.exists():
            print("✗ AppImage not found!")
            return None

        print(f"🚀 Running {benchmark_type} benchmark...")
        print("   This may take 15-90 minutes depending on benchmark type")
        print()

        try:
            # Run AppImage with specified benchmark type
            arg_map = {
                'quick': '--quick',
                'full': '--full',
                'fps': '--fps',
                'ai': '--ai',
                'cpu': '--cpu'
            }

            arg = arg_map.get(benchmark_type, '--quick')

            # Run with extract-and-run for compatibility
            process = subprocess.Popen(
                [str(self.appimage_path), '--appimage-extract-and-run', arg, '--no-deps-check'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Stream output
            for line in process.stdout:
                print(line, end='')

            process.wait()

            if process.returncode == 0:
                print()
                print("✓ Benchmark completed successfully!")
                return True
            else:
                print()
                print(f"✗ Benchmark failed with exit code {process.returncode}")
                return False

        except Exception as e:
            print(f"✗ Error running benchmark: {e}")
            return False

    def find_results(self):
        """Find generated .pbr results file"""
        results_dir = self.work_dir / "results"

        if not results_dir.exists():
            return None

        # Find most recent .pbr file
        pbr_files = list(results_dir.glob('*.pbr'))
        if pbr_files:
            latest = max(pbr_files, key=lambda p: p.stat().st_mtime)
            return latest

        return None

    def upload_results(self, pbr_file):
        """Upload results to server"""
        print(f"📤 Uploading results to {SERVER_URL}...")

        try:
            with open(pbr_file, 'r') as f:
                pbr_content = f.read()

            # This would normally use requests library, but keeping minimal dependencies
            # For now, just inform user to upload manually
            print()
            print("=" * 70)
            print("📋 MANUAL UPLOAD REQUIRED")
            print("=" * 70)
            print(f"Results saved to: {pbr_file}")
            print()
            print("To submit your results:")
            print(f"1. Go to {SERVER_URL}/submit")
            print("2. Upload the .pbr file shown above")
            print("3. View your score on the leaderboard!")
            print("=" * 70)

        except Exception as e:
            print(f"✗ Error: {e}")

    def run(self):
        """Main client execution"""
        self.print_header()

        # Step 1: Detect hardware
        self.detect_hardware()

        # Step 2: Check dependencies
        missing = self.check_dependencies()

        # Step 3: Download AppImage
        self.download_appimage()

        if not self.appimage_path:
            print("✗ Cannot continue without AppImage")
            return

        # Step 4: Get GPU price
        gpu_price, gpu_model = self.get_gpu_price()

        # Step 5: Choose benchmark type
        print("📊 Select Benchmark Type:")
        print("  1. Quick (FPS only, ~15 min)")
        print("  2. Full (FPS + AI + CPU, ~90 min)")
        print("  3. FPS only")
        print("  4. AI only")
        print("  5. CPU only")

        choice = input("\nChoice (1-5): ").strip()

        benchmark_map = {
            '1': 'quick',
            '2': 'full',
            '3': 'fps',
            '4': 'ai',
            '5': 'cpu'
        }

        benchmark_type = benchmark_map.get(choice, 'quick')

        # Step 6: Run benchmark
        success = self.run_benchmark(benchmark_type)

        if success:
            # Step 7: Find and upload results
            pbr_file = self.find_results()
            if pbr_file:
                self.upload_results(pbr_file)
            else:
                print("⚠ Could not find results file")

        print()
        print("=" * 70)
        print("🐷 Thank you for using PiggyBankPC!")
        print("=" * 70)


if __name__ == "__main__":
    try:
        client = PiggyBankPCClient()
        client.run()
    except KeyboardInterrupt:
        print("\n\n⚠ Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        sys.exit(1)
