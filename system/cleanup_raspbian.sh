# Citizenwatt Raspbian cleanup script
# Launch as root

# Remove useless packages
apt-get --yes purge x11-common lxde dillo gnome-icon-theme \
  gnome-themes-standard-data libgnome-keyring-common libgnome-keyring0 \
  libsoup-gnome2.4-1 lxde-common lxde-icon-theme omxplayer dbus-x11 libx11-6 \
  libx11-data libx11-xcb1 desktop-file-utils debian-reference-en \
  debian-reference-common java-common

apt-get --yes install mysql-client mysql-server avahi-daemon

# Remove unused packets
apt-get --yes autoremove --purge

# Clear APT cache
#apt-get clean

rm -rf /opt/vc /home/pi/Desktop /home/pi/python_games /home/pi/ocr_pi.png

# Do updates
apt-get update && apt-get upgrade --yes

