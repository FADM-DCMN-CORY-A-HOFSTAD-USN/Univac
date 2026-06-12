#include <iostream>
#include <cstring>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>
#include <thread>
#include <vector>
#include <sched.h>     // Required for CPU pinning
#include <pthread.h>   // Required for thread affinity

// Include DDS auto-generated headers
#include "TacticalTrackTypeSupportImpl.h" 

#define PORT 5005
#define BUFFER_SIZE 16  

uint32_t convert_big_endian_to_native(uint32_t value) {
    return ntohl(value);
}

// -------------------------------------------------------------------------
// THREAD WORKER: Each core runs an independent instance of this loop
// -------------------------------------------------------------------------
void uplink_worker(int core_id, LegacyTrackDataWriter_var track_writer) {
    // 1. Hardware Pinning: Lock this thread to the specific CPU core
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    // 2. Initialize Worker Socket
    int server_fd;
    struct sockaddr_in address;
    uint32_t network_buffer[4];
    
    if ((server_fd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        std::cerr << "[Core " << core_id << "] Socket creation failed." << std::endl;
        return;
    }

    // CRITICAL: SO_REUSEPORT allows multiple threads to bind to port 5005. 
    // The Linux kernel will automatically load-balance incoming UDP frames across them.
    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt))) {
        std::cerr << "[Core " << core_id << "] SO_REUSEPORT failed." << std::endl;
        return;
    }
    
    std::memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY; 
    address.sin_port = htons(PORT);
    
    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        std::cerr << "[Core " << core_id << "] Bind failed." << std::endl;
        close(server_fd);
        return;
    }

    std::cout << "[INFO] Core " << core_id << " pinned and listening." << std::endl;

    // 3. Independent Core Pipeline Loop
    while (true) {
        struct sockaddr_in client_addr;
        socklen_t addr_len = sizeof(client_addr);
        
        ssize_t bytes_received = recvfrom(server_fd, network_buffer, BUFFER_SIZE, 0,
                                          (struct sockaddr*)&client_addr, &addr_len);
                                          
        if (bytes_received == BUFFER_SIZE) {
            LegacyTrack track_msg;
            
            track_msg.track_id           = convert_big_endian_to_native(network_buffer[0]) & 0x3FFFFFFF;
            track_msg.target_range_yds   = convert_big_endian_to_native(network_buffer[1]);
            track_msg.target_bearing_min = convert_big_endian_to_native(network_buffer[2]);
            track_msg.target_altitude_ft = convert_big_endian_to_native(network_buffer[3]);
            
            // The DDS DataWriter is thread-safe by default, allowing all cores to publish concurrently
            track_writer->write(track_msg, DDS::HANDLE_NIL);
        }
    }
    close(server_fd);
}

int main() {
    // 1. Initialize Global DDS Infrastructure
    auto participant = DDS::DomainParticipantFactory::get_instance()->create_participant(
        0, PARTICIPANT_QOS_DEFAULT, nullptr, STATUS_MASK_NONE);
        
    LegacyTrackTypeSupport_var ts = new LegacyTrackTypeSupportImpl();
    ts->register_type(participant.in(), "");
    
    auto topic = participant->create_topic(
        "Aegis_Legacy_Tracks", ts->get_type_name(), TOPIC_QOS_DEFAULT, nullptr, STATUS_MASK_NONE);
        
    auto publisher = participant->create_publisher(PUBLISHER_QOS_DEFAULT, nullptr, STATUS_MASK_NONE);
    
    auto writer = publisher->create_datawriter_with_profile(
        topic.in(), "TacticalCombatLibrary", "HighPriorityTargetProfile", nullptr, STATUS_MASK_NONE);
        
    LegacyTrackDataWriter_var track_writer = LegacyTrackDataWriter::_narrow(writer.in());

    // 2. Hardware Query & Thread Spawning
    unsigned int num_cores = std::thread::hardware_concurrency();
    std::cout << "[INFO] Detected " << num_cores << " CPU cores. Spawning UDP worker array..." << std::endl;

    std::vector<std::thread> worker_threads;
    for (unsigned int i = 0; i < num_cores; ++i) {
        worker_threads.emplace_back(uplink_worker, i, track_writer);
    }

    // 3. Keep main thread alive
    for (auto& t : worker_threads) {
        if (t.joinable()) {
            t.join();
        }
    }

    return 0;
}
