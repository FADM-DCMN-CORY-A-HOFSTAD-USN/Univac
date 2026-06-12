#!/usr/bin/env python3
# File Name: bridge_execution_engine.py
# Location: / (Root Directory of Univac-Aegis-Bridge)

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
    from hydro_coordinated_predictor import HydroCoordinatedPredictor
except ImportError as e:
    print(f"[WARNING] Sub-module import failed. Ensure /src/ directory is accessible. Error: {e}")

class UnivacReplacementBridgeEngine:
from control_core.asymmetric_trim_subroutine import AsymmetricRudderTrimSubroutine

# Inside your UnivacReplacementBridgeEngine __init__:
self.trim_subroutine = AsymmetricRudderTrimSubroutine(vessel_profile)

    """
    MASTER EXECUTION ENGINE: UNIVAC REPLACEMENT BRIDGE
    Synthesizes Aegis/Sea Machines target requests with physical hull limits.
    Incorporates all 75 features, including propeller diameter shear protection
    and rudder-length roll coupling.
    """
# Create an instance of the weapons matrix inside your main bootstrap launcher:
from src.config.weapon_balance_matrix import NavalWeaponsBalanceMatrix
weapons_matrix = NavalWeaponsBalanceMatrix()

# Inside your 50Hz execution loop thread, ingest live weapon telemetry strings:
weapon_impact = weapons_matrix.evaluate_vessel_cross_coupling_impact(
    ship_class='DDG_ARLEIGH_BURKE',
    weapon_azimuth_deg=telemetry['gun_azimuth_deg'],
    weapon_elevation_deg=telemetry['gun_elevation_deg'],
    az_rate=telemetry['gun_azimuth_rate_rads'],
    el_rate=telemetry['gun_elevation_rate_rads']
)

