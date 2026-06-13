# File Name: main.py
# Location: /src/
# Subsystem: Central Orchestration Entry Point & Real-Time Timing Profile Loop

import time
import sys
import math
import queue
import threading
import serial # Requires pyserial

# ------------------------------------------------------------------------------
# SUBSYSTEM IMPORTS
# ------------------------------------------------------------------------------
from config.boot_verification_suite import AutomatedBootVerificationSuite
from config.config_manager import VesselConfigManager
from config.weapon_balance_matrix import NavalWeaponsBalanceMatrix
from control_core.bridge_execution_engine import UnivacReplacementBridgeEngine
from control_core.asymmetric_roll_stabilizer import AsymmetricRollStabilizerMatrix
from control_core.anchor_interlock_subroutine import AutonomousAnchorInterlockSubroutine
from control_core.bilge_authority_router import BilgeControlAuthorityRouter
from control_core.flag_changer_subroutine import AutomaticFlagChangerSubroutine

from network_layer.multi_ledger_watchdog import MultiLedgerHardwareWatchdog
from network_layer.bridge_network_router import BridgeNetworkRouter
from network_layer.serial_port_listener import ThreadedSerialPortListener
from network_layer.tcp_command_listener import JsonTcpCommandListener
from network_layer.weapon_serial_parser import WeaponSerialBusParser
from network_layer.weapon_async_parser import WeaponAsyncParserExtension
from network_layer.weapon_serial_serializer import WeaponSerialOutputSerializer
from network_layer.asymmetric_network_serializer import AsymmetricNetworkSerializer

from network_layer.data_logger_node import AutomatedMissionDataLogger
from network_layer.flag_fault_logger import FlagHalyardFaultLogger
from network_layer.bilge_audit_logger import BilgeEnvironmentalAuditLogger

# ------------------------------------------------------------------------------
# AUDIT FIX 1: ASYNCHRONOUS TRANSMISSION QUEUE (9600-Baud Trap Resolution)
# ------------------------------------------------------------------------------
tx_queue = queue.Queue(maxsize=200)

def serial_tx_worker():
    """Background thread to handle slow RS-422 writes without blocking the 50Hz math loop."""
    while True:
        payload, port = tx_queue.get()
        if port and port.is_open:
            try:
                port.write(payload)
            except serial.SerialException as e:
                print(f"[TX_ERROR] Serial write failed: {e}")
        tx_queue.task_done()

# Spin up the background I/O worker immediately
threading.Thread(target=serial_tx_worker, daemon=True).start()

