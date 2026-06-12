# Actuator Calibration and Troubleshooting Matrix (Rudder Control Interface)

## 1. Functional Overview
The steering gear control subsystem converts digital mathematical steering vectors ($\delta_{command}$) into physical hydraulic actuator displacements. This document defines the precise analog voltage mapping, calibration bounds, mechanical feedback thresholds, and runtime troubleshooting interlocks required to verify that the rudder linkages safely follow ordered commands.

## 2. Analog Signal Calibration Matrix
The physical interface layer utilizes a dual-channel, isolated $\pm 10\text{V}$ DC differential control loop to drive the proportional hydraulic directional valves, alongside a redundant 4–20mA current loop for rotary feedback encoders.

| Mechanical Rudder Angle | Control Voltage Channel A ($V_{cmd}$) | Control Voltage Channel B ($V_{invert}$) | Nominal Valve State / Port Direction |
| :--- | :--- | :--- | :--- |
| **$35.0^\circ$ Hard Port** | $-10.00\text{ VDC}$ | $+10.00\text{ VDC}$ | Maximum Flow / Port Actuation |
| **$15.0^\circ$ Standard Port** | $-4.28\text{ VDC}$ | $+4.28\text{ VDC}$ | Proportional Flow / Port Actuation |
| **$0.0^\circ$ Dead Center** | $0.00\text{ VDC}$ | $0.00\text{ VDC}$ | Null Position / Zero Flow |
| **$15.0^\circ$ Standard Stbd** | $+4.28\text{ VDC}$ | $-4.28\text{ VDC}$ | Proportional Flow / Starboard Actuation |
| **$35.0^\circ$ Hard Stbd** | $+10.00\text{ VDC}$ | $-10.00\text{ VDC}$ | Maximum Flow / Starboard Actuation |

### Encoder Feedback Conversion Parameters
The linear displacement or rotary transformation sensor converts structural rod positions into a stabilized 4–20mA current loop to maximize electrical noise immunity over long cable runs:
* **$4.0\text{ mA}$**: $-35.0^\circ$ Position Limit (Hard Port)
* **$12.0\text{ mA}$**: $0.0^\circ$ Position Limit (Neutral Center)
* **$20.0\text{ mA}$**: $+35.0^\circ$ Position Limit (Hard Starboard)

$$\text{Rudder Angle (Degrees)} = (\text{Current}_{\text{mA}} - 12.0) \times 4.375$$

## 3. Real-Time Diagnostics & Structural Thresholds
The `ActuatorTelemetryReceiverNode` constantly evaluates the delta between the mathematically ordered rudder position ($\delta_{cmd}$) and the physical position reported by the current loop encoder ($\delta_{meas}$). 



┌──────────────────┐
│ Ordered Rudder │
└──────────────────┘
│
▼
[Subtract] <─── [Redundant 4-20mA Feedback Loop]
│
▼
Tracking Deviation (Δ δ)
│
├──> Within ±2.5°: Nominal Operation (Reset Error Timer)
│
└──> Exceeds ±2.5°: Start Tracking Error Clock
│
▼
Duration ≥ 1.5 Seconds?
│
├──> YES: Flag MECHANICAL_LINKAGE_JAM Interlock
└──> NO: Increment Clock, Continue Tracking

* **Nominal Deviation Band**: $\le \pm 1.0^\circ$. Regular hydraulic system mechanical latency.
* **Warning Threshold**: $\pm 2.5^\circ$. Active tracking error clock starts incrementing.
* **Critical Interlock Threshold**: $\ge \pm 2.5^\circ$ for **$\ge 1.5$ continuous seconds**. Instantly registers a `MECHANICAL_LINKAGE_JAM` state fault.

## 4. Troubleshooting Matrix (Fault Codes & Field Isolation)

When a bitmask fault code is broadcast by the steering gear processor, look up the code below to determine the immediate system-level interlock action taken by the core software.

| Fault Register Bitmask | System Error String | Trigger Condition | System Automation Interlock Response | Field Correction Steps |
| :--- | :--- | :--- | :--- | :--- |
| **`0x0001`** | `HYDRAULIC_PRESSURE_DROP` | System accumulator pressure drops below $140\text{ bar}$. | Triggers proactive torque shedding on main propulsion; drops allowed shaft speed by 60% to reduce lateral hull forces. | Inspect hydraulic pump lines for fluid leaks, verify valve seals, and check accumulator nitrogen pre-charge levels. |
| **`0x0002`** | `MOTOR_CURRENT_OVERLOAD` | Actuator motor amplifier draws $> 45\text{ Amps}$ for over $500\text{ms}$. | Caps maximum rudder slew rate to $2.0^\circ/\text{sec}$ to mitigate severe motor winding heat stress. | Verify rudder horn clearance, inspect pintle bearings for scoring or binding, and test motor winding resistance. |
| **`0x0004`** | `ACTUATOR_THERMAL_CRITICAL` | Stator or hydraulic oil temperature exceeds $85^\circ\text{C}$. | Temporarily widens steering loop tracking deadband to $\pm 3.0^\circ$ to reduce high-frequency micro-corrections. | Check cooling water heat exchanger loop, verify fluid levels, and check for high-frequency hunting in control law. |
| **`0x0008`** | `FEEDBACK_SENSOR_FAULT` | Feedback current drops below $3.8\text{ mA}$ or rises above $20.5\text{ mA}$. | **Hard Fault**. Reverts bridge to manual backup joystick bypass mode. Safely sets motor torque command to $0.0\text{ Nm}$. | Check current loop wire continuity for an open circuit ($0\text{ mA}$) or a short circuit to ground. Replace encoder module. |
| **`0x0010`** | `MECHANICAL_LINKAGE_JAM` | Deviation exceeds threshold band for over $1.5\text{ seconds}$. | **Hard Fault**. Force-aborts all autonomous navigation commands. Sets propulsion torque instantly to $0.0\text{ Nm}$. | Clear debris from the rudder blade, inspect hydraulic cylinder rods for binding, and check mechanical tie-bars. |


## 5. Automated System Interlock Responses
If any fault register evaluates to a **Hard Fault** state (`0x0008` or `0x0010`), the network layer overrides active maneuvering and tracking targets. The system forces the main propulsion motor to a **neutral torque state ($0.0\text{ Nm}$)** to quickly strip forward momentum from the vessel. This prevents the ship from entering an uncommanded tight circle or spinning out, shielding both the hull and the rudder assembly from catastrophic structural shear stress.

This actuator calibration and troubleshooting document is now fully structured and formatted into a clean markdown code window for your documentation library.
Where would you like to direct focus next? We can build a Hardware Deployment and Pin-Configuration Guide (deployment.md) to map your specific physical COM/tty USB ports and network socket configurations, or we can build an Operator Diagnostic Checklist (diagnostics.md) for pre-sail bridge checks. Let me know what you need.
