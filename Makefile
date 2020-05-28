.PHONY: all packages run

all: packages

packages:
	$(MAKE) -C clip_server
	$(MAKE) -C clipboard_bridge

run:
	cd clip_server; make run &
	cd clipboard_bridge; make run &
stop:
	# simplistic, but effective way of stopping the application
	pgrep python3 | xargs kill
