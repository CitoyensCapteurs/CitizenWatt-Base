# Citizenwatt Raspbian cleanup script
# Launch as root

# Remove useless packages
apt-get purge x11-common midori lxde dillo gnome-icon-theme \
  gnome-themes-standard-data libgnome-keyring-common libgnome-keyring0 \
  libsoup-gnome2.4-1 lxde-common lxde-icon-theme omxplayer dbus-x11 libx11-6 \
  libx11-data libx11-xcb1 gcc-4.5-base gcc-4.6-base desktop-file-utils \
  debian-reference-en debian-reference-common java-common

# Remove unused packets
apt-get autoremove --purge

# Clear APT cache
apt-get clean

rm -rf /opt/vc
