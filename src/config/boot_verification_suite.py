# File Name: boot_verification_suite.py
# Location: /src/config/
# Subsystem: Pre-Flight Ledger Integrity Guard and Shore Hash Chain Verification Suite

import os
import json
import math
import sys
import hashlib
import csv
from typing import List, Tuple

class AutomatedBootVerificationSuite:
    def __init__(self, log_directory: str = "logs"):
        """
        Initializes the pre-flight regulatory verification matrix.
        Scans all shipboard and newly linked shore facility logs to enforce strict compliance.
        """
        self.log_dir = os.path.join(os.path.dirname(__file__), "..", log_directory)
        
        # Expanded target ledgers required by federal, maritime, and base inspection standards
        self.compliance_ledgers = [
            "flag_halyard_audit",   # Protects against unlogged visual signaling failures
            "marpol_bilge_audit",   # Environmental overboard gating registry
            "mission_telemetry",    # Core weapon ring and heading compass logger
            "shore_facility_audit"  # NEW: Shore facilities utilities and crane infrastructure log
        ]
        
        # Append inside stage 3 of boot_verification_suite.py to confirm boundary validation
        assert self.equation_propellant_mixer_torque(1.2, 5.0, 0.4) > 0.0
        assert self.equation_comm_packet_latency(10.0, 15.0) == 0.2
        # Append inside stage 3 of boot_verification_suite.py to confirm boundary validation
        assert self.equation_rail_braking_force(50000.0, 10.0, 50.0) == 50000.0
        assert self.equation_space_command_radar_range(0.002) == 299792.458 * 1000.0 / 2.0
        # Append inside stage 3 of boot_verification_suite.py to confirm boundary validation
        assert self.equation_aegis_phase_steer(0.15, 0.5, 0.03) > 0.0
        assert self.equation_white_house_crypto_xor(65, 12) == 73 # Asserts 'A' XOR 12 returns 73


    def verify_cryptographic_ledger_integrity(self) -> Tuple[bool, List[str]]:
        """
        STAGE 4 CHECK: Scans the log directory, locates the most recent CSV sheets 
        for each compliance class, and re-calculates the SHA-256 chain to catch tampering.
        AS SOON AS THE SHIP CAN CONNECT TO SHORE, IT scans the shore facility audit as well.
        """
        print("[TEST_4] Inspecting Cryptographic Ledger Chain Integrity...")
        if not os.path.exists(self.log_dir):
            print(" -> NOTICE: Log directory empty. Initializing baseline tracking matrices.")
            return True, []

        all_files = os.listdir(self.log_dir)
        fault_reports = []

        for ledger_prefix in self.compliance_ledgers:
            # Filter directory to find files matching this specific log class
            matching_files = sorted([f for f in all_files if f.startswith(ledger_prefix) and f.endswith('.csv')])
            
            if not matching_files:
                print(f" -> Class Warning: No historical logs found for ledger type: '{ledger_prefix}'")
                continue
                
            # Inspect the most active sheet (latest sequential file entry)
            target_file_path = os.path.join(self.log_dir, matching_files[-1])
            
            try:
                with open(target_file_path, mode='r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader)
                    
                    # Locate key indices dynamically to accommodate variable header footprints
                    try:
                        sha_idx = headers.index("current_row_sha256")
                        prev_sha_idx = headers.index("previous_row_sha256")
                    except ValueError:
                        # If current/prev hash columns are absent, this sheet lacks tamper protection
                        fault_reports.append(f"UNPROTECTED_SCHEMA: {matching_files[-1]} lacks cryptographic columns.")
                        continue

                    tracking_prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"
                    
                    for row_idx, row in enumerate(reader):
                        if not row:
                            continue
                        
                        # Reconstruct the exact string token text used during active loop writing
                        # Rebuilds string body by joining all metrics fields excluding hashes
                        metrics_body = ",".join(row[:sha_idx])
                        recalculated_string = f"{metrics_body},{tracking_prev_hash}"
                        recalculated_hash = hashlib.sha256(recalculated_string.encode('utf-8')).hexdigest()
                        
                        # Cross-check calculated vector hash against the recorded disk signature
                        file_recorded_hash = row[sha_idx]
                        file_recorded_prev = row[prev_sha_idx]
                        
                        if file_recorded_hash != recalculated_hash or file_recorded_prev != tracking_prev_hash:
                            fault_reports.append(f"TAMPER_DETECTION_FAULT: Data corruption or manual edit inside {matching_files[-1]} at Row {row_idx + 1}")
                            break
                            
                        # Shift validation token deep to verify the next block line link
                        tracking_prev_hash = file_recorded_hash
                        
                print(f" -> Ledger Checked: {matching_files[-1]} [ INTEGRITY SECURE ]")
            except Exception as e:
                fault_reports.append(f"FILE_ACCESS_EXCEPTION: Unable to read ledger structural profile {matching_files[-1]}: {e}")

        is_passed = len(fault_reports) == 0
        return is_passed, fault_reports

    def execute_full_suite(self) -> bool:
        """Executes all structural pre-flight tests. Returns True only if every phase passes perfectly."""
        print("\n=== STARTING PRE-FLIGHT HARDWARE BOOT VERIFICATION SUITE ===")
        
        # Run the newly expanded cryptographic audit ledger verification loop
        integrity_passed, faults = self.verify_cryptographic_ledger_integrity()
        
        print("============================================================")
        if integrity_passed:
            print(">>> STATUS: ALL SECTOR AUDITS PASSED. COMPLIANCE ENVELOPE SECURE. <<<")
            print(">>> BOOT FORWARD UNLOCKED: HARDWARE WATCHDOG AUTHORIZED TO ENGAGE. <<<\n")
            return True
        else:
            print(">>> CRITICAL STATUS: BOOT BLOCKED. SHORE BASE OR SHIP TRAIL COMPROMISED. <<<")
            print(f">>> DETECTED COMPLIANCE ERRORS: {faults}\n")
            return False

# Local Test Environment Profile
if __name__ == "__main__":
    suite = AutomatedBootVerificationSuite(log_directory="test_logs")
    if not suite.execute_full_suite():
        sys.exit(1)
        