# Apply the weapon's induced list angle directly as an addition to your live roll sensors
# to ensure the Rudder Roll Stabilization (RRS) matrices pre-compensate for the gun's weight:
telemetry['roll_angle_rad'] += math.radians(weapon_impact['induced_roll_list_angle_deg'])
    
    def __init__(self, vessel_profile: Dict[str, float]):
        # 1. Exact Physical Vessel Dimensions (Crucial for Hydrodynamic Gating)
        self.D = vessel_profile.get('diameter', 3.4)                  # Propeller Diameter (Meters)
        self.draft = vessel_profile.get('draft', 6.5)                 # Static Draft (Meters)
        self.hull_length = vessel_profile.get('hull_length', 45.0)    # Length overall (Meters)
        self.rudder_arm_z = vessel_profile.get('rudder_arm_z', 2.8)   # Distance from Center of Gravity to Rudder Center of Effort (Meters)
        
        # 2. Structural Yields & Inertia
        self.J_prop = vessel_profile.get('inertia_prop', 500.0)       # Shaft Inertia
        self.max_yield_torque = vessel_profile.get('max_torque', 90000.0)
        self.max_rudder_deg = vessel_profile.get('max_rudder_deg', 35.0)
        self.rho = 1025.0  # Saltwater density (kg/m^3)
        
        # 3. Instantiate UNIVAC Math Subsystems
        try:
            self.wave_matrix = WaveParameterMatrix(diameter=self.D, draft=self.draft)
            self.bank_suction = BankSuctionLookupTable(draft=self.draft, length=self.hull_length)
            self.hydro_predictor = HydroCoordinatedPredictor(
                diameter=self.D, inertia=self.J_prop, draft=self.draft, 
                max_torque=self.max_yield_torque, max_rudder_deg=self.max_rudder_deg, kt=0.85
            )
            self.nav_mod = NAVMOD_Subsystem()
            self.subsystems_online = True
        except NameError:
            self.subsystems_online = False
            print("[CRITICAL] Running in Safe-Mode. Advanced subsystems offline.")

        # Engine State Tracking
        self.current_rpm = 0.0
        self.current_rudder = 0.0

    # ==============================================================================
    # INTERNAL FEATURE: PROPELLER DIAMETER BENDING MOMENT CLAMP
    # ==============================================================================
    def _enforce_propeller_shear_protection(self, target_yaw_rate: float, current_omega: float) -> float:
        """
        Uses Propeller Diameter (D^5) to calculate asymmetrical lift during a turn.
        Prevents the propeller from snapping off if Aegis commands a sharp turn at high RPM.
        """
        # Kbend is a generic hydrodynamic lift coefficient for the blade foil
        k_bend = 0.015 
        
        # M_bend = K * rho * omega^2 * D^5 * yaw_rate
        # Notice how D^5 makes propeller diameter the most critical factor in shaft safety
        projected_bending_moment = k_bend * self.rho * (current_omega**2) * (self.D**5) * abs(target_yaw_rate)
        
        safety_factor = 0.85
        max_allowable_moment = self.max_yield_torque * safety_factor
        
        if projected_bending_moment > max_allowable_moment:
            # Calculate the mathematically maximum safe yaw rate for this specific RPM and Propeller Diameter
            safe_yaw_rate = max_allowable_moment / (k_bend * self.rho * (current_omega**2) * (self.D**5))
            return math.copysign(safe_yaw_rate, target_yaw_rate)
        
        return target_yaw_rate

    # ==============================================================================
    # INTERNAL FEATURE: RUDDER LENGTH ROLL COUPLING
    # ==============================================================================
    def _calculate_rudder_roll_moment(self, actual_rudder_deg: float, speed_ms: float) -> float:
        """
        Uses the Rudder Arm Z-Axis length to predict how much the hull will lean 
        when the rudder bites into the water.
        """
        rudder_area = 4.5 # Sq meters, parameterized 
        lift_coeff = 0.1 * actual_rudder_deg # Simplified linear lift curve
        
        lateral_force = 0.5 * self.rho * (speed_ms**2) * rudder_area * lift_coeff
        
        # Moment = Force * Distance (Rudder Arm Length from CG)
        roll_moment_nm = lateral_force * self.rudder_arm_z
        return roll_moment_nm

    # ==============================================================================
    # MASTER EXECUTION LOOP (Runs at 10Hz - 50Hz)
    # ==============================================================================
    def execute_bridge_loop(self, autonomy_targets: Dict[str, float], telemetry: Dict[str, float], dt: float) -> Dict[str, Any]:
        """
        The central multi-rate matrix. Ingests targets, runs 75-feature physics math, 
        and outputs raw torque and angle commands for the serial hardware.
        """
        # 1. Unpack Current State
        current_rpm = telemetry.get('rpm', self.current_rpm)
        current_omega = (current_rpm * 2.0 * math.pi) / 60.0
        depth = telemetry.get('depth', 50.0)
        speed_ms = telemetry.get('speed_ms', 0.0)
        
        # 2. Extract Requested Targets (From Aegis or Autopilot)
        requested_rpm = autonomy_targets.get('rpm', current_rpm)
        requested_yaw_rate = autonomy_targets.get('target_yaw_rate', 0.0)

        # ----------------------------------------------------------------------
        # STAGE 1: ENVIRONMENTAL MODIFIERS (Waves & Boundaries)
        # ----------------------------------------------------------------------
        ventilation_beta = 1.0
        wave_notch_rudder = requested_yaw_rate
        autopilot_trim = 0.0
        
        if self.subsystems_online:
            # Feature 26-27: Bank Suction & Cushion 
            bank_data = self.bank_suction.evaluate_bank_forces(telemetry, dt)
            autopilot_trim = bank_data.get('suggested_autopilot_counter_rudder_deg', 0.0)
            
            # Feature 40-43: Autoregressive Wave Protection
            wave_data = self.wave_matrix.process_wave_cycle(requested_rpm, requested_yaw_rate, telemetry, dt)
            ventilation_beta = wave_data.get('internal_ventilation_index', 1.0)
            wave_notch_rudder = wave_data.get('command_rudder_angle_deg', requested_yaw_rate)

        # ----------------------------------------------------------------------
        # STAGE 2: PHYSICAL HULL STRUCTURAL GATING
        # ----------------------------------------------------------------------
        # Apply Propeller Diameter (D^5) Gyroscopic/Bending limit to the requested turn
        safe_yaw_rate = self._enforce_propeller_shear_protection(requested_yaw_rate, current_omega)
        
        # Apply Rudder Roll Stabilization (RRS) & Squat Limits
        if self.subsystems_online:
            final_torque, final_rudder_deg, _ = self.hydro_predictor.execute_maneuver(
                target_rpm=requested_rpm,
                target_yaw_rate=safe_yaw_rate,
                telemetry=telemetry,
                dt=dt
            )
        else:
            # Fallback basic pass-through if sub-modules are missing
            final_torque = (requested_rpm - current_rpm) * 100.0
            final_rudder_deg = math.degrees(safe_yaw_rate)

        # Pre-emptively scale torque down if the Wave Matrix predicts the propeller is lifting out of the water
        final_torque = final_torque * ventilation_beta
        
        # Apply Bank Cushion trim offset so the ship drives straight next to canal walls
        final_rudder_deg += autopilot_trim

        # Calculate predicted roll moment from this rudder action for Sea Machines logging
        predicted_roll_moment = self._calculate_rudder_roll_moment(final_rudder_deg, speed_ms)

        # ----------------------------------------------------------------------
        # STAGE 3: CLAMP TO HARDWARE LIMITS & UPDATE STATE
        # ----------------------------------------------------------------------
        self.current_rudder = max(-self.max_rudder_deg, min(self.max_rudder_deg, final_rudder_deg))
        safe_torque_nm = max(-self.max_yield_torque, min(self.max_yield_torque, final_torque))

        # ----------------------------------------------------------------------
        # STAGE 4: DISPATCH OUTPUTS
        # ----------------------------------------------------------------------
        return {
            'command_motor_torque_nm': round(safe_torque_nm, 2),
            'command_rudder_angle_deg': round(self.current_rudder, 2),
            
            # The "Upstream Autonomy Telemetry" payload feeds rich hydrodynamic data 
            # back to Aegis or Sea Machines so they know *why* the ship isn't turning as requested.
            'upstream_autonomy_telemetry': {
                'propeller_ventilation_risk': round(1.0 - ventilation_beta, 3),
                'structural_yaw_override_active': abs(requested_yaw_rate - safe_yaw_rate) > 0.01,
                'predicted_rudder_roll_moment_nm': round(predicted_roll_moment, 1),
                'bank_suction_trim_active': autopilot_trim != 0.0
            }
        }

