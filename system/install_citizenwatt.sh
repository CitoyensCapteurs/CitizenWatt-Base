# Citizenwatt install script
# Launch as root

# Change Hostname
echo "citizenwatt" > /etc/hostname

# Add citizenWatt repository
echo "deb http://ks.citoyenscapteurs.net/repos/apt/debian/ wheezy main" > /etc/apt/sources.list.d/citizenwatt.list

# Add our GPG key
wget -O - http://ks.citoyenscapteurs.net/repos/apt/citizenwatt.public.key | apt-key add -

# Update
apt-get update

# Install packages
# TODO : add citizenwatt-visu
apt-get install librf24-dev

# Install Python
/bin/bash install_python34.sh

# Python modules
pip3 install requests sqlalchemy mysql-connector-python pycrypto numpy cherrypy
