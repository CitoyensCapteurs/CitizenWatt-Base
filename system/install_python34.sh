# Citizenwatt Python 3.4 install script
# Launch as root

# Upgrade Raspbian
apt-get update
apt-get --yes upgrade

# Add testing sources
echo "deb http://mirrordirector.raspbian.org/raspbian/ jessie main" > /etc/apt/sources.list.d/jessie.list

# Pinning
echo -e "Package: *\nPin: release a=testing\nPin-Priority: 300" > /etc/apt/preferences.d/jessie.pref

# Update
apt-get update

# Install
apt-get -t jessie --yes install python3 gcc python3-pip python3-dev

# Python modules
pip3 install requests sqlalchemy mysql-connector-python pycrypto numpy cherrypy

# Remove unused packets
apt-get --yes autoremove --purge
