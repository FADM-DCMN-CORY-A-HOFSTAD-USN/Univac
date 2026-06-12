# File Name: bilge_gating_subroutine.py
# Location: /src/control_core/
# Subsystem: Environmental Bilge Water Discharge Gating & OCM Interlock

import math
import time
from typing import Dict, Any

class BilgeWaterEnvironmentalGatingSubroutine:
    def __init__(self, critical_oil_threshold_ppm: float = 14.8):
        """
        Initializes the bilge pumping environmental gate.
        critical_oil_threshold_ppm: Safety ceiling below the legal 15.0 PPM limit (default 14.8).
        """
        self.ppm_limit = critical_oil_threshold_ppm
        
        # Valid States: "SECURED", "DISCHARGING_OVERBOARD", "RECIRCULATING_FAULT"
        self.valve_state = "SECURED"
        self.total_liters_discharged = 0.0
        self.last_execution_time = time.time()

    def evaluate_discharge_safety_matrix(self, telemetry: dict, ocm_ppm_sensor: float) -> dict:
        """
        Processes oil concentration measurements alongside hull roll/pitch acceleration.
        Controls the overboard three-way valve to prevent illegal oil discharge.
        """
        current_time = time.time()
        dt = current_time - self.last_execution_time
        self.last_execution_time = current_time

        roll_rate = abs(telemetry.get('roll_rate_rads', 0.0))
        pitch_angle = abs(telemetry.get('pitch_angle_rad', 0.0)) # Needs pitch to map slosh
        bilge_pump_active = telemetry.get('bilge_pump_active_relay', False)

        # Fluid Dynamics Sloshing Risk Index:
        # Rapid hull motion disrupts oily-water separators, causing pocket oil to bypass filters.
        is_sloshing_severe = (roll_rate > 0.12) or (pitch_angle > 0.08)

        # --- ENVIRONEMENTAL GATING STATE MACHINE ---
        if not bilge_pump_active:
            self.valve_state = "SECURED"
            overboard_valve_open = 0
            recirc_valve_open = 0
            action_msg = "Pumping inactive. Overboard discharge lines closed."
        else:
            if ocm_ppm_sensor >= self.ppm_limit:
                # HARD ENVIRONMENTAL INTERLOCK: Force instant valve closure
                self.valve_state = "RECIRCULATING_FAULT"
                overboard_valve_open = 0
                recirc_valve_open = 1 # Open route back to the slop holding tank
                action_msg = f"CRITICAL FAULT: Bilge oil at {ocm_ppm_sensor:.2f} PPM. Recirculation locked."
            elif is_sloshing_severe and ocm_ppm_sensor > 8.0:
                # PROACTIVE HOLD: Oil is below 15 PPM, but heavy hull movement risks a spike.
                self.valve_state = "RECIRCULATING_FAULT"
                overboard_valve_open = 0
                recirc_valve_open = 1
                action_msg = "WARNING: Heavy hull sloshing detected. Holding overboard discharge."
            else:
                # ENVIRONMENTALLY SAFE: Discharge to sea allowed
                self.valve_state = "DISCHARGING_OVERBOARD"
                overboard_valve_open = 1
                recirc_valve_open = 0
                action_msg = f"NOMINAL: Discharging clean water ({ocm_ppm_sensor:.2f} PPM)."
                
                # Accrue total volume metrics (Assuming standard 5.0 Liters/second pump capacity)
                self.total_liters_discharged += 5.0 * dt

        return {
            "gating_valve_state_string": self.valve_state,
            "actuator_overboard_valve_open": overboard_valve_open,
            "actuator_recirculation_valve_open": recirc_valve_open,
            "total_clean_water_discharged_liters": round(self.total_liters_discharged, 1),
            "telemetry_log_message": action_msg
        }

# Verification Execution Profile
if __name__ == "__main__":
    gating_system = BilgeWaterEnvironmentalGatingSubroutine()
    
    print("TESTING ENVIRONMENTAL BILGE WATER OVERBOARD DISCHARGE INTERLOCKS:")
    print("=" * 75)
    
    # Test 1: Pump active, water is clean, hull is sitting stable at the pier
    mock_telemetry_calm = {'roll_rate_rads': 0.01, 'pitch_angle_rad': 0.0, 'bilge_pump_active_relay': True}
    res_1 = gating_system.evaluate_discharge_safety_matrix(mock_telemetry_calm, ocm_ppm_sensor=3.2)
    print(f"Test 1 -> State: {res_1['gating_valve_state_string']} | Msg: {res_1['telemetry_log_message']}")
    
    # Test 2: Storm hits, water is at 9.5 PPM, but heavy hull rolling creates an immediate sloshing risk
    mock_telemetry_storm = {'roll_rate_rads': 0.15, 'pitch_angle_rad': 0.02, 'bilge_pump_active_relay': True}
    res_2 = gating_system.evaluate_discharge_safety_matrix(mock_telemetry_storm, ocm_ppm_sensor=9.5)
    print(f"Test 2 -> State: {res_2['gating_valve_state_string']} | Msg: {res_2['telemetry_status_message' if 'telemetry_status_message' in res_2 else 'telemetry_log_message']}")
    
    # Test 3: Oil Concentration spikes past the absolute regulatory legal limit
    res_3 = gating_system.evaluate_discharge_safety_matrix(mock_telemetry_calm, ocm_ppm_sensor=16.4)
    print(f"Test 3 -> State: {res_3['gating_valve_state_string']} | Msg: {res_3['telemetry_log_message']}")
