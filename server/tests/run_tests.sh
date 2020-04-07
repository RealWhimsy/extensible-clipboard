#!/bin/sh
cd "$(dirname "$0")"
. ./../venv/bin/activate
python3 ./../src/main.py -p 5000
coverage run -m pytest . ./../src/main.py --html=pytest-report.html
coverage report --omit="*/venv/*"
echo $pId
kill $pId