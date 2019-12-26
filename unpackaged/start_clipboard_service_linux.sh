#!/usr/bin/env bash
pip3 install -r ./src/clipboard_server/.requirements.txt
sudo apt install python3-pyqt5
SERVER_ADDR=$1
python3 ./src/clipboard_server/main.py --port 5555 --domain=public --clipserver=$SERVER_ADDR --sync-clipboard True
