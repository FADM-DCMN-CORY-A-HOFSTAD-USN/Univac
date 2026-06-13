# System Communication Protocol Manual

## 1. Functional Overview
This manual defines every proprietary serial command sentence used across the UNIVAC Replacement Bridge Matrix system architecture. All communications on the maritime data bus use ASCII-encoded text strings based on industrial NMEA-0183 syntax rules.

To guarantee hard-deterministic execution profiles, all packets must be transmitted as binary ASCII byte frames terminated with a strict carriage return and line feed line terminator sequence (\r\n). 

## 2. Universal Frame Syntax Structures
Every outbound and inbound proprietary command string must adhere to the following structural framing schema:

$[Prefix],[Data_1],[Data_2],...,[Data_N]*[Checksum]\r\n

1. $ (Hex 0x24): The mandatory start-of-sentence framing character.
2. P (Hex 0x50): Proprietary address indicator token.
3. [Prefix]: 6-character identifier mapping the device source and sentence content type.
4. , (Hex 0x2C): Data field delimiter character.
5. *[Checksum]: 8-bit exclusive OR (XOR) hexadecimal verification tag.
6. \r\n (Hex 0x0D, 0x0A): End-of-line carriage return and line feed.

### 8-Bit XOR Checksum Reference Formula
The validation checksum is calculated by performing an XOR operation on the ASCII values of all characters situated between the leading $ and trailing * delimiters:

Checksum = XOR sum of ord(char) for all characters in the payload body.

## 3. Outbound Actuator Serial Commands (Propulsion and Steering)

### A. Propulsion Drive Command Set ($PUNVCPRP)
* Source Subsystem: Core Calculation Plant (bridge_execution_engine.py)
* Target Hardware Link: Main Propulsion Motor Variable Frequency Drive / PLC
* Transmission Cadence: 50Hz Frequency Cycles (20ms intervals)
* Sentence Template:
  $PUNVCPRP,[Torque],[RPM_Cap],[Fatigue]*[CS]\r\n
* Payload Fields Specification:
  * Torque: Float, 1 decimal place. Ordered engine drive force. Range: -90000.0 to 90000.0 Nm.
  * RPM_Cap: Float, 1 decimal place. Dynamic shallow water or structural speed ceiling. Range: 0.0 to 1200.0 RPM.
  * Fatigue: Float, 1 decimal place. Live structural shaft fatigue strain meter calculation. Range: 0.0% to 100.0%.
* Example Binary Frame:
  $PUNVCPRP,45200.5,480.0,42.1*1B\r\n

### B. Asymmetric Port Steering Surface Command Set ($PUNVCPRT)
* Source Subsystem: Asymmetric Control Core Matrix (asymmetric_roll_stabilizer.py)
* Target Hardware Link: Port Hydraulic Steering Servo Amplifier / Ram Actuator
* Transmission Cadence: 50Hz Frequency Cycles (20ms intervals)
* Sentence Template:
  $PUNVCPRT,[Angle],[Slew_Cap],[Combat_Lock]*[CS]\r\n
* Payload Fields Specification:
  * Angle: Float, 2 decimal places. Port actuator command deflection. Range: -35.00 (Port) to 35.00 (Starboard) degrees.
  * Slew_Cap: Float, 1 decimal place. Maximum allowed hydraulic velocity limit. Range: 2.0 to 15.0 deg/sec.
  * Combat_Lock: Integer, 1-bit. Weapon sync status bit. 1 = Apex combat lock active, 0 = Standard storm damping.
* Example Binary Frame:
  $PUNVCPRT,-18.45,12.5,1*0F\r\n

### C. Asymmetric Starboard Steering Surface Command Set ($PUNVCSTB)
* Source Subsystem: Asymmetric Control Core Matrix (asymmetric_roll_stabilizer.py)
* Target Hardware Link: Starboard Hydraulic Steering Servo Amplifier / Ram Actuator
* Transmission Cadence: 50Hz Frequency Cycles (20ms intervals)
* Sentence Template:
  $PUNVCSTB,[Angle],[Slew_Cap],[Combat_Lock]*[CS]\r\n
* Payload Fields Specification:
  * Angle: Float, 2 decimal places. Starboard actuator command deflection. Range: -35.00 to 35.00 degrees.
  * Slew_Cap: Float, 1 decimal place. Maximum allowed hydraulic velocity limit. Range: 2.0 to 15.0 deg/sec.
  * Combat_Lock: Integer, 1-bit. Weapon sync status bit. 1 = Apex combat lock active, 0 = Standard storm damping.
