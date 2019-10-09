SERVER_ADDR=$1
python3 ./src/webhooks/main.py -p 6000 -d http://localhost:6000/ -c $SERVER_ADDR
