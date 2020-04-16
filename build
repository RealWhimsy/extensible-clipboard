#!/bin/sh
sudo apt install python3-venv python3-dev binutils
cd ./z_servers_obsolete
python3 -m venv venv
. venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
fbs freeze
