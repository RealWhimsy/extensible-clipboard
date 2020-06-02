.PHONY: all packages run

all: packages

packages:
	$(MAKE) -C clip_server
	$(MAKE) -C clipboard_bridge

run:
	cd clip_server && . venv/bin/activate && python3 ./src/main.py & echo $$! > server.pid
	cd clipboard_bridge && . venv/bin/activate && python3 ./src/main.py & echo $$! > bridge.pid
stop:
	# simplistic, but effective way of stopping the application
	cat server.pid | xargs kill
	rm server.pid
	cat bridge.pid | xargs kill
	rm bridge.pid