SERVER_ADDR=$1
MY_IP=$(dig @resolver1.opendns.com ANY myip.opendns.com +short)
MY_IP="http://$MY_IP:5555/"
echo $MY_IP
python3 ./src/clipboard_server/main.py --port 5555 --domain $MY_IP --clipserver=$SERVER_ADDR --sync-clipboard True