#!/usr/bin/env python3
"""
AI Token Benchmark Module
Tests AI inference performance using Ollama or fallback methods
"""

import subprocess
import time
import logging
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class AIBenchmark:
    """Runs AI token generation benchmarks"""

    def __init__(self, base_dir, hardware_detector=None):
        self.base_dir = Path(base_dir)
        self.results_dir = self.base_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger("AIBenchmark")
        self.hardware_detector = hardware_detector

    def check_ollama_installed(self) -> bool:
        """
        Check if Ollama is installed and running

        Returns:
            bool: True if available
        """
        try:
            result = subprocess.run(
                ["which", "ollama"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Failed to check Ollama: {str(e)}")
            return False

    def check_ollama_service(self) -> bool:
        """
        Check if Ollama service is running

        Returns:
            bool: True if service is active
        """
        try:
            # Try to list models to check if service is running
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def ensure_model_installed(self, model_name: str = "llama2:7b") -> bool:
        """
        Ensure the test model is installed

        Args:
            model_name: Model to install

        Returns:
            bool: True if model is available
        """
        self.logger.info(f"Checking if {model_name} is installed...")

        try:
            # List installed models
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and model_name in result.stdout:
                self.logger.info(f"Model {model_name} is already installed")
                return True

            # Model not found, ask user to install
            print(f"\n⚠️  Model '{model_name}' not found")
            print(f"To run AI benchmarks, this model needs to be downloaded (~4GB)")
            response = input(f"Download {model_name}? (y/n): ").strip().lower()

            if response == 'y':
                print(f"\nDownloading {model_name}... (this may take a few minutes)")
                result = subprocess.run(
                    ["ollama", "pull", model_name],
                    timeout=600  # 10 minute timeout
                )
                return result.returncode == 0
            else:
                print("Skipping AI benchmark")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("Model installation timed out")
            return False
        except Exception as e:
            self.logger.error(f"Failed to install model: {str(e)}")
            return False

    def run_ollama_benchmark(self, model_name: str = "llama2:7b", num_tokens: int = 500) -> Dict:
        """
        Run AI inference benchmark using Ollama

        Args:
            model_name: Model to test
            num_tokens: Target number of tokens to generate

        Returns:
            dict: Benchmark results
        """
        self.logger.info(f"Running Ollama benchmark with {model_name}...")

        if not self.check_ollama_installed():
            return {
                "benchmark_type": "ollama",
                "status": "error",
                "error": "Ollama not installed"
            }

        if not self.check_ollama_service():
            return {
                "benchmark_type": "ollama",
                "status": "error",
                "error": "Ollama service not running"
            }

        if not self.ensure_model_installed(model_name):
            return {
                "benchmark_type": "ollama",
                "status": "skipped",
                "reason": "Model not available"
            }

        try:
            print(f"\n{'='*60}")
            print("RUNNING AI TOKEN GENERATION BENCHMARK")
            print(f"Model: {model_name}")
            print(f"Target tokens: {num_tokens}")
            print(f"{'='*60}\n")

            # Prepare prompt that will generate substantial output
            prompt = """Write a detailed technical explanation of how graphics processing units (GPUs)
work, including their architecture, parallel processing capabilities, and differences from CPUs.
Include details about CUDA cores, memory hierarchy, and typical use cases."""

            # Run inference and measure time
            start_time = time.time()

            process = subprocess.Popen(
                ["ollama", "run", model_name, prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            output_lines = []
            gpu_temps = []
            gpu_utils = []
            cpu_temps = []
            cpu_utils = []
            vram_usage = []

            print("Generating tokens", end="", flush=True)

            # Monitor output and thermal stats
            for line in process.stdout:
                output_lines.append(line)
                print(".", end="", flush=True)

                # Periodically check thermal stats
                if len(output_lines) % 10 == 0 and self.hardware_detector:
                    # Get GPU stats
                    gpu_stats = self.hardware_detector.get_current_gpu_stats()
                    if 'temperature' in gpu_stats:
                        gpu_temps.append(gpu_stats['temperature'])
                    if 'gpu_utilization' in gpu_stats:
                        util_str = gpu_stats['gpu_utilization'].replace('%', '').strip()
                        try:
                            gpu_utils.append(float(util_str))
                        except ValueError:
                            pass

                    # Get CPU stats
                    cpu_stats = self.hardware_detector.get_current_cpu_stats()
                    if 'temperature' in cpu_stats:
                        cpu_temps.append(cpu_stats['temperature'])
                    if 'cpu_utilization' in cpu_stats:
                        cpu_util_str = cpu_stats['cpu_utilization'].replace('%', '').strip()
                        try:
                            cpu_utils.append(float(cpu_util_str))
                        except ValueError:
                            pass

            process.wait()
            end_time = time.time()

            print("\n\nGeneration completed!")

            # Calculate metrics
            full_output = "".join(output_lines)
            duration = end_time - start_time

            # Estimate token count (rough approximation: ~4 chars per token)
            estimated_tokens = len(full_output) // 4
            tokens_per_second = estimated_tokens / duration if duration > 0 else 0

            # Get VRAM usage
            vram_used = "N/A"
            if self.hardware_detector:
                success, vram_output, _ = self.hardware_detector.run_command([
                    "nvidia-smi",
                    "--query-gpu=memory.used",
                    "--format=csv,noheader"
                ])
                if success:
                    vram_used = vram_output.strip()

            # Prepare thermal metrics
            thermal_metrics = {}
            if gpu_temps:
                thermal_metrics["gpu_temp_min"] = min(gpu_temps)
                thermal_metrics["gpu_temp_avg"] = round(sum(gpu_temps) / len(gpu_temps), 1)
                thermal_metrics["gpu_temp_max"] = max(gpu_temps)
            if gpu_utils:
                thermal_metrics["gpu_util_min"] = round(min(gpu_utils), 1)
                thermal_metrics["gpu_util_avg"] = round(sum(gpu_utils) / len(gpu_utils), 1)
                thermal_metrics["gpu_util_max"] = round(max(gpu_utils), 1)
            if cpu_temps:
                thermal_metrics["cpu_temp_min"] = min(cpu_temps)
                thermal_metrics["cpu_temp_avg"] = round(sum(cpu_temps) / len(cpu_temps), 1)
                thermal_metrics["cpu_temp_max"] = max(cpu_temps)
            if cpu_utils:
                thermal_metrics["cpu_util_min"] = round(min(cpu_utils), 1)
                thermal_metrics["cpu_util_avg"] = round(sum(cpu_utils) / len(cpu_utils), 1)
                thermal_metrics["cpu_util_max"] = round(max(cpu_utils), 1)

            results = {
                "benchmark_type": "ollama",
                "model": model_name,
                "status": "completed",
                "tokens_generated": estimated_tokens,
                "duration_seconds": round(duration, 2),
                "tokens_per_second": round(tokens_per_second, 2),
                "avg_gpu_temp": round(sum(gpu_temps) / len(gpu_temps), 1) if gpu_temps else "N/A",
                "max_gpu_temp": max(gpu_temps) if gpu_temps else "N/A",
                "vram_used": vram_used,
                "thermal_metrics": thermal_metrics,
                "timestamp": datetime.now().isoformat()
            }

            self._save_results(results)

            return results

        except subprocess.TimeoutExpired:
            self.logger.error("Ollama benchmark timed out")
            return {
                "benchmark_type": "ollama",
                "status": "error",
                "error": "Benchmark timed out"
            }
        except Exception as e:
            self.logger.error(f"Ollama benchmark failed: {str(e)}")
            return {
                "benchmark_type": "ollama",
                "status": "error",
                "error": str(e)
            }

    def run_ollama_cpu_benchmark(self, model_name: str = "llama2:7b", num_tokens: int = 500) -> Dict:
        """
        Run AI inference benchmark using Ollama on CPU ONLY
        Tests CPU token generation with thermal monitoring

        Args:
            model_name: Model to test
            num_tokens: Target number of tokens to generate

        Returns:
            dict: Benchmark results with CPU thermal metrics
        """
        self.logger.info(f"Running Ollama CPU-only benchmark with {model_name}...")

        if not self.check_ollama_installed():
            return {
                "benchmark_type": "ollama_cpu",
                "status": "error",
                "error": "Ollama not installed"
            }

        if not self.check_ollama_service():
            return {
                "benchmark_type": "ollama_cpu",
                "status": "error",
                "error": "Ollama service not running"
            }

        if not self.ensure_model_installed(model_name):
            return {
                "benchmark_type": "ollama_cpu",
                "status": "skipped",
                "reason": "Model not available"
            }

        try:
            print(f"\n{'='*60}")
            print("RUNNING AI TOKEN GENERATION BENCHMARK (CPU ONLY)")
            print(f"Model: {model_name}")
            print(f"Target tokens: {num_tokens}")
            print(f"Backend: CPU (GPU disabled)")
            print(f"{'='*60}\n")

            # Prepare prompt
            prompt = """Write a detailed technical explanation of how graphics processing units (GPUs)
work, including their architecture, parallel processing capabilities, and differences from CPUs.
Include details about CUDA cores, memory hierarchy, and typical use cases."""

            # Run inference on CPU only (disable GPU)
            import os
            env = os.environ.copy()
            env['CUDA_VISIBLE_DEVICES'] = ''  # Hide GPU from Ollama, force CPU

            start_time = time.time()

            process = subprocess.Popen(
                ["ollama", "run", model_name, prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )

            output_lines = []
            cpu_temps = []
            cpu_utils = []

            print("Generating tokens on CPU", end="", flush=True)

            # Monitor output and CPU stats
            for line in process.stdout:
                output_lines.append(line)
                print(".", end="", flush=True)

                # Periodically check CPU stats
                if len(output_lines) % 10 == 0 and self.hardware_detector:
                    cpu_stats = self.hardware_detector.get_current_cpu_stats()
                    if 'temperature' in cpu_stats:
                        cpu_temps.append(cpu_stats['temperature'])
                    if 'cpu_utilization' in cpu_stats:
                        cpu_util_str = cpu_stats['cpu_utilization'].replace('%', '').strip()
                        try:
                            cpu_utils.append(float(cpu_util_str))
                        except ValueError:
                            pass

            process.wait()
            end_time = time.time()

            print("\n\nGeneration completed!")

            # Calculate metrics
            full_output = "".join(output_lines)
            duration = end_time - start_time

            # Estimate token count (rough approximation: ~4 chars per token)
            estimated_tokens = len(full_output) // 4
            tokens_per_second = estimated_tokens / duration if duration > 0 else 0

            # Prepare thermal metrics
            thermal_metrics = {}
            if cpu_temps:
                thermal_metrics["cpu_temp_min"] = min(cpu_temps)
                thermal_metrics["cpu_temp_avg"] = round(sum(cpu_temps) / len(cpu_temps), 1)
                thermal_metrics["cpu_temp_max"] = max(cpu_temps)
            if cpu_utils:
                thermal_metrics["cpu_util_min"] = round(min(cpu_utils), 1)
                thermal_metrics["cpu_util_avg"] = round(sum(cpu_utils) / len(cpu_utils), 1)
                thermal_metrics["cpu_util_max"] = round(max(cpu_utils), 1)

            results = {
                "benchmark_type": "ollama_cpu",
                "model": model_name,
                "status": "completed",
                "tokens_generated": estimated_tokens,
                "duration_seconds": round(duration, 2),
                "tokens_per_second": round(tokens_per_second, 2),
                "backend": "CPU",
                "avg_cpu_temp": round(sum(cpu_temps) / len(cpu_temps), 1) if cpu_temps else "N/A",
                "max_cpu_temp": max(cpu_temps) if cpu_temps else "N/A",
                "thermal_metrics": thermal_metrics,
                "timestamp": datetime.now().isoformat()
            }

            self._save_results(results)

            return results

        except subprocess.TimeoutExpired:
            self.logger.error("Ollama CPU benchmark timed out")
            return {
                "benchmark_type": "ollama_cpu",
                "status": "error",
                "error": "Benchmark timed out"
            }
        except Exception as e:
            self.logger.error(f"Ollama CPU benchmark failed: {str(e)}")
            return {
                "benchmark_type": "ollama_cpu",
                "status": "error",
                "error": str(e)
            }

    def run_fallback_ai_test(self) -> Dict:
        """
        Run fallback AI test using basic GPU computation

        Returns:
            dict: Benchmark results
        """
        self.logger.info("Running fallback AI test...")

        print(f"\n{'='*60}")
        print("AI BENCHMARK - FALLBACK MODE")
        print("Note: Ollama not available - running basic GPU test")
        print(f"{'='*60}\n")

        # Simple GPU utilization test as fallback
        try:
            start_time = time.time()
            duration = 30  # 30 second test

            gpu_utils = []
            temps = []

            while time.time() - start_time < duration:
                if self.hardware_detector:
                    stats = self.hardware_detector.get_current_gpu_stats()

                    if 'gpu_utilization' in stats:
                        util_str = stats['gpu_utilization'].replace('%', '').strip()
                        try:
                            gpu_utils.append(float(util_str))
                        except ValueError:
                            pass

                    if 'temperature' in stats:
                        temps.append(stats['temperature'])

                print(".", end="", flush=True)
                time.sleep(1)

            print("\n")

            avg_util = sum(gpu_utils) / len(gpu_utils) if gpu_utils else 0

            results = {
                "benchmark_type": "fallback_ai_test",
                "status": "completed",
                "note": "Ollama not available - Install Ollama for AI token benchmarks",
                "avg_gpu_utilization": f"{avg_util:.1f}%",
                "avg_temperature": f"{sum(temps) / len(temps):.1f}°C" if temps else "N/A",
                "timestamp": datetime.now().isoformat()
            }

            self._save_results(results)
            return results

        except Exception as e:
            self.logger.error(f"Fallback test failed: {str(e)}")
            return {
                "benchmark_type": "fallback_ai_test",
                "status": "error",
                "error": str(e)
            }

    def run_benchmark(self, model_name: str = "llama2:7b", num_tokens: int = 500) -> Dict:
        """
        Run AI benchmark with automatic fallback

        Args:
            model_name: Model to use for testing
            num_tokens: Target number of tokens

        Returns:
            dict: Benchmark results
        """
        if self.check_ollama_installed() and self.check_ollama_service():
            return self.run_ollama_benchmark(model_name, num_tokens)
        else:
            self.logger.warning("Ollama not available - using fallback test")
            return self.run_fallback_ai_test()

    def _save_results(self, results: Dict):
        """
        Save benchmark results to JSON file

        Args:
            results: Benchmark results dictionary
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.results_dir / f"ai_benchmark_{timestamp}.json"

        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            self.logger.info(f"Results saved to: {output_file}")
            print(f"\n✓ Results saved to: {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to save results: {str(e)}")


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = Path(__file__).parent.parent

    # Import hardware detector
    try:
        from hardware_detection import HardwareDetector
        hw_detector = HardwareDetector(base_dir)
    except ImportError:
        hw_detector = None

    benchmark = AIBenchmark(base_dir, hw_detector)

    # Run test
    print("\nRunning AI token benchmark...")
    results = benchmark.run_benchmark()

    print("\n" + "="*60)
    print("BENCHMARK RESULTS")
    print("="*60)
    for key, value in results.items():
        print(f"{key}: {value}")
    print("="*60)
