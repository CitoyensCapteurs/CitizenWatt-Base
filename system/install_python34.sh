#!/bin/bash

### Python 3.4 install script
# Install Python 3.4 (from Debian Testing/Jessie)
# 
# Author: AlexFaraino
# Date: 29/10/2014
#
###

# Stop on error
set -e

# Launch as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Add testing sources
echo "deb http://mirrordirector.raspbian.org/raspbian/ jessie main" > /etc/apt/sources.list.d/jessie.list

# Pinning
echo -e "Package: *\nPin: release a=testing\nPin-Priority: 300" > /etc/apt/preferences.d/jessie.pref

# Update
apt-get update

# Install
apt-get -t jessie --yes install python3 gcc python3-pip python3-dev

# Remove unused packets (ie. Python3.2)
apt-get --yes autoremove --purge
