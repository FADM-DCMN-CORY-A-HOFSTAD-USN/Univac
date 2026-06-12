#!/usr/bin/env python3
# File Name: bridge_execution_engine.py
# Location: /src/control_core/
# Subsystem: Unified Coordinated Propulsion & Steering Control Matrix
from src.control_core.inertial_dead_reckoning import InertialDeadReckoning
import math
import numpy as np
import time
from typing import Dict, Any

# ==============================================================================
# SUB-MODULE IMPORTS (75-Feature Architecture)
# ==============================================================================
try:
    from src.hydrodynamics.wave_matrix_processor import WaveParameterMatrix
    from src.hydrodynamics.bank_suction_lookup import BankSuctionLookupTable
    from src.control_core.univac_features_library import NAVMOD_Subsystem
    from src.control_core.hydro_coordinated_predictor import HydroCoordinatedPredictor
    from src.control_core.asymmetric_trim_subroutine import AsymmetricRudderTrimSubroutine
    from src.config.weapon_balance_matrix import NavalWeaponsBalanceMatrix
except ImportError as e:
    print(f"[WARNING] Sub-module import failed. Ensure /src/ directory is accessible. Error: {e}")

class UnivacReplacementBridgeEngine:
    """
    MASTER EXECUTION ENGINE: UNIVAC REPLACEMENT BRIDGE
    Synthesizes Aegis/Sea Machines target requests with physical hull limits.
    Incorporates all 75 features, including propeller diameter shear protection,
    rudder-length roll coupling, AR wave forecasting, and weapon cross-coupling.
    """
    def __init__(self, vessel_profile: Dict[str, float]):
        # 1. Exact Physical Vessel Dimensions (Crucial for Hydrodynamic Gating)
        self.D = float(vessel_profile.get('diameter', 3.4))
        self.J_prop = float(vessel_profile.get('inertia_prop', 500.0))
        self.draft = float(vessel_profile.get('draft', 6.5))
        self.max_torque = float(vessel_profile.get('max_torque', 90000.0))
        self.max_rudder_deg = float(vessel_profile.get('max_rudder_deg', 35.0))
        self.L_hull = float(vessel_profile.get('hull_length', 45.0))
        self.B_beam = float(vessel_profile.get('beam', 9.5))
        self.rudder_arm_z = float(vessel_profile.get('rudder_arm_z', 2.8))

        # Environmental Constants
        self.rho = 1025.0     # Seawater density (kg/m^3)
        self.g = 9.81         # Gravity (m/s^2)
        self.K_bend = 0.015   # Propeller asymmetric lift factor

        # 2. Instantiate UNIVAC Math Subsystems
        try:
            self.wave_matrix = WaveParameterMatrix(diameter=self.D, draft=self.draft)
            self.bank_suction = BankSuctionLookupTable(draft=self.draft, length=self.L_hull)
            self.hydro_predictor = HydroCoordinatedPredictor(
                diameter=self.D, inertia=self.J_prop, draft=self.draft, 
                max_torque=self.max_torque, max_rudder_deg=self.max_rudder_deg, kt=0.85
            )
            self.nav_mod = NAVMOD_Subsystem()
            self.trim_subroutine = AsymmetricRudderTrimSubroutine(vessel_profile)
            self.weapons_matrix = NavalWeaponsBalanceMatrix()
            self.dr_engine = InertialDeadReckoning()
            self.subsystems_online = True
        except NameError:
            self.subsystems_online = False
            print("[CRITICAL] Running in Safe-Mode. Advanced subsystems offline.")

        # --- FEATURE 40: AUTOREGRESSIVE SEAKEEPING BUFFER ---
        self.history_depth = 5
        self.elevation_history = np.zeros(self.history_depth)
        self.ar_weights = np.array([0.842, -0.441, 0.198, -0.048, 0.009])

        # --- FEATURE 43: ADAPTIVE STEERING NOTCH FILTER REGISTERS ---
        self.notch_x1 = 0.0
        self.notch_x2 = 0.0
        self.notch_y1 = 0.0
        self.notch_y2 = 0.0

        # --- INTERNAL CONTROLLER STATE REGISTERS ---
        self.integral_speed_error = 0.0
        self.current_accel = 0.0
        self.max_jerk = 5.0       # Max rate of change of acceleration (RPM/s^3)
        self.max_accel_lim = 50.0  # Max structural acceleration limit (RPM/s^2)
        self.current_ramp_rpm = 0.0
        self.current_rpm_state = 0.0

    # ==============================================================================
    # INTERNAL FEATURE ARRAYS: DETERMINISTIC MATH
    # ==============================================================================
    def _execute_s_curve_profile(self, target_rpm: float, current_rpm: float, dt: float) -> float:
        """S-Curve profile generator to smoothly ramp target RPM without steps."""
        if self.current_ramp_rpm == 0.0:
            self.current_ramp_rpm = current_rpm
            
        error = target_rpm - self.current_ramp_rpm
        if abs(error) < 0.1:
            self.current_accel = 0.0
            return target_rpm
            
        jerk_direction = 1.0 if error > 0 else -1.0
        self.current_accel += jerk_direction * self.max_jerk * dt
        self.current_accel = max(-self.max_accel_lim, min(self.max_accel_lim, self.current_accel))
        
        self.current_ramp_rpm += self.current_accel * dt
        return max(-200.0, min(1200.0, self.current_ramp_rpm))

    def _calculate_wave_ventilation(self, raw_bow_meters: float) -> float:
        """Features 40 & 41: Forecasts wave elevations and propeller ventilation loss."""
        self.elevation_history = np.roll(self.elevation_history, -1)
        self.elevation_history[-1] = raw_bow_meters
        pred_elevation = float(np.dot(self.ar_weights, self.elevation_history))
        
        nominal_shaft_depth = 3.5
        submergence = nominal_shaft_depth + pred_elevation
        if submergence >= self.D:
            return 1.0
        elif submergence <= 0.0:
            return 0.05
        else:
            return math.sin((math.pi / 2.0) * (submergence / self.D)) ** 2

    def _execute_feature_43_notch_filter(self, rudder_cmd_deg: float, dt: float) -> float:
        """FEATURE 43: Second-Order Bilinear Notch Filter to suppress wave noise."""
        w_wave = 0.82   # Target wave oscillation band (rad/s)
        zeta_1 = 0.05   # Narrow attenuation notch width
        zeta_2 = 0.70   # Broad tracking passband damping
        
        tan_coef = math.tan((w_wave * dt) / 2.0)
        
        b0 = 1.0 + (2.0 * zeta_1 * tan_coef) + (tan_coef ** 2)
        b1 = 2.0 * (tan_coef ** 2) - 2.0
        b2 = 1.0 - (2.0 * zeta_1 * tan_coef) + (tan_coef ** 2)
        
        a0 = 1.0 + (2.0 * zeta_2 * tan_coef) + (tan_coef ** 2)
        a1 = 2.0 * (tan_coef ** 2) - 2.0
        a2 = 1.0 - (2.0 * zeta_2 * tan_coef) + (tan_coef ** 2)
        
        filtered_rudder = (b0/a0)*rudder_cmd_deg + (b1/a0)*self.notch_x1 + (b2/a0)*self.notch_x2 - (a1/a0)*self.notch_y1 - (a2/a0)*self.notch_y2
        
        self.notch_x2 = self.notch_x1
        self.notch_x1 = rudder_cmd_deg
        self.notch_y2 = self.notch_y1
        self.notch_y1 = filtered_rudder
        return filtered_rudder

    def _enforce_propeller_shear_protection(self, target_yaw_rate: float, current_omega: float) -> float:
        """Propeller Diameter (D^5) Gyroscopic limits to prevent shaft snapping."""
        projected_bending_moment = self.K_bend * self.rho * (current_omega**2) * (self.D**5) * abs(target_yaw_rate)
        safety_factor = 0.85
        max_allowable_moment = self.max_torque * safety_factor
        
        if projected_bending_moment > max_allowable_moment and current_omega > 0.1:
            safe_yaw_rate = max_allowable_moment / (self.K_bend * self.rho * (current_omega**2) * (self.D**5))
            return math.copysign(safe_yaw_rate, target_yaw_rate)
        return target_yaw_rate

    def _calculate_rudder_roll_moment(self, actual_rudder_deg: float, speed_ms: float) -> float:
        """Uses Rudder Arm Z-Axis length to predict hull lean induced by steering."""
        rudder_area = 4.5 
        lift_coeff = 0.1 * actual_rudder_deg
        lateral_force = 0.5 * self.rho * (speed_ms**2) * rudder_area * lift_coeff
        return lateral_force * self.rudder_arm_z

    # ==============================================================================
    # MASTER EXECUTION LOOP (Runs at 10Hz - 50Hz)
    # ==============================================================================
    def execute_bridge_loop(self, targets: dict, telemetry: dict, dt: float) -> dict:
        """
        Executes a single hard-real-time multi-variable tracking cycle.
        Coordinates wave prediction, shallow depth capping, structural limits, and RRS.
        """
        current_rpm = telemetry.get('rpm', self.current_rpm_state)
        current_omega = (current_rpm * 2.0 * math.pi) / 60.0
        speed_ms = telemetry.get('speed_ms', 0.0)
        heading_rad = telemetry.get('heading_rad', 0.0)
        gps_valid = telemetry.get('gps_valid', True)

        # --- 0. SENSOR VALIDATION & INERTIAL DEAD RECKONING ---
        if gps_valid:
            self.last_known_lat_rad = telemetry.get('latitude_rad', self.last_known_lat_rad)
            self.last_known_lon_rad = telemetry.get('longitude_rad', self.last_known_lon_rad)
        else:
            if self.subsystems_online and hasattr(self, 'dr_engine'):
                new_lat, new_lon = self.dr_engine.feature_10_integrate_dr_position(
                    self.last_known_lat_rad, self.last_known_lon_rad, speed_ms, heading_rad, dt
                )
                self.last_known_lat_rad = new_lat
                self.last_known_lon_rad = new_lon
                # Overwrite telemetry so downstream math uses the projected DR coordinates
                telemetry['latitude_rad'] = new_lat
                telemetry['longitude_rad'] = new_lon

        # --- WEAPON CROSS-COUPLING ---
        if self.subsystems_online and 'gun_azimuth_deg' in telemetry:
            weapon_impact = self.weapons_matrix.evaluate_vessel_cross_coupling_impact(
                ship_class='DDG_ARLEIGH_BURKE',
                weapon_azimuth_deg=telemetry['gun_azimuth_deg'],
                weapon_elevation_deg=telemetry.get('gun_elevation_deg', 0.0),
                az_rate=telemetry.get('gun_azimuth_rate_rads', 0.0),
                el_rate=telemetry.get('gun_elevation_rate_rads', 0.0)
            )
            # Apply weapon's induced list angle to pre-compensate RRS matrices
            telemetry['roll_angle_rad'] = telemetry.get('roll_angle_rad', 0.0) + math.radians(weapon_impact.get('induced_roll_list_angle_deg', 0.0))

        # --- 1. SHALLOW WATER PROTECTION INTERLOCKS (Feature 16/20) ---
        clearance = max(0.1, telemetry.get('depth', 50.0) - self.draft)
        squat = 0.7 * ((speed_ms / 10.0) ** 2) * (1.0 + 0.1 * (self.draft / clearance))
        dynamic_draft = self.draft + squat
        
        fr_depth = speed_ms / math.sqrt(self.g * max(0.5, telemetry.get('depth', 50.0)))

        # Speed saturation constraint adjustment
        if fr_depth > 0.85:
            safe_target_rpm = min(targets.get('rpm', 0.0), 250.0)
            slowdown_active = True
        else:
            safe_target_rpm = targets.get('rpm', 0.0)
            slowdown_active = False

        # --- 2. ASYMMETRIC CANAL BANK STABILIZATION ---
        delta_trim_deg = 0.0
        bank_suction_force = 0.0
        if self.subsystems_online:
            trim_res = self.trim_subroutine.calculate_asymmetric_channel_trim(telemetry)
            delta_trim_deg = trim_res.get('asymmetric_trim_required_deg', 0.0)
            
            bank_data = self.bank_suction.evaluate_bank_forces(telemetry, dt)
            bank_suction_force = bank_data.get('feature_26_suction_force_n', 0.0)

        # --- 3. WAVE AND VENTILATION PLANT ENGINE ---
        # Run AR Predictor
        beta_v = self._calculate_wave_ventilation(telemetry.get('bow_sensor_meters', 0.0))
        if self.subsystems_online:
            wave_data = self.wave_matrix.process_wave_cycle(safe_target_rpm, targets.get('target_yaw_rate', 0.0), telemetry, dt)
            # Take the most conservative ventilation constraint
            beta_v = min(beta_v, wave_data.get('internal_ventilation_index', 1.0))

        # --- 4. CLOSED-LOOP PROPULSION EXECUTION ---
        profiled_target_rpm = self._execute_s_curve_profile(safe_target_rpm, current_rpm, dt)
        target_omega = (profiled_target_rpm * 2.0 * math.pi) / 60.0
        
        speed_error = target_omega - current_omega
        self.integral_speed_error += speed_error * dt
        
        base_torque = (220.0 * speed_error) + (10.0 * self.integral_speed_error)
        
        # Feature 42: Proactively attenuate torque if wave ventilation occurs at the stern
        coordinated_torque = base_torque * beta_v
        
        # Feature 26: Preemptive shedding for bank suction drag
        if bank_suction_force > 10000.0:
            coordinated_torque -= (bank_suction_force * 0.1)

        final_motor_torque = max(-self.max_torque, min(self.max_torque, coordinated_torque))

        # --- 5. CLOSED-LOOP STEERING GEAR EXECUTION ---
        raw_target_yaw_rate = targets.get('target_yaw_rate', 0.0)
        safe_yaw_rate = self._enforce_propeller_shear_protection(raw_target_yaw_rate, current_omega)

        # Coordinated Law: Low-Frequency Trajectory + High-Frequency Roll Damping
        delta_steering = 1.8 * (safe_yaw_rate - telemetry.get('yaw_rate_rads', 0.0))
        delta_stabilization = -2.5 * telemetry.get('roll_rate_rads', 0.0)
        
        combined_rudder_deg = math.degrees(delta_steering + delta_stabilization)

        # Apply the newly unlocked Coriolis calculation
        coriolis_trim = self.nav_mod.feature_14_coriolis_drift_compensation(telemetry['latitude'], speed_ms)

        # Add it to the final output
        asymmetric_stabilized_rudder_deg = combined_rudder_deg + delta_trim_deg + coriolis_trim

        asymmetric_stabilized_rudder_deg = combined_rudder_deg + delta_trim_deg
        
        # Feature 43: Clear out high-frequency wave-slap hydraulic oscillations
        notch_filtered_rudder = self._execute_feature_43_notch_filter(asymmetric_stabilized_rudder_deg, dt)
        
        # Feature 65: Apply Speed-Dependent Rudder Angle Saturation Cap
        rudder_cap = self.max_rudder_deg * math.exp(-0.015 * abs(current_omega))
        final_rudder_pos = max(-rudder_cap, min(rudder_cap, notch_filtered_rudder))

        predicted_roll_moment = self._calculate_rudder_roll_moment(final_rudder_pos, speed_ms)

        # --- 6. STRUCTURAL TRACKING CHECK MATRIX ---
        m_bend = self.K_bend * self.rho * (current_omega ** 2) * (self.D ** 5) * telemetry.get('yaw_rate_rads', 0.0)
        m_gyro = self.J_prop * current_omega * telemetry.get('yaw_rate_rads', 0.0)
        m_total_structural = abs(m_bend) + abs(m_gyro)
        
        allowable_moment = 1500000.0 / 2.5
        structural_load_pct = (m_total_structural / allowable_moment) * 100.0

        self.current_rpm_state = current_rpm

        # Compile interface packet structures
        upstream_autonomy_packet = {
            "UNIVAC_Water_Insight_Link": {
                "subsurface_ventilation_index": round(beta_v, 3),
                "predicted_keel_clearance_meters": round(telemetry.get('depth', 50.0) - dynamic_draft, 2),
                "structural_fatigue_load_percentage": round(structural_load_pct, 1),
                "asymmetric_channel_trim_applied_deg": round(delta_trim_deg, 2),
                "predicted_rudder_roll_moment_nm": round(predicted_roll_moment, 1),
                "structural_yaw_override_active": abs(raw_target_yaw_rate - safe_yaw_rate) > 0.01
            }
        }
        
        return {
            "command_motor_torque_nm": round(final_motor_torque, 1),
            "command_rudder_angle_deg": round(final_rudder_pos, 2),
            "active_structural_moment_nm": round(m_total_structural, 1),
            "active_rpm_cap": round(profiled_target_rpm, 1),
            "shallow_water_slowdown_active": slowdown_active,
            "upstream_autonomy_telemetry": upstream_autonomy_packet
        }

