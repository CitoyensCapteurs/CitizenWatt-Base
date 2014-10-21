#!/bin/bash

# Stop on any error
set -e
cd /opt/citizenwatt

echo "Start CitizenWatt update..."

# Update
git pull
sudo ./post_update.sh

# Start back everything
sudo supervisorctl reload

echo "End CitizenWatt update"

# Old packages
#sudo apt-get update
#sudo apt-get --yes --only-upgrade install libnrf24-dev citizenwatt-visu
