"""
Benchmark API Routes
Provides web-based benchmark control and real-time progress updates
"""
from flask import Blueprint, jsonify, request, render_template, send_file, session
import subprocess
import json
import os
import uuid
from pathlib import Path
from datetime import datetime
import threading
import time

benchmark_api_bp = Blueprint('benchmark_api', __name__)

# Store active benchmark processes
active_benchmarks = {}


def _detect_system_hardware():
    """
    Detect hardware on host system
    This runs BEFORE launching AppImage to ensure accurate detection
    """
    hardware_info = {
        'cpu': {},
        'gpu': {},
        'ram': {}
    }

    # Detect CPU
    try:
        result = subprocess.run(['lscpu'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'Model name:' in line:
                    hardware_info['cpu']['model'] = line.split(':', 1)[1].strip()
                elif 'CPU MHz:' in line:
                    hardware_info['cpu']['speed'] = line.split(':', 1)[1].strip() + ' MHz'
                elif 'CPU(s):' in line and 'On-line' not in line:
                    hardware_info['cpu']['cores'] = line.split(':', 1)[1].strip()
            hardware_info['cpu']['detected'] = True
        else:
            hardware_info['cpu'] = {'model': 'Unknown', 'detected': False}
    except Exception as e:
        hardware_info['cpu'] = {'model': 'Unknown', 'detected': False, 'error': str(e)}

    # Detect GPU
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            hardware_info['gpu']['model'] = result.stdout.strip()
            hardware_info['gpu']['detected'] = True
        else:
            hardware_info['gpu'] = {'model': 'Unknown', 'detected': False}
    except Exception as e:
        hardware_info['gpu'] = {'model': 'Unknown', 'detected': False, 'error': str(e)}

    # Detect RAM
    try:
        result = subprocess.run(['free', '-h'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Mem:'):
                    parts = line.split()
                    if len(parts) >= 2:
                        hardware_info['ram']['total'] = parts[1]
                        hardware_info['ram']['detected'] = True
        else:
            hardware_info['ram'] = {'total': 'Unknown', 'detected': False}
    except Exception as e:
        hardware_info['ram'] = {'total': 'Unknown', 'detected': False, 'error': str(e)}

    return hardware_info


class BenchmarkRunner:
    """Manages benchmark execution and status tracking"""

    def __init__(self, benchmark_id, benchmark_type):
        self.id = benchmark_id
        self.type = benchmark_type
        self.status = 'starting'
        self.progress = 0
        self.logs = []
        self.results = None
        self.process = None
        self.error = None

    def add_log(self, message, level='info'):
        """Add log entry"""
        self.logs.append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'level': level
        })

    def run(self):
        """Run benchmark in background thread"""
        try:
            self.status = 'running'
            self.add_log(f'Starting {self.type} benchmark...', 'info')

            # Search for AppImage in multiple locations
            home_dir = Path.home()
            search_locations = [
                home_dir / "Desktop" / "PiggyBankPC-Benchmark.AppImage",
                home_dir / "Downloads" / "PiggyBankPC-Benchmark.AppImage",
                home_dir / "PiggyBankPC-Benchmark.AppImage",
                Path("/home/john/Desktop/benchmark-suite/PiggyBankPC-Benchmark.AppImage"),
                Path("/storage/data/media/PiggyBankPC-Benchmark-FINAL.AppImage"),
            ]

            appimage_path = None
            for location in search_locations:
                if location.exists():
                    appimage_path = location
                    self.add_log(f'Found AppImage at: {location}', 'success')
                    break

            if not appimage_path:
                self.add_log('AppImage not found, downloading latest version...', 'info')
                self.progress = 5

                # Download from GitHub
                download_url = "https://github.com/piggybankpc-eng/piggybankpc-leaderboard/raw/main/PiggyBankPC-Benchmark.AppImage"
                download_path = home_dir / "Desktop" / "PiggyBankPC-Benchmark.AppImage"

                # Ensure Desktop directory exists
                download_path.parent.mkdir(parents=True, exist_ok=True)

                try:
                    import urllib.request
                    self.add_log(f'Downloading from: {download_url}', 'info')

                    # Download with progress
                    def report_progress(block_num, block_size, total_size):
                        downloaded = block_num * block_size
                        if total_size > 0:
                            percent = min(int((downloaded / total_size) * 100), 100)
                            if percent % 10 == 0:  # Log every 10%
                                self.add_log(f'Download progress: {percent}%', 'info')

                    urllib.request.urlretrieve(download_url, download_path, reporthook=report_progress)

                    # Make executable
                    import os
                    os.chmod(download_path, 0o755)

                    appimage_path = download_path
                    self.add_log('✓ Download complete!', 'success')
                    self.progress = 10

                except Exception as e:
                    self.error = f"Failed to download AppImage: {str(e)}"
                    self.status = 'error'
                    self.add_log(f'ERROR: {self.error}', 'error')
                    self.add_log('Please download manually from GitHub', 'error')
                    return

            # Run benchmark based on type
            self.progress = 10
            self.add_log('Initializing benchmark environment...', 'info')

            # Actually run the AppImage
            self._run_real_benchmark(appimage_path)

        except Exception as e:
            self.error = str(e)
            self.status = 'error'
            self.add_log(f'Error: {self.error}', 'error')

    def _detect_hardware_for_benchmark(self):
        """Detect hardware on host system before launching AppImage"""
        # Use pre-detected hardware from session if available
        if 'detected_hardware' in session:
            return session['detected_hardware']

        # Otherwise detect now
        return _detect_system_hardware()

    def _run_real_benchmark(self, appimage_path):
        """Actually run the AppImage and parse real results"""
        try:
            # Map benchmark type to command-line argument
            arg_map = {
                'quick': '--quick',
                'full': '--full',
                'fps': '--fps',
                'ai': '--ai',
                'cpu': '--cpu'
            }

            arg = arg_map.get(self.type, '--quick')

            self.add_log(f'Running benchmark: {arg}', 'info')
            self.add_log('This may take 15-90 minutes depending on benchmark type', 'info')
            self.progress = 15

            # PRE-DETECT HARDWARE before launching AppImage
            self.add_log('Pre-detecting system hardware...', 'info')
            hardware_info = self._detect_hardware_for_benchmark()

            # Save to temp JSON file
            import tempfile
            import json
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            json.dump(hardware_info, temp_file, indent=2)
            temp_file.close()
            self.add_log(f'✓ Hardware pre-detected: CPU={hardware_info["cpu"]["model"][:30]}, GPU={hardware_info["gpu"]["model"][:30]}', 'success')

            # Execute AppImage with argument
            self.add_log(f'Executing: {appimage_path} {arg}', 'info')

            # Check if AppImage is executable
            import os
            if not os.access(appimage_path, os.X_OK):
                self.add_log('Making AppImage executable...', 'info')
                os.chmod(appimage_path, 0o755)

            # Use --appimage-extract-and-run by default (FUSE often not available in web environments)
            self.add_log('Executing benchmark with extract-and-run method...', 'info')

            # Pass pre-detected hardware info via environment variable
            env = os.environ.copy()
            env['PIGGYBANKPC_HARDWARE_INFO'] = temp_file.name

            self.process = subprocess.Popen(
                [str(appimage_path), '--appimage-extract-and-run', arg, '--no-deps-check'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env
            )

            # Monitor process output
            self.progress = 20
            while True:
                if self.status == 'stopped':
                    self.process.terminate()
                    return

                # Check if process is still running
                retcode = self.process.poll()
                if retcode is not None:
                    # Process finished
                    if retcode == 0:
                        self.add_log('✓ Benchmark execution completed', 'success')
                    else:
                        self.add_log(f'Benchmark exited with code {retcode}', 'error')
                        # Read and log stderr for debugging
                        stderr = self.process.stderr.read()
                        if stderr:
                            self.add_log(f'Error output: {stderr}', 'error')
                    break

                # Read output line by line
                line = self.process.stdout.readline()
                if line:
                    self.add_log(line.strip(), 'info')

                # Increment progress slowly
                if self.progress < 90:
                    self.progress += 1

                time.sleep(0.5)

            self.progress = 95

            # Check for existing results in ~/PiggyBankPC/results/
            home_dir = Path.home()
            results_dir = home_dir / "PiggyBankPC" / "results"

            if results_dir.exists():
                # Find most recent .pbr file
                pbr_files = list(results_dir.glob('*.pbr'))
                if pbr_files:
                    latest_pbr = max(pbr_files, key=lambda p: p.stat().st_mtime)
                    self.add_log(f'Found existing results: {latest_pbr.name}', 'success')

                    # Try to parse JSON results
                    json_files = list(results_dir.glob('benchmark_results_*.json'))
                    if json_files:
                        latest_json = max(json_files, key=lambda p: p.stat().st_mtime)
                        try:
                            with open(latest_json, 'r') as f:
                                data = json.load(f)

                            # Extract results
                            self.results = {}

                            if 'fps' in data:
                                fps_data = data['fps']
                                if 'configurations' in fps_data:
                                    # Get first configuration
                                    configs = fps_data['configurations']
                                    if configs:
                                        first_config = list(configs.values())[0]
                                        self.results['fps'] = {
                                            'average_fps': first_config.get('average_fps', 0),
                                            'min_fps': first_config.get('min_fps', 0),
                                            'max_fps': first_config.get('max_fps', 0)
                                        }

                            if 'ai' in data:
                                ai_data = data['ai']
                                self.results['ai'] = {
                                    'tokens_per_second': ai_data.get('tokens_per_second', 0),
                                    'model': ai_data.get('model', 'llama2:7b')
                                }

                            if 'cpu' in data:
                                cpu_data = data['cpu']
                                self.results['cpu'] = {
                                    'score': cpu_data.get('events_per_second', 0),
                                    'threads': cpu_data.get('threads_used', 0)
                                }

                            self.results['download_url'] = '/api/benchmark/download/' + self.id

                            self.progress = 100
                            self.status = 'complete'
                            self.add_log('✓ Results loaded successfully!', 'success')
                            return

                        except Exception as e:
                            self.add_log(f'Error parsing results: {str(e)}', 'error')

            # No results found
            self.progress = 100
            self.status = 'complete'
            self.add_log('No recent results found', 'info')
            self.add_log('Please run the AppImage manually to generate results', 'info')
            self.results = None

        except Exception as e:
            self.error = str(e)
            self.status = 'error'
            self.add_log(f'Error: {self.error}', 'error')

    def stop(self):
        """Stop running benchmark"""
        self.status = 'stopped'
        if self.process:
            self.process.terminate()
        self.add_log('Benchmark stopped by user', 'info')


@benchmark_api_bp.route('/benchmark-control')
def benchmark_control_page():
    """Render benchmark control page"""
    return render_template('benchmark_control.html')


@benchmark_api_bp.route('/api/benchmark/system-info')
def get_system_info():
    """Get system information - uses pre-detected hardware from session"""
    try:
        # Use pre-detected hardware from session (set during prepare phase)
        if 'detected_hardware' in session:
            hardware = session['detected_hardware']
            cpu_info = hardware.get('cpu', {})
            gpu_info = hardware.get('gpu', {})
            ram_info = hardware.get('ram', {})
        else:
            # Fallback: detect now if not in session
            hardware = _detect_system_hardware()
            cpu_info = hardware.get('cpu', {})
            gpu_info = hardware.get('gpu', {})
            ram_info = hardware.get('ram', {})

        # Check GPU price (from config file)
        gpu_price = 0.0
        home_dir = Path.home()
        price_file = home_dir / "PiggyBankPC" / "config" / "gpu-prices.txt"

        if price_file.exists() and gpu_info.get('detected'):
            try:
                with open(price_file, 'r') as f:
                    for line in f:
                        if gpu_info['model'].lower() in line.lower() and '=' in line:
                            price_str = line.split('=')[1].strip()
                            import re
                            match = re.search(r'£?(\d+(?:\.\d{2})?)', price_str)
                            if match:
                                gpu_price = float(match.group(1))
                                break
            except:
                pass

        return jsonify({
            'success': True,
            'cpu': cpu_info,
            'gpu': gpu_info,
            'ram': ram_info,
            'gpu_price': gpu_price
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@benchmark_api_bp.route('/api/benchmark/save-gpu-price', methods=['POST'])
def save_gpu_price():
    """Save GPU price to config file"""
    try:
        data = request.json
        price = float(data.get('price', 0))
        gpu_model = data.get('gpu_model', None)  # Optional - use if provided

        if price < 0:
            return jsonify({'success': False, 'error': 'Invalid price'}), 400

        # Get GPU model if not provided
        if not gpu_model:
            try:
                # Try to find nvidia-smi
                import shutil
                nvidia_smi = shutil.which('nvidia-smi')
                if not nvidia_smi:
                    nvidia_smi = '/usr/bin/nvidia-smi'

                result = subprocess.run(
                    [nvidia_smi, '--query-gpu=name', '--format=csv,noheader'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    gpu_model = result.stdout.strip()
                else:
                    # Fallback: use generic name
                    gpu_model = 'Unknown GPU'
            except Exception as e:
                # If nvidia-smi fails, use generic name
                gpu_model = 'Unknown GPU'

        # Save to config file
        home_dir = Path.home()
        config_dir = home_dir / "PiggyBankPC" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        price_file = config_dir / "gpu-prices.txt"

        with open(price_file, 'a') as f:
            f.write(f"\n{gpu_model} = £{price:.2f}\n")

        return jsonify({'success': True, 'message': 'GPU price saved'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@benchmark_api_bp.route('/api/benchmark/prepare', methods=['POST'])
def prepare_benchmark():
    """Prepare system for benchmarking - download AppImage, detect hardware"""
    try:
        # STEP 1: Pre-detect hardware FIRST
        hardware_info = _detect_system_hardware()

        # Store in session for later use
        session['detected_hardware'] = hardware_info

        # STEP 2: Check for AppImage
        home_dir = Path.home()
        search_locations = [
            home_dir / "Desktop" / "PiggyBankPC-Benchmark.AppImage",
            home_dir / "Downloads" / "PiggyBankPC-Benchmark.AppImage",
            home_dir / "PiggyBankPC-Benchmark.AppImage",
            Path("/home/john/Desktop/benchmark-suite/PiggyBankPC-Benchmark.AppImage"),
            Path("/storage/data/media/PiggyBankPC-Benchmark-FINAL.AppImage"),
        ]

        # Check if AppImage already exists
        appimage_path = None
        for location in search_locations:
            if location.exists():
                appimage_path = location
                return jsonify({
                    'success': True,
                    'message': f'Found at {location.name}',
                    'hardware': hardware_info
                })

        # Download if not found
        download_url = "https://github.com/piggybankpc-eng/piggybankpc-leaderboard/raw/main/PiggyBankPC-Benchmark.AppImage"
        download_path = home_dir / "Desktop" / "PiggyBankPC-Benchmark.AppImage"
        download_path.parent.mkdir(parents=True, exist_ok=True)

        import urllib.request
        urllib.request.urlretrieve(download_url, download_path)

        # Make executable
        import os
        os.chmod(download_path, 0o755)

        return jsonify({
            'success': True,
            'message': 'Downloaded successfully'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@benchmark_api_bp.route('/api/benchmark/start', methods=['POST'])
def start_benchmark():
    """Start a new benchmark"""
    try:
        data = request.json
        benchmark_type = data.get('type', 'quick')

        if benchmark_type not in ['quick', 'full', 'fps', 'ai', 'cpu']:
            return jsonify({'success': False, 'error': 'Invalid benchmark type'}), 400

        # Create new benchmark
        benchmark_id = str(uuid.uuid4())
        runner = BenchmarkRunner(benchmark_id, benchmark_type)
        active_benchmarks[benchmark_id] = runner

        # Start in background thread
        thread = threading.Thread(target=runner.run)
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True,
            'benchmark_id': benchmark_id,
            'message': 'Benchmark started'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@benchmark_api_bp.route('/api/benchmark/status/<benchmark_id>')
def get_benchmark_status(benchmark_id):
    """Get benchmark status and progress"""
    try:
        runner = active_benchmarks.get(benchmark_id)

        if not runner:
            return jsonify({'success': False, 'error': 'Benchmark not found'}), 404

        # Get new logs since last poll (last 10 for now)
        recent_logs = runner.logs[-10:] if len(runner.logs) > 0 else []

        return jsonify({
            'success': True,
            'status': runner.status,
            'progress': runner.progress,
            'logs': recent_logs,
            'results': runner.results,
            'error': runner.error
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@benchmark_api_bp.route('/api/benchmark/stop/<benchmark_id>', methods=['POST'])
def stop_benchmark(benchmark_id):
    """Stop a running benchmark"""
    try:
        runner = active_benchmarks.get(benchmark_id)

        if not runner:
            return jsonify({'success': False, 'error': 'Benchmark not found'}), 404

        runner.stop()

        return jsonify({
            'success': True,
            'message': 'Benchmark stopped'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@benchmark_api_bp.route('/api/benchmark/cleanup', methods=['POST'])
def cleanup_benchmark():
    """Clean up old benchmark results"""
    try:
        home_dir = Path.home()
        results_dir = home_dir / "PiggyBankPC" / "results"
        logs_dir = home_dir / "PiggyBankPC" / "logs"

        files_removed = 0

        # Remove result files
        if results_dir.exists():
            for file in results_dir.glob('*'):
                file.unlink()
                files_removed += 1

        # Remove log files
        if logs_dir.exists():
            for file in logs_dir.glob('*.log'):
                file.unlink()
                files_removed += 1

        # Remove Heaven HTML results
        for file in home_dir.glob('Unigine_Heaven_Benchmark_*.html'):
            file.unlink()
            files_removed += 1

        return jsonify({
            'success': True,
            'message': f'Removed {files_removed} files'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@benchmark_api_bp.route('/api/benchmark/download/<benchmark_id>')
def download_results(benchmark_id):
    """Download benchmark results"""
    try:
        runner = active_benchmarks.get(benchmark_id)

        if not runner or runner.status != 'complete':
            return jsonify({'success': False, 'error': 'Results not available'}), 404

        # Find most recent .pbr file
        home_dir = Path.home()
        results_dir = home_dir / "PiggyBankPC" / "results"

        pbr_files = list(results_dir.glob('*.pbr'))
        if not pbr_files:
            return jsonify({'success': False, 'error': 'No result files found'}), 404

        # Get most recent file
        latest_file = max(pbr_files, key=lambda p: p.stat().st_mtime)

        return send_file(
            latest_file,
            as_attachment=True,
            download_name=latest_file.name
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
