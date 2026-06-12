# File Name: serial_port_listener.py
# Location: /src/network_layer/
# Subsystem: Asynchronous Hardware Serial Ingestion Engine

import threading
import time
import sys

# Ensure user has pyserial installed ('pip install pyserial')
try:
    import serial
except ImportError:
    # Safe fallback wrapper mock class if testing without physical hardware packages
    serial = None

class ThreadedSerialPortListener:
    def __init__(self, router_instance, port_name: str = "/dev/ttyUSB0", baud_rate: int = 4800, timeout_sec: float = 1.0):
        """
        Initializes an isolated high-priority background serial ingestion loop.
        
        router_instance: Instantiated BridgeNetworkRouter object to route decoded data.
        port_name: System hardware handle (e.g., '/dev/ttyUSB0' on Linux, 'COM3' on Windows).
        baud_rate: Standard maritime NMEA communication speed (4800 for legacy, 38400 for AIS).
        timeout_sec: Maximum blocking window for serial buffer reading operations.
        """
        self.router = router_instance
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.timeout = timeout_sec
        
        self.serial_connection = None
        self.is_listening = False
        self.worker_thread = None

    def _execute_read_loop(self):
        """Asynchronous worker thread running the hard-real-time ingestion cycle."""
        print(f"[SERIAL] Establishing connection matrix on hardware port: {self.port_name} ({self.baud_rate} Baud)")
        
        while self.is_listening:
            try:
                if self.serial_connection is None or not self.serial_connection.is_open:
                    if serial is None:
                        print("[SERIAL_MOCK] Pyserial module not found. Running software emulation.")
                        self._run_emulation_routine()
                        return
                        
                    # Attempt physical connection open sequence
                    self.serial_connection = serial.Serial(
                        port=self.port_name,
                        baudrate=self.baud_rate,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=self.timeout
                    )
                    print(f"[SERIAL] Hardware port {self.port_name} connected successfully.")

                # Read raw input sequence until reaching an end-of-line frame
                # NMEA-0183 standard sentences always terminate with \n (0x0A)
                raw_bytes = self.serial_connection.readline()
                
                if raw_bytes:
                    try:
                        # Decode raw binary ascii buffer stream safely into standard characters
                        decoded_sentence = raw_bytes.decode('ascii', errors='ignore')
                        
                        # Forward the string package straight to the network router cache matrix
                        if decoded_sentence.strip():
                            self.router.ingest_raw_serial_line(decoded_sentence)
                    except Exception as parse_error:
                        print(f"[SERIAL_ERROR] Local byte string decoding failure: {parse_error}")

            except (IOError, Exception) as hardware_disconnect_error:
                print(f"[SERIAL_ALERT] Connection dropped on {self.port_name}: {hardware_disconnect_error}")
                print("[SERIAL] Re-attempting physical interface registration in 3.0 seconds...")
                if self.serial_connection:
                    try:
                        self.serial_connection.close()
                    except:
                        pass
                    self.serial_connection = None
                time.sleep(3.0)

    def _run_emulation_routine(self):
        """Generates mock hardware telemetry over time if run on a non-connected machine."""
        mock_heading = 124.5
        while self.is_listening:
            time.sleep(0.2)
            mock_heading = (mock_heading + 0.1) % 360.0
            # Construct a simulated heading frame with a valid pre-computed checksum (*1C format equivalent)
            dummy_sentence = f"$HEHDT,{mock_heading:.1f},T*1C\r\n"
            self.router.ingest_raw_serial_line(dummy_sentence)

    def start_listening(self):
        """Spins up the isolated hardware interception background thread."""
        if self.is_listening:
            return
        self.is_listening = True
        self.worker_thread = threading.Thread(target=self._execute_read_loop, daemon=True)
        self.worker_thread.start()
        print(f"[SERIAL] Threaded Listener service spawned for {self.port_name}.")

    def stop_listening(self):
        """Gracefully winds down the interface serial connection port."""
        self.is_listening = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print(f"[SERIAL] Hardware device {self.port_name} closed down.")

# Verification Integration Check
if __name__ == "__main__":
    # Mock Router framework stub to catch incoming telemetry metrics for local verification
    class MockRouterStub:
        def ingest_raw_serial_line(self, raw_nmea_string: str):
            print(f"[ROUTER_STUB_RECV] Received from wire: {raw_nmea_string.strip()}")

    mock_router = MockRouterStub()
    
    # Configure cross-platform listener parameter formats safely
    test_port = "COM3" if sys.platform.startswith('win') else "/dev/ttyUSB0"
    
    listener = ThreadedSerialPortListener(router_instance=mock_router, port_name=test_port, baud_rate=4800)
    
    print("LAUNCHING SERIAL TELEMETRY INTERCEPTION NODES:")
    print("-" * 65)
    listener.start_listening()
    
    time.sleep(1.0) # Allow standard streaming frames to cascade across loop threads
    listener.stop_listening()
