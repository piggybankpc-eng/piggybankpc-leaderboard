#!/usr/bin/env python3
"""
GPU Price Management System
Loads, manages, and matches GPU prices from configuration file
"""

import logging
import re
from pathlib import Path
from typing import Optional, Dict, List


class GPUPriceManager:
    """Manages GPU pricing data for benchmark calculations"""

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.config_dir = self.base_dir / "config"
        self.config_dir.mkdir(exist_ok=True)
        self.price_file = self.config_dir / "gpu-prices.txt"
        self.logger = logging.getLogger("GPUPriceManager")
        self.prices = {}
        self.load_prices()

    def load_prices(self):
        """
        Load GPU prices from configuration file

        Returns:
            bool: True if loaded successfully
        """
        if not self.price_file.exists():
            self.logger.warning(f"Price file not found: {self.price_file}")
            self.create_default_price_file()
            return False

        try:
            with open(self.price_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue

                    # Parse format: GPU_MODEL = £PRICE
                    if '=' not in line:
                        self.logger.warning(f"Invalid format on line {line_num}: {line}")
                        continue

                    parts = line.split('=', 1)
                    if len(parts) != 2:
                        continue

                    gpu_model = parts[0].strip()
                    price_str = parts[1].strip()

                    # Extract price value (remove £ symbol)
                    price_match = re.search(r'£?(\d+(?:\.\d{2})?)', price_str)
                    if price_match:
                        price = float(price_match.group(1))
                        self.prices[gpu_model.lower()] = {
                            'display_name': gpu_model,
                            'price': price
                        }
                    else:
                        self.logger.warning(f"Could not parse price on line {line_num}: {line}")

            self.logger.info(f"Loaded {len(self.prices)} GPU prices from config")
            return True

        except Exception as e:
            self.logger.error(f"Error loading price file: {str(e)}")
            return False

    def create_default_price_file(self):
        """Create default GPU price configuration file"""
        default_content = """# GPU Price Configuration File
# Format: GPU_MODEL = £PRICE
# Add one GPU per line - prices will be used for price-per-performance calculations

GTX 1060 6GB = £68
GTX 1070 = £89
GTX 1070 Ti = £120
GTX 1080 Ti = £250
RTX 2080 Ti = £187
RTX 3060 12GB = £230
RTX 3090 = £600
Quadro K1200 4GB = £25
Radeon Pro WX 5100 8GB = £47
"""
        try:
            with open(self.price_file, 'w') as f:
                f.write(default_content)
            self.logger.info(f"Created default price file: {self.price_file}")
            self.load_prices()
        except Exception as e:
            self.logger.error(f"Failed to create default price file: {str(e)}")

    def find_gpu_price(self, gpu_model: str) -> Optional[float]:
        """
        Find price for GPU model using fuzzy matching

        Args:
            gpu_model: GPU model name from hardware detection

        Returns:
            float: Price if found, None otherwise
        """
        if not gpu_model:
            return None

        gpu_model_lower = gpu_model.lower()

        # Direct match
        if gpu_model_lower in self.prices:
            return self.prices[gpu_model_lower]['price']

        # Fuzzy matching - try to match key parts
        # Extract key identifiers like "1060", "1070 ti", "2080 ti", etc.
        patterns = [
            r'gtx\s*(\d{4}(?:\s*ti)?)',  # GTX series
            r'rtx\s*(\d{4}(?:\s*ti)?)',  # RTX series
            r'quadro\s*([a-z0-9]+)',     # Quadro series
            r'radeon\s*pro\s*([a-z0-9\s]+)',  # Radeon Pro
        ]

        for pattern in patterns:
            match = re.search(pattern, gpu_model_lower)
            if match:
                identifier = match.group(0)

                # Search through price list
                for price_key, price_data in self.prices.items():
                    if identifier in price_key:
                        self.logger.info(
                            f"Fuzzy matched '{gpu_model}' to '{price_data['display_name']}'"
                        )
                        return price_data['price']

        # No match found
        self.logger.warning(f"No price found for GPU: {gpu_model}")
        return None

    def add_gpu_price(self, gpu_model: str, price: float) -> bool:
        """
        Add new GPU price to configuration file

        Args:
            gpu_model: GPU model name
            price: Price in GBP

        Returns:
            bool: True if added successfully
        """
        try:
            # Add to in-memory dict
            self.prices[gpu_model.lower()] = {
                'display_name': gpu_model,
                'price': price
            }

            # Append to file
            with open(self.price_file, 'a') as f:
                f.write(f"{gpu_model} = £{price:.2f}\n")

            self.logger.info(f"Added GPU price: {gpu_model} = £{price:.2f}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add GPU price: {str(e)}")
            return False

    def update_gpu_price(self, gpu_model: str, new_price: float) -> bool:
        """
        Update existing GPU price in configuration file

        Args:
            gpu_model: GPU model name
            new_price: New price in GBP

        Returns:
            bool: True if updated successfully
        """
        try:
            # Read all lines
            with open(self.price_file, 'r') as f:
                lines = f.readlines()

            # Find and update the line
            updated = False
            for i, line in enumerate(lines):
                if gpu_model.lower() in line.lower() and '=' in line:
                    lines[i] = f"{gpu_model} = £{new_price:.2f}\n"
                    updated = True
                    break

            if updated:
                # Write back
                with open(self.price_file, 'w') as f:
                    f.writelines(lines)

                # Update in-memory dict
                self.prices[gpu_model.lower()] = {
                    'display_name': gpu_model,
                    'price': new_price
                }

                self.logger.info(f"Updated GPU price: {gpu_model} = £{new_price:.2f}")
                return True
            else:
                self.logger.warning(f"GPU not found in price list: {gpu_model}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to update GPU price: {str(e)}")
            return False

    def delete_gpu_price(self, gpu_model: str) -> bool:
        """
        Delete GPU price from configuration file

        Args:
            gpu_model: GPU model name

        Returns:
            bool: True if deleted successfully
        """
        try:
            # Read all lines
            with open(self.price_file, 'r') as f:
                lines = f.readlines()

            # Filter out the GPU
            new_lines = []
            deleted = False
            for line in lines:
                if gpu_model.lower() in line.lower() and '=' in line:
                    deleted = True
                    continue
                new_lines.append(line)

            if deleted:
                # Write back
                with open(self.price_file, 'w') as f:
                    f.writelines(new_lines)

                # Remove from in-memory dict
                if gpu_model.lower() in self.prices:
                    del self.prices[gpu_model.lower()]

                self.logger.info(f"Deleted GPU price: {gpu_model}")
                return True
            else:
                self.logger.warning(f"GPU not found in price list: {gpu_model}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to delete GPU price: {str(e)}")
            return False

    def list_all_prices(self) -> List[Dict[str, any]]:
        """
        Get list of all GPU prices

        Returns:
            list: List of GPU price dictionaries
        """
        return [
            {
                'model': data['display_name'],
                'price': data['price']
            }
            for data in self.prices.values()
        ]

    # Convenience aliases for benchmark_runner compatibility
    def get_price(self, gpu_model: str) -> Optional[float]:
        """Alias for find_gpu_price()"""
        return self.find_gpu_price(gpu_model)

    def get_all_prices(self) -> Dict[str, float]:
        """Get all prices as a simple dict"""
        return {
            data['display_name']: data['price']
            for data in self.prices.values()
        }

    def add_price(self, gpu_model: str, price: float) -> bool:
        """Alias for add_gpu_price()"""
        return self.add_gpu_price(gpu_model, price)

    def delete_price(self, gpu_model: str) -> bool:
        """Alias for delete_gpu_price()"""
        return self.delete_gpu_price(gpu_model)

    def get_price_interactive(self, gpu_model: str) -> float:
        """
        Get GPU price interactively - auto-detect or prompt user

        Args:
            gpu_model: Detected GPU model name

        Returns:
            float: GPU price
        """
        # Try to find price automatically
        auto_price = self.find_gpu_price(gpu_model)

        if auto_price:
            print(f"\n✓ GPU price found: {gpu_model} = £{auto_price:.2f}")
            response = input("Use this price? (y/n): ").strip().lower()

            if response == 'y':
                return auto_price

        # Manual input
        print(f"\nGPU detected: {gpu_model}")
        print("Please enter the price you paid for this GPU (or press Ctrl+C to skip):")

        while True:
            try:
                price_input = input("Price (£): ").strip()

                # Allow empty input to skip
                if not price_input:
                    print("Skipping price entry...")
                    return 0.0

                # Remove £ symbol if present
                price_input = price_input.replace('£', '').replace(',', '')
                price = float(price_input)

                if price < 0:
                    print("ERROR: Price cannot be negative")
                    continue

                if price == 0:
                    print("Using £0 as price (no cost)")
                    return 0.0

                # Ask if user wants to save this price
                save = input(f"Save {gpu_model} = £{price:.2f} to price list? (y/n): ").strip().lower()
                if save == 'y':
                    self.add_gpu_price(gpu_model, price)
                    print("✓ Price saved to configuration")

                return price

            except ValueError:
                print("ERROR: Invalid price format. Please enter a number (e.g., 68 or 68.50)")
            except KeyboardInterrupt:
                print("\n\nOperation cancelled by user - using £0 as price")
                return 0.0
            except EOFError:
                print("\n\nNo input detected - using £0 as price")
                return 0.0


if __name__ == "__main__":
    # Test GPU price manager
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = Path(__file__).parent.parent

    manager = GPUPriceManager(base_dir)

    print("\n" + "="*60)
    print("GPU PRICE MANAGER TEST")
    print("="*60)

    # List all prices
    all_prices = manager.list_all_prices()
    print(f"\nLoaded {len(all_prices)} GPU prices:")
    for gpu in all_prices:
        print(f"  {gpu['model']}: £{gpu['price']:.2f}")

    # Test fuzzy matching
    test_gpus = [
        "NVIDIA GeForce GTX 1060 6GB",
        "GeForce RTX 3090",
        "NVIDIA Quadro K1200"
    ]

    print("\n" + "-"*60)
    print("Testing fuzzy matching:")
    for gpu in test_gpus:
        price = manager.find_gpu_price(gpu)
        if price:
            print(f"  ✓ {gpu}: £{price:.2f}")
        else:
            print(f"  ✗ {gpu}: No price found")

    print("\n" + "="*60)
