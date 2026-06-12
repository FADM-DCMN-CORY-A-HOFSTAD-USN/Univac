**1\. The Computer: Trenton Systems Rugged ION Mini PC or 3U BAM Server**

[Trenton Systems](https://www.trentonsystems.com/en-us/resource-hub/blog/rugged-computers-military-satellite-communications) is an authoritative manufacturer of **cybersecure, tactical computers that are fully designed, manufactured, and assembled in Lawrenceville, Georgia, USA**. \[1, 2\]

* **Environmental Protection:** Their tactical enclosures are fully sealed and ruggedized to meet **MIL-STD-810H** and **IP67 waterproof/dustproof testing standards**, making them resilient against water spray and moisture in shipboard environments. \[1, 3\]  
* **The Aegis Port:** Out of the box, these systems are equipped with high-throughput **10GbE (Gigabit Ethernet) RJ-45 or fiber-optic ports**. This serves as your dedicated **Aegis Connection**, plugging straight into the ship’s modern combat network switches to stream the C++ DDS target tracking topics you built earlier. \[4\]

## ---

**2\. The Univac Connection: GET Engineering PCIe NTDS Parallel Adapter \[5\]**

To add the missing Univac port, you must populate one of the computer's internal PCIe slots with a specialized card from **GET Engineering** (based in El Cajon, California, USA), or **IXI Technology** (based in San Clemente, California, USA). These companies specialize in legacy Naval Tactical Data System (NTDS) hardware translation. \[6, 7, 8\]

* **The Card:** The [GET Engineering Parallel PCI Express Interface Adapter (Product 10075001\)](https://gethdio.com/10075001) is explicitly designed for this task. \[7\]  
* **The Univac Port:** The card features a heavy-duty, military-grade front panel connector (such as a **MIL-DTL-32139 nano-miniature or a multi-pin SEARAY connector**). This connects directly to the heavy, copper **MIL-STD-1397 Type C (Fast Parallel)** cables coming out of the back of the 1970s UNIVAC computer. \[7\]  
* **How it Works:** The card uses an on-board, military-grade Field Programmable Gate Array (FPGA) and Direct Memory Access (DMA) channels. It automatically handles the exact physical latching registers, oversampling, and asynchronous hardware handshakes (ODR/ODA) without adding any processing overhead to the computer's CPU. \[7\]

## ---

**3\. System Architecture Layout**

When integrated, the final hardware configuration completely fills the architectural gap:

  `+----------------------------------------------------------------------------+`

  `|                   TRENTON SYSTEMS RUGGED USA COMPUTER                      |`  
  `|                                                                            |`  
  `|  [ GET Engineering PCIe Card ]               [ Native Network Interface ]  |`  
  `|               |                                            |               |`  
  `|               |                                            |               |`  
  `+---------------|--------------------------------------------|---------------+`

                  `|                                            |`  
                  `| MIL-STD-1397                               | Gigabit Ethernet`  
                  `| Heavy Parallel Cable                       | Cat6A / Fiber Optic`  
                  `v                                            v`  
     `+-------------------------+                  +-------------------------+`

     `| 1970s UNIVAC MAINFRAME  |                  |   MODERN AEGIS LAN      |`  
     `|  (Dumb Terminal Mode)   |                  | (DDS Network Switch)    |`  
     `+-------------------------+                  +-------------------------+`

1. The physical UNIVAC pins connect via a copper cable to the internal **GET Engineering card**.  
2. The card routes the incoming bytes over the internal PCIe bus to your compiled **C++ driver script**.  
3. The computer processes the data, calculates the global coordinates using your kinematics matrix, and pumps the output straight out its integrated **waterproof Ethernet gland** right into the Aegis routing switch. \[4, 7\]
