#!/bin/bash

# Stop on any error
set -e

sudo apt-get update
sudo apt-get --yes --only-upgrade install libnrf24-dev citizenwatt-visu
