SHELL := /bin/bash

clean:
	rm -r ~/.cache/cauldron

server:
	CAULDRON_DIR=~/.cache/cauldron ./dist/server

install-ubuntu:
	sudo systemctl stop desktop.cauldron.service
	mkdir -p ~/.cache/cauldron
	cp dist/download_blacklist.txt ~/.cache/cauldron
	sudo cp dist/cauldron /usr/local/bin
	sudo cp install/desktop.cauldron.service /etc/systemd/system/desktop.cauldron.service
	sudo systemctl daemon-reload
	sudo systemctl start desktop.cauldron.service
	sudo systemctl enable desktop.cauldron.service

build:
	python3 -m venv .cauldron-venv
	source .cauldron-venv/bin/activate; \
	pip install -r requirements.txt; \
	pyinstaller --clean --onefile cauldron.py
	cp download_blacklist.txt dist

optipng:
	find wget/downloads -name '*.png' -print0 | xargs -0 optipng -o7

