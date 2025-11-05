#!/usr/bin/env python3
"""
Dependency Checker and Auto-Installer
Checks for required dependencies and installs them if missing
"""

import subprocess
import sys
import logging
from pathlib import Path
import shutil


class DependencyChecker:
    """Checks and installs required dependencies"""

    def __init__(self):
        self.logger = logging.getLogger("DependencyChecker")
        self.missing_deps = []
        self.missing_system_tools = []

    def check_python_packages(self):
        """Check for required Python packages"""
        required_packages = [
            'psutil',
            'requests',
            'cryptography'
        ]

        for package in required_packages:
            try:
                __import__(package)
                self.logger.info(f"✓ Python package found: {package}")
            except ImportError:
                self.logger.warning(f"✗ Python package missing: {package}")
                self.missing_deps.append(package)

        return len(self.missing_deps) == 0

    def check_system_tools(self):
        """Check for required system tools"""
        required_tools = {
            'nvidia-smi': 'NVIDIA drivers (nvidia-utils)',
            'lscpu': 'util-linux',
            'dmidecode': 'dmidecode',
            'stress-ng': 'stress-ng (optional - for CPU benchmark)',
            'sysbench': 'sysbench (optional - for CPU benchmark)',
        }

        for tool, package in required_tools.items():
            if shutil.which(tool):
                self.logger.info(f"✓ System tool found: {tool}")
            else:
                self.logger.warning(f"✗ System tool missing: {tool} ({package})")
                self.missing_system_tools.append((tool, package))

        return len(self.missing_system_tools) == 0

    def install_python_packages(self):
        """Install missing Python packages"""
        if not self.missing_deps:
            return True

        print("\n" + "="*70)
        print("MISSING PYTHON PACKAGES")
        print("="*70)
        print("\nThe following Python packages are required:")
        for pkg in self.missing_deps:
            print(f"  - {pkg}")

        response = input("\nInstall missing packages? (y/n): ").strip().lower()
        if response != 'y':
            return False

        try:
            print("\nInstalling packages...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--user', '--quiet'
            ] + self.missing_deps)
            print("✓ Packages installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install packages: {e}")
            return False

    def install_system_tools(self):
        """Provide instructions for installing system tools"""
        if not self.missing_system_tools:
            return True

        print("\n" + "="*70)
        print("MISSING SYSTEM TOOLS")
        print("="*70)
        print("\nThe following system tools are recommended:")

        packages_to_install = []
        for tool, package in self.missing_system_tools:
            print(f"  - {tool} ({package})")
            if 'optional' not in package.lower():
                packages_to_install.append(package.split()[0])

        if not packages_to_install:
            print("\nAll missing tools are optional. Benchmarks will use fallback methods.")
            return True

        print("\nTo install required tools, run:")
        print(f"  sudo apt update")
        print(f"  sudo apt install -y {' '.join(packages_to_install)}")

        response = input("\nAttempt to install now? (requires sudo) (y/n): ").strip().lower()
        if response == 'y':
            try:
                subprocess.check_call(['sudo', 'apt', 'update'])
                subprocess.check_call(['sudo', 'apt', 'install', '-y'] + packages_to_install)
                print("✓ System tools installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to install system tools: {e}")
                print("\n⚠ Installation failed. Please install manually.")
                return False

        return True

    def check_unigine_heaven(self):
        """Check if Unigine Heaven is available"""
        heaven_locations = [
            Path.home() / "Unigine_Heaven-4.0" / "bin" / "heaven_x64",
            Path("/opt/Unigine_Heaven-4.0/bin/heaven_x64"),
            Path("/usr/local/games/heaven/bin/heaven_x64"),
        ]

        for location in heaven_locations:
            if location.exists():
                self.logger.info(f"✓ Unigine Heaven found: {location}")
                return True

        self.logger.warning("✗ Unigine Heaven not found")
        return False

    def provide_unigine_instructions(self):
        """Provide instructions for downloading Unigine Heaven"""
        print("\n" + "="*70)
        print("UNIGINE HEAVEN BENCHMARK (Optional)")
        print("="*70)
        print("\nFor the most accurate FPS benchmarks, download Unigine Heaven:")
        print("\n  1. Visit: https://benchmark.unigine.com/heaven")
        print("  2. Download 'Heaven Benchmark 4.0' for Linux")
        print("  3. Extract and run the installer")
        print("  4. Or extract to: ~/Unigine_Heaven-4.0/")
        print("\nWithout Unigine, we'll use synthetic GPU stress testing (less accurate).")

    def check_all(self):
        """Check all dependencies"""
        print("\n" + "="*70)
        print("CHECKING DEPENDENCIES")
        print("="*70)

        # Check Python packages
        print("\n[1/3] Checking Python packages...")
        python_ok = self.check_python_packages()

        # Check system tools
        print("\n[2/3] Checking system tools...")
        system_ok = self.check_system_tools()

        # Check Unigine Heaven
        print("\n[3/3] Checking Unigine Heaven...")
        heaven_ok = self.check_unigine_heaven()

        # Summary
        print("\n" + "="*70)
        print("DEPENDENCY CHECK SUMMARY")
        print("="*70)
        print(f"Python Packages: {'✓ OK' if python_ok else '✗ MISSING'}")
        print(f"System Tools:    {'✓ OK' if system_ok else '⚠ SOME MISSING'}")
        print(f"Unigine Heaven:  {'✓ OK' if heaven_ok else '⚠ NOT FOUND'}")

        # Install missing dependencies
        if not python_ok:
            if not self.install_python_packages():
                print("\n⚠ Warning: Some Python packages are missing.")
                print("   Benchmark may not function correctly.")
                return False

        if not system_ok:
            if not self.install_system_tools():
                print("\n⚠ Warning: Some system tools are missing.")
                print("   Benchmarks will use fallback methods.")

        if not heaven_ok:
            self.provide_unigine_instructions()

        print("\n" + "="*70)
        return True


def main():
    """Main entry point for standalone testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    checker = DependencyChecker()
    checker.check_all()


if __name__ == "__main__":
    main()
