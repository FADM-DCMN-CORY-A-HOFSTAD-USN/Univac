# Univac to Aegis Digital Tactical Intermediary Controller (DTIC)

This repository contains the software translation layer, protocol bridge, and legacy software patches required to integrate a 1970s UNIVAC mainframe (such as the CP-642B or AN/UYK-7) with a modern Aegis Combat System baseline.

## Overview
The Digital Tactical Intermediary Controller (DTIC) bridges the physical and architectural gap between 30/32-bit parallel MIL-STD-1397 asynchronous data and modern DDS-compliant UDP/IP Ethernet networks. By offloading complex kinematics and target tracking to the Aegis network, the legacy UNIVAC is transformed into a highly reliable, deterministic "dumb terminal" dedicated to managing raw sensor input and physical weapon actuation.

## Core Components
- **`NTDS_BRIDGE_PATCH.cms2`**: A CMS-2Y patch that allocates a tactical track memory pool and routes parallel output to the FPGA interface via legacy I/O Channel 5.
- **`ACTUATE.CMS`**: Replaces the mainframe's legacy weapon math with a hardened hardware input handler featuring CRC bitmask verification, velocity delta clamps, and a watchdog timer for safe fallback states.
- **`main.cpp` / `downlink_driver.cpp`**: C++ DDS network drivers that manage endianness conversion, DDS topic publishing/subscribing, and checksum generation.
- **`aegis_kinematics.hpp`**: Mathematical subroutines executing the transformation of raw imperial radar returns (yards/arcminutes) into standard Earth-Centered, Earth-Fixed (ECEF) coordinates.
- **`USER_QOS_PROFILES.xml`**: Strict DDS Quality of Service profiles ensuring high-priority, low-latency target delivery using DSCP 46 tagging and 20ms maximum blocking time rules.

## Build Instructions
1. Install an enterprise DDS distribution (such as OpenDDS or RTI Connext DDS) and the `Development Tools` GNU toolchain.
2. Initialize an isolated build directory: 
   `mkdir build && cd build`
3. Configure the CMake environment for Release execution: 
   `cmake -DCMAKE_BUILD_TYPE=Release ..`
4. Compile the binaries and auto-generate the IDL DDS TypeSupport code: 
   `cmake --build . --config Release -j$(nproc)`
