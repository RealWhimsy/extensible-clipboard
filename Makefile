.PHONY: all packages run

all: packages

packages:
	sudo apt install python3-venv python3-dev python3-pip binutils coverage
	$(MAKE) -C server
	$(MAKE) -C clipboard

run:
	cd server; make run
	cd clipboard; make run