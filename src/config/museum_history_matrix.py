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

# File Name: museum_history_matrix_part3.py
# Location: /src/config/
# Subsystem: Tertiary Museum Node Mathematical Equations Array

import math

# 21. PROPELLANT: Viscous Flow Chemical Mixer Shearing Torque
# Calculates mechanical resistance inside a mixing vat based on fluid viscosity
def equation_propellant_mixer_torque(viscosity_pas: float, rotational_speed_rads: float, blade_radius_m: float) -> float:
    return 4.0 * math.pi * viscosity_pas * rotational_speed_rads * (blade_radius_m ** 3)

# 22. NAVCOMMSTA: Queued Teletype Packet Latency Window (M/M/1 Queue Model)
# Predicts network transmission delay based on message arrival rate (lam) and service capacity (mu)
def equation_comm_packet_latency(arrival_rate: float, service_capacity: float) -> float:
    if service_capacity <= arrival_rate:
        return 999.9  # Queue saturation overflow limit
    return 1.0 / (service_capacity - arrival_rate)

# 23. CRYPTOLOGY: Hyperbolic Line of Bearing (LOB) Intersection Coordinate
# Triangulates target latitude offset using cross-bearing error variations
def equation_crypt_triangulation_offset(base_distance_m: float, bearing_angle_rad: float) -> float:
    return base_distance_m * math.tan(bearing_angle_rad)

# 24. METALLURGY: Gamma Radiation Attenuation Shielding Thickness
# Calculates required lead/steel barrier depth to reduce radiation intensity to target safety bounds
def equation_shielding_radiation_attenuation(initial_intensity: float, target_intensity: float, linear_atten_coef: float) -> float:
    if initial_intensity <= target_intensity:
        return 0.0
    return math.log(initial_intensity / target_intensity) / linear_atten_coef

# 25. JET TEST CELL: Turbine Gas Thermal Kinetic Velocity
# Calculates exhaust gas stream speeds based on enthalpy changes and exit temperature
def equation_turbine_exhaust_velocity(specific_heat: float, inlet_temp_k: float, outlet_temp_k: float) -> float:
    temp_delta = inlet_temp_k - outlet_temp_k
    if temp_delta <= 0:
        return 0.0
    return math.sqrt(2.0 * specific_heat * temp_delta)

# 26. SUPPLY CHAIN: Failure Rate Probability Mask (Weibull Distribution)
# Predicts components failure probability during active voyages based on wear factors (beta, alpha)
def equation_supply_failure_probability(time_days: float, scale_alpha: float, shape_beta: float) -> float:
    return 1.0 - math.exp(-((time_days / scale_alpha) ** shape_beta))

# 27. SONOBUOY: Submarine Propeller Blade-Rate Acoustic Frequency Cavitation
# Calculates target base frequency based on shaft rotations per minute and number of blades
def equation_asw_blade_rate_frequency(shaft_rpm: float, number_of_blades: int) -> float:
    return (shaft_rpm / 60.0) * number_of_blades

# 28. ORDNANCE VAULT: Mine Magnetic Sensor Ambient Flux Calibration
# Calculates boundary stray currents passing through underwater casing alloys
def equation_mine_magnetic_flux(permeability: float, coil_turns: int, current_amps: float, length_m: float) -> float:
    return (permeability * coil_turns * current_amps) / length_m

# 29. WEATHER: Geostrophic Wind Balance Velocity Vector
# Calculates true tracking wind velocity generated by changing barometric pressure gradients
def equation_weather_geostrophic_wind(pressure_gradient: float, air_density: float, coriolis_parameter: float) -> float:
    denom = air_density * coriolis_parameter
    if abs(denom) < 1e-6:
        return 0.0
    return pressure_gradient / denom

# 30. HYDROFOIL: Strut Submerged Hydrofoil Cavitation Limit Index
# Calculates the cavitation safety ceiling threshold to prevent lift breakdown at flank speeds
def equation_hydrofoil_cavitation_index(static_pressure: float, vapor_pressure: float, velocity_ms: float) -> float:
    rho_seawater = 1025.0
    denom = 0.5 * rho_seawater * (velocity_ms ** 2)
    if denom <= 0.1:
        return 999.0
    return (static_pressure - vapor_pressure) / denom

# File Name: museum_history_matrix_part4.py
# Location: /src/config/
# Subsystem: Subterranean & Aerospace Museum Node Mathematical Equations Array

import math

# 31. CBRN DOOR: Blast Valve Shockwave Overpressure Peak Load
# Calculates structural impact force (Newtons) acting on an underground door based on blast pressure
def equation_cbrn_blast_force(peak_overpressure_psi: float, door_area_m2: float) -> float:
    psi_to_pascal = 6894.76
    return peak_overpressure_psi * psi_to_pascal * door_area_m2

