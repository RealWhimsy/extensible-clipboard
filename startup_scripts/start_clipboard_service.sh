SERVER_ADDR=$1
echo $SERVER_ADDR
python3 ./extensible-clipboard/src/clipboard_server/main.py --port 5555 --domain http://localhost:5555/ --clipserver=$SERVER_ADDR --sync-clipboard True
