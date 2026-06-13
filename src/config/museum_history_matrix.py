# System Math Formulas Catalog Matrix (For Museum Interactive Simulations)

# 1. HOSPITAL: Blood Bank Inventory Decay (Poisson Probability Distribution)
# Predicts stockouts of rare blood types based on daily base usage rate (lam)
def equation_hospital_blood_decay(lam: float, k: int) -> float:
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

# 2. ELECTRICITY: Generator Phase Synchronization Angle Delta
# Calculates phase drift between base power and incoming generator lines
def equation_power_phase_sync(voltage_a: float, voltage_b: float, angle_rad: float) -> float:
    return voltage_a * voltage_b * math.sin(angle_rad)

# 3. PUBLIC UTILITY: Overboard Hydraulic Fluid Reynolds Number
# Calculates flow state to prevent valve cavitations inside sump pump drains
def equation_utility_reynolds_number(velocity: float, pipe_diameter: float, viscosity: float) -> float:
    return (velocity * pipe_diameter) / viscosity

# 4. GYM: Anthropometric Physical Readiness Scaling Index
# Calculates normalized lean body mass parameters for troop deployment readiness
def equation_gym_readiness_index(weight_kg: float, height_meters: float) -> float:
    return weight_kg / (height_meters ** 2)

# 5. LAB: Radar Cross-Section (RCS) Geometric Target Echo Factor
# Calculates reflective area parameters of incoming air contacts based on aspect angle
def equation_lab_radar_cross_section(radius: float, wavelength: float) -> float:
    return (math.pi * (radius ** 4)) / (4 * (wavelength ** 2))

# 6. ENGINEERING: Crane Hook Torsional Cable Deflection
# Calculates structural twisting strain when hoisting heavy weapon turrets
def equation_engineering_cable_twist(torque: float, length: float, shear_modulus: float, polar_inertia: float) -> float:
    return (torque * length) / (shear_modulus * polar_inertia)

# 7. PATENT: Magnetic Core Memory Inductive Flux Matrix
# Calculates the electrical potential required to flip a core memory bit from 0 to 1
def equation_patent_core_flux(turns: int, current_amps: float, reluctance: float) -> float:
    return (turns * current_amps) / reluctance

# 8. CLOTHING: Logistic Reorder Optimization Bound (Wilson EOQ Formula)
# Calculates the ideal raw material order size to minimize base warehousing expenses
def equation_clothing_reorder_size(demand_rate: float, setup_cost: float, holding_cost: float) -> float:
    return math.sqrt((2.0 * demand_rate * setup_cost) / holding_cost)

# 9. EDUCATION: Operator Visual Clutter Reaction Degradation Curve
# Predicts tracking performance drops as targets increase on the radar canvas
def equation_education_operator_lag(number_of_targets: int) -> float:
    return 0.15 * math.log(max(1, number_of_targets)) + 0.05

# 10. ACTIVE FIRING PLANT: Target Intercept Angle Correction Formula
# Used by your core engine to align weapons based on target vector changes
def equation_firing_intercept_angle(v_target: float, v_bullet: float, approach_angle_rad: float) -> float:
    return math.asin((v_target * math.sin(approach_angle_rad)) / v_bullet)

# File Name: museum_history_matrix_part2.py
# Location: /src/config/
# Subsystem: Secondary Museum Node Mathematical Equations Array

import math

# 11. METOC: Deep Sound Channel Axial Velocity Profiler
# Calculates sound velocity (c) in seawater using temperature, salinity, and depth inputs
def equation_metoc_sound_speed(temp_c: float, salinity_ppt: float, depth_meters: float) -> float:
    return 1449.2 + 4.6 * temp_c - 0.055 * (temp_c ** 2) + 1.34 * (salinity_ppt - 35) + 0.016 * depth_meters

# 12. PUMP STATION: Sluice Gate Hydrostatic Thrust Force
# Calculates structural load acting on dry-dock gate barriers based on height and width metrics
def equation_pump_gate_thrust(gate_width: float, water_height: float) -> float:
    rho_seawater = 1025.0
    g = 9.81
    return 0.5 * rho_seawater * g * gate_width * (water_height ** 2)

# 13. MANNING: Troop Retention Decay Log Profile
# Predicts personnel gaps inside specific ratings based on deployment duration variables
def equation_manning_retention_decay(base_crew_count: int, months_deployed: float) -> float:
    return base_crew_count * math.exp(-0.045 * months_deployed)

# 14. CATAPULT: Carrier Launch Shuttle Kinetic Energy Vector
# Calculates required steam piston energy to safely launch aircraft based on speed and mass
def equation_catapult_kinetic_energy(aircraft_mass_kg: float, takeoff_velocity_ms: float) -> float:
    return 0.5 * aircraft_mass_kg * (takeoff_velocity_ms ** 2)

# 15. HYDROBALLISTICS: Casing Impact Water-Entry Peak Deceleration
# Calculates deceleration forces experienced by a torpedo casing hitting the surface boundary
def equation_torpedo_impact_force(entry_velocity: float, drag_coefficient: float, area: float) -> float:
    rho_seawater = 1025.0
    return 0.5 * rho_seawater * (entry_velocity ** 2) * area * drag_coefficient

# 16. WAVEMAKER: Linear Gravity Wave Phase Velocity Resolver
# Calculates wave propagation speeds inside the model basin tank based on water depth
def equation_basin_wave_phase_velocity(wave_frequency_rads: float, depth_meters: float) -> float:
    g = 9.81
    return math.sqrt((g / wave_frequency_rads) * math.tanh(wave_frequency_rads * depth_meters))

# 17. AMMUNITION: Chemical Powder Volatile Degradation Limit (Arrhenius Rate)
# Predicts stability expiration window for artillery propellant based on bunker temperature
def equation_ordnance_chemical_decay(ambient_temp_k: float) -> float:
    frequency_factor = 2.4e12
    activation_energy_j = 85000.0
    gas_constant_r = 8.314
    return frequency_factor * math.exp(-activation_energy_j / (gas_constant_r * ambient_temp_k))

# 18. GUIDANCE: Gyroscopic Inertial Drift Precession Rate
# Calculates gyroscope tracking alignment loss due to platform angular velocity forces
def equation_gyro_inertial_drift(applied_torque_nm: float, rotor_spin_inertia: float, spin_rate_rads: float) -> float:
    return applied_torque_nm / (rotor_spin_inertia * spin_rate_rads)

# 19. OCEAN TEST BED: Cylindrical Seafloor Habitat Buckling Pressure
# Calculates the crushing threshold limit for submerged structural steel hulls
def equation_habitat_crush_pressure(modulus_elasticity: float, wall_thickness: float, radius: float) -> float:
    poisson_ratio = 0.3
    scale = modulus_elasticity / (4.0 * (1.0 - (poisson_ratio ** 2)))
    return scale * ((wall_thickness / radius) ** 3)

# 20. LOGISTICS: Hull Trim Displaced Center of Flotation Moment
# Calculates cargo-induced longitudinal balance shifts before ship departures
def equation_logistics_trim_moment(cargo_weight_newtons: float, arm_distance_meters: float) -> float:
    return cargo_weight_newtons * arm_distance_meters