# 32. SEWAGE PUMP: Deep-Silo Hydrostatic Head Lift Velocity
# Calculates required pump discharge velocity based on subterranean vertical lift height
def equation_silo_pump_lift_velocity(pump_pressure_pascal: float, head_height_meters: float) -> float:
    rho_seawater = 1025.0
    g = 9.81
    velocity_squared = (2.0 * pump_pressure_pascal / rho_seawater) - (2.0 * g * head_height_meters)
    return math.sqrt(max(0.0, velocity_squared))

# 33. STANDBY POWER: AC Generator Alternating Current Impedance Balance
# Calculates electrical line drop parameters inside underground bunker grids
def equation_bunker_power_impedance(resistance_ohms: float, inductance_henries: float, frequency_hz: float) -> float:
    reactance = 2.0 * math.pi * frequency_hz * inductance_henries
    return math.sqrt((resistance_ohms ** 2) + (reactance ** 2))

# 34. LOX STORAGE: Cryogenic Boiling Liquid Expanding Vapor Explosion (BLEVE) Risk Index
# Predicts pressure escalation trends inside an Atlas silo oxygen storage container based on temperature
def equation_silo_lox_pressure(ambient_temp_k: float, volume_m3: float, moles_gas: float) -> float:
    gas_constant_r = 8.314
    return (moles_gas * gas_constant_r * ambient_temp_k) / volume_m3

# 35. FLAME FLUSH: Silo Exhaust Acoustic Deluge Mass Attenuation Flow Rate
# Calculates required water dump volume to absorb rocket exhaust kinetic acoustic energy
def equation_silo_water_flow_rate(rocket_thrust_newtons: float, exhaust_velocity_ms: float) -> float:
    if exhaust_velocity_ms <= 0.1:
        return 999.0
    return rocket_thrust_newtons / exhaust_velocity_ms

# 36. SPACE TRACKING: Keplerian Two-Body Orbital Trajectory Velocity Vector
# Calculates true velocity of a spacecraft at any point along its orbit relative to Earth
def equation_orbital_velocity(altitude_meters: float, semi_major_axis_meters: float) -> float:
    mu_earth = 3.986004418e14  # Earth standard gravitational parameter
    r_radius = 6371000.0 + altitude_meters
    velocity_squared = mu_earth * ((2.0 / r_radius) - (1.0 / semi_major_axis_meters))
    return math.sqrt(max(0.0, velocity_squared))

# 37. DEW LINE RADAR: Ionospheric Aurora Attenuation Dispersion Factor
# Calculates radar signal attenuation passing through high-latitude auroral storms
def equation_radar_aurora_attenuation(electron_density_m3: float, radar_freq_hz: float) -> float:
    if radar_freq_hz <= 1.0:
        return 999.0
    plasma_freq = 8.98 * math.sqrt(electron_density_m3)
    return math.sqrt(max(0.0, 1.0 - (plasma_freq / radar_freq_hz) ** 2))

# 38. ELECTRONIC FENCE: Radar Baseline Interferometer Target Cross-Bearing Intersection
# Triangulates satellite latitude using phase-difference angles from a radio telescope receiver array
def equation_satellite_fence_distance(baseline_distance_m: float, phase_delta_rad: float) -> float:
    if abs(math.sin(phase_delta_rad)) < 1e-5:
        return 999999.0
    return baseline_distance_m / math.sin(phase_delta_rad)

# 39. SKYLAB LIFE SUPPORT: Partial Pressure Oxygen Molecular Density Allocation
# Calculates oxygen density levels to satisfy breathing parameters without fire risks
def equation_space_habitat_oxygen_partial_pressure(total_pressure_atm: float, oxygen_fraction: float) -> float:
    return total_pressure_atm * oxygen_fraction

# 40. VLF ARRAY: Helical Coil Variometer Resonant Frequency
# Calculates tuning parameters to match communications waves deep underwater to submarines
def equation_vlf_helical_resonance(inductance_henries: float, capacitance_farads: float) -> float:
    denom = 2.0 * math.pi * math.sqrt(inductance_henries * capacitance_farads)
    if denom <= 0.0:
        return 0.0
    return 1.0 / denom

# File Name: museum_history_matrix_part5.py
# Location: /src/config/
# Subsystem: Extended Infrastructure Museum Node Mathematical Equations Array

import math

# 41. RAIL FREIGHT: Rolling Train Wheel Kinetic Braking Force
def equation_rail_braking_force(train_mass_kg: float, velocity_ms: float, stop_distance_m: float) -> float:
    if stop_distance_m <= 0.1: return 999999.0
    return (0.5 * train_mass_kg * (velocity_ms ** 2)) / stop_distance_m

# 42. STATION: Manifest Processing Network Capacity (Little's Law)
def equation_station_manifest_queue(arrival_rate_per_min: float, average_wait_min: float) -> float:
    return arrival_rate_per_min * average_wait_min

# 43. TRAFFIC: Roadway Loop Sensor Inductance Shift Vector
def equation_traffic_loop_inductance(turns: int, area_m2: float, permeability: float, length_m: float) -> float:
    return (permeability * (turns ** 2) * area_m2) / length_m

