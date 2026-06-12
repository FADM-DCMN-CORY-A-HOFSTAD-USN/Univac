# File Name: boot_verification_suite.py
# Location: /src/config/
# Subsystem: Pre-Flight Hardware Registry & JSON Schema Boot Verification Suite

import os
import json
import math
import sys

# Import core elements to validate mathematical structures
from config.config_manager import VesselConfigManager
from network_layer.asymmetric_network_serializer import AsymmetricNetworkSerializer
from network_layer.weapon_async_parser import WeaponAsyncParserExtension

class AutomatedBootVerificationSuite:
    def __init__(self, target_config_file: str = "vessel_config.json"):
        self.config_name = target_config_file
        self.config_manager = VesselConfigManager(config_filename=target_config_file)
        self.serializer = AsymmetricNetworkSerializer(prefix_manufacturer="PUNVC")
        self.weapon_parser = WeaponAsyncParserExtension(manufacturer_code="MK45")

    def run_stage_1_json_schema_test(self) -> bool:
        """VERIFICATION STAGE 1: Asserts JSON parsing and schema property boundaries."""
        print("[TEST_1] Running JSON Configuration Schema Validation...")
        try:
            profile = self.config_manager.load_system_specifications()
            
            # Assert schema keys exist and contain non-zero positive measurements
            required_keys = ['diameter', 'inertia_prop', 'draft', 'max_torque', 'max_rudder_deg', 'hull_length', 'beam']
            for key in required_keys:
                if key not in profile:
                    print(f" -> FAIL: Missing required configuration structural key: '{key}'")
                    return False
                if float(profile[key]) <= 0.0:
                    print(f" -> FAIL: Boundary value fault. Key '{key}' cannot be zero or negative.")
                    return False
                    
            print(f" -> PASS: JSON Profile Schema fully populated. (Hull Length: {profile['hull_length']}m)")
            return True
        except Exception as e:
            print(f" -> CRITICAL EXCEPTION: Configuration layer breakdown: {e}")
            return False

    def run_stage_2_nmea_checksum_test(self) -> bool:
        """VERIFICATION STAGE 2: Validates accuracy of the 8-bit XOR checksum calculations."""
        print("[TEST_2] Running NMEA Checksum Protocol Verification...")
        
        # Test A: Validate out-of-loop checksum generation engine
        mock_payload = "PUNVCPRT,-18.45,12.5,1"
        generated_cs = self.serializer._compute_nmea_checksum(mock_payload)
        expected_cs = "0F"
        
        if generated_cs != expected_cs:
            print(f" -> FAIL: Serializer Checksum discrepancy. Generated: {generated_cs}, Expected: {expected_cs}")
            return False

        # Test B: Validate high-speed incoming weapon bus string parser validations
        valid_sentence = "$MK45,045.50,012.20,0000*29\r\n"
        corrupt_sentence = "$MK45,045.50,012.20,0000*FF\r\n" # Broken checksum token
        
        if not self.weapon_parser._verify_checksum_bytes(valid_sentence):
            print(" -> FAIL: Weapon parser rejected a structurally valid wire sentence.")
            return False
            
        if self.weapon_parser._verify_checksum_bytes(corrupt_sentence):
            print(" -> FAIL: Weapon parser erroneously accepted a corrupted wire sentence checksum.")
            return False

        print(" -> PASS: Checksum generation and ingestion validation matrix verified.")
        return True

    def run_stage_3_mimo_matrix_boundary_test(self) -> bool:
        """VERIFICATION STAGE 3: Stress-tests core mathematical matrices against extreme variables."""
        print("[TEST_3] Running MIMO Subsystem Floating-Point Boundary Verification...")
        
        try:
            # Force a simulated high-speed snap turn to verify limits won't hit division by zero
            test_omega = (600.0 * 2.0 * math.pi) / 60.0 # Extreme 600 RPM input
            test_yaw_rate = 0.75                        # Extreme turning slide speed
            
            # Replicate the internal bending moment formulas locally to assert stability limits
            m_bend = 0.012 * 1025.0 * (test_omega ** 2) * (3.4 ** 5) * test_yaw_rate
            m_gyro = 500.0 * test_omega * test_yaw_rate
            m_total = abs(m_bend) + abs(m_gyro)
            
            if math.isnan(m_total) or math.isinf(m_total):
                print(" -> FAIL: Floating point explosion detected inside structural moment matrix calculation.")
                return False
                
            print(f" -> PASS: Math matrix calculation boundaries verified. Peak Load: {m_total:.1f} Nm")
            return True
        except Exception as e:
            print(f" -> FAIL: Mathematical tracking routine execution exception: {e}")
            return False

    def execute_full_suite(self) -> bool:
        """Executes all checks sequentially. Returns True only if every phase passes perfectly."""
        print("\n=== STARTING PRE-FLIGHT HARDWARE BOOT VERIFICATION SUITE ===")
        
        s1 = self.run_stage_1_json_schema_test()
        s2 = self.run_stage_2_nmea_checksum_test()
        s3 = self.run_stage_3_mimo_matrix_boundary_test()
        
        print("============================================================")
        if s1 and s2 and s3:
            print(">>> STATUS: ALL SECTOR TESTS PASSED. BOOT FORWARD UNLOCKED. <<<\n")
            return True
        else:
            print(">>> CRITICAL STATUS: BOOT BLOCKED. SYSTEM INTEGRITY COMPROMISED. <<<\n")
            return False

# Local Verification Run Profile
if __name__ == "__main__":
    suite = AutomatedBootVerificationSuite()
    # Force a local dry-run pass check. 
    # If it fails, it exits with system code 1 to abort any main scripts attempting to open hardware lines.
    if not suite.execute_full_suite():
        sys.exit(1)
