# File Name: bridge_execution_engine.py
# Location: Place this file in your bridge control source tree under '/src/control_core/'

import math
import numpy as np

class UnivacReplacementBridgeEngine:
    def __init__(self, vessel_profile: dict):
        """
        Initializes the unified, multi-variable bridge predictive engine.
        vessel_profile requires:
            'diameter': Propeller diameter (m)
            'inertia_prop': Shaft and propeller combined rotational inertia (kg*m^2)
            'inertia_roll': Mass moment of inertia about the roll X-axis (kg*m^2)
            'inertia_yaw': Mass moment of inertia about the yaw Z-axis (kg*m^2)
            'draft': Static vessel draft (m)
            'rudder_arm_z': Vertical distance from rudder center to center of gravity (m)
            'max_torque': Absolute peak motor torque capability (Nm)
            'max_rudder_deg': Mechanical physical hard stops of the rudder gear (degrees)
            'hull_length': Distance from forward monitoring array to stern (m)
        """
        self.p = vessel_profile
        self.rho = 1025.0  # Seawater density (kg/m^3)
        self.g = 9.81
        
        # State Vectors
        self.current_omega = 0.0
        self.past_elevations = [0.0] * 5
        self.ar_weights = np.array([0.85, -0.45, 0.20, -0.05, 0.01])
        
        # Tuning Gains
        self.Kp_speed = 220.0
        self.Kp_yaw = 1.8
        self.Kd_roll = 2.5
        self.K_bend = 0.012

    def _predict_wave_mechanics(self, telemetry: dict) -> tuple:
        """Calculates short-term deterministic wave arrival and stern water levels."""
        est_wave_freq = 0.85  # Rad/s, derived from hull cycle estimations
        k = (est_wave_freq ** 2) / self.g
        c_p = self.g / est_wave_freq
        
        # Dispersion delay time window
        denom = c_p + telemetry['speed_ms']
        lookahead_seconds = self.p['hull_length'] / denom if denom > 0.1 else 0.0
        
        # Autoregressive wave prediction projection
        self.past_elevations.pop(0)
        self.past_elevations.append(telemetry['bow_sensor_meters'])
        predicted_wave_shift = np.dot(self.ar_weights, np.array(self.past_elevations))
        
        predicted_submergence = 4.0 + predicted_wave_shift # 4.0m baseline depth
        
        # Compute ventilation factor
        if predicted_submergence >= self.p['diameter']:
            beta_v = 1.0
        elif predicted_submergence <= 0:
            beta_v = 0.05
        else:
            beta_v = math.sin((math.pi / 2.0) * (predicted_submergence / self.p['diameter'])) ** 2
            
        return beta_v, lookahead_seconds

    def _apply_shallow_water_enforcement(self, telemetry: dict, active_targets: dict) -> dict:
        """Predicts and enforces shallow water velocity caps and rudder slew rates."""
        clearance = telemetry['depth'] - self.p['draft']
        if clearance <= 0.2:
            clearance = 0.2  # Floor clearance value to prevent division by zero
        clearance_ratio = clearance / self.p['draft']
        
        omega_max_allowed = 125.0 * math.tanh(1.8 * clearance_ratio)
        rpm_max_allowed = (omega_max_allowed * 60.0) / (2 * math.pi)
        
        rudder_slew_rate_max = 15.0 * math.tanh(clearance_ratio)
        
        return {
            'safe_rpm_cap': max(20.0, rpm_max_allowed),
            'slew_rate_cap': max(2.0, rudder_slew_rate_max)
        }

    def execute_bridge_loop(self, targets: dict, telemetry: dict, dt: float) -> dict:
        """
        Executes a single hard-real-time tracking and protection loop cycle.
        Coordinates wave prediction, shallow depth capping, structural limits, and RRS.
        """
        self.current_omega = (telemetry['rpm'] * 2.0 * math.pi) / 60.0
        
        # 1. Run Environmental Fluid Layer
        beta_v, wave_warning_time = self._predict_wave_mechanics(telemetry)
        depth_limits = self._apply_shallow_water_enforcement(telemetry, targets)
        
        # 2. Dynamic Target Speed Saturation
        safe_target_rpm = min(targets['rpm'], depth_limits['safe_rpm_cap'])
        safe_target_omega = (safe_target_rpm * 2.0 * math.pi) / 60.0
        
        # 3. MIMO Rudder Roll Stabilization & Trajectory Control
        yaw_error = targets['target_yaw_rate'] - telemetry['yaw_rate_rads']
        delta_steering = self.Kp_yaw * yaw_error
        delta_stabilization = -self.Kd_roll * telemetry['roll_rate_rads']
        
        raw_rudder_deg = math.degrees(delta_steering + delta_stabilization)
        
        # Enforce speed-dependent maximum rudder angles to prevent hull snap-off
        rudder_max_allowed = self.p['max_rudder_deg'] * math.exp(-0.015 * abs(self.current_omega))
        safe_target_rudder = max(-rudder_max_allowed, min(rudder_max_allowed, raw_rudder_deg))
        
        # Apply shallow-water hydraulic slew rate cap
        rudder_error = safe_target_rudder - telemetry['rudder_deg']
        max_move_this_step = depth_limits['slew_rate_cap'] * dt
        actual_rudder_step = max(-max_move_this_step, min(max_move_this_step, rudder_error))
        final_rudder_pos = telemetry['rudder_deg'] + actual_rudder_step
        
        # 4. Coordinated Motor Torque Calculation & Power Shedding
        speed_error = safe_target_omega - self.current_omega
        base_feedback_torque = self.Kp_speed * speed_error
        
        # Preemptive Torque Drops (Maneuver load + shallow water clearance factor)
        clearance_factor = 1.0 + 0.6 * (self.p['draft'] / max(0.2, telemetry['depth'] - self.p['draft']))
        torque_shed_maneuver = 450.0 * abs(final_rudder_pos) * (self.current_omega ** 1.5) * clearance_factor
        
        # Wave ventilation power cut
        total_torque_demand = (base_feedback_torque * beta_v) - torque_shed_maneuver
        final_motor_torque = max(-self.p['max_torque'], min(self.p['max_torque'], total_torque_demand))
        
        # 5. Monitor Structural Stress Telemetry
        actual_moment = (self.K_bend * self.rho * (self.current_omega**2) * (self.p['diameter']**5) * abs(telemetry['yaw_rate_rads'])) + (self.p['inertia_prop'] * self.current_omega * abs(telemetry['yaw_rate_rads']))
        allowable_moment = 1500000.0 / 2.5 # Using 1.5M Nm design yield limit with 2.5x safety margin
        structural_load_pct = (actual_moment / allowable_moment) * 100.0
        
        return {
            'command_motor_torque_nm': round(final_motor_torque, 1),
            'command_rudder_angle_deg': round(final_rudder_pos, 2),
            'telemetry_structural_load_pct': round(structural_load_pct, 1),
            'telemetry_wave_lookahead_sec': round(wave_warning_time, 2),
            'active_rpm_cap': round(depth_limits['safe_rpm_cap'], 1)
        }

# Verification Execution Profile
if __name__ == "__main__":
    ship_profile = {
        'diameter': 3.4, 'inertia_prop': 500.0, 'inertia_roll': 850000.0, 'inertia_yaw': 4500000.0,
        'draft': 6.5, 'rudder_arm_z': 2.8, 'max_torque': 90000.0, 'max_rudder_deg': 35.0, 'hull_length': 45.0
    }
    
    engine = UnivacReplacementBridgeEngine(ship_profile)
    
    # Simulating an emergency coordinate turn while hitting a wave trough in shallow waters
    mock_telemetry = {'rpm': 520.0, 'rudder_deg': 12.0, 'depth': 8.2, 'bow_sensor_meters': -2.1, 'speed_ms': 7.2, 'yaw_rate_rads': 0.04, 'roll_rate_rads': 0.12}
    mock_targets = {'rpm': 600.0, 'target_yaw_rate': 0.08}
    
    output_commands = engine.execute_bridge_loop(mock_targets, mock_telemetry, dt=0.2)
    print("BRIDGE ENGINE STATUS OUTPUT COEFFICIENTS:")
    print(output_commands)
