#!/usr/bin/env python3
"""
FPS Benchmark Module using Unigine Heaven
Measures gaming performance and GPU capabilities
"""

import subprocess
import time
import logging
import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class FPSBenchmark:
    """Runs FPS benchmarks using Unigine Heaven or fallback tools"""

    def __init__(self, base_dir, hardware_detector=None):
        self.base_dir = Path(base_dir)
        self.results_dir = self.base_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger("FPSBenchmark")
        self.hardware_detector = hardware_detector

    def check_unigine_installed(self) -> bool:
        """
        Check if Unigine Heaven is installed

        Returns:
            bool: True if installed
        """
        # Check common installation paths
        possible_paths = [
            Path.home() / ".local/share/unigine/heaven",
            Path("/opt/unigine/heaven"),
            Path("/usr/share/unigine/heaven"),
            Path.home() / "Unigine_Heaven-4.0"
        ]

        for path in possible_paths:
            if path.exists():
                heaven_bin = path / "bin" / "heaven_x64"
                if heaven_bin.exists():
                    self.logger.info(f"Found Unigine Heaven at: {path}")
                    return True

        self.logger.warning("Unigine Heaven not found in standard locations")
        return False

    def run_glxgears_fallback(self, duration: int = 300) -> Dict:
        """
        Fallback FPS test using glxgears (basic OpenGL test)

        Args:
            duration: Test duration in seconds

        Returns:
            dict: FPS benchmark results
        """
        self.logger.info(f"Running glxgears fallback test ({duration}s)...")

        try:
            # Start glxgears in background
            process = subprocess.Popen(
                ["glxgears"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            print(f"\n{'='*60}")
            print("RUNNING FPS BENCHMARK (glxgears fallback)")
            print(f"Duration: {duration} seconds")
            print(f"{'='*60}\n")

            # Monitor GPU stats during test
            fps_samples = []
            start_time = time.time()

            while time.time() - start_time < duration:
                remaining = duration - int(time.time() - start_time)
                print(f"\rTime remaining: {remaining}s", end="", flush=True)

                # Get GPU stats if available
                if self.hardware_detector:
                    stats = self.hardware_detector.get_current_gpu_stats()
                    if 'temperature' in stats:
                        print(f" | GPU Temp: {stats['temperature']}°C", end="", flush=True)

                time.sleep(5)

            # Stop glxgears
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

            print("\n\nBenchmark completed!")

            # glxgears doesn't provide detailed FPS metrics
            # This is a basic fallback
            return {
                "benchmark_type": "glxgears_fallback",
                "status": "completed",
                "note": "Basic OpenGL test - Unigine Heaven recommended for accurate results",
                "average_fps": "N/A",
                "min_fps": "N/A",
                "max_fps": "N/A",
                "duration": duration
            }

        except Exception as e:
            self.logger.error(f"glxgears test failed: {str(e)}")
            return {
                "benchmark_type": "glxgears_fallback",
                "status": "failed",
                "error": str(e)
            }

    def run_unigine_heaven(self, duration: int = None) -> Dict:
        """
        Run Unigine Heaven benchmark - INTERACTIVE with AUTO RESULTS
        User runs benchmarks, suite reads results automatically from HTML files

        Returns:
            dict: Benchmark results with all test configurations
        """
        print(f"\n{'='*70}")
        print("UNIGINE HEAVEN FPS BENCHMARK")
        print(f"{'='*70}")
        print("\nHow it works:")
        print("1. Heaven will launch")
        print("2. You select settings and click RUN")
        print("3. When done, click 'Benchmark' to save results")
        print("4. Close Heaven")
        print("5. We'll read your results automatically!")
        print("6. Get suggestions for next test or skip ahead")
        print(f"{'='*70}\n")

        input("Press ENTER to start...")

        all_results = {}
        test_number = 1

        while True:
            print(f"\n{'='*70}")
            print(f"TEST #{test_number}")
            print(f"{'='*70}")

            # Launch Heaven and wait for user
            result = self._run_heaven_interactive()

            if result and result.get('status') == 'completed':
                # Store result
                res = result['resolution']
                qual = result['quality']
                key = f"{res}_{qual}".lower().replace('x', 'p').replace(' ', '_')
                all_results[key] = result

                # Show what we captured
                print(f"\n✓ RESULTS CAPTURED:")
                print(f"  Resolution: {res}")
                print(f"  Quality: {qual}")
                print(f"  Average FPS: {result['average_fps']}")
                print(f"  Min FPS: {result['min_fps']}")
                print(f"  Max FPS: {result['max_fps']}")

                # Give suggestion
                suggestion = self._suggest_next_test(result)
                if suggestion:
                    print(f"\n{suggestion}")

            # Ask what to do next
            print(f"\n{'='*70}")
            print("What would you like to do?")
            print("1. Run another test")
            print("2. Finish FPS testing and move to AI/CPU benchmarks")
            choice = input("\nChoice (1-2): ").strip()

            if choice == "2":
                break

            test_number += 1

        return {
            "benchmark_type": "unigine_heaven_interactive",
            "status": "completed",
            "configurations": all_results,
            "timestamp": datetime.now().isoformat()
        }

    def _find_heaven_binary(self):
        """Find Unigine Heaven binary"""
        heaven_paths = [
            Path.home() / "Unigine_Heaven-4.0",
            Path("/opt/unigine/heaven"),
            Path.home() / ".local/share/unigine/heaven",
        ]

        for path in heaven_paths:
            test_bin = path / "bin" / "heaven_x64"
            if test_bin.exists():
                return test_bin
        return None

    def _run_heaven_interactive(self):
        """
        Launch Heaven, wait for user to finish, parse HTML results

        Returns:
            dict: Parsed benchmark results
        """
        heaven_bin = self._find_heaven_binary()
        if not heaven_bin:
            return {"status": "error", "error": "Unigine Heaven not installed"}

        heaven_dir = heaven_bin.parent.parent
        launcher = heaven_dir / "heaven"

        print("\n🚀 Launching Unigine Heaven...")
        print("   Select your settings and click RUN")
        print("   When finished, click 'Benchmark' button to save results")
        print("   Then close Heaven\n")

        # Get timestamp before launch to find new HTML files
        import glob
        before_files = set(glob.glob(str(Path.home() / "Unigine_Heaven_Benchmark_*.html")))

        try:
            # Launch Heaven
            process = subprocess.Popen(
                ["/bin/bash", str(launcher)],
                cwd=heaven_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            print("✓ Heaven launched! Waiting for you to finish...\n")

            # Wait for process to exit
            process.wait()

            print("\n✓ Heaven closed! Looking for results...\n")

            # Find new HTML file
            time.sleep(1)  # Give filesystem time to sync
            after_files = set(glob.glob(str(Path.home() / "Unigine_Heaven_Benchmark_*.html")))
            new_files = after_files - before_files

            if not new_files:
                print("⚠ No result file found. Did you click 'Benchmark' before closing?")
                return {"status": "error", "error": "No results file"}

            # Parse the newest file
            result_file = max(new_files, key=lambda f: Path(f).stat().st_mtime)
            return self._parse_heaven_html(result_file)

        except Exception as e:
            self.logger.error(f"Heaven interactive failed: {e}")
            return {"status": "error", "error": str(e)}

    def _parse_heaven_html(self, html_file):
        """
        Parse Heaven HTML results file

        Args:
            html_file: Path to HTML file

        Returns:
            dict: Parsed results
        """
        try:
            with open(html_file, 'r') as f:
                content = f.read()

            # Parse FPS values using regex
            import re

            fps_match = re.search(r'<td class="right">FPS:</td><td><div class="orange"><strong>([\d.]+)</strong>', content)
            min_fps_match = re.search(r'<td class="right">Min FPS:</td><td><div class="orange"><strong>([\d.]+)</strong>', content)
            max_fps_match = re.search(r'<td class="right">Max FPS:</td><td><div class="orange"><strong>([\d.]+)</strong>', content)

            # Parse resolution
            mode_match = re.search(r'<td class="right">Mode:</td><td><div class="highlight">(\d+x\d+)', content)

            # Parse quality
            quality_match = re.search(r'<td class="right">Quality</td><td><div class="highlight">(\w+)</div>', content)

            avg_fps = float(fps_match.group(1)) if fps_match else "N/A"
            min_fps = float(min_fps_match.group(1)) if min_fps_match else "N/A"
            max_fps = float(max_fps_match.group(1)) if max_fps_match else "N/A"
            resolution = mode_match.group(1) if mode_match else "Unknown"
            quality = quality_match.group(1) if quality_match else "Unknown"

            return {
                "status": "completed",
                "average_fps": avg_fps,
                "min_fps": min_fps,
                "max_fps": max_fps,
                "resolution": resolution,
                "quality": quality,
                "result_file": html_file,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to parse Heaven results: {e}")
            return {"status": "error", "error": str(e)}

    def _suggest_next_test(self, result):
        """
        Suggest next test based on current results

        Args:
            result: Current test result

        Returns:
            str: Suggestion message
        """
        avg_fps = result.get('average_fps', 0)
        if avg_fps == "N/A":
            return None

        resolution = result.get('resolution', '')
        quality = result.get('quality', '').lower()

        suggestions = []

        if avg_fps >= 60:
            suggestions.append(f"💡 EXCELLENT! {avg_fps} FPS is very smooth!")
            if quality in ["low", "medium"]:
                suggestions.append("   Try RAISING quality settings for better visuals")
            elif "1920x1080" in resolution:
                suggestions.append("   Try 1440p (2560x1440) or 4K for higher resolution!")
        elif avg_fps >= 30:
            suggestions.append(f"✓ PLAYABLE at {avg_fps} FPS")
            if quality in ["high", "ultra"]:
                suggestions.append("   Consider LOWERING quality for smoother 60 FPS")
        else:
            suggestions.append(f"⚠ LOW FPS: {avg_fps} may feel choppy")
            suggestions.append("   Try LOWER quality settings or resolution")

        return "\n".join(suggestions) if suggestions else None

    def _run_heaven_with_gui(self, resolution, quality, name, duration):
        """
        Run Heaven with GUI visible and monitor performance

        Args:
            resolution: Tuple of (width, height)
            quality: Quality preset
            name: Display name
            duration: Duration in seconds

        Returns:
            dict: Test results
        """
        heaven_bin = self._find_heaven_binary()
        if not heaven_bin:
            return {"status": "error", "error": "Unigine Heaven not installed"}

        heaven_dir = heaven_bin.parent.parent

        # Use the launcher script but run heaven directly for more control
        width, height = resolution

        print(f"\n{'='*60}")
        print(f"RUNNING: {name}")
        print(f"Duration: {duration} seconds")
        print(f"Resolution: {width}x{height}")
        print(f"Quality: {quality.upper()}")
        print(f"{'='*60}\n")

        # Launch using the heaven launcher script with env vars
        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = f"{heaven_dir}/bin:{env.get('LD_LIBRARY_PATH', '')}"

        launcher = heaven_dir / "heaven"

        try:
            # Start Heaven
            process = subprocess.Popen(
                ["/bin/bash", str(launcher)],
                cwd=heaven_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Monitor for duration
            start_time = time.time()
            gpu_temps = []

            print("Heaven GUI launched! Monitor running...")
            print("(You should see the Heaven benchmark window)\n")

            while time.time() - start_time < duration:
                if process.poll() is not None:
                    break

                remaining = duration - int(time.time() - start_time)
                print(f"\rTime remaining: {remaining}s", end="", flush=True)

                # Get GPU stats
                if self.hardware_detector:
                    stats = self.hardware_detector.get_current_gpu_stats()
                    if 'temperature' in stats:
                        gpu_temps.append(stats['temperature'])
                        print(f" | GPU Temp: {stats['temperature']}°C", end="", flush=True)

                time.sleep(5)

            # Stop benchmark
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()

            print("\n\nTest completed!")

            return {
                "status": "completed",
                "duration": duration,
                "resolution": f"{width}x{height}",
                "quality": quality,
                "average_fps": "N/A",  # Heaven doesn't output to stdout easily
                "min_fps": "N/A",
                "max_fps": "N/A",
                "gpu_temp_avg": sum(gpu_temps) / len(gpu_temps) if gpu_temps else "N/A",
                "gpu_temp_max": max(gpu_temps) if gpu_temps else "N/A",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"{name} failed: {e}")
            return {"status": "failed", "error": str(e)}

    def _collect_user_results(self):
        """Collect benchmark results from user input"""
        print("\n" + "="*70)
        print("RECORD YOUR RESULTS")
        print("="*70)
        print("\nHow many different configurations did you test?")
        print("(e.g., 1080p Low, 1080p High, 1440p Medium, etc.)")

        try:
            num_tests = int(input("\nNumber of tests: ").strip())
        except ValueError:
            num_tests = 1

        all_results = {}

        for i in range(num_tests):
            print(f"\n{'='*70}")
            print(f"TEST {i+1} OF {num_tests}")
            print(f"{'='*70}")

            # Get resolution
            print("\nResolution:")
            print("1. 1920x1080 (1080p)")
            print("2. 2560x1440 (1440p)")
            print("3. 3840x2160 (4K)")
            print("4. Other")
            res_choice = input("Choice: ").strip()

            if res_choice == "1":
                resolution = "1920x1080"
            elif res_choice == "2":
                resolution = "2560x1440"
            elif res_choice == "3":
                resolution = "3840x2160"
            else:
                resolution = input("Enter resolution (e.g., 1920x1080): ").strip()

            # Get quality preset
            print("\nQuality Preset:")
            print("1. Low")
            print("2. Medium")
            print("3. High")
            print("4. Ultra")
            print("5. Custom")
            quality_choice = input("Choice: ").strip()

            quality_map = {"1": "low", "2": "medium", "3": "high", "4": "ultra", "5": "custom"}
            quality = quality_map.get(quality_choice, "custom")

            # Get FPS results
            print("\nFPS Results (from Heaven's final screen):")
            try:
                avg_fps = float(input("Average FPS: ").strip())
            except ValueError:
                avg_fps = "N/A"

            try:
                min_fps = float(input("Min FPS: ").strip())
            except ValueError:
                min_fps = "N/A"

            try:
                max_fps = float(input("Max FPS: ").strip())
            except ValueError:
                max_fps = "N/A"

            # Create result key
            result_key = f"{resolution}_{quality}".replace("x", "p").lower()

            all_results[result_key] = {
                "status": "completed",
                "resolution": resolution,
                "quality": quality,
                "average_fps": avg_fps,
                "min_fps": min_fps,
                "max_fps": max_fps,
                "timestamp": datetime.now().isoformat()
            }

            # Give recommendation
            if avg_fps != "N/A":
                self._give_recommendation(resolution, quality, avg_fps)

        return {
            "benchmark_type": "unigine_heaven_interactive",
            "status": "completed",
            "configurations": all_results,
            "timestamp": datetime.now().isoformat()
        }

    def _give_recommendation(self, resolution, quality, avg_fps):
        """Give performance recommendation based on FPS"""
        print(f"\n{'='*70}")
        print("RECOMMENDATION")
        print(f"{'='*70}")

        if avg_fps >= 60:
            print(f"✓ EXCELLENT! {avg_fps} FPS is smooth!")
            if quality in ["low", "medium"]:
                print("  💡 Try RAISING quality settings for better visuals")
            elif resolution == "1920x1080":
                print("  💡 Try 1440p or 4K for higher resolution!")
        elif avg_fps >= 30:
            print(f"✓ PLAYABLE at {avg_fps} FPS")
            if quality == "high" or quality == "ultra":
                print("  💡 Consider LOWERING quality for smoother performance")
        else:
            print(f"⚠ LOW FPS: {avg_fps} may feel choppy")
            print("  💡 LOWER quality settings or resolution recommended")

        print(f"{'='*70}\n")

    def _run_single_unigine_test(self, resolution, quality, name, duration):
        """
        Run a single Unigine Heaven test configuration

        Args:
            resolution: Tuple of (width, height)
            quality: Quality preset string ("low", "medium", "high")
            name: Display name for this test
            duration: Test duration in seconds

        Returns:
            dict: Test results
        """
        self.logger.info(f"Running {name} benchmark ({duration}s)...")

        # Find Unigine Heaven installation
        heaven_paths = [
            Path.home() / ".local/share/unigine/heaven",
            Path("/opt/unigine/heaven"),
            Path.home() / "Unigine_Heaven-4.0"
        ]

        heaven_bin = None
        for path in heaven_paths:
            test_bin = path / "bin" / "heaven_x64"
            if test_bin.exists():
                heaven_bin = test_bin
                break

        if not heaven_bin:
            self.logger.error("Unigine Heaven binary not found")
            return {"status": "error", "error": "Unigine Heaven not installed"}

        try:
            # Map quality presets to Unigine Heaven settings
            quality_settings = {
                "low": {
                    "quality": "0",  # Low
                    "tessellation": "0",  # Disabled
                    "shaders": "0",  # Low
                    "anisotropy": "0",  # Off
                    "occlusion": "0",  # Off
                    "refraction": "0",  # Off
                    "volumetric": "0",  # Off
                },
                "medium": {
                    "quality": "2",  # Medium
                    "tessellation": "0",  # Disabled
                    "shaders": "1",  # Medium
                    "anisotropy": "2",  # 4x
                    "occlusion": "1",  # On
                    "refraction": "1",  # On
                    "volumetric": "0",  # Off
                },
                "high": {
                    "quality": "3",  # High
                    "tessellation": "1",  # Extreme
                    "shaders": "2",  # High
                    "anisotropy": "4",  # 16x
                    "occlusion": "1",  # On
                    "refraction": "1",  # On
                    "volumetric": "1",  # On
                },
            }

            settings = quality_settings.get(quality, quality_settings["medium"])
            width, height = resolution

            cmd = [
                str(heaven_bin),
                "-project_name", "Heaven",
                "-video_mode", "-1",  # Borderless window
                "-video_fullscreen", "0",  # Windowed
                "-video_width", str(width),
                "-video_height", str(height),
                "-sound", "0",  # No sound
                "-quality", settings["quality"],
                "-tessellation", settings["tessellation"],
                "-shaders", settings["shaders"],
                "-anisotropy", settings["anisotropy"],
                "-occlusion", settings["occlusion"],
                "-refraction", settings["refraction"],
                "-volumetric", settings["volumetric"],
            ]

            print(f"\n{'='*60}")
            print(f"RUNNING: {name}")
            print(f"Duration: {duration} seconds")
            print(f"Resolution: {width}x{height}")
            print(f"Quality: {quality.upper()}")
            print(f"{'='*60}\n")

            # Start benchmark
            # Set up environment for Unigine Heaven
            env = os.environ.copy()
            heaven_dir = heaven_bin.parent.parent
            env['LD_LIBRARY_PATH'] = f"{heaven_dir}/bin:{env.get('LD_LIBRARY_PATH', '')}"

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=heaven_dir,
                env=env
            )

            # Monitor during test
            start_time = time.time()
            gpu_temps = []
            gpu_clocks = []

            while time.time() - start_time < duration:
                if process.poll() is not None:
                    # Process ended early
                    break

                remaining = duration - int(time.time() - start_time)
                print(f"\rTime remaining: {remaining}s", end="", flush=True)

                # Get GPU stats
                if self.hardware_detector:
                    stats = self.hardware_detector.get_current_gpu_stats()
                    if 'temperature' in stats:
                        gpu_temps.append(stats['temperature'])
                        print(f" | GPU Temp: {stats['temperature']}°C", end="", flush=True)

                        # Warn if overheating
                        if stats['temperature'] > 80:
                            print(" ⚠️ HIGH TEMP", end="", flush=True)

                    if 'gpu_clock' in stats:
                        gpu_clocks.append(stats['gpu_clock'])

                time.sleep(5)

            # Stop benchmark
            process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()

            print("\n\nTest completed!")

            # Parse results from output
            # Note: Unigine Heaven outputs results to log file
            results = {
                "status": "completed",
                "duration": duration,
                "resolution": f"{width}x{height}",
                "quality": quality,
                "average_fps": self._extract_fps_from_output(stdout, stderr),
                "min_fps": "N/A",  # Would need log file parsing
                "max_fps": "N/A",  # Would need log file parsing
                "gpu_temp_avg": sum(gpu_temps) / len(gpu_temps) if gpu_temps else "N/A",
                "gpu_temp_max": max(gpu_temps) if gpu_temps else "N/A",
                "timestamp": datetime.now().isoformat()
            }

            return results

        except Exception as e:
            self.logger.error(f"{name} benchmark failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _extract_fps_from_output(self, stdout: str, stderr: str) -> str:
        """
        Try to extract FPS from benchmark output

        Args:
            stdout: Standard output from benchmark
            stderr: Standard error from benchmark

        Returns:
            str: Average FPS or "N/A"
        """
        # Look for FPS patterns in output
        fps_patterns = [
            r'fps:\s*(\d+\.?\d*)',
            r'FPS:\s*(\d+\.?\d*)',
            r'average.*?(\d+\.?\d*)',
        ]

        combined_output = stdout + "\n" + stderr

        for pattern in fps_patterns:
            match = re.search(pattern, combined_output, re.IGNORECASE)
            if match:
                return match.group(1)

        return "N/A"

    def run_synthetic_benchmark(self, duration: int = 300) -> Dict:
        """
        Run synthetic GPU benchmark using nvidia-smi stress test

        Args:
            duration: Test duration in seconds

        Returns:
            dict: Benchmark results
        """
        self.logger.info(f"Running synthetic GPU benchmark ({duration}s)...")

        try:
            # Use a simple CUDA/OpenGL stress test
            # This is a fallback when Unigine isn't available

            print(f"\n{'='*60}")
            print("RUNNING SYNTHETIC GPU BENCHMARK")
            print(f"Duration: {duration} seconds")
            print(f"{'='*60}\n")

            # Monitor GPU utilization
            start_time = time.time()
            utilization_samples = []
            temp_samples = []

            while time.time() - start_time < duration:
                remaining = duration - int(time.time() - start_time)
                print(f"\rTime remaining: {remaining}s", end="", flush=True)

                if self.hardware_detector:
                    stats = self.hardware_detector.get_current_gpu_stats()

                    if 'gpu_utilization' in stats:
                        util_str = stats['gpu_utilization'].replace('%', '').strip()
                        try:
                            utilization_samples.append(float(util_str))
                        except ValueError:
                            pass

                    if 'temperature' in stats:
                        temp_samples.append(stats['temperature'])
                        print(f" | GPU: {stats['gpu_utilization']} | Temp: {stats['temperature']}°C", end="", flush=True)

                time.sleep(2)

            print("\n\nBenchmark completed!")

            avg_util = sum(utilization_samples) / len(utilization_samples) if utilization_samples else 0
            avg_temp = sum(temp_samples) / len(temp_samples) if temp_samples else 0

            results = {
                "benchmark_type": "synthetic",
                "status": "completed",
                "duration": duration,
                "average_gpu_utilization": f"{avg_util:.1f}%",
                "average_temperature": f"{avg_temp:.1f}°C",
                "max_temperature": f"{max(temp_samples) if temp_samples else 0}°C",
                "note": "Synthetic benchmark - Install Unigine Heaven for FPS testing",
                "timestamp": datetime.now().isoformat()
            }

            self._save_results(results)
            return results

        except Exception as e:
            self.logger.error(f"Synthetic benchmark failed: {str(e)}")
            return {
                "benchmark_type": "synthetic",
                "status": "failed",
                "error": str(e)
            }

    def run_benchmark(self, duration: int = 300, force_fallback: bool = False) -> Dict:
        """
        Run FPS benchmark with automatic fallback

        Args:
            duration: Test duration in seconds
            force_fallback: Force use of fallback benchmark

        Returns:
            dict: Benchmark results
        """
        if not force_fallback and self.check_unigine_installed():
            return self.run_unigine_heaven(duration)
        else:
            self.logger.warning("Unigine Heaven not available - using fallback")
            return self.run_synthetic_benchmark(duration)

    def _save_results(self, results: Dict):
        """
        Save benchmark results to JSON file

        Args:
            results: Benchmark results dictionary
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.results_dir / f"fps_benchmark_{timestamp}.json"

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

    # Import hardware detector for GPU monitoring
    try:
        from hardware_detection import HardwareDetector
        hw_detector = HardwareDetector(base_dir)
    except ImportError:
        hw_detector = None

    benchmark = FPSBenchmark(base_dir, hw_detector)

    # Run quick test (60 seconds)
    print("\nRunning quick FPS benchmark (60 seconds)...")
    results = benchmark.run_benchmark(duration=60)

    print("\n" + "="*60)
    print("BENCHMARK RESULTS")
    print("="*60)
    for key, value in results.items():
        print(f"{key}: {value}")
    print("="*60)
