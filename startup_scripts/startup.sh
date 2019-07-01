echo "Attention, this action will kill all active python3 processes!"
pgrep python3 | xargs kill

cd ./extensible-clipboard
echo "Start Servers"
python3 ./src/server/main.py &
python3 ./src/clipboard_server/main.py --port 5555 --domain http://localhost:5555/ --clipserver http://localhost:5000/ --sync-clipboard True & 
python3 ./src/webhooks/main.py -p 6000 -d http://localhost:6000/ -c http://localhost:5000/ &