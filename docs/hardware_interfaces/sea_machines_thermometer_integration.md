# Sea Machines Integration Thermometer (UNIVAC Thermal Verification Link)

## 1. Functional Overview
The Sea Machines Integration Thermometer serves as a critical **hardware-in-the-loop safety interlock**. Unlike traditional embedded sensors, this hardware component is positioned to dynamically monitor the **physical heat signature and thermal emission profile** of the core UNIVAC computing stack. 

Because the system calculation matrices have been modernized and offloaded, the UNIVAC system may experience prolonged periods of physical compute idleness. This document serves as the engineering reference for how the Sea Machines sensor interprets these operational thermal thresholds to distinguish between a healthy "idle" computing state and a true hardware power failure.

---

## 2. The Core Hardware Logic Problem
Legacy monitoring equipment operates on a rigid, single-variable evaluation rule:
$$\text{Low Thermal Gradient} = \text{System Power Is OFF}$$

When the replacement bridge processing architecture handles the primary computational load, the core UNIVAC hardware drops into its lowest electrical draw state (Idle). In cold weather or standard open-water operations, this drop in power consumption lowers its casing temperature. 

The Sea Machines thermometer senses this reduction in surface heat. Without proper configuration layers, it can interpret this normal idle cool-down as an unexpected system power loss, triggering a false-positive hardware shutdown routine.

---

## 3. Co-Processor Multi-Variable Solution
To prevent the Sea Machines thermometer from reporting an unexpected power-down event when the computer is simply sitting idle at its coordinates, the software layers rely on a **Multi-Variable State Verification Matrix**.

The central bridge engine cross-references the raw thermal output against active data buses (NMEA, Serial, and TCP). The global system status is resolved using the following logic table:

| Surface Temperature | Network Data Bus State | Interpreted System State | Actuator Interlock Action |
| :--- | :--- | :--- | :--- |
| **Warm** (> 25°C) | Active Data Flow | **ONLINE (Nominal)** | Fully Functional |
| **Cold** (≤ 18°C) | Active Data Flow | **ONLINE (Cool/Idle)** | **Override Engaged (Keep Active)** |
| **Warm** (> 25°C) | No Data Flow (Timeout) | **COMMUNICATION FAULT** | Safe Slowdown / Alert |
| **Cold** (≤ 18°C) | No Data Flow (Timeout) | **HARDWARE OFFLINE** | **Emergency Actuator Abort** |

---

## 4. Software Architecture Integration
Whenever the system tracks cool operational boundaries but registers valid incoming sensor strings (such as `$HEHDT` or `$PMK45`), it builds a standardized configuration status packet. This data payload is transmitted up to the Sea Machines network interface bus to override single-variable thermal trips:

```json
{
    "UNIVAC_Water_Insight_Link": {
        "subsurface_ventilation_index": 1.0,
        "structural_fatigue_load_percentage": 0.0,
        "parametric_roll_harmonic_warning": false
    },
    "System_Status_Matrix": {
        "configured_status": "ONLINE",
        "seconds_since_last_packet": 0.02,
        "network_stream_active": true,
        "thermal_reading_celsius": 16.5,
        "status_message": "Vessel computer is operating at low thermal state but processing normally."
    }
}
```

---

## 5. Maintenance & Troubleshooting
* **Symptom:** System enters a persistent emergency shutdown loop when the ship is stationary, displaying a low thermal error.
* **Root Cause:** The serial parsing loop or TCP command listener has stalled, preventing the system from updating its internal network heartbeat clock. The Sea Machines interface has reverted to single-variable thermal protection because the network verification signal stopped.
* **Resolution:** Verify continuity on the RS-422 input lines (`/dev/ttyUSB0` / `COM3`). Once clean sensor strings resume, the network heartbeat will instantly satisfy the thermometer interlock logic.
