#include <iostream>
#include <cstring>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>
// Include DDS auto-generated headers (assumes OpenDDS/RTI environment) 
#include "TacticalTrackTypeSupportImpl.h" 

#define PORT 5005
#define BUFFER_SIZE 16  // 4 words * 4 bytes per word = 16 bytes  

// Helper to handle Endianness conversion from UNIVAC Big-Endian to x86 Little-Endian 
uint32_t convert_big_endian_to_native(uint32_t value) {
    return ntohl(value);
}

int main() {
    // 1. Initialize System Socket     
    int server_fd;
    struct sockaddr_in address;
    uint32_t network_buffer[4];
    
    if ((server_fd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        std::cerr << "[ERR] Failed to create UDP socket." << std::endl;
        return -1;
    }
    
    std::memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY; // Listen on all network interfaces     
    address.sin_port = htons(PORT);
    
    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        std::cerr << "[ERR] Bind failed on port " << PORT << std::endl;
        close(server_fd);
        return -1;
    }
    
    // 2. Initialize DDS Infrastructure      
    auto participant = DDS::DomainParticipantFactory::get_instance()->create_participant(
        0, PARTICIPANT_QOS_DEFAULT, nullptr, STATUS_MASK_NONE);
        
    LegacyTrackTypeSupport_var ts = new LegacyTrackTypeSupportImpl();
    ts->register_type(participant.in(), "");
    
    auto topic = participant->create_topic(
        "Aegis_Legacy_Tracks", ts->get_type_name(), TOPIC_QOS_DEFAULT, nullptr, STATUS_MASK_NONE);
        
    auto publisher = participant->create_publisher(PUBLISHER_QOS_DEFAULT, nullptr, STATUS_MASK_NONE);
    
    // Load the specific XML profile from our file structure 
    auto writer = publisher->create_datawriter_with_profile(
        topic.in(), 
        "TacticalCombatLibrary",      // Library Name matching XML     
        "HighPriorityTargetProfile",  // Profile Name matching XML     
        nullptr, 
        STATUS_MASK_NONE);
        
    LegacyTrackDataWriter_var track_writer = LegacyTrackDataWriter::_narrow(writer.in());
    
    std::cout << "[INFO] Aegis Controller Driver Active. Listening on UDP Port " << PORT << "..." << std::endl;
    
    // 3. Real-Time Data Pipeline Loop     
    while (true) {
        struct sockaddr_in client_addr;
        socklen_t addr_len = sizeof(client_addr);
        
        // Blocking read on the Ethernet switch input stream         
        ssize_t bytes_received = recvfrom(server_fd, network_buffer, BUFFER_SIZE, 0,
                                          (struct sockaddr*)&client_addr, &addr_len);
                                          
        if (bytes_received == BUFFER_SIZE) {
            // Instantiate our DDS Topic Object             
            LegacyTrack track_msg;
            
            // Extract bytes and fix the Endianness shift from the UNIVAC architecture             
            track_msg.track_id           = convert_big_endian_to_native(network_buffer[0]);
            track_msg.target_range_yds   = convert_big_endian_to_native(network_buffer[1]);
            track_msg.target_bearing_min = convert_big_endian_to_native(network_buffer[2]);
            track_msg.target_altitude_ft = convert_big_endian_to_native(network_buffer[3]);
            
            // Zero-mask upper bits just in case of any 30-bit padding leaks from legacy registers             
            track_msg.track_id &= 0x3FFFFFFF;
            
            // 4. Publish directly into the Aegis Combat System LAN             
            DDS::ReturnCode_t ret = track_writer->write(track_msg, DDS::HANDLE_NIL);
            
            if (ret != DDS::RETCODE_OK) {
                std::cerr << "[WARN] DDS Track Publish Failed." << std::endl;
            }
        } else {
            std::cerr << "[WARN] Corrupted packet size received: " << bytes_received << " bytes." << std::endl;
        }
    }
    
    // Cleanup resources (unreachable in infinite loop execution)     
    close(server_fd);
    return 0;
}
