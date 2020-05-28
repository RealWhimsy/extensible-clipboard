.PHONY: all packages clean run

all: packages

packages:
	python3 -m venv venv; . venv/bin/activate; pip3 install -r requirements.txt

run:
	. venv/bin/activate; python3 ./src/main.py $(ARGS)

clean:
	rm -rf venv
test:
	. venv/bin/activate; python3 ./src/main.py $(ARGS) &
	. venv/bin/activate; coverage run -m pytest --html=pytest-report.html
	pgrep python3 | xargs kill