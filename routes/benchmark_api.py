"""
Benchmark API Routes
Provides web-based benchmark control and real-time progress updates
"""
from flask import Blueprint, jsonify, request, render_template, send_file
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

            # Determine which benchmark to run
            home_dir = Path.home()
            appimage_path = home_dir / "Desktop" / "PiggyBankPC-Benchmark.AppImage"

            if not appimage_path.exists():
                self.error = "AppImage not found"
                self.status = 'error'
                self.add_log(f'Error: {self.error}', 'error')
                return

            # Run benchmark based on type
            self.progress = 10
            self.add_log('Initializing benchmark environment...', 'info')

            # For now, simulate benchmark progress
            # TODO: Actually run the AppImage and parse output
            self._simulate_benchmark()

        except Exception as e:
            self.error = str(e)
            self.status = 'error'
            self.add_log(f'Error: {self.error}', 'error')

    def _simulate_benchmark(self):
        """Simulate benchmark for testing (replace with real execution)"""
        stages = {
            'quick': ['Hardware Detection', 'FPS Benchmark'],
            'full': ['Hardware Detection', 'FPS Benchmark', 'AI Benchmark', 'CPU Benchmark'],
            'fps': ['Hardware Detection', 'FPS Benchmark'],
            'ai': ['Hardware Detection', 'AI Benchmark'],
            'cpu': ['Hardware Detection', 'CPU Benchmark']
        }

        stage_list = stages.get(self.type, ['Hardware Detection'])
        stage_progress = 100 // len(stage_list)

        for i, stage in enumerate(stage_list):
            if self.status == 'stopped':
                return

            self.progress = (i + 1) * stage_progress
            self.add_log(f'{stage}...', 'info')
            time.sleep(3)  # Simulate work

        self.progress = 100
        self.status = 'complete'
        self.add_log('Benchmark complete!', 'success')

        # Mock results
        self.results = {
            'fps': {'average_fps': 113.5, 'min_fps': 17.0, 'max_fps': 225.4},
            'ai': {'tokens_per_second': 17.44, 'model': 'llama2:7b'},
            'cpu': {'score': 21706, 'threads': 20},
            'download_url': '/api/benchmark/download/' + self.id
        }

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
    """Get system information"""
    try:
        # Detect GPU
        gpu_info = {}
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                gpu_info['model'] = result.stdout.strip()
                gpu_info['detected'] = True
            else:
                gpu_info['model'] = 'Unknown'
                gpu_info['detected'] = False
        except:
            gpu_info['model'] = 'Unknown'
            gpu_info['detected'] = False

        # Detect CPU
        cpu_info = {}
        try:
            result = subprocess.run(
                ['lscpu'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Model name:' in line:
                        cpu_info['model'] = line.split(':', 1)[1].strip()
                        cpu_info['detected'] = True
                        break
            if not cpu_info:
                cpu_info['model'] = 'Unknown'
                cpu_info['detected'] = False
        except:
            cpu_info['model'] = 'Unknown'
            cpu_info['detected'] = False

        # Detect RAM
        ram_info = {}
        try:
            result = subprocess.run(
                ['free', '-h'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Mem:'):
                        parts = line.split()
                        if len(parts) >= 2:
                            ram_info['total'] = parts[1]
                            ram_info['detected'] = True
                            break
            if not ram_info:
                ram_info['total'] = 'Unknown'
                ram_info['detected'] = False
        except:
            ram_info['total'] = 'Unknown'
            ram_info['detected'] = False

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

        if price < 0:
            return jsonify({'success': False, 'error': 'Invalid price'}), 400

        # Get GPU model
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return jsonify({'success': False, 'error': 'Could not detect GPU'}), 400

        gpu_model = result.stdout.strip()

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
