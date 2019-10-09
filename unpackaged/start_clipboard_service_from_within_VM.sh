# If you are hosting from within a VM, it can be a bit tricky
# to forward the requests to the guest system.
#
# I have come up with a simple way of forwarding the request to another
# port: Choose NAT network adapter and forward from within "Port Forwarding":
# PORT 5555 to PORT 5556. Leave the IP addresses blank!
SERVER_ADDR=$1
MY_IP=$(dig @resolver1.opendns.com ANY myip.opendns.com +short)
MY_IP="http://$MY_IP:5555/"
echo $MY_IP
python3 ./src/clipboard_server/main.py --port 5556 --domain $MY_IP --clipserver=$SERVER_ADDR --sync-clipboard True
