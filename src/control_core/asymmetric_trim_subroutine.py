# File Name: asymmetric_trim_subroutine.py
# Location: /src/control_core/
# Subsystem: Hydrodynamic Asymmetric Rudder-Trim Control Subroutine

import math
from typing import Dict, Any

class AsymmetricRudderTrimSubroutine:
    def __init__(self, physical_params: dict):
        """
        Initializes the asymmetric rudder-trim plant.
        physical_params requires:
            'hull_length': Total length of the ship hull (m)
            'beam': Total breadth/width of the vessel hull (m)
            'draft': Current structural operating draft (m)
            'max_rudder_deg': Mechanical physical hard stops of the rudder gear
        """
        self.L = float(physical_params['hull_length'])
        self.B = float(physical_params['beam'])
        self.T = float(physical_params['draft'])
        self.max_rudder = float(physical_params['max_rudder_deg'])
        
        self.rho = 1025.0    # Density of seawater (kg/m^3)
        self.N_delta = 0.045 # Rudder control authority lift coefficient

    def calculate_asymmetric_channel_trim(self, telemetry: dict) -> dict:
        """
        Calculates the required feedforward rudder trim bias to safely 
        neutralize bank suction and cushion forces inside narrow channels.
        """
        speed_ms = max(0.1, telemetry.get('speed_ms', 0.0))
        depth = telemetry.get('depth', 50.0)
        dist_bank = telemetry.get('distance_to_bank_meters', 100.0)
        bank_side = telemetry.get('bank_lateral_side', 'starboard') # 'port' or 'starboard'
        
        # 1. Evaluate shallow water restriction parameters (Feature 16 / 20)
        clearance = max(0.2, depth - self.T)
        clearance_ratio = clearance / self.T
        
        # 2. Extract asymmetric hydrodynamic lift profile (Feature 26/27 Boundary Model)
        # Force amplification scales exponentially as the hull approaches the wall boundary
        distance_ratio = dist_bank / self.B
        
        if distance_ratio >= 4.0 or dist_bank > 40.0:
            # Open water boundary: asymmetric interactions are mathematically negligible
            return self._compile_nominal_report()
            
        # Empirical scaling factor representing boundary layer suction profile intensity
        c_n_base = 0.035 * math.exp(-0.85 * distance_ratio)
        shallow_amplification = 1.0 + 0.6 * (1.0 / math.tanh(clearance_ratio))
        c_n_dynamic = c_n_base * shallow_amplification
        
        # Compute total predicted turning moment: N_bank = 0.5 * C_N * rho * V^2 * L^2 * T
        dynamic_pressure = 0.5 * self.rho * (speed_ms ** 2)
        predicted_bank_moment_nm = c_n_dynamic * dynamic_pressure * (self.L ** 2) * self.T
        
        # 3. Invert fluid models to find the matching stabilization rudder angle (Trim Bias)
        # Torque balanced: delta_trim = N_bank / (0.5 * rho * V^2 * L^2 * T * N_delta)
        denom = dynamic_pressure * (self.L ** 2) * self.T * self.N_delta
        raw_trim_rad = predicted_bank_moment_nm / denom if denom > 0.01 else 0.0
        raw_trim_deg = math.degrees(raw_trim_rad)
        
        # 4. Directional orientation balancing mapping
        # If bank is to Starboard, bow is cushioned to Port. Rudder must trim to Starboard (+) to counter.
        # If bank is to Port, bow is cushioned to Starboard. Rudder must trim to Port (-) to counter.
        if bank_side == 'starboard':
            final_trim_deg = raw_trim_deg
            induced_moment = -predicted_bank_moment_nm
        else:
            final_trim_deg = -raw_trim_deg
            induced_moment = predicted_bank_moment_nm
            
        # Clamp trim allocation to maximum 45% of mechanical steering gear availability
        trim_limit = self.max_rudder * 0.45
        clamped_trim_deg = max(-trim_limit, min(trim_limit, final_trim_deg))
        
        return {
            "asymmetric_trim_required_deg": round(clamped_trim_deg, 2),
            "predicted_bank_moment_nm": round(induced_moment, 1),
            "boundary_severity_index": round(min(1.0, abs(clamped_trim_deg / trim_limit)), 3),
            "autopilot_safety_override": True if abs(clamped_trim_deg) >= (trim_limit * 0.8) else False
        }

    def _compile_nominal_report(self) -> dict:
        """Returns flat baseline data when outside narrow channel boundaries."""
        return {
            "asymmetric_trim_required_deg": 0.0,
            "predicted_bank_moment_nm": 0.0,
            "boundary_severity_index": 0.0,
            "autopilot_safety_override": False
        }

# Verification Execution Profile
if __name__ == "__main__":
    # Load 45-meter Arleigh Burke replacement hull parameters matrix
    vessel_specs = {'hull_length': 45.0, 'beam': 9.5, 'draft': 3.2, 'max_rudder_deg': 35.0}
    subroutine = AsymmetricRudderTrimSubroutine(vessel_specs)
    
    # Mission Test Vector: Vessel traveling at 10 knots (5.14 m/s) inside a narrow channel.
    # Telemetry registers the starboard wall has closed in to only 8.5 meters away.
    # Seafloor depth has dropped down to 4.5 meters (Shallow boundary ratio ~1.4).
    mock_channel_telemetry = {
        'speed_ms': 5.14,
        'depth': 4.5,
        'distance_to_bank_meters': 8.5,
        'bank_lateral_side': 'starboard'
    }
    
    trim_packet = subroutine.calculate_asymmetric_channel_trim(mock_channel_telemetry)
    
    print("UNIVAC ASYMMETRIC RUDDER-TRIM CALCULATION RESULTS:")
    print("-" * 65)
    print(f"Calculated Hydrodynamic Bank Moment: {trim_packet['predicted_bank_moment_nm']} Nm")
    print(f"Dispatched Feedforward Trim Bias:    {trim_packet['asymmetric_trim_required_deg']} Degrees")
    print(f"Autopilot Channel Safety Override:   {trim_packet['autopilot_safety_override']}")
