#!/usr/bin/env python3
"""
Overclock Analysis Module
Analyzes CPU and RAM overclocks and calculates performance uplift
"""

import subprocess
import re
import logging
from typing import Dict, Optional


class OverclockAnalyzer:
    """Analyzes CPU/RAM overclocks and calculates performance gains"""

    # Known CPU base specs (GHz)
    CPU_SPECS = {
        "i9-9900X": {"base": 3.5, "boost": 4.5, "cores": 10},
        "i9-9900K": {"base": 3.6, "boost": 5.0, "cores": 8},
        "i7-9700K": {"base": 3.6, "boost": 4.9, "cores": 8},
        "Ryzen 9 5950X": {"base": 3.4, "boost": 4.9, "cores": 16},
        "Ryzen 9 5900X": {"base": 3.7, "boost": 4.8, "cores": 12},
        "Ryzen 7 5800X": {"base": 3.8, "boost": 4.7, "cores": 8},
    }

    # DDR4 JEDEC standard speeds
    DDR4_JEDEC_SPEEDS = [2133, 2400, 2666, 2933, 3200]

    def __init__(self):
        self.logger = logging.getLogger("OverclockAnalyzer")

    def get_cpu_specs(self, cpu_model: str) -> Optional[Dict]:
        """
        Get stock CPU specifications

        Args:
            cpu_model: CPU model name

        Returns:
            dict: CPU specs or None
        """
        for key, specs in self.CPU_SPECS.items():
            if key in cpu_model:
                return specs
        return None

    def get_current_cpu_freq(self) -> Dict:
        """
        Get current CPU frequencies

        Returns:
            dict: Current min/max/avg frequencies
        """
        try:
            # Get current CPU frequencies
            result = subprocess.run(
                ["lscpu"],
                capture_output=True,
                text=True,
                timeout=5
            )

            output = result.stdout

            # Parse frequencies
            max_mhz_match = re.search(r'CPU max MHz:\s+([\d.]+)', output)
            min_mhz_match = re.search(r'CPU min MHz:\s+([\d.]+)', output)

            max_mhz = float(max_mhz_match.group(1)) if max_mhz_match else None
            min_mhz = float(min_mhz_match.group(1)) if min_mhz_match else None

            # Get actual running frequency
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()

            # Get all CPU MHz values
            freq_matches = re.findall(r'cpu MHz\s+:\s+([\d.]+)', cpuinfo)
            if freq_matches:
                freqs = [float(f) for f in freq_matches]
                avg_mhz = sum(freqs) / len(freqs)
            else:
                avg_mhz = None

            return {
                "min_mhz": min_mhz,
                "max_mhz": max_mhz,
                "avg_mhz": avg_mhz,
                "min_ghz": round(min_mhz / 1000, 2) if min_mhz else None,
                "max_ghz": round(max_mhz / 1000, 2) if max_mhz else None,
                "avg_ghz": round(avg_mhz / 1000, 2) if avg_mhz else None,
            }

        except Exception as e:
            self.logger.error(f"Failed to get CPU frequency: {e}")
            return {}

    def analyze_cpu_overclock(self, cpu_model: str, actual_freq: Dict) -> Dict:
        """
        Analyze CPU overclock

        Args:
            cpu_model: CPU model name
            actual_freq: Actual frequencies from get_current_cpu_freq()

        Returns:
            dict: Overclock analysis
        """
        specs = self.get_cpu_specs(cpu_model)
        if not specs or not actual_freq.get('max_ghz'):
            return {"overclocked": False}

        stock_base = specs['base']
        stock_boost = specs['boost']
        actual_max = actual_freq['max_ghz']

        # Calculate overclock percentages
        base_overclock = ((actual_max - stock_base) / stock_base) * 100
        boost_overclock = ((actual_max - stock_boost) / stock_boost) * 100

        return {
            "overclocked": actual_max > stock_boost,
            "stock_base_ghz": stock_base,
            "stock_boost_ghz": stock_boost,
            "actual_max_ghz": actual_max,
            "base_overclock_percent": round(base_overclock, 1),
            "boost_overclock_percent": round(boost_overclock, 1),
        }

    def get_ram_specs(self) -> Dict:
        """
        Get RAM specifications and calculate overclock

        Returns:
            dict: RAM specs and overclock info
        """
        try:
            result = subprocess.run(
                ["sudo", "dmidecode", "-t", "memory"],
                capture_output=True,
                text=True,
                timeout=10
            )

            output = result.stdout

            # Find configured speed
            speed_match = re.search(r'Configured Memory Speed:\s+(\d+)\s+MT/s', output)
            actual_speed = int(speed_match.group(1)) if speed_match else None

            if not actual_speed:
                return {"overclocked": False}

            # Find closest JEDEC standard
            jedec_speed = max([s for s in self.DDR4_JEDEC_SPEEDS if s <= actual_speed], default=2133)

            # Calculate overclock
            overclock_percent = ((actual_speed - jedec_speed) / jedec_speed) * 100

            return {
                "overclocked": actual_speed > jedec_speed,
                "jedec_standard_mhz": jedec_speed,
                "actual_speed_mhz": actual_speed,
                "overclock_percent": round(overclock_percent, 1),
            }

        except Exception as e:
            self.logger.error(f"Failed to get RAM specs: {e}")
            return {"overclocked": False}

    def estimate_stock_performance(self, actual_score: float, overclock_percent: float) -> Dict:
        """
        Estimate what stock performance would be based on overclock

        Args:
            actual_score: Actual benchmark score
            overclock_percent: Overclock percentage

        Returns:
            dict: Stock performance estimate
        """
        if overclock_percent <= 0:
            return {
                "estimated_stock_score": actual_score,
                "performance_gain_percent": 0
            }

        # Estimate stock performance (assuming linear scaling)
        stock_score = actual_score / (1 + (overclock_percent / 100))
        gain_percent = ((actual_score - stock_score) / stock_score) * 100

        return {
            "estimated_stock_score": round(stock_score, 2),
            "performance_gain_percent": round(gain_percent, 1),
            "actual_score": actual_score
        }


