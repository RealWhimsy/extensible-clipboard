#!/bin/sh
sudo apt-get install coverage
cd "$(dirname "$0")"
cd ..
. ./../../../venv/bin/activate
python3 main.py -nocbs & pId=$!
coverage run -m pytest ./tests ./main.py --html=pytest-report.html
coverage report --omit="*/venv/*"
echo $pId
kill $pId