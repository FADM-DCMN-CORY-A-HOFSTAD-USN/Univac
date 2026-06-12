# API Payload Cheat-Sheet (Upstream JSON Commands)

## 1. Functional Overview
This reference guide details the upstream JSON command payloads accepted by the **`JsonTcpCommandListener`** server on Port 7000. These definitions allow automated workstations, integrated bridge systems, and cargo computers to interface natively with the core control plant. 

Because cargo configuration operations alter the vessel's displacement profile, all **Cargo Mass updates** must be explicitly dispatched down this pipeline to calibrate the hydrodynamic matrices before conducting the final pre-sail check sequence.


## 2. Core API Endpoint Specifications
All network messages must be sent over an active TCP stream connection, formatted as a **single line of minified, clean UTF-8 JSON text terminated with a single newline character (`\n`)**.



[ Remote Workstation ] ─── JSON String + \n ───> [ TCP Port 7000 Server ]
[ Remote Workstation ] <─── JSON Status + \n ─── [ TCP Port 7000 Server ]

### A. Endpoint 1: Motion Trajectory Targets (`motion_setpoint`)
Used by navigation consoles and autopilot routines during active transit to change velocity vectors and turning arcs.

* **Payload Example**:

  {"msg_type": "motion_setpoint", "rpm": 450.0, "target_yaw_rate": 0.05}

* **Field Specifications**:
  * `msg_type`: *String*. Must read exactly `"motion_setpoint"`.
  * `rpm`: *Float*. Target propeller shaft speed. Range: `-200.0` (Astern) to `1200.0` (Ahead).
  * `target_yaw_rate`: *Float*. Requested angular turning velocity. Range: `-0.8` (Hard Port) to `0.8` (Hard Starboard) in rad/s.

### B. Endpoint 2: Pre-Sail Cargo State Allocation (`cargo_load`)
**Mandatory Before Pre-Sail Check Execution**. Transmits physical changes in vessel distribution variables so the `HYDRO_Subsystem` can recalculate squat bounds, displacement profiles, and metacentric tracking matrices ($GM$).

* **Payload Example**:

  {"msg_type": "cargo_load", "cargo_mass_tonnes": 420.5, "added_trim_meters": 0.15, "computed_gm_meters": 1.38}

* **Field Specifications**:
  * `msg_type`: *String*. Must read exactly `"cargo_load"`.
  * `cargo_mass_tonnes`: *Float*. Total weight of all secure items loaded. Range: `0.0` to `5000.0`.
  * `added_trim_meters`: *Float*. Geometric bow-to-stern draft variance caused by cargo balance. Range: `-1.5` to `1.5`.
  * `computed_gm_meters`: *Float*. Newly calculated metacentric stability height. Range: `0.4` to `3.5`.



## 3. Server Acknowledgment and Status Responses
The bridge TCP server returns an explicit execution response sentence frame over the active network wire for every single parsed line command received.

### A. Success Confirmation Format
Returned when data structures match validation criteria and are pushed down to core engine cache memory.

{"status": "OK", "message": "ACCEPTED: Targets updated successfully"}


### B. Rejection / Validation Fault Format
Returned if syntax breaks, keys are omitted, or parameters fall outside allowed physical limits.

{"status": "ERROR", "message": "REJECTED: Requested RPM out of structural design range (-200 to 1200)"}




## 4. Hardware Data Broadcast Schema (Outbound UDP Telemetry)
The co-processor outputs high-fidelity hydrodynamic tracking metrics as an outbound JSON data package embedded inside its network pipeline. Autonomy clients can capture this packet to patch holes in their situational awareness sensors.


{
    "UNIVAC_Water_Insight_Link": {
        "subsurface_ventilation_index": 0.985,
        "predicted_keel_clearance_meters": 4.12,
        "structural_fatigue_load_percentage": 14.2,
        "parametric_roll_harmonic_warning": false,
        "leeway_crab_angle_compensation_deg": 1.84
    }
}


* `subsurface_ventilation_index`: Real-time calculation of propeller density loss due to aerated wave actions ($1.0 = \text{Nominal}$).
* `predicted_keel_clearance_meters`: Computed true distance between the bottom of the hull and the seabed floor, adjusting for static draft + cargo load + active hull squat speed variations.
* `structural_fatigue_load_percentage`: Stress analysis checking combined bending and gyroscopic moments acting across the physical shaft rings.


This API payload cheat-sheet is now fully mapped, providing clear definitions for motion control commands, cargo initialization properties, and response messages.
Since you mention loading cargo is your initial step, we can build the Operator Pre-Sail Diagnostic Checklist (diagnostics.md) next. This will provide a sequential guide for verifying your serial ports, sensor inputs, and weapon tracking rings before departing the pier. Would you like to generate that checklist file?
