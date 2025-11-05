#!/usr/bin/env python3
"""
PiggyBankPC Benchmark Security Module
Handles result signing, hardware fingerprinting, and tamper protection
"""

import hashlib
import hmac
import json
import uuid
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import base64


class BenchmarkSecurity:
    """Handles security and anti-tampering for benchmark results"""

    VERSION = "1.0.0"

    def __init__(self, base_dir, signing_key=None):
        self.base_dir = Path(base_dir)
        self.logger = logging.getLogger("BenchmarkSecurity")

        # This is your secret signing key - keep this safe!
        # In production, store this securely on your server, not in the code
        self.signing_key = signing_key or "PIGGYBANK_PC_BENCHMARK_SECRET_2025"

    def generate_hardware_fingerprint(self) -> str:
        """
        Generate unique hardware fingerprint for this system
        Makes it harder to fake results from different hardware

        Returns:
            str: Unique hardware fingerprint hash
        """
        fingerprint_data = []

        try:
            # CPU ID from /proc/cpuinfo
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line or 'vendor_id' in line:
                        fingerprint_data.append(line.strip())

            # Motherboard info
            try:
                result = subprocess.run(
                    ['sudo', 'dmidecode', '-t', 'baseboard'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'Serial Number' in line or 'UUID' in line:
                            fingerprint_data.append(line.strip())
            except:
                pass

            # Machine ID
            machine_id_file = Path('/etc/machine-id')
            if machine_id_file.exists():
                fingerprint_data.append(machine_id_file.read_text().strip())

            # GPU UUID
            try:
                result = subprocess.run(
                    ['nvidia-smi', '--query-gpu=uuid', '--format=csv,noheader'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    fingerprint_data.append(result.stdout.strip())
            except:
                pass

            # Combine all fingerprint data
            combined = "|".join(fingerprint_data)

            # Hash it
            fingerprint_hash = hashlib.sha256(combined.encode()).hexdigest()

            self.logger.info(f"Generated hardware fingerprint: {fingerprint_hash[:16]}...")
            return fingerprint_hash

        except Exception as e:
            self.logger.error(f"Failed to generate hardware fingerprint: {str(e)}")
            # Fallback to random UUID if fingerprinting fails
            return str(uuid.uuid4())

    def sign_results(self, results: Dict) -> Dict:
        """
        Sign benchmark results with HMAC to prevent tampering

        Args:
            results: Raw benchmark results dictionary

        Returns:
            dict: Signed results package with metadata
        """
        try:
            # Add metadata
            timestamp = datetime.now().isoformat()
            hardware_fp = self.generate_hardware_fingerprint()

            # Create the data package
            data_package = {
                'version': self.VERSION,
                'timestamp': timestamp,
                'hardware_fingerprint': hardware_fp,
                'results': results
            }

            # Convert to canonical JSON (sorted keys for consistent hashing)
            canonical_json = json.dumps(data_package, sort_keys=True)

            # Generate HMAC signature
            signature = hmac.new(
                self.signing_key.encode(),
                canonical_json.encode(),
                hashlib.sha256
            ).hexdigest()

            # Create final signed package
            signed_package = {
                'data': data_package,
                'signature': signature,
                'signature_algorithm': 'HMAC-SHA256'
            }

            self.logger.info("Results signed successfully")
            return signed_package

        except Exception as e:
            self.logger.error(f"Failed to sign results: {str(e)}")
            raise

    def verify_signature(self, signed_package: Dict) -> bool:
        """
        Verify that signed results haven't been tampered with

        Args:
            signed_package: Signed results package

        Returns:
            bool: True if signature is valid
        """
        try:
            data = signed_package.get('data')
            provided_signature = signed_package.get('signature')

            if not data or not provided_signature:
                self.logger.error("Missing data or signature")
                return False

            # Recreate the canonical JSON
            canonical_json = json.dumps(data, sort_keys=True)

            # Calculate expected signature
            expected_signature = hmac.new(
                self.signing_key.encode(),
                canonical_json.encode(),
                hashlib.sha256
            ).hexdigest()

            # Constant-time comparison to prevent timing attacks
            is_valid = hmac.compare_digest(expected_signature, provided_signature)

            if is_valid:
                self.logger.info("Signature verification PASSED")
            else:
                self.logger.warning("Signature verification FAILED")

            return is_valid

        except Exception as e:
            self.logger.error(f"Signature verification error: {str(e)}")
            return False

    def encode_for_submission(self, signed_package: Dict) -> str:
        """
        Encode signed package for submission (base64)
        Makes it harder to manually edit

        Args:
            signed_package: Signed results package

        Returns:
            str: Base64 encoded submission string
        """
        try:
            json_string = json.dumps(signed_package)
            encoded = base64.b64encode(json_string.encode()).decode()

            self.logger.info("Results encoded for submission")
            return encoded

        except Exception as e:
            self.logger.error(f"Failed to encode results: {str(e)}")
            raise

    def decode_submission(self, encoded_string: str) -> Dict:
        """
        Decode and verify submitted results

        Args:
            encoded_string: Base64 encoded submission

        Returns:
            dict: Decoded and verified results, or None if invalid
        """
        try:
            # Decode from base64
            json_string = base64.b64decode(encoded_string.encode()).decode()
            signed_package = json.loads(json_string)

            # Verify signature
            if not self.verify_signature(signed_package):
                self.logger.error("Submission verification FAILED - signature invalid")
                return None

            self.logger.info("Submission decoded and verified successfully")
            return signed_package['data']

        except Exception as e:
            self.logger.error(f"Failed to decode submission: {str(e)}")
            return None

    def create_submission_file(self, signed_package: Dict, output_dir: Path) -> Path:
        """
        Create encrypted submission file for user to upload

        Args:
            signed_package: Signed results package
            output_dir: Directory to save submission file

        Returns:
            Path: Path to submission file
        """
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True, parents=True)

            # Encode the package
            encoded = self.encode_for_submission(signed_package)

            # Create filename with timestamp and hardware fingerprint
            hardware_fp = signed_package['data']['hardware_fingerprint']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"piggybank_benchmark_{timestamp}_{hardware_fp[:8]}.pbr"

            filepath = output_dir / filename

            # Write submission file
            with open(filepath, 'w') as f:
                f.write("# PiggyBankPC Benchmark Results\n")
                f.write("# DO NOT EDIT THIS FILE\n")
                f.write("# Upload this file to: https://piggybankpc.com/submit\n")
                f.write(f"# Version: {self.VERSION}\n")
                f.write(f"# Timestamp: {timestamp}\n")
                f.write("#\n")
                f.write(encoded)

            self.logger.info(f"Submission file created: {filepath}")
            print(f"\n{'='*70}")
            print(f"✓ SUBMISSION FILE CREATED")
            print(f"{'='*70}")
            print(f"File: {filepath}")
            print(f"\nUpload this file to the PiggyBankPC leaderboard:")
            print(f"https://piggybankpc.com/submit")
            print(f"\n{'='*70}")

            return filepath

        except Exception as e:
            self.logger.error(f"Failed to create submission file: {str(e)}")
            raise

    def validate_submission_file(self, filepath: Path) -> Optional[Dict]:
        """
        Validate a submission file

        Args:
            filepath: Path to submission file

        Returns:
            dict: Validated results or None if invalid
        """
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()

            # Find the encoded data (skip comment lines)
            encoded_data = None
            for line in lines:
                if not line.startswith('#') and line.strip():
                    encoded_data = line.strip()
                    break

            if not encoded_data:
                self.logger.error("No data found in submission file")
                return None

            # Decode and verify
            results = self.decode_submission(encoded_data)

            if results:
                print(f"\n✓ Submission file is VALID")
                print(f"  Version: {results.get('version')}")
                print(f"  Timestamp: {results.get('timestamp')}")
                print(f"  Hardware: {results.get('hardware_fingerprint', '')[:16]}...")
            else:
                print(f"\n✗ Submission file is INVALID or TAMPERED")

            return results

        except Exception as e:
            self.logger.error(f"Failed to validate submission file: {str(e)}")
            return None

    def validate_submission_content(self, file_content: str) -> Optional[Dict]:
        """
        Validate submission file content (for web uploads)

        Args:
            file_content: Content of the .pbr file as string

        Returns:
            dict: Validated results or None if invalid
        """
        try:
            lines = file_content.strip().split('\n')

            # Find the encoded data (skip comment lines)
            encoded_data = None
            for line in lines:
                if not line.startswith('#') and line.strip():
                    encoded_data = line.strip()
                    break

            if not encoded_data:
                self.logger.error("No data found in submission file")
                return None

            # Decode and verify
            results = self.decode_submission(encoded_data)

            if results:
                self.logger.info("Submission file is VALID")
            else:
                self.logger.warning("Submission file is INVALID or TAMPERED")

            return results

        except Exception as e:
            self.logger.error(f"Failed to validate submission content: {str(e)}")
            return None
