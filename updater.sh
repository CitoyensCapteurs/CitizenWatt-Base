#!/bin/bash

# Stop on any error
set -e

echo "Start CitizenWatt update..."
sudo apt-get update
sudo apt-get --yes --only-upgrade install libnrf24-dev citizenwatt-visu
echo "End CitizenWatt update"
