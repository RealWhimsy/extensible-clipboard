.PHONY: all packages run

all: packages

packages:
	$(MAKE) -C clipserver
	$(MAKE) -C clipboard

run:
	cd clipserver; make run &
	cd clipboard; make run &
stop:
	# simplistic, but effective way of stopping the application
	pgrep python3 | xargs kill
