#include <cstdlib>
#include <iostream>
#include <fstream>
#include <string>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <signal.h>
#include <RF24.h>

/**
 * This program receives a measure packet through the nRF and pipes it to a named fifo.
 *
 * It is to be seen as an (ugly) wrapper to use the nRF24 lib written in C++ in Python.
 */

volatile sig_atomic_t flag = 0;
void quit(int sig) {
  flag = 1;
}

const bool DEBUG = true;

// Speed for the nrf module
// RF24_250KBPS / RF24_1MBPS / RF24_2MBPS
// Reduce it to improve reliability
const rf24_datarate_e NRF_SPEED = RF24_1MBPS;

// PreAmplifier level for the nRF
// Lower this to reduce power consumption. This will reduce range.
const rf24_pa_dbm_e NRF_DEFAULT_PA_LEVEL = RF24_PA_HIGH;

// Channel for the nrf module
// 76 is default safe channel in RF24
const int NRF_CHANNEL = 0x4c;

const uint64_t default_addr = 0xE056D446D0LL;

//RF24 radio(RPI_V2_GPIO_P1_15, RPI_V2_GPIO_P1_24, BCM2835_SPI_SPEED_8MHZ);
RF24 radio("/dev/spidev0.0",8000000 , 25);

// Named pipe
int fd;
char * myfifo = "/tmp/sensor";

int main() {
    uint8_t payload[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

    // Create FIFO
    mkfifo(myfifo, 0666);
    signal(SIGINT, quit);

    // Open FIFO - while wait here until another thread opens the same fifo
    fd = open(myfifo, O_WRONLY);

    // Get the address to listen on
    std::ifstream config_addr;
    config_addr.open("~/.config/citizenwatt/base_address", std::ios::in);
    std::ifstream nrf_power;
    nrf_power.open("~/.config/citizenwatt/nrf_power", std::ios::in);
    uint64_t addr;
    if (config_addr.is_open()) {
        config_addr >> addr;
        config_addr.close();
    }
    else {
        addr = default_addr;
    }
    uint64_t power;
    if (nrf_power.is_open()) {
        nrf_power >> power;
        nrf_power.close();
        switch (power) {
            case 0:
                power = RF24_PA_MIN;
                break;

            case 1:
                power = RF24_PA_LOW;
                break;

            case 2:
                power = RF24_PA_MED;
                break;

            case 3:
                power = RF24_PA_HIGH;
                break;

            default:
                power = NRF_DEFAULT_PA_LEVEL;
                break;
        }
    }
    else {
        power = NRF_DEFAULT_PA_LEVEL;
    }

    // Initialize nRF
    radio.begin();
    // Max number of retries and max delay between them
    radio.setRetries(15, 15);
    radio.setChannel(NRF_CHANNEL);
    // Reduce payload size to improve reliability
    radio.setPayloadSize(16);
    // Set the datarate
    radio.setDataRate(NRF_SPEED);
    // Use the largest CRC
    radio.setCRCLength(RF24_CRC_16);
    // Ensure auto ACK is enabled
    radio.setAutoAck(1);
    // Use the best PA level
    radio.setPALevel(power);
    // Open reading pipe
    radio.openReadingPipe(1, addr);

    radio.startListening();

    while(1) {
        if(flag) {
            close(fd);
            unlink(myfifo);
            std::cout << "Exiting…\n";
            return 0;
        }

        if(radio.available()) {
            radio.read(&payload, sizeof(payload));

            if(DEBUG) {
                std::cout << "Received : ";
                for(int i=0; i<sizeof(payload); i++) {
                    std::cout << std::hex << (int) payload[i];
                }
                std::cout << "\n";
            }

            // Send to fifo
            write(fd, payload, sizeof(payload));
            // Maybe needed ? fflush(fd)
        }
	sleep(2);
    }
    close(fd);
}
