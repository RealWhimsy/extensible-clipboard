.PHONY: all packages clean

all: packages

packages:
	sudo apt install python3-venv python3-dev python3-pip binutils
	$(MAKE) -C server
	$(MAKE) -C clipboard

clean:
	$(MAKE) clean server
