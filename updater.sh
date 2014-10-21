#!/bin/bash

echo "Start update"
sudo apt-get update
sudo apt-get --yes --only-upgrade install libnrf24-dev citizenwatt-visu
echo "End update"
