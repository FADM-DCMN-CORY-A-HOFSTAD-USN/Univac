# File Name: main.py
# Location: /src/
# Subsystem: Central Orchestration Entry Point & Real-Time Timing Profile Loop

import time
import sys
import math

# Core Subsystem Imports
from config.config_manager import VesselConfigManager
from config.weapon_balance_matrix import NavalWeaponsBalanceMatrix
from control_core.bridge_execution_engine import UnivacReplacementBridgeEngine
from network_layer.bridge_network_router import BridgeNetworkRouter
from network_layer.serial_port_listener import ThreadedSerialPortListener
from network_layer.tcp_command_listener import JsonTcpCommandListener
from network_layer.weapon_serial_parser import WeaponSerialBusParser
from network_layer.data_logger_node import AutomatedMissionDataLogger

# Bootstrap real-time data logger pipeline
mission_logger = AutomatedMissionDataLogger(log_directory="logs", file_prefix="uss_univac_bridge")
mission_logger.start_logging_services()

def bootstrap_system():
    print("=" * 80)
    print("        UNIVAC REPLACEMENT COGNITIVE MATRIX BRIDGE ARCHITECTURE MASTER CORE")
    print("=" * 80)

    # STEP 1: Centralized Configuration Loading
    print("[BOOT] Accessing storage matrix data layers...")
    config_loader = VesselConfigManager("vessel_config.json")
    vessel_profile = config_loader.load_system_specifications()

    # STEP 2: Mathematical Engine Core Initialization
    print("[BOOT] Booting 75-Feature Predictive Control Engine Core...")
    engine = UnivacReplacementBridgeEngine(vessel_profile)
    weapons_matrix = NavalWeaponsBalanceMatrix()

    # STEP 3: Network Topology Setup (Hardware Abstraction Multiplexers)
    print("[BOOT] Binding hardware network abstraction routing matrices...")
    # Target IP must point to your physical motor driver PLC / central switch array
    router = BridgeNetworkRouter(target_hardware_ip="192.168.1.50", target_port=5005)
    router.start_router_services(udp_rate_hz=50.0)

    # STEP 4: Asynchronous Serial / Network Port Ingestion Deployment
    print("[BOOT] Activating JSON-over-TCP terminal listener on Port 7000...")
    command_server = JsonTcpCommandListener(host_ip="0.0.0.0", port=7000)
    command_server.start_server()

    print("[BOOT] Deploying background serial port reading loops...")
    # Cross-platform parameter adjustments for Windows (COMx) vs. Unix (/dev/ttyUSBx) interfaces
    compass_port = "COM3" if sys.platform.startswith('win') else "/dev/ttyUSB0"
    sonar_port = "COM4" if sys.platform.startswith('win') else "/dev/ttyUSB1"
    weapon_port = "COM5" if sys.platform.startswith('win') else "/dev/ttyUSB2"
    
    compass_listener = ThreadedSerialPortListener(router, port_name=compass_port, baud_rate=4800)
    sonar_listener = ThreadedSerialPortListener(router, port_name=sonar_port, baud_rate=4800)
    
    # Initialize the high-speed independent weapon bus parser
    weapon_parser = WeaponSerialBusParser()
    weapon_listener = ThreadedSerialPortListener(router, port_name=weapon_port, baud_rate=9600)
    
    compass_listener.start_listening()
    sonar_listener.start_listening()
    weapon_listener.start_listening()

    print("\n[BOOT] System initialization complete. Entering real-time control matrix loop.")
    print("-" * 80)

    # --- MAIN HARD-REAL-TIME TIMING STACK CONFIGURATION ---
    loop_rate_hz = 50.0  # Runs calculations exactly at 50Hz frequency cycles (20ms)
    dt = 1.0 / loop_rate_hz
    
    # Identify active fleet hull type to track weapon mass cross-coupling shifts
    # Options catalog: 'DDG_ARLEIGH_BURKE', 'CG_TICONDEROGA', 'WMSL_LEGEND_USCG'
    selected_ship_class = 'DDG_ARLEIGH_BURKE' 
    
    try:
        while True:
            start_cycle_time = time.time()
            
            # 1. Thread-safe ingestion of sensor telemetry and network targets
            active_targets = command_server.get_latest_targets()
            live_telemetry = router.get_synchronized_telemetry()
            
            # 2. Extract and resolve raw weapon tracking strings if present on the data line
            # Custom encoder parsing allows numerical differentiation for velocities (rad/s)
            raw_weapon_data = router.get_synchronized_telemetry().get('raw_weapon_string', "")
            live_gun_state = weapon_parser.ingest_encoder_sentence(raw_weapon_data, start_cycle_time)
            
            # 3. Calculate dynamic asymmetric mass moment shifts & gyroscopic deck strains
            weapon_imbalance = weapons_matrix.evaluate_vessel_cross_coupling_impact(
                ship_class=selected_ship_class,
                weapon_azimuth_deg=live_gun_state['azimuth_deg'],
                weapon_elevation_deg=live_gun_state['elevation_deg'],
                az_rate=live_gun_state['azimuth_rate_rads'],
                el_rate=live_gun_state['elevation_rate_rads']
            )
            
            # 4. Inject weapon induced list adjustments straight into the active roll state
            # This forces the Rudder Roll Stabilization (RRS) matrix to pre-compensate for gun weight
            induced_list_rad = math.radians(weapon_imbalance['induced_roll_list_angle_deg'])
            live_telemetry['roll_angle_rad'] += induced_list_rad
            
            # 5. Execute 75-feature multi-variable calculation loop step
            actuator_commands = engine.execute_bridge_loop(active_targets, live_telemetry, dt)
            
            # Append weapon metrics to outbound monitoring diagnostics packet
            actuator_commands['upstream_autonomy_telemetry']['Weapon_Balance_Metrics'] = weapon_imbalance
            
            # 6. Dispatch wire-level serial and UDP control datagram sentences down to hardware
            router.route_calculated_loop_outputs(actuator_commands)
            
            # 7. Enforce strict deterministic clock bounding limits
            execution_time = time.time() - start_cycle_time
            sleep_window = dt - execution_time
            if sleep_window > 0:
                time.sleep(sleep_window)
                
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Intercepted manual shutdown request. Suspending communication pipes...")
        compass_listener.stop_listening()
        sonar_listener.stop_listening()
        weapon_listener.stop_listening()
        command_server.stop_server()
        router.stop_router_services()
        print("[SHUTDOWN] Replacement bridge system matrix completely offline.")

if __name__ == "__main__":
    bootstrap_system()