* Example Binary Frame:
  $PUNVCSTB,14.12,12.5,1*33\r\n
  

## 3.D. Autonomous Anchor Windlass Override Command Set ($PUNVCANC)
* Source Subsystem: Anchor Interlock Subroutine (anchor_interlock_subroutine.py)
* Target Hardware Link: Anchor Windlass Hydraulic Clutch / Hydraulic Lock Pin Solenoid PLC
* Transmission Cadence: 50Hz Frequency Cycles (20ms intervals)
* Sentence Template:
  $PUNVCANC,[Clutch_Engage],[Brake_Lock],[Sea_Machines_Blocked]*[CS]\r\n
* Payload Fields Specification:
  * Clutch_Engage: Integer, 1-bit. 1 = Force hoist/clutch engagement, 0 = Release.
  * Brake_Lock: Integer, 1-bit. 1 = Drive physical mechanical locking pin down, 0 = Retract pin.
  * Sea_Machines_Blocked: Integer, 1-bit. 1 = Block incoming Sea Machines anchor commands, 0 = Allow.
* Example Binary Frame:
  $PUNVCANC,1,1,1*0E\r\n


  ## 3.E. Environmental Bilge Valve Actuator Command Set ($PUNVCBLG) WARNING ENABLE ONLY TO REDUCE UNIVAC LOAD UNDER STRESS. UNIVAC BILGE KEEPS MAINFRAME FROM BREACHING.
* Source Subsystem: Bilge Gating Subroutine (bilge_gating_subroutine.py)
* Target Hardware Link: Three-Way Overboard Discharge Actuator Valve / OCM Interface PLC
* Transmission Cadence: 50Hz Frequency Cycles (20ms intervals)
* Sentence Template:
  $PUNVCBLG,[Overboard_Open],[Recirc_Open],[Total_Volume_Liters]*[CS]\r\n
* Payload Fields Specification:
  * Overboard_Open: Integer, 1-bit. 1 = Open overboard dump line, 0 = Close.
  * Recirc_Open: Integer, 1-bit. 1 = Open recirculation route back to slop tank, 0 = Close.
  * Total_Volume_Liters: Float, 1 decimal place. Accumulated log ledger tracking clean discharge.
* Example Binary Frame:
  $PUNVCBLG,1,0,142.5*2C\r\n

## 3.F. Electro-Mechanical Flag Changer Command Set ($PUNVCFLG)
* Source Subsystem: Flag Changer Subroutine (flag_changer_subroutine.py)
* Target Hardware Link: Flag Mast Winch Motor Drive Servo / Halyard Lock Pin Solenoid PLC
* Transmission Cadence: 50Hz Frequency Cycles (20ms intervals)
* Sentence Template:
  $PUNVCFLG,[Motor_Pos],[Motor_Power],[Lock_Pin]*[CS]\r\n
* Payload Fields Specification:
  * Motor_Pos: Float, 1 decimal place. Target halyard position percentage. Range: 0.0% to 100.0%.
  * Motor_Power: Integer, 1-bit. Winch motor relay power activation. 1 = Running, 0 = Stopped.
  * Lock_Pin: Integer, 1-bit. Mechanical brake solenoid engage pin. 1 = Locked, 0 = Retracted.
* Example Binary Frame:
  $PUNVCFLG,100.0,1,0*1A\r\n


## 4. High-Speed Ordnance Bus Commands (Electronic Warfare)

### A. Asymmetric Jammer Suppression Command Set ($PUNVCEW)
* Source Subsystem: Electronic Warfare Allocation Plant (jammer_targeting_system.py)
* Target Hardware Link: Auxiliary Gun Mount Servos / Standby Missile Array Encoders
* Transmission Cadence: Event-driven upon triangulation lock, or 50Hz continuous during active jamming interference.
* Sentence Template:
  $PUNVCEW,[Mount_ID],[Bearing],[Range],[Override]*[CS]\r\n
