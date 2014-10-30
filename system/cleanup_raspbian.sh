#!/bin/bash

### Citizenwatt Raspbian cleanup script
# Remove unused packages. Not mandatory.
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

# Remove useless packages
apt-get --yes purge x11-common lxde dillo gnome-icon-theme \
  gnome-themes-standard-data libgnome-keyring-common libgnome-keyring0 \
  libsoup-gnome2.4-1 lxde-common lxde-icon-theme omxplayer dbus-x11 libx11-6 \
  libx11-data libx11-xcb1 desktop-file-utils java-common

# Remove unused packets
apt-get --yes autoremove --purge

rm -rf /opt/vc /home/pi/Desktop /home/pi/python_games /home/pi/ocr_pi.png
