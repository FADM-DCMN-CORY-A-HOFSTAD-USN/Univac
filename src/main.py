# File Name: main.py
# Location: /src/
# Subsystem: Central Orchestration Entry Point

import time
import sys
from config.config_manager import VesselConfigManager
from control_core.bridge_execution_engine import UnivacReplacementBridgeEngine
from network_layer.bridge_network_router import BridgeNetworkRouter
from network_layer.serial_port_listener import ThreadedSerialPortListener
from network_layer.tcp_command_listener import JsonTcpCommandListener

def bootstrap_system():
    print("=" * 80)
    print("        INITIALIZING UNIVAC REPLACEMENT BRIDGE COGNITIVE MATRIX ARCHITECTURE")
    print("=" * 80)

    # STEP 1: Load and validate vessel parameters from disk configuration file
    config_loader = VesselConfigManager("vessel_config.json")
    vessel_profile = config_loader.load_system_specifications()

    # STEP 2: Instantiate core mathematical execution loop
    print("[BOOT] Booting 75-Feature Predictive Control Engine Core...")
    engine = UnivacReplacementBridgeEngine(vessel_profile)

    # STEP 3: Spin up data network routers and background UDP streams
    print("[BOOT] Binding hardware network abstraction routing matrices...")
    # Change IP to match your hardware motor driver PLC/Controller network configuration
    router = BridgeNetworkRouter(target_hardware_ip="192.168.1.50", target_port=5005)
    router.start_router_services(udp_rate_hz=50.0)

    # STEP 4: Start Ethernet TCP server to capture remote workstation inputs
    print("[BOOT] Starting JSON-over-TCP terminal listener on Port 7000...")
    command_server = JsonTcpCommandListener(host_ip="0.0.0.0", port=7000)
    command_server.start_server()

    # STEP 5: Attach serial hardware listener strings to active router caches
    print("[BOOT] Deploying background serial port reading loops...")
    compass_port = "COM3" if sys.platform.startswith('win') else "/dev/ttyUSB0"
    sonar_port = "COM4" if sys.platform.startswith('win') else "/dev/ttyUSB1"
    
    compass_listener = ThreadedSerialPortListener(router, port_name=compass_port, baud_rate=4800)
    sonar_listener = ThreadedSerialPortListener(router, port_name=sonar_port, baud_rate=4800)
    
    compass_listener.start_listening()
    sonar_listener.start_listening()

    print("\n[BOOT] System initialization complete. Entering real-time control matrix loop.")
    print("-" * 80)

    # --- MAIN HARD-REAL-TIME REALTIME EXECUTION TIMING PROFILE LOOP ---
    loop_rate_hz = 50.0
    dt = 1.0 / loop_rate_hz
    
    try:
        while True:
            start_cycle_time = time.time()
            
            # Thread-safely grab latest network targets and sensor updates
            active_targets = command_server.get_latest_targets()
            live_telemetry = router.get_synchronized_telemetry()
            
            # Execute the core 75-feature multi-variable calculation matrix step
            actuator_commands = engine.execute_bridge_loop(active_targets, live_telemetry, dt)
            
            # Instantly serialize and dispatch data packages across the hardware network
            router.route_calculated_loop_outputs(actuator_commands)
            
            # Maintain deterministic cycle timing execution profile bounds
            execution_time = time.time() - start_cycle_time
            sleep_window = dt - execution_time
            if sleep_window > 0:
                time.sleep(sleep_window)
                
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Intercepted stop signal. Commencing orderly teardown sequence...")
        compass_listener.stop_listening()
        sonar_listener.stop_listening()
        command_server.stop_server()
        router.stop_router_services()
        print("[SHUTDOWN] Bridge core safely offline.")

if __name__ == "__main__":
    bootstrap_system()