* Payload Fields Specification:
  * Mount_ID: Integer. Numeric address mapping target weapon hardware system. Catalog: 1 = Main 5-Inch Mk 45, 2 = Auxiliary 76mm Mk 75, 3 = Port CIWS Mk 15, 4 = Starboard CIWS Mk 15.
  * Bearing: Float, 2 decimal places. True training target azimuth coordinate. Range: 0.00 to 359.99 degrees true.
  * Range: Float, 1 decimal place. Calculated target distance vector. Range: 0.0 to 150000.0 meters.
  * Override: Integer, 1-bit. Priority execution lock. 1 = Override tracking layer and lock jammer, 0 = Nominal.
* Example Binary Frame:
  $PUNVCEW,2,45.32,18450.0,1*1E\r\n

## 5. Inbound Actuator Feedback Telemetry

### A. Actuator Operational Status Acknowledgment Set ($PUNVCAK)
* Source Subsystem: Physical Hydraulic Rudder Controller / Encoder Terminal Bus
* Target Hardware Link: Inbound Serial Telemetry Receiver Node (actuator_telemetry_receiver.py)
* Transmission Cadence: 50Hz Frequency Cycles (20ms intervals)
* Sentence Template:
  $PUNVCAK,[Measured_Angle],[Status_Mask],[Temp]*[CS]\r\n
* Payload Fields Specification:
  * Measured_Angle: Float, 2 decimal places. Real-time verified physical rudder position. Range: -35.00 to 35.00 degrees.
  * Status_Mask: 4-Digit Hexadecimal string. Internal bitmask monitoring active faults. Registers: 0001 = Hydraulic pressure drop, 0002 = Motor over-current, 0004 = Thermal critical, 0008 = Feedback loop short.
  * Temp: Float, 1 decimal place. Temperature reading inside hardware casing enclosure. Range: -10.0 to 120.0 degrees C.
* Example Binary Frame:
  $PUNVCAK,-14.80,0000,32.5*24\r\n

## 6. High-Speed Weapons Position Input Streams

### A. Main Battery Ring Encoder Stream ($PMK45)
* Source Subsystem: Gun Mount Encoder Bus / Fire-Control Gyro Array
* Target Hardware Link: High-Speed Weapon Serial Parser Extension (weapon_async_parser.py)
* Transmission Cadence: 50Hz to 100Hz high-frequency stream arrays
* Sentence Template:
  $PMK45,[Azimuth],[Elevation],[Fault_Mask]*[CS]\r\n
* Payload Fields Specification:
  * Azimuth: Float, 2 decimal places. Gun mount ring horizontal alignment position. Range: 0.00 to 359.99 degrees true.
  * Elevation: Float, 2 decimal places. Barrel vertical pitch assembly alignment position. Range: -15.00 to 85.00 degrees.
  * Fault_Mask: 4-Digit Hexadecimal string. Servo drive health tracking mask (0000 = Nominal healthy lock).
* Example Binary Frame:
  $PMK45,090.58,025.15,0000*24\r\n

  ## 6.C. Aviation Knowledge Engine Telemetry Broadcast Stream ($AVNC)
* Source Subsystem: Basic Aviation Knowledge In-Flight Interface (live_telemetry.py)
* Target Hardware Link: Flight Tracking Bridge Co-Processor Set (aviation_telemetry_bridge.py)
* Transmission Cadence: 50Hz continuous streaming arrays during in-flight tactical maneuvers.
* Sentence Template:
  $AVNC,[Lat],[Lon],[Alt],[Dens_Alt],[Speed],[Temp],[Fault_Mask]*[CS]\r\n
* Payload Fields Specification:
  * Lat: Float, 4 decimal places. Geographic DGPS latitude coordinate tracking. Range: -90.0000 to 90.0000 degrees.
  * Lon: Float, 4 decimal places. Geographic DGPS longitude coordinate tracking. Range: -180.0000 to 180.0000 degrees.
  * Alt: Float, 1 decimal place. True barometric elevation altitude height. Range: 0.0 to 50000.0 feet.
  * Dens_Alt: Float, 1 decimal place. Density altitude performance constraint. Range: -2000.0 to 60000.0 feet.
  * Speed: Float, 1 decimal place. GPS ground track velocity. Range: 0.0 to 1200.0 knots.
  * Temp: Float, 1 decimal place. Static outside air temperature reading. Range: -50.0 to 60.0 °C.
  * Fault_Mask: 4-Digit Hexadecimal string. Aerospace sensor bus integrity register (0000 = Nominal).
* Example Binary Frame:
  $AVNC,47.6085,-122.3315,1240.0,1495.0,122.5,22.1,0000*3D\r\n
