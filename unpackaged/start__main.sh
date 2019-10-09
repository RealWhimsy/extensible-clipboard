echo "Serve MongoDB"
pgrep mongo > kill
mongod &
echo "MongoDB served"
python3 ./src/server/main.py