# 44. DAM: Hydrostatic Spillway Discharge Flow Rate (Weir Equation)
def equation_dam_spillway_flow(discharge_coef: float, width_m: float, head_height_m: float) -> float:
    return discharge_coef * width_m * (head_height_m ** 1.5)

# 45. DYNAMO: Synchronous AC Generator Phase Power Angle
def equation_generator_dynamo_power(v_internal: float, v_bus: float, react_ohms: float, delta_rad: float) -> float:
    if react_ohms <= 0.01: return 0.0
    return ((v_internal * v_bus) / react_ohms) * math.sin(delta_rad)

# 46. BUNKER HVAC: Airflow Velocity Duct Pressure (Bernoulli Equation)
def equation_bunker_hvac_pressure(air_density: float, velocity_ms: float) -> float:
    return 0.5 * air_density * (velocity_ms ** 2)

# 47. SCHOOL: Simulated Radar Signal Doppler Shift Frequency
def equation_school_doppler_frequency(base_freq_hz: float, target_velocity_ms: float) -> float:
    c_speed_of_light = 299792458.0
    return base_freq_hz * (1.0 + (target_velocity_ms / c_speed_of_light))

# 48. NIKE SAM: Missile Target Intercept Aspect Radius Vector
def equation_nike_sam_intercept(r_target_m: float, v_missile_ms: float, t_flight_sec: float) -> float:
    return r_target_m + (v_missile_ms * t_flight_sec)

# 49. SCIENCE CENTER: Microwave Antenna Waveguide Cutoff Frequency
def equation_science_waveguide_cutoff(width_m: float) -> float:
    c_speed = 299792458.0
    return c_speed / (2.0 * width_m)

# 50. SECURITY ALARM: Infrared Fence Sensor Boundary Break Signal Volt
def equation_security_sensor_voltage(input_voltage: float, r_sensor: float, r_fixed: float) -> float:
    if (r_sensor + r_fixed) <= 0.0: return 0.0
    return input_voltage * (r_fixed / (r_sensor + r_fixed))

# 51. WIND TURBINE: Aerodynamic Rotor Lift Power Extraction
def equation_wind_turbine_power(air_density: float, blade_radius_m: float, wind_speed_ms: float, cp_efficiency: float) -> float:
    area = math.pi * (blade_radius_m ** 2)
    return 0.5 * air_density * area * (wind_speed_ms ** 3) * cp_efficiency

# 52. SOLAR ARRAY: Photovoltaic Panel Incidence Angle Correction
def equation_solar_incidence_power(base_flux_wm2: float, sun_angle_rad: float, panel_angle_rad: float) -> float:
    return base_flux_wm2 * math.cos(sun_angle_rad - panel_angle_rad)

# 53. CCTV: Coaxial Video Cable Attenuation Decibel Drop
def equation_cctv_cable_loss(length_feet: float, attenuation_per_100ft: float) -> float:
    return (length_feet / 100.0) * attenuation_per_100ft

# 54. CORE DRILL: Shaft Torsional Shear Stress Limit
def equation_drill_shaft_shear_stress(torque_nm: float, shaft_radius_m: float) -> float:
    polar_inertia = (math.pi * (shaft_radius_m ** 4)) / 2.0
    return (torque_nm * shaft_radius_m) / polar_inertia

# 55. CRANE CONSTRUCTION: Boom Overturning Load Tension Moment
def equation_construction_crane_moment(load_mass_kg: float, radius_arm_m: float) -> float:
    return load_mass_kg * 9.81 * radius_arm_m

# 56. BUILDER SEABEE: Airfield Landing Mat Shear Load Index
def equation_seabee_mat_load(aircraft_weight_n: float, contact_area_m2: float) -> float:
    if contact_area_m2 <= 0.01: return aircraft_weight_n
    return aircraft_weight_n / contact_area_m2

# 57. MACHINE LOGIC: Heuristic Symbolic Logic State Search Tree Bounds
def equation_ai_tree_complexity(branching_factor: int, depth_limit: int) -> float:
    return float(branching_factor ** depth_limit)

# 58. SPACE FORCE: Satellite Elliptic Path Radial Distance
def equation_space_force_radius(semi_major_axis_m: float, eccentricity: float, true_anomaly_rad: float) -> float:
    numerator = semi_major_axis_m * (1.0 - (eccentricity ** 2))
    denominator = 1.0 + eccentricity * math.cos(true_anomaly_rad)
    return numerator / denominator

# 59. SPACE COMMAND: Radar Pulse Time-Of-Flight Distance Target
def equation_space_command_radar_range(time_of_flight_sec: float) -> float:
    c_speed = 299792458.0
    return (c_speed * time_of_flight_sec) / 2.0

# 60. RADIO TRANSMITTER: Antenna Resonant LC Impedance Match Frequency
def equation_radio_antenna_impedance(inductance_h: float, capacitance_f: float) -> float:
    denom = 2.0 * math.pi * math.sqrt(inductance_h * capacitance_f)
    if denom <= 0.0: return 0.0
    return 1.0 / denom
