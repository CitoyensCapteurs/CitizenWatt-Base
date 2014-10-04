#include <cstdlib>
#include <iostream>
#include <sstream>
#include <string>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <signal.h>
#include <RF24.h>

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
const rf24_pa_dbm_e NRF_PA_LEVEL = RF24_PA_LOW;

// Channel for the nrf module
// 76 is default safe channel in RF24
const int NRF_CHANNEL = 0x4c;

const uint64_t addr = 0xE056D446D0LL;

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
    radio.setPALevel(NRF_PA_LEVEL);
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
    }
    close(fd);
}