# ==============================================================================
# VERIFICATION EXECUTION PROFILE
# ==============================================================================
if __name__ == "__main__":
    vessel_config = {
        'diameter': 3.4, 'inertia_prop': 500.0, 'draft': 6.5, 
        'max_torque': 90000.0, 'max_rudder_deg': 35.0, 
        'hull_length': 45.0, 'beam': 9.5, 'rudder_arm_z': 2.8
    }
    
    print("=====================================================================")
    print("UNIVAC REPLACEMENT BRIDGE COGNITIVE MATRIX ONLINE")
    print("=====================================================================\n")
    
    engine = UnivacReplacementBridgeEngine(vessel_config)
    
    # Testing combined stress profiles: Cruising at 500 RPM near a canal bank while 
    # firing the Mk 92 gun system in rough shallow water.
    telemetry_sample = {
        'rpm': 500.0, 'depth': 7.8, 'speed_ms': 7.5, 'bow_sensor_meters': -1.9,
        'yaw_rate_rads': 0.04, 'roll_angle_rad': 0.08, 'roll_rate_rads': 0.14,
        'distance_to_bank_meters': 14.5, 'rudder_deg': 5.0,
        'gun_azimuth_deg': 45.0, 'gun_elevation_deg': 10.0,
        'gun_azimuth_rate_rads': 0.1, 'gun_elevation_rate_rads': 0.05
    }
    target_sample = {'rpm': 550.0, 'target_yaw_rate': 0.15}
    
    commands = engine.execute_bridge_loop(target_sample, telemetry_sample, dt=0.1)
    
    print(f"Motor Torque Command:  {commands['command_motor_torque_nm']} Nm")
    print(f"Rudder Angle Command:  {commands['command_rudder_angle_deg']} Degrees\n")
    print(">> UPSTREAM TELEMETRY TO SEA MACHINES/AEGIS:")
    for key, val in commands['upstream_autonomy_telemetry']['UNIVAC_Water_Insight_Link'].items():
        print(f" - {key.replace('_', ' ').title()}: {val}")
    print("\n=====================================================================")
