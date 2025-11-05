#!/usr/bin/env python3
"""
CPU Benchmark Module
Tests CPU performance using Geekbench or sysbench
"""

import subprocess
import time
import logging
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict
from overclock_analyzer import OverclockAnalyzer


class CPUBenchmark:
    """Runs CPU performance benchmarks"""

    def __init__(self, base_dir, hardware_detector=None):
        self.base_dir = Path(base_dir)
        self.results_dir = self.base_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger("CPUBenchmark")
        self.hardware_detector = hardware_detector

    def check_geekbench_installed(self) -> bool:
        """
        Check if Geekbench is installed

        Returns:
            bool: True if available
        """
        try:
            # Check for Geekbench 6
            result = subprocess.run(
                ["which", "geekbench6"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return True

            # Check for Geekbench 5
            result = subprocess.run(
                ["which", "geekbench5"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0

        except Exception:
            return False

    def check_sysbench_installed(self) -> bool:
        """
        Check if sysbench is installed

        Returns:
            bool: True if available
        """
        try:
            result = subprocess.run(
                ["which", "sysbench"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def run_geekbench(self) -> Dict:
        """
        Run Geekbench CPU benchmark

        Returns:
            dict: Benchmark results
        """
        self.logger.info("Running Geekbench benchmark...")

        # Determine which version is available
        geekbench_cmd = None
        for cmd in ["geekbench6", "geekbench5"]:
            result = subprocess.run(
                ["which", cmd],
                capture_output=True
            )
            if result.returncode == 0:
                geekbench_cmd = cmd
                break

        if not geekbench_cmd:
            return {
                "benchmark_type": "geekbench",
                "status": "error",
                "error": "Geekbench not found"
            }

        try:
            print(f"\n{'='*60}")
            print("RUNNING GEEKBENCH CPU BENCHMARK")
            print("This may take 10-15 minutes...")
            print(f"{'='*60}\n")

            start_time = time.time()

            # Run Geekbench
            result = subprocess.run(
                [geekbench_cmd],
                capture_output=True,
                text=True,
                timeout=1200  # 20 minute timeout
            )

            duration = time.time() - start_time

            if result.returncode != 0:
                return {
                    "benchmark_type": "geekbench",
                    "status": "error",
                    "error": result.stderr
                }

            # Parse results
            output = result.stdout

            single_core = "N/A"
            multi_core = "N/A"

            # Look for score patterns
            single_match = re.search(r'Single-Core Score\s+(\d+)', output)
            if single_match:
                single_core = int(single_match.group(1))

            multi_match = re.search(r'Multi-Core Score\s+(\d+)', output)
            if multi_match:
                multi_core = int(multi_match.group(1))

            results = {
                "benchmark_type": "geekbench",
                "version": geekbench_cmd,
                "status": "completed",
                "single_core_score": single_core,
                "multi_core_score": multi_core,
                "duration_seconds": round(duration, 2),
                "timestamp": datetime.now().isoformat()
            }

            self._save_results(results)
            return results

        except subprocess.TimeoutExpired:
            self.logger.error("Geekbench timed out")
            return {
                "benchmark_type": "geekbench",
                "status": "error",
                "error": "Benchmark timed out"
            }
        except Exception as e:
            self.logger.error(f"Geekbench failed: {str(e)}")
            return {
                "benchmark_type": "geekbench",
                "status": "error",
                "error": str(e)
            }

    def run_sysbench(self) -> Dict:
        """
        Run sysbench CPU benchmark

        Returns:
            dict: Benchmark results
        """
        self.logger.info("Running sysbench benchmark...")

        try:
            print(f"\n{'='*60}")
            print("RUNNING SYSBENCH CPU BENCHMARK")
            print("Testing CPU performance...")
            print(f"{'='*60}\n")

            # Get CPU thread count
            threads = 1
            if self.hardware_detector:
                cpu_info = self.hardware_detector.detect_cpu()
                if cpu_info.get('threads') != 'Unknown':
                    try:
                        threads = int(cpu_info['threads'])
                    except ValueError:
                        threads = 1

            start_time = time.time()

            # Run CPU test
            result = subprocess.run(
                [
                    "sysbench",
                    "cpu",
                    f"--threads={threads}",
                    "--time=60",
                    "run"
                ],
                capture_output=True,
                text=True,
                timeout=120
            )

            duration = time.time() - start_time

            if result.returncode != 0:
                return {
                    "benchmark_type": "sysbench",
                    "status": "error",
                    "error": result.stderr
                }

            # Parse results
            output = result.stdout

            events_per_second = "N/A"
            total_time = "N/A"

            # Look for performance metrics
            events_match = re.search(r'events per second:\s+([\d.]+)', output)
            if events_match:
                events_per_second = float(events_match.group(1))

            time_match = re.search(r'total time:\s+([\d.]+)s', output)
            if time_match:
                total_time = float(time_match.group(1))

            # Analyze overclocking
            oc_analyzer = OverclockAnalyzer()

            # Get CPU info
            cpu_model = "Unknown"
            if self.hardware_detector:
                cpu_info = self.hardware_detector.detect_cpu()
                cpu_model = cpu_info.get('model', 'Unknown')

            # CPU overclock analysis
            cpu_freq = oc_analyzer.get_current_cpu_freq()
            cpu_oc = oc_analyzer.analyze_cpu_overclock(cpu_model, cpu_freq)

            # RAM overclock analysis
            ram_oc = oc_analyzer.get_ram_specs()

            # Estimate stock performance if overclocked
            stock_perf = {}
            if cpu_oc.get('overclocked') and events_per_second != "N/A":
                stock_perf = oc_analyzer.estimate_stock_performance(
                    events_per_second,
                    cpu_oc['boost_overclock_percent']
                )

            results = {
                "benchmark_type": "sysbench",
                "status": "completed",
                "threads_used": threads,
                "events_per_second": events_per_second,
                "total_time_seconds": total_time,
                "duration_seconds": round(duration, 2),
                "overclock_analysis": {
                    "cpu": cpu_oc,
                    "ram": ram_oc,
                    "stock_performance_estimate": stock_perf
                },
                "timestamp": datetime.now().isoformat()
            }

            # Display overclock info
            self._display_overclock_analysis(cpu_oc, ram_oc, stock_perf)

            self._save_results(results)
            return results

        except subprocess.TimeoutExpired:
            self.logger.error("Sysbench timed out")
            return {
                "benchmark_type": "sysbench",
                "status": "error",
                "error": "Benchmark timed out"
            }
        except Exception as e:
            self.logger.error(f"Sysbench failed: {str(e)}")
            return {
                "benchmark_type": "sysbench",
                "status": "error",
                "error": str(e)
            }

    def run_benchmark(self, prefer_geekbench: bool = True) -> Dict:
        """
        Run CPU benchmark with automatic fallback

        Args:
            prefer_geekbench: Prefer Geekbench over sysbench

        Returns:
            dict: Benchmark results
        """
        if prefer_geekbench and self.check_geekbench_installed():
            return self.run_geekbench()
        elif self.check_sysbench_installed():
            return self.run_sysbench()
        else:
            self.logger.error("No CPU benchmark tool available")
            return {
                "benchmark_type": "none",
                "status": "error",
                "error": "No CPU benchmark tool installed (install geekbench or sysbench)"
            }

    def _display_overclock_analysis(self, cpu_oc, ram_oc, stock_perf):
        """Display overclock analysis"""
        print(f"\n{'='*70}")
        print("OVERCLOCK ANALYSIS")
        print(f"{'='*70}")

        # CPU Overclock
        if cpu_oc.get('overclocked'):
            print("\n✓ CPU IS OVERCLOCKED!")
            print(f"  Stock Boost:  {cpu_oc['stock_boost_ghz']} GHz")
            print(f"  Actual Max:   {cpu_oc['actual_max_ghz']} GHz")
            print(f"  Overclock:    +{cpu_oc['boost_overclock_percent']}%")

            if stock_perf:
                print(f"\n💡 PERFORMANCE UPLIFT:")
                print(f"  Actual Score:     {stock_perf['actual_score']:.2f} events/sec")
                print(f"  Stock Estimate:   {stock_perf['estimated_stock_score']:.2f} events/sec")
                print(f"  Performance Gain: +{stock_perf['performance_gain_percent']}%")
        else:
            print("\n  CPU running at stock speeds")

        # RAM Overclock
        if ram_oc.get('overclocked'):
            print(f"\n✓ RAM IS OVERCLOCKED!")
            print(f"  JEDEC Standard: {ram_oc['jedec_standard_mhz']} MHz")
            print(f"  Actual Speed:   {ram_oc['actual_speed_mhz']} MHz")
            print(f"  Overclock:      +{ram_oc['overclock_percent']}%")
        else:
            if ram_oc.get('actual_speed_mhz'):
                print(f"\n  RAM running at JEDEC speeds ({ram_oc['actual_speed_mhz']} MHz)")

        print(f"\n{'='*70}\n")

    def _save_results(self, results: Dict):
        """
        Save benchmark results to JSON file

        Args:
            results: Benchmark results dictionary
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.results_dir / f"cpu_benchmark_{timestamp}.json"

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

    benchmark = CPUBenchmark(base_dir, hw_detector)

    print("\nRunning CPU benchmark...")
    results = benchmark.run_benchmark()

    print("\n" + "="*60)
    print("BENCHMARK RESULTS")
    print("="*60)
    for key, value in results.items():
        print(f"{key}: {value}")
    print("="*60)
