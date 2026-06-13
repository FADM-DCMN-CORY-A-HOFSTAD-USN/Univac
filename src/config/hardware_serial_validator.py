# File Name: hardware_serial_validator.py
# Location: /src/config/
# Subsystem: Pre-Sail Physical Layer Loopback & RS-422 Serial Integrity Stress-Tester

import os
import json
import time
import threading
import serial # Requires: pip install pyserial
from typing import Dict, Any, List

class HardwareSerialValidationEngine:
    def __init__(self, manifest_filename: str = "manifest.json"):
        """Initializes the physical layer diagnostic suite by reading frozen manifest boundaries."""
        self.config_dir = os.path.dirname(__file__)
        self.manifest_path = os.path.join(self.config_dir, manifest_filename)
        self.ports_to_test = self._load_frozen_ports_from_manifest()
        
        self.lock = threading.Lock()
        self.validation_results = {}
        self.test_active = False

    def _load_frozen_ports_from_manifest(self) -> dict:
        """Dynamically ingests frozen port assignments from manifest.json to preserve strict hardware maps."""
        if not os.path.exists(self.manifest_path):
            print(f"[VALIDATOR_WARN] Manifest file missing at {self.manifest_path}. Deploying fallback test matrix.")
            return {
                "COM3": {"baud": 4800, "id": "COMPASS_FALLBACK"},
                "COM4": {"baud": 4800, "id": "DEPTH_FALLBACK"}
            }
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                serial_map = data.get("hardware_abstraction_layer", {}).get("serial_ports", {})
                
                extracted_ports = {}
                for key, config in serial_map.items():
                    # Pick the appropriate handle footprint depending on target OS environment
                    port_handle = config["windows_handle"] if os.name == 'nt' else config["linux_handle"]
                    extracted_ports[port_handle] = {
                        "baud": int(config["baud_rate"]),
                        "id": config["protocol_standard"].split()[0] # Capture string prefix identifier
                    }
                return extracted_ports
        except Exception as e:
            print(f"[VALIDATOR_CRITICAL] Unable to parse master manifest configuration profiles: {e}")
            return {}

    def _compute_8bit_xor_checksum(self, text_body: str) -> str:
        """Computes reference NMEA validation bytes to stress-test data parity loops."""
        checksum = 0
        for char in text_body:
            checksum ^= ord(char)
        return f"{checksum:02X}"

    def _stress_test_isolated_port(self, port_handle: str, config: dict, frame_count: int = 50):
        """Thread-isolated loopback worker function handling byte transmission and frame audit steps."""
        print(f"[VALIDATOR] Initiating loopback checks on target {port_handle} at {config['baud']} Baud...")
        
        # Initialize isolated result tracking dictionary for this specific port
        results = {
            "interface_id": config["id"],
            "frames_transmitted": 0,
            "frames_received": 0,
            "checksum_failures": 0,
            "line_timeouts": 0,
            "integrity_status": "PENDING"
        }
        
        try:
            # Establish direct low-level serial link connection using manifest parameters
            # Sets a strict 100ms timeout window ceiling to catch hardware lag drops instantly
            with serial.Serial(port=port_handle, baudrate=config["baud"], timeout=0.1) as ser:
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                
                for step in range(frame_count):
                    if not self.test_active:
                        break
                        
                    # Build structured test sentence frame: $PUNVCDG,port,index*CS\r\n
                    payload = f"PUNVCDG,{config['id']},{step:03d}"
                    checksum = self._compute_8bit_xor_checksum(payload)
                    outbound_sentence = f"${payload}*{checksum}\r\n"
                    
                    # Convert to raw ASCII bytes and write directly onto the copper bus wire
                    ser.write(outbound_sentence.encode('ascii'))
                    results["frames_transmitted"] += 1
                    
                    # Pause briefly to match physical signal transmission pacing limits
                    time.sleep(0.01)
                    
                    # Ingest returned loopback byte blocks off the physical wire
                    inbound_raw = ser.readline()
                    
                    if not inbound_raw:
                        results["line_timeouts"] += 1
                        continue
                        
                    try:
                        inbound_str = inbound_raw.decode('ascii', errors='ignore').strip()
                        
                        if not inbound_str.startswith('$') or '*' not in inbound_str:
                            results["checksum_failures"] += 1
                            continue
                            
                        # Verify loopback token integrity and cross-validate the returned checksum
                        body, received_cs = inbound_str[1:].split('*')
                        calculated_cs = self._compute_8bit_xor_checksum(body)
                        
                        if calculated_cs != received_cs.upper():
                            results["checksum_failures"] += 1
                        else:
                            results["frames_received"] += 1
                            
                    except Exception:
                        results["checksum_failures"] += 1
                        
            # Determine definitive physical wire pass/fail status thresholds
            if results["frames_received"] == frame_count and results["checksum_failures"] == 0:
                results["integrity_status"] = "PASSED (100% Signal Integrity)"
            else:
                results["integrity_status"] = "FAILED (Line Noise or Missing Loopback Plug)"
                
        except serial.SerialException as ser_error:
            results["integrity_status"] = f"PORT_UNAVAILABLE (Hardware Offline: {ser_error})"
            
        with self.lock:
            self.validation_results[port_handle] = results

    def execute_complete_hardware_verification(self, frames_per_port: int = 50) -> dict:
        """Spawns parallel background workers to stress-test all ports simultaneously without blocking."""
        print("\n======================= UNIVAC HARDWARE PROTOCOL VALIDATION SUITE =======================")
        print(f"[BOOT_DIAG] Loaded {len(self.ports_to_test)} frozen hardware ports from master manifest.")
        
        if not self.ports_to_test:
            print("[CRITICAL] Configuration matrix empty. Aborting validation routines.")
            return {}
            
        self.test_active = True
        self.validation_results.clear()
        
        worker_threads = []
        for handle, config in self.ports_to_test.items():
            t = threading.Thread(target=self._stress_test_isolated_port, args=(handle, config, frames_per_port))
            worker_threads.append(t)
            t.start()
            
        # Await completion of all independent parallel physical link checks
        for t in worker_threads:
            t.join()
            
        self.test_active = False
        
        # Output clean compliance audit report to command window
        print("\n============================= FINAL COMPLIANCE TELEMETRY LEDGER =============================")
        for handle, res in self.validation_results.items():
            print(f"Port Target: {handle:12} | ID: {res['interface_id']:10} | Status: {res['integrity_status']}")
            print(f" -> Tx Frames: {res['frames_transmitted']:3d} | Rx Frames: {res['frames_received']:3d} | Checksum Errors: {res['checksum_failures']:2d} | Timeouts: {res['line_timeouts']:2d}")
            print("-" * 90)
            
        return self.validation_results

# Standalone Execution Entry Point
if __name__ == "__main__":
    # Assume file runs from within '/src/config/' or handles safe parent directory routing steps
    engine = HardwareSerialValidationEngine(manifest_filename="manifest.json")
    engine.execute_complete_hardware_verification(frames_per_port=50)
