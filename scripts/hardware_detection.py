#!/usr/bin/env python3
"""
Hardware Detection Module for GPU Benchmark Suite
Detects and logs all system hardware specifications
"""

import subprocess
import json
import logging
import re
from datetime import datetime
from pathlib import Path


class HardwareDetector:
    """Detects and logs system hardware specifications"""

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.results_dir = self.base_dir / "results"
        self.results_dir.mkdir(exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger("HardwareDetector")

    def run_command(self, command, shell=False):
        """
        Execute shell command and return output

        Args:
            command: Command to execute (list or string)
            shell: Whether to use shell execution

        Returns:
            tuple: (success: bool, output: str, error: str)
        """
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=30
            )
            return (result.returncode == 0, result.stdout.strip(), result.stderr.strip())
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {command}")
            return (False, "", "Command timed out")
        except Exception as e:
            self.logger.error(f"Command failed: {command} - {str(e)}")
            return (False, "", str(e))

    def detect_gpu(self):
        """
        Detect GPU information using nvidia-smi

        Returns:
            dict: GPU information or error details
        """
        self.logger.info("Detecting GPU...")

        # Check if nvidia-smi exists
        success, _, _ = self.run_command(["which", "nvidia-smi"])
        if not success:
            self.logger.warning("nvidia-smi not found - attempting to detect GPU manually")
            return {
                "detected": False,
                "error": "nvidia-smi not found",
                "model": "Unknown",
                "vram": "Unknown",
                "driver_version": "Unknown"
            }

        # Get GPU name
        success, gpu_name, error = self.run_command([
            "nvidia-smi",
            "--query-gpu=name",
            "--format=csv,noheader"
        ])

        if not success:
            self.logger.error(f"Failed to detect GPU name: {error}")
            return {
                "detected": False,
                "error": error,
                "model": "Unknown"
            }

        # Get GPU memory
        success, gpu_memory, _ = self.run_command([
            "nvidia-smi",
            "--query-gpu=memory.total",
            "--format=csv,noheader"
        ])

        # Get driver version
        success_driver, driver_ver, _ = self.run_command([
            "nvidia-smi",
            "--query-gpu=driver_version",
            "--format=csv,noheader"
        ])

        # Get GPU clocks
        success_clocks, gpu_clocks, _ = self.run_command([
            "nvidia-smi",
            "--query-gpu=clocks.current.graphics,clocks.current.memory",
            "--format=csv,noheader"
        ])

        # Get temperature
        success_temp, gpu_temp, _ = self.run_command([
            "nvidia-smi",
            "--query-gpu=temperature.gpu",
            "--format=csv,noheader"
        ])

        gpu_info = {
            "detected": True,
            "model": gpu_name.strip(),
            "vram": gpu_memory.strip() if success else "Unknown",
            "driver_version": driver_ver.strip() if success_driver else "Unknown",
            "clock_speed": gpu_clocks.strip() if success_clocks else "Unknown",
            "temperature": f"{gpu_temp.strip()}°C" if success_temp else "Unknown"
        }

        self.logger.info(f"GPU detected: {gpu_info['model']}")
        return gpu_info

    def detect_cpu(self):
        """
        Detect CPU information using lscpu

        Returns:
            dict: CPU information
        """
        self.logger.info("Detecting CPU...")

        success, lscpu_output, error = self.run_command(["lscpu"])

        if not success:
            self.logger.error(f"Failed to detect CPU: {error}")
            return {
                "detected": False,
                "error": error,
                "model": "Unknown"
            }

        cpu_info = {
            "detected": True,
            "model": "Unknown",
            "cores": "Unknown",
            "threads": "Unknown",
            "architecture": "Unknown",
            "max_mhz": "Unknown"
        }

        # Parse lscpu output
        for line in lscpu_output.split('\n'):
            if "Model name:" in line:
                cpu_info["model"] = line.split(":", 1)[1].strip()
            elif "CPU(s):" in line and "NUMA" not in line and "On-line" not in line:
                cpu_info["threads"] = line.split(":", 1)[1].strip()
            elif "Core(s) per socket:" in line:
                cpu_info["cores"] = line.split(":", 1)[1].strip()
            elif "Architecture:" in line:
                cpu_info["architecture"] = line.split(":", 1)[1].strip()
            elif "CPU max MHz:" in line:
                cpu_info["max_mhz"] = line.split(":", 1)[1].strip()

        self.logger.info(f"CPU detected: {cpu_info['model']}")
        return cpu_info

    def detect_ram(self):
        """
        Detect RAM information using dmidecode and free

        Returns:
            dict: RAM information
        """
        self.logger.info("Detecting RAM...")

        # Get total RAM
        success, mem_output, _ = self.run_command(["free", "-h"])

        ram_info = {
            "detected": True,
            "total": "Unknown",
            "speed": "Unknown",
            "type": "Unknown",
            "sticks": "Unknown"
        }

        if success:
            for line in mem_output.split('\n'):
                if line.startswith("Mem:"):
                    parts = line.split()
                    if len(parts) >= 2:
                        ram_info["total"] = parts[1]

        # Try to get detailed info with dmidecode (requires root)
        success, dmidecode_output, _ = self.run_command(
            ["sudo", "dmidecode", "-t", "memory"],
            shell=False
        )

        if success:
            stick_count = 0
            for line in dmidecode_output.split('\n'):
                if "Speed:" in line and "Unknown" not in line and ram_info["speed"] == "Unknown":
                    ram_info["speed"] = line.split(":", 1)[1].strip()
                elif "Type:" in line and "Error" not in line and ram_info["type"] == "Unknown":
                    type_val = line.split(":", 1)[1].strip()
                    if type_val in ["DDR3", "DDR4", "DDR5"]:
                        ram_info["type"] = type_val
                elif "Size:" in line and "No Module Installed" not in line:
                    stick_count += 1

            if stick_count > 0:
                ram_info["sticks"] = str(stick_count)

        self.logger.info(f"RAM detected: {ram_info['total']}")
        return ram_info

    def detect_motherboard(self):
        """
        Detect motherboard information

        Returns:
            dict: Motherboard information
        """
        self.logger.info("Detecting motherboard...")

        mobo_info = {
            "detected": True,
            "manufacturer": "Unknown",
            "product": "Unknown",
            "version": "Unknown"
        }

        # Try dmidecode for motherboard info
        success, output, _ = self.run_command(
            ["sudo", "dmidecode", "-t", "baseboard"],
            shell=False
        )

        if success:
            for line in output.split('\n'):
                if "Manufacturer:" in line:
                    mobo_info["manufacturer"] = line.split(":", 1)[1].strip()
                elif "Product Name:" in line:
                    mobo_info["product"] = line.split(":", 1)[1].strip()
                elif "Version:" in line:
                    mobo_info["version"] = line.split(":", 1)[1].strip()

        self.logger.info(f"Motherboard detected: {mobo_info['manufacturer']} {mobo_info['product']}")
        return mobo_info

    def detect_storage(self):
        """
        Detect storage devices

        Returns:
            list: List of storage devices
        """
        self.logger.info("Detecting storage devices...")

        success, lsblk_output, _ = self.run_command([
            "lsblk", "-d", "-o", "NAME,SIZE,TYPE,MODEL", "-n"
        ])

        if not success:
            return [{
                "detected": False,
                "error": "Failed to detect storage"
            }]

        storage_devices = []
        for line in lsblk_output.split('\n'):
            if not line.strip():
                continue

            parts = line.split()
            if len(parts) >= 3 and parts[2] == "disk":
                device_name = parts[0]
                size = parts[1]
                model = " ".join(parts[3:]) if len(parts) > 3 else "Unknown"

                # Determine if SSD or HDD
                success, rotational, _ = self.run_command(
                    f"cat /sys/block/{device_name}/queue/rotational",
                    shell=True
                )

                drive_type = "HDD" if rotational == "1" else "SSD"

                storage_devices.append({
                    "device": f"/dev/{device_name}",
                    "size": size,
                    "type": drive_type,
                    "model": model
                })

        self.logger.info(f"Storage devices detected: {len(storage_devices)}")
        return storage_devices

    def detect_system_info(self):
        """
        Detect system information (OS, kernel, uptime)

        Returns:
            dict: System information
        """
        self.logger.info("Detecting system information...")

        system_info = {
            "detected": True,
            "os": "Unknown",
            "kernel": "Unknown",
            "uptime": "Unknown",
            "hostname": "Unknown"
        }

        # Get OS info
        success, os_info, _ = self.run_command(["lsb_release", "-d"])
        if success:
            system_info["os"] = os_info.split(":", 1)[1].strip() if ":" in os_info else os_info

        # Get kernel version
        success, kernel, _ = self.run_command(["uname", "-r"])
        if success:
            system_info["kernel"] = kernel

        # Get uptime
        success, uptime, _ = self.run_command(["uptime", "-p"])
        if success:
            system_info["uptime"] = uptime

        # Get hostname
        success, hostname, _ = self.run_command(["hostname"])
        if success:
            system_info["hostname"] = hostname

        return system_info

    def detect_all(self):
        """
        Run all hardware detection methods

        Returns:
            dict: Complete hardware information
        """
        self.logger.info("Starting complete hardware detection...")

        hardware_info = {
            "detection_timestamp": datetime.now().isoformat(),
            "gpu": self.detect_gpu(),
            "cpu": self.detect_cpu(),
            "ram": self.detect_ram(),
            "motherboard": self.detect_motherboard(),
            "storage": self.detect_storage(),
            "system": self.detect_system_info()
        }

        # Save to JSON file
        output_file = self.results_dir / f"hardware_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(output_file, 'w') as f:
                json.dump(hardware_info, f, indent=2)
            self.logger.info(f"Hardware detection saved to: {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to save hardware detection: {str(e)}")

        return hardware_info

    def get_current_gpu_stats(self):
        """
        Get real-time GPU statistics (temp, clock, power)

        Returns:
            dict: Current GPU statistics
        """
        stats = {}

        # Temperature
        success, temp, _ = self.run_command([
            "nvidia-smi",
            "--query-gpu=temperature.gpu",
            "--format=csv,noheader"
        ])
        if success:
            stats["temperature"] = int(temp.strip())

        # GPU clock
        success, clock, _ = self.run_command([
            "nvidia-smi",
            "--query-gpu=clocks.current.graphics",
            "--format=csv,noheader"
        ])
        if success:
            stats["gpu_clock"] = clock.strip()

        # Memory clock
        success, mem_clock, _ = self.run_command([
            "nvidia-smi",
            "--query-gpu=clocks.current.memory",
            "--format=csv,noheader"
        ])
        if success:
            stats["memory_clock"] = mem_clock.strip()

        # Power draw
        success, power, _ = self.run_command([
            "nvidia-smi",
            "--query-gpu=power.draw",
            "--format=csv,noheader"
        ])
        if success:
            stats["power_draw"] = power.strip()

        # GPU utilization
        success, utilization, _ = self.run_command([
            "nvidia-smi",
            "--query-gpu=utilization.gpu",
            "--format=csv,noheader"
        ])
        if success:
            stats["gpu_utilization"] = utilization.strip()

        return stats


if __name__ == "__main__":
    # Test hardware detection
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Determine base directory
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = Path(__file__).parent.parent

    detector = HardwareDetector(base_dir)
    hardware_info = detector.detect_all()

    # Print summary
    print("\n" + "="*60)
    print("HARDWARE DETECTION SUMMARY")
    print("="*60)

    if hardware_info["gpu"]["detected"]:
        print(f"\nGPU: {hardware_info['gpu']['model']}")
        print(f"  VRAM: {hardware_info['gpu']['vram']}")
        print(f"  Driver: {hardware_info['gpu']['driver_version']}")

    if hardware_info["cpu"]["detected"]:
        print(f"\nCPU: {hardware_info['cpu']['model']}")
        print(f"  Cores: {hardware_info['cpu']['cores']}")
        print(f"  Threads: {hardware_info['cpu']['threads']}")

    print(f"\nRAM: {hardware_info['ram']['total']}")

    print(f"\nOS: {hardware_info['system']['os']}")
    print(f"Kernel: {hardware_info['system']['kernel']}")

    print("\n" + "="*60)
