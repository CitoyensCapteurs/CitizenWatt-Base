# CD to home
cd

# Get RF24
git clone https://github.com/stanleyseow/RF24.git RF24

# Checkout to our version
cd RF24
git checkout 2a1a4e6e27056844a3bc419d65b8a2d4e0f1770e

# Build
cd librf24-rpi/librf24
make
sudo make install