# ==============================================================================
# VERIFICATION EXECUTION PROFILE
# ==============================================================================
if __name__ == "__main__":
    # Initialize the engine with EXACT physical naval measurements
    vessel_config = {
        'diameter': 3.4,           # D^5 multiplier for shaft torque
        'inertia_prop': 500.0, 
        'draft': 6.5, 
        'hull_length': 45.0, 
        'rudder_arm_z': 2.8,       # Length for roll coupling
        'max_torque': 90000.0,
        'max_rudder_deg': 35.0
    }
    
    print("=====================================================================")
    print("UNIVAC REPLACEMENT BRIDGE COGNITIVE MATRIX ONLINE")
    print("=====================================================================\n")
    
    engine = UnivacReplacementBridgeEngine(vessel_config)
    
    # Simulating a highly stressful environment: 
    # High speed, shallow depth, heavy wave roll, and close to a canal bank.
    telemetry_sample = {
        'rpm': 500.0, 
        'depth': 7.8, 
        'speed_ms': 7.5, 
        'bow_sensor_meters': -1.9, # Predicting a wave trough
        'yaw_rate_rads': 0.04, 
        'roll_angle_rad': 0.08, 
        'roll_rate_rads': 0.14,
        'distance_to_bank_meters': 14.5, 
        'rudder_deg': 5.0
    }
    
    # Aegis/Sea Machines requests full speed and a dangerously sharp turning arc
    target_sample = {
        'rpm': 650.0, 
        'target_yaw_rate': 0.15 # Highly aggressive turn request
    }
    
    print(">> INGESTING TARGETS:")
    print(f"Requested RPM: {target_sample['rpm']}")
    print(f"Requested Yaw Rate: {target_sample['target_yaw_rate']} rad/s\n")
    
    # Execute 1 clock cycle (100ms)
    commands = engine.execute_bridge_loop(target_sample, telemetry_sample, dt=0.1)
    
    print(">> DISPATCHING HARDWARE COMMANDS:")
    print(f"Motor Torque Command:  {commands['command_motor_torque_nm']} Nm")
    print(f"Rudder Angle Command:  {commands['command_rudder_angle_deg']} Degrees\n")
    
    print(">> UPSTREAM TELEMETRY TO SEA MACHINES/AEGIS:")
    for key, val in commands['upstream_autonomy_telemetry'].items():
        print(f" - {key.replace('_', ' ').title()}: {val}")
    print("\n=====================================================================")
