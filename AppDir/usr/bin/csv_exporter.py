#!/usr/bin/env python3
"""
CSV Exporter for Benchmark Results
Exports benchmark data with price calculations to CSV format
"""

import csv
import json
import logging
from pathlib import Path
from datetime import datetime


class CSVExporter:
    """Exports benchmark results to CSV format"""

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        # Use home directory for AppImage compatibility
        home_dir = Path.home()
        self.results_dir = home_dir / "PiggyBankPC" / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("CSVExporter")
    
    def export(self, results):
        """
        Export benchmark results to CSV
        
        Args:
            results: Dictionary containing all benchmark results
        """
        if not results:
            self.logger.error("No results to export")
            return
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = self.results_dir / f"benchmark_results_{timestamp}.csv"
        
        try:
            # Prepare data
            data = self._prepare_data(results)
            
            # Write CSV
            with open(csv_filename, 'w', newline='') as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            
            self.logger.info(f"CSV exported to: {csv_filename}")
            print(f"\n✓ CSV Export: {csv_filename}")
            
            # Also save as master results JSON
            self._save_json_results(results, timestamp)
            
        except Exception as e:
            self.logger.error(f"Failed to export CSV: {str(e)}")
            print(f"❌ Export failed: {str(e)}")
    
    def _prepare_data(self, results):
        """
        Prepare data for CSV export
        
        Args:
            results: Raw benchmark results
            
        Returns:
            list: List of dictionaries ready for CSV
        """
        data = []
        
        try:
            system_info = results.get('system_info', {})
            cpu_info = system_info.get('cpu', {})
            gpu_info = system_info.get('gpu', {})
            gpu_price = system_info.get('gpu_price', 'N/A')
            
            # Base row with system info
            row = {
                'Test_Date': datetime.now().strftime('%Y-%m-%d'),
                'Test_Time': datetime.now().strftime('%H:%M:%S'),
                'CPU_Model': cpu_info.get('model', 'Unknown'),
                'CPU_Cores': cpu_info.get('cores', 'Unknown'),
                'GPU_Model': gpu_info.get('model', 'Unknown'),
                'GPU_VRAM': gpu_info.get('vram', 'Unknown'),
                'GPU_Price_£': gpu_price if gpu_price != 'N/A' else '',
            }
            
            # FPS Results
            fps_data = results.get('fps', {})
            if fps_data.get('status') == 'completed':
                fps_avg = fps_data.get('average_fps', 'N/A')
                row['FPS_Average'] = fps_avg
                row['FPS_Min'] = fps_data.get('min_fps', 'N/A')
                row['FPS_Max'] = fps_data.get('max_fps', 'N/A')
                row['GPU_Load_%'] = fps_data.get('gpu_load', 'N/A')
                
                # Calculate price per FPS
                if gpu_price != 'N/A' and fps_avg != 'N/A':
                    try:
                        price_per_fps = float(gpu_price) / float(fps_avg)
                        row['Price_Per_FPS_£'] = f"{price_per_fps:.4f}"
                    except (ValueError, ZeroDivisionError):
                        row['Price_Per_FPS_£'] = 'N/A'
                else:
                    row['Price_Per_FPS_£'] = 'N/A'
            else:
                row['FPS_Average'] = 'ERROR'
                row['FPS_Min'] = fps_data.get('error', 'Unknown')
                row['FPS_Max'] = ''
                row['GPU_Load_%'] = ''
                row['Price_Per_FPS_£'] = ''
            
            # AI Results
            ai_data = results.get('ai', {})
            if ai_data.get('status') == 'completed':
                tokens_per_sec = ai_data.get('tokens_per_second', 'N/A')
                row['Tokens_Per_Sec'] = tokens_per_sec
                row['AI_Model'] = ai_data.get('model', 'N/A')
                
                # Calculate price per token
                if gpu_price != 'N/A' and tokens_per_sec != 'N/A':
                    try:
                        price_per_token = float(gpu_price) / float(tokens_per_sec)
                        row['Price_Per_Token_£'] = f"{price_per_token:.4f}"
                    except (ValueError, ZeroDivisionError):
                        row['Price_Per_Token_£'] = 'N/A'
                else:
                    row['Price_Per_Token_£'] = 'N/A'
            else:
                row['Tokens_Per_Sec'] = 'ERROR'
                row['AI_Model'] = ai_data.get('error', 'Unknown')
                row['Price_Per_Token_£'] = ''
            
            # CPU Results
            cpu_data = results.get('cpu', {})
            if cpu_data.get('status') == 'completed':
                if cpu_data.get('benchmark_type') == 'geekbench':
                    row['CPU_Single_Core'] = cpu_data.get('single_core_score', 'N/A')
                    row['CPU_Multi_Core'] = cpu_data.get('multi_core_score', 'N/A')
                    row['CPU_Benchmark_Type'] = 'Geekbench'
                else:
                    row['CPU_Single_Core'] = ''
                    row['CPU_Multi_Core'] = cpu_data.get('events_per_second', 'N/A')
                    row['CPU_Benchmark_Type'] = 'Sysbench'
            else:
                row['CPU_Single_Core'] = 'ERROR'
                row['CPU_Multi_Core'] = cpu_data.get('error', 'Unknown')
                row['CPU_Benchmark_Type'] = ''
            
            data.append(row)
            
        except Exception as e:
            self.logger.error(f"Error preparing CSV data: {str(e)}")
        
        return data
    
    def _save_json_results(self, results, timestamp):
        """
        Save complete results as JSON
        
        Args:
            results: Results dictionary
            timestamp: Timestamp string
        """
        try:
            json_filename = self.results_dir / f"benchmark_results_{timestamp}.json"
            
            with open(json_filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.logger.info(f"JSON exported to: {json_filename}")
            print(f"✓ JSON Export: {json_filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to save JSON: {str(e)}")


if __name__ == "__main__":
    # Test the exporter
    logging.basicConfig(level=logging.INFO)
    
    test_results = {
        'system_info': {
            'cpu': {'model': 'Intel i9-9900X', 'cores': '10'},
            'gpu': {'model': 'GTX 1060 6GB', 'vram': '6GB'},
            'gpu_price': 68
        },
        'fps': {
            'status': 'completed',
            'average_fps': 85.5,
            'min_fps': 75.2,
            'max_fps': 95.1,
            'gpu_load': 95
        },
        'ai': {
            'status': 'completed',
            'tokens_per_second': 45.3,
            'model': 'llama2:7b'
        },
        'cpu': {
            'status': 'completed',
            'benchmark_type': 'sysbench',
            'events_per_second': 1234.56
        }
    }
    
    exporter = CSVExporter(Path(__file__).parent)
    exporter.export(test_results)
