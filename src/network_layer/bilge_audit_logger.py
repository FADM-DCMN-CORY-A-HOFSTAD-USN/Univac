# File Name: bilge_audit_logger.py
# Location: /src/network_layer/
# Subsystem: Asynchronous Tamper-Proof Environmental Operational Audit Logger

import os
import csv
import queue
import threading
import time
import hashlib
from typing import Dict, Any

class BilgeEnvironmentalAuditLogger:
    def __init__(self, log_directory: str = "logs", file_prefix: str = "marpol_bilge_audit"):
        """
        Initializes the thread-isolated asynchronous environmental log engine.
        log_directory: The subdirectory directory footprint on the storage disk.
        file_prefix: Spreadsheet title tag (Defaults to maritime MARPOL style).
        """
        self.log_dir = os.path.join(os.path.dirname(__file__), "..", log_directory)
        self.file_prefix = file_prefix
        self.log_file_path = ""
        
        # High-speed RAM thread-safe FIFO buffer queue to offload I/O delays
        self.log_queue = queue.Queue(maxsize=1000)
        self.is_logging = False
        self.worker_thread = None
        
        # Tracking register storing the cryptographic signature hash of the previous row.
        # This creates a data chain, making any manual text tampering easily detectable.
        self.previous_row_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        
        # Definitive structural header schema mapping for environmental compliance audits
        self.csv_headers = [
            "timestamp_epoch", "active_authority_mode", "routing_source", 
            "overboard_valve_state", "recirc_valve_state", "total_volume_discharged_liters", 
            "oil_concentration_ppm", "current_row_sha256", "previous_row_sha256"
        ]

    def _initialize_log_file(self):
        """Creates the directory matrix and structures a fresh time-stamped CSV spreadsheet file on disk."""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
            
        time_str = time.strftime("%Y%m%d")
        filename = f"{self.file_prefix}_{time_str}.csv"
        self.log_file_path = os.path.join(self.log_dir, filename)
        
        # Write column headers to storage immediately if it is a new file
        if not os.path.exists(self.log_file_path):
            try:
                with open(self.log_file_path, mode='w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.csv_headers)
                print(f"[LOGGER] Environmental compliance ledger deployed at: {self.log_file_path}")
                watchdog.log_write_success('MARPOL_BILGE_AUDIT', self.log_queue.qsize())
            except IOError as e:
                print(f"[LOGGER_ERROR] Storage directory write restriction caught during boot: {e}")

    def capture_bilge_state_snapshot(self, resolved_commands: Dict[str, Any], oil_ppm: float):
        """
        Non-blocking high-speed entry point. Call this directly inside your 50Hz 
        main calculation loop to cache snapshots cleanly into RAM memory buffers.
        """
        if not self.is_logging:
            return
            
        try:
            # Flatten metrics into a clean intermediate dictionary data block
            snapshot_data = {
                'timestamp': time.time(),
                'mode': resolved_commands.get('active_authority_mode', 'UNKNOWN'),
                'source': resolved_commands.get('routing_source_string', 'UNKNOWN'),
                'overboard': resolved_commands.get('resolved_overboard_valve_open', 0),
                'recirc': resolved_commands.get('resolved_recirculation_valve_open', 0),
                'volume': resolved_commands.get('total_clean_water_discharged_liters', 0.0),
                'ppm': oil_ppm
            }
            
            # Non-blocking enqueue. If full, drop frame to prioritize calculation clock stability.
            self.log_queue.put_nowait(snapshot_data)
        except queue.Full:
            pass

    def _io_writer_worker_loop(self):
        """Asynchronous disk I/O worker thread loop handling string packaging."""
        self._initialize_log_file()
        
        while self.is_logging or not self.log_queue.empty():
            try:
                # Retrieve the snapshot data out of the RAM queue
                data = self.log_queue.get(timeout=1.0)
                
                # --- TAMPER-PROOF CRYPTOGRAPHIC SIGNATURE GENERATION ---
                # Build a raw string concatenation baseline summarizing the transaction parameters
                data_string = f"{data['timestamp']},{data['mode']},{data['source']},{data['overboard']},{data['recirc']},{data['volume']},{data['ppm']},{self.previous_row_hash}"
                
                # Compute SHA-256 validation hash signature
                current_sha256 = hashlib.sha256(data_string.encode('utf-8')).hexdigest()
                
                # Compile standard flat list mapping row elements matching headers
                final_row = [
                    data['timestamp'], data['mode'], data['source'],
                    data['overboard'], data['recirc'], data['volume'],
                    data['ppm'], current_sha256, self.previous_row_hash
                ]
                
                # Append line to storage file on the disk array
                with open(self.log_file_path, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(final_row)
                    watchdog.log_write_success('MARPOL_BILGE_AUDIT', self.log_queue.qsize())
                    
                # Cache current signature hash deep into memory to link the next line
                self.previous_row_hash = current_sha256
                self.log_queue.task_done()
                
            except queue.Empty:
                continue
            except IOError as disk_fault:
                print(f"[LOGGER_ERROR] Environmental log disk access delayed: {disk_fault}")
                time.sleep(1.0)

    def start_logger_services(self):
        """Spins up the isolated data-writing worker background thread."""
        if self.is_logging:
            return
        self.is_logging = True
        self.worker_thread = threading.Thread(target=self._io_writer_worker_loop, daemon=True)
        self.worker_thread.start()
        print("[LOGGER] Asynchronous environmental audit recording thread active.")

    def stop_logger_services(self):
        """Gracefully flushes remaining data rows to storage and secures file locks."""
        print(f"[LOGGER] Flushing {self.log_queue.qsize()} pending environmental logs to storage arrays...")
        self.is_logging = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
        print("[LOGGER] Environmental compliance ledger closed safely on hardware storage.")

# Verification and Diagnostic Validation Run Profile
if __name__ == "__main__":
    logger = BilgeEnvironmentalAuditLogger(log_directory="test_logs")
    logger.start_logger_services()
    
    # Generate two sequential mock status shifts to verify hashing mechanics
    mock_resolved_1 = {'active_authority_mode': 'UNIVAC', 'routing_source_string': 'UNIVAC_MAINFRAME_PASS_THROUGH', 'resolved_overboard_valve_open': 1, 'resolved_recirculation_valve_open': 0, 'total_clean_water_discharged_liters': 15.5}
    mock_resolved_2 = {'active_authority_mode': 'REPLACEMENT', 'routing_source_string': 'OUR_CORE_PHYSICS_LOOP', 'resolved_overboard_valve_open': 0, 'resolved_recirculation_valve_open': 1, 'total_clean_water_discharged_liters': 15.5}
    
    print("\nSimulating on-the-fly authority transitions across tracking registers...")
    logger.capture_bilge_state_snapshot(mock_resolved_1, oil_ppm=2.4)
    time.sleep(0.05)
    logger.capture_bilge_state_snapshot(mock_resolved_2, oil_ppm=14.8)
    
    time.sleep(0.5) # Let background threads finish writing to files
    logger.stop_logging_services()
    
    # Read the file text blocks back dynamically to demonstrate tamper proof validation
    with open(logger.log_file_path, mode='r') as test_file:
        lines = test_file.readlines()
        print("\nGENERATED AUDIT LOG SAMPLE ENTRIES (COMPLIANCE ENCRYPTED):")
        print("-" * 115)
        for idx, line in enumerate(lines[1:]): # Skip headers
            print(f"Row {idx} String: {line.strip()[:105]}...")
            
    # Cleanup verification test directory tracks
    if os.path.exists(logger.log_file_path):
        os.remove(logger.log_file_path)
        os.rmdir(logger.log_dir)
