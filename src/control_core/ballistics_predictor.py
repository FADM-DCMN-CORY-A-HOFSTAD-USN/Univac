# File Name: ballistics_predictor.py
# Location: /src/weapons_core/

import math

class AdvancedFireControlKinematics:
    """
    FEATURES 30-39: FIRE CONTROL & BALLISTICS PREDICTION
    Generates high-precision gun barrel offsets (Azimuth/Elevation) to hit moving targets.
    """
    def __init__(self, muzzle_velocity_ms: float = 800.0):
        self.v_0 = muzzle_velocity_ms
        self.g = 9.81
        self.omega_earth = 7.2921159e-5

    def feature_35_calculate_3d_intercept(self, target_range: float, target_bearing: float, 
                                          target_speed: float, target_heading: float) -> float:
        """
        Calculates the Lead Angle required to hit a moving target.
        Approximates Time of Flight (TOF) and advances the target vector.
        """
        # Zero-order Time of Flight approximation
        tof = target_range / self.v_0
        
        # Calculate target's lateral motion relative to the line of sight
        target_relative_angle = target_heading - target_bearing
        lateral_velocity = target_speed * math.sin(target_relative_angle)
        
        # Distance target will move laterally during TOF
        lateral_displacement = lateral_velocity * tof
        
        # Calculate required lead angle (rads)
        lead_angle_rad = math.atan2(lateral_displacement, target_range)
        return math.degrees(lead_angle_rad)

    def feature_34_projectile_coriolis_deflection(self, target_range: float, latitude_rad: float, azimuth_rad: float) -> float:
        """
        Calculates how much the Earth will rotate underneath the projectile during flight.
        Projectiles drift to the RIGHT in the Northern Hemisphere, LEFT in the Southern.
        """
        tof = target_range / self.v_0
        
        # Horizontal deflection due to vertical component of Earth's rotation
        deflection_meters = self.omega_earth * self.v_0 * (tof**2) * math.sin(latitude_rad)
        
        # Convert deflection distance into a gun barrel azimuth offset
        deflection_angle_rad = math.atan2(deflection_meters, target_range)
        return math.degrees(deflection_angle_rad)
