// Append or include alongside your existing C++ network driver environment
#include "CommandDownlinkTypeSupportImpl.h"

// Listener class that fires a callback whenever Aegis issues a fire command
class WeaponDownlinkListener : public DDS::DataReaderListener {
public:
    int tx_socket_fd;
    struct sockaddr_in dtic_hardware_addr;

    void on_data_available(DDS::DataReader_ptr reader) override {
        AegisActuationCommandDataReader_var cmd_reader = AegisActuationCommandDataReader::_narrow(reader);
        AegisActuationCommand cmd;
        DDS::SampleInfo info;

        if (cmd_reader->take_next_sample(cmd, info) == DDS::RETCODE_OK) {
            if (info.valid_data) {
                uint32_t outbound_payload[3];

                // Convert Little-Endian Aegis math into Big-Endian layout for UNIVAC registers
                outbound_payload[0] = htonl(cmd.raw_launcher_azimuth);
                outbound_payload[1] = htonl(cmd.raw_launcher_elevation);
                outbound_payload[2] = htonl(cmd.fire_trigger_bitmask);

                // Push raw 12-byte payload over Ethernet straight to the FPGA interface unit
                sendto(tx_socket_fd, outbound_payload, 12, 0, 
                       (struct sockaddr*)&dtic_hardware_addr, sizeof(dtic_hardware_addr));
            }
        }
    }
};