if __name__ == "__main__":
    # Test the analyzer
    logging.basicConfig(level=logging.INFO)

    analyzer = OverclockAnalyzer()

    print("\n" + "="*60)
    print("OVERCLOCK ANALYZER TEST")
    print("="*60)

    # Test CPU frequency
    freq = analyzer.get_current_cpu_freq()
    print(f"\nCurrent CPU Frequency:")
    print(f"  Min: {freq.get('min_ghz')} GHz")
    print(f"  Max: {freq.get('max_ghz')} GHz")
    print(f"  Avg: {freq.get('avg_ghz')} GHz")

    # Test CPU overclock analysis
    cpu_model = "Intel(R) Core(TM) i9-9900X CPU @ 3.50GHz"
    oc_analysis = analyzer.analyze_cpu_overclock(cpu_model, freq)
    if oc_analysis.get('overclocked'):
        print(f"\n✓ CPU IS OVERCLOCKED!")
        print(f"  Stock Boost: {oc_analysis['stock_boost_ghz']} GHz")
        print(f"  Actual Max: {oc_analysis['actual_max_ghz']} GHz")
        print(f"  Overclock: +{oc_analysis['boost_overclock_percent']}%")

    # Test RAM
    ram_specs = analyzer.get_ram_specs()
    if ram_specs.get('overclocked'):
        print(f"\n✓ RAM IS OVERCLOCKED!")
        print(f"  JEDEC Standard: {ram_specs['jedec_standard_mhz']} MHz")
        print(f"  Actual Speed: {ram_specs['actual_speed_mhz']} MHz")
        print(f"  Overclock: +{ram_specs['overclock_percent']}%")

    print("\n" + "="*60)
