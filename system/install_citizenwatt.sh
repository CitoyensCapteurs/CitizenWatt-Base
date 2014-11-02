#!/bin/bash

### Citizenwatt install script
# Install Citizenwatt packages and configure hostname
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

# Change Hostname
echo "citizenwatt" > /etc/hostname

# Add citizenWatt repository
echo "deb http://ks.citoyenscapteurs.net/repos/apt/debian/ wheezy main" > /etc/apt/sources.list.d/citizenwatt.list

# Add our GPG key
wget -O - http://ks.citoyenscapteurs.net/repos/apt/citizenwatt.public.key | apt-key add -

# Install Python
/bin/bash install_python34.sh

# Install packages
apt-get --yes install citizenwatt-visu librf24-dev postgresql supervisor avahi-daemon redis-server iptables-persistent

# Install Python module deps
apt-get -t jessie --yes install postgresql-server-dev-all

# Python modules
pip3 install requests sqlalchemy pycrypto numpy cherrypy psycopg2 redis

# Database setup
su - postgres
psql -c "CREATE DATABASE citizenwatt;"
psql -c "CREATE USER citizenwatt PASSWORD 'citizenwatt';"
psql -c "GRANT ALL ON DATABASE citizenwatt TO citizenwatt;"
exit

# Firewall setup
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination :8080
/etc/init.d/iptables-persistent save
