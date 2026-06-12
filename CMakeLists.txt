cmake_minimum_required(VERSION 3.12)
project(AegisLegacyBridge VERSION 1.0.0 LANGUAGES CXX)

# Enforce Modern C++ Standard Guidelines
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Optimization and hardening flags for real-time tactical software deployment
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -Wall -Wextra -Werror -fstack-protector-strong -D_FORTIFY_SOURCE=2")

# Locate and Load DDS Middleware Dependencies
find_package(OpenDDS REQUIRED)
find_package(Threads REQUIRED)

# Code Generation Pipeline: Compile IDL files into C++ Source
set(IDL_FILES
    TacticalTrack.idl
    CommandDownlink.idl
)

OPENDDS_TARGET_SOURCES(AegisLegacyBridge_IDL_TARGET
    SOURCES ${IDL_FILES}
    SUPPRESS_SUCH_WARNINGS
)

# Define the Executable Targets and Source Mapping
set(SOURCE_FILES
    main.cpp            
    downlink_driver.cpp 
)

add_executable(aegis_bridge_driver ${SOURCE_FILES})

# Direct Dependency Mapping and Compilation Links
target_link_libraries(aegis_bridge_driver
    PRIVATE
        AegisLegacyBridge_IDL_TARGET
        OpenDDS::OpenDDS            
        Threads::Threads               
)

# Include Path Architectures
target_include_directories(aegis_bridge_driver
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_CURRENT_BINARY_DIR}    
)

install(TARGETS aegis_bridge_driver
    RUNTIME DESTINATION /opt/aegis/bin
    COMPONENT Runtime
)

message(STATUS "Aegis-UNIVAC Legacy Bridge build matrix configured successfully.")
