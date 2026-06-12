cmake_minimum_required(VERSION 3.12)
project(AegisLegacyBridge VERSION 1.0.0 LANGUAGES CXX)

# 1. Enforce Modern C++ Standard Guidelines
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Optimization and hardening flags for real-time tactical software deployment
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -Wall -Wextra -Werror -fstack-protector-strong -D_FORTIFY_SOURCE=2")

# 2. Locate and Load DDS Middleware Dependencies
# (Example configured for OpenDDS; easily adaptable to RTI Connext via find_package)
find_package(OpenDDS REQUIRED)

# 3. Code Generation Pipeline: Compile IDL files into C++ Source
# This macro invokes the IDL compiler to generate TypeSupport, DataReader, and DataWriter files
set(IDL_FILES
    TacticalTrack.idl
    CommandDownlink.idl
)

# OpenDDS macro to automatically compile the IDL definitions into the build tree
OPENDDS_TARGET_SOURCES(AegisLegacyBridge_IDL_TARGET
    SOURCES ${IDL_FILES}
    SUPPRESS_SUCH_WARNINGS
)

# 4. Define the Executable Targets and Source Mapping
set(SOURCE_FILES
    main.cpp            # Contains socket listener loops and business logic
    downlink_driver.cpp # Implements DDS subscriber handlers for weapon commands
)

# Add the main compilation target
add_executable(aegis_bridge_driver ${SOURCE_FILES})

# 5. Direct Dependency Mapping and Compilation Links
# Link the auto-generated IDL library dependencies directly into the main driver binary
target_link_libraries(aegis_bridge_driver
    PRIVATE
        AegisLegacyBridge_IDL_TARGET
        OpenDDS::OpenDDS                # Core DDS libraries
        Threads::Threads               # Required for low-latency multi-threading
)

# 6. Include Path Architectures
target_include_directories(aegis_bridge_driver
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_CURRENT_BINARY_DIR}    # Required to find auto-generated headers (.h)
)

# 7. Deployment Configuration: Define Target Binaries Destination
install(TARGETS aegis_bridge_driver
    RUNTIME DESTINATION /opt/aegis/bin
    COMPONENT Runtime
)

message(STATUS "Aegis-UNIVAC Legacy Bridge build matrix configured successfully.")
