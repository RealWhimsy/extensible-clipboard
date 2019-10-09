# Allow sid repository (https://stackoverflow.com/questions/47638143/install-mongodb-on-debian-buster)
echo "Installing MongoDB..."
sudo touch /etc/apt/sources.list.d/sid.list
sudo echo "deb http://deb.debian.org/debian/ sid main\ndeb-src http://deb.debian.org/debian/ sid main"> /etc/apt/sources.list.d/sid.list
sudo apt update
sudo apt install mongodb-server
echo "MongoDB installed"

echo "Serve MongoDB"
sudo pgrep mongo > kill
sudo mkdir /data/db -p
sudo mongod &
echo "MongoDB served"

# Clone Project from git
git clone https://github.com/FelixRDL/extensible-clipboard.git

# Install dependencies of services
cd ./extensible-clipboard
pip install flask
pip install requests
pip install -r requirements.txt
