# Citizenwatt install script
# Launch as root

# Change Hostname
echo "citizenwatt" > /etc/hostname

# Add citizenWatt repository
echo "deb http://ks.citoyenscapteurs.net/repos/apt/debian/ wheezy main" > /etc/apt/sources.list.d/citizenwatt.list

# Add our GPG key
wget -O - http://ks.citoyenscapteurs.net/repos/apt/citizenwatt.public.key | apt-key add -

# Install Python
/bin/bash install_python34.sh

# Install packages
# TODO : add citizenwatt-visu
apt-get install librf24-dev postgresql supervisor

# Install Python module deps
apt-get -t jessie --yes install postgresql-server-dev-all

# Python modules
pip3 install requests sqlalchemy pycrypto numpy cherrypy psycopg2
