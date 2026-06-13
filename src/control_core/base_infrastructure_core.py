# File Name: base_infrastructure_core.py
# Location: /src/control_core/
# Subsystem: Shore Facility Auxiliaries & Base Infrastructure Control Multiplexer

import time
import threading
from typing import Dict, Any

class UnivacBaseInfrastructureCore:
    def __init__(self):
        """
        Initializes the shore facilities automation routing engine.
        Tracks cranes, heavy doors, grid breakers, pump states, and HVAC zones.
        """
        self.lock = threading.Lock()
        
        # Valid Management Modes: "UNIVAC_DIRECT", "NETWORK_OVERRIDE"
        self.active_routing_mode = "UNIVAC_DIRECT"
        
        # --- SHORE FACILITY ACTUATOR REGISTER STATES ---
        self.base_telemetry_cache = {
            'crane_hoist_power_pct': 0.0,
            'crane_hook_lock_solenoid': 1,      # 1 = Mechanically Locked/Secured
            'blast_door_actuator_state': 0,     # 0 = Sealed/Closed, 1 = Opening
            'substation_breaker_relay': 1,      # 1 = Grid Energized, 0 = Shed Load
            'sump_pump_override_relay': 0,      # 1 = Force Drain On, 0 = Off
            'hvac_dehumidifier_setpoint': 45.0,  # Relative Humidity % Target
            'climate_heating_valve_open': 0     # 0 = Secured, 1 = Supplying Heat
        }
        
        self.last_update_time = time.time()

    def set_base_routing_authority(self, requested_mode: str) -> tuple:
        """Changes the system's operational routing authority context on the fly."""
        sanitized = requested_mode.upper().strip()
        if sanitized in ["UNIVAC_DIRECT", "NETWORK_OVERRIDE"]:
            with self.lock:
                if self.active_routing_mode != sanitized:
                    self.active_routing_mode = sanitized
                    self.last_update_time = time.time()
                return True, f"BASE INFRASTRUCTURE CONTROL ROUTED TO: {sanitized}"
        return False, f"REJECTED: Invalid base authority mode code: '{requested_mode}'"

    def execute_infrastructure_update_step(self, network_commands: dict, legacy_mainframe_inputs: dict) -> dict:
        """
        Synchronously multiplexes incoming commands to target the physical base actuators.
        Guarantees clear, single-source authority over heavy facility utilities.
        """
        with self.lock:
            mode = self.active_routing_mode
            
        # Isolate inputs based on active hardware routing gates
        if mode == "NETWORK_OVERRIDE":
            active_input_source = network_commands
            source_string = "NETWORK_REMOTE_CONSOLE"
        else:
            active_input_source = legacy_mainframe_inputs
            source_string = "UNIVAC_MAINFRAME_PASS_THROUGH"

        # Safe extraction and bounding of physical engineering parameters
        resolved_crane_power = max(-100.0, min(100.0, float(active_input_source.get('crane_hoist_power_pct', 0.0))))
        resolved_hook_lock = 1 if int(active_input_source.get('crane_hook_lock_solenoid', 1)) != 0 else 0
        resolved_blast_door = 1 if int(active_input_source.get('blast_door_actuator_state', 0)) != 0 else 0
        resolved_breaker = 1 if int(active_input_source.get('substation_breaker_relay', 1)) != 0 else 0
        resolved_sump = 1 if int(active_input_source.get('sump_pump_override_relay', 0)) != 0 else 0
        resolved_dehumidifier = max(20.0, min(85.0, float(active_input_source.get('hvac_dehumidifier_setpoint', 45.0))))
        resolved_heat_valve = 1 if int(active_input_source.get('climate_heating_valve_open', 0)) != 0 else 0

        # Update core tracking variables thread-safely
        with self.lock:
            self.base_telemetry_cache = {
                'crane_hoist_power_pct': resolved_crane_power,
                'crane_hook_lock_solenoid': resolved_hook_lock,
                'blast_door_actuator_state': resolved_blast_door,
                'substation_breaker_relay': resolved_breaker,
                'sump_pump_override_relay': resolved_sump,
                'hvac_dehumidifier_setpoint': resolved_dehumidifier,
                'climate_heating_valve_open': resolved_heat_valve
            }
            
        return {
            "active_authority_mode": mode,
            "resolved_infrastructure_source": source_string,
            "dispatched_actuator_cache": self.base_telemetry_cache.copy(),
            "timestamp_resolved": time.time()
        }

    def get_infrastructure_snapshot(self) -> dict:
        """Safe thread-locked interface to pass active base parameters down the line."""
        with self.lock:
            return self.base_telemetry_cache.copy()

# Verification Verification Run Environment
if __name__ == "__main__":
    base_engine = UnivacBaseInfrastructureCore()
    print("TESTING CO-PROCESSOR SHORE BASE INFRASTRUCTURE MATRIX ENGINE:")
    print("=" * 75)
    
    # Setup competing inputs: Mainframe runs standard profiles, Network requests an emergency override dump
    mock_mainframe = {'crane_hoist_power_pct': 0.0, 'substation_breaker_relay': 1, 'sump_pump_override_relay': 0, 'hvac_dehumidifier_setpoint': 45.0}
    mock_network = {'crane_hoist_power_pct': -50.0, 'substation_breaker_relay': 1, 'sump_pump_override_relay': 1, 'hvac_dehumidifier_setpoint': 30.0}
    
    # 1. Default Verification: Ensure baseline is mainframe pass-through
    res_1 = base_engine.execute_infrastructure_update_step(mock_network, mock_mainframe)
    print(f"Default Status -> Source: {res_1['resolved_infrastructure_source']}")
    print(f"Actuator Map   -> Sump Pump: {res_1['dispatched_actuator_cache']['sump_pump_override_relay']} | Crane Hoist: {res_1['dispatched_actuator_cache']['crane_hoist_power_pct']}%")
    
    # 2. Shift control on the fly to the Remote Network Console
    success, msg = base_engine.set_base_routing_authority("NETWORK_OVERRIDE")
    print(f"\nCommand Matrix Action: {msg}")
    
    res_2 = base_engine.execute_infrastructure_update_step(mock_network, mock_mainframe)
    print(f"Override Status -> Source: {res_2['resolved_infrastructure_source']}")
    print(f"Actuator Map    -> Sump Pump: {res_2['dispatched_actuator_cache']['sump_pump_override_relay']} | Crane Hoist: {res_2['dispatched_actuator_cache']['crane_hoist_power_pct']}%")
