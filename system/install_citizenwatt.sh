# Add citizenWatt repository
echo "deb http://ks.citoyenscapteurs.net/repos/apt/debian/ wheezy main" > /etc/apt/sources.list.d/citizenwatt.list

# Add our GPG key
wget -O - http://ks.citoyenscapteurs.net/repos/apt/citizenwatt.public.key | apt-key add -

# Update
apt-get update

# Install packages
apt-get install librf24-dev citizenwatt-visu
