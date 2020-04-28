.PHONY: all packages run

all: packages

packages:
	sudo apt install python3-venv python3-dev python3-pip binutils
	$(MAKE) -C clipserver
	$(MAKE) -C clipboard

run:
	cd clipserver; make run &
	cd clipboard; make run &
stop:
	# simplistic, but effective way of stopping the application
	pgrep python3 | xargs kill