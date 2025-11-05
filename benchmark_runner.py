#!/usr/bin/env python3
"""
Benchmark Suite Main Runner
Orchestrates all benchmarks and manages the menu system
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import json

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from hardware_detection import HardwareDetector
from gpu_price_manager import GPUPriceManager
from fps_benchmark import FPSBenchmark
from ai_benchmark import AIBenchmark
from cpu_benchmark import CPUBenchmark
from dependency_checker import DependencyChecker


class BenchmarkSuite:
    """Main benchmark suite orchestrator"""
    
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = Path(__file__).parent

        self.base_dir = Path(base_dir)

        # Use user's home directory for results (AppImage-safe)
        home_dir = Path.home()
        self.results_dir = home_dir / "PiggyBankPC" / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging in user's home directory
        log_dir = home_dir / "PiggyBankPC" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("BenchmarkSuite")
        
        # Initialize components (use home directory for AppImage compatibility)
        writable_dir = home_dir / "PiggyBankPC"
        self.hardware_detector = HardwareDetector(writable_dir)
        self.price_manager = GPUPriceManager(writable_dir)

        # Always enable interactive mode for FPS benchmark
        # Heaven launches a GUI and doesn't need stdin interaction
        # User interacts with Heaven GUI directly, not via terminal prompts
        interactive = True

        self.fps_benchmark = FPSBenchmark(writable_dir, self.hardware_detector, interactive=interactive)
        self.ai_benchmark = AIBenchmark(writable_dir, self.hardware_detector)
        self.cpu_benchmark = CPUBenchmark(writable_dir, self.hardware_detector)
        
        self.all_results = {}
        
    def display_header(self):
        """Display suite header"""
        print("\n" + "="*70)
        print("     PIGGY BANK PC - BENCHMARK SUITE v1.0")
        print("     GPU Performance Testing for YouTube Content")
        print("="*70 + "\n")
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*70)
        print("MAIN MENU")
        print("="*70)
        print("1. Quick Benchmark (FPS only - ~15 minutes)")
        print("2. Full Suite (FPS + AI + CPU - ~90 minutes)")
        print("3. Custom Tests (select individual benchmarks)")
        print("4. View Previous Results")
        print("5. Manage GPU Prices")
        print("6. View System Information")
        print("7. Exit")
        print("="*70)
        
    def detect_system(self):
        """Detect and display system information"""
        print("\n" + "="*70)
        print("DETECTING SYSTEM HARDWARE...")
        print("="*70)
        
        cpu_info = self.hardware_detector.detect_cpu()
        gpu_info = self.hardware_detector.detect_gpu()
        ram_info = self.hardware_detector.detect_ram()
        
        print("\n✓ CPU DETECTED:")
        for key, value in cpu_info.items():
            print(f"  {key}: {value}")
        
        print("\n✓ GPU DETECTED:")
        for key, value in gpu_info.items():
            print(f"  {key}: {value}")
        
        print("\n✓ RAM DETECTED:")
        for key, value in ram_info.items():
            print(f"  {key}: {value}")
        
        # Check GPU price (interactive - prompts if not found)
        gpu_model = gpu_info.get('model', 'Unknown')
        price = None

        # Only prompt for price if GPU was successfully detected
        if gpu_info.get('detected', False) and gpu_model != 'Unknown':
            try:
                price = self.price_manager.get_price_interactive(gpu_model)
            except Exception as e:
                self.logger.error(f"Error getting GPU price: {str(e)}")
                print(f"\n⚠ Error getting GPU price: {str(e)}")
                print("  Continuing without price data...")
                price = None
        else:
            print(f"\n⚠ GPU not detected or unknown")
            print("  Continuing without price data...")

        return {
            'cpu': cpu_info,
            'gpu': gpu_info,
            'ram': ram_info,
            'gpu_price': price if price else 0.0
        }
    
    def run_quick_benchmark(self):
        """Run quick benchmark (FPS only)"""
        print("\n" + "="*70)
        print("QUICK BENCHMARK - FPS ONLY")
        print("="*70)
        
        system_info = self.detect_system()
        
        print("\n" + "-"*70)
        print("Starting FPS Benchmark...")
        print("-"*70)
        
        fps_results = self.fps_benchmark.run_benchmark()
        self.all_results['fps'] = fps_results
        self.all_results['system_info'] = system_info
        
        self._display_results()
        self._export_results()
    
    def run_full_suite(self):
        """Run full benchmark suite"""
        print("\n" + "="*70)
        print("FULL BENCHMARK SUITE")
        print("="*70)
        
        system_info = self.detect_system()
        
        # FPS Benchmark
        print("\n" + "-"*70)
        print("1/3 - Running FPS Benchmark...")
        print("-"*70)
        fps_results = self.fps_benchmark.run_benchmark()
        self.all_results['fps'] = fps_results
        
        # AI Benchmark
        print("\n" + "-"*70)
        print("2/3 - Running AI Token Benchmark...")
        print("-"*70)
        ai_results = self.ai_benchmark.run_benchmark()
        self.all_results['ai'] = ai_results
        
        # CPU Benchmark
        print("\n" + "-"*70)
        print("3/3 - Running CPU Benchmark...")
        print("-"*70)
        cpu_results = self.cpu_benchmark.run_benchmark()
        self.all_results['cpu'] = cpu_results
        
        self.all_results['system_info'] = system_info
        
        self._display_results()
        self._export_results()
    
    def run_custom_benchmark(self):
        """Run custom selected benchmarks"""
        print("\n" + "="*70)
        print("CUSTOM BENCHMARK")
        print("="*70)
        
        system_info = self.detect_system()
        
        print("\nSelect benchmarks to run:")
        print("1. FPS Benchmark")
        print("2. AI Token Benchmark")
        print("3. CPU Benchmark")
        print("4. All of above")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            fps_results = self.fps_benchmark.run_benchmark()
            self.all_results['fps'] = fps_results
        elif choice == '2':
            ai_results = self.ai_benchmark.run_benchmark()
            self.all_results['ai'] = ai_results
        elif choice == '3':
            cpu_results = self.cpu_benchmark.run_benchmark()
            self.all_results['cpu'] = cpu_results
        elif choice == '4':
            fps_results = self.fps_benchmark.run_benchmark()
            self.all_results['fps'] = fps_results
            ai_results = self.ai_benchmark.run_benchmark()
            self.all_results['ai'] = ai_results
            cpu_results = self.cpu_benchmark.run_benchmark()
            self.all_results['cpu'] = cpu_results
        
        self.all_results['system_info'] = system_info
        self._display_results()
        self._export_results()
    
    def view_previous_results(self):
        """View previous benchmark results"""
        print("\n" + "="*70)
        print("PREVIOUS RESULTS")
        print("="*70)
        
        result_files = sorted(self.results_dir.glob("benchmark_*.json"), reverse=True)
        
        if not result_files:
            print("\nNo previous results found.")
            return
        
        print("\nAvailable results:")
        for i, file in enumerate(result_files[:10], 1):
            print(f"{i}. {file.name}")
        
        choice = input("\nEnter file number to view (or press Enter to skip): ").strip()
        
        if choice.isdigit() and 0 < int(choice) <= len(result_files):
            file = result_files[int(choice) - 1]
            with open(file, 'r') as f:
                results = json.load(f)
            self._display_json_results(results)
    
    def manage_gpu_prices(self):
        """Manage GPU price list"""
        print("\n" + "="*70)
        print("MANAGE GPU PRICES")
        print("="*70)
        
        while True:
            print("\n1. View GPU Price List")
            print("2. Add New GPU")
            print("3. Edit GPU Price")
            print("4. Delete GPU")
            print("5. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                prices = self.price_manager.get_all_prices()
                print("\nCurrent GPU Prices:")
                for gpu, price in sorted(prices.items()):
                    print(f"  {gpu}: £{price}")
            
            elif choice == '2':
                gpu = input("Enter GPU model: ").strip()
                price = input("Enter price (£): ").strip()
                try:
                    self.price_manager.add_price(gpu, float(price))
                    print(f"✓ Added {gpu}: £{price}")
                except ValueError:
                    print("Invalid price format")
            
            elif choice == '3':
                gpu = input("Enter GPU model to edit: ").strip()
                price = input("Enter new price (£): ").strip()
                try:
                    self.price_manager.add_price(gpu, float(price))
                    print(f"✓ Updated {gpu}: £{price}")
                except ValueError:
                    print("Invalid price format")
            
            elif choice == '4':
                gpu = input("Enter GPU model to delete: ").strip()
                self.price_manager.delete_price(gpu)
                print(f"✓ Deleted {gpu}")
            
            elif choice == '5':
                break
    
    def view_system_info(self):
        """View detailed system information"""
        print("\n" + "="*70)
        print("SYSTEM INFORMATION")
        print("="*70)
        self.detect_system()
    
    def _display_results(self):
        """Display benchmark results"""
        print("\n" + "="*70)
        print("BENCHMARK RESULTS")
        print("="*70)
        
        if 'fps' in self.all_results:
            print("\n✓ FPS BENCHMARK:")
            fps = self.all_results['fps']
            if fps.get('status') == 'completed':
                print(f"  Average FPS: {fps.get('average_fps', 'N/A')}")
                print(f"  Min FPS: {fps.get('min_fps', 'N/A')}")
                print(f"  Max FPS: {fps.get('max_fps', 'N/A')}")
                print(f"  GPU Load: {fps.get('gpu_load', 'N/A')}%")
            else:
                print(f"  Status: {fps.get('error', 'Unknown error')}")
        
        if 'ai' in self.all_results:
            print("\n✓ AI TOKEN BENCHMARK:")
            ai = self.all_results['ai']
            if ai.get('status') == 'completed':
                print(f"  Tokens/Second: {ai.get('tokens_per_second', 'N/A')}")
                print(f"  Total Tokens: {ai.get('total_tokens', 'N/A')}")
                print(f"  Model: {ai.get('model', 'N/A')}")
            else:
                print(f"  Status: {ai.get('error', 'Unknown error')}")
        
        if 'cpu' in self.all_results:
            print("\n✓ CPU BENCHMARK:")
            cpu = self.all_results['cpu']
            if cpu.get('status') == 'completed':
                if cpu.get('benchmark_type') == 'geekbench':
                    print(f"  Single-Core: {cpu.get('single_core_score', 'N/A')}")
                    print(f"  Multi-Core: {cpu.get('multi_core_score', 'N/A')}")
                else:
                    print(f"  Events/Sec: {cpu.get('events_per_second', 'N/A')}")
                    print(f"  Threads: {cpu.get('threads_used', 'N/A')}")
            else:
                print(f"  Status: {cpu.get('error', 'Unknown error')}")
        
        # Price calculations
        if 'system_info' in self.all_results and 'fps' in self.all_results:
            gpu_price = self.all_results['system_info'].get('gpu_price')
            fps = self.all_results['fps'].get('average_fps')
            
            if gpu_price and fps and fps != 'N/A':
                price_per_fps = gpu_price / fps
                print(f"\n💷 PRICE TO PERFORMANCE:")
                print(f"  GPU Price: £{gpu_price}")
                print(f"  Price per FPS: £{price_per_fps:.2f}")
        
        print("\n" + "="*70)
    
    def _display_json_results(self, results):
        """Display JSON results nicely"""
        print("\nResults:")
        print(json.dumps(results, indent=2))
    
    def _export_results(self):
        """Export results to CSV, JSON, and encrypted .pbr file"""
        from csv_exporter import CSVExporter
        from security import BenchmarkSecurity

        # Export CSV and JSON
        exporter = CSVExporter(self.base_dir)
        exporter.export(self.all_results)

        # Create encrypted .pbr file for leaderboard submission
        security = BenchmarkSecurity(
            base_dir=self.base_dir,
            signing_key='PIGGYBANK_PC_BENCHMARK_SECRET_2025'
        )

        # Sign the results first
        signed_package = security.sign_results(self.all_results)

        # Create submission file in home directory
        pbr_file = security.create_submission_file(signed_package, self.results_dir)

        if pbr_file:
            print("\n✓ Results exported to CSV, JSON, and encrypted .pbr")
            print(f"  Location: {self.results_dir}")
            print(f"\n🔒 ENCRYPTED .PBR FILE CREATED:")
            print(f"  {pbr_file}")
            print("\n📤 Upload this .pbr file to: https://piggybankpc.uk/submit")
        else:
            print("\n⚠ Warning: Failed to create encrypted .pbr file")
            print(f"  CSV/JSON files available in: {self.results_dir}")
    
    def run(self):
        """Main event loop"""
        self.display_header()

        # Check dependencies on first run
        print("\n⚙️  Checking dependencies...")
        dep_checker = DependencyChecker()
        dep_checker.check_all()

        input("\nPress Enter to continue to main menu...")

        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                self.run_quick_benchmark()
            elif choice == '2':
                self.run_full_suite()
            elif choice == '3':
                self.run_custom_benchmark()
            elif choice == '4':
                self.view_previous_results()
            elif choice == '5':
                self.manage_gpu_prices()
            elif choice == '6':
                self.view_system_info()
            elif choice == '7':
                print("\nThanks for using Piggy Bank PC Benchmark Suite!")
                print("Your results are saved in: " + str(self.results_dir))
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='PiggyBankPC Benchmark Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                   # Interactive mode
  %(prog)s --quick           # Quick benchmark (FPS only)
  %(prog)s --full            # Full suite (FPS + AI + CPU)
  %(prog)s --fps             # FPS benchmark only
  %(prog)s --ai              # AI benchmark only
  %(prog)s --cpu             # CPU benchmark only
        """
    )

    parser.add_argument('--quick', action='store_true',
                        help='Run quick benchmark (FPS only, ~15 min)')
    parser.add_argument('--full', action='store_true',
                        help='Run full benchmark suite (FPS + AI + CPU, ~90 min)')
    parser.add_argument('--fps', action='store_true',
                        help='Run FPS benchmark only')
    parser.add_argument('--ai', action='store_true',
                        help='Run AI token benchmark only')
    parser.add_argument('--cpu', action='store_true',
                        help='Run CPU benchmark only')
    parser.add_argument('--no-deps-check', action='store_true',
                        help='Skip dependency checking (assumes all tools installed)')

    args = parser.parse_args()

    suite = BenchmarkSuite()

    # Non-interactive mode - run specified benchmark and exit
    if args.quick or args.full or args.fps or args.ai or args.cpu:
        suite.display_header()

        # Check dependencies unless skipped
        if not args.no_deps_check:
            print("\n⚙️  Checking dependencies...")
            dep_checker = DependencyChecker()
            dep_checker.check_all()

        # Run the specified benchmark
        if args.quick:
            suite.run_quick_benchmark()
        elif args.full:
            suite.run_full_suite()
        elif args.fps:
            print("\n" + "="*70)
            print("FPS BENCHMARK ONLY")
            print("="*70)
            system_info = suite.detect_system()
            fps_results = suite.fps_benchmark.run_benchmark()
            suite.all_results['fps'] = fps_results
            suite.all_results['system_info'] = system_info
            suite._display_results()
            suite._export_results()
        elif args.ai:
            print("\n" + "="*70)
            print("AI BENCHMARK ONLY")
            print("="*70)
            system_info = suite.detect_system()
            ai_results = suite.ai_benchmark.run_benchmark()
            suite.all_results['ai'] = ai_results
            suite.all_results['system_info'] = system_info
            suite._display_results()
            suite._export_results()
        elif args.cpu:
            print("\n" + "="*70)
            print("CPU BENCHMARK ONLY")
            print("="*70)
            system_info = suite.detect_system()
            cpu_results = suite.cpu_benchmark.run_benchmark()
            suite.all_results['cpu'] = cpu_results
            suite.all_results['system_info'] = system_info
            suite._display_results()
            suite._export_results()

        print("\n✅ Benchmark complete!")
        print(f"📁 Results saved to: {suite.results_dir}")
        sys.exit(0)

    # Interactive mode
    suite.run()
