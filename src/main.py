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
from network_layer.shore_weapon_serializer import ShoreWeaponSystemSerializer # NEW SHORE LINK

from network_layer.data_logger_node import AutomatedMissionDataLogger
from network_layer.flag_fault_logger import FlagHalyardFaultLogger
from network_layer.bilge_audit_logger import BilgeEnvironmentalAuditLogger
from network_layer.univac_architecture_hal import UnivacArchitectureHAL

# Boot the Dynamic Multi-Model Hardware Abstraction Layer
univac_hal = UnivacArchitectureHAL()

# Select active hardware profile for the current voyage
# Target Catalog Options: '1219', 'AN/UYK-43', 'AN/UYK-20', 'AN/AYK-14', '490', '494', '1107', '1108'
target_computer_profile = 'AN/UYK-43' 
univac_hal.clear_interlocks_for_model(target_computer_profile)

# ------------------------------------------------------------------------------
# ASYNCHRONOUS TRANSMISSION QUEUE (9600-Baud Trap Resolution)
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

    from control_core.cognitive_ring_processor import CognitiveRingProcessor

    # Initialize the independent asynchronous cognitive ring processor
    cognitive_plant = CognitiveRingProcessor(vessel_profile)
    cognitive_data_lock = threading.Lock()
    latest_cognitive_output = {}
    # Open your central '/src/main.py' script and navigate to your asynchronous cognitive loop worker:

    def asynchronous_cognitive_loop_worker():
    global latest_cognitive_output
    print("[BOOT] Isolated Cognitive Ring Thread successfully active.")
    
    # Import the newly developed diagnostic and vibration equations
    from control_core.museum_history_matrix import equation_body_vibration_resonance
    from control_core.museum_history_matrix import equation_adaptive_frequency_cancellation
    
    # Pre-seed mock vectors for the serial pattern detective check
    historical_noise_profile = [0.12, -0.05, 0.88, 0.41, -0.22]
    
    while True:
        # Pull safe thread-locked snapshots of active telemetry fields
        current_telemetry_snapshot = router.get_synchronized_telemetry()
        current_targets_snapshot = command_server.get_latest_targets()
        
        # 1. Execute cognitive, resonance, and financial calculations (from previous steps)
        # ... (Tesla tower, mimic decoy, and tactical risk indexes run here) ...
        
        # 2. NEW INJECTION: PROCESS PERIMETER VIBRATION AND PATTERN SEARCH MATRICES
        # Calculate localized deck vibration resonance values across crew quarters
        live_platform_stiffness = float(current_telemetry_snapshot.get('structural_stiffness_nm', 450000.0))
        live_platform_mass = float(vessel_profile.get('displacement_tonnes', 4500.0)) * 0.1 # local scale approximation
        
        calculated_deck_resonance_hz = equation_body_vibration_resonance(
            stiffness_n_m=live_platform_stiffness,
            structural_mass_kg=live_platform_mass
        )
        
        # Compute the active anti-phase hydraulic dampening output to stabilize the floor plane
        live_amplitude = float(current_telemetry_snapshot.get('roll_rate_rads', 0.0)) * 0.05 # amplitude proxy
        calculated_counter_force = equation_adaptive_frequency_cancellation(
            amplitude_m=live_amplitude,
            phase_rad=0.24,
            frequency_hz=calculated_deck_resonance_hz,
            elapsed_time=time.time()
        )
        
        # 3. Write results to the shared register via a fast memory thread-lock
        with cognitive_data_lock:
            latest_cognitive_output['deck_vibration_hz'] = calculated_deck_resonance_hz
            latest_cognitive_output['hydraulic_dampening_command_n'] = calculated_counter_force
            latest_cognitive_output['right_wrong_logic_nominal'] = True
            latest_cognitive_output['serial_pattern_match_ratio'] = 0.14 # Baseline low match ratio example
            
        time.sleep(0.05) # Maintain a steady 20Hz update pace for non-safety logic

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

    # ... Previous navigation, weapons balance, and anchor interlocks execute above ...

    # 1. Extract raw parameters from your central telemetry caches
    live_radar_freq = float(live_telemetry.get('enemy_radar_frequency_hz', 3e9))
    live_cargo_weight_kg = float(live_telemetry.get('crane_hoist_power_pct', 0.0)) * 50.0 # load scale proxy
            
    # 2. RUN THE RADAR & LEVITATION CALCULATIONS (50Hz Multi-Variable Plant)
    # AS SOON AS THE SYSTEM ENCOUNTERS INTERFERENCE, IT calculates cross-eye radar tricks
    # and inductive levitation force balances over the shared memory registers
    calculated_decoy_phase = bilge_gate_manager.equation_radar_crosseye_phase(
        jammer_baseline_m=12.5,     # 12.5-meter physical antennae spacing boundary
        target_range_m=15000.0,     # 15km threat tracker distance
        frequency_hz=live_radar_freq
    )
            
    required_lifting_current = bilge_gate_manager.equation_inductive_levitation_force(
        current_amps=float(live_telemetry.get('tesla_input_current_amps', 450.0)),
        coil_turns=1200,
        gap_distance_m=0.045,       # 45mm magnetic track levitation suspension gap
        area_m2=0.25
    )
            
    # Apply marine coral biofouling equations to adjust predicted fuel burn limits
    adjusted_hull_drag = bilge_gate_manager.equation_coral_drag_amplification(0.0045, 12.4, live_telemetry.get('speed_ms', 0.0))

    # 3. Append the calculated metrics directly to the outbound network monitoring package
    actuator_commands['upstream_autonomy_telemetry']['Advanced_Tricks'] = {
        "crosseye_radar_phase_shift_rad": round(calculated_decoy_phase, 4),
        "magnetic_levitation_lift_force_n": round(required_lifting_current, 1),
        "adjusted_biofouling_drag_coefficient": round(adjusted_hull_drag, 5)
    }
            
    # If the calculated drag coefficient spikes past safety boundaries, reduce allowed shaft ceilings
    if adjusted_hull_drag > 0.0085:
        actuator_commands['active_rpm_cap'] = min(actuator_commands['active_rpm_cap'], 450.0)
            
    # Poke your safety hardware watchdog to confirm the main loop is running smoothly
    watchdog.poke_watchdog('MAIN_CORE_MATH')

    # NEW: Shore Weapon System Serializer
    shore_weapon_link = ShoreWeaponSystemSerializer(prefix_code="PUNVC")
    shore_batteries_inventory = [
        {'shore_station_id': 'SHORE_BATTERY_ALPHA', 'umbilical_link_connected': False, 'navy_combat_release_cleared': False},
        {'shore_station_id': 'COASTAL_VLS_CELL_MATRIX', 'umbilical_link_connected': False, 'navy_combat_release_cleared': False}
    ]

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
        shore_weapon_serial_hardware_wire = serial.Serial('/dev/ttyUSB4', 9600, timeout=0) # Shore Link
    except serial.SerialException:
        print("[WARNING] Hardware serial ports not found. Running in simulation/headless mode.")
        steering_serial_hardware_wire, weapon_serial_hardware_wire, machinery_bus_serial_port, shore_weapon_serial_hardware_wire = None, None, None, None

            # ... Combined torque and steering control laws execute above ...
            
            # Extract calculated rudder command integer value
            target_rudder_integer = int(actuator_commands['command_rudder_angle_deg'] * 100)
            
            # Convert system integers back into big-endian byte blocks matching native limits
            native_wire_bytes, active_proto_string = univac_hal.unpack_64bit_to_native_bytes(target_rudder_integer)
            
            # Write the formatted byte string down the active RS-422 copper communication port
            try:
                machinery_bus_serial_port.write(native_wire_bytes)
            except NameError:
                pass

        # ... Read raw metrics strings from your serial or network input lines ...

        # Example: Ingest an integer target bearing word read off the legacy data bus
        raw_unmasked_bearing_word = int(live_telemetry.get('raw_bus_word_hex', "0x0000"), 16)

        # Sanitize the word frame instantly through the dynamic bit-width mask matrix
        # This ensures 16, 18, 30, 32, and 36-bit words all align perfectly to 64-bit software variables
        sanitized_target_word = univac_hal.pack_native_word_to_64bit(raw_unmasked_bearing_word)
    
        # Run calculations safely now that bit boundaries are perfectly matched
         actuator_commands = engine.execute_bridge_loop(active_targets, live_telemetry, dt)

    print("\n[BOOT] System initialization complete. Entering 50Hz real-time control matrix loop.")
    print("-" * 80)
    # --------------------------------------------------------------------------
    # HARD-REAL-TIME TIMING STACK (50Hz)
    # --------------------------------------------------------------------------
    loop_rate_hz = 50.0  
    dt = 1.0 / loop_rate_hz
    # ... Previous navigation, weapons balance, and anchor interlocks execute above ...

    # 1. Extract dynamic environmental inputs from your telemetry cache
    current_voyage_time_hours = (time.time() - start_cycle_time) / 3600.0
    live_lake_depth = float(live_telemetry.get('depth', 12.5))
            
    # 2. RUN THE HARMONIC TIDAL RESOLVER (50Hz Multi-Variable Plant)
    # AS SOON AS THE SHIP APPOACHES THE RESTRICTED CHANNEL, IT calculates the lake seiche period
    # and ocean tide heights to pre-compensate the keel clearance data logs
    calculated_seiche_window = bilge_gate_manager.equation_lake_seiche_period(
        basin_length_meters=8000.0,  # 8km Lake Washington tracking length
        average_depth_meters=live_lake_depth
    )
            
    simulated_tidal_shift_m = bilge_gate_manager.equation_ocean_harmonic_tide(
        time_hours=current_voyage_time_hours,
        amp_m2=1.4,                 # 1.4-meter principal semi-diurnal amplitude
        amp_s2=0.45                 # 0.45-meter solar amplitude
    )
            
    # Apply titanium hull yield limits to track structural safety bounds
    hull_crush_depth_m = bilge_gate_manager.equation_titanium_hull_collapse(850e6, 2.1, 1.95) / 10055.0

    # 3. Append the calculated metrics directly to the outbound network monitoring package
    actuator_commands['upstream_autonomy_telemetry']['Environmental_Tides'] = {
        "predicted_harmonic_tidal_height_m": round(simulated_tidal_shift_m, 2),
        "lake_seiche_resonance_period_sec": round(calculated_seiche_window, 1),
        "titanium_hull_collapse_depth_m": round(hull_crush_depth_m, 1)
    }
            
    # Update the central depth calculation log to account for dynamic tidal swells
    live_telemetry['depth'] += simulated_tidal_shift_m
            
    # Poke your safety hardware watchdog to confirm the main loop is running smoothly
    watchdog.poke_watchdog('MAIN_CORE_MATH')

    def asynchronous_cognitive_loop_worker():
    global latest_cognitive_output
    print("[BOOT] Isolated Cognitive Ring Thread successfully active.")
    while True:
        # Pull safe snapshots of active telemetry fields
        current_telemetry_snapshot = router.get_synchronized_telemetry()
        current_targets_snapshot = command_server.get_latest_targets()
        
        # Process the 15-node cognitive and resonance calculations independently
        calculated_results = cognitive_plant.process_cognitive_step(
            live_telemetry=current_telemetry_snapshot,
            active_targets=current_targets_snapshot,
            dt=0.05
        )
        
        # Write results to the shared register via a fast memory thread-lock
        with cognitive_data_lock:
            latest_cognitive_output = calculated_results.copy()
            
        time.sleep(0.05) # Maintain a steady 20Hz update pace for non-safety logic

        # Spin up the background worker thread before launching the 50Hz core navigation loop
        cog_thread = threading.Thread(target=asynchronous_cognitive_loop_worker, daemon=True)
        cog_thread.start()

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
            live_telemetry['roll_angle_rad'] += math.radians(weapon_imbalance['induced_roll_list_angle_deg'])

            # -- C. MASTER UNIVAC ENGINE LOOP --
            actuator_commands = engine.execute_bridge_loop(active_targets, live_telemetry, dt)
            actuator_commands['upstream_autonomy_telemetry']['Weapon_Balance_Metrics'] = weapon_imbalance
            slew_rate_cap = actuator_commands.get('active_rpm_cap', 5.0)

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

                        # ... Core navigation laws, warning gates, and asymmetric rudder trim loops execute above ...

            # Read the pre-calculated metrics from the asynchronous memory lock
            with cognitive_data_lock:
                active_cog_metrics = latest_cognitive_output.copy()

            # If the adaptive frequency compensator registers a severe, sustained structural vibration spike,
            # automatically engage protective speed caps to reduce hull slamming stresses:
            if active_cog_metrics.get('deck_vibration_hz', 0.0) >= 12.5: # Extreme structural vibration limit
                actuator_commands['active_rpm_cap'] = min(actuator_commands['active_rpm_cap'], 140.0)
                
            # Pass metrics down to the physical serial ports and append to outbound packets
            if active_cog_metrics:
                actuator_commands['upstream_autonomy_telemetry']['Diagnostic_Maintenance_Metrics'] = {
                    "measured_deck_resonance_hz": active_cog_metrics.get('deck_vibration_hz', 0.0),
                    "active_hydraulic_cancellation_force_n": active_cog_metrics.get('hydraulic_dampening_command_n', 0.0),
                    "serial_line_pattern_match_ratio": active_cog_metrics.get('serial_pattern_match_ratio', 0.0),
                    "right_wrong_decider_active": active_cog_metrics.get('right_wrong_logic_nominal', True)
                }
                
            # Poke your safety hardware watchdog to confirm the main loop is running smoothly
            watchdog.poke_watchdog('MAIN_CORE_MATH')

            # ... Core navigation laws and asymmetric rudder trim loops execute above ...

            # Read the pre-calculated metrics from the asynchronous memory lock
            with cognitive_data_lock:
                active_cog_metrics = latest_cognitive_output.copy()

            # If the legal matrix flags a boundary warning, automatically cap speed parameters
            if active_cog_metrics.get('legal_boundary_alert_active', False):
                actuator_commands['active_rpm_cap'] = min(actuator_commands['active_rpm_cap'], 150.0)
                
            # Pass Tesla tower and electronic decoy variables down to the hardware serial ports
            # Replace 'machinery_bus_serial_port' with your active physical port object handle
            if active_cog_metrics:
                tesla_power = active_cog_metrics.get('tesla_radiated_power_watts', 0.0)
                decoy_phase = active_cog_metrics.get('mimic_decoy_phase_shift_rad', 0.0)
                
                # Append metrics directly to the outbound network monitoring package
                actuator_commands['upstream_autonomy_telemetry']['Tesla_Resonance_Metrics'] = active_cog_metrics
                
            # Poke your safety hardware watchdog to confirm the main loop is running smoothly
            watchdog.poke_watchdog('MAIN_CORE_MATH')

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

            # 4. Asymmetric Roll Stabilizers
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

            # ──────────────────────────────────────────────────────────────────────────
            # 5. SHORE COMBAT INTERLOCK DISPATCH (NEW)
            # ──────────────────────────────────────────────────────────────────────────
            shore_link_connected = live_telemetry.get('shore_power_cable_attached', False)

            for battery in shore_batteries_inventory:
                battery['umbilical_link_connected'] = shore_link_connected
                battery['navy_combat_release_cleared'] = active_targets.get('navy_combat_release_cleared', False)

            if shore_link_connected:
                # The active_targets dict inherently replaces app.high_speed_numeric_buffer
                # and is already thread-locked inside the JsonTcpCommandListener block.
                ship_targeting_snapshot = active_targets.copy()
                
                shore_combat_packets = shore_weapon_link.serialize_shore_fire_commands(
                    high_speed_target_buffer=ship_targeting_snapshot,
                    active_shore_weapons=shore_batteries_inventory
                )
                
                # Sent through the isolated TX queue to protect the 50Hz timing!
                if shore_weapon_serial_hardware_wire:
                    for wire_frame in shore_combat_packets:
                        tx_queue.put_nowait((wire_frame, shore_weapon_serial_hardware_wire))
                
                watchdog.poke_watchdog('WEAPON_BUS_IN')
            # ──────────────────────────────────────────────────────────────────────────

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
