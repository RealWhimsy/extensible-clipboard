.PHONY: all packages clean run

all: packages

packages:
	python3 -m venv venv
	. venv/bin/activate
	pip3 install -r requirements.txt

run:
	. venv/bin/activate
	python3 ./src/main.py $(ARGS) &
	echo "Server running as process $!"

clean:
	rm -rf venv