# ------------------------------------------------------------------------------
# MAIN BOOTSTRAP ROUTINE
# ------------------------------------------------------------------------------
def bootstrap_system():
    print("=" * 80)
    print("        UNIVAC REPLACEMENT COGNITIVE MATRIX BRIDGE ARCHITECTURE MASTER CORE")
    print("=" * 80)

    # 1. PRE-FLIGHT BOOT COGNITIVE SUITE
    boot_validator = AutomatedBootVerificationSuite(target_config_file="vessel_config.json", log_directory="logs")
    if not boot_validator.execute_full_suite():
        print("[CRITICAL_BOOT_FAIL] Safety validations broke. Aborting startup to protect actuators.")
        sys.exit(1)

    # 2. CONFIGURATION & HARDWARE PROFILES
    print("[BOOT] Accessing storage matrix data layers...")
    config_loader = VesselConfigManager("vessel_config.json")
    vessel_profile = config_loader.load_system_specifications()
    selected_ship_class = 'DDG_ARLEIGH_BURKE' 

    # 3. SAFETY WATCHDOG
    print("[BOOT] Activating Multi-Ledger Hardware Watchdog...")
    watchdog = MultiLedgerHardwareWatchdog(write_timeout_sec=1.5, log_directory="logs")
    watchdog.start_watchdog()

    # 4. MATHEMATICAL ENGINE & SUBSYSTEMS
    print("[BOOT] Booting 75-Feature Predictive Control Engine Core...")
    engine = UnivacReplacementBridgeEngine(vessel_profile)
    weapons_matrix = NavalWeaponsBalanceMatrix()
    asym_stabilizer = AsymmetricRollStabilizerMatrix(vessel_profile)
    anchor_lock_manager = AutonomousAnchorInterlockSubroutine()
    bilge_router = BilgeControlAuthorityRouter()
    flag_manager = AutomaticFlagChangerSubroutine()
    ew_serializer = WeaponSerialOutputSerializer(manufacturer_code="UNVC")
    asym_serializer = AsymmetricNetworkSerializer(prefix_manufacturer="PUNVC")
    weapon_async_link = WeaponAsyncParserExtension(manufacturer_code="MK45")
    weapon_parser = WeaponSerialBusParser()

    # 5. DATA LOGGERS
    print("[BOOT] Starting environmental and mission audit loggers...")
    mission_logger = AutomatedMissionDataLogger(log_directory="logs", file_prefix="uss_univac_bridge")
    flag_logger = FlagHalyardFaultLogger(log_directory="logs", file_prefix="flag_halyard_audit")
    bilge_logger = BilgeEnvironmentalAuditLogger(log_directory="logs", file_prefix="marpol_bilge_audit")
    mission_logger.start_logging_services()
    flag_logger.start_logger_services()
    bilge_logger.start_logger_services()

    # 6. NETWORK INGESTION & LISTENERS
    print("[BOOT] Binding hardware network abstraction routing matrices...")
    router = BridgeNetworkRouter(target_hardware_ip="192.168.1.50", target_port=5005)
    router.start_router_services(udp_rate_hz=50.0)

    command_server = JsonTcpCommandListener(host_ip="0.0.0.0", port=7000)
    command_server.start_server()

    # Mock Serial Port Mapping (Replace with actual physical ports)
    try:
        steering_serial_hardware_wire = serial.Serial('/dev/ttyUSB1', 9600, timeout=0)
        weapon_serial_hardware_wire = serial.Serial('/dev/ttyUSB2', 9600, timeout=0)
        machinery_bus_serial_port = serial.Serial('/dev/ttyUSB3', 9600, timeout=0)
    except serial.SerialException:
        print("[WARNING] Hardware serial ports not found. Running in simulation/headless mode.")
        steering_serial_hardware_wire, weapon_serial_hardware_wire, machinery_bus_serial_port = None, None, None

    print("\n[BOOT] System initialization complete. Entering 50Hz real-time control matrix loop.")
    print("-" * 80)

    # --------------------------------------------------------------------------
    # HARD-REAL-TIME TIMING STACK (50Hz)
    # --------------------------------------------------------------------------
    loop_rate_hz = 50.0  
    dt = 1.0 / loop_rate_hz
    
    try:
        while True:
            start_cycle_time = time.time()
            
            # -- A. INGESTION & SENSOR PARSING --
            active_targets = command_server.get_latest_targets()
            live_telemetry = router.get_synchronized_telemetry()
            
            # Extract high-speed weapon encoder state
            raw_weapon_data = live_telemetry.get('raw_weapon_string', "")
            live_gun_state = weapon_parser.ingest_encoder_sentence(raw_weapon_data, start_cycle_time)
            if weapon_serial_hardware_wire and weapon_serial_hardware_wire.is_open:
                raw_gun_bus_string = weapon_serial_hardware_wire.readline().decode('ascii', errors='ignore')
                gun_metrics = weapon_async_link.process_async_line(raw_gun_bus_string)
            else:
                gun_metrics = {'azimuth_deg': 0.0, 'elevation_deg': 0.0, 'azimuth_rate_rads': 0.0, 'elevation_rate_rads': 0.0}

            # -- B. WEAPON CROSS-COUPLING (LIST COMPENSATION) --
            weapon_imbalance = weapons_matrix.evaluate_vessel_cross_coupling_impact(
                ship_class=selected_ship_class,
                weapon_azimuth_deg=gun_metrics['azimuth_deg'],
                weapon_elevation_deg=gun_metrics['elevation_deg'],
                az_rate=gun_metrics['azimuth_rate_rads'],
                el_rate=gun_metrics['elevation_rate_rads']
            )
            # Pre-compensate Rudder Roll Stabilization for gun weight shift
            live_telemetry['roll_angle_rad'] += math.radians(weapon_imbalance['induced_roll_list_angle_deg'])

            # -- C. MASTER UNIVAC ENGINE LOOP --
            actuator_commands = engine.execute_bridge_loop(active_targets, live_telemetry, dt)
            actuator_commands['upstream_autonomy_telemetry']['Weapon_Balance_Metrics'] = weapon_imbalance
            slew_rate_cap = actuator_commands.get('active_rpm_cap', 5.0) # Fallback mapping

            # -- D. AUXILIARY ACTUATOR ROUTING (Anchor, Bilge, Flag, Stabilizers) --
            
            # 1. Anchor Interlock
            navy_clearance_flag = active_targets.get('navy_anchor_release_code', False)
            anchor_interlock_commands = anchor_lock_manager.evaluate_anchor_safety_matrix(
                weapon_metrics=live_gun_state,
                user_override_unlock=navy_clearance_flag
            )
            if not anchor_interlock_commands['sea_machines_anchor_authority_allowed']:
                actuator_commands['active_rpm_cap'] = min(actuator_commands['active_rpm_cap'], 100.0)
            
            anchor_payload = f"PUNVCANC,{anchor_interlock_commands['command_windlass_clutch_engage']},{anchor_interlock_commands['command_brake_solenoid_lock']},{1 if not anchor_interlock_commands['sea_machines_anchor_authority_allowed'] else 0}"
            anchor_cs = 0
            for char in anchor_payload: anchor_cs ^= ord(char)
            anchor_packet = f"${anchor_payload}*{anchor_cs:02X}\r\n".encode('ascii')
            tx_queue.put_nowait((anchor_packet, weapon_serial_hardware_wire))

            # 2. Bilge Authority Router
            requested_mode = active_targets.get('requested_authority_mode')
            if requested_mode:
                bilge_router.set_control_authority(requested_mode)
            
            resolved_bilge_commands = bilge_router.resolve_final_actuator_commands(
                univac_pass_through={'actuator_overboard_valve_open': 1, 'actuator_recirculation_valve_open': 0},
                our_physics_loop={'actuator_overboard_valve_open': 0, 'actuator_recirculation_valve_open': 1},
                seamachines_input={'actuator_overboard_valve_open': 0, 'actuator_recirculation_valve_open': 0}
            )
            bilge_payload = f"PUNVCBLG,{resolved_bilge_commands['resolved_overboard_valve_open']},{resolved_bilge_commands['resolved_recirculation_valve_open']},0.0"
            bilge_cs = 0
            for char in bilge_payload: bilge_cs ^= ord(char)
            bilge_packet = f"${bilge_payload}*{bilge_cs:02X}\r\n".encode('ascii')
            tx_queue.put_nowait((bilge_packet, machinery_bus_serial_port))

            # 3. Flag Changer
            flag_actuation_commands = flag_manager.evaluate_flag_logic_matrix(
                weapon_state=live_gun_state,
                telemetry=live_telemetry,
                transit_targets=active_targets
            )
            flag_payload = f"PUNVCFLG,{flag_actuation_commands['commanded_halyard_motor_position_pct']:.1f},{flag_actuation_commands['actuator_motor_power_relay']},{flag_actuation_commands['actuator_mechanical_lock_pin']}"
            flag_cs = 0
            for char in flag_payload: flag_cs ^= ord(char)
            flag_packet = f"${flag_payload}*{flag_cs:02X}\r\n".encode('ascii')
            tx_queue.put_nowait((flag_packet, machinery_bus_serial_port))

            # 4. Asymmetric Roll Stabilizers (Port/Stbd Rudder Split)
            stabilizer_commands = asym_stabilizer.calculate_fire_synchronized_stabilization(
                targets=active_targets,
                telemetry=live_telemetry,
                weapon_state=live_gun_state,
                dt=dt
            )
            port_wire_packet, stbd_wire_packet = asym_serializer.serialize_asymmetric_actuator_channels(
                stabilizer_matrix_output=stabilizer_commands,
                depth_slew_cap=slew_rate_cap
            )
            tx_queue.put_nowait((port_wire_packet, steering_serial_hardware_wire))
            tx_queue.put_nowait((stbd_wire_packet, steering_serial_hardware_wire))

            # -- E. WATCHDOG SAFETY INTERLOCKS --
            compliance_status = watchdog.get_watchdog_diagnostics()
            if compliance_status['watchdog_system_faulted']:
                actuator_commands['command_motor_torque_nm'] = 0.0
                print(f"[SAFETY_INTERLOCK] Propulsion secured. Fault detected: {compliance_status['watchdog_tripped_ledgers']}")

            # -- F. LOGGING & DISPATCH --
            router.route_calculated_loop_outputs(actuator_commands)
            mission_logger.log_snapshot(actuator_commands, live_telemetry)
            flag_logger.capture_flag_event_snapshot(flag_actuation_commands)
            
            resolved_bilge_commands['total_clean_water_discharged_liters'] = 0.0
            bilge_logger.capture_bilge_state_snapshot(resolved_bilge_commands, live_telemetry.get('ppm_reading', 0.0))

            watchdog.poke_watchdog('MAIN_CORE_MATH')

            # -- G. 50HZ CLOCK TIMING ENFORCEMENT --
            execution_time = time.time() - start_cycle_time
            sleep_window = dt - execution_time
            if sleep_window > 0:
                time.sleep(sleep_window)
            else:
                print(f"[WARN] Frame dropped! Loop took {execution_time*1000:.1f}ms (Max 20.0ms)")

    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Intercepted manual shutdown request. Suspending communication pipes...")
        flag_logger.stop_logger_services() 
        bilge_logger.stop_logging_services() 
        mission_logger.stop_logging_services() 
        command_server.stop_server()
        router.stop_router_services()
        print("[SHUTDOWN] Replacement bridge system matrix completely offline.")

if __name__ == "__main__":
    bootstrap_system()
