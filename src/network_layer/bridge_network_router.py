# File Name: bridge_network_router.py
# Location: /src/network_layer/
# Subsystem: Core Network Multiplexer and Hardware Routing Layer

import threading
import time
from typing import Dict, Any

# Import your existing network layer components
from nmea_serial_parser import NmeaSerialDataParser
from actuator_serial_serializer import ActuatorSerialOutputSerializer
from actuator_telemetry_receiver import ActuatorTelemetryReceiverNode
from bridge_network_interface import BridgeActuatorNetworkInterface

class BridgeNetworkRouter:
    def __init__(self, target_hardware_ip: str, target_port: int, manufacturer_code: str = "UNVC"):
        """
        Manages data routing across the serial ports, UDP broadcast buffers, 
        and hardware abstraction filters.
        """
        # Instantiate network-layer sub-modules
        self.parser = NmeaSerialDataParser()
        self.serializer = ActuatorSerialOutputSerializer(manufacturer_code)
        self.receiver = ActuatorTelemetryReceiverNode(manufacturer_code)
        self.udp_interface = BridgeActuatorNetworkInterface(target_ip=target_hardware_ip, target_port=target_port)
        
        # Thread isolation registers
        self.router_lock = threading.Lock()
        self.is_active = False
        self.routing_thread = None
        
        # Internal state memory caches
        self.live_telemetry_cache = {}
        self.latest_engine_commands = {}

    def ingest_raw_serial_line(self, raw_nmea_string: str):
        """
        Entry-point for raw incoming copper-wire serial lines (RS-422).
        Parses strings and automatically stores results into the global routing cache.
        """
        current_time = time.time()
        with self.router_lock:
            # Parse sentence and update the central network metrics register
            self.live_telemetry_cache = self.parser.parse_sentence(raw_nmea_string, current_time)

    def route_calculated_loop_outputs(self, engine_output: Dict[str, Any]) -> tuple:
        """
        Ingests calculated output metrics from the bridge engine,
        routes them instantly to the UDP background broadcaster, and builds 
        proprietary NMEA byte strings for physical steering and motor lines.
        """
        with self.router_lock:
            self.latest_engine_commands = engine_output.copy()
            
        # 1. Update the concurrent background UDP stream interface
        self.udp_interface.update_latest_commands(engine_output)
        
        # 2. Serialize raw NMEA byte-sentences for local serial line transmitters
        steering_serial_packet = self.serializer.serialize_rudder_command(engine_output)
        propulsion_serial_packet = self.serializer.serialize_propulsion_command(engine_output)
        
        return steering_serial_packet, propulsion_serial_packet

    def ingest_hardware_feedback_line(self, raw_feedback_string: str, dt: float) -> dict:
        """
        Ingests acknowledgment verification data returned directly from physical rudders.
        Cross-checks against ordered targets to monitor for linkage jams.
        """
        with self.router_lock:
            ordered_rudder = self.latest_engine_commands.get('command_rudder_angle_deg', 0.0)
            
        # Process structural checks inside the receiver node
        feedback_report = self.receiver.process_hardware_feedback(raw_feedback_string, ordered_rudder, dt)
        
        # If the feedback receiver detects a structural fault, append it back to live telemetry
        with self.router_lock:
            self.live_telemetry_cache['rudder_deg'] = feedback_report.get('measured_rudder_deg', 0.0)
            if feedback_report.get('hardware_faults_active'):
                self.live_telemetry_cache['hardware_fault_triggered'] = True
                
        return feedback_report

    def get_synchronized_telemetry(self) -> dict:
        """Safe thread-locked snapshot of current metrics for the main math engine."""
        with self.router_lock:
            return self.live_telemetry_cache.copy()

    def start_router_services(self, udp_rate_hz: float = 50.0):
        """Spins up background network execution tasks."""
        if self.is_active:
            return
        self.is_active = True
        self.udp_interface.start_interface(tx_rate_hz=udp_rate_hz)
        print("[ROUTER] Async Network Router Infrastructure Active.")

    def stop_router_services(self):
        """Safely winds down all active communication links."""
        self.is_active = False
        self.udp_interface.stop_interface()
        print("[ROUTER] Async Network Router Infrastructure Suspended.")

# Verification Environment
if __name__ == "__main__":
    # Test setting up the router targeting a local loopback IP
    router = BridgeNetworkRouter(target_hardware_ip="127.0.0.1", target_port=5005)
    router.start_router_services(udp_rate_hz=10.0)
    
    # Simulate feeding raw radar/sonar sensor streams into the network router input
    print("\nSimulating incoming sensor network strings...")
    router.ingest_raw_serial_line("$SDDBT,24.6,f,8.40,M,4.1,F*0E\r\n") # Depth 8.4m
    
    # Check that data synchronized into cache matrix perfectly
    cached_data = router.get_synchronized_telemetry()
    print(f"Router Synchronized Cache Verification (Depth): {cached_data['depth']} Meters")
    
    router.stop_router_services()